# Built-in
import os
from urllib.parse import urlparse

from PIL import Image as PILImage
from django.conf import settings
from django.contrib.auth import login
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from django.views import View
from django.views.generic import TemplateView, CreateView, ListView, DetailView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from urllib.request import urlopen, HTTPError
from django.core.files import File

# Custom:
from .models import Image, Album, Comment, Like, Favorite, Report
from .forms import ImageForm, UserRegistrationForm, UserLoginForm, AlbumForm, UserSearchForm, \
    ImageEditForm, CommentForm, ReportForm


def moderators_check(user):
    """
    function to check if the logged-in user belong to moderators group. used in:
    ImageDetailView, ImageDeleteView, AlbumDeleteView, ImageEditView
    """
    return user.groups.filter(name='Moderators').exists()


class TempMainView(TemplateView):
    # website home page view
    template_name = 'home.html'





class HomeView(CreateView):
    """
    View for uploading images with dynamic options based on user authentication.
    Users can upload images from their computer or provide an image URL.
    Authenticated users have additional options to specify privacy settings and associate images with albums.
    Uploaded images are processed, and if no title is provided, the image title is generated from the file name.
    """
    template_name = 'index.html'
    form_class = ImageForm

    def get_form(self, form_class=None):
        """
        Retrieves the image upload form with dynamic options based on user authentication.
        """
        form = super().get_form(form_class)

        # If the user is not logged in, remove private and album options
        if not self.request.user.is_authenticated:
            form.fields.pop('is_private')
            form.fields.pop('album')
        else:
            # Limit album choices to albums owned by the user
            form.fields['album'].queryset = Album.objects.filter(user=self.request.user)

        # Set available category choices for both authenticated and guest users
        form.fields['category'].choices = Image.CATEGORY_CHOICES
        return form

    def form_valid(self, form):
        """
        Processes the submitted form and saves the uploaded image.
        If no title is provided, the image title is generated from the image file name.
        Handles image upload from both computer and URL.
        """

        image = form.save(commit=False)

        if form.cleaned_data.get('url'):
            url = form.cleaned_data.get('url')
            try:
                response = urlopen(url)
                # Extract the file name from the URL
                parsed_url = urlparse(url)
                file_name = os.path.basename(parsed_url.path)

                # Associate the uploaded image with the logged-in user
                if self.request.user.is_authenticated:
                    image.user = self.request.user

                # Save the image from URL
                image.image.save(
                    file_name,
                    File(response),
                    save=True
                )

                # Generate title from the file name if not provided
                if not image.title:
                    image.title = os.path.splitext(file_name)[0]
            except HTTPError as e:
                # Display error message if URL fetch fails
                form.add_error(None, f"Failed to fetch image from URL: {e}")
                return self.form_invalid(form)
        else:
            # Handle image upload from computer
            # Generate title from the file name if not provided
            if not image.title:
                file_name = os.path.splitext(self.request.FILES['image'].name)[0]
                slug = slugify(file_name)
                image.title = slug

            # Associate the uploaded image with the logged-in user
            if self.request.user.is_authenticated:
                image.user = self.request.user
            image.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('image_details', kwargs={'pk': self.object.pk})


