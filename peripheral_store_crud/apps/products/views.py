from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Avg
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.views import View
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .models import Product
from .forms import ProductForm, ProductImageFormSet, ProductSpecificationFormSet
from apps.users.models import User
from apps.categories.models import Category

# Create your views here.
#catalogo de los productos
class CatalogView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'product_catalog.html'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(status='active')
        q = self.request.GET.get('q')
        category_id = self.request.GET.get('category')
        if q:
            queryset = queryset.filter(name__icontains=q)
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["query"] = self.request.GET.get("q", "")
        context["selected_category"] = self.request.GET.get("category", "")
        return context

#vista publica de los productos individuales
class PublicProductDetailView(DetailView):
    model = Product
    template_name = 'public_product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return super().get_queryset().filter(status='active')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_products'] = Product.objects.filter(
            category=self.object.category
        ).exclude(id=self.object.id)[:5]
        return context

#clase que muestra los productos ingresados
class ProductListView(ListView):
    model = Product
    context_object_name = "products"
    paginate_by = 5
    template_name = "product_list.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        #busqueda por nombre si hay 'q'
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q','')
        return context

class ProductDetailView(DetailView):
    model = Product
    context_object_name = "product"
    template_name = "product_detail.html"
    success_url = reverse_lazy('products:product_list')

#CRUD
class ProductCreateView(View):
    template_name = "product_form.html"

    def get(self, request):
        form = ProductForm()
        image_formset = ProductImageFormSet(prefix='images')
        spec_formset = ProductSpecificationFormSet(prefix='specs')
        return render(request, self.template_name, {
            'form': form,
            'image_formset': image_formset,
            'spec_formset': spec_formset
        })
    def post(self, request):
        form = ProductForm(request.POST)
        image_formset = ProductImageFormSet(request.POST, request.FILES, prefix='images')
        spec_formset = ProductSpecificationFormSet(request.POST, prefix='specs')

        if form.is_valid() and image_formset.is_valid() and spec_formset.is_valid():
            product = form.save()

            image_formset.instance = product
            for instance in image_formset.save(commit=False):
                instance.product = product
                instance.save()
            
            spec_formset.instance = product
            for instance in spec_formset.save(commit=False):
                instance.product = product
                instance.save()

            messages.success(request, f'Product {product.name} created successfully')
            return redirect('products:product_list')
    
        return render(request, self.template_name, {
            'form': form,
            'image_formset': image_formset,
            'spec_formset': spec_formset
        })

class ProductUpdateView(View):
    template_name = "product_form.html"

    def get(self,request, slug):
        product = get_object_or_404(Product, slug=slug)
        form = ProductForm(instance=product)
        image_formset = ProductImageFormSet(instance=product, prefix='images')
        spec_formset = ProductSpecificationFormSet(instance=product, prefix='specs')

        return render(request, self.template_name, {
            'form': form,
            'image_formset': image_formset,
            'spec_formset': spec_formset,
            'product': product
        })
    
    def post(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        form = ProductForm(request.POST, instance=product)
        image_formset = ProductImageFormSet(request.POST, request.FILES, instance=product, prefix='images')
        spec_formtset = ProductSpecificationFormSet(request.POST, instance=product, prefix='specs')

        if form.is_valid() and image_formset.is_valid() and spec_formtset.is_valid():
            product = form.save()

            image_formset.save()
            spec_formtset.save()

            messages.success(request, f'Product {product.name} updated successfully')
            return redirect('products:product_list')
        
        return render(request, self.template_name, {
            'form': form,
            'image_formset': image_formset,
            'spec_formset': spec_formtset,
            'product': product
        })

class ProductDeleteView(DeleteView):
    model = Product
    template_name = "product_delete.html"
    success_url = reverse_lazy('products:product_list')

    def delete (self, request, *args, **kwargs):
        product = self.get_object()
        messages.success(self.request,  f'Product {product.name} deleted successfully')
        return super().delete(request, *args, **kwargs)

@api_view(['GET'])
def get_product_details(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        return JsonResponse({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'stock': product.stock
        })
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)