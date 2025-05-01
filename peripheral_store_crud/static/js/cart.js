
document.addEventListener('DOMContentLoaded', function() {
    // Manejar añadir al carrito AJAX
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    if (addToCartForms) {
        addToCartForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                const formData = new FormData(this);
                
                fetch(this.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    credentials: 'same-origin'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Actualizar contador de carrito en el navbar
                        document.querySelectorAll('.cart-count').forEach(el => {
                            el.textContent = data.cart_count;
                        });
                        
                        // Mostrar mensaje de éxito
                        showToast('Success', data.message, 'success');
                    } else {
                        showToast('Error', data.message, 'danger');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showToast('Error', 'An error occurred while processing your request.', 'danger');
                });
            });
        });
    }
    
    // Manejar actualización de cantidad en el carrito
    const updateCartForms = document.querySelectorAll('.update-cart-form');
    if (updateCartForms) {
        updateCartForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                const formData = new FormData(this);
                
                fetch(this.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    credentials: 'same-origin'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Actualizar contador de carrito en el navbar
                        document.querySelectorAll('.cart-count').forEach(el => {
                            el.textContent = data.cart_count;
                        });
                        
                        // Actualizar subtotal del carrito
                        document.querySelectorAll('.cart-subtotal').forEach(el => {
                            el.textContent = `$${data.subtotal}`;
                        });
                        
                        // Si la cantidad es 0, eliminar la fila
                        const quantityInput = form.querySelector('input[name="quantity"]');
                        if (parseInt(quantityInput.value) === 0) {
                            const cartRow = form.closest('tr');
                            if (cartRow) {
                                cartRow.remove();
                            }
                        }
                        
                        // Mostrar mensaje
                        showToast('Success', data.message, 'success');
                        
                        // Si el carrito está vacío, recargar la página
                        if (data.cart_count === 0) {
                            window.location.reload();
                        }
                    } else {
                        showToast('Error', data.message, 'danger');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showToast('Error', 'An error occurred while processing your request.', 'danger');
                });
            });
        });
    }
    
    // Manejar eliminar item del carrito
    const removeItemForms = document.querySelectorAll('.remove-item-form');
    if (removeItemForms) {
        removeItemForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                if (!confirm('Are you sure you want to remove this item from your cart?')) {
                    return;
                }
                
                const formData = new FormData(this);
                
                fetch(this.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    credentials: 'same-origin'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Actualizar contador de carrito en el navbar
                        document.querySelectorAll('.cart-count').forEach(el => {
                            el.textContent = data.cart_count;
                        });
                        
                        // Actualizar subtotal del carrito
                        document.querySelectorAll('.cart-subtotal').forEach(el => {
                            el.textContent = `$${data.subtotal}`;
                        });
                        
                        // Eliminar la fila del carrito
                        const cartRow = form.closest('tr');
                        if (cartRow) {
                            cartRow.remove();
                        }
                        
                        // Mostrar mensaje
                        showToast('Success', data.message, 'success');
                        
                        // Si el carrito está vacio, recargar la página
                        if (data.cart_count === 0) {
                            window.location.reload();
                        }
                    } else {
                        showToast('Error', data.message, 'danger');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showToast('Error', 'An error occurred while processing your request.', 'danger');
                });
            });
        });
    }
    
    // Manejar vaciar carrito
    const clearCartForm = document.querySelector('.clear-cart-form');
    if (clearCartForm) {
        clearCartForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (!confirm('Are you sure you want to clear your entire cart?')) {
                return;
            }
            
            const formData = new FormData(this);
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Actualizar contador de carrito en el navbar
                    document.querySelectorAll('.cart-count').forEach(el => {
                        el.textContent = '0';
                    });
                    
                    // Mostrar mensaje y recargar la página
                    showToast('Success', data.message, 'success');
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    showToast('Error', data.message, 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Error', 'An error occurred while processing your request.', 'danger');
            });
        });
    }
    
    // Función para mostrar notificaciones toast
    function showToast(title, message, type = 'info') {
        // Si estás usando Bootstrap Toast
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            // Crear un contenedor si no existe
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(container);
        }
        
        const toastId = `toast-${Date.now()}`;
        const toastHTML = `
            <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        <strong>${title}</strong>: ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;
        
        document.getElementById('toast-container').insertAdjacentHTML('beforeend', toastHTML);
        
        // Inicializar y mostrar el toast usando Bootstrap 5
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            delay: 5000
        });
        toast.show();
    }
    
    // Función para actualizar el contador de carrito
    function updateCartCounter(count) {
        document.querySelectorAll('.cart-count').forEach(el => {
            el.textContent = count;
        });
    }
});