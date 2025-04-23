from django.shortcuts import render
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from .models import Order, OrderItem
from .forms import OrderForm, OrderItemForm
from django.db import transaction

# Create your views here.
class OrderDashboardView(LoginRequiredMixin, UserPassesTestMixin, View):
    '''Vista de las estadisticas de los pedidos'''
    template_name = 'order_dashboard.html'

    def test_func(self):
        """Verifica si el usuario es staff"""
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        """Redirige a catalogo si no tiene permisos"""
        return redirect('public_products:catalog_list')

    def get(self, request, *args, **kwargs):
        """Obtiene estadisticas de pedidos"""
        try:
            total_orders = Order.objects.count()
            pending_orders = Order.objects.filter(status='pending').count()
            processing_orders = Order.objects.filter(status='processing').count()
            shipped_orders = Order.objects.filter(status='shipped').count()
            delivered_orders = Order.objects.filter(status='delivered').count()
            cancelled_orders = Order.objects.filter(status='cancelled').count()
            
            # Obtener las ultimos pedidos
            latest_orders = Order.objects.all().order_by('-created_at')[:10]
            
            context = {
                'total_orders': total_orders,
                'pending_orders': pending_orders,
                'processing_orders': processing_orders,
                'shipped_orders': shipped_orders,
                'delivered_orders': delivered_orders,
                'cancelled_orders': cancelled_orders,
                'latest_orders': latest_orders,
            }
            return render(request, self.template_name, context)
        except Exception as e:
            messages.error(request, f"Error loading dashboard: {str(e)}")
            return redirect('orders:order_list')
    
class OrderListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    '''Vista de la lista de pedidos'''
    model = Order
    template_name = 'order_list.html'
    context_object_name = 'orders'
    paginate_by = 15

    def test_func(self):
        """Verifica si el usuario es staff"""
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        """Redirige a catalogo si no tiene permisos"""
        return redirect('public_products:catalog_list')

    def get_queryset(self):
        """Filtra pedidos por busqueda y estado"""
        try:
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
        except Exception as e:
            messages.error(self.request, f"Error filtering orders: {str(e)}")
            return Order.objects.none()

    def get_context_data(self, **kwargs):
        """Agrega opciones de filtro al contexto"""
        try:
            context = super().get_context_data(**kwargs)
            context['status_choices'] = Order.STATUS_CHOICES
            context['q'] = self.request.GET.get('q', '')
            context['status'] = self.request.GET.get('status', '')
            return context
        except Exception as e:
            messages.error(self.request, f"Error loading context data: {str(e)}")
            return super().get_context_data(**kwargs)

class OrderDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    '''Vista individual de los pedidos'''
    model = Order
    context_object_name = 'order'
    template_name = 'order_detail.html'
    slug_field = 'order_number'
    slug_url_kwarg = 'order_number'

    def test_func(self):
        """Verifica si el usuario es staff"""
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        """Redirige a catalogo si no tiene permisos"""
        return redirect('public_products:catalog_list')
    
    def get_object(self, queryset=None):
        """Obtiene el pedido y maneja errores"""
        try:
            return super().get_object(queryset)
        except Exception as e:
            messages.error(self.request, f"Order not found: {str(e)}")
            return None
    
    def get_context_data(self, **kwargs):
        """Agrega items y opciones de estado al contexto"""
        try:
            context = super().get_context_data(**kwargs)
            context['order_items'] = self.object.items.all()
            context['status_choices'] = Order.STATUS_CHOICES
            context['payment_status_choices'] = Order.PAYMENT_STATUS_CHOICES
            return context
        except Exception as e:
            messages.error(self.request, f"Error loading order details: {str(e)}")
            return super().get_context_data(**kwargs)
    
    def get(self, request, *args, **kwargs):
        """Maneja la visualizacion del detalle con control de errores"""
        self.object = self.get_object()
        if self.object is None:
            return redirect('orders:order_list')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
    
class OrderUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vista para actualizar pedidos"""
    model = Order
    form_class = OrderForm
    template_name = 'order_form.html'
    slug_field = 'order_number'
    slug_url_kwarg = 'order_number'

    def test_func(self):
        """Verifica si el usuario es staff"""
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        """Redirige a catalogo si no tiene permisos"""
        return redirect('public_products:catalog_list')
    
    def get_object(self, queryset=None):
        """Obtiene el pedido y maneja errores"""
        try:
            return super().get_object(queryset)
        except Exception as e:
            messages.error(self.request, f"Order not found: {str(e)}")
            return None
    
    def get(self, request, *args, **kwargs):
        """Maneja la visualizacion del formulario con control de errores"""
        self.object = self.get_object()
        if self.object is None:
            return redirect('orders:order_list')
        return super().get(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        """Prepara parametros para el formulario"""
        try:
            kwargs = super().get_form_kwargs()
            kwargs['user'] = self.object.user
            return kwargs
        except Exception as e:
            messages.error(self.request, f"Error preparing form: {str(e)}")
            return super().get_form_kwargs()

    def form_valid(self, form):
        """Procesa formulario valido"""
        try:
            with transaction.atomic():
                response = super().form_valid(form)
                messages.success(self.request, f'Order #{self.object.order_number} updated successfully.')
                return response
        except Exception as e:
            messages.error(self.request, f"Error updating order: {str(e)}")
            return self.form_invalid(form)

    def get_success_url(self):
        """URL de redireccion tras actualizacion exitosa"""
        return reverse('orders:order_detail', kwargs={'order_number': self.object.order_number})
    
class OrderItemUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vista para actualizar items de pedido"""
    model = OrderItem
    form_class = OrderItemForm
    template_name = 'orderitem_form.html'
    pk_url_kwarg = 'item_id'

    def test_func(self):
        """Verifica si el usuario es staff"""
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        """Redirige a catalogo si no tiene permisos"""
        return redirect('public_products:catalog_list')

    def get_object(self, queryset=None):
        """Obtiene el item de pedido"""
        try:
            order_number = self.kwargs.get('order_number')
            item_id = self.kwargs.get('item_id')
            return get_object_or_404(OrderItem, id=item_id, order__order_number=order_number)
        except Exception as e:
            messages.error(self.request, f"Order item not found: {str(e)}")
            return None
    
    def get(self, request, *args, **kwargs):
        """Maneja la visualizacion del formulario con control de errores"""
        self.object = self.get_object()
        if self.object is None:
            return redirect('orders:order_list')
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """Agrega pedido relacionado al contexto"""
        try:
            context = super().get_context_data(**kwargs)
            context['order'] = self.object.order
            return context
        except Exception as e:
            messages.error(self.request, f"Error loading context: {str(e)}")
            return super().get_context_data(**kwargs)
    
    def form_valid(self, form):
        """Procesa formulario valido y recalcula totales"""
        try:
            with transaction.atomic():
                response = super().form_valid(form)
                order = self.object.order
                # Recalculacion del total del pedido
                order.recalculate_totals()
                messages.success(self.request, 'Order item updated successfully.')
                return response
        except Exception as e:
            messages.error(self.request, f"Error updating order item: {str(e)}")
            return self.form_invalid(form)
    
    def get_success_url(self):
        """URL de redireccion tras actualizacion exitosa"""
        order_number = self.object.order.order_number
        return reverse('orders:order_detail', kwargs={'order_number': order_number})
    
class OrderItemDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Vista para eliminar un item de pedido"""
    model = OrderItem
    template_name = 'orderitem_delete_confirm.html'
    success_url = reverse_lazy('orders:order_list')
    pk_url_kwarg = 'item_id'

    def test_func(self):
        """Verifica si el usuario es staff"""
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        """Redirige a catalogo si no tiene permisos"""
        return redirect('public_products:catalog_list')

    def get_object(self, queryset=None):
        """Obtiene el item de pedido"""
        try:
            order_number = self.kwargs.get('order_number')
            item_id = self.kwargs.get('item_id')
            return get_object_or_404(OrderItem, id=item_id, order__order_number=order_number)
        except Exception as e:
            messages.error(self.request, f"Order item not found: {str(e)}")
            return None
    
    def get(self, request, *args, **kwargs):
        """Maneja la visualizacion de confirmacion con control de errores"""
        self.object = self.get_object()
        if self.object is None:
            return redirect('orders:order_list')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Agrega pedido relacionado al contexto"""
        try:
            context = super().get_context_data(**kwargs)
            context['order'] = self.object.order
            return context
        except Exception as e:
            messages.error(self.request, f"Error loading context: {str(e)}")
            return super().get_context_data(**kwargs)

    def delete(self, request, *args, **kwargs):
        """Elimina item y recalcula totales"""
        try:
            with transaction.atomic():
                order_item = self.get_object()
                if order_item is None:
                    return redirect('orders:order_list')
                
                order = order_item.order
                
                # Eliminar el item
                order_item.delete()
                # Recalculacion del total del pedido
                order.recalculate_totals()
                
                messages.success(request, 'Order item deleted successfully.')
                return redirect('orders:order_detail', order_number=order.order_number)
        except Exception as e:
            messages.error(request, f"Error deleting order item: {str(e)}")
            return redirect('orders:order_list')

class OrderUpdateStatusView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Vista para actualizar rápidamente el estado del pedido"""

    def test_func(self):
        """Verifica si el usuario es staff"""
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        """Redirige a catalogo si no tiene permisos"""
        return redirect('public_products:catalog_list')
    
    def post(self, request, order_number):
        """Actualiza el estado del pedido"""
        try:
            order = get_object_or_404(Order, order_number=order_number)
            new_status = request.POST.get('status')

            if new_status in dict(Order.STATUS_CHOICES):
                order.status = new_status
                order.save()
                messages.success(request, 'Order status updated successfully.')
            else:
                messages.error(request, 'Invalid status provided.')
                
            return redirect('orders:order_detail', order_number=order_number)
        except Order.DoesNotExist:
            messages.error(request, "Order not found")
            return redirect('orders:order_list')
        except Exception as e:
            messages.error(request, f"Error updating order status: {str(e)}")
            return redirect('orders:order_list')

class OrderUpdatePaymentStatusView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Vista para actualizar rápidamente el estado de pago"""
    
    def test_func(self):
        """Verifica si el usuario es staff"""
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        """Redirige a catalogo si no tiene permisos"""
        return redirect('public_products:catalog_list')
    
    def post(self, request, order_number):
        """Actualiza el estado de pago del pedido"""
        try:
            order = get_object_or_404(Order, order_number=order_number)
            new_status = request.POST.get('payment_status')

            if new_status in dict(Order.PAYMENT_STATUS_CHOICES):
                order.payment_status = new_status
                order.save()
                messages.success(request, 'Payment status updated successfully.')
            else:
                messages.error(request, 'Invalid payment status provided.')

            return redirect('orders:order_detail', order_number=order_number)
        except Order.DoesNotExist:
            messages.error(request, "Order not found")
            return redirect('orders:order_list')
        except Exception as e:
            messages.error(request, f"Error updating payment status: {str(e)}")
            return redirect('orders:order_list')
