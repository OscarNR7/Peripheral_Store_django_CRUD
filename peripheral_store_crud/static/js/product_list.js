document.addEventListener('DOMContentLoaded', function() {
    // Inicializar todos los modales una sola vez
    const viewProductModal = new bootstrap.Modal(document.getElementById('viewProductModal'));
    const editProductModal = new bootstrap.Modal(document.getElementById('editProductModal'));
    const deleteProductModal = new bootstrap.Modal(document.getElementById('deleteProductModal'));
    const createProductModal = new bootstrap.Modal(document.getElementById('createProductModal'));

    // Handle View Product
    document.querySelectorAll('.view-product').forEach(button => {
        button.addEventListener('click', () => {
            const urlBase = button.dataset.url;
            const urlModal = urlBase + (urlBase.includes('?') ? '&' : '?') + 'modal=true';

            fetch(urlModal)
                .then(response => {
                    if (!response.ok) throw new Error('No se pudo cargar el detalle');
                    return response.text();
                })
                .then(html => {
                    document.getElementById('viewProductDetails').innerHTML = html;
                    viewProductModal.show(); // Usar la instancia existente
                })
                .catch(err => {
                    document.getElementById('viewProductDetails').innerHTML = 
                        `<p class="text-danger">${err.message}</p>`;
                    viewProductModal.show();
                });
        });
    });
      
    // Handle Edit from View
    // Handle Edit from View
document.getElementById('editFromViewBtn').addEventListener('click', function() {
    // Obtener el slug desde el contenido cargado
    const slug = document.getElementById('viewProductDetails')
      .querySelector('[data-product-slug]').dataset.productSlug;
    
    viewProductModal.hide(); // Usar la instancia existente
    
    fetch(`/products/${slug}/update/?modal=true`)
      .then(response => response.text())
      .then(html => {
        document.getElementById('editProductForm').innerHTML = html;
        initFormScripts();
        editProductModal.show(); // Usar la instancia existente <--- Aquí está el cambio
      });
  });

    // Handle Edit Product
    const editButtons = document.querySelectorAll('.edit-product');
    editButtons.forEach(button => {
      button.addEventListener('click', function() {
        const slug = this.getAttribute('data-product-slug');
        
        fetch(`/products/${slug}/update/?modal=true`)
          .then(response => response.text())
          .then(html => {
            document.getElementById('editProductForm').innerHTML = html;
            initFormScripts();
            editProductModal.show(); // Usar la instancia existente
          });
      });
    });

    // Handle Delete Product
    const deleteButtons = document.querySelectorAll('.delete-product');
    deleteButtons.forEach(button => {
      button.addEventListener('click', function() {
        const slug = this.getAttribute('data-product-slug');
        const name = this.getAttribute('data-product-name');
        
        document.getElementById('deleteProductName').textContent = name;
        document.getElementById('deleteProductForm').action = `/products/${slug}/delete/`;
        deleteProductModal.show(); // Usar la instancia existente
      });
    });

    function initFormScripts() {
      // Initialize tabs if they exist
      const tabTriggers = document.querySelectorAll('[data-bs-toggle="tab"]');
      tabTriggers.forEach(trigger => {
        new bootstrap.Tab(trigger);
      });

      // Add image formset functionality
      const addImageBtn = document.getElementById('add-image');
      if (addImageBtn) {
        addImageBtn.addEventListener('click', function() {
          const totalImageForms = document.getElementById('id_images-TOTAL_FORMS');
          const formCount = parseInt(totalImageForms.value);
          const newForm = document.querySelector('.image-form').cloneNode(true);
          
          // Clear values
          newForm.querySelectorAll('input:not([type=hidden])').forEach(input => input.value = '');
          newForm.querySelectorAll('input[type=checkbox]').forEach(checkbox => checkbox.checked = false);
          newForm.querySelectorAll('img').forEach(img => img.remove());
          
          // Update IDs and names
          newForm.querySelectorAll('input, select, textarea').forEach(element => {
            const name = element.getAttribute('name').replace('-0-', `-${formCount}-`);
            const id = `id_${name}`;
            element.setAttribute('name', name);
            element.setAttribute('id', id);
          });
          
          // Insert the new form
          document.querySelector('.image-form:last-of-type').after(newForm);
          totalImageForms.value = formCount + 1;
        });
      }

      // Add specification formset functionality
      const addSpecBtn = document.getElementById('add-spec');
      if (addSpecBtn) {
        addSpecBtn.addEventListener('click', function() {
          const totalSpecForms = document.getElementById('id_specs-TOTAL_FORMS');
          const formCount = parseInt(totalSpecForms.value);
          const newForm = document.querySelector('.spec-form').cloneNode(true);
          
          // Clear values
          newForm.querySelectorAll('input:not([type=hidden])').forEach(input => input.value = '');
          
          // Update IDs and names
          newForm.querySelectorAll('input, select, textarea').forEach(element => {
            const name = element.getAttribute('name').replace('-0-', `-${formCount}-`);
            const id = `id_${name}`;
            element.setAttribute('name', name);
            element.setAttribute('id', id);
          });
          
          // Insert the new form
          document.querySelector('.spec-form:last-of-type').after(newForm);
          totalSpecForms.value = formCount + 1;
        });
      }
    }
  });
