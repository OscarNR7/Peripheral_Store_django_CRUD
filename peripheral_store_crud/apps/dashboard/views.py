from django.views.generic import TemplateView
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from apps.orders.models import Order
from apps.products.models import Product
from apps.users.models import User

class DashboardView(TemplateView):
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Order statistics
        total_orders = Order.objects.count()
        context['total_orders'] = total_orders
        
        # Order status counts
        pending_orders = Order.objects.filter(status='pending').count()
        processing_orders = Order.objects.filter(status='processing').count()
        shipped_orders = Order.objects.filter(status='shipped').count()
        delivered_orders = Order.objects.filter(status='delivered').count()
        cancelled_orders = Order.objects.filter(status='cancelled').count()
        
        context['pending_orders'] = pending_orders
        context['processing_orders'] = processing_orders
        context['shipped_orders'] = shipped_orders
        context['delivered_orders'] = delivered_orders
        context['cancelled_orders'] = cancelled_orders
        
        # Calculate percentages for progress bars
        if total_orders > 0:
            context['pending_percentage'] = (pending_orders / total_orders) * 100
            context['processing_percentage'] = (processing_orders / total_orders) * 100
            context['shipped_percentage'] = (shipped_orders / total_orders) * 100
            context['delivered_percentage'] = (delivered_orders / total_orders) * 100
            context['cancelled_percentage'] = (cancelled_orders / total_orders) * 100
        
        # Recent orders
        context['latest_orders'] = Order.objects.all().order_by('-created_at')[:10]
        
        # Product statistics
        context['total_products'] = Product.objects.count()
        context['low_stock_products'] = Product.objects.filter(stock__lte=5).order_by('stock')[:5]
        
        # User statistics
        context['total_users'] = User.objects.count()
        context['latest_users'] = User.objects.all().order_by('-date_joined')[:5]
        
        # Revenue statistics
        revenue = Order.objects.filter(status__in=['delivered', 'shipped']).aggregate(
            total=Sum('total')
        )
        context['total_revenue'] = revenue['total'] if revenue['total'] else 0
        
        return context