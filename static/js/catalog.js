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
  const buyerForm     = document.getElementById('buyerFormSection');
  const emptyMsg      = document.getElementById('emptyOrderMsg');
  const cartDataInput = document.getElementById('cartDataInput');
  const orderForm     = document.getElementById('orderForm');
  const drawerBadge   = document.getElementById('drawerBadge');

  function showDrawer() {
    drawer.style.display = '';
    if (layout) layout.classList.remove('drawer-hidden');
  }

  function hideDrawer() {
    drawer.style.display = 'none';
    if (layout) layout.classList.add('drawer-hidden');
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
    var stepSize = 0.5;

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
    }

    // Show/hide buyer form
    if (itemCount > 0) {
      buyerForm.style.display = '';
      emptyMsg.style.display  = 'none';
    } else {
      buyerForm.style.display = 'none';
      emptyMsg.style.display  = '';
    }
  }

  // ---- Form submission — inject cart JSON ----
  if (orderForm) {
    orderForm.addEventListener('submit', function (e) {
      if (cart.size === 0) {
        e.preventDefault();
        alert('Please add at least one vegetable to your order before submitting.');
        return;
      }

      var payload = [];
      cart.forEach(function (item) {
        payload.push({ id: item.id, weight_kg: item.weight_kg });
      });

      cartDataInput.value = JSON.stringify(payload);
    });
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

    startAuto();
  }());

})();
