from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Cart, CartItem

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    """Crea un carrito para un usuario cuando se registra"""
    if created:
        Cart.objects.create(user=instance)

@receiver(post_save, sender=CartItem)
def update_cart_on_item_update(sender, instance, **kwargs):
    """Actualiza la fecha de actualizacion del carrito cuando un item es actualizado"""
    #usado para activar la actualizacion del carrito
    instance.cart.save(update_fields=['updated_at'])

@receiver(post_delete, sender=CartItem)
def update_cart_on_item_delete(sender, instance, **kwargs):
    """Actualiza la fecha de actualizacion del carrito cuando un item es eliminado"""
    try:
        #verificar que el carrito aun existe antes de actualizarlo
        if instance.cart:
            instance.cart.save(update_fields=['updated_at'])
    except Cart.DoesNotExist:
        pass