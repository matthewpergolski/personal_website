(function () {
  try {
    const saved = localStorage.getItem("theme_v2");
    const theme = saved || "dark";
    document.documentElement.setAttribute("data-theme", theme);
    document.addEventListener("DOMContentLoaded", function () {
      const btn = document.getElementById("theme-toggle");
      if (!btn) return;
      btn.addEventListener("click", function () {
        const cur =
          document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", cur);
        localStorage.setItem("theme_v2", cur);
      });
    });
  } catch (e) {}
})();
