from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from apps.products.models import Product
from apps.users.models import User, Address
from django.db.models import Sum

# Create your models here.
class Order(models.Model):
    '''
    modelo del pedido
    '''
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    PAYMENT_METHOD_CHOICES = (
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='User')
    order_number = models.CharField(max_length=20, unique=True, verbose_name='Order Number')
    billing_address = models.ForeignKey(Address, on_delete=models.SET_NULL, related_name='billing_orders', 
                                       null=True, blank=True, verbose_name='Billing Address')
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, related_name='shipping_orders', 
                                        null=True, blank=True, verbose_name='Shipping Address')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Status')
    payment_status = models.CharField(max_length=20,blank=True, null=True, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name='Payment Status')
    payment_method = models.CharField(max_length=20, blank=True, null=True,choices=PAYMENT_METHOD_CHOICES, verbose_name='Payment Method')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Subtotal')
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Shipping Cost')
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Tax')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Discount')
    total = models.DecimalField(max_digits=10 ,decimal_places=2, verbose_name='Total',blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True, verbose_name='Tracking Number')
    notes = models.TextField(blank=True, null=True, verbose_name='Notes')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    estimated_delivery_date = models.DateField(null=True, blank=True, verbose_name='Estimated Delivery Date')

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Order {self.order_number} by {self.user.get_full_name()}'
    def get_absolute_url(self):
        return reverse('orders:order_detail', kwargs={'order_number': self.order_number})
    
    def save(self, *args, **kwargs):
        #metodo para generar el numero de pedido, usando timestamp y el ID del usuario
        if not self.order_number:
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.order_number = f'{self.user.id}-{timestamp}'
    
        self.calculate_total()
    
        super().save(*args, **kwargs)

    def calculate_total(self):
        """Calcula el total del del pedido sin tocas el subtotal"""
        self.total = self.subtotal + self.shipping_cost + self.tax - self.discount
        return self.total

    def recalculate_totals(self):
        """Recalcula el subtotal y el total del pedido"""
        agg = self.items.aggregate(sum=Sum('total_price'))
        self.subtotal = agg.get('sum') or 0
        self.calculate_total()
       
        self.save(update_fields=['subtotal', 'total'])

class OrderItem(models.Model):
    """
    Modelo para los items del pedido
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Order')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items', verbose_name='Product')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Quantity')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Unit Price')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Total Price')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        unique_together = ('order', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.order_number}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
