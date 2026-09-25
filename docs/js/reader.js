(function () {
  'use strict';

  var BOOK = window.BOOK;
  var bookEl = document.getElementById('book');
  var tocTree = document.getElementById('toc-tree');
  var root = document.documentElement;
  var VIEWS = ['original', 'parallel', 'modern'];
  var NARROW = window.matchMedia('(max-width: 1000px)');

  if (!BOOK) {
    bookEl.innerHTML = '<p class="loading">The book data could not be loaded.</p>';
    return;
  }

  // ------------------------------------------------------------ render text

  function renderBook() {
    var out = [];
    BOOK.blocks.forEach(function (b, i) {
      var light = b.l !== undefined ? b.l : b.o;
      var same = b.l === undefined;
      var cls = b.c ? ' ' + b.c : '';

      if (b.k === 'h') {
        var tag = 'h' + Math.min(b.lv, 6);
        out.push(
          '<div class="row row--h row--h' + b.lv + (same ? ' row--same' : '') + '" id="' + b.id + '">' +
            '<' + tag + ' class="o">' + b.o + '</' + tag + '>' +
            '<' + tag + ' class="l">' + light + '</' + tag + '>' +
          '</div>'
        );
        return;
      }
      if (b.k === 'hr') {
        out.push('<hr class="rule">');
        return;
      }
      var wrap = (b.k === 'p' || b.k === 'fn') ? 'p' : 'div';
      out.push(
        '<div class="row' + (same ? ' row--same' : '') + '">' +
          '<' + wrap + ' class="o' + cls + '">' + b.o + '</' + wrap + '>' +
          '<' + wrap + ' class="l' + cls + '">' + light + '</' + wrap + '>' +
        '</div>'
      );
    });
    out.push(
      '<footer class="colophon">' +
        '<p>Original text: <em>The Book of Common Worship</em>, published by authority of the General Assembly of the ' +
        'Presbyterian Church in the United States of America (Philadelphia: Presbyterian Board of Publication and ' +
        'Sabbath-School Work, 1906), transcribed from the ' +
        '<a href="https://archive.org/details/bookofcommonwor00pres" target="_blank" rel="noopener">Internet Archive scan</a>. ' +
        'The lightly modernized text is an editorial rendering for this site. Holy Scripture is given unchanged in the ' +
        'words of the King James Version, and the Lord’s Prayer, the Apostles’ Creed, the Gloria Patri, the ' +
        'ancient hymns and canticles, and the marriage vows are likewise left as printed.</p>' +
      '</footer>'
    );
    bookEl.innerHTML = out.join('');
  }

  // ------------------------------------------------------------ table of contents

  function buildTree() {
    var top = [];
    var stack = [];
    BOOK.blocks.forEach(function (b) {
      if (b.k !== 'h' || b.lv < 2 || b.lv > 4) return;
      var node = { id: b.id, lv: b.lv, o: b.o, l: b.l !== undefined ? b.l : b.o, kids: [] };
      while (stack.length && stack[stack.length - 1].lv >= b.lv) stack.pop();
      if (stack.length) stack[stack.length - 1].kids.push(node); else top.push(node);
      stack.push(node);
    });
    return top;
  }

  function stripTags(s) { return s.replace(/<[^>]+>/g, ''); }

  function renderToc(nodes) {
    function item(n) {
      var hasKids = n.kids.length > 0;
      return (
        '<li class="toc__item toc__item--' + n.lv + '" data-id="' + n.id + '">' +
          '<div class="toc__row">' +
            (hasKids
              ? '<button type="button" class="toc__twisty" aria-expanded="false" aria-label="Show subsections"></button>'
              : '<span class="toc__twisty toc__twisty--none"></span>') +
            '<a href="#' + n.id + '" data-target="' + n.id + '">' +
              '<span class="toc-o">' + stripTags(n.o) + '</span>' +
              '<span class="toc-l">' + stripTags(n.l) + '</span>' +
            '</a>' +
          '</div>' +
          (hasKids ? '<ol class="toc__kids">' + n.kids.map(item).join('') + '</ol>' : '') +
        '</li>'
      );
    }
    tocTree.innerHTML = '<ol class="toc__list">' + nodes.map(item).join('') + '</ol>';
  }

  // Accordion: expanding an item collapses its siblings (and their descendants).
  function setExpanded(li, open) {
    li.classList.toggle('is-open', open);
    var t = li.querySelector(':scope > .toc__row > .toc__twisty');
    if (t && t.tagName === 'BUTTON') t.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (!open) li.querySelectorAll('.toc__item.is-open').forEach(function (d) { setExpanded(d, false); });
  }

  function expandOnly(li) {
    // open li and all its ancestors; close every sibling branch along the way
    var chain = [];
    for (var n = li; n && n.classList && n.classList.contains('toc__item'); n = n.parentElement.closest('.toc__item')) chain.push(n);
    chain.forEach(function (node) {
      Array.prototype.forEach.call(node.parentElement.children, function (sib) {
        if (sib !== node && sib.classList.contains('is-open')) setExpanded(sib, false);
      });
      if (node.querySelector(':scope > .toc__kids')) setExpanded(node, true);
    });
  }

  function setupToc() {
    tocTree.addEventListener('click', function (e) {
      var twisty = e.target.closest('button.toc__twisty');
      var li = e.target.closest('.toc__item');
      if (!li) return;
      if (twisty) {
        if (li.classList.contains('is-open')) setExpanded(li, false); else expandOnly(li);
        return;
      }
      if (e.target.closest('a')) {
        expandOnly(li);
        markActive(li.dataset.id);
        if (NARROW.matches) setTocVisible(false);
      }
    });

    document.getElementById('toc-toggle').addEventListener('click', function () {
      setTocVisible(!tocVisible());
    });
    document.getElementById('toc-close').addEventListener('click', function () { setTocVisible(false); });
    document.getElementById('toc-backdrop').addEventListener('click', function () { setTocVisible(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && NARROW.matches && tocVisible()) setTocVisible(false);
    });
    NARROW.addEventListener('change', syncTocState);
    syncTocState();
  }

  // On wide screens the contents panel is shown unless the reader has hidden it (remembered).
  // On narrow screens it is an overlay drawer, closed until opened.
  function tocVisible() {
    return NARROW.matches ? root.classList.contains('toc-open') : !root.classList.contains('toc-hidden');
  }
  function setTocVisible(show) {
    if (NARROW.matches) {
      root.classList.toggle('toc-open', show);
    } else {
      root.classList.toggle('toc-hidden', !show);
      try { localStorage.setItem('bcw-toc', show ? 'shown' : 'hidden'); } catch (e) {}
    }
    document.getElementById('toc-toggle').setAttribute('aria-expanded', show ? 'true' : 'false');
  }
  function syncTocState() {
    root.classList.remove('toc-open');
    document.getElementById('toc-toggle').setAttribute('aria-expanded', tocVisible() ? 'true' : 'false');
  }

  // ------------------------------------------------------------ active section tracking

  var activeId = null;
  var tocHover = false;

  function markActive(id) {
    if (id === activeId) return;
    activeId = id;
    tocTree.querySelectorAll('a.is-active').forEach(function (a) { a.classList.remove('is-active'); });
    var a = tocTree.querySelector('a[data-target="' + id + '"]');
    if (!a) return;
    a.classList.add('is-active');
    if (!tocHover) {
      expandOnly(a.closest('.toc__item'));
      var box = tocTree.closest('.toc');
      var r = a.getBoundingClientRect(), br = box.getBoundingClientRect();
      if (r.top < br.top + 40 || r.bottom > br.bottom - 20) {
        box.scrollTop += r.top - br.top - br.height / 3;
      }
    }
  }

  function setupScrollSpy() {
    var heads = Array.prototype.slice.call(document.querySelectorAll('.row--h2, .row--h3, .row--h4'));
    if (!heads.length) return;
    var toc = document.getElementById('toc');
    toc.addEventListener('mouseenter', function () { tocHover = true; });
    toc.addEventListener('mouseleave', function () { tocHover = false; });

    var ticking = false;
    function update() {
      ticking = false;
      var line = barHeight() + 24;
      var current = null;
      // binary search for the last heading above the line
      var lo = 0, hi = heads.length - 1;
      while (lo <= hi) {
        var mid = (lo + hi) >> 1;
        if (heads[mid].getBoundingClientRect().top <= line) { current = heads[mid]; lo = mid + 1; } else hi = mid - 1;
      }
      if (current) markActive(current.id);
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    update();
  }

  function barHeight() {
    return document.getElementById('bar').getBoundingClientRect().height;
  }

  // ------------------------------------------------------------ view toggle

  function initialView() {
    var p = new URLSearchParams(location.search).get('view');
    if (VIEWS.indexOf(p) >= 0) return p;
    try {
      var s = localStorage.getItem('bcw-view');
      if (VIEWS.indexOf(s) >= 0) return s;
    } catch (e) {}
    return 'parallel';
  }

  function anchorRow() {
    var line = barHeight();
    var rows = bookEl.children;
    // binary search for first row whose bottom is below the bar
    var lo = 0, hi = rows.length - 1, found = null;
    while (lo <= hi) {
      var mid = (lo + hi) >> 1;
      if (rows[mid].getBoundingClientRect().bottom > line) { found = rows[mid]; hi = mid - 1; } else lo = mid + 1;
    }
    return found;
  }

  function applyView(view, keepPlace) {
    var anchor = keepPlace ? anchorRow() : null;
    var before = anchor ? anchor.getBoundingClientRect().top : 0;

    root.setAttribute('data-view', view);
    document.querySelectorAll('#view-toggle button').forEach(function (b) {
      b.setAttribute('aria-pressed', b.dataset.view === view ? 'true' : 'false');
    });
    try { localStorage.setItem('bcw-view', view); } catch (e) {}
    var url = new URL(location.href);
    url.searchParams.set('view', view);
    history.replaceState(null, '', url);

    if (anchor) window.scrollBy(0, anchor.getBoundingClientRect().top - before);
  }

  function setupViewToggle() {
    applyView(initialView(), false);
    document.getElementById('view-toggle').addEventListener('click', function (e) {
      var b = e.target.closest('button[data-view]');
      if (b) applyView(b.dataset.view, true);
    });
  }

  // ------------------------------------------------------------ start

  function syncBarHeight() {
    var h = barHeight();
    root.style.setProperty('--bar-h', h + 'px');
    root.style.scrollPaddingTop = (h + 16) + 'px';
  }
  syncBarHeight();
  window.addEventListener('resize', syncBarHeight);

  renderBook();
  renderToc(buildTree());
  setupViewToggle();
  setupToc();

  if (location.hash) {
    var target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (target) target.scrollIntoView({ block: 'start' });
  }
  setupScrollSpy();
})();
