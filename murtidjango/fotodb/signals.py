from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.conf import settings


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        subject = 'Welcome to YPH'
        message = (
            f'Hi {instance.username},\n\nWelcome to our website! Thank you for registering an account with us.'
            f'Please keep your login credentials safe and do not share them with anyone.\n\n'
            f'If you have any questions or need assistance, feel free to contact us at {settings.DEFAULT_FROM_EMAIL}.'
        )
        to = instance.email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[to],
        )
