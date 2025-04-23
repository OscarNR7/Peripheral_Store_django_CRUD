from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth import get_user_model
from cloudinary.models import CloudinaryField

# Create your models here.
class Product (models.Model):
    STATUS_CHOICE = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('out_of_stock','Out of Stock'),
    )
    name = models.CharField(max_length=200, verbose_name='Name')
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(verbose_name='Description')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Price')
    category = models.ForeignKey('categories.Category', on_delete=models.CASCADE,related_name='products',
                                 verbose_name='Category')
    stock = models.PositiveIntegerField(default=0, verbose_name='Stock')
    sku = models.CharField(max_length=100, unique=True, verbose_name='SKU')
    brand = models.CharField(max_length=100, blank=True, null=True, verbose_name='Brand')
    featured = models.BooleanField(default=False, verbose_name='Featured')
    status = models.CharField(max_length=20,choices=STATUS_CHOICE, default='active', verbose_name='Status')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        app_label = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='images', verbose_name='Product')
    image = CloudinaryField('image', folder='products')
    alt_text = models.CharField(max_length=200, blank=True, null=True, verbose_name='Alt Text')
    is_main = models.BooleanField(default=False, verbose_name='Is Main Image')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
    def __str__(self):
        return f"{self.product.name} - {self.image.url}"
    
class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='specifications', verbose_name='Product')
    name = models.CharField(max_length=200, verbose_name='Name')
    value = models.CharField(max_length=200, verbose_name='Value')

    class Meta:
        verbose_name = 'Product Specification'
        verbose_name_plural = 'Product Specifications'
        unique_together = ('product', 'name')
    def __str__(self):
        return f"{self.product.name} - {self.name}:  {self.value}"