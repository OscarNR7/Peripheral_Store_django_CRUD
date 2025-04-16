from django.contrib import admin
from .models import Category, CategoryAttribute

# Register your models here.
class CategoryAttributeInline(admin.TabularInline):
    model = CategoryAttribute
    extra = 1
    fields = ('name','description','is_required','is_filterable')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active','featured','order', 'created_at')
    list_filter = ('parent', 'is_active')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'featured','order')
    inlines = [CategoryAttributeInline]
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None,{
            'fields': ('name', 'slug', 'parent', 'description')
        }),
        ('Visualization options',{
            'fields': ('is_active', 'featured', 'order', 'image')
        }),
        ('System data',{
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    #metodo para mostrar el nombre con sangriia para la jerarquia
    def indented_name (self, obj):
        level = 0
        parent = obj.parent
        while parent:
            level += 1
            parent = parent.parent

        indent = '_ ' * level
        return f"{indent}{obj.name}"
    indented_name.short_description = 'Name'

    #metodo para mostrar la cantidad de productos en la categoria
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Product Count'

@admin.register(CategoryAttribute)
class CategoryAttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_required', 'is_filterable')
    list_filter = ('category', 'is_required', 'is_filterable')
    search_fields = ('name','description','category__name')