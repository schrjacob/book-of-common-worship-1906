(function () {
  function current() {
    return document.documentElement.getAttribute('data-theme') || 'light';
  }
  function apply(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
      btn.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
      btn.textContent = theme === 'dark' ? 'Light mode' : 'Dark mode';
    });
  }
  document.addEventListener('DOMContentLoaded', function () {
    apply(current());
    document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var next = current() === 'dark' ? 'light' : 'dark';
        try { localStorage.setItem('bcw-theme', next); } catch (e) {}
        apply(next);
      });
    });
  });
})();
