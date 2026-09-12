(function() {
"use strict";

gsap.registerPlugin(ScrollTrigger);

window.App = {};

App.config = {
  cursorFollower: {
    enabled: true,
    disableBreakpoint: '992', // cursor will be disabled on this device width
  },
}

App.html = document.querySelector('html');
App.body = document.querySelector('body');
App.SMcontroller = new ScrollMagic.Controller();

window.onload = function () {
  document.fonts.ready.then(function () {
    initialReveal()
  })
}

function initialReveal() {
  const preloader = document.querySelector('.js-preloader')
  
  if (!preloader) {
    RevealAnim.init()
    initComponents()
    return
  }

  setTimeout(() => {
    preloader.classList.add('-is-hidden')
    initComponents()
    RevealAnim.init()
  }, 600)
}


// Reloads all scripts when navigating through pages
function initComponents() {
  sectionSlider()
  marquee()
  headerSticky()
  menuAccordion()
  menuEvents()
  Tabs.init()
  Accordion.init()
  lazyLoading()
  parallaxInit()
  mapCard()
  galleryInit()
  Cursor.init()

  heroSlider7()
  heroSlider9()
  heroSlider10()

  Select.init(".js-select")
  priceRangeSliderInit()
  requestForm()

  splitText()
  parallaxIt()
  hero1Reveal()
  toTopButton()
  tabsSlider()
  hero5Reveal()
  testimonialsSlider1()

  //
	// your custom plugins init here
  //
}

function heroSlider7() {
  const target = document.querySelector('.js-hero-type-7 .js-slider')

  new Swiper(target, {
    speed: 600,
    parallax: true,
    lazy: true,
    spaceBetween: 0,
    slidesPerView: 1,

    lazy: {
      loadPrevNext: true,
    },
    navigation: {
      prevEl: ".js-prev",
      nextEl: ".js-next",
    },
  })
}

function heroSlider9() {
  const target = document.querySelector('.js-hero-type-9 .js-slider')

  if (!target) return

  new Swiper(target, {
    // direction: "vertical",
    speed: 600,
    parallax: true,
    lazy: true,
    spaceBetween: 0,
    slidesPerView: 1,
    lazy: {
      loadPrevNext: true,
    },
    pagination: {
      el: '.js-nav',
      clickable: true,
      renderBullet: function (index, className) {
        return `<div class="${className}">0${index + 1}</div>`
      },
    },
    navigation: {
      prevEl: ".js-prev",
      nextEl: ".js-next",
    },
  })
}

function heroSlider10() {
  const target = document.querySelector('.js-hero-type-10 .js-slider')

  new Swiper(target, {
    direction: "vertical",
    speed: 600,
    parallax: true,
    lazy: true,
    spaceBetween: 0,
    slidesPerView: 1,
    mousewheel: {
      invert: false,
    },
    lazy: {
      loadPrevNext: true,
    },
    pagination: {
      el: '.js-pagination',
      bulletClass: 'pagination__item',
      bulletActiveClass: 'is-active',
      bulletElement: 'div',
      clickable: true
    }
  })
}

function mapCard() {
  const targets = document.querySelectorAll('.js-mapPlaces')
  
  targets.forEach((target) => {
    const cards = target.querySelectorAll('[data-map-card]')
    const buttons = target.querySelectorAll(`[data-map-place]`)

    cards.forEach((el) => {
      const attrVal = el.getAttribute('data-map-card')
      const button = target.querySelector(`[data-map-place="${attrVal}"]`)

      el.addEventListener('click', (e) => {
        cards.forEach((el) => el.classList.remove('isCardActive'))
        buttons.forEach((el) => el.classList.remove('isActive'))

        if (!el.classList.contains('isCardActive')) {
          button.classList.toggle('isActive')
          el.classList.add('isCardActive')
        }
      })
    })
  })
}

function galleryInit() {
  GLightbox({
    selector: '.js-gallery',
    touchNavigation: true,
    loop: false,
    autoplayVideos: true,
  });
}

function priceRangeSliderInit() {
  const targets = document.querySelectorAll('.js-price-rangeSlider')

  targets.forEach(el => {
    const slider = el.querySelector('.js-slider')

    noUiSlider.create(slider, {
      start: [20, 70000],
      step: 1,
      connect: true,
      range: {
        'min': 0,
        'max': 100000
      },
      format: {
        to: function (value) {
          return "$" + value.toFixed(0)
        },
  
        from: function (value) {
          return value
        }
      }
    })
  
    const snapValues = [
      el.querySelector('.js-lower'),
      el.querySelector('.js-upper')
    ]
  
    slider.noUiSlider.on('update', function (values, handle) {
      snapValues[handle].innerHTML = values[handle];
    })
  })
}

function requestForm() {
  const buttons = document.querySelectorAll('.js-toggle-requestForm')
  const form = document.querySelector('.js-requestForm')

  if (!buttons || !form) return

  buttons.forEach((el) => {
    el.addEventListener('click', () => form.classList.toggle('is-active'))
  })
}

function splitText() {
  splt({
    target: ".js-splt"
  })
}

function parallaxIt() {
  const target = document.querySelectorAll('.js-mouse-move-container')

  target.forEach(container => {
    const $this = container
    const targets = container.querySelectorAll('.js-mouse-move')
    
    targets.forEach(el => {
      const movement = el.getAttribute('data-move')

      document.addEventListener('mousemove', (e) => {
        const relX = e.pageX - $this.offsetLeft
        const relY = e.pageY - $this.offsetTop
      
        gsap.to(el, {
          x: (relX - $this.offsetWidth / 2) / $this.offsetWidth * -movement,
          duration: 0.4,
        })
      })
    })
  })
}

function hero1Reveal() {
  const hero = document.querySelector('.js-hero-type-1')
  if (!hero) return

  const title = hero.querySelectorAll('.js-title .char')
  const bg = hero.querySelector('.js-bg')
  const image = hero.querySelector('.js-image')

  gsap.timeline()
    .fromTo(title, {
      opacity: 0,
      y: "-100%",
      rotate: "12deg",
    }, {
      rotate: "0",
      y: "0%",
      opacity: 1,
      duration: 0.25,
      delay: 1.0,
      stagger: 0.1,
    })
    .fromTo(image, {
      opacity: 0,
      y: "32px",
    }, {
      y: "0px",
      opacity: 1,
      duration: 0.5,
    })
}

function hero5Reveal() {
  const hero = document.querySelector('.js-hero-type-5')
  if (!hero) return

  const lines = hero.querySelector('.js-lines')
  const icon = hero.querySelector('.js-icon')
  const image = hero.querySelector('.js-image')
  const subtitle = hero.querySelectorAll('.js-subtitle > *')
  const title = hero.querySelector('.js-title')
  const text = hero.querySelector('.js-text')
  const button = hero.querySelector('.js-button')

  gsap.timeline()
    .fromTo(lines, {
      opacity: 0,
      scale: 0.95,
    }, {
      opacity: 1,
      scale: 1,
      duration: 0.5,
      delay: 0.5,
    })
    .fromTo(icon, {
      opacity: 0,
      scale: 0.95,
    }, {
      opacity: 1,
      scale: 1,
      duration: 0.5,
      delay: 0.1,
    })
    .fromTo(image, {
      opacity: 0,
      x: "32px",
    }, {
      x: "0px",
      opacity: 1,
      duration: 0.5,
      delay: 0.1,
    })

    .fromTo(subtitle, {
      opacity: 0,
      scale: 0.95,
    }, {
      scale: 1,
      opacity: 1,
      duration: 0.5,
      stagger: 0.5,
      delay: 0.2,
    })
    .fromTo([title, text, button], {
      opacity: 0,
      x: "20px",
    }, {
      x: "0px",
      opacity: 1,
      duration: 0.5,
      stagger: 0.5,
    })
}

function toTopButton() {
  const button = document.querySelector('.js-top-button')

  if (!button) return

  new ScrollMagic.Scene({ duration: '300px', })
    .setClassToggle(button, 'is-hidden')
    .addTo(App.SMcontroller)

  button.addEventListener('click', () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    })
  })
}

