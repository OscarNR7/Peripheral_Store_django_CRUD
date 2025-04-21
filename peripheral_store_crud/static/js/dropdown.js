// Manejo del dropdown de perfil
document.addEventListener('DOMContentLoaded', function() {
    const profileBtn = document.getElementById('profile-dropdown-btn');
    const profileDropdown = document.getElementById('profile-dropdown');
    
    if (profileBtn && profileDropdown) {
        // Toggle del dropdown
        profileBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            profileDropdown.classList.toggle('hidden');
        });
        
        // Cerrar al hacer clic fuera
        document.addEventListener('click', function() {
            profileDropdown.classList.add('hidden');
        });
        
        // Prevenir que el dropdown se cierre al hacer clic dentro
        profileDropdown.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
    
    // Cerrar dropdown al hacer submit en el logout
    const logoutForm = document.querySelector('#profile-dropdown form');
    if (logoutForm) {
        logoutForm.addEventListener('submit', function() {
            profileDropdown.classList.add('hidden');
        });
    }
});