from django import forms
from django.forms import inlineformset_factory
from .models import Category, CategoryAttribute

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'parent', 'image', 'is_active', 'featured']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['parent'].queryset = Category.objects.exclude(pk=self.instance.pk).exclude(
                parent=self.instance
            )
class CategoryAttributeForm(forms.ModelForm):
    class Meta:
        model = CategoryAttribute
        fields = ['name', 'description', 'is_required', 'is_filterable']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_filterable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

CategoryAttributeFormSet = inlineformset_factory(
    Category,
    CategoryAttribute,
    form=CategoryAttributeForm,
    extra=1,
    can_delete=True
)