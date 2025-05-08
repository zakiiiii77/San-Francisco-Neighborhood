from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='roommates/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/create/', views.create_room, name='create_room'),
    path('rooms/<int:room_id>/', views.room_detail, name='room_detail'),
    path('rooms/<int:room_id>/add-member', views.add_member, name='add_member'),
    path('rooms/<int:room_id>/tasks/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    path('rooms/<int:room_id>/tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('dashboard/<int:room_id>/', views.room_dashboard, name='room_dashboard'),
    path('tasks/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('rooms/<int:room_id>/add-task/', views.add_task, name='add_task'),
    path('rooms/<int:room_id>/members-partial/', views.room_members_partial, name='room_members_partial'),
    path('todo/<int:task_id>/add_comment', views.add_comment, name='add_comment'),
    path('spotify/login/', views.spotify_login, name='spotify_login'),
    path('spotify/callback/', views.spotify_callback, name='spotify_callback')
]