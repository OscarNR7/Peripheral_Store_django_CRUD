from django.db import models
from django.utils.text import slugify
from django.urls import reverse


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=200,verbose_name='Name')
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(verbose_name='Description')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True,
                                 related_name='subcategories', verbose_name='Parent Category')
    image = models.ImageField(upload_to='categories/images/', blank=True, null=True, verbose_name='Image')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    featured = models.BooleanField(default=False, verbose_name='Featured')
    order = models.PositiveIntegerField(default=0, verbose_name='Order')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('categories:category_detail', kwargs={'slug': self.slug})
    
    #metodo para retornar todos los productos de una categoria y sus categporias
    def get_all_products(self):
        products = self.products.all()
        for child in self.subcategories.all():
            products = products | child.get_all_products()
        return products
    
    #metodo para retornar todas las subcategorias de una categoria directas
    @property
    def get_subcategories(self):
        return self.subcategories.filter(is_active=True)
    
    #identificacion de categorias sin padre
    @property
    def is_root(self):
        return self.parent is None
    
    #Idica si tiene categorias
    @property
    def has_subcategories(self):
        return self.subcategories.exists()

class CategoryAttribute(models.Model):
    '''Define los atributos de las categorias'''
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='attributes', verbose_name='Category')
    name = models.CharField(max_length=200, verbose_name='Name')
    description = models.TextField(blank=True,null=True,verbose_name='Description')
    is_required = models.BooleanField(default=False, verbose_name='Is Required')
    is_filterable = models.BooleanField(default=False, verbose_name='Is Filterable')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        verbose_name = 'Category Attribute'
        verbose_name_plural = 'Category Attributes'
        unique_together = ('category', 'name')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"
    