from django.urls import path
from . import views, consumers
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
    path('rooms/<int:room_id>/add-todo', views.add_todo, name='add_todo'),
    path('rooms/<int:room_id>/add-member', views.add_member, name='add_member'),
    path('rooms/<int:room_id>/todos/<int:todo_id>/edit/', views.edit_todo, name='edit_todo'),
    path('rooms/<int:room_id>/todos/<int:todo_id>/remove/', views.delete_todo, name='delete_todo'),
]