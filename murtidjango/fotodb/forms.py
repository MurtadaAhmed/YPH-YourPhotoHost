# built-in
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from multiupload.fields import MultiFileField

# custom
from .models import Image, Album, Comment, Report

from django import forms
from .models import Image


class ImageForm(forms.ModelForm):
    MAX_FILE_SIZE = 15 * 1024 * 1024

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_private'].label = "Private"
        self.fields['image'].label = False
        self.fields['url'].label = False
        self.fields['title'].label = False

        self.fields['image'].widget.attrs['placeholder'] = "Upload an image"
        self.fields['url'].widget.attrs['placeholder'] = "Enter image URL (if not uploading from your computer)"
        self.fields['title'].widget.attrs['placeholder'] = "Title (optional)"

    url = forms.URLField(required=False, label="Image URL")

    class Meta:
        model = Image
        fields = ['image', 'url', 'title', 'is_private', 'album', 'category']
        widgets = {
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        url = cleaned_data.get('url')

        if not image and not url:
            raise forms.ValidationError("You must upload an image or provide an image URL.")

        if image and url:
            raise forms.ValidationError("You can only use either image upload or URL, not both.")

        return cleaned_data

    def clean_image(self):
        image = self.cleaned_data.get('image')
        url = self.cleaned_data.get('url')

        if image and url:
            raise forms.ValidationError("You can only use either image upload or URL, not both.")

        if image:
            if image.size > self.MAX_FILE_SIZE:
                raise forms.ValidationError(f'File size cannot exceed {self.MAX_FILE_SIZE / 1024 / 1024} MB!')

        return image


class MultipleImageForm(forms.Form):
    MAX_FILE_SIZE = 15 * 10000 * 10000

    images = MultiFileField(min_num=1, max_num=10, max_file_size=MAX_FILE_SIZE)
    is_private = forms.BooleanField(required=False, label='Private')
    album = forms.ModelChoiceField(queryset=Album.objects.none(), required=False, label='Album')
    category = forms.ChoiceField(choices=Image.CATEGORY_CHOICES, required=False, label='Category')

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if self.user and self.user.is_authenticated:
            self.fields['album'].queryset = Album.objects.filter(user=self.user)
            self.fields['is_private'].widget = forms.CheckboxInput(attrs={'class': 'form-check-input'})
        else:
            self.fields.pop('is_private')
            self.fields.pop('album')











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


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason']