class ImageDetailView(DetailView):
    """
    Displays the details of an uploaded image, along with associated actions and information.
    """
    template_name = 'image_detail.html'
    model = Image
    context_object_name = 'image'

    def get_context_data(self, **kwargs):
        """
        Retrieves additional context data for rendering the image detail template.
        """
        context = super().get_context_data(**kwargs)
        is_moderator = moderators_check(self.request.user)  # Check if the user is a moderator
        image = self.get_object()

        # Determine if the image can be viewed based on privacy settings and user authentication
        if image.is_private:
            if not self.request.user.is_authenticated:
                context['can_view'] = False

            elif not (self.request.user == image.user or self.request.user.is_superuser or moderators_check(
                    self.request.user)):
                context['can_view'] = False

            else:
                context['can_view'] = True
        else:
            context['can_view'] = True

        # Determine if the user has permission to delete the image
        if self.request.user == image.user:
            context['can_delete'] = True
        else:
            context['can_delete'] = False
        context['is_moderator'] = is_moderator
        context['is_superuser'] = self.request.user.is_superuser
        context['dimensions'] = f'{image.image.width} X {image.image.height} '
        context['size'] = f'{image.image.size / 1000:.1f} kB'
        # Retrieve comments associated with the image and provide them to the template in descensing order.
        context['comments'] = Comment.objects.filter(image=image).order_by('-created_at')
        liked = False
        favorite = False
        like_count = self.object.like_set.count()
        if self.request.user.is_authenticated:
            context['comment_form'] = CommentForm()
            liked = self.object.like_set.filter(user=self.request.user).exists()
            favorite = self.object.favorite_set.filter(user=self.request.user).exists()
        context['liked'] = liked
        context['favorite'] = favorite
        context['like_count'] = like_count
        return context

    def post(self, request, *args, **kwargs):
        """
        Handles user interactions such as posting comments, liking, and favoriting the image.
        """
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))

        image = self.get_object()
        form = CommentForm(request.POST)
        liked = Like.objects.filter(user=self.request.user, image=image).exists()
        favorite = Favorite.objects.filter(user=self.request.user, image=image).exists()
        if 'action' in request.POST:
            action = request.POST['action']
            if action == 'like':
                if not liked:
                    # If the user hasn't liked the image, create a new like
                    Like.objects.create(user=self.request.user, image=image)
            elif action == 'unlike':
                if liked:
                    # If the user has liked the image, remove the like
                    Like.objects.filter(user=self.request.user, image=image).delete()
            elif action == 'favorite':
                if not favorite:
                    # If the user hasn't favorited the image, create a new favorite
                    Favorite.objects.create(user=self.request.user, image=image)
            elif action == 'unfavorite':
                if favorite:
                    # If the user has favorited the image, remove the favorite
                    Favorite.objects.filter(user=self.request.user, image=image).delete()
            else:
                # Redirect back to the image details page if the action is not recognized
                return HttpResponseRedirect(reverse('image_details', kwargs={'pk': image.pk}))

        if form.is_valid():
            # If the submitted comment form is valid, save the comment and redirect to the image details page
            comment = form.save(commit=False)
            comment.user = request.user
            comment.image = image
            comment.save()
            return HttpResponseRedirect(reverse('image_details', kwargs={'pk': image.pk}))

        return self.get(request, *args, **kwargs)


class DeleteCommentView(View):
    """
    Handles the deletion of comments associated with an image.
    """

    def post(self, request, pk, *args, **kwargs):
        # Retrieve the comment object using the provided primary key
        comment = get_object_or_404(Comment, pk=pk)

        # Check if the current user has the necessary permissions to delete the comment:
        # (image uploader/comment owner/moderator/superuser)
        if self.request.user == comment.image.user or self.request.user == comment.user or self.request.user.is_superuser or moderators_check(
                self.request.user):
            comment.delete()
        return redirect('image_details', pk=comment.image.pk)


class ImageDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Displays a confirmation page for deleting an image. Accessible to superusers, moderators, and the image uploader.
    Upon successful deletion, the user is redirected to MyPhotosView.
    """
    model = Image
    template_name = 'delete_image.html'
    success_url = reverse_lazy('my_images')

    def test_func(self):
        """
        Checks whether the current user has the necessary permissions to delete the image.
        Returns True if the user is a superuser, the image uploader, or a moderator.
        """
        image = self.get_object()
        return self.request.user.is_superuser or self.request.user == image.user or moderators_check(self.request.user)

    def get_queryset(self):
        """
        Retrieves the queryset of images to be considered for deletion.
        Limits the queryset based on user permissions: superusers and moderators see all images,
        while regular users see only their own images.
        """
        if self.request.user.is_superuser or moderators_check(self.request.user):
            return super().get_queryset()
        return super().get_queryset().filter(user=self.request.user)


class RecentUploadedView(TemplateView):
    """
    A view that displays recently uploaded images with options to filter by categories.
    Images are sorted by upload date/time in descending order and displayed with pagination.
    """
    template_name = 'recent.html'

    def get_context_data(self, **kwargs):
        """
        Retrieves and organizes data to populate the context for the recent images view.
        Categories: Retrieves unique image categories and adds them to the context.
        Selected Category: Checks if a specific category is selected through GET parameters.
        If selected, filters images based on the category; otherwise, shows all images.
        Pagination: Divides the images into pages, with each page displaying up to 12 images.
        """
        context = super().get_context_data(**kwargs)

        # Retrieve unique image categories and add them to the context
        categories = set([category for category, _ in Image.CATEGORY_CHOICES])
        context['categories'] = categories

        # Check if a specific category is selected through GET parameters
        selected_category = self.request.GET.get('category')
        if selected_category:
            # Filter images based on the selected category and order by upload date/time
            images = Image.objects.filter(category=selected_category).order_by('-uploaded_at')
        else:
            # Show all images, ordered by upload date/time
            images = Image.objects.order_by('-uploaded_at')

        # pagination
        paginator = Paginator(images, 12)
        page_number = self.request.GET.get('page')
        page_object = paginator.get_page(page_number)

        context['recent_images'] = page_object
        context['selected_category'] = selected_category
        return context


class UserLoginView(LoginView):
    template_name = 'login.html'
    form_class = UserLoginForm


class UserRegistrationView(CreateView):
    """
    A view for user registration and account creation.
    """
    template_name = 'register.html'
    form_class = UserRegistrationForm

    def form_valid(self, form):
        """
        Process the registration form and log in the user upon successful registration.
        Redirect the user to the home page.
        """
        user = form.save()
        login(self.request, user)
        return redirect('home')


class AlbumListView(LoginRequiredMixin, ListView):
    """
    Show the albums created by the logged-in user ('My Albums' link)
    """
    model = Album
    template_name = "album_list.html"
    context_object_name = 'albums'

    def get_queryset(self):
        return Album.objects.filter(user=self.request.user)


class AlbumCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new album.
    Allows logged-in users to create albums to organize their uploaded images.
    """
    template_name = 'create_album.html'
    form_class = AlbumForm
    success_url = reverse_lazy('album_list')

    def form_valid(self, form):
        """
        Validates the submitted form and associates the album with the logged-in user.
        """
        form.instance.user = self.request.user
        return super().form_valid(form)


