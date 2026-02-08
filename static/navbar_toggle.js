document.addEventListener('DOMContentLoaded', function() {
    const toggler = document.getElementById('navbarToggler');
    const navbarCollapse = document.getElementById('navbarNavDropdown');

    if (toggler && navbarCollapse) {
        toggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('open');
        });
    }
});