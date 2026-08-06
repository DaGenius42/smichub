from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
app_name = 'accounts'
urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('', auth_views.LoginView.as_view(template_name='registrations/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]