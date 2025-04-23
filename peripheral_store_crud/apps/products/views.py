from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView,DeleteView, DetailView
from django.views import View
from rest_framework.decorators import api_view
from django.http import JsonResponse
from .models import Product
from .forms import ProductForm, ProductImageFormSet, ProductSpecificationFormSet
from apps.categories.models import Category

# Create your views here.
class CatalogView(ListView):
    """Vista para mostrar el catalogo de productos"""
    model = Product
    context_object_name = 'products'
    template_name = 'product_catalog.html'
    paginate_by = 12

    def get_queryset(self):
        """Obtiene productos filtrados por busqueda y categoria"""
        try:
            queryset = Product.objects.filter(status='active')
            q = self.request.GET.get('q')
            category_id = self.request.GET.get('category')
            if q:
                queryset = queryset.filter(name__icontains=q)
            
            if category_id:
                queryset = queryset.filter(category_id=category_id)
            return queryset
        except Exception as e:
            # Registrar el error y devolver queryset vacio
            print(f"Error en get_queryset: {str(e)}")
            return Product.objects.none()
    
    def get_context_data(self, **kwargs):
        """Agrega datos adicionales al contexto"""
        try:
            context = super().get_context_data(**kwargs)
            context["categories"] = Category.objects.all()
            context["query"] = self.request.GET.get("q", "")
            context["selected_category"] = self.request.GET.get("category", "")
            return context
        except Exception as e:
            print(f"Error en get_context_data: {str(e)}")
            return super().get_context_data(**kwargs)

class PublicProductDetailView(DetailView):
    """Vista publica de los productos individuales"""
    model = Product
    template_name = 'public_product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        """Filtra solo productos activos"""
        try:
            return super().get_queryset().filter(status='active')
        except Exception as e:
            print(f"Error en get_queryset: {str(e)}")
            return Product.objects.none()
            
    def get_context_data(self, **kwargs):
        """Agrega productos relacionados al contexto"""
        try:
            context = super().get_context_data(**kwargs)
            context['related_products'] = Product.objects.filter(
                category=self.object.category
            ).exclude(id=self.object.id)[:5]
            return context
        except Exception as e:
            print(f"Error en get_context_data: {str(e)}")
            return super().get_context_data(**kwargs)

class ProductListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Vista admin para listar todos los productos"""
    model = Product
    context_object_name = "products"
    paginate_by = 5
    template_name = "product_list.html"

    def test_func(self):
        """Verifica si el usuario es staff"""
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        """Redirige a usuarios sin permisos"""
        return redirect('public_products:catalog_list')

    def get_queryset(self):
        """Filtra productos por termino de busqueda"""
        try:
            queryset = super().get_queryset()
            query = self.request.GET.get('q')
            if query:
                queryset = queryset.filter(name__icontains=query)
            return queryset
        except Exception as e:
            print(f"Error en get_queryset: {str(e)}")
            return Product.objects.none()
        
    def get_context_data(self, **kwargs):
        """Agrega el termino de busqueda al contexto"""
        try:
            context = super().get_context_data(**kwargs)
            context['query'] = self.request.GET.get('q','')
            return context
        except Exception as e:
            print(f"Error en get_context_data: {str(e)}")
            return super().get_context_data(**kwargs)

class ProductDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Vista para ver detalles de un producto (admin)"""
    model = Product
    context_object_name = "product"
    template_name = "product_detail.html"
    success_url = reverse_lazy('products:product_list')

    def test_func(self):
        """Verifica si el usuario es staff"""
        return self.request.user.is_staff
        
    def handle_no_permission(self):
        """Redirige a usuarios sin permisos"""
        return redirect('public_products:catalog_list')

class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Vista para crear nuevos productos"""
    template_name = "product_form.html"

    def test_func(self):
        """Verifica si el usuario es staff"""
        return self.request.user.is_staff
        
    def handle_no_permission(self):
        """Redirige a usuarios sin permisos"""
        return redirect('public_products:catalog_list')

    def get(self, request):
        """Muestra formulario para crear producto"""
        try:
            form = ProductForm()
            image_formset = ProductImageFormSet(prefix='images')
            spec_formset = ProductSpecificationFormSet(prefix='specs')
            return render(request, self.template_name, {
                'form': form,
                'image_formset': image_formset,
                'spec_formset': spec_formset
            })
        except Exception as e:
            messages.error(request, f"Error preparing form: {str(e)}")
            return redirect('products:product_list')
            
    def post(self, request):
        """Procesa formulario para crear producto"""
        try:
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
        except Exception as e:
            messages.error(request, f"Error creating product: {str(e)}")
            return redirect('products:product_list')

class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Vista para actualizar productos existentes"""
    template_name = "product_form.html"

    def test_func(self):
        """Verifica si el usuario es staff"""
        return self.request.user.is_staff
        
    def handle_no_permission(self):
        """Redirige a usuarios sin permisos"""
        return redirect('public_products:catalog_list')

    def get(self, request, slug):
        """Muestra formulario para editar producto"""
        try:
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
        except Exception as e:
            messages.error(request, f"Error loading product: {str(e)}")
            return redirect('products:product_list')
    
    def post(self, request, slug):
        """Procesa formulario para actualizar producto"""
        try:
            product = get_object_or_404(Product, slug=slug)
            form = ProductForm(request.POST, instance=product)
            image_formset = ProductImageFormSet(request.POST, request.FILES, instance=product, prefix='images')
            spec_formset = ProductSpecificationFormSet(request.POST, instance=product, prefix='specs')

            if form.is_valid() and image_formset.is_valid() and spec_formset.is_valid():
                product = form.save()

                image_formset.save()
                spec_formset.save()

                messages.success(request, f'Product {product.name} updated successfully')
                return redirect('products:product_list')
            
            return render(request, self.template_name, {
                'form': form,
                'image_formset': image_formset,
                'spec_formset': spec_formset,
                'product': product
            })
        except Exception as e:
            messages.error(request, f"Error updating product: {str(e)}")
            return redirect('products:product_list')

class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Vista para eliminar productos"""
    model = Product
    template_name = "product_delete.html"
    success_url = reverse_lazy('products:product_list')

    def test_func(self):
        """Verifica si el usuario es staff"""
        return self.request.user.is_staff
        
    def handle_no_permission(self):
        """Redirige a usuarios sin permisos"""
        return redirect('public_products:catalog_list')

    def delete(self, request, *args, **kwargs):
        """Elimina el producto y muestra mensaje"""
        try:
            product = self.get_object()
            messages.success(self.request, f'Product {product.name} deleted successfully')
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f"Error deleting product: {str(e)}")
            return redirect('products:product_list')

@api_view(['GET'])
def get_product_details(request, product_id):
    """API endpoint para obtener detalles de producto"""
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
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)