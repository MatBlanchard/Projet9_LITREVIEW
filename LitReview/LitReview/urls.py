from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.LoginPageView.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('signup/', views.signup_page, name='signup'),
    path('flux/', views.flux, name='flux'),
    path('posts/', views.posts, name='posts'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('ticket/', views.ticket_form, name='ticket'),
    path('review/', views.review_form, name='review'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
