/* ============================================================
   ARTISAN COAT — main.js
   ============================================================ */

// ── NAV SCROLL EFFECT ────────────────────────────────────────
const nav = document.querySelector('.nav');
window.addEventListener('scroll', () => {
  if (nav) nav.classList.toggle('scrolled', window.scrollY > 40);
});

// ── MOBILE NAV TOGGLE ────────────────────────────────────────
const toggle = document.querySelector('.nav-toggle');
const mobileNav = document.querySelector('.nav-mobile');
if (toggle && mobileNav) {
  toggle.addEventListener('click', function () {
    const isOpen = mobileNav.style.display === 'block';
    mobileNav.style.display = isOpen ? 'none' : 'block';
    const spans = this.querySelectorAll('span');
    spans[0].style.transform = isOpen ? '' : 'rotate(45deg) translate(5px, 5px)';
    spans[1].style.opacity  = isOpen ? '' : '0';
    spans[2].style.transform = isOpen ? '' : 'rotate(-45deg) translate(5px, -5px)';
  });
}

// ── ACTIVE NAV LINK ──────────────────────────────────────────
const currentPage = window.location.pathname.split('/').pop() || 'index.html';
document.querySelectorAll('.nav-links a, .nav-mobile a').forEach(link => {
  const href = link.getAttribute('href');
  if (href === currentPage || (currentPage === '' && href === 'index.html')) {
    link.classList.add('active');
  }
});


// ── FAQ ACCORDION ────────────────────────────────────────────
document.querySelectorAll('.faq-item').forEach(item => {
  item.querySelector('.faq-question').addEventListener('click', () => {
    const isOpen = item.classList.contains('open');
    document.querySelectorAll('.faq-item.open').forEach(o => o.classList.remove('open'));
    if (!isOpen) item.classList.add('open');
  });
});

// ── GALLERY FILTER ───────────────────────────────────────────
document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const filter = btn.dataset.filter;
    document.querySelectorAll('.gallery-item').forEach(item => {
      item.style.display = (filter === 'all' || item.dataset.cat === filter) ? 'block' : 'none';
    });
  });
});

// ── LIGHTBOX ─────────────────────────────────────────────────
const lightbox = document.querySelector('.lightbox');
const lbImg    = lightbox && lightbox.querySelector('img');
const lbClose  = lightbox && lightbox.querySelector('.lightbox-close');

document.querySelectorAll('.gallery-item').forEach(item => {
  item.addEventListener('click', () => {
    if (!lightbox) return;
    const img = item.querySelector('img');
    if (img && img.src) {
      lbImg.src = img.src;
      lbImg.alt = img.alt || '';
      lightbox.classList.add('open');
      document.body.style.overflow = 'hidden';
    }
  });
});

function closeLightbox() {
  if (!lightbox) return;
  lightbox.classList.remove('open');
  document.body.style.overflow = '';
}
if (lbClose) lbClose.addEventListener('click', closeLightbox);
if (lightbox) lightbox.addEventListener('click', e => { if (e.target === lightbox) closeLightbox(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeLightbox(); });

// ── SMOOTH ANCHOR SCROLL ─────────────────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', e => {
    const target = document.querySelector(anchor.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});
