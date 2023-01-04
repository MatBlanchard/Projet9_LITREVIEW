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
    path('unfollow/<int:follow_id>', views.unfollow, name='unfollow'),
    path('review-existing_ticket/<int:ticket_id>', views.review_existing_ticket, name='review-existing_ticket'),
    path('delete_ticket/<int:ticket_id>', views.delete_ticket, name='delete_ticket'),
    path('update_ticket/<int:ticket_id>', views.update_ticket, name='update_ticket'),
    path('delete_review/<int:review_id>', views.delete_review, name='delete_review'),
    path('update_review/<int:review_id>', views.update_review, name='update_review'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
