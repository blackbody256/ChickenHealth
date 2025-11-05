// landing.js — small interaction handlers for the Tailwind landing page

document.addEventListener('DOMContentLoaded', function () {
  // Mobile menu toggle
  const mobileBtn = document.getElementById('mobileBtn');
  const mobileMenu = document.getElementById('mobileMenu');
  if (mobileBtn && mobileMenu) {
    mobileBtn.addEventListener('click', () => {
      mobileMenu.classList.toggle('hidden');
    });
  }

  // AOS init (if AOS loaded)
  if (typeof AOS !== 'undefined') {
    AOS.init({
      duration: 700,
      once: true,
    });
  }

  // Smooth scroll for internal links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const href = this.getAttribute('href');
      if (href.length > 1) {
        e.preventDefault();
        const el = document.querySelector(href);
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // Buttons styled with .btn-primary -> add a small ripple or focus
  document.querySelectorAll('.btn-primary').forEach(btn => {
    btn.addEventListener('click', () => {
      // small visual feedback
      btn.classList.add('opacity-80');
      setTimeout(() => btn.classList.remove('opacity-80'), 150);
    });
  });
});
