import os

from django.shortcuts import render

from django.views.generic import TemplateView, FormView

# Custom:
from fotodb.models import Image
from fotodb.forms import MultipleImageForm


class MultipleImageView(FormView):
    """
    View for handling the upload of multiple images.

    Attributes:
        template_name (str): The name of the template to be used for rendering the view.
        form_class (class): The form class to be used for processing multiple image uploads.
        success_url (str): The URL to redirect to after a successful form submission.

    Methods:
        get(self, request, *args, **kwargs): Handle GET requests to render the form.
        get_form_kwargs(self): Customize form initialization by passing additional parameters.
        form_valid(self, form): Process the form and save each uploaded image.
    """
    template_name = 'multiple.html'
    form_class = MultipleImageForm
    success_url = '/successfully_uploaded'

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to render the form.

        Initialize the form with the current user to customize the available options.
        """
        form = self.form_class(user=request.user)
        return render(request, self.template_name, {'form': form})

    def get_form_kwargs(self):
        """
        Customize form initialization by passing additional parameters.

        Pass the current user to the form to customize available options.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
        Process the form and save each uploaded image.

        For each uploaded image, create a new Image instance and save it.
        Store the primary keys of the uploaded images in the session for later use.
        """
        images = form.cleaned_data['images']
        uploaded_image_pks = []

        for image in images:
            album = form.cleaned_data.get('album')
            is_private = form.cleaned_data.get('is_private', False)
            new_image = Image(
                image=image,
                title=os.path.splitext(image.name)[0],
                user=self.request.user if self.request.user.is_authenticated else None,
                is_private=is_private,
                album=album,
                category=form.cleaned_data['category']
            )

            new_image.save()
            uploaded_image_pks.append(new_image.pk)

        self.request.session['uploaded_images'] = uploaded_image_pks
        return super().form_valid(form)


class SuccessfullyUploadedView(TemplateView):
    """
    View for displaying a success message after images have been successfully uploaded.

    Attributes:
        template_name (str): The name of the template to be used for rendering the view.

    Methods:
        get_context_data(self, **kwargs): Retrieve and prepare data to be used in the template.
    """
    template_name = 'successfully_uploaded.html'

    def get_context_data(self, **kwargs):
        """
        Retrieve and prepare data to be used in the template.

        Retrieve the primary keys of uploaded images from the session.
        Query the database to get the Image instances associated with those primary keys.
        """
        context = super().get_context_data(**kwargs)
        uploaded_image_pks = self.request.session.get('uploaded_images', [])
        context['uploaded_images'] = Image.objects.filter(pk__in=uploaded_image_pks)
        return context