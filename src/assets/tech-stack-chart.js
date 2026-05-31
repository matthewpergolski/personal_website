(function () {
  if (!window.Plotly) return;

  const dataEl = document.getElementById("tech-stack-chart-data");
  if (!dataEl) return;

  let chartData;
  try {
    chartData = JSON.parse(dataEl.textContent || "{}");
  } catch (_) {
    return;
  }

  const labelsBytes = chartData.labelsBytes || [];
  const valuesBytes = chartData.valuesBytes || [];
  const labelsRepos = chartData.labelsRepos || [];
  const valuesRepos = chartData.valuesRepos || [];
  const ghUser = chartData.githubUsername || "";
  if (!labelsBytes.length && !labelsRepos.length) return;

  function colors(n) {
    const palette = [
      "#60a5fa",
      "#fbbf24",
      "#34d399",
      "#f472b6",
      "#a78bfa",
      "#fca5a5",
      "#93c5fd",
      "#fcd34d",
      "#4ade80",
      "#f9a8d4",
    ];
    const arr = [];
    for (let i = 0; i < n; i += 1) arr.push(palette[i % palette.length]);
    return arr;
  }

  let metric = "repos";
  let current = "donut";
  const viewHints = {
    donut: "Donut shows proportional share across the selected metric.",
    bar: "Bar compares absolute totals, making ranking easiest to scan.",
    tree: "Treemap shows the overall mix in a compact space.",
  };
  const metricHints = {
    repos: "Repos counts how often each language appears across projects.",
    bytes: "Bytes weights the view by code volume.",
  };

  function getLabels() {
    return metric === "bytes" ? labelsBytes : labelsRepos;
  }

  function getVals() {
    return metric === "bytes" ? valuesBytes : valuesRepos;
  }

  function compactName(label) {
    const map = {
      "Jupyter Notebook": "Jupyter",
      Dockerfile: "Docker",
      TypeScript: "TS",
      JavaScript: "JS",
    };
    return map[label] || label;
  }

  function compactPieText(labels, values, compact) {
    if (!compact) return labels.map(() => "");
    const total = values.reduce((acc, val) => acc + val, 0) || 1;
    return labels.map((label, index) => {
      const pct = values[index] / total;
      if (pct < 0.08) return "";
      return `${compactName(label)}<br>${(pct * 100).toFixed(1)}%`;
    });
  }

  function formatChartValue(value) {
    if (metric === "repos") return `${value} repo${value === 1 ? "" : "s"}`;
    const units = ["bytes", "KB", "MB", "GB"];
    let amount = value;
    let unitIndex = 0;
    while (amount >= 1024 && unitIndex < units.length - 1) {
      amount /= 1024;
      unitIndex += 1;
    }
    const decimals = amount >= 10 || unitIndex === 0 ? 0 : 1;
    return `${amount.toFixed(decimals)} ${units[unitIndex]}`;
  }

  function chartPercent(value, total) {
    const pct = (value / (total || 1)) * 100;
    return `${pct < 1 ? pct.toFixed(2) : pct.toFixed(1)}%`;
  }

  function renderChartKey(labels, values, palette, compact) {
    const key = document.getElementById("chart-key");
    if (!key) return;
    if (!compact) {
      key.replaceChildren();
      return;
    }
    const total = values.reduce((acc, val) => acc + val, 0) || 1;
    const list = document.createElement("div");
    list.className = "chart-key-list";
    labels.forEach((label, index) => {
      const item = document.createElement("div");
      item.className = "chart-key-item";
      item.setAttribute(
        "aria-label",
        `${label}, ${formatChartValue(values[index])}, ${chartPercent(values[index], total)}`,
      );

      const swatch = document.createElement("span");
      swatch.className = "chart-key-swatch";
      swatch.style.background = palette[index];

      const name = document.createElement("span");
      name.className = "chart-key-label";
      name.textContent = compactName(label);
      name.title = label;

      const value = document.createElement("span");
      value.className = "chart-key-value";
      value.textContent = `${formatChartValue(values[index])} / ${chartPercent(values[index], total)}`;

      item.append(swatch, name, value);
      list.append(item);
    });
    key.replaceChildren(list);
  }

  function chartLayout(textColor, compactChart, kind) {
    const bg = "rgba(0,0,0,0)";
    if (kind === "bar") {
      return {
        paper_bgcolor: bg,
        plot_bgcolor: bg,
        margin: compactChart ? { t: 10, b: 44, l: 122, r: 16 } : { t: 10, b: 30, l: 140, r: 10 },
        xaxis: {
          tickfont: { color: textColor },
          gridcolor: "rgba(255,255,255,0.05)",
          title: metric === "bytes" ? "Bytes" : "Repositories",
          rangemode: "tozero",
        },
        yaxis: { tickfont: { color: textColor } },
        font: { color: textColor },
        showlegend: false,
        uniformtext: { mode: "hide", minsize: 10 },
      };
    }
    if (kind === "tree") {
      return {
        paper_bgcolor: bg,
        plot_bgcolor: bg,
        margin: { t: 10, b: 10, l: 10, r: 10 },
        font: { color: textColor },
      };
    }
    return {
      paper_bgcolor: bg,
      plot_bgcolor: bg,
      showlegend: !compactChart,
      legend: { font: { color: textColor }, orientation: "h", y: -0.12 },
      margin: compactChart ? { t: 18, b: 24, l: 28, r: 28 } : { t: 24, b: 80, l: 72, r: 72 },
      font: { color: textColor },
      uniformtext: { mode: "show", minsize: compactChart ? 9 : 11 },
    };
  }

  function render(kind) {
    const textColor =
      getComputedStyle(document.documentElement).getPropertyValue("--text-color").trim() ||
      "#e2e8f0";
    const compactChart = window.matchMedia("(max-width: 640px)").matches;
    const labels = getLabels();
    const values = getVals();
    const palette = colors(values.length);
    let data;
    renderChartKey(labels, values, palette, compactChart);
    if (kind === "bar") {
      data = [
        {
          type: "bar",
          orientation: "h",
          x: values,
          y: labels,
          marker: { color: palette },
          hovertemplate:
            metric === "bytes"
              ? "%{y}: %{x:,} bytes<extra></extra>"
              : "%{y}: %{x} repos<extra></extra>",
        },
      ];
    } else if (kind === "tree") {
      data = [
        {
          type: "treemap",
          labels,
          parents: labels.map(() => ""),
          values,
          marker: { colors: palette },
          hovertemplate:
            metric === "bytes"
              ? "%{label}<br>%{value:,} bytes<extra></extra>"
              : "%{label}<br>%{value} repos<extra></extra>",
        },
      ];
    } else {
      data = [
        {
          type: "pie",
          hole: 0.5,
          labels,
          values,
          text: compactPieText(labels, values, compactChart),
          marker: { colors: palette },
          textinfo: compactChart ? "text" : "label+percent",
          textposition: compactChart ? "auto" : "outside",
          insidetextorientation: "horizontal",
          automargin: true,
          hovertemplate:
            metric === "bytes"
              ? "%{label}: %{value:,} bytes (%{percent})<extra></extra>"
              : "%{label}: %{value} repos (%{percent})<extra></extra>",
        },
      ];
    }
    Plotly.newPlot("lang-chart", data, chartLayout(textColor, compactChart, kind), {
      displayModeBar: false,
      responsive: true,
    }).then((graph) => {
      graph.on("plotly_click", (ev) => {
        if (!ev || !ev.points || !ev.points.length) return;
        const lang = (ev.points[0].label || ev.points[0].y || "").toString();
        if (!lang) return;
        const url = ghUser
          ? `https://github.com/${ghUser}?tab=repositories&language=${encodeURIComponent(lang)}`
          : `https://github.com/search?q=language:${encodeURIComponent(lang)}&type=repositories`;
        window.open(url, "_blank");
      });
      const exportButton = document.getElementById("chart-export");
      if (exportButton) {
        exportButton.onclick = async () => {
          try {
            const img = await Plotly.toImage(graph, {
              format: "png",
              height: 700,
              width: 1000,
              scale: 2,
            });
            const link = document.createElement("a");
            link.href = img;
            link.download = "tech-stack.png";
            link.click();
          } catch (_) {}
        };
      }
    });
  }

  function setActive() {
    const map = {
      "chart-bar": current === "bar",
      "chart-donut": current === "donut",
      "chart-tree": current === "tree",
      "metric-repos": metric === "repos",
      "metric-bytes": metric === "bytes",
    };
    Object.keys(map).forEach((id) => {
      const el = document.getElementById(id);
      if (!el) return;
      if (map[id]) el.classList.add("active");
      else el.classList.remove("active");
    });
    const hint = document.getElementById("chart-hint");
    if (hint) hint.textContent = `${viewHints[current]} ${metricHints[metric]}`;
  }

  render(current);
  setActive();
  document.getElementById("chart-bar")?.addEventListener("click", () => {
    current = "bar";
    render(current);
    setActive();
  });
  document.getElementById("chart-donut")?.addEventListener("click", () => {
    current = "donut";
    render(current);
    setActive();
  });
  document.getElementById("chart-tree")?.addEventListener("click", () => {
    current = "tree";
    render(current);
    setActive();
  });
  document.getElementById("metric-bytes")?.addEventListener("click", () => {
    metric = "bytes";
    render(current);
    setActive();
  });
  document.getElementById("metric-repos")?.addEventListener("click", () => {
    metric = "repos";
    render(current);
    setActive();
  });
})();
