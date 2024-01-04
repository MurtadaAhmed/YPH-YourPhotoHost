import os

from PIL import Image as PILImage
from django.conf import settings
from django.core.paginator import Paginator

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views import View

from django.views.generic import TemplateView, DetailView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect

# Custom:
from fotodb.models import Image, Album, Comment, Like, Favorite
from fotodb.forms import ImageEditForm, CommentForm


def moderators_check(user):
    """
    function to check if the logged-in user belong to moderators group. used in:
    ImageDetailView, ImageDeleteView, AlbumDeleteView, ImageEditView
    """
    return user.groups.filter(name='Moderators').exists()

class ImageDetailView(DetailView):
    """
    View for displaying detailed information about an uploaded image.

    Attributes:
        template_name (str): The name of the template to be used for rendering the view.
        model (class): The model class to be used for querying the database.
        context_object_name (str): The variable name to use in the template for the retrieved object.

    Methods:
        get_context_data(self, **kwargs): Retrieve and prepare data to be used in the template.
        post(self, request, *args, **kwargs): Handle POST requests, such as user actions like liking and commenting.
    """
    template_name = 'image_detail.html'
    model = Image
    context_object_name = 'image'

    def get_context_data(self, **kwargs):
        """
        Retrieve and prepare data to be used in the template.

        Check if the user is a moderator.
        Determine if the image can be viewed based on privacy settings and user authentication.
        Determine if the user has permission to delete the image.
        Provide image dimensions, size, and comments to the template.
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
        Handle POST requests, such as user actions like liking and commenting.

        Redirect to login if the user is not authenticated.
        Process user actions like liking, unliking, favoriting, and unfavorite.
        Save submitted comments and redirect to the image details page.
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


class ImageDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View for handling the deletion of an image. Accessible to superusers, moderators, and the image uploader.

    Inherits from LoginRequiredMixin and UserPassesTestMixin to enforce authentication
    and user permission checks before allowing the deletion.

    Inherits from DeleteView to simplify the handling of image deletion.

    Attributes:
        model (class): The model class to be used for querying the database.
        template_name (str): The name of the template to be used for rendering the view.
        success_url (str): The URL to redirect to after a successful image deletion.

    Methods:
        test_func(self): Check if the current user has the necessary permissions to delete the image.
        get_queryset(self): Limit the queryset based on user permissions.
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



class DeleteCommentView(View):
    """
    View for handling the deletion of a comment.

    Inherits from View to handle HTTP methods, specifically POST in this case.

    Methods:
        post(self, request, pk, *args, **kwargs): Handle the deletion of a comment.
    """

    def post(self, request, pk, *args, **kwargs):
        """
        Handle the deletion of a comment.

        Retrieve the comment object using the provided primary key.
        Check if the current user has the necessary permissions to delete the comment
        (image uploader, comment owner, moderator, or superuser).
        Delete the comment and redirect to the image details page.
        """
        comment = get_object_or_404(Comment, pk=pk)

        if self.request.user == comment.image.user or self.request.user == comment.user or self.request.user.is_superuser or moderators_check(
                self.request.user):
            comment.delete()
        return redirect('image_details', pk=comment.image.pk)