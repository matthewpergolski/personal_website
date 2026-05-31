(function () {
  document.addEventListener("mousemove", function (e) {
    try {
      document.documentElement.style.setProperty("--glow-x", e.clientX + "px");
      document.documentElement.style.setProperty("--glow-y", e.clientY + "px");
    } catch (_) {}
  });
  // Mobile nav toggle + close on link/escape/outside; first-time wiggle
  document.addEventListener("DOMContentLoaded", function () {
    try {
      var seen = localStorage.getItem("menu_hint_seen") === "1";
      var btn = document.getElementById("nav-toggle");
      if (btn && !seen && window.innerWidth <= 768) {
        btn.classList.add("nudge");
        setTimeout(function () {
          try {
            btn.classList.remove("nudge");
            localStorage.setItem("menu_hint_seen", "1");
          } catch (_) {}
        }, 1600);
      }
    } catch (_) {}
  });

  document.addEventListener("click", function (e) {
    var t = e.target;
    var nav = document.querySelector(".nav");
    var links = document.getElementById("nav-links");
    if (t && t.id === "nav-close") {
      if (nav) {
        nav.classList.remove("open");
        document.body.classList.remove("nav-open");
        try {
          var b = document.getElementById("nav-toggle");
          if (b) b.setAttribute("aria-expanded", "false");
        } catch (_) {}
      }
      return;
    }
    if (t && t.id === "nav-toggle") {
      if (nav) {
        var open = nav.classList.toggle("open");
        document.body.classList.toggle("nav-open", open);
        try {
          var btn = document.getElementById("nav-toggle");
          if (btn) btn.setAttribute("aria-expanded", open ? "true" : "false");
        } catch (_) {}
      }
      return;
    }
    if (nav && nav.classList.contains("open")) {
      var withinLinks = links && (links.contains(t) || (t.closest && t.closest("#nav-links")));
      var isToggle = t.id === "nav-toggle";
      if (!withinLinks && !isToggle) {
        nav.classList.remove("open");
        document.body.classList.remove("nav-open");
        try {
          var btn = document.getElementById("nav-toggle");
          if (btn) btn.setAttribute("aria-expanded", "false");
        } catch (_) {}
      }
    }
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      var nav = document.querySelector(".nav");
      if (nav && nav.classList.contains("open")) {
        nav.classList.remove("open");
        document.body.classList.remove("nav-open");
      }
    }
  });
  // Highlight active tab in the bottom tab bar
  document.addEventListener("DOMContentLoaded", function () {
    try {
      var p = location.pathname || "/";
      var id = p.startsWith("/projects")
        ? "tab-projects"
        : p.startsWith("/about")
          ? "tab-about"
          : p.startsWith("/resume")
            ? "tab-resume"
            : p.startsWith("/chat")
              ? "tab-chat"
              : p.startsWith("/contact")
                ? "tab-contact"
                : "tab-home";
      var el = document.getElementById(id);
      if (el) el.classList.add("active");
    } catch (_) {}
  });

  // Basic edge-swipe gestures (open from right edge, close by swiping right on panel)
  (function () {
    var startX = 0,
      startY = 0,
      trackingOpen = false,
      trackingClose = false;
    document.addEventListener(
      "touchstart",
      function (e) {
        try {
          var t = e.touches && e.touches[0];
          if (!t) return;
          startX = t.clientX;
          startY = t.clientY;
          var nav = document.querySelector(".nav");
          var links = document.getElementById("nav-links");
          var edge = 24;
          if (nav && !nav.classList.contains("open") && startX > window.innerWidth - edge)
            trackingOpen = true;
          else if (nav && nav.classList.contains("open") && links && links.contains(e.target))
            trackingClose = true;
        } catch (_) {}
      },
      { passive: true },
    );
    document.addEventListener(
      "touchmove",
      function (e) {
        try {
          var t = e.touches && e.touches[0];
          if (!t) return;
          var dx = t.clientX - startX;
          var dy = t.clientY - startY;
          if (Math.abs(dy) > 40) {
            trackingOpen = false;
            trackingClose = false;
            return;
          }
          var nav = document.querySelector(".nav");
          if (trackingOpen && dx < -50) {
            if (nav) {
              nav.classList.add("open");
              document.body.classList.add("nav-open");
              try {
                var b = document.getElementById("nav-toggle");
                if (b) b.setAttribute("aria-expanded", "true");
              } catch (_) {}
            }
            trackingOpen = false;
          }
          if (trackingClose && dx > 50) {
            if (nav) {
              nav.classList.remove("open");
              document.body.classList.remove("nav-open");
              try {
                var b = document.getElementById("nav-toggle");
                if (b) b.setAttribute("aria-expanded", "false");
              } catch (_) {}
            }
            trackingClose = false;
          }
        } catch (_) {}
      },
      { passive: true },
    );
    document.addEventListener(
      "touchend",
      function () {
        trackingOpen = false;
        trackingClose = false;
      },
      { passive: true },
    );
  })();
  // Starfield: layered parallax stars drifting across the viewport
  function initBelt() {
    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    var c = document.getElementById("asteroid-belt");
    if (!c) return;
    var ctx = c.getContext("2d");
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    function resize() {
      // Ensure canvas covers full viewport regardless of parent layout
      c.style.width = "100vw";
      c.style.height = "100vh";
      c.width = Math.floor((window.innerWidth || document.documentElement.clientWidth) * dpr);
      c.height = Math.floor((window.innerHeight || document.documentElement.clientHeight) * dpr);
    }
    resize();
    window.addEventListener("resize", resize);
    var W = () => c.width,
      H = () => c.height; // in device pixels
    var textColor =
      getComputedStyle(document.documentElement).getPropertyValue("--text-color").trim() ||
      "#e2e8f0";
    var col = "rgba(255,255,255,0.6)";
    try {
      // derive color from CSS var (approx)
      var tmp = document.createElement("canvas");
      var tctx = tmp.getContext("2d");
      tctx.fillStyle = textColor; // may be rgb(...)
      col = tctx.fillStyle.replace("rgb", "rgba").replace(")", " ,0.55)");
    } catch (_) {}
    function makeLayer(count, speed, sizeMin, sizeMax) {
      var arr = [];
      for (var i = 0; i < count; i++) {
        arr.push({
          x: Math.random() * W(),
          y: Math.random() * H(),
          s: (sizeMin + Math.random() * (sizeMax - sizeMin)) * dpr,
          v: speed * (0.6 + Math.random() * 0.8),
          tw: Math.random() * Math.PI * 2,
          tws: 0.015 + Math.random() * 0.03,
        });
      }
      return arr;
    }
    var baseCount = Math.min(c.clientWidth, c.clientHeight) > 900 ? 140 : 90;
    var layer1 = makeLayer(Math.floor(baseCount * 0.5), 0.02, 0.5, 1.2);
    var layer2 = makeLayer(Math.floor(baseCount * 0.35), 0.04, 0.8, 1.8);
    var layer3 = makeLayer(Math.floor(baseCount * 0.15), 0.07, 1.2, 2.4);
    var layers = [layer1, layer2, layer3];
    var lastT = 0,
      paused = false;
    document.addEventListener("visibilitychange", () => {
      paused = document.hidden;
    });
    function tick(t) {
      if (paused) {
        requestAnimationFrame(tick);
        return;
      }
      var dt = Math.min(32, t - lastT || 16);
      lastT = t;
      ctx.clearRect(0, 0, W(), H());
      for (var li = 0; li < layers.length; li++) {
        var arr = layers[li];
        for (var i = 0; i < arr.length; i++) {
          var p = arr[i];
          p.x += p.v * dt; // drift to the right
          if (p.x > W() + 10) p.x = -10;
          // gentle vertical drift
          p.y += Math.sin(p.tw + t * 0.0003) * 0.02 * dt;
          if (p.y < -10) p.y = H() + 10;
          else if (p.y > H() + 10) p.y = -10;
          p.tw += (p.tws * dt) / 16;
          var alpha = 0.18 + 0.22 * Math.abs(Math.sin(p.tw));
          ctx.fillStyle = col.replace(/\d?\.\d+\)/, " " + alpha.toFixed(2) + ")");
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.s, 0, Math.PI * 2);
          ctx.fill();
        }
      }
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }
  document.addEventListener("DOMContentLoaded", initBelt);
})();
