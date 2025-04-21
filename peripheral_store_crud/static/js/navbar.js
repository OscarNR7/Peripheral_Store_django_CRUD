document.addEventListener('DOMContentLoaded', function() {
    // Dropdown de usuario
    const userDropdown = document.querySelector('.user-dropdown');
    if (userDropdown) {
        userDropdown.addEventListener('click', function(e) {
            const menu = this.querySelector('.user-menu');
            if (menu) {
                menu.classList.toggle('hidden');
            }
        });
    }

    // Cerrar dropdown al hacer click fuera
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.user-dropdown')) {
            const menus = document.querySelectorAll('.user-menu');
            menus.forEach(menu => {
                menu.classList.add('hidden');
            });
        }
    });

    // Tema oscuro/claro
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.documentElement.classList.toggle('dark');
            localStorage.setItem('theme', document.documentElement.classList.contains('dark') ? 'dark' : 'light');
        });
    }
});