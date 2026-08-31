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
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.view_profile, name='view_profile'),
    path('users/search/', views.search_users, name='search_users'),
    path('accounts/signup/', views.signup, name='signup'),
    path('cc/', views.cc, name='cc'),
    path('stuco/', views.stuco, name='stuco'),
    path('notifications/', views.notifications, name='notifications'),
    path('house_standings/', views.house_standings, name='house_standings'),
    path('vote/create/', views.create_vote, name='create_vote'),
    path('vote/<int:vote_id>/vote/', views.vote_vote, name='vote_vote'),
    path('price/<int:price_id>/like/', views.like_price, name='like_price'),
    ]