from django.urls import path
from . import views

app_name = 'public_products'

urlpatterns = [
    path('catalog/', views.CatalogView.as_view(), name='catalog_list'),
    path('product/<slug:slug>/public/', views.PublicProductDetailView.as_view(), name='public_product_detail'),
]