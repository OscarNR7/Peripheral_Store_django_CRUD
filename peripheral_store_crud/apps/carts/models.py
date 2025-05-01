from django.db import models
from django.db.models import Sum, F
from django.contrib.auth import get_user_model
from apps.products.models import Product
from django.utils import timezone

User = get_user_model()

# Create your models here.
class Cart(models.Model):
    """Modelo del carrito"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', verbose_name='User')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Cart of {self.user.get_full_name()}"
    
    @property
    def subtotal(self):
        """calcula el sbtotal del carrito depediendo de los productos"""
        agg = self.items.aggregate(sum=Sum(F('quantity') * F('product__price')))
        return agg.get('sum') or 0
    @property
    def total_items(self):
        """Retorna el número total de items en el carrito"""
        agg = self.items.aggregate(sum=Sum('quantity'))
        return agg.get('sum') or 0
    
    def clear(self):
        """Elimina todos los items del carrito"""
        self.items.all().delete()
        self.save()

    def add_product(self, product_id, quantity=1):
        """Añade un producto al carrito o incrementa su cantidad si ya existe"""
        try:
            product = Product.objects.get(id=product_id)
            
            # Verificar si hay suficiente stock
            if product.stock < quantity:
                return False, f"Not enough stock. Only {product.stock} available."
            
            # Buscar si el producto ya está en el carrito
            cart_item, created = CartItem.objects.get_or_create(
                cart=self,
                product=product,
                defaults={'quantity': quantity}
            )
            
            # Si el producto ya estaba en el carrito, incrementar la cantidad
            if not created:
                if cart_item.quantity + quantity > product.stock:
                    return False, f"Not enough stock. Only {product.stock} available."
                cart_item.quantity += quantity
                cart_item.save()
            
            self.updated_at = timezone.now()
            self.save()
            
            return True, f"{product.name} added to cart."
        except Product.DoesNotExist:
            return False, "Product does not exist."
        except Exception as e:
            return False, str(e)
    
    def update_item_quantity(self, item_id, quantity):
        """Actualiza la cantidad de un item específico en el carrit"""
        try:
            item = self.items.get(id=item_id)
            # Verificar si hay suficiente stock
            if quantity > item.product.stock:
                return False, f"Not enough stock. Only {item.product.stock} available."
            
            if quantity <= 0:
                item.delete()
                return True, "Item removed from cart."
            
            item.quantity = quantity
            item.save()
            
            self.updated_at = timezone.now()
            self.save()
            
            return True, "Cart updated successfully."
        except CartItem.DoesNotExist:
            return False, "Item not found in cart."
        except Exception as e:
            return False, str(e)
    
    def remove_item(self, item_id):
        """Elimina un item del carrito"""
        try:
            item = self.items.get(id=item_id)
            item.delete()
            
            self.updated_at = timezone.now()
            self.save()
            
            return True, "Item removed from cart."
        except CartItem.DoesNotExist:
            return False, "Item not found in cart."
        except Exception as e:
            return False, str(e)

class CartItem(models.Model):
    """
    Modelo para los items del carrito
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name='Cart')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items', verbose_name='Product')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Quantity')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ('cart', 'product')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def total_price(self):
        """Calcula el precio total del item basado en la cantidad y el precio unitario"""
        return self.quantity * self.product.price