function tabsSlider() {
  const slider = document.querySelector('.js-tabsSlider')

  if (!slider) return

  new Swiper(slider, {
    speed: 400,
    slidesPerView: 1,
    spaceBetween: 0,
    // effect: "fade",
    navigation: {
      prevEl: '.js-tabsSlider-prev',
      nextEl: '.js-tabsSlider-next',
    },
    pagination: {
      el: document.querySelector('.js-tabsSlider-pagination'),
      clickable: true,
      renderBullet: function (index, className) {
        return `<div class="${className}">VILLA STYLE ${index + 1}</div>`
      },
    }
  })
}

function testimonialsSlider1() {
  const slider = document.querySelector('.js-section-slider-testimonials')
  if (!slider) return

  const images = document.querySelector('.js-section-slider-testimonials-images')

  const swiper = new Swiper(slider, {
    speed: 400,
    slidesPerView: 1,
    spaceBetween: 0,
    navigation: {
      prevEl: '.js-section-slider-testimonials-prev',
      nextEl: '.js-section-slider-testimonials-next',
    },
  })

  swiper.on('slideChange', function () {
    console.log(swiper.realIndex)
    images.style.transform = `translateX(${swiper.realIndex * -100}%)`
  })
}

function headerSticky() {
  const target = document.querySelector(".js-header")

  window.addEventListener('scroll', () => {
    if (window.scrollY > 20) {
      target.classList.add('-is-sticky')
    } else {
      target.classList.remove('-is-sticky')
    }
  })
}

