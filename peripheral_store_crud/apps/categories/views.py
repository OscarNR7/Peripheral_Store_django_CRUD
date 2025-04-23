from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, DeleteView
from django.views import View
from django.db import transaction
from .models import Category
from .forms import CategoryForm, CategoryAttributeFormSet

class CategoryListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Vista para listar categorias padre"""
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'
    paginate_by = 10

    def test_func(self):
        """Verifica si el usuario es staff"""
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        """Redirige a catalogo si no tiene permisos"""
        return redirect('public_products:catalog_list')

    def get_queryset(self):
        """Obtiene solo categorias padre"""
        try:
            return Category.objects.filter(parent=None)
        except Exception as e:
            messages.error(self.request, f"Error al cargar categorias: {str(e)}")
            return Category.objects.none()
    
class CategoryDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Vista de detalle de categoria"""
    model = Category
    form_class = CategoryForm
    template_name = 'category_detail.html'
    context_object_name = 'category'
    
    def test_func(self):
        """Verifica si el usuario es staff"""
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        """Redirige a catalogo si no tiene permisos"""
        return redirect('public_products:catalog_list')

    def get_context_data(self, **kwargs):
        """Agrega atributos al contexto"""
        try:
            context = super().get_context_data(**kwargs)
            context['attributes'] = self.object.attributes.all()
            return context
        except Exception as e:
            messages.error(self.request, f"Error al cargar datos: {str(e)}")
            context = super().get_context_data(**kwargs)
            context['attributes'] = []
            return context

class CategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Vista para crear categorias"""
    template_name = 'category_form.html'

    def test_func(self):
        """Verifica si el usuario es staff"""
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        """Redirige a catalogo si no tiene permisos"""
        return redirect('public_products:catalog_list')

    def get(self, request):
        """Muestra formulario de creacion"""
        try:
            form = CategoryForm()
            attribute_formset = CategoryAttributeFormSet(prefix='attributes')
            return render(request, self.template_name, {
                'form': form,
                'attribute_formset': attribute_formset
            })
        except Exception as e:
            messages.error(request, f"Error al cargar formulario: {str(e)}")
            return redirect('categories:category_list')
    
    def post(self, request):
        """Procesa formulario de creacion"""
        form = CategoryForm(request.POST, request.FILES)
        attribute_formset = CategoryAttributeFormSet(request.POST, prefix='attributes')

        try:
            with transaction.atomic():
                if form.is_valid() and attribute_formset.is_valid():
                    category = form.save()

                    attribute_formset.instance = category
                    attribute_instances = attribute_formset.save(commit=False)
                                
                    for instance in attribute_instances:
                        instance.category = category
                        instance.save()
                    
                    for obj in attribute_formset.deleted_objects:
                        obj.delete()
                    
                    attribute_formset.save_m2m()

                    messages.success(request, "Category created successfully")
                    return redirect('categories:category_list')
                else:
                    print("Form errors:", form.errors)
                    print("Formset errors:", attribute_formset.errors)
        except Exception as e:
            messages.error(request, f"Error creating category: {str(e)}")
            transaction.rollback()
        
        return render(request, self.template_name, {
            'form': form,
            'attribute_formset': attribute_formset
        })
    
class CategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Vista para actualizar categorias"""
    template_name = 'category_form.html'

    def test_func(self):
        """Verifica si el usuario es staff"""
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        """Redirige a catalogo si no tiene permisos"""
        return redirect('public_products:catalog_list')

    def get(self, request, pk):
        """Muestra formulario de edicion"""
        try:
            category = get_object_or_404(Category, pk=pk)
            form = CategoryForm(instance=category)
            attribute_formset = CategoryAttributeFormSet(instance=category, prefix='attributes')

            return render(request, self.template_name, {
                'form': form,
                'attribute_formset': attribute_formset,
                'category': category
            })
        except Category.DoesNotExist:
            messages.error(request, "Category not found")
            return redirect('categories:category_list')
        except Exception as e:
            messages.error(request, f"Error loading category: {str(e)}")
            return redirect('categories:category_list')

    def post(self, request, pk):
        """Procesa formulario de actualizacion"""
        try:
            category = get_object_or_404(Category, pk=pk)
            form = CategoryForm(request.POST, request.FILES, instance=category)
            attribute_formset = CategoryAttributeFormSet(request.POST, instance=category, prefix='attributes')

            with transaction.atomic():
                if form.is_valid() and attribute_formset.is_valid():
                    category = form.save()
                    
                    # Guardar formset con la categoría correcta
                    attribute_formset.instance = category
                    attribute_instances = attribute_formset.save(commit=False)
                    
                    for instance in attribute_instances:
                        instance.category = category
                        instance.save()

                    for obj in attribute_formset.deleted_objects:
                        obj.delete()
                        
                    attribute_formset.save_m2m()

                    messages.success(request, "Category updated successfully")
                    return redirect('categories:category_list')
                else:
                    print("Form errors:", form.errors)
                    print("Formset errors:", attribute_formset.errors)
        except Category.DoesNotExist:
            messages.error(request, "Category not found")
            return redirect('categories:category_list')
        except Exception as e:
            messages.error(request, f"Error updating category: {str(e)}")
            transaction.rollback()

        return render(request, self.template_name, {
            'form': form,
            'attribute_formset': attribute_formset,
            'category': category
        })


class CategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Vista para eliminar categorias"""
    model = Category
    template_name = 'category_delete.html'
    success_url = reverse_lazy('categories:category_list')
    context_object_name = 'category'

    def test_func(self):
        """Verifica si el usuario es staff"""
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        """Redirige a catalogo si no tiene permisos"""
        return redirect('public_products:catalog_list')

    def delete(self, request, *args, **kwargs):
        """Elimina categoria y muestra mensaje"""
        try:
            with transaction.atomic():
                messages.success(request, 'Category deleted successfully')
                return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f"Error deleting category: {str(e)}")
            return redirect('categories:category_list')