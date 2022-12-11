from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.LoginPageView.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('signup/', views.signup_page, name='signup'),
    path('flux/', views.flux, name='flux'),
]