function menuAccordion() {
  const menu = document.querySelector('.js-menu')
  const hasSubmenu = menu.querySelectorAll('.js-has-submenu')

  hasSubmenu.forEach((el) => {
    const buttonLink = el.querySelector("* > a")
    const submenu = el.querySelector("* > .js-submenu")

    buttonLink.addEventListener('click', (e) => {
      e.preventDefault()

      if (submenu.classList.contains('-is-active')) {
        submenu.classList.remove('-is-active')
        submenu.style.maxHeight = null
      } else {
        submenu.classList.add('-is-active')
        submenu.style.maxHeight = submenu.scrollHeight + "px"
      }
    })
  })
}


function menuEvents() {
  let isMenuOpen = false
  const menuButtons = document.querySelectorAll('.js-menu-button')

  menuButtons.forEach((el) => {
    el.addEventListener('click', (e) => {
      if (!isMenuOpen) {
        menuOpen()
        isMenuOpen = true
      } else {
        menuClose()
        isMenuOpen = false
      }
    })
  })
}

function menuOpen() {
  const menu = document.querySelector('.js-menu')
  const header = document.querySelector('.js-header')

  gsap.timeline()
    .to(menu, {
      opacity: 1,
      onStart: () => {
        menu.classList.add("-is-active")
        document.body.classList.add("overflow-hidden")
        header.classList.add("-dark")
      }
    })
}

function menuClose() {
  const menu = document.querySelector('.js-menu')
  const header = document.querySelector('.js-header')

  gsap.timeline()
    .to(menu, {
      opacity: 0,
      onStart: () => {
        menu.classList.remove("-is-active")
        document.body.classList.remove("overflow-hidden")
        header.classList.remove("-dark")
      }
    })
}

function marquee() {
  const targets = document.querySelectorAll('.js-marquee')

  if (!targets) return

  targets.forEach((el) => {
    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: el,
        start: "top bottom",
        scrub: 1,
        // markers: true,
      }
    })
  
    tl
      .to(".js-first", {duration: 4, xPercent: -80})
      .to(".js-second", {duration: 4, xPercent: 80}, "<")
  })
}

/*--------------------------------------------------
  08. Section sliders
---------------------------------------------------*/

