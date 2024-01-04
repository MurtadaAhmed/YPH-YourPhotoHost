import os
from urllib.parse import urlparse

from django.utils.text import slugify

from django.views.generic import CreateView
from django.urls import reverse_lazy
from urllib.request import urlopen, HTTPError
from django.core.files import File

# Custom:
from fotodb.models import Image, Album
from fotodb.forms import ImageForm


class HomeView(CreateView):
    """
    View for handling image uploads and displaying the home page.

    Attributes:
        template_name (str): The name of the template to be used for rendering the view.
        form_class (class): The form class to be used for processing image uploads.

    Methods:
        get_form(self, form_class=None): Customize the form based on user authentication status.
        form_valid(self, form): Process the form and save the image, handling both URL and file uploads.
        get_success_url(self): Define the URL to redirect to after a successful form submission.
    """
    template_name = 'index.html'
    form_class = ImageForm

    def get_form(self, form_class=None):
        """
        Customize the form based on the user's authentication status.

        If the user is not logged in, remove private and album options.
        If the user is logged in, limit album choices to albums owned by the user.
        Set available category choices for both authenticated and guest users.
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
        Process the form and save the image, handling both URL and file uploads.

        If URL is provided, fetch the image from the URL and save it.
        If file is uploaded, save it and associate it with the logged-in user.
        Generate a title if not provided.
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
        """
        Define the URL to redirect to after a successful form submission.

        Redirect to the image details page for the newly uploaded image.
        """
        return reverse_lazy('image_details', kwargs={'pk': self.object.pk})
