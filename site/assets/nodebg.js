/* gemeinwert — drifting node-network background, whole-page.
 * Auto-creates a fixed-position canvas covering the viewport if one
 * isn't already in the DOM. ~25 small bone nodes drift slowly; when two
 * come within range, a thin line connects them. The cursor acts as a
 * gold node so the network responds to motion across the entire page.
 * Respects prefers-reduced-motion. */
(function () {
  'use strict';

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  // Auto-create the canvas if not present
  let c = document.getElementById('node-bg');
  if (!c) {
    c = document.createElement('canvas');
    c.id = 'node-bg';
    c.className = 'page-bg';
    c.setAttribute('aria-hidden', 'true');
    // Inline-style fallback in case site.css hasn't loaded the .page-bg rule
    c.style.cssText = [
      'position:fixed', 'inset:0', 'width:100vw', 'height:100vh',
      'z-index:-1', 'pointer-events:none', 'opacity:0.55',
    ].join(';');
    document.body.appendChild(c);
  }

  const ctx = c.getContext('2d');
  let W = 0, H = 0, dpr = window.devicePixelRatio || 1;

  function resize() {
    W = window.innerWidth;
    H = window.innerHeight;
    c.width = W * dpr;
    c.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  resize();
  window.addEventListener('resize', resize);

  // Spawn nodes — count scales with viewport
  const TARGET_DENSITY = 32000; // one node per this many px²
  const N = Math.max(18, Math.min(48, Math.floor((W * H) / TARGET_DENSITY)));
  const nodes = [];
  for (let i = 0; i < N; i++) {
    nodes.push({
      x: Math.random() * W,
      y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.16,
      vy: (Math.random() - 0.5) * 0.16,
      r: Math.random() < 0.08 ? 2.6 : 1.8,
      gold: Math.random() < 0.05, // rare gold accent
    });
  }

  // Cursor follower — listen at window level since canvas is fixed-viewport
  let mx = -9999, my = -9999;
  window.addEventListener('mousemove', e => {
    mx = e.clientX;
    my = e.clientY;
  });
  window.addEventListener('mouseleave', () => { mx = -9999; my = -9999; });
  window.addEventListener('blur', () => { mx = -9999; my = -9999; });

  const LINK = 140;   // link distance threshold (node-to-node)
  const LINK_M = 200; // link distance threshold (mouse-to-node)

  function tick() {
    ctx.clearRect(0, 0, W, H);

    // update node positions
    for (const n of nodes) {
      n.x += n.vx;
      n.y += n.vy;
      if (n.x < -10) n.x = W + 10;
      if (n.x > W + 10) n.x = -10;
      if (n.y < -10) n.y = H + 10;
      if (n.y > H + 10) n.y = -10;
    }

    // links between nodes (draw first so dots paint on top)
    ctx.lineWidth = 1;
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i], b = nodes[j];
        const dx = a.x - b.x, dy = a.y - b.y;
        const d2 = dx * dx + dy * dy;
        if (d2 < LINK * LINK) {
          const d = Math.sqrt(d2);
          const t = 1 - d / LINK;
          ctx.strokeStyle = 'rgba(63, 77, 91, ' + (0.50 * t).toFixed(3) + ')';
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      }
    }

    // links between mouse and nearby nodes (gold)
    if (mx > -1000) {
      for (const n of nodes) {
        const dx = n.x - mx, dy = n.y - my;
        const d2 = dx * dx + dy * dy;
        if (d2 < LINK_M * LINK_M) {
          const d = Math.sqrt(d2);
          const t = 1 - d / LINK_M;
          ctx.strokeStyle = 'rgba(244, 196, 48, ' + (0.34 * t).toFixed(3) + ')';
          ctx.beginPath();
          ctx.moveTo(n.x, n.y);
          ctx.lineTo(mx, my);
          ctx.stroke();
        }
      }
    }

    // draw nodes
    for (const n of nodes) {
      ctx.fillStyle = n.gold ? '#f4c430' : '#5a6878';
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
      ctx.fill();
    }

    // cursor node (gold)
    if (mx > -1000) {
      ctx.fillStyle = '#f4c430';
      ctx.beginPath();
      ctx.arc(mx, my, 3, 0, Math.PI * 2);
      ctx.fill();
    }

    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})();
