from django import forms
from django.core.exceptions import ValidationError

from .models import Order, OrderItem
from apps.users.models import Address
from apps.products.models import Product


class OrderForm(forms.ModelForm):
    """Formulario para crear/actulizar pedido"""
    class Meta:
        model = Order
        fields = ['status', 'payment_method', 'payment_status', 'tracking_number',
                 'notes', 'estimated_delivery_date', 'subtotal', 'shipping_cost', 
                 'tax', 'discount', 'billing_address', 'shipping_address']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'estimated_delivery_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['billing_address'].queryset = Address.objects.filter(
                user=self.user, address_type='billing'
            )
            self.fields['shipping_address'].queryset = Address.objects.filter(
                user=self.user, address_type='shipping'
            )
            
            self.fields['billing_address'].required = False
            self.fields['shipping_address'].required = False

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        if commit:
            instance.save()
        return instance

class OrderItemForm(forms.ModelForm):
    """Formulario para crear/actualizar items de un pedido"""
    class Meta:
        model = OrderItem
        fields = ['order', 'product', 'quantity', 'unit_price']

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity', 0)
        product = self.cleaned_data.get('product')
        if product and quantity > product.stock:
            raise ValidationError(f"Only {product.stock} units available in stock.")
        return quantity
