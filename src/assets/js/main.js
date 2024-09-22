/**
 * Main
 */

'use strict';

window.isDarkStyle = window.Helpers.isDarkStyle();
let menu,
  animate,
  isHorizontalLayout = false;

if (document.getElementById('layout-menu')) {
  isHorizontalLayout = document.getElementById('layout-menu').classList.contains('menu-horizontal');
}

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
  //   Waves.attach('.menu-vertical .menu-item .menu-link.menu-toggle');
  // }

  // select light/dark mode based on system preference
  // const style = (window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light';
  // const classesToRemove = style === 'light' ? ['dark-style'] : ['light-style']
  // classesToRemove.forEach(cls => {
  //   document.documentElement.classList.remove(cls)
  // })
  // document.documentElement.classList.add(`${style}-style`);

  // Window scroll function for navbar
  function onScroll() {
    var layoutPage = document.querySelector('.layout-page');
    if (layoutPage) {
      if (window.pageYOffset > 0) {
        layoutPage.classList.add('window-scrolled');
      } else {
        layoutPage.classList.remove('window-scrolled');
      }
    }
  }
  // On load time out
  setTimeout(() => {
    onScroll();
  }, 200);

  // On window scroll
  window.onscroll = function () {
    onScroll();
  };

  setTimeout(function () {
    window.Helpers.initCustomOptionCheck();
  }, 1000);

  // Initialize menu
  //-----------------

  let layoutMenuEl = document.querySelector('#layout-menu');
  menu = new Menu(layoutMenuEl, {
    orientation: 'vertical',
    closeChildren: false,
  });
  // Change parameter to true if you want scroll animation
  window.Helpers.scrollToActive((animate = false));
  window.Helpers.mainMenu = menu;

  // Initialize menu togglers and bind click on each
  let menuToggler = document.querySelectorAll('.layout-menu-toggle');
  menuToggler.forEach(item => {
    item.addEventListener('click', event => {
      event.preventDefault();
      window.Helpers.toggleCollapsed();
      // Enable menu state with local storage support if enableMenuLocalStorage = true from config.js
      if (config.enableMenuLocalStorage && !window.Helpers.isSmallScreen()) {
        try {
          localStorage.setItem(
            'templateCustomizer-' + templateName + '--LayoutCollapsed',
            String(window.Helpers.isCollapsed())
          );
          // Update customizer checkbox state on click of menu toggler
          let layoutCollapsedCustomizerOptions = document.querySelector('.template-customizer-layouts-options');
          if (layoutCollapsedCustomizerOptions) {
            let layoutCollapsedVal = window.Helpers.isCollapsed() ? 'collapsed' : 'expanded';
            layoutCollapsedCustomizerOptions.querySelector(`input[value="${layoutCollapsedVal}"]`).click();
          }
        } catch (e) {}
      }
    });
  });

  // Menu swipe gesture

  // Detect swipe gesture on the target element and call swipe In
  window.Helpers.swipeIn('.drag-target', function (e) {
    window.Helpers.setCollapsed(false);
  });

  // Detect swipe gesture on the target element and call swipe Out
  window.Helpers.swipeOut('#layout-menu', function (e) {
    if (window.Helpers.isSmallScreen()) window.Helpers.setCollapsed(true);
  });

  // Display in main menu when menu scrolls
  let menuInnerContainer = document.getElementsByClassName('menu-inner'),
    menuInnerShadow = document.getElementsByClassName('menu-inner-shadow')[0];
  if (menuInnerContainer.length > 0 && menuInnerShadow) {
    menuInnerContainer[0].addEventListener('ps-scroll-y', function () {
      if (this.querySelector('.ps__thumb-y').offsetTop) {
        menuInnerShadow.style.display = 'block';
      } else {
        menuInnerShadow.style.display = 'none';
      }
    });
  }
})();
