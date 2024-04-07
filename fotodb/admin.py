from django.contrib import admin
from django.contrib.auth.models import Group

# Register your models here.
from .models import Album, Image


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'user')
    list_filter = ('user', 'title',)
    search_fields = ('title', 'user__username')
    ordering = ('title',)
    list_per_page = 20


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'uploaded_at', 'user', 'album', 'is_private', 'category')
    list_filter = ('uploaded_at', 'user', 'album', 'is_private', 'category')
    search_fields = ('title', 'user__username')
    ordering = ('-uploaded_at',)
    list_per_page = 20


admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'member_count')

    def member_count(self, obj):
        return obj.user_set.count()

    member_count.short_description = 'Member Count'
