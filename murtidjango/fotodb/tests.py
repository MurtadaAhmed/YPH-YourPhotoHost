import os

from django import forms
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from django.test import TestCase

from .forms import ImageForm, MultipleImageForm
from .models import Album, Image, Comment, Like, Favorite, Report
from django.db.utils import IntegrityError


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testusername", password="testpassword")
        self.album = Album.objects.create(title="testalbum", user=self.user)
        self.image = Image.objects.create(title='testimage', user=self.user, album=self.album)

    def tearDown(self):
        Comment.objects.all().delete()
        Like.objects.all().delete()
        Favorite.objects.all().delete()
        Report.objects.all().delete()
        Image.objects.all().delete()
        Album.objects.all().delete()
        User.objects.all().delete()

    def test_album_correct_name_return_true(self):
        album = Album.objects.get(pk=self.album.pk)
        self.assertEqual(str(album), 'testalbum')

    def test_album_creation_invalid_title_raised_integrity_error(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Album.objects.create(title=None, user=self.user)

    def test_image_title_return_true(self):
        image = Image.objects.get(pk=self.image.pk)
        self.assertEqual(str(image), 'testimage')

    def test_comment_user_and_creation_date_return_true(self):
        comment = Comment.objects.create(user=self.user, image=self.image, text='text')
        self.assertEqual(str(comment), f'{self.user.username} - {comment.created_at}')

    def test_invalid_comment_creation_user_none_raises_integrity_error(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Comment.objects.create(user=None, image=self.image, text='test')

    def test_invalid_comment_creation_image_none_raises_integrity_error(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Comment.objects.create(user=self.user, image=None, text='test')

    def test_like_creation_is_instance_return_true(self):
        like = Like.objects.create(user=self.user, image=self.image)
        self.assertTrue(isinstance(like, Like))

    def test_invalid_like_creation_user_raises_integrity_error(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Like.objects.create(user=None, image=self.image)

    def test_invalid_like_creation_image_raises_integrity_error(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Like.objects.create(user=self.user, image=None)

    def test_favorite_creation_is_instance_return_true(self):
        favorite = Favorite.objects.create(user=self.user, image=self.image)
        self.assertTrue(isinstance(favorite, Favorite))

    def test_invalid_favorite_creation_user_none_raises_integrity_error(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Favorite.objects.create(user=None, image=self.image)

    def test_invalid_favorite_creation_image_none_raises_integrity_error(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Favorite.objects.create(user=self.user, image=None)

    def test_report_creation_is_instance_return_true(self):
        report = Report.objects.create(reporter=self.user, image=self.image, reason="testreport")
        self.assertTrue(isinstance(report, Report))

    def test_invalid_report_creation_user_none_raises_exception(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Report.objects.create(reporter=None, image=self.image, reason="testreport")


class FormTests(TestCase):

    def test_valid_image_file_upload_form_return_true(self):
        image_path = os.path.join(os.path.dirname(__file__), 'test.jpeg')

        with open(image_path, 'rb') as f:
            image = f.read()
            image_file = SimpleUploadedFile('test.jpeg', image, content_type='image/jpeg')

        form_data = {
            'title': 'testimage',
            'is_private': False,
            'album': None,
            'category': None,
        }
        files = {
            'image': image_file
        }
        form = ImageForm(data=form_data, files=files)

        self.assertTrue(form.is_valid())

    def test_valid_image_url_upload_form_return_true(self):
        image_url = 'https://i.ibb.co/42YMbpc/puppy.jpg'

        form_data = {
            'title': "testimage",
            'url': image_url,
            'is_private': False,
            'album': None,
            'category': None,
        }

        form = ImageForm(data=form_data)
        print(form.errors)
        self.assertTrue(form.is_valid())

    def test_valid_multiple_images_upload_form_return_true(self):
        first_image_path = os.path.join(os.path.dirname(__file__), 'test.jpeg')
        second_image_path = os.path.join(os.path.dirname(__file__), 'test1.jpeg')

        with open(first_image_path, 'rb') as fi, open(second_image_path, 'rb') as si:
            first_image = fi.read()
            second_image = si.read()
            image_file_1 = SimpleUploadedFile('test.jpeg', first_image, content_type='image/jpeg')
            image_file_2 = SimpleUploadedFile('test1.jpeg', second_image, content_type='image/jpeg')

        form_data = {
            'is_private': False,
            'album': False,
            'category': None,
        }

        files = {
            'images': [image_file_1, image_file_2]
        }

        form = MultipleImageForm(data=form_data, files=files)

        self.assertTrue(form.is_valid())

    def test_invalid_image_form_no_image_or_url_raises_validation_error(self):
        form_data = {
            'title': 'testimage',
            'is_private': False,
            'album': None,
            'category': None,
        }

        form = ImageForm(data=form_data)

        self.assertFalse(form.is_valid())

        with self.assertRaises(forms.ValidationError) as ve:
            form.clean()

        self.assertIn("You must upload an image or provide an image URL.", str(ve.exception))