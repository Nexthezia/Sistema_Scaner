// Script para menú mobile
document.addEventListener('DOMContentLoaded', () => {
    const btnMenuMobile = document.getElementById('btnMenuMobile');
    const menuLinks = document.getElementById('menuLinks');

    if (btnMenuMobile) {
        btnMenuMobile.addEventListener('click', () => {
            btnMenuMobile.classList.toggle('activo');
            menuLinks.classList.toggle('mostrar');
        });

        // Cerrar menú al hacer click en un link
        menuLinks.querySelectorAll('.link-menu').forEach(link => {
            link.addEventListener('click', () => {
                btnMenuMobile.classList.remove('activo');
                menuLinks.classList.remove('mostrar');
            });
        });

        // Cerrar menú al hacer click fuera
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.MenuContenedor')) {
                btnMenuMobile.classList.remove('activo');
                menuLinks.classList.remove('mostrar');
            }
        });
    }
});
