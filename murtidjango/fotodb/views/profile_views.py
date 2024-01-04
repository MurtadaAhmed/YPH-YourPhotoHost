
from django.core.paginator import Paginator

from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.models import User
from django.urls import reverse_lazy


# Custom:
from fotodb.models import Image, Favorite


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