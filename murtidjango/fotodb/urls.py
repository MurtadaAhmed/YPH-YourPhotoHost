# Built-in
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView as UserLogoutView
# custom
from .views import HomeView, RecentUploadedView, UserLoginView, UserRegistrationView, AlbumListView, AlbumCreateView, \
    AlbumImageView, ImageDetailView, AlbumDeleteView, ImageDeleteView, ProfileDetailsView, EditProfileView, \
    MyPhotosView, ImageEditView, UserListViewAdmin, UserDetailViewAdmin, UserDeleteViewAdmin, UserImageViewAdmin, \
    UserAlbumViewAdmin, UserAlbumImageViewAdmin, TempMainView

urlpatterns = [
    path('', TempMainView.as_view(), name='main_page'),
    path('home/', HomeView.as_view(), name='home'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('recent/', RecentUploadedView.as_view(), name='recent'),
    path('albums/', AlbumListView.as_view(), name='album_list'),
    path('albums/create/', AlbumCreateView.as_view(), name='create_album'),
    path('albums/<int:album_id>/', AlbumImageView.as_view(), name='album_images'),
    path('image/<int:pk>/', ImageDetailView.as_view(), name='image_details'),
    path('albums/<int:pk>/delete/', AlbumDeleteView.as_view(), name='delete_album'),
    path('image/<int:pk>/delete', ImageDeleteView.as_view(), name='delete_image'),
    path('profile/', ProfileDetailsView.as_view(), name='profile_details'),
    path('profile/edit/', EditProfileView.as_view(), name='edit_profile'),
    path('images/', MyPhotosView.as_view(), name='my_images'),
    path('image/<int:pk>/edit/', ImageEditView.as_view(), name='image_edit'),

    # superusers/moderators urls:
    path('users', UserListViewAdmin.as_view(), name='users_list'),
    path('users/<int:pk>/', UserDetailViewAdmin.as_view(), name='user_detail'),
    path('users/<int:pk>/images/', UserImageViewAdmin.as_view(), name='user_images'),
    path('users/<int:pk>/albums/', UserAlbumViewAdmin.as_view(), name='user_albums'),
    path('users/<int:pk>/delete/', UserDeleteViewAdmin.as_view(), name='user_delete'),
    path('users/<int:pk>/albums/<int:album_pk>/images/', UserAlbumImageViewAdmin.as_view(), name='admin_album_images'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)