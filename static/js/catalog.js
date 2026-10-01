/**
 * LEAFS Exotic Vegetables — Catalog
 * Category filter and banner slider.
 */

(function () {
  'use strict';

  // ---- Category filter ----
  document.querySelectorAll('.tab-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      document.querySelectorAll('.tab-btn').forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      var category = btn.dataset.category;
      document.querySelectorAll('.product-card').forEach(function (card) {
        if (category === 'all' || card.dataset.category === category) {
          card.style.display = '';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });

  // ---- Banner Slider ----
  (function () {
    var slider = document.getElementById('bannerSlider');
    if (!slider) return;

    var slides = slider.querySelectorAll('.banner-slide');
    if (slides.length <= 1) return;

    var dots    = slider.querySelectorAll('.dot');
    var current = 0;
    var timer;

    function goTo(index) {
      slides[current].classList.remove('active');
      dots[current] && dots[current].classList.remove('active');
      current = (index + slides.length) % slides.length;
      slides[current].classList.add('active');
      dots[current] && dots[current].classList.add('active');
    }

    function startAuto() {
      timer = setInterval(function () { goTo(current + 1); }, 5000);
    }

    function resetAuto() {
      clearInterval(timer);
      startAuto();
    }

    var prevBtn = slider.querySelector('.banner-prev');
    var nextBtn = slider.querySelector('.banner-next');

    if (prevBtn) prevBtn.addEventListener('click', function () { goTo(current - 1); resetAuto(); });
    if (nextBtn) nextBtn.addEventListener('click', function () { goTo(current + 1); resetAuto(); });

    dots.forEach(function (dot) {
      dot.addEventListener('click', function () { goTo(parseInt(dot.dataset.index)); resetAuto(); });
    });

    // Pause on hover
    slider.addEventListener('mouseenter', function () { clearInterval(timer); });
    slider.addEventListener('mouseleave', startAuto);

    // ---- Drag on left / right edge zones only ----
    var dragZones = slider.querySelectorAll('.banner-drag-zone');
    if (dragZones.length) {
      var dragStartX = 0;
      var dragging   = false;
      var THRESHOLD  = 40;

      dragZones.forEach(function (zone) {
        zone.addEventListener('mousedown', function (e) {
          if (e.button !== 0) return;
          dragStartX = e.clientX;
          dragging   = true;
          clearInterval(timer);
          zone.style.cursor = 'grabbing';
          e.preventDefault();
        });
      });

      document.addEventListener('mouseup', function (e) {
        if (!dragging) return;
        dragging = false;
        dragZones.forEach(function (z) { z.style.cursor = ''; });
        var diff = e.clientX - dragStartX;
        if (Math.abs(diff) >= THRESHOLD) {
          diff < 0 ? goTo(current + 1) : goTo(current - 1);
          resetAuto();
        } else {
          startAuto();
        }
      });

      // Touch swipe on full slider (natural on mobile)
      slider.addEventListener('touchstart', function (e) {
        dragStartX = e.touches[0].clientX;
        clearInterval(timer);
      }, { passive: true });

      slider.addEventListener('touchend', function (e) {
        var diff = e.changedTouches[0].clientX - dragStartX;
        if (Math.abs(diff) >= THRESHOLD) {
          diff < 0 ? goTo(current + 1) : goTo(current - 1);
        }
        startAuto();
      }, { passive: true });
    }

    startAuto();
  }());

})();
