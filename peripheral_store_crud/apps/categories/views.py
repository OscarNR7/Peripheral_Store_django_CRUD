from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, DeleteView
from django.views import View
from .models import Category
from .forms import CategoryForm, CategoryAttributeFormSet

# Create your views here.
class CategoryListView(LoginRequiredMixin,UserPassesTestMixin,ListView):
    model =Category
    template_name = 'category_list.html'
    context_object_name = 'categories'
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_staff
    def handle_no_permission(self):
        return redirect('public_products:catalog_list')

    def get_queryset(self):
        return Category.objects.filter(parent=None)
    
class CategoryDetailView(LoginRequiredMixin,UserPassesTestMixin,DetailView):
    model = Category
    form_class = CategoryForm
    template_name = 'category_detail.html'
    context_object_name = 'category'
    
    def test_func(self):
        return self.request.user.is_staff
    def handle_no_permission(self):
        return redirect('public_products:catalog_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attributes'] = self.object.attributes.all()
        return context

class CategoryCreateView(LoginRequiredMixin,UserPassesTestMixin,View):
    template_name = 'category_form.html'

    def test_func(self):
        return self.request.user.is_staff
    def handle_no_permission(self):
        return redirect('public_products:catalog_list')

    def get(self, request):
        form = CategoryForm()
        attribute_formset = CategoryAttributeFormSet(prefix='attributes')
        return render(request, self.template_name,{
            'form': form,
            'attribute_formset' : attribute_formset
        })
    
    def post(self, request):
        form = CategoryForm(request.POST, request.FILES)
        attribute_formset = CategoryAttributeFormSet(request.POST, prefix='attributes')

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
        
        return render(request, self.template_name, {
            'form': form,
            'attribute_formset' : attribute_formset
        })
    
class CategoryUpdateView(LoginRequiredMixin,UserPassesTestMixin,View):
    template_name = 'category_form.html'

    def test_func(self):
        return self.request.user.is_staff
    def handle_no_permission(self):
        return redirect('public_products:catalog_list')


    def get(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        form = CategoryForm(instance=category)
        attribute_formset = CategoryAttributeFormSet(instance=category, prefix='attributes')

        return render(request, self.template_name,{
            'form': form,
            'attribute_formset' : attribute_formset,
            'category': category
        })

    def post(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        form = CategoryForm(request.POST, request.FILES, instance=category)
        attribute_formset = CategoryAttributeFormSet(request.POST, instance=category, prefix='attributes')

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

        return render(request, self.template_name,{
            'form': form,
            'attribute_formset' : attribute_formset,
            'category': category
        })


class CategoryDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Category
    template_name = 'category_delete.html'
    success_url = reverse_lazy('categories:category_list')
    context_object_name = 'category'

    def test_func(self):
        return self.request.user.is_staff
    def handle_no_permission(self):
        return redirect('public_products:catalog_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Category deleted successfully')
        return super().delete(request, *args, **kwargs)
