# apps/orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.OrderDashboardView.as_view(), name='order_dashboard'),
    
    # Order CRUD
    path('', views.OrderListView.as_view(), name='order_list'),
    path('<slug:order_number>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('<slug:order_number>/edit/', views.OrderUpdateView.as_view(), name='order_update'),
    
    # Order Status Updates
    path('<slug:order_number>/update-status/', views.OrderUpdateStatusView.as_view(), name='order_update_status'),
    path('<slug:order_number>/update-payment-status/', views.OrderUpdatePaymentStatusView.as_view(), name='order_update_payment_status'),
    
    # Order Items
    path('<slug:order_number>/items/<int:item_id>/edit/', views.OrderItemUpdateView.as_view(), name='order_item_update'),
    path('<slug:order_number>/items/<int:item_id>/delete/', views.OrderItemDeleteView.as_view(), name='order_item_delete'),
]