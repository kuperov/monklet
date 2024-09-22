'use strict';

window.isDarkStyle = window.Helpers.isDarkStyle();

(function () {
  // Button & Pagination Waves effect
  // if (typeof Waves !== 'undefined') {
  //   Waves.init();
  //   Waves.attach(
  //     ".btn[class*='btn-']:not(.position-relative):not([class*='btn-outline-']):not([class*='btn-label-'])",
  //     ['waves-light']
  //   );
  //   Waves.attach("[class*='btn-outline-']:not(.position-relative)");
  //   Waves.attach("[class*='btn-label-']:not(.position-relative)");
  //   Waves.attach('.pagination .page-item .page-link');
  //   Waves.attach('.dropdown-menu .dropdown-item');
  //   Waves.attach('.light-style .list-group .list-group-item-action');
  //   Waves.attach('.dark-style .list-group .list-group-item-action', ['waves-light']);
  //   Waves.attach('.nav-tabs:not(.nav-tabs-widget) .nav-item .nav-link');
  //   Waves.attach('.nav-pills .nav-item .nav-link', ['waves-light']);
  // }

  // color scheme
  // const style = (window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light';
  // const classesToRemove = style === 'light' ? ['dark-style'] : ['light-style']
  // classesToRemove.forEach(cls => {
  //   document.documentElement.classList.remove(cls)
  // })
  // document.documentElement.classList.add(`${style}-style`)

  const menu = document.getElementById('navbarSupportedContent'),
    nav = document.querySelector('.landing-navbar'),
    navItemLink = document.querySelectorAll('.navbar-nav .nav-link');

  // Navbar
  window.addEventListener('scroll', e => {
    if (window.scrollY > 10) {
      nav.classList.add('navbar-active');
    } else {
      nav.classList.remove('navbar-active');
    }
  });
  window.addEventListener('load', e => {
    if (window.scrollY > 10) {
      nav.classList.add('navbar-active');
    } else {
      nav.classList.remove('navbar-active');
    }
  });

  // Function to close the mobile menu
  function closeMenu() {
    menu.classList.remove('show');
  }

  document.addEventListener('click', function (event) {
    // Check if the clicked element is inside mobile menu
    if (!menu.contains(event.target)) {
      closeMenu();
    }
  });

  navItemLink.forEach(link => {
    link.addEventListener('click', event => {
      if (!link.classList.contains('dropdown-toggle')) {
        closeMenu();
      } else {
        event.preventDefault();
      }
    });
  });

})();
