# Built-in
import os
from PIL import Image as PILImage
from django.conf import settings
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.utils.text import slugify
from django.views.generic import TemplateView, CreateView, ListView, DetailView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse
from django.contrib import messages

# Custom:
from .models import Image, Album, Comment, Like, Favorite, Report
from .forms import ImageForm, UserRegistrationForm, UserLoginForm, AlbumForm, UserSearchForm, UserDeleteForm, \
    ImageEditForm, CommentForm, ReportForm


def moderators_check(user):
    """
    function to check if the logged-in user belong to moderators group. used in:
    ImageDetailView, ImageDeleteView, AlbumDeleteView, ImageEditView, UserListViewAdmin,
    UserDetailViewAdmin, UserImageViewAdmin, UserAlbumViewAdmin, UserAlbumImageViewAdmin
    """
    return user.groups.filter(name='Moderators').exists()


class TempMainView(TemplateView):
    # website home page view
    template_name = 'home.html'


class HomeView(CreateView):
    """
    project home page view:
    form_class >> image upload form
    """
    template_name = 'index.html'
    form_class = ImageForm

    def get_form(self, form_class=None):
        """
        if the user is logged-in, it will show the private & album options.
        the category is shows for the users and guests
        """
        form = super().get_form(form_class)
        if not self.request.user.is_authenticated:
            form.fields.pop('is_private')
            form.fields.pop('album')
        else:
            form.fields['album'].queryset = Album.objects.filter(user=self.request.user)
        form.fields['category'].choices = Image.CATEGORY_CHOICES
        return form

    def form_valid(self, form):
        """
        if no title is provided, the image is title is generated from the image file name.
        if user is logged-in the uploaded image will be related to the logged-in user.
        """
        image = form.save(commit=False)
        if not image.title:
            file_name = os.path.splitext(self.request.FILES['image'].name)[0]
            slug = slugify(file_name)
            image.title = slug
        if self.request.user.is_authenticated:
            image.user = self.request.user
        image.save()
        self.request.uploaded_image = image
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('image_details', kwargs={'pk': self.request.uploaded_image.pk})


class ImageDetailView(DetailView):
    """
    shows the details of the uploaded image.
    """
    template_name = 'image_detail.html'
    model = Image
    context_object_name = 'image'

    def get_context_data(self, **kwargs):
        """
        if image owner or moderator, they can see edit/delete options.
        comment form is shown only if the users are logged-in.
        """
        context = super().get_context_data(**kwargs)
        is_moderator = moderators_check(self.request.user)
        image = self.get_object()
        if self.request.user == image.user:
            context['can_delete'] = True
        else:
            context['can_delete'] = False
        context['is_moderator'] = is_moderator
        context['dimensions'] = f'{image.image.width} X {image.image.height} '
        context['size'] = f'{image.image.size / 1000:.1f} kB'
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
        post method for the comment section.
        if the post is successful, it will return be to the same image details page
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
                    Like.objects.create(user=self.request.user, image=image)
            elif action == 'unlike':
                if liked:
                    Like.objects.filter(user=self.request.user, image=image).delete()
            elif action == 'favorite':
                if not favorite:
                    Favorite.objects.create(user=self.request.user, image=image)
            elif action == 'unfavorite':
                if favorite:
                    Favorite.objects.filter(user=self.request.user, image=image).delete()
            else:
                return HttpResponseRedirect(reverse('image_details', kwargs={'pk': image.pk}))

        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.image = image
            comment.save()
            return HttpResponseRedirect(reverse('image_details', kwargs={'pk': image.pk}))

        return self.get(request, *args, **kwargs)


class ImageDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    image delete confirmation page.
    page is shown only to superusers, moderators and the image uploader.
    upon successful deletion, the user if forwarded to MyPhotosView.
    """
    model = Image
    template_name = 'delete_image.html'
    success_url = reverse_lazy('my_images')

    def test_func(self):
        image = self.get_object()
        return self.request.user.is_superuser or self.request.user == image.user or moderators_check(self.request.user)

    def get_queryset(self):
        if self.request.user.is_superuser or moderators_check(self.request.user):
            return super().get_queryset()
        return super().get_queryset().filter(user=self.request.user)


class RecentUploadedView(TemplateView):
    """
    show all uploaded images ('All Uploaded Images' link).
    show the images divided by categories (if any), sorted by upload date/time in descending order.
    has pagination to show 12 images per page

    """
    template_name = 'recent.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = set([category for category, _ in Image.CATEGORY_CHOICES])
        context['categories'] = categories
        selected_category = self.request.GET.get('category')
        if selected_category:
            images = Image.objects.filter(category=selected_category).order_by('-uploaded_at')
        else:
            images = Image.objects.order_by('-uploaded_at')
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
    # forward to login page upon successful registration
    template_name = 'register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')


class AlbumListView(LoginRequiredMixin, ListView):
    # show the albums created by the logged-in user ('My Albums' link)
    model = Album
    template_name = "album_list.html"
    context_object_name = 'albums'

    def get_queryset(self):
        return Album.objects.filter(user=self.request.user)


class AlbumCreateView(LoginRequiredMixin, CreateView):
    template_name = 'create_album.html'
    form_class = AlbumForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class AlbumImageView(LoginRequiredMixin, TemplateView):
    """
    show all images of the specific album.
    accessible by logged_in users only.
    """
    template_name = 'album_images.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
    album delete view, accessible by album owners, superusers and moderators
    """
    model = Album
    template_name = 'delete_album.html'
    success_url = reverse_lazy('album_list')

    def test_func(self):
        album = self.get_object()
        return self.request.user.is_superuser or self.request.user == album.user or moderators_check(self.request.user)

    def get_queryset(self):
        if self.request.user.is_superuser or moderators_check(self.request.user):
            return super().get_queryset()
        return super().get_queryset().filter(user=self.request.user)


class ProfileDetailsView(LoginRequiredMixin, DetailView):
    """
    show the profile page of the logged-in user('My Profile' link).
    it shows the username, email address, uploaded images and album count, and Edit profile link.
    """
    template_name = 'profile_details.html'
    model = User
    context_object_name = 'user'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = {
            "user": self.request.user,
            'albums_count': self.request.user.album_set.count(),
            'uploaded_images_count': self.request.user.image_set.count()
        }

        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    """
    edit profile page accessible by the logged-in user.
    it has the option to change firstname, lastname, email and username.
    """
    template_name = 'edit_profile.html'
    model = User
    fields = ['first_name', 'last_name', 'email', 'username']
    success_url = reverse_lazy('profile_details')

    def get_object(self, queryset=None):
        return self.request.user