function sectionSlider() {
  const sectionSlider = document.querySelectorAll('.js-section-slider');
  if (!sectionSlider.length) return;

  for (let i = 0; i < sectionSlider.length; i++) {
    const el = sectionSlider[i];

    let prevNavElement = el.querySelector('.js-prev')
    let nextNavElement = el.querySelector('.js-next')

    if (el.getAttribute('data-nav-prev'))
      prevNavElement = document.querySelector(`.${el.getAttribute('data-nav-prev')}`)
    if (el.getAttribute('data-nav-next'))
      nextNavElement = document.querySelector(`.${el.getAttribute('data-nav-next')}`)
    
    let gap = 0;
    let loop = false;
    let centered = false;
    let pagination = false;
    let scrollbar = false;

    if (el.getAttribute('data-gap'))    gap = el.getAttribute('data-gap');
    if (el.hasAttribute('data-loop'))   loop = true;
    if (el.hasAttribute('data-center')) centered = true;

    if (el.getAttribute('data-pagination')) {
      let paginationElement = document.querySelector(`.${el.getAttribute('data-pagination')}`)
      
      pagination = {
        el: paginationElement,
        bulletClass: 'pagination__item',
        bulletActiveClass: 'is-active',
        bulletElement: 'div',
        clickable: true,
        renderBullet: function (index, className) {
          return '<span class="' + className + '">' + 0 + (index + 1) + "</span>";
        },
      }
    }

    if (el.hasAttribute('data-scrollbar')) {
      scrollbar = {
        el: '.js-scrollbar',
        draggable: true,
      }
    }
   
    const colsArray = el.getAttribute('data-slider-cols').split(' ');

    let cols_base = 1;
    let cols_xl = 1;
    let cols_lg = 1;
    let cols_md = 1;
    let cols_sm = 1;

    colsArray.forEach(el => {
      if (el.includes('base')) cols_base = el.slice(-1);
      if (el.includes('xl')) cols_xl = el.slice(-1);
      if (el.includes('lg')) cols_lg = el.slice(-1);
      if (el.includes('md')) cols_md = el.slice(-1);
      if (el.includes('sm')) cols_sm = el.slice(-1);
    });

    new Swiper(el, {
      speed: 600,
      autoHeight: true,
      
      centeredSlides: centered,
      parallax: true,
      watchSlidesVisibility: true,
      loop: loop,
      loopAdditionalSlides: 1,
      preloadImages: false,
      lazy: true,
      
      scrollbar: scrollbar,
      pagination: pagination,
      spaceBetween: 10,
      
      // width: 330,
      slidesPerView: parseInt(cols_base),
      breakpoints: {
        1199: { slidesPerView: parseInt(cols_xl), width: null, spaceBetween: parseInt(gap), },
        991: { slidesPerView: parseInt(cols_lg), width: null, spaceBetween: parseInt(gap), },
        767:  { slidesPerView: parseInt(cols_md), width: null, spaceBetween: parseInt(gap), },
        574:  { slidesPerView: parseInt(cols_sm), width: null, spaceBetween: parseInt(gap), },
      },

      lazy: {
        loadPrevNext: true,
      },
      navigation: {
        prevEl: prevNavElement,
        nextEl: nextNavElement,
      },
    })
  }
}

// function featuresMobileSlider() {
//   if (window.innerWidth < 575) {
//     new Swiper('.js-featuresMobileSlider', {
//       speed: 400,
//       slidesPerView: 1,
//       spaceBetween: 10,
//       width: 330,
//       lazy: {
//         loadPrevNext: true,
//       },
//       navigation: {
//         prevEl: '.js-featuresMobileSlider-prev',
//         nextEl: '.js-featuresMobileSlider-next',
//       },
//       pagination: {
//         el: '.js-featuresMobileSlider-pagination',
//         bulletClass: 'pagination__item',
//         bulletActiveClass: 'is-active',
//         bulletElement: 'div',
//         clickable: true
//       }
//     })
//   }
// }

// function testimonialsSlider_1() {
//   const slider = new Swiper('.js-testimonialsSlider_1', {
//     speed: 400,
//     slidesPerView: 1,
//     lazy: {
//       loadPrevNext: true,
//     },
//     pagination: {
//       el: '.js-featuresMobileSlider-pagination',
//       bulletClass: 'pagination__item',
//       bulletActiveClass: 'is-active',
//       bulletElement: 'div',
//       clickable: true
//     }
//   })

//   const paginationItems = document.querySelectorAll('.js-testimonialsSlider_1-pagination > * > *')

//   paginationItems.forEach((el, i) => {
//     el.addEventListener('click', () => {
//       document
//         .querySelector('.js-testimonialsSlider_1-pagination .is-active')
//         .classList.remove('is-active')
//       el.classList.add('is-active')
//       slider.slideTo(i + 1)
//     })
//   })

