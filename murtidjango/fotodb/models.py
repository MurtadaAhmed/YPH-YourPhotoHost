from django.db import models

from django.contrib.auth.models import User


# Album model
class Album(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


# Image uploading model. options are (Title/Upload Photo/Select Album/Category/public or private)
class Image(models.Model):
    CATEGORY_CHOICES = (
        (None, '---'),
        ('animal', 'Animal'),
        ('human', 'Human'),
        ('nature', 'Nature'),
        ('sports', 'Sports'),
        ('food', 'Food'),
        ('architecture', 'Architecture'),
        ('technology', 'Technology'),
        ('travel', 'Travel'),
        ('music', 'Music'),
        ('art', 'Art'),
        ('other', 'Other'),
    )

    title = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, blank=True, null=True)
    is_private = models.BooleanField(default=False)
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES, default=None, blank=True, null=True)

    def __str__(self):
        return self.title


# photo comment section, has the user and the image as foreign keys, text and created_at
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.created_at}'


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'image')


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
