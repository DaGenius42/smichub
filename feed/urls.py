from django.urls import path
from . import views

app_name = 'feed'
urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('userpost/<int:post_id>/', views.user_post, name='user_post'),
    path('news/<int:news_id>/', views.news_post, name='news_post'),
    path('userpost/create/', views.create_post, name='create_post'),
    path('userpost/delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('userpost/comment/<int:post_id>/', views.create_comment, name='create_comment'),
    path('userpost/like/<int:post_id>/', views.like_post, name='like_post'),
    path('news/like/<int:news_id>/', views.like_news, name='like_news'),
    ]