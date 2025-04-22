from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib import messages
from .models import User, Profile, Address
from .forms import CustomUserCreationForm, CustomUserLoginForm, CustomUserChangeForm, ProfileForm, AddressForm


# Create your views here.
class UserLoginView(LoginView):
    '''
    Vista para el login de usuarios
    '''
    template_name = 'login.html'
    authentication_form = CustomUserLoginForm

    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse_lazy('public_products:catalog_list')
        return reverse_lazy('public_products:catalog_list')
    
class CustomLogoutView(LogoutView):
    '''
    Vista para el logout de usuarios
    '''
    next_page = reverse_lazy('public_products:catalog_list')
    
class UserCreateView(CreateView):
    '''
    Resgitro de usarios
    '''
    model = User
    form_class = CustomUserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Usuario {self.object.email} registrado correctamente')
        login(self.request, self.object)
        return response
    
    def get_success_url(self):
        return reverse('public_products:catalog_list')
    
#Gestion de usuarios: Perfil, actulizaciones y listado de usuarios

class UserProfileView(DetailView):
    '''
    Vista del perfil del usuario
    '''
    model = User
    template_name = 'profile.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        
        addresses = user.addresses.all()
        
        context.update({
            'profile': user.profile if hasattr(user, 'profile') else None,
            'default_billing': addresses.filter(
                address_type='billing', 
                is_default=True
            ).first(),
            'default_shipping': addresses.filter(
                address_type='shipping', 
                is_default=True
            ).first(),
            'has_addresses': addresses.exists()
        })
        
        return context

class UserUpdateView(View):
    template_name= 'profile_update.html'
    
    def get(self,request, pk):
        user_obj = get_object_or_404(User, pk=pk)
        if request.user != user_obj and not request.user.is_staff:
            messages.error(request, "Don't have permission to edit this user")
            return redirect('users:profile_detail', pk=pk)
        
        user_form = CustomUserChangeForm(instance=user_obj)
        try:
            profile_instance = user_obj.profile
        except Profile.DoesNotExist:
            profile_instance = None
        profile_form = ProfileForm(instance=profile_instance)
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
            'user_obj': user_obj
        })
    def post(self, request, pk):
        user_obj = get_object_or_404(User, pk=pk)
        if request.user != user_obj and not request.user.is_staff:
            messages.error(request, "Don't have permission to edit this user")
            return redirect('users:profile_detail', pk=pk)
        user_form = CustomUserChangeForm(request.POST, instance=user_obj)
        try:
            profile_instance = user_obj.profile
        except Profile.DoesNotExist:
            profile_instance = None
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile_instance)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()# Guarda o crea el perfil
            profile = profile_form.save(commit=False)
            profile.user = user_obj
            profile.save()
            messages.success(request, "Profile updated successfully")
            return redirect('users:profile_detail', pk=pk)
        else:
            messages.error(request, "Error updating profile")
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
            'user_obj': user_obj
        })
    
class UserListView(ListView):
    '''
    Vista de la list de usurios
    '''
    model =User
    template_name = 'user_list.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        #filtro por nombre
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(first_name__icontains=query)
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        # Filtro por role
        role = self.request.GET.get('role')
        if role == 'staff':
            queryset = queryset.filter(is_staff=True)
        elif role == 'customer':
            queryset = queryset.filter(is_staff=False)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

        
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')
        if not request.user.is_staff:
            messages.error(request, "You don't have permission to access this page")
            return redirect('users:profile_detail', pk=request.user.pk)
        return super().dispatch(request, *args, **kwargs)
    
class UserDeleteView(DeleteView):
    '''
    Vista para eliminar un usuario- Solo administradores o el propio usuario pueden hacerlo
    '''
    model = User
    template_name = 'user_delete.html'
    success_url = reverse_lazy('users:user_list')

    def delete(self, request, *args, **kwargs):
        user_obj = self.get_object()
        messages.success(request, f'Usuario {user_obj.email} eliminado correctamente.')
        return super().delete(request, *args, **kwargs)

#Address management
class SetDefaultAddressView(View):
    """
    Vista para establecer una dirección como predeterminada
    """
    def post(self, request, pk):
        address = get_object_or_404(Address, pk=pk, user=request.user)
        
        # Establecer esta dirección como predeterminada para su tipo
        Address.objects.filter(
            user=request.user,
            address_type=address.address_type
        ).update(is_default=False)
        
        address.is_default = True
        address.save()
        
        messages.success(request, f"{address.get_address_type_display()} address set as default")
        return redirect('users:address_list')
class AddressListView(LoginRequiredMixin, ListView):
    '''
    Vista para listar las direcciones de un usuario
    '''
    model = Address
    template_name = 'address_list.html'
    context_object_name = 'addresses'
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

class AddressCreateView(LoginRequiredMixin, CreateView):
    '''
    Vista para crear una nueva dirección
    '''
    model = Address
    form_class = AddressForm
    template_name = 'address_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        messages.success(self.request, 'Address added successfully')
        return reverse('users:address_list')

class AddressUpdateView(LoginRequiredMixin, UpdateView):
    '''
    Vista para actualizar una dirección existente
    '''
    model = Address
    form_class = AddressForm
    template_name = 'address_form.html'
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        messages.success(self.request, 'Address updated successfully')
        return reverse('users:address_list')

class AddressDeleteView(LoginRequiredMixin, DeleteView):
    '''
    Vista para eliminar una dirección
    '''
    model = Address
    template_name = 'address_confirm_delete.html'
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        messages.success(self.request, 'Address deleted successfully')
        return reverse('users:address_list')