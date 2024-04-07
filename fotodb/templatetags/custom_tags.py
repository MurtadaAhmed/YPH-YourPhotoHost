from django import template

from django.contrib.auth.models import Group

register = template.Library()


@register.filter
def is_moderator(user):
    return user.groups.filter(name='Moderators').exists()
