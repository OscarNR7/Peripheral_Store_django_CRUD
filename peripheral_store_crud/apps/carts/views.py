from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.db import transaction
from django.utils import timezone
from .models import Cart, CartItem
from apps.products.models import Product
from apps.orders.models import Order, OrderItem
from apps.users.models import Address
from decimal import Decimal
import json

# Create your views here.
class CartView(LoginRequiredMixin, View):
    """Vista del carrito"""
    template_name = 'cart.html'

    def get(self, request):
        """Muestra el carrtio del usuario"""
        try: 
            #se obtiene el carrito del usaurio y sus direcciones
            cart, created = Cart.objects.get_or_create(user=request.user)
            shipping_addresses = Address.objects.filter(user = request.user, address_type = 'shipping')
            billing_addresses = Address.objects.filter(user = request.user, address_type = 'billing')

            context = {
                'cart': cart,
                'cart_items': cart.items.all(),
                'subtotal': cart.subtotal,
                'shipping_addresses': shipping_addresses,
                'billing_addresses': billing_addresses,
            }
            return render(request, self.template_name, context)
        except Exception as e:
            messages.error(request, f"Error loading cart: {str(e)}")
            return redirect('public_products:catalog_list')

class AddToCartView(LoginRequiredMixin, View):
    """Vista para añadir productos al carrito"""
    def post(self, request):
        """Añade un producto al carrito"""
        try:
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))
            
            if not product_id or quantity <= 0:
                messages.error(request, "Invalid product or quantity")
                return redirect('public_products:catalog_list')
            
            # Obtener o crear el carrito y añade el producto al carrito
            cart, created = Cart.objects.get_or_create(user=request.user)
            success, message = cart.add_product(product_id, quantity)
            
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)
            
            # Si es una solicitud AJAX devolver respuesta JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': success,
                    'message': message,
                    'cart_count': cart.total_items,
                    'subtotal': str(cart.subtotal)
                })
            
            #Redireccionar a la pagina anterior o al catalogo
            referer = request.META.get('HTTP_REFERER')
            return redirect(referer if referer else 'public_products:catalog_list')
        
        except Exception as e:
            messages.error(request, f"Error adding to cart: {str(e)}")
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                })
            
            return redirect('public_products:catalog_list')

class UpdateCartItemView(LoginRequiredMixin, View):
    """Vista para actualizar la cantidad de un item en el carrito"""
    def post(self, request, item_id):
        """Actualiza la cantidad de un item en el carrito"""
        try:
            quantity = int(request.POST.get('quantity', 0))
            
            # Obtener el carrito del usuario y actualizar la cantidad del item
            cart = get_object_or_404(Cart, user=request.user)
            success, message = cart.update_item_quantity(item_id, quantity)
            
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)
            
            #Si es una solicitud AJAX, devolver respuesta JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': success,
                    'message': message,
                    'cart_count': cart.total_items,
                    'subtotal': str(cart.subtotal)
                })
            
            return redirect('carts:cart')
            
        except Exception as e:
            messages.error(request, f"Error updating cart: {str(e)}")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                })
            return redirect('carts:cart')
    
class RemoveFromCartView(LoginRequiredMixin, View):
    """Vista para eliminar un item del carrito"""
    def post(self, request, item_id):
        """Elimina un item del carrito"""
        try:
            cart = get_object_or_404(Cart, user=request.user)
            
            #Eliminar el item del carrito
            success, message = cart.remove_item(item_id)
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)
            
            # Si es una solicitud AJAX, devolver respuesta JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': success,
                    'message': message,
                    'cart_count': cart.total_items,
                    'subtotal': str(cart.subtotal)
                })
            return redirect('carts:cart')
            
        except Exception as e:
            messages.error(request, f"Error removing item: {str(e)}")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                })
            return redirect('carts:cart')
        
class ClearCartView(LoginRequiredMixin, View):
    """Vista para vaciar el carrito"""
    def post(self, request):
        """Vacía el carrito del usuario"""
        try:
            cart = get_object_or_404(Cart, user=request.user)
            
            # Vaciar el carrito
            cart.clear()
            messages.success(request, "Cart cleared successfully")
            
            # Si es una solicitud AJAX, devolver respuesta JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': "Cart cleared successfully",
                    'cart_count': 0,
                    'subtotal': '0.00'
                })
            
            return redirect('carts:cart')
            
        except Exception as e:
            messages.error(request, f"Error clearing cart: {str(e)}")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                })
            return redirect('carts:cart')

