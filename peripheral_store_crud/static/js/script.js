document.addEventListener('DOMContentLoaded', function() {
    // Elementos principales
    const body = document.querySelector('body');
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.querySelector('.toggle-container');
    const themeControl = document.querySelector('.theme-control');
    const profileDropdown = document.querySelector('.profile-dropdown');
    
    // 1. Toggle de la barra lateral
    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('close');
        localStorage.setItem('sidebarState', sidebar.classList.contains('close') ? 'closed' : 'open');
    });

    // 2. Toggle del tema oscuro
    themeControl.addEventListener('click', () => {
        body.classList.toggle('dark-theme');
        
        if(body.classList.contains('dark-theme')) {
            localStorage.setItem('theme', 'dark');
        } else {
            localStorage.setItem('theme', 'light');
        }
    });

    // 3. Dropdown de perfil
    profileDropdown.addEventListener('click', function(e) {
        e.stopPropagation();
        this.classList.toggle('active');
    });
    
    // Cerrar dropdown al hacer clic fuera
    document.addEventListener('click', function() {
        profileDropdown.classList.remove('active');
    });

    // 4. Cargar estados guardados
    function loadSavedStates() {
        // Estado de la barra lateral
        const sidebarState = localStorage.getItem('sidebarState');
        if(sidebarState === 'closed') {
            sidebar.classList.add('close');
        } else if(window.innerWidth < 768) {
            sidebar.classList.add('close');
            localStorage.setItem('sidebarState', 'closed');
        }

        // Estado del tema
        if(localStorage.getItem('theme') === 'dark') {
            body.classList.add('dark-theme');
        }
    }

    // 5. Manejo responsive
    function handleResponsive() {
        if(window.innerWidth < 768 && !sidebar.classList.contains('close')) {
            sidebar.classList.add('close');
            localStorage.setItem('sidebarState', 'closed');
        }
    }

    // Inicialización
    loadSavedStates();
    handleResponsive();
    window.addEventListener('resize', handleResponsive);
});