//   slider.on('slideChangeTransitionStart', () => {
//     document
//       .querySelector('.js-testimonialsSlider_1-pagination .is-active')
//       .classList.remove('is-active')
//     paginationItems[slider.realIndex].classList.add('is-active')
//   })
// }

// function cardImageSlider() {
//   new Swiper('.js-cardImage-slider', {
//     speed: 400,
//     loop: true,
//     lazy: {
//       loadPrevNext: true,
//     },
//     navigation: {
//       prevEl: '.js-prev',
//       nextEl: '.js-next',
//     },
//     pagination: {
//       el: '.js-pagination',
//       bulletClass: 'pagination__item',
//       bulletActiveClass: 'is-active',
//       bulletElement: 'div',
//       clickable: true
//     }
//   })
// }

const Tabs = (function() {
  function init() {
    const targets = document.querySelectorAll(".js-tabs");
    if (!targets) return;

    targets.forEach(el => {
      singleTab(el)
    })
  }

  function singleTab(target) {
    const controls = target.querySelector('.js-tabs-controls');
    const controlsItems = target.querySelectorAll('.js-tabs-controls .js-tabs-button');
    const content = target.querySelector('.js-tabs-content');

    for (let l = 0; l < controlsItems.length; l++) {
      const el = controlsItems[l];
      
      el.addEventListener("click", (e) => {
        const selector = el.getAttribute('data-tab-target');

        controls.querySelector('.is-tab-el-active').classList.remove('is-tab-el-active')
        content.querySelector('.is-tab-el-active').classList.remove('is-tab-el-active')

        el.classList.add('is-tab-el-active')
        content.querySelector(selector).classList.add('is-tab-el-active')
      });
    }
  }

  return {
    init: init,
  }
})();

const Accordion = (function() {
  function init() {
    const targets = document.querySelectorAll(".js-accordion");
    if (!targets) return;

    for (let i = 0; i < targets.length; i++) {
      const items = targets[i].querySelectorAll('.accordion__item');

      for (let l = 0; l < items.length; l++) {
        const button = items[l].querySelector('.accordion__button')
        const content = items[l].querySelector('.accordion__content')
        const titleChange = items[l].querySelector('[data-open-change-title]')
        let buttonOrigTitle
        let buttonNewTitle

        if (items[l].classList.contains('js-accordion-item-active')) {
          items[l].classList.toggle('is-active')
          content.style.maxHeight = content.scrollHeight + "px"
        }

        if (titleChange) {
          buttonOrigTitle = titleChange.innerHTML
          buttonNewTitle = titleChange.getAttribute('data-open-change-title')
        }
        
        button.addEventListener("click", (e) => {
          items[l].classList.toggle('is-active');

          if (titleChange) {
            if (items[l].classList.contains('is-active')) {
              titleChange.innerHTML = buttonNewTitle
            } else {
              titleChange.innerHTML = buttonOrigTitle
            }
          }
  
          if (content.style.maxHeight) {
            content.style.maxHeight = null
          } else {
            content.style.maxHeight = content.scrollHeight + "px"
          }
        })
      }
    }
  }

  return {
    init: init,
  }
})();

const ShowMore = (function() {
  function init() {
    const targets = document.querySelectorAll(".js-show-more");
    if (!targets) return;

    targets.forEach((el, i) => {
      const button = el.querySelector('.show-more__button')
      const content = el.querySelector('.show-more__content')
      
      button.addEventListener("click", (e) => {
        el.classList.toggle('is-active')

        if (content.style.maxHeight) {
          content.style.maxHeight = null
        } else {
          content.style.maxHeight = content.scrollHeight + "px"
        }
      })
    })
  }

  return {
    init: init,
  }
})();

/*--------------------------------------------------
  12. Parallax
---------------------------------------------------*/

function parallaxInit() {
  if (!document.querySelector('[data-parallax]')) return;
  const target = document.querySelectorAll('[data-parallax]')

  target.forEach(el => {
    jarallax(el, {
      speed: el.getAttribute('data-parallax'),
      imgElement: '[data-parallax-target]',
    })
  })
}