class AlbumImageView(LoginRequiredMixin, TemplateView):
    """
    View for displaying all images of a specific album.
    Accessible only by logged-in users.
    """
    template_name = 'album_images.html'

    def get_context_data(self, **kwargs):
        # Retrieve album information based on the provided album_id and user authentication
        album_id = self.kwargs['album_id']
        album = get_object_or_404(Album, id=album_id, user=self.request.user)
        context = {
            'album': album,
            'images': album.image_set.all(),
            'can_delete': True if self.request.user == album.user else False
        }

        return context


class AlbumDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View for deleting an album, accessible by album owners, superusers, and moderators.
    """
    model = Album
    template_name = 'delete_album.html'
    success_url = reverse_lazy('album_list')

    def test_func(self):
        """
        Test whether the current user is authorized to delete the album.
        """
        album = self.get_object()
        return self.request.user.is_superuser or self.request.user == album.user or moderators_check(self.request.user)

    def get_queryset(self):
        if self.request.user.is_superuser or moderators_check(self.request.user):
            return super().get_queryset()
        return super().get_queryset().filter(user=self.request.user)


class ProfileDetailsView(LoginRequiredMixin, DetailView):
    """
    View for displaying the profile page of the logged-in user ('My Profile' link).
    This view provides users with a personalized profile page that showcases various details about their account.
    Users can see the number of uploaded images, the count of albums they have created,
    the number of images marked as favorites, and the links to view them, as well as a link to edit their profile.
    """
    template_name = 'profile_details.html'
    model = User
    context_object_name = 'user'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = {
            "user": self.request.user,
            'albums_count': self.request.user.album_set.count(),
            'uploaded_images_count': self.request.user.image_set.count(),
            'favorites_count': Favorite.objects.filter(user=self.request.user).count(),
        }

        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    """
    View for editing the profile information of the logged-in user.
    """
    template_name = 'edit_profile.html'
    model = User
    fields = ['first_name', 'last_name', 'email', 'username']
    success_url = reverse_lazy('profile_details')

    def get_object(self, queryset=None):
        """
        Retrieve the logged-in user's profile for editing.
        """
        return self.request.user


class MyPhotosView(LoginRequiredMixin, ListView):
    """
    View that displays the uploaded images of the logged-in user.
    This view provides users with a page showcasing the images they have uploaded, accessible through the 'My Images' link.
    The images are presented in a paginated manner, sorted by their upload date and time in descending order. Users can
    also filter images by category, if available.
    """
    model = Image
    template_name = 'my_photos.html'
    context_object_name = 'photos'
    paginate_by = 12

    def get_queryset(self):
        """
        Retrieve the queryset of images uploaded by the logged-in user, optionally filtered by category,
        and sorted by their upload date and time in descending order.
        """

        # Filter the queryset to include only images uploaded by the logged-in user
        queryset = super().get_queryset().filter(user=self.request.user)

        # Get the selected category from the URL parameters (if provided)
        category = self.request.GET.get('category')

        # If a category is specified, further filter the queryset to include only images from that category
        if category:
            queryset = queryset.filter(category=category)

        # Sort the queryset by upload date and time, with the most recent images coming first
        queryset = queryset.order_by('-uploaded_at')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = set(Image.objects.filter(user=self.request.user).values_list('category', flat=True))
        context['categories'] = [category for category in categories if category]
        context['selected_category'] = self.request.GET.get('category')

        paginator = Paginator(context['photos'], self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['photos'] = page_obj
        return context


class ImageEditView(LoginRequiredMixin, UpdateView):
    """
    A view for editing image details, accessible by superusers, moderators, and image uploaders.
    Provides options to modify the title, album, category, width, and height of the image.
    Images can be resized if both the width and height fields are specified.
    """
    model = Image
    template_name = "image_edit.html"
    form_class = ImageEditForm

    def get_success_url(self):
        return reverse('image_details', kwargs={'pk': self.object.pk})

    def get_queryset(self):
        """
        Retrieves the queryset of images available for editing based on user permissions.
        Superusers and moderators can edit any image, while regular users can only edit their own images.
        """
        if self.request.user.is_superuser or moderators_check(self.request.user):
            return super().get_queryset()
        else:
            return Image.objects.filter(user=self.request.user)

    def get_form(self, form_class=None):
        """
        Retrieves the image editing form with dynamically populated options for album and category fields.
        Initializes the width and height fields with the original image dimensions.
        """
        form = super().get_form(form_class)
        form.fields['album'].queryset = Album.objects.filter(user=self.request.user)
        form.fields['category'].choices = Image.CATEGORY_CHOICES

        original_width = self.object.image.width
        original_height = self.object.image.height

        form.fields['width'].initial = original_width
        form.fields['height'].initial = original_height

        return form

    def form_valid(self, form):
        """
        Handles the form submission and updates the image details, including optional resizing.
        If both width and height fields are provided, the image is resized accordingly.
        """
        image = form.save(commit=False)
        # Get the values of width and height from the form's POST data
        width = self.request.POST.get('width')
        height = self.request.POST.get('height')

        # Check if both width and height are provided
        if width and height:
            # Get the path to the original image on the server
            original_image_path = image.image.path

            # Open the original image using Pillow
            with PILImage.open(original_image_path) as img:
                # Resize the image using the specified width and height values
                resized_img = img.resize((int(width), int(height)))

            # Define the path for the resized image
            resized_image_path = os.path.join(os.path.dirname(original_image_path),
                                              os.path.basename(original_image_path))

            # Save the resized image to the specified path with the same format as the original
            resized_img.save(resized_image_path, img.format)
            image.image.name = os.path.relpath(resized_image_path, start=settings.MEDIA_ROOT)

        return super().form_valid(form)


class UserListViewAdmin(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Admin view to display a list of users and the reported images.
    Accessible only by superusers and moderators.
    """
    model = User
    template_name = 'user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def test_func(self):
        """
        Checks whether the current user has the necessary permissions to access this view.
        Returns True if the user is a superuser or a moderator, otherwise denies access.
        """
        return self.request.user.is_superuser or moderators_check(self.request.user)

    def get_queryset(self):
        """
        Retrieves the queryset of users to be displayed, optionally filtered by search query.
        If a valid search query is provided, filters users based on username, first name, or last name.
        Returns a queryset containing all users if no search query is provided.
        """

        # Create an instance of the UserSearchForm using the GET data from the request.
        form = UserSearchForm(self.request.GET)
        if form.is_valid():
            search_query = form.cleaned_data['search_query']
            if search_query:
                # Use the User model's manager to filter users based on the search query.
                # The Q objects enable complex queries using logical OR conditions.
                return User.objects.filter(
                    Q(username__icontains=search_query) | Q(first_name__icontains=search_query) | Q(
                        last_name__icontains=search_query)
                )

        # If no valid search query is provided or the form is not valid,
        # return a queryset containing all users.
        return User.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UserSearchForm(self.request.GET)
        context['reports_count'] = Report.objects.all().count()
        return context