class MyPhotosView(LoginRequiredMixin, ListView):
    """
    shows the uploaded images by the logged-in user('My Images' link).
    shows the categories of the uploaded images (if any).
    images are sorted by the upload date/time in descending order.
    it has pagination to show images per page.
    """
    model = Image
    template_name = 'my_photos.html'
    context_object_name = 'photos'
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
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
    image edit view, accessible by superusers, moderators and image uploader.
    it has the options: title, album, category, width, height.
    the image can be resized only if both width and height fields are true.
    """
    model = Image
    template_name = "image_edit.html"
    form_class = ImageEditForm

    def get_success_url(self):
        return reverse('image_details', kwargs={'pk': self.object.pk})

    def get_queryset(self):
        if self.request.user.is_superuser or moderators_check(self.request.user):
            return super().get_queryset()
        else:
            return Image.objects.filter(user=self.request.user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['album'].queryset = Album.objects.filter(user=self.request.user)
        form.fields['category'].choices = Image.CATEGORY_CHOICES

        original_width = self.object.image.width
        original_height = self.object.image.height

        form.fields['width'].initial = original_width
        form.fields['height'].initial = original_height

        return form

    def form_valid(self, form):
        image = form.save(commit=False)
        width = self.request.POST.get('width')
        height = self.request.POST.get('height')

        if width and height:
            original_image_path = image.image.path

            with PILImage.open(original_image_path) as img:
                resized_img = img.resize((int(width), int(height)))

            resized_image_path = os.path.join(os.path.dirname(original_image_path),
                                              os.path.basename(original_image_path))
            resized_img.save(resized_image_path, img.format)
            image.image.name = os.path.relpath(resized_image_path, start=settings.MEDIA_ROOT)

        return super().form_valid(form)


# superusers/moderators views

class UserListViewAdmin(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    a view to list the registered users ('User Admin' link).
    accessible by superusers and moderators only.
    has a search function to search for users by firstname, lastname or username.
    delete user button is visible to superusers only.
    has pagination to list 20 users per page.
    """
    model = User
    template_name = 'user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_superuser or moderators_check(self.request.user)

    def get_queryset(self):
        form = UserSearchForm(self.request.GET)
        if form.is_valid():
            search_query = form.cleaned_data['search_query']
            if search_query:
                return User.objects.filter(
                    Q(username__icontains=search_query) | Q(first_name__icontains=search_query) | Q(
                        last_name__icontains=search_query)
                )
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
    view the uploaded images for the specific user.

    """
    template_name = 'user_images.html'
    model = Image
    context_object_name = 'images'
    paginate_by = 12


    def get_queryset(self):
        username = self.kwargs['pk']
        user = get_object_or_404(User, pk=username)
        return Image.objects.filter(user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(context['images'], self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['images'] = page_obj
        return context


class UserAlbumViewAdmin(LoginRequiredMixin, ListView):
    """
    view the albums for the specific user.
    """
    template_name = 'user_albums.html'
    model = Album
    context_object_name = 'albums'


    def get_queryset(self):
        username = self.kwargs['pk']
        user = get_object_or_404(User, pk=username)
        return Album.objects.filter(user=user)


class UserAlbumImageViewAdmin(LoginRequiredMixin, TemplateView):
    """
    view the uploaded photo for the album for the specific user.
    show the username of the album creator and the album name when accessed.
    """
    template_name = "album_images_admin.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs['pk']
        album_id = self.kwargs['album_pk']
        user = get_object_or_404(User, id=user_id)
        album = get_object_or_404(Album, id=album_id, user=user)
        images = album.image_set.all()
        context['user'] = user
        context['album'] = album
        context['images'] = images
        return context


class UserDeleteViewAdmin(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    user delete view accessible by superusers only.
    once submitted successfully, it deletes the user along with the attached images and albums.
    """
    model = User
    template_name = 'user_delete_confirmation.html'
    success_url = reverse_lazy('users_list')

    def test_func(self):
        return self.request.user.is_superuser

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        albums = Album.objects.filter(user=user)
        images = Image.objects.filter(user=user)
        for image in images:
            image_path = os.path.join(settings.MEDIA_ROOT, str(image.image))
            if os.path.exists(image_path):
                os.remove(image_path)
        albums.delete()
        images.delete()

        return super().delete(request, *args, **kwargs)


class MyFavoriteView(LoginRequiredMixin, ListView):
    template_name = 'my_favorites.html'
    model = Image
    context_object_name = 'favorite_images'
    paginate_by = 12

    def get_queryset(self):
        return Image.objects.filter(favorite__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = set(Image.objects.filter(favorite__user=self.request.user).values_list('category', flat=True))
        context['categories'] = [category for category in categories if category]
        context['selected_category'] = self.request.GET.get('category')
        return context


class ReportImageView(LoginRequiredMixin, CreateView):
    template_name = "report_image.html"
    form_class = ReportForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['image'] = get_object_or_404(Image, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        image = get_object_or_404(Image, pk=self.kwargs['pk'])
        existing_report = Report.objects.filter(image=image).exists()
        if not existing_report:
            report = form.save(commit=False)
            report.image = image
            report.reporter = self.request.user
            report.save()
        return redirect('recent')


class ReportedImagesView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'reported_images.html'
    model = Report
    context_object_name = 'reports'

    def test_func(self):
        return self.request.user.is_superuser or moderators_check(self.request.user)

    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk)

        if 'delete' in request.POST:

            report.image.delete()
            report.delete()
        elif 'cancel' in request.POST:

            report.delete()


        return redirect('reported_images')


