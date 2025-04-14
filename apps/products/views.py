from django.shortcuts import render
from .models import Product, ProductImage, ProductSpecification
from django.views.generic import ListView

# Create your views here.

#clase que muestra los productos ingresados
class ProductListView(ListView):
    model = Product
    context_object_name = "products"
    paginate_by = 5
    template_name = "product_list.html"

    def get_queryset(self):
        return super().get_queryset()
    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)
    