from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'categories'

urlpatterns = [
    path('', views.CategoryListView.as_view(), name='category_list'),
    path('/create-category/', views.CategoryCreateView.as_view(), name='category_create'),
    path('/<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
]