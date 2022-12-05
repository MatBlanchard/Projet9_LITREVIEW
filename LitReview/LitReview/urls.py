from django.contrib import admin
from django.urls import path
from listings import views

urlpatterns = [
    path('login/', views.login)
]
