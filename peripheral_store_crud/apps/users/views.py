from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib import messages
from .models import User, Profile, Address
from .forms import CustomUserCreationForm, CustomUserLoginForm, CustomUserChangeForm, ProfileForm, AddressForm

# Create your views here.
class UserLoginView(LoginView):
    """Vista para el login de usuarios"""
    template_name = 'login.html'
    authentication_form = CustomUserLoginForm

    def get_success_url(self):
        """Determina la URL de redireccion despues del login"""
        try:
            if self.request.user.is_staff:
                return reverse_lazy('public_products:catalog_list')
            return reverse_lazy('public_products:catalog_list')
        except Exception as e:
            print(f"Error en get_success_url: {str(e)}")
            return reverse_lazy('public_products:catalog_list')
    
class CustomLogoutView(LogoutView):
    """Vista para el logout de usuarios"""
    next_page = reverse_lazy('public_products:catalog_list')
    
class UserCreateView(CreateView):
    """Registro de usuarios"""
    model = User
    form_class = CustomUserCreationForm
    template_name = 'register.html'
    
    def form_valid(self, form):
        """Procesa el formulario válido y autentica al usuario"""
        try:
            print("Form is valid. Attempting to save...")
            print("Form data:", form.cleaned_data)
            
            # Guardar el usuario de forma explícita
            user = form.save(commit=False)
            print(f"User created (not saved yet): {user.email}")
            
            # Guardar el usuario en la base de datos
            user.save()
            print(f"User saved with ID: {user.id}")
            
            # Configurar la contraseña (si es necesario)
            raw_password = form.cleaned_data.get('password1')
            if raw_password:
                print("Setting password...")
                user.set_password(raw_password)
                user.save(update_fields=['password'])
            
            # Almacenar el objeto creado
            self.object = user
            
            # Mensaje de éxito
            messages.success(self.request, f'Usuario {self.object.email} registrado correctamente')
            
            # Iniciar sesión
            login(self.request, self.object)
            print(f"User logged in: {self.request.user.is_authenticated}")
            
            # Redireccionar
            return HttpResponseRedirect(self.get_success_url())
        except Exception as e:
            print(f"Error in form_valid: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            messages.error(self.request, f"Error al registrar usuario: {str(e)}")
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Maneja formularios inválidos"""
        print("Form is invalid!")
        print("Form errors:", form.errors)
        return super().form_invalid(form)
    
    def get_success_url(self):
        """URL después de registro exitoso"""
        return reverse_lazy('public_products:catalog_list')
    
class UserProfileView(DetailView):
    """Vista del perfil del usuario"""
    model = User
    template_name = 'profile.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        """Agrega datos del perfil y direcciones al contexto"""
        try:
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
        except Exception as e:
            print(f"Error en get_context_data: {str(e)}")
            return super().get_context_data(**kwargs)

class UserUpdateView(View):
    """Vista para actualizar datos de usuario"""
    template_name = 'profile_update.html'
    
    def get(self, request, pk):
        """Muestra formulario de actualizacion de perfil"""
        try:
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
        except Exception as e:
            messages.error(request, f"Error al cargar perfil: {str(e)}")
            return redirect('public_products:catalog_list')
            
    def post(self, request, pk):
        """Procesa formulario de actualizacion de perfil"""
        try:
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
                user_form.save()
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
        except Exception as e:
            messages.error(request, f"Error al actualizar perfil: {str(e)}")
            return redirect('users:profile_detail', pk=pk)
    
class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Vista de la lista de usuarios"""
    model = User
    template_name = 'user_list.html'
    context_object_name = 'users'
    paginate_by = 10

    def test_func(self):
        """Verifica si el usuario es staff"""
        return self.request.user.is_staff
        
    def handle_no_permission(self):
        """Redirige a usuarios sin permisos"""
        return redirect('public_products:catalog_list')

    def get_queryset(self):
        """Filtra la lista de usuarios segun parametros"""
        try:
            queryset = super().get_queryset()

            # Filtro por nombre
            query = self.request.GET.get('q')
            if query:
                queryset = queryset.filter(first_name__icontains=query)
                
            # Filtro por estado
            status = self.request.GET.get('status')
            if status == 'active':
                queryset = queryset.filter(is_active=True)
            elif status == 'inactive':
                queryset = queryset.filter(is_active=False)
            
            # Filtro por rol
            role = self.request.GET.get('role')
            if role == 'staff':
                queryset = queryset.filter(is_staff=True)
            elif role == 'customer':
                queryset = queryset.filter(is_staff=False)
                
            return queryset
        except Exception as e:
            print(f"Error en get_queryset: {str(e)}")
            return User.objects.none()

    def get_context_data(self, **kwargs):
        """Agrega parametros de busqueda al contexto"""
        try:
            context = super().get_context_data(**kwargs)
            context['query'] = self.request.GET.get('q', '')
            return context
        except Exception as e:
            print(f"Error en get_context_data: {str(e)}")
            return super().get_context_data(**kwargs)

    def dispatch(self, request, *args, **kwargs):
        """Verifica autenticacion y permisos antes de procesar"""
        try:
            if not request.user.is_authenticated:
                return redirect('users:login')
            if not request.user.is_staff:
                messages.error(request, "You don't have permission to access this page")
                return redirect('public_products:catalog_list')
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('public_products:catalog_list')
    
class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Vista para eliminar un usuario"""
    model = User
    template_name = 'user_delete.html'
    success_url = reverse_lazy('users:user_list')

    def test_func(self):
        """Verifica si el usuario es staff"""
        return self.request.user.is_staff
        
    def handle_no_permission(self):
        """Redirige a usuarios sin permisos"""
        return redirect('public_products:catalog_list')

    def delete(self, request, *args, **kwargs):
        """Elimina el usuario y muestra mensaje"""
        try:
            user_obj = self.get_object()
            messages.success(request, f'Usuario {user_obj.email} eliminado correctamente.')
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f"Error al eliminar usuario: {str(e)}")
            return redirect('users:user_list')

# Address management
class SetDefaultAddressView(LoginRequiredMixin, View):
    """Vista para establecer una direccion como predeterminada"""
    def post(self, request, pk):
        """Marca una direccion como predeterminada"""
        try:
            address = get_object_or_404(Address, pk=pk, user=request.user)
            
            # Establecer esta direccion como predeterminada para su tipo
            Address.objects.filter(
                user=request.user,
                address_type=address.address_type
            ).update(is_default=False)
            
            address.is_default = True
            address.save()
            
            messages.success(request, f"{address.get_address_type_display()} address set as default")
            return redirect('users:address_list')
        except Address.DoesNotExist:
            messages.error(request, "Address not found")
            return redirect('users:address_list')
        except Exception as e:
            messages.error(request, f"Error setting default address: {str(e)}")
            return redirect('users:address_list')
            
class AddressListView(LoginRequiredMixin, ListView):
    """Vista para listar las direcciones de un usuario"""
    model = Address
    template_name = 'address_list.html'
    context_object_name = 'addresses'
    
    def get_queryset(self):
        """Filtra las direcciones del usuario actual"""
        try:
            return Address.objects.filter(user=self.request.user)
        except Exception as e:
            print(f"Error en get_queryset: {str(e)}")
            return Address.objects.none()

class AddressCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear una nueva direccion"""
    model = Address
    form_class = AddressForm
    template_name = 'address_form.html'
    
    def get_form_kwargs(self):
        """Agrega el usuario al formulario"""
        try:
            kwargs = super().get_form_kwargs()
            kwargs['user'] = self.request.user
            return kwargs
        except Exception as e:
            print(f"Error en get_form_kwargs: {str(e)}")
            return super().get_form_kwargs()
    
    def form_valid(self, form):
        """Procesa el formulario valido"""
        try:
            form.instance.user = self.request.user
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"Error creating address: {str(e)}")
            return super().form_invalid(form)
    
    def get_success_url(self):
        """URL de redireccion tras crear direccion"""
        try:
            messages.success(self.request, 'Address added successfully')
            return reverse('users:address_list')
        except Exception as e:
            print(f"Error en get_success_url: {str(e)}")
            return reverse('users:address_list')

class AddressUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para actualizar una direccion existente"""
    model = Address
    form_class = AddressForm
    template_name = 'address_form.html'
    
    def get_queryset(self):
        """Filtra direcciones del usuario actual"""
        try:
            return Address.objects.filter(user=self.request.user)
        except Exception as e:
            print(f"Error en get_queryset: {str(e)}")
            return Address.objects.none()
    
    def get_form_kwargs(self):
        """Agrega el usuario al formulario"""
        try:
            kwargs = super().get_form_kwargs()
            kwargs['user'] = self.request.user
            return kwargs
        except Exception as e:
            print(f"Error en get_form_kwargs: {str(e)}")
            return super().get_form_kwargs()
    
    def get_success_url(self):
        """URL de redireccion tras actualizar direccion"""
        try:
            messages.success(self.request, 'Address updated successfully')
            return reverse('users:address_list')
        except Exception as e:
            print(f"Error en get_success_url: {str(e)}")
            return reverse('users:address_list')

class AddressDeleteView(LoginRequiredMixin, DeleteView):
    """Vista para eliminar una direccion"""
    model = Address
    template_name = 'address_confirm_delete.html'
    
    def get_queryset(self):
        """Filtra direcciones del usuario actual"""
        try:
            return Address.objects.filter(user=self.request.user)
        except Exception as e:
            print(f"Error en get_queryset: {str(e)}")
            return Address.objects.none()
    
    def delete(self, request, *args, **kwargs):
        """Elimina la direccion y muestra mensaje"""
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f"Error deleting address: {str(e)}")
            return redirect('users:address_list')
    
    def get_success_url(self):
        """URL de redireccion tras eliminar direccion"""
        try:
            messages.success(self.request, 'Address deleted successfully')
            return reverse('users:address_list')
        except Exception as e:
            print(f"Error en get_success_url: {str(e)}")
            return reverse('users:address_list')