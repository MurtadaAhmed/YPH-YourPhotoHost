# Generated by Django 4.2.3 on 2023-07-25 19:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fotodb', '0010_alter_image_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='tags',
        ),
        migrations.DeleteModel(
            name='Like',
        ),
        migrations.DeleteModel(
            name='Tag',
        ),
    ]
