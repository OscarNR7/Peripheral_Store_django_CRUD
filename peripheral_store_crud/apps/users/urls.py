from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.UserCreateView.as_view(), name='register'),
    path('profile/<int:pk>/', views.UserProfileView.as_view(), name='profile_detail'),
    path('profile/<int:pk>/update/', views.UserUpdateView.as_view(), name='profile_update'),
    path('users-list/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
]