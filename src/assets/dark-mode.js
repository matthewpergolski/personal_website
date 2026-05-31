(function () {
  const THEME_KEY = "site_theme_v1";
  const APPEARANCE_KEY = "site_appearance_v1";
  const LEGACY_THEME_KEY = "theme_v2";
  const defaults = window.__SITE_THEME_DEFAULTS__ || {};
  const validThemes = ["cosmic", "graphite", "evergreen", "atelier", "sunrise", "spectrum"];
  const validAppearances = ["system", "light", "dark"];
  const media = window.matchMedia("(prefers-color-scheme: dark)");

  function normalize(value, allowed, fallback) {
    return allowed.includes(value) ? value : fallback;
  }

  function readTheme() {
    return normalize(localStorage.getItem(THEME_KEY), validThemes, defaults.theme || "cosmic");
  }

  function readAppearance() {
    const saved = localStorage.getItem(APPEARANCE_KEY);
    if (saved) return normalize(saved, validAppearances, defaults.appearance || "dark");
    const legacy = localStorage.getItem(LEGACY_THEME_KEY);
    if (legacy === "light" || legacy === "dark") return legacy;
    return normalize(defaults.appearance, validAppearances, "dark");
  }

  function resolveAppearance(choice) {
    if (choice === "system") return media.matches ? "dark" : "light";
    return choice;
  }

  function setPressed(selector, predicate) {
    document.querySelectorAll(selector).forEach(function (node) {
      const active = predicate(node);
      node.classList.toggle("active", active);
      node.setAttribute("aria-pressed", active ? "true" : "false");
    });
  }

  function syncControls(theme, appearanceChoice, resolvedAppearance) {
    document.querySelectorAll("[data-theme-select]").forEach(function (select) {
      select.value = theme;
    });
    setPressed("[data-appearance-choice]", function (button) {
      return button.dataset.appearanceChoice === appearanceChoice;
    });
    document.querySelectorAll("[data-appearance-toggle]").forEach(function (button) {
      button.textContent = resolvedAppearance === "dark" ? "☀️" : "🌙";
      button.title = resolvedAppearance === "dark" ? "Switch to light mode" : "Switch to dark mode";
      button.setAttribute(
        "aria-label",
        resolvedAppearance === "dark" ? "Switch to light mode" : "Switch to dark mode",
      );
    });
  }

  function applyTheme(theme, appearanceChoice) {
    const resolvedAppearance = resolveAppearance(appearanceChoice);
    document.documentElement.setAttribute("data-theme", theme);
    document.documentElement.setAttribute("data-appearance", resolvedAppearance);
    document.documentElement.setAttribute("data-appearance-choice", appearanceChoice);
    syncControls(theme, appearanceChoice, resolvedAppearance);
  }

  function saveAndApply(theme, appearanceChoice) {
    localStorage.setItem(THEME_KEY, theme);
    localStorage.setItem(APPEARANCE_KEY, appearanceChoice);
    applyTheme(theme, appearanceChoice);
  }

  function currentTheme() {
    return document.documentElement.getAttribute("data-theme") || readTheme();
  }

  function currentAppearanceChoice() {
    return document.documentElement.getAttribute("data-appearance-choice") || readAppearance();
  }

  try {
    applyTheme(readTheme(), readAppearance());

    document.addEventListener("DOMContentLoaded", function () {
      syncControls(
        currentTheme(),
        currentAppearanceChoice(),
        document.documentElement.getAttribute("data-appearance") || "dark",
      );

      document.querySelectorAll("[data-theme-select]").forEach(function (select) {
        select.addEventListener("change", function () {
          saveAndApply(normalize(select.value, validThemes, "cosmic"), currentAppearanceChoice());
        });
      });

      document.querySelectorAll("[data-appearance-choice]").forEach(function (button) {
        button.addEventListener("click", function () {
          saveAndApply(
            currentTheme(),
            normalize(button.dataset.appearanceChoice, validAppearances, "dark"),
          );
        });
      });

      document.querySelectorAll("[data-appearance-toggle]").forEach(function (button) {
        button.addEventListener("click", function () {
          const resolved = document.documentElement.getAttribute("data-appearance");
          saveAndApply(currentTheme(), resolved === "dark" ? "light" : "dark");
        });
      });

      media.addEventListener("change", function () {
        if (currentAppearanceChoice() === "system") {
          applyTheme(currentTheme(), "system");
        }
      });
    });
  } catch (e) {}
})();
