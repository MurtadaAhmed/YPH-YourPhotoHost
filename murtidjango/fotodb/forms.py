# built-in
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# custom
from .models import Image, Album, Comment


class ImageForm(forms.ModelForm):
    """
    image uploading form.
    it has a validation for the image size not to exceed 15 MB.
    """
    MAX_FILE_SIZE = 15 * 1024 * 1024

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_private'].label = "Private"

    class Meta:
        model = Image
        fields = ['title', 'image', 'is_private', 'album', 'category']
        widgets = {
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > self.MAX_FILE_SIZE:
                raise ValidationError(f'File size cannot exceed {self.MAX_FILE_SIZE / 2048} MB!')
        return image


class ImageEditForm(forms.ModelForm):
    """
    image edit form.
    it has a validation for the maximum width and height not to exceed 4000 pixels.
    """
    width = forms.IntegerField(label='Width', required=False)
    height = forms.IntegerField(label='Height', required=False)

    class Meta:
        model = Image
        fields = ['title', 'is_private', 'album', 'category']

    def clean(self):
        cleaned_data = super().clean()
        width = cleaned_data.get('width')
        height = cleaned_data.get('height')
        max_width = 4000
        max_height = 4000

        if width and height:
            if width > max_width or height > max_height:
                raise forms.ValidationError("Width or height exceeds 4000")

        return cleaned_data


class UserRegistrationForm(UserCreationForm):
    """
    register form showing username, email, password and password confirmation.
    labels are removed and replaced with placeholders for all the field.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = False
        self.fields['password1'].label = False
        self.fields['password2'].label = False
        self.fields['email'].label = False
        self.fields['username'].widget.attrs['placeholder'] = 'Enter your username'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter your email address'
        self.fields['password1'].widget.attrs['placeholder'] = 'Enter your password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm the password'

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# Login form
class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = False
        self.fields['password'].label = False
        self.fields['username'].widget.attrs['placeholder'] = 'Enter your username'
        self.fields['password'].widget.attrs['placeholder'] = 'Enter your password'

    class Meta:
        model = User
        fields = ['username', 'password']


class AlbumForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = False
        self.fields['title'].widget.attrs['placeholder'] = 'Enter New Album Name'

    class Meta:
        model = Album
        fields = ('title',)


# superusers forms

class UserSearchForm(forms.Form):
    search_query = forms.CharField(label='', max_length=100, required=False)


class UserDeleteForm(forms.Form):
    confirmation = forms.BooleanField(label='Are you sure you want to delete this user?', required=True)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {'text': forms.Textarea(attrs={'rows': 2, 'cols': 5})}
        labels = {'text': False}
