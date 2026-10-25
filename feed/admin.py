from django.contrib import admin
from .models import Post, News, House, Comments, CustomUser, Vote, Price, Notification
# Register your models here.
admin.site.register(Post)
admin.site.register(News)
admin.site.register(House)
admin.site.register(Comments)
admin.site.register(CustomUser)
admin.site.register(Vote)
admin.site.register(Price)
admin.site.register(Notification)