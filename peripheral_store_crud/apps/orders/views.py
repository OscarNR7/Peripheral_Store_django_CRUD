from django.shortcuts import render
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, View
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Sum, Count
from django.http import HttpResponseRedirect
from django.utils import timezone
from .models import Order, OrderItem
from .forms import OrderForm, OrderItemForm
from apps.users.models import User, Address
from apps.products.models import Product

# Create your views here.

class OrderDashboardView(View):
    '''Vista de las estadisticas de los pedidos'''
    template_name = 'order_dashboard.html'

    def get(self,request,*args,**kwargs):
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        processing_orders = Order.objects.filter(status='processing').count()
        shipped_orders = Order.objects.filter(status='shipped').count()
        delivered_orders = Order.objects.filter(status='delivered').count()
        cancelled_orders = Order.objects.filter(status='cancelled').count()
        
        #obtener las ultimos pedidos
        latest_orders = Order.objects.all().order_by('-created_at')[:10]
        
        context = {'total_orders': total_orders,'pending_orders': pending_orders,'processing_orders': processing_orders,
            'shipped_orders': shipped_orders,'delivered_orders': delivered_orders,'cancelled_orders': cancelled_orders,
            'latest_orders': latest_orders,}
        return render(request, self.template_name, context)
    
class OrderListView(ListView):
    '''vista de la lista de pedidos'''
    model = Order
    template_name = 'order_list.html'
    context_object_name = 'orders'
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(order_number__icontains=q) |
                Q(user__email__icontains=q) |
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q)
            )
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['status_choices'] = Order.STATUS_CHOICES
        context['q'] = self.request.GET.get('q', '')
        context['status'] = self.request.GET.get('status', '')
        return context

class OrderDetailView(DetailView):
    '''vista individual de los pedidos'''
    model = Order
    context_object_name = 'order'
    template_name = 'order_detail.html'
    slug_field = 'order_number'
    slug_url_kwarg = 'order_number'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_items'] = self.object.items.all()
        context['status_choices'] = Order.STATUS_CHOICES
        context['payment_status_choices'] = Order.PAYMENT_STATUS_CHOICES
        return context
    
class OrderUpdateView(UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'order_form.html'
    slug_field = 'order_number'
    slug_url_kwarg = 'order_number'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.object.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Order #{self.object.order_number} updated successfully.')
        return response

    def get_success_url(self):
        return reverse('orders:order_detail', kwargs={'order_number': self.object.order_number})
    
class OrderItemUpdateView(UpdateView):
    model = OrderItem
    form_class = OrderItemForm
    template_name = 'orderitem_form.html'
    pk_url_kwarg = 'item_id'

    def get_object(self, queryset=None):
        order_number = self.kwargs.get('order_number')
        item_id = self.kwargs.get('item_id')
        return get_object_or_404(OrderItem, id=item_id, order__order_number=order_number)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.object.order
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        order = self.object.order
     #reculaculacion del total del pedido
        order.recalculate_totals()

        messages.success(self.request, 'Order item updated successfully.')
        return response
    
    def get_success_url(self):
        order_number = self.object.order.order_number
        return reverse('orders:order_detail', kwargs={'order_number': order_number})
    
class OrderItemDeleteView(DeleteView):
    """View para eliminar un item de pedido"""
    model = OrderItem
    template_name = 'orderitem_delete_confirm.html'
    success_url = reverse_lazy('orders:order_list')
    pk_url_kwarg = 'item_id'

    def get_object(self, queryset=None):
        order_number = self.kwargs.get('order_number')
        item_id = self.kwargs.get('item_id')
        return get_object_or_404(OrderItem, id=item_id, order__order_number=order_number)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.object.order
        return context

    def delete(self, request, *args, **kwargs):
        order_item = self.get_object()
        order = order_item.order

        # eliminar el item
        order_item.delete()
        #reculaculacion del total del pedido
        order.recalculate_totals()

        messages.success(request, 'Order item deleted successfully.')
        return redirect('orders:order_detail', order_number=order.order_number)

class OrderUpdateStatusView(View):
    """Vista para actualizar rápidamente el estado del pedido"""

    def post(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number)
        new_status = request.POST.get('status')

        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, 'Order status updated successfully.')
        else:
            messages.error(request, 'Invalid status provided.')

        return redirect('orders:order_list', order_number=order_number)

class OrderUpdatePaymentStatusView(View):
    """Vista para actualizar rápidamente el estado de pago"""

    def post(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number)
        new_status = request.POST.get('payment_status')

        if new_status in dict(Order.PAYMENT_STATUS_CHOICES):
            order.payment_status = new_status
            order.save()
            messages.success(request, 'Payment status updated successfully.')
        else:
            messages.error(request, 'Invalid payment status provided.')

        return redirect('orders:order_detail', order_number=order_number)
