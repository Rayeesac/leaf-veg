/**
 * LEAFS Chinese Vegetables — Catalog Cart Engine
 * Manages weight inputs, live subtotals, order drawer, and form submission.
 */

(function () {
  'use strict';

  // ---- Enforce min pickup date = tomorrow (client-side) ----
  var dateInput = document.getElementById('id_pickup_date');
  if (dateInput) {
    var tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    var yyyy = tomorrow.getFullYear();
    var mm   = String(tomorrow.getMonth() + 1).padStart(2, '0');
    var dd   = String(tomorrow.getDate()).padStart(2, '0');
    dateInput.min = yyyy + '-' + mm + '-' + dd;
  }

  // ---- State ----
  const cart = new Map(); // vegetable_id (string) -> { id, title, code, price, weight_kg }

  // ---- DOM Refs ----
  const drawer        = document.getElementById('orderDrawer');
  const layout        = document.querySelector('.catalog-layout');
  const drawerItems   = document.getElementById('drawerItems');
  const totalWeightEl = document.getElementById('totalWeight');
  const grandTotalEl  = document.getElementById('grandTotal');
  const totalWeightEl2 = document.getElementById('totalWeight2');
  const grandTotalEl2  = document.getElementById('grandTotal2');
  const emptyMsg      = document.getElementById('emptyOrderMsg');
  const cartDataInput = document.getElementById('cartDataInput');
  const orderForm     = document.getElementById('orderForm');
  const drawerBadge   = document.getElementById('drawerBadge');
  const mobileCartBar = document.getElementById('mobileCartBar');
  const mcbCount      = document.getElementById('mcbCount');
  const mcbTotal      = document.getElementById('mcbTotal');
  const mcbBtn        = document.getElementById('mcbBtn');
  const continueBtn   = document.getElementById('continueBtn');
  const backBtn       = document.getElementById('backBtn');
  const step1Panel    = document.getElementById('step1Panel');
  const step2Panel    = document.getElementById('step2Panel');
  const stepPill1     = document.getElementById('stepPill1');
  const stepPill2     = document.getElementById('stepPill2');

  // ---- Step state ----
  var currentStep = 1;

  function showDrawer() {
    drawer.style.display = '';
    if (layout) layout.classList.remove('drawer-hidden');
  }

  function hideDrawer() {
    drawer.style.display = 'none';
    if (layout) layout.classList.add('drawer-hidden');
  }

  function goToStep(n) {
    currentStep = n;
    if (n === 1) {
      step1Panel.style.display = '';
      step2Panel.style.display = 'none';
      stepPill1.classList.add('active');
      stepPill2.classList.remove('active');
    } else {
      step1Panel.style.display = 'none';
      step2Panel.style.display = '';
      stepPill1.classList.remove('active');
      stepPill2.classList.add('active');
      // Sync compact summary on step 2
      if (totalWeightEl2) totalWeightEl2.textContent = totalWeightEl.textContent;
      if (grandTotalEl2)  grandTotalEl2.textContent  = grandTotalEl.textContent;
      // Scroll drawer to top
      drawer.scrollTop = 0;
    }
  }

  if (continueBtn) {
    continueBtn.addEventListener('click', function () { goToStep(2); });
  }

  if (backBtn) {
    backBtn.addEventListener('click', function () { goToStep(1); });
  }

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

  // ---- Weight input wiring ----
  document.querySelectorAll('.product-card').forEach(function (card) {
    var input      = card.querySelector('.weight-input');
    var incBtn     = card.querySelector('.increment');
    var decBtn     = card.querySelector('.decrement');
    var subtotalEl = card.querySelector('.subtotal-value');

    if (!input) return;

    var vegId    = card.dataset.id;
    var price    = parseFloat(card.dataset.price) || 0;
    var title    = card.dataset.title;
    var code     = card.dataset.code;
    var stepSize = 1;

    function clamp(val) {
      var n = parseFloat(val);
      return isNaN(n) || n < 0 ? 0 : Math.round(n * 100) / 100;
    }

    // Called while typing — update subtotal live without rewriting the input value
    function updateLive() {
      var kg = clamp(input.value);
      var lineTotal = kg * price;
      subtotalEl.textContent = '₹' + lineTotal.toFixed(2);

      if (kg > 0) {
        cart.set(vegId, { id: parseInt(vegId), title: title, code: code, price: price, weight_kg: kg });
      } else {
        cart.delete(vegId);
      }
      renderDrawer();
    }

    // Called on blur / step buttons — normalise the displayed value
    function updateCommit() {
      var kg = clamp(input.value);
      input.value = kg;
      updateLive();
    }

    input.addEventListener('input', updateLive);
    input.addEventListener('change', updateCommit);

    if (incBtn) {
      incBtn.addEventListener('click', function () {
        input.value = (clamp(input.value) + stepSize).toFixed(1);
        updateCommit();
      });
    }

    if (decBtn) {
      decBtn.addEventListener('click', function () {
        var newVal = clamp(input.value) - stepSize;
        input.value = newVal < 0 ? 0 : newVal.toFixed(1);
        updateCommit();
      });
    }
  });

  // ---- Render Order Drawer ----
  function renderDrawer() {
    var totalWeight = 0;
    var grandTotal  = 0;
    var itemCount   = cart.size;

    // Build drawer item list
    var html = '';
    cart.forEach(function (item) {
      var lineTotal = item.weight_kg * item.price;
      totalWeight  += item.weight_kg;
      grandTotal   += lineTotal;

      html += '<div class="drawer-item">' +
        '<div>' +
          '<div class="drawer-item-name">' + escapeHtml(item.title) + '</div>' +
          '<div class="drawer-item-detail">' + escapeHtml(item.code) + ' &nbsp;·&nbsp; ' + item.weight_kg.toFixed(2) + ' kg @ ₹' + item.price.toFixed(2) + '/kg</div>' +
        '</div>' +
        '<div class="drawer-item-total">₹' + lineTotal.toFixed(2) + '</div>' +
      '</div>';
    });

    drawerItems.innerHTML = html || '<p class="drawer-empty">No items selected yet.</p>';
    totalWeightEl.textContent = totalWeight.toFixed(2) + ' kg';
    grandTotalEl.textContent  = '₹' + grandTotal.toFixed(2);

    // Drawer badge
    if (drawerBadge) drawerBadge.textContent = itemCount;

    // Show/hide drawer — reveal when items are added, hide when cart is empty
    if (itemCount > 0) {
      showDrawer();
    } else {
      hideDrawer();
      goToStep(1);
    }

    // Show/hide continue button and empty message
    if (continueBtn) continueBtn.style.display = itemCount > 0 ? '' : 'none';
    if (emptyMsg)    emptyMsg.style.display     = itemCount > 0 ? 'none' : '';

    // Keep compact step-2 summary in sync while user is on step 2
    if (currentStep === 2) {
      if (totalWeightEl2) totalWeightEl2.textContent = totalWeightEl.textContent;
      if (grandTotalEl2)  grandTotalEl2.textContent  = grandTotalEl.textContent;
    }

    // ---- Mobile cart bar (≤900px only) ----
    var isMobile = window.matchMedia('(max-width: 900px)').matches;
    if (mobileCartBar) {
      if (isMobile && itemCount > 0) {
        mobileCartBar.style.display = '';
        document.body.classList.add('has-cart-bar');
        if (mcbCount) mcbCount.textContent = itemCount + (itemCount === 1 ? ' item' : ' items');
        if (mcbTotal) mcbTotal.textContent = '₹' + grandTotal.toFixed(2);
      } else {
        mobileCartBar.style.display = 'none';
        document.body.classList.remove('has-cart-bar');
      }
    }
  }

  // ---- Mobile cart bar button — scroll to order drawer ----
  if (mcbBtn) {
    mcbBtn.addEventListener('click', function () {
      var drawerEl = document.getElementById('orderDrawer');
      if (drawerEl) {
        drawerEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  }

  // ---- Form submission — AJAX, no page reload ----
  if (orderForm) {
    orderForm.addEventListener('submit', function (e) {
      e.preventDefault();

      if (cart.size === 0) {
        showFieldError('__all__', 'Please add at least one vegetable to your order before submitting.');
        return;
      }

      // Inject cart JSON
      var payload = [];
      cart.forEach(function (item) {
        payload.push({ id: item.id, weight_kg: item.weight_kg });
      });
      cartDataInput.value = JSON.stringify(payload);

      // Clear previous errors
      clearFormErrors();

      var submitBtn = document.getElementById('submitBtn');
      if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Submitting…'; }

      var formData = new FormData(orderForm);

      fetch(orderForm.action, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        body: formData,
      })
        .then(function (res) {
          return res.json().then(function (data) { return { status: res.status, data: data }; });
        })
        .then(function (result) {
          if (result.data.redirect) {
            window.location.href = result.data.redirect;
            return;
          }
          // Show field-level errors
          if (result.data.errors) {
            Object.keys(result.data.errors).forEach(function (field) {
              showFieldError(field, result.data.errors[field].join(' '));
            });
          }
          if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = '✅ Place Pre-Order'; }
        })
        .catch(function () {
          showFieldError('__all__', 'A network error occurred. Please try again.');
          if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = '✅ Place Pre-Order'; }
        });
    });
  }

  function clearFormErrors() {
    orderForm.querySelectorAll('.field-error').forEach(function (el) { el.remove(); });
    orderForm.querySelectorAll('.field-group').forEach(function (el) { el.classList.remove('has-error'); });
    var existing = orderForm.querySelector('.form-error-banner');
    if (existing) existing.remove();
  }

  function showFieldError(field, msg) {
    if (field === '__all__') {
      // Show as a banner above the submit button
      var existing = orderForm.querySelector('.form-error-banner');
      if (existing) { existing.textContent = msg; return; }
      var banner = document.createElement('p');
      banner.className = 'form-error-banner field-error';
      banner.textContent = msg;
      var submitBtn = document.getElementById('submitBtn');
      orderForm.insertBefore(banner, submitBtn);
      return;
    }
    // Map Django field name -> input id (e.g. buyer_name -> id_buyer_name)
    var inputEl = orderForm.querySelector('[name="' + field + '"]');
    if (!inputEl) return;
    var group = inputEl.closest('.field-group');
    if (group) group.classList.add('has-error');
    var errEl = document.createElement('span');
    errEl.className = 'field-error';
    errEl.textContent = msg;
    inputEl.insertAdjacentElement('afterend', errEl);
  }

  // Initial render
  renderDrawer();

  // ---- Utility ----
  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

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

      document.addEventListener('mousemove', function (e) {
        if (!dragging) return;
        // Visual feedback: update cursor on whichever zone started the drag
        dragZones.forEach(function (z) {
          if (z.style.cursor === 'grabbing') return;
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