/*--------------------------------------------------
  06. Elements reveal
---------------------------------------------------*/

const RevealAnim = (function() {
  function single() {
    const animationTarget = document.querySelectorAll('[data-anim]');
    if (!animationTarget.length) return;

    for (let i = 0; i < animationTarget.length; i++) {
      const el = animationTarget[i];
    
      new ScrollMagic.Scene({
        offset: '350px',
        triggerElement: el,
        triggerHook: "onEnter",
        reverse: false,
      })
      .on('enter', function (event) {
        animateElement(el);
      })
      .addTo(App.SMcontroller)
    }
  }
  
  function container() {
  
    const animationContainer = document.querySelectorAll('[data-anim-wrap]');
  
    if (!animationContainer.length) {
      return;
    }
    
    for (let i = 0; i < animationContainer.length; i++) {
      const el = animationContainer[i];
    
      new ScrollMagic.Scene({
        offset: '350px',
        triggerElement: el,
        triggerHook: "onEnter",
        reverse: false,
      })
      .on('enter', function (event) {
        
        const animChilds = el.querySelectorAll('[data-anim-child]');
        el.classList.add('animated');
        animChilds.forEach(el => animateElement(el));
        
      })
      .addTo(App.SMcontroller)
    }
  
  }
  

  function animateElement(target) {
    
    let attrVal;
    let animDelay;
    let attrDelayPart;
  
    if (target.getAttribute('data-anim')) {
      attrVal = target.getAttribute('data-anim');
    } else {
      attrVal = target.getAttribute('data-anim-child');
    }
    
    if (attrVal.includes('delay-')) {
      attrDelayPart = attrVal.split(' ').pop();
      animDelay = attrDelayPart.substr(attrDelayPart.indexOf('-') + 1) / 10;
    }
  
    if (attrVal.includes('counter')) {
      counter(target, animDelay);
    }
    else if (attrVal.includes('line-chart')) {
      lineChart(target, animDelay);
    }
    else if (attrVal.includes('pie-chart')) {
      pieChart(target, animDelay);
    }
    else if (attrVal.includes('split-lines')) {
      splitLines(target, animDelay);
    }
    else {
      target.classList.add('is-in-view');
    }

  }

  function pieChart(target, animDelay = 0) {
  
    const counterVal = target.getAttribute('data-percent');
    const chartBar = target.querySelector('.js-chart-bar');
    
    if (counterVal < 0) { counterVal = 0;}
    if (counterVal > 100) { counterVal = 100;}
    
    gsap.fromTo(chartBar, {
      drawSVG: `0%`,
    }, {
      delay: 0.3 + animDelay,
      duration: 1.4,
      ease: 'power3.inOut',
      drawSVG: `${counterVal}%`,
  
      onStart: () => {
        chartBar.classList.remove('bar-stroke-hidden');
      }
    });
  
  
    let object = { count: 0 };
    const barPercent = target.querySelector('.js-chart-percent');
  
    gsap.to(object, {
      count: counterVal,
      delay: 0.45 + animDelay,
      duration: 1,
      ease: 'power3.inOut',
      
      onUpdate: function() {
        barPercent.innerHTML = Math.round(object.count) + '%';
      },
    });
  
  }
  
  function lineChart(target, animDelay = 0) {
  
    const counterVal = target.getAttribute('data-percent');
  
    gsap.fromTo(target.querySelector('.js-bar'), {
      scaleX: 0,
    }, {
      delay: 0.45 + animDelay,
      duration: 1,
      ease: 'power3.inOut',
      scaleX: counterVal / 100,
    })
  
  
    let object = { count: 0 };
    const barPercent = target.querySelector('.js-number');
  
    gsap.to(object, {
      count: counterVal,
      delay: 0.45 + animDelay,
      duration: 1,
      ease: 'power3.inOut',
      
      onUpdate: function() {
        barPercent.innerHTML = Math.round(object.count);
      },
    });
  
  }
  
  function counter(target, animDelay = 0) {
  
    const counterVal = target.getAttribute('data-counter');
    const counterAdd = target.getAttribute('data-counter-add');
    const totalDelay = animDelay;
    let symbols = '';
    
    let object = { count: 0 };
    const counterNum = target.querySelector('.js-counter-num');

    if (counterAdd) {
      symbols = counterAdd;
    }
  
    gsap.to(object, {
      count: counterVal,
      delay: totalDelay,
      duration: 1.8,
      ease: 'power3.inOut',
      
      onUpdate: function() {
        counterNum.innerHTML = Math.round(object.count) + symbols;
      },
    });
  
  }

  function init() {
    single();
    container();
  }

  return {
    init: init,
  }
})();

/*--------------------------------------------------
  11. Lazy loading
---------------------------------------------------*/

function lazyLoading() {
  if (!document.querySelector('.js-lazy')) {
    return;
  }

  new LazyLoad({
    elements_selector: ".js-lazy",
  });
}

const Select = (function() {
  function init(selector) {
    document.querySelectorAll(selector).forEach((el) => singleSelect(el))
    document.querySelectorAll('.js-multiple-select').forEach((el) => multipleSelect(el))
  }

  function multipleSelect(target) {
    console.log(target)
    const button = target.querySelector('.js-button')
    const title = button.querySelector('.js-button-title')
    
    button.addEventListener('click', () => {
      let dropdown = target.querySelector('.js-dropdown')
      
      if (dropdown.classList.contains('-is-visible')) {
        dropdown.classList.remove('-is-visible')
      } else {
        closeAlldropdowns()
        dropdown.classList.add('-is-visible')
      }
    })

    const dropdown = target.querySelector('.js-dropdown')
    const options = dropdown.querySelectorAll('.js-options > *')

    options.forEach((el) => {
      el.addEventListener('click', () => {
        let selectedValues = []
        el.classList.toggle('-is-choosen')

        const array = dropdown.querySelectorAll('.-is-choosen .js-target-title')
        array.forEach((el2) => {
          selectedValues.push(el2.innerHTML)
        })

        if (!array.length) {
          title.innerHTML = "Default"
          target.setAttribute("data-select-value", "")
        } else {
          title.innerHTML = selectedValues.join(', ')
          target.setAttribute("data-select-value", selectedValues.join(', '))
        }

        const checkbox = el.querySelector('input')
        checkbox.checked = !checkbox.checked
      })
    })
  }

  function singleSelect(target) {
    const button = target.querySelector('.js-button')
    const title = button.querySelector('.js-button-title')
    
    if (target.classList.contains('js-liveSearch')) {
      liveSearch(target)
    }

    button.addEventListener('click', () => {
      let dropdown = target.querySelector('.js-dropdown')
      
      if (dropdown.classList.contains('-is-visible')) {
        dropdown.classList.remove('-is-visible')
      } else {
        closeAlldropdowns()
        dropdown.classList.add('-is-visible')
      }
      
      if (target.classList.contains('js-liveSearch')) {
        target.querySelector('.js-search').focus()
      }
    })

    const dropdown = target.querySelector('.js-dropdown')
    const options = dropdown.querySelectorAll('.js-options > *')

    options.forEach((el) => {
      el.addEventListener('click', () => {
        title.innerHTML = el.innerHTML
        target.setAttribute("data-select-value", el.getAttribute('data-value'))
        dropdown.classList.toggle('-is-visible')
      })
    })
  }

  function liveSearch(target) {
    const search = target.querySelector('.js-search')
    const options = target.querySelectorAll('.js-options > *')
    
    search.addEventListener('input', (event) => {
      let searchTerm = event.target.value.toLowerCase()

      options.forEach((el) => {
        el.classList.add('d-none')

        if (el.getAttribute('data-value').includes(searchTerm)) {
          el.classList.remove('d-none')
        }
      })
    })
  }

  function closeAlldropdowns() {
    const targets = document.querySelectorAll('.js-select, .js-multiple-select')
    if (!targets) return
    
    targets.forEach(el => {
      if (el.querySelector('.-is-visible')) {
        el.querySelector('.-is-visible').classList.remove('-is-visible')
      }
    })
  }

  return {
    init: init,
  }
})()

/*--------------------------------------------------
  05. Custom cursor
---------------------------------------------------*/

const Cursor = (function() {

  const cursor = document.querySelector(".js-cursor");
  let follower;
  let label;
  let icon;

  let clientX;
  let clientY;
  let cursorWidth;
  let cursorHeight;
  let cursorTriggers;
  let state;

  function variables() {

    follower = cursor.querySelector(".js-follower");
    label = cursor.querySelector(".js-label");
    icon = cursor.querySelector(".js-icon");

    clientX = -100;
    clientY = -100;
    cursorWidth = cursor.offsetWidth / 2;
    cursorHeight = cursor.offsetHeight / 2;
    cursorTriggers;
    state = false;

  }

  function init() {

    if (!cursor) return;

    variables();
    state = true;
    cursor.classList.add('is-enabled');

    document.addEventListener("mousedown", e => {
      cursor.classList.add('is-mouse-down');
    });

    document.addEventListener("mouseup", e => {
      cursor.classList.remove('is-mouse-down');
    });

    document.addEventListener("mousemove", (event) => {
      clientX = event.clientX;
      clientY = event.clientY;
    });

    const render = () => {
      cursor.style.transform = `translate(${clientX - cursorWidth}px, ${clientY - cursorHeight}px)`;
      requestAnimationFrame(render);
    };

    requestAnimationFrame(render);

    update();
    breakpoint();

  }

  function enterHandler({ target }) {

    cursor.classList.add('is-active');

    if (target.getAttribute('data-cursor-label')) {
      App.body.classList.add('is-cursor-active');
      cursor.classList.add('has-label');
      label.innerHTML = target.getAttribute('data-cursor-label');
    }

    if (target.getAttribute('data-cursor-label-light')) {
      App.body.classList.add('is-cursor-active');
      cursor.classList.add('has-label-light');
      label.innerHTML = target.getAttribute('data-cursor-label-light');
    }

    if (target.getAttribute('data-cursor-icon')) {
      App.body.classList.add('is-cursor-active');
      cursor.classList.add('has-icon');
      const iconAttr = target.getAttribute('data-cursor-icon');
      icon.innerHTML = feather.icons[iconAttr].toSvg();
    }

  }
  
  function leaveHandler() {

    App.body.classList.remove('is-cursor-active');
    cursor.classList.remove('is-active');
    cursor.classList.remove('has-label');
    cursor.classList.remove('has-label-light');
    cursor.classList.remove('has-icon');
    label.innerHTML = '';
    icon.innerHTML = '';

  }

  function update() {

    if (!cursor) return;

    cursorTriggers = document.querySelectorAll([
      "button",
      "a",
      "input",
      "[data-cursor]",
      "[data-cursor-label]",
      "[data-cursor-label-light]",
      "[data-cursor-icon]",
      "textarea"
    ]);
    
    cursorTriggers.forEach(el => {
      el.addEventListener("mouseenter", enterHandler);
      el.addEventListener("mouseleave", leaveHandler);
    });

  }

  function clear() {

    if (!cursor) return;
    
    cursorTriggers.forEach(el => {
      el.removeEventListener("mouseenter", enterHandler);
      el.removeEventListener("mouseleave", leaveHandler);
    });

  }

  function hide() {

    if (!cursor) return;
    cursor.classList.add('is-hidden');

  }

  function show() {

    if (!cursor) return;
    cursor.classList.remove('is-hidden');

  }

  function breakpoint() {

    if (!state) return;
    if (!App.config.cursorFollower.disableBreakpoint) return;

    let width = (window.innerWidth > 0) ? window.innerWidth : screen.width;

    if (width < App.config.cursorFollower.disableBreakpoint) {
      state = false;
      cursor.classList.remove('is-enabled');
      clear();
    } else {
      state = true;
      cursor.classList.add('is-enabled');
      update();
    }

    window.addEventListener('resize', () => {
      let width = (window.innerWidth > 0) ? window.innerWidth : screen.width;

      if (width < App.config.cursorFollower.disableBreakpoint) {
        state = false;
        cursor.classList.remove('is-enabled');
        clear();
      } else {
        state = true;
        cursor.classList.add('is-enabled');
        update();
      }
    })

  }

  return {
    init: init,
    leaveHandler: leaveHandler,
    update: update,
    clear: clear,
    hide: hide,
    show: show,
  };

})();


})();
