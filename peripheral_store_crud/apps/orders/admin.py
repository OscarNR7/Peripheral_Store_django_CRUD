from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    autocomplete_fields = ['product']
    fields = ['product', 'quantity', 'total_price']
    readonly_fields = ['total_price']
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        
        # Inicializa unit_price con el precio del producto cuando se selecciona
        if 'product' in form.base_fields:
            widget = form.base_fields['product'].widget
            widget.attrs['onchange'] = 'setUnitPrice(this)'
            
        return formset

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user_info', 'total', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status')
        }),
        ('Address Information', {
            'fields': ('billing_address', 'shipping_address')
        }),
        # ('Payment Information', {
        #     'fields': ('payment_method', 'payment_status')
        # }),
        ('Financial Details', {
            'fields': ('subtotal', 'shipping_cost', 'tax', 'discount', 'total')
        }),
        ('Additional Information', {
            'fields': ('tracking_number', 'estimated_delivery_date', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_info(self, obj):
        """Display user information with link to user admin"""
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name())
    
    user_info.short_description = 'Customer'

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        
        for instance in instances:
            if isinstance(instance, OrderItem):
                # Si el producto está seleccionado pero no hay unit_price, 
                # usar el precio del producto
                if instance.product and not instance.unit_price:
                    instance.unit_price = instance.product.price
                
                # Calcular el precio total
                instance.total_price = instance.quantity * instance.unit_price
                instance.save()
        
        for deleted_object in formset.deleted_objects:
            deleted_object.delete()
        
        formset.save_m2m()
        
        # Recalcular totales del pedido
        if form.instance:
            form.instance.recalculate_totals()
