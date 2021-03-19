from django.contrib import admin

from .models import Comment, Follow, Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display = ("text", "pub_date", "author", "group",)
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "description")
    search_fields = ("description",)
    empty_value_display = "-пусто-"


class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'created')
    search_fields = ("post",)
    empty_value_display = "-пусто-"
    list_filter = ('created', )


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('author',)
    list_filter = ('user', )


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
