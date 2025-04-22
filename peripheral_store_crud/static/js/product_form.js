document.addEventListener('DOMContentLoaded', function() {
    // Inicialización de tabs de Bootstrap
    var tabElms = [].slice.call(document.querySelectorAll('[data-bs-toggle="tab"]'));
    tabElms.forEach(function(tabElm) {
        new bootstrap.Tab(tabElm);
    });

    // Funcionalidad para añadir imágenes
    const addImageBtn = document.getElementById('add-image');
    if (addImageBtn) {
        addImageBtn.addEventListener('click', function() {
            const totalForms = document.getElementById('id_images-TOTAL_FORMS');
            const formNum = parseInt(totalForms.value);
            const formContainer = document.querySelector('.image-container');
            const emptyForm = document.querySelector('.image-form').cloneNode(true);
            
            // Actualizar IDs y nombres
            emptyForm.innerHTML = emptyForm.innerHTML.replace(/images-\d+-/g, `images-${formNum}-`);
            emptyForm.innerHTML = emptyForm.innerHTML.replace(/id_images-\d+-/g, `id_images-${formNum}-`);
            
            // Limpiar valores
            emptyForm.querySelectorAll('input:not([type="hidden"]').forEach(input => {
                if (input.type !== 'checkbox') input.value = '';
                else input.checked = false;
            });
            
            // Eliminar vista previa si existe
            const preview = emptyForm.querySelector('.img-preview-container');
            if (preview) preview.remove();
            
            formContainer.appendChild(emptyForm);
            totalForms.value = formNum + 1;
        });
    }

    // Funcionalidad para añadir especificaciones
    const addSpecBtn = document.getElementById('add-spec');
    if (addSpecBtn) {
        addSpecBtn.addEventListener('click', function() {
            const totalForms = document.getElementById('id_specs-TOTAL_FORMS');
            const formNum = parseInt(totalForms.value);
            const formContainer = document.getElementById('spec-formset');
            const emptyForm = document.querySelector('.spec-form').cloneNode(true);
            
            // Actualizar IDs y nombres
            emptyForm.innerHTML = emptyForm.innerHTML.replace(/specs-\d+-/g, `specs-${formNum}-`);
            emptyForm.innerHTML = emptyForm.innerHTML.replace(/id_specs-\d+-/g, `id_specs-${formNum}-`);
            
            // Limpiar valores
            emptyForm.querySelectorAll('input:not([type="hidden"]').forEach(input => {
                if (input.type !== 'checkbox') input.value = '';
                else input.checked = false;
            });
            
            formContainer.appendChild(emptyForm);
            totalForms.value = formNum + 1;
        });
    }

    // Manejar eliminación de formularios
    document.addEventListener('change', function(e) {
        if (e.target.classList.contains('delete-checkbox')) {
            const formCard = e.target.closest('.card');
            if (e.target.checked) {
                formCard.classList.add('to-delete');
            } else {
                formCard.classList.remove('to-delete');
            }
        }
    });

    // Vista previa de imágenes
    document.addEventListener('change', function(e) {
        if (e.target.type === 'file' && e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            const reader = new FileReader();
            const formGroup = e.target.closest('.card-body');
            
            // Eliminar vista previa existente
            const existingPreview = formGroup.querySelector('.img-preview-container');
            if (existingPreview) existingPreview.remove();
            
            reader.onload = function(event) {
                const previewContainer = document.createElement('div');
                previewContainer.className = 'img-preview-container text-center mb-3';
                
                const img = document.createElement('img');
                img.src = event.target.result;
                img.className = 'img-thumbnail image-preview';
                
                previewContainer.appendChild(img);
                formGroup.insertBefore(previewContainer, formGroup.firstChild);
            };
            
            reader.readAsDataURL(file);
        }
    });

    // Validación de formulario
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function() {
            this.classList.add('was-validated');
        });
    }
});