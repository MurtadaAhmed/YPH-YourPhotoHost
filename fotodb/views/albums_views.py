from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, CreateView, ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy

# Custom:
from fotodb.models import Album
from fotodb.forms import AlbumForm


def moderators_check(user):
    """
    function to check if the logged-in user belong to moderators group. used in:
    ImageDetailView, ImageDeleteView, AlbumDeleteView, ImageEditView
    """
    return user.groups.filter(name='Moderators').exists()


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
