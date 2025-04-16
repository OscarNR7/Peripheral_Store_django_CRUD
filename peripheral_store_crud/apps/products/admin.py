from django.contrib import admin
from .models import Product, ProductImage, ProductSpecification

# Register your models here.
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'status', 'created_at')
    list_filter = ('category', 'status', 'featured')
    search_fields = ('name', 'sku')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductSpecificationInline]