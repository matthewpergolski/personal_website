from __future__ import annotations

import json

from fasthtml.common import Button, Div, H2, P, Script, Section, Span

from src.components.ui import HeroSection


def _top_language_items(values: dict | None, limit: int = 8) -> list[tuple[str, int]]:
    items = sorted(
        [(name, value) for name, value in (values or {}).items() if value > 0],
        key=lambda x: x[1],
        reverse=True,
    )
    top = items[:limit]
    if len(items) > limit:
        top.append(("Others", sum(v for _, v in items[limit:])))
    return top


def _repo_language_counts(repos: list[dict] | None) -> dict[str, int]:
    counts: dict[str, int] = {}
    for repo in repos or []:
        language = repo.get("language") or "Other"
        counts[language] = counts.get(language, 0) + 1
    return counts


def build_home_page(
    profile: dict | None,
    lang_bytes: dict | None,
    repos: list[dict] | None,
    experience_data: dict | None,
    github_username: str | None,
):
    experience_data = experience_data or {}
    highlights = [str(item) for item in experience_data.get("highlights", [])[:6]]

    byte_items = _top_language_items(lang_bytes)
    repo_items = _top_language_items(_repo_language_counts(repos))
    labels_bytes = [name for name, _ in byte_items]
    values_bytes = [value for _, value in byte_items]
    labels_repos = [name for name, _ in repo_items]
    values_repos = [value for _, value in repo_items]

    highlights_section = (
        Section(
            H2("Highlights", cls="section-title"),
            Div(
                *[
                    Div(
                        Span(f"{idx:02d}", cls="highlight-index"),
                        P(highlight, cls="highlight-copy"),
                        cls="highlight-card",
                    )
                    for idx, highlight in enumerate(highlights[:3], start=1)
                ],
                cls="container highlight-grid",
            ),
            cls="section",
        )
        if highlights
        else Div()
    )

    chart_section = (
        Section(
            H2("Tech Stack Snapshot", cls="section-title"),
            Div(
                Div(
                    Div(
                        Div(
                            Span("View", cls="chart-control-label"),
                            Div(
                                Button("Donut", id="chart-donut", cls="icon-link"),
                                Button("Bar", id="chart-bar", cls="icon-link"),
                                Button("Treemap", id="chart-tree", cls="icon-link"),
                                cls="chart-segment",
                            ),
                            cls="chart-control-group",
                        ),
                        Div(
                            Span("Metric", cls="chart-control-label"),
                            Div(
                                Button("Repos", id="metric-repos", cls="icon-link"),
                                Button("Bytes", id="metric-bytes", cls="icon-link"),
                                cls="chart-segment",
                            ),
                            cls="chart-control-group",
                        ),
                        Button(
                            "Download PNG",
                            id="chart-export",
                            cls="icon-link chart-export",
                            title="Download chart as PNG",
                        ),
                        cls="chart-toolbar",
                    ),
                    Div(id="lang-chart", cls="chart-canvas"),
                    cls="chart-shell",
                ),
            ),
            Script(
                _chart_script(
                    labels_bytes,
                    values_bytes,
                    labels_repos,
                    values_repos,
                    github_username,
                )
            ),
            cls="section",
        )
        if labels_bytes and values_bytes
        else Div()
    )

    return (
        HeroSection(profile, experience_data),
        highlights_section,
        chart_section,
    )


def _chart_script(
    labels_bytes: list[str],
    values_bytes: list[int],
    labels_repos: list[str],
    values_repos: list[int],
    github_username: str | None,
) -> str:
    return f"""
        (function(){{
          if(!window.Plotly) return;
          const labelsBytes = {json.dumps(labels_bytes)};
          const valuesBytes = {json.dumps(values_bytes)};
          const labelsRepos = {json.dumps(labels_repos)};
          const valuesRepos = {json.dumps(values_repos)};
          const ghUser = {json.dumps(github_username or "")};
          if(!labelsBytes.length && !labelsRepos.length) return;
          function colors(n) {{
            const palette=['#60a5fa','#fbbf24','#34d399','#f472b6','#a78bfa','#fca5a5','#93c5fd','#fcd34d','#4ade80','#f9a8d4'];
            const arr=[]; for(let i=0;i<n;i++) arr.push(palette[i%palette.length]); return arr;
          }}
          let metric='repos';
          function getLabels(){{ return metric==='bytes' ? labelsBytes : labelsRepos; }}
          function getVals(){{ return metric==='bytes' ? valuesBytes : valuesRepos; }}
          function compactPieText(labels, values, compact) {{
            if(!compact) return labels.map(_ => '');
            const total = values.reduce((acc, val) => acc + val, 0) || 1;
            return labels.map((label, index) => {{
              const pct = values[index] / total;
              if(pct < 0.1) return '';
              return `${{label}}<br>${{(pct * 100).toFixed(pct >= 0.1 ? 1 : 2)}}%`;
            }});
          }}
          function render(kind) {{
            const textColor = getComputedStyle(document.documentElement).getPropertyValue('--text-color').trim() || '#e2e8f0';
            const bg = 'rgba(0,0,0,0)';
            const compactChart = window.matchMedia('(max-width: 640px)').matches;
            let data, layout;
            const labels = getLabels();
            const v = getVals();
            if(kind==='bar') {{
              data=[{{ type:'bar', orientation:'h', x:v, y:labels, marker:{{color:colors(v.length)}}, hovertemplate: metric==='bytes' ? '%{{y}}: %{{x:,}} bytes<extra></extra>' : '%{{y}}: %{{x}} repos<extra></extra>' }}];
              const xtitle = metric==='bytes' ? 'Bytes' : 'Repositories';
              layout={{ paper_bgcolor:bg, plot_bgcolor:bg, margin: compactChart ? {{t:10,b:44,l:122,r:16}} : {{t:10,b:30,l:140,r:10}}, xaxis:{{tickfont:{{color:textColor}}, gridcolor:'rgba(255,255,255,0.05)', title:xtitle, rangemode:'tozero'}}, yaxis:{{tickfont:{{color:textColor}}}}, font:{{color:textColor}}, showlegend:false, uniformtext:{{mode:'hide', minsize:10}} }};
            }} else if (kind==='tree') {{
              data=[{{ type:'treemap', labels:labels, parents:labels.map(_=>''), values:v, marker:{{colors:colors(v.length)}}, hovertemplate: metric==='bytes' ? '%{{label}}<br>%{{value:,}} bytes<extra></extra>' : '%{{label}}<br>%{{value}} repos<extra></extra>' }}];
              layout={{ paper_bgcolor:bg, plot_bgcolor:bg, margin:{{t:10,b:10,l:10,r:10}}, font:{{color:textColor}} }};
            }} else {{
              data=[{{ type:'pie', hole:.5, labels, values:v, text:compactPieText(labels, v, compactChart), marker:{{colors:colors(v.length)}}, textinfo: compactChart ? 'text' : 'label+percent', textposition: compactChart ? 'inside' : 'outside', insidetextorientation:'horizontal', automargin:true, hovertemplate: metric==='bytes' ? '%{{label}}: %{{value:,}} bytes (%{{percent}})<extra></extra>' : '%{{label}}: %{{value}} repos (%{{percent}})<extra></extra>' }}];
              layout={{ paper_bgcolor:bg, plot_bgcolor:bg, showlegend:!compactChart, legend:{{ font:{{color:textColor}}, orientation:'h', y:-.12 }}, margin: compactChart ? {{t:16,b:18,l:18,r:18}} : {{t:24,b:80,l:72,r:72}}, font:{{color:textColor}}, uniformtext:{{mode:'hide', minsize: compactChart ? 9 : 11}} }};
            }}
            Plotly.newPlot('lang-chart', data, layout, {{displayModeBar:false, responsive:true}}).then(function(g) {{
              g.on('plotly_click', function(ev) {{
                if(!ev || !ev.points || !ev.points.length) return;
                const lang = (ev.points[0].label || ev.points[0].y || '').toString();
                if(!lang) return;
                const url = ghUser ? `https://github.com/${{ghUser}}?tab=repositories&language=${{encodeURIComponent(lang)}}` : `https://github.com/search?q=language:${{encodeURIComponent(lang)}}&type=repositories`;
                window.open(url, '_blank');
              }});
              const exportButton = document.getElementById('chart-export');
              if(exportButton) exportButton.onclick = async () => {{ try{{ const img=await Plotly.toImage(g, {{format:'png', height:700, width:1000, scale:2}}); const a=document.createElement('a'); a.href=img; a.download='tech-stack.png'; a.click(); }}catch(e){{}} }};
            }});
          }}
          let current='donut';
          function setActive(){{
            const map = {{
              'chart-bar': current==='bar',
              'chart-donut': current==='donut',
              'chart-tree': current==='tree',
              'metric-repos': metric==='repos',
              'metric-bytes': metric==='bytes'
            }};
            Object.keys(map).forEach(id=>{{
              const el=document.getElementById(id); if(!el) return;
              if(map[id]) el.classList.add('active'); else el.classList.remove('active');
            }});
          }}
          render(current); setActive();
          document.getElementById('chart-bar')?.addEventListener('click', ()=>{{current='bar'; render(current); setActive();}});
          document.getElementById('chart-donut')?.addEventListener('click', ()=>{{current='donut'; render(current); setActive();}});
          document.getElementById('chart-tree')?.addEventListener('click', ()=>{{current='tree'; render(current); setActive();}});
          document.getElementById('metric-bytes')?.addEventListener('click', ()=>{{metric='bytes'; render(current); setActive();}});
          document.getElementById('metric-repos')?.addEventListener('click', ()=>{{metric='repos'; render(current); setActive();}});
        }})();
    """
