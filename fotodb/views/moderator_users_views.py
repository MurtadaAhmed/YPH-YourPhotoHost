import os
from django.conf import settings
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404

from django.views.generic import TemplateView, ListView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy

# Custom:
from fotodb.models import Image, Album, Report
from fotodb.forms import UserSearchForm


def moderators_check(user):
    """
    function to check if the logged-in user belong to moderators group. used in:
    ImageDetailView, ImageDeleteView, AlbumDeleteView, ImageEditView
    """
    return user.groups.filter(name='Moderators').exists()


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