class CheckoutView(LoginRequiredMixin, View):
    """Vista para procesar el checkout y convertir el carrito en una orden"""
    template_name = 'checkout.html'
    
    def get(self, request):
        """Muestra la pagina de checkout"""
        try:
            cart = get_object_or_404(Cart, user=request.user)
            # Verificar que el carrito tenga items
            if cart.items.count() == 0:
                messages.error(request, "Your cart is empty")
                return redirect('carts:cart')
            #Verificar stock antes de proceder
            for item in cart.items.all():
                if item.quantity > item.product.stock:
                    messages.error(
                        request,
                        f"Not enough stock for {item.product.name}. Only {item.product.stock} available."
                    )
                    return redirect('carts:cart')
            #obtener las direcciones del usuario
            shipping_addresses = Address.objects.filter(user=request.user,address_type='shipping')
            billing_addresses = Address.objects.filter(user=request.user,address_type='billing')
            
            context = {
                'cart': cart,
                'cart_items': cart.items.all(),
                'subtotal': cart.subtotal,
                'shipping_addresses': shipping_addresses,
                'billing_addresses': billing_addresses,
                'payment_methods': Order.PAYMENT_METHOD_CHOICES,
            }
            return render(request, self.template_name, context)
        except Exception as e:
            messages.error(request, f"Error in checkout: {str(e)}")
            return redirect('carts:cart')
    
    def post(self, request):
        """Procesa el checkout y crea la orden"""
        try:
            cart = get_object_or_404(Cart, user=request.user)
            
            #Verificar que el carrito tenga items
            if cart.items.count() == 0:
                messages.error(request, "Your cart is empty")
                return redirect('carts:cart')
            
            # Obtener datos del formulario
            shipping_address_id = request.POST.get('shipping_address')
            billing_address_id = request.POST.get('billing_address')
            payment_method = request.POST.get('payment_method')
            notes = request.POST.get('notes')
            
            # Validar direcciones
            try:
                shipping_address = Address.objects.get(id=shipping_address_id,user=request.user,address_type='shipping')
            except Address.DoesNotExist:
                messages.error(request, "Please select a valid shipping address")
                return redirect('carts:checkout')
            
            try:
                billing_address = Address.objects.get(id=billing_address_id,user=request.user,address_type='billing')
            except Address.DoesNotExist:
                messages.error(request, "Please select a valid billing address")
                return redirect('carts:checkout')
            
            # Validar método de pago
            if payment_method not in dict(Order.PAYMENT_METHOD_CHOICES):
                messages.error(request, "Please select a valid payment method")
                return redirect('carts:checkout')
            
            # Verificar stock antes de proceder
            for item in cart.items.all():
                if item.quantity > item.product.stock:
                    messages.error(request,f"Not enough stock for {item.product.name}. Only {item.product.stock} available.")
                    return redirect('carts:cart')

            # Crear la orden y los items de la orden en una transaccion
            with transaction.atomic():
                #Crear la orden
                order = Order.objects.create(
                    user=request.user,
                    subtotal=cart.subtotal,
                    shipping_cost=Decimal('300.00'),
                    tax=Decimal('120.00'),            
                    discount=Decimal('0.00'),
                    shipping_address=shipping_address,
                    billing_address=billing_address,
                    payment_method=payment_method,
                    payment_status='pending',
                    status='pending',
                    notes=notes
                )
                
                # Calcular el total (activara save() y generara el order_number)
                order.save()
                # Crear los items de la orden
                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        unit_price=cart_item.product.price,
                        total_price=cart_item.total_price
                    )
                    # Actualizar el stock del producto
                    product = cart_item.product
                    product.stock -= cart_item.quantity
                    product.save()
                
                #Vaciar el carrito
                cart.clear()
                messages.success(request,f"Your order has been placed successfully. Order number: {order.order_number}")
                return redirect('orders:order_detail', order_number=order.order_number)
        except Exception as e:
            messages.error(request, f"Error processing order: {str(e)}")
            return redirect('carts:checkout')