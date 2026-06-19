var $ = jQuery.noConflict();
(function($) {
  "use strict"; // Start of use strict

  // Toggle the side navigation
  $("#sidebarToggle, #sidebarToggleTop").on('click', function(e) {
    $("body").toggleClass("sidebar-toggled");
    $(".sidebar").toggleClass("toggled");
    if ($(".sidebar").hasClass("toggled")) {
      $('.sidebar .collapse').collapse('hide');
    };
    
    // Cambiar ícono del toggle
    var toggleIcon = $(this).find('i');
    if (toggleIcon.length) {
      if ($(".sidebar").hasClass("toggled")) {
        toggleIcon.removeClass('fa-chevron-left');
        toggleIcon.addClass('fa-chevron-right');
      } else {
        toggleIcon.removeClass('fa-chevron-right');
        toggleIcon.addClass('fa-chevron-left');
      }
    }
  });

  // Close any open menu accordions when window is resized below 768px
  $(window).resize(function() {
    if ($(window).width() < 768) {
      $('.sidebar .collapse').collapse('hide');
    };
    
    // Toggle the side navigation when window is resized below 480px
    if ($(window).width() < 480 && !$(".sidebar").hasClass("toggled")) {
      $("body").addClass("sidebar-toggled");
      $(".sidebar").addClass("toggled");
      $('.sidebar .collapse').collapse('hide');
    };
  });

  // Prevent the content wrapper from scrolling when the fixed side navigation hovered over
  $('body.fixed-nav .sidebar').on('mousewheel DOMMouseScroll wheel', function(e) {
    if ($(window).width() > 768) {
      var e0 = e.originalEvent,
        delta = e0.wheelDelta || -e0.detail;
      this.scrollTop += (delta < 0 ? 1 : -1) * 30;
      e.preventDefault();
    }
  });

  // Scroll to top button appear
  $(document).on('scroll', function() {
    var scrollDistance = $(this).scrollTop();
    if (scrollDistance > 100) {
      $('.scroll-to-top').fadeIn();
    } else {
      $('.scroll-to-top').fadeOut();
    }
  });

  // Smooth scrolling using jQuery easing
  $(document).on('click', 'a.scroll-to-top', function(e) {
    var $anchor = $(this);
    $('html, body').stop().animate({
      scrollTop: ($($anchor.attr('href')).offset().top)
    }, 1000, 'easeInOutExpo');
    e.preventDefault();
  });

})(jQuery); // End of use strict

// Funciones para abrir modales (sin cambios)
function abrir_modal_edicion(url) {
    $.ajax({
        url: url,
        type: 'GET',
        success: function(data) {
            $('#edicion').html(data);
            $('#edicion').modal('show');
        },
        error: function(xhr, status, error) {
            console.error("Error al cargar el modal de edición:", error);
            showToast('error', 'Error', 'No se pudo cargar el formulario de edición');
        }
    });
}

function abrir_modal_registro(url) {
    $.ajax({
        url: url,
        type: 'GET',
        success: function(data) {
            $('#edicion').html(data);
            $('#edicion').modal('show');
        },
        error: function(xhr, status, error) {
            console.error("Error al cargar el modal de registro:", error);
            showToast('error', 'Error', 'No se pudo cargar el formulario de registro');
        }
    });
}
/*
// Función para abrir modal de eliminación
function abrir_modal_eliminacion(url, nombreDocumento) {
  // Configurar el contenido del modal
  $('#eliminacion #documentName').text(nombreDocumento);
  
  // Cargar el modal
  $('#eliminacion').modal('show');
  
  // Configurar el evento de eliminación
  configurarEliminacion(url);
}*/