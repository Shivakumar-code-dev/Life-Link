// ──────────────────────────────────────────────
// BLOOD DONATION PORTAL — FRONTEND SCRIPTS
// ──────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {

  // Auto-dismiss flash messages after 5 seconds
  document.querySelectorAll(".alert").forEach(alert => {
    setTimeout(() => {
      alert.style.transition = "opacity 0.5s";
      alert.style.opacity = "0";
      setTimeout(() => alert.remove(), 500);
    }, 5000);
  });

  // Animate stats counters on landing page
  const counters = document.querySelectorAll("[data-count]");
  if (counters.length) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          animateCounter(e.target);
          observer.unobserve(e.target);
        }
      });
    }, { threshold: 0.5 });
    counters.forEach(el => observer.observe(el));
  }

  function animateCounter(el) {
    const target = parseInt(el.getAttribute("data-count"), 10);
    const duration = 1500;
    const start = performance.now();
    function update(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(target * eased).toLocaleString();
      if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
  }

  // Dashboard tab switching
  const tabLinks = document.querySelectorAll("[data-tab]");
  const tabPanels = document.querySelectorAll("[data-panel]");
  if (tabLinks.length) {
    tabLinks.forEach(link => {
      link.addEventListener("click", e => {
        e.preventDefault();
        const target = link.getAttribute("data-tab");
        tabLinks.forEach(l => l.classList.remove("active"));
        tabPanels.forEach(p => p.classList.add("hidden"));
        link.classList.add("active");
        const panel = document.querySelector(`[data-panel="${target}"]`);
        if (panel) panel.classList.remove("hidden");
      });
    });
    // Show first tab by default
    if (tabLinks[0]) tabLinks[0].click();
  }

  // Password strength indicator
  const passwordInput = document.getElementById("password");
  const strengthBar   = document.getElementById("strength-bar");
  if (passwordInput && strengthBar) {
    passwordInput.addEventListener("input", () => {
      const val = passwordInput.value;
      let score = 0;
      if (val.length >= 8) score++;
      if (/[A-Z]/.test(val)) score++;
      if (/[0-9]/.test(val)) score++;
      if (/[^A-Za-z0-9]/.test(val)) score++;
      const colors = ["", "#E74C3C", "#F39C12", "#3498DB", "#27AE60"];
      const widths  = ["0%", "25%", "50%", "75%", "100%"];
      strengthBar.style.width = widths[score];
      strengthBar.style.background = colors[score];
    });
  }

  // Confirm password validation
  const form = document.getElementById("register-form");
  if (form) {
    form.addEventListener("submit", e => {
      const p1 = form.querySelector("#password");
      const p2 = form.querySelector("#confirm_password");
      if (p1 && p2 && p1.value !== p2.value) {
        e.preventDefault();
        showToast("Passwords do not match.", "danger");
      }
    });
  }

  // Delete confirmation
  document.querySelectorAll("[data-confirm]").forEach(el => {
    el.addEventListener("click", e => {
      if (!confirm(el.getAttribute("data-confirm"))) e.preventDefault();
    });
  });

  // Search form — live filter on table rows
  const searchInput = document.getElementById("live-search");
  if (searchInput) {
    searchInput.addEventListener("input", () => {
      const val = searchInput.value.toLowerCase();
      document.querySelectorAll(".searchable-row").forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(val) ? "" : "none";
      });
    });
  }

  // Toast helper
  function showToast(message, type = "info") {
    const div = document.createElement("div");
    div.className = `alert alert-${type}`;
    div.textContent = message;
    const wrapper = document.querySelector(".alerts-wrapper");
    if (wrapper) {
      wrapper.prepend(div);
      setTimeout(() => div.remove(), 5000);
    }
  }

  // Mobile nav toggle
  const menuToggle = document.getElementById("menu-toggle");
  const navLinks   = document.getElementById("nav-links");
  if (menuToggle && navLinks) {
    menuToggle.addEventListener("click", () => {
      navLinks.classList.toggle("open");
    });
  }

});
