from django.urls import path
from . import views

app_name = 'carts'

urlpatterns = [
    #Vista principal del carrito
    path('', views.CartView.as_view(), name='cart'),
    
    #Gestion de productos en el carrito
    path('add/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('update/<int:item_id>/', views.UpdateCartItemView.as_view(), name='update_cart_item'),
    path('remove/<int:item_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('clear/', views.ClearCartView.as_view(), name='clear_cart'),
    
    #checkout
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
]