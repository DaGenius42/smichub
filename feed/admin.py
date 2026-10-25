from django.contrib import admin
from .models import Post, News, House, Comments, CustomUser, Vote, Price, Notification
# Register your models here.
admin.site.register(Post)
admin.site.register(House)
admin.site.register(Comments)
admin.site.register(CustomUser)
admin.site.register(Vote)
admin.site.register(Price)
admin.site.register(Notification)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not change:
            # Used by the post_save signal to attribute the StuCo notification.
            obj._created_by = request.user
        super().save_model(request, obj, form, change)