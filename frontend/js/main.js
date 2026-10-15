import { api } from './services/api.js';

document.addEventListener('DOMContentLoaded', () => {
  initDbStatusBadge();
  highlightActiveNav();
});

async function initDbStatusBadge() {
  const badge = document.getElementById('db-status-badge');
  if (!badge) return;

  try {
    const health = await api.getDatabaseHealth();
    if (health.status === 'connected') {
      badge.className = 'status-pill connected';
      badge.innerHTML = '<span class="status-dot"></span> Atlas: Connected';
      badge.title = `Connected to ${health.details?.database || 'MongoDB Atlas'}`;
    } else {
      badge.className = 'status-pill disconnected';
      badge.innerHTML = '<span class="status-dot"></span> Atlas: Disconnected';
      badge.title = health.details?.message || 'Database connection offline';
    }
  } catch (err) {
    badge.className = 'status-pill disconnected';
    badge.innerHTML = '<span class="status-dot"></span> Backend Offline';
    badge.title = 'Cannot reach backend server at http://localhost:8000';
  }
}

function highlightActiveNav() {
  const currentPath = window.location.pathname.toLowerCase();
  const links = document.querySelectorAll('.nav-link');
  links.forEach(link => {
    const href = link.getAttribute('href')?.toLowerCase();
    if (href && (currentPath.endsWith(href) || (currentPath === '/' && href.includes('index')))) {
      link.classList.add('active');
    }
  });
}