class UserDetailViewAdmin(LoginRequiredMixin, DetailView):
    """
    show the user details (from 'User Admin' link).
    show the firstname, lastname, email, username, uploaded images & albums count and links to view them.

    """
    model = User
    template_name = 'user_details.html'
    context_object_name = 'user'


class UserImageViewAdmin(LoginRequiredMixin, ListView):
    """
    View for displaying the uploaded images for a specific user.
    """
    template_name = 'user_images.html'
    model = Image
    context_object_name = 'images'
    paginate_by = 12

    def get_queryset(self):
        """
        Retrieves the queryset of images uploaded by the specific user.
        The images are filtered based on the provided pk and ordered by upload date/time in descending order.
        """
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        return Image.objects.filter(user=user).order_by('-uploaded_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(context['images'], self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['images'] = page_obj
        return context


class UserAlbumViewAdmin(LoginRequiredMixin, ListView):
    """
    View for the albums created by the specific user.
    """
    template_name = 'user_albums.html'
    model = Album
    context_object_name = 'albums'

    def get_queryset(self):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        return Album.objects.filter(user=user)


class UserAlbumImageViewAdmin(LoginRequiredMixin, TemplateView):
    """
    View for displaying the uploaded photos within a specific album for a particular user.
    """
    template_name = "album_images_admin.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs['pk']  # Retrieve the user ID from the URL parameters.
        album_id = self.kwargs['album_pk']  # Retrieve the album ID from the URL parameters.
        user = get_object_or_404(User, id=user_id)  # Get the user object based on the retrieved user ID.
        album = get_object_or_404(Album, id=album_id, user=user)  # Get the album associated with the user and album ID.

        # Retrieve the images within the album and order them by upload date/time in descending order.
        images = album.image_set.all().order_by('-uploaded_at')
        context['user'] = user
        context['album'] = album
        context['images'] = images
        return context


class UserDeleteViewAdmin(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View for deleting a user's account, accessible to superusers only.
    Upon successful deletion, the user's account, along with their attached images and albums, is removed.
    """
    model = User
    template_name = 'user_delete_confirmation.html'
    success_url = reverse_lazy('users_list')

    def test_func(self):
        """
        Performs a test to determine whether the logged-in user is a superuser.
        """
        return self.request.user.is_superuser

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        """
        Handles the deletion process of the user account, associated images, and albums.
        """
        user = self.get_object()  # Get the user object to be deleted.
        albums = Album.objects.filter(user=user)  # Retrieve albums associated with the user.
        images = Image.objects.filter(user=user)  # Retrieve images associated with the user.

        # Delete associated images from the filesystem and database.
        for image in images:
            image_path = os.path.join(settings.MEDIA_ROOT, str(image.image))
            if os.path.exists(image_path):
                os.remove(image_path)

        # Delete the albums and images from the database.
        albums.delete()
        images.delete()

        # Delete the user.
        return super().delete(request, *args, **kwargs)


class MyFavoriteView(LoginRequiredMixin, ListView):
    """
    Displays a list of favorite images for the logged-in user ('My Favorites' link in 'My Profile' page).
    The view retrieves and displays the images that the user has marked as favorites.
    """
    template_name = 'my_favorites.html'
    model = Image
    context_object_name = 'favorite_images'

    def get_queryset(self):
        """
        Retrieves the queryset of favorite images for the logged-in user.
        It filters images based on the user's favorites relationship.
        """
        return Image.objects.filter(favorite__user=self.request.user).order_by('-favorite__created_at')


class ReportImageView(LoginRequiredMixin, CreateView):
    """
    Allows users to report an image for inappropriate content or violations.
    Users can provide a detailed report by filling out the reporting form.
    """
    template_name = "report_image.html"
    form_class = ReportForm

    def get_context_data(self, **kwargs):
        """
        Retrieves the context data for rendering the reporting form.
        Adds the image associated with the report to the context.
        """
        context = super().get_context_data(**kwargs)
        context['image'] = get_object_or_404(Image, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        """
        Handles the submission of the reporting form and saves the report.
        If no existing report exists for the image, a new report is created.
        """
        image = get_object_or_404(Image, pk=self.kwargs['pk'])
        existing_report = Report.objects.filter(image=image).exists()
        if not existing_report:
            report = form.save(commit=False)
            image.is_private = True
            image.save()
            report.image = image
            report.reporter = self.request.user
            report.save()

        return redirect('recent')


class ReportedImagesView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Displays a list of reported images, accessible by superusers and moderators.
    Superusers and moderators can view and take actions on reported images, such as deleting images or canceling reports.
    """
    template_name = 'reported_images.html'
    model = Report
    context_object_name = 'reports'

    def test_func(self):
        """
        Checks if the logged-in user is a superuser or a moderator.
        """
        return self.request.user.is_superuser or moderators_check(self.request.user)

    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk)

        if 'delete' in request.POST:
            # Delete the reported image and the associated report
            report.image.delete()
            report.delete()
        elif 'cancel' in request.POST:
            # Delete the report without taking any action on the image
            report.image.is_private = False
            report.image.save()
            report.delete()

        return redirect('reported_images')
