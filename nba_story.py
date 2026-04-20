"""
SI 649 Narrative Visualization Project

Builds a single index.html narrative that explains how the NBA's playstyle has
shifted across a half-century of rule changes and analytics adoption.

Data lives in /data as CSVs sourced from Basketball-Reference:
    data/league_seasons.csv      per-season league averages, 1979-80 -> 2023-24
    data/shot_zones.csv          per-season shot-zone share of FGA, 1996-97+
    data/position_shooting.csv   per-position 3PA, 3P%, TS% by decade

How to run:
    pip install altair pandas
    python nba_story.py

Output:
    index.html   (uploadable as-is to GitHub Pages)
"""

from pathlib import Path
import textwrap

import altair as alt
import pandas as pd


DATA_DIR = Path(__file__).parent / "data"

league = pd.read_csv(DATA_DIR / "league_seasons.csv")
zones = pd.read_csv(DATA_DIR / "shot_zones.csv")
positions = pd.read_csv(DATA_DIR / "position_shooting.csv")

# pre-compute a few "nice to display" columns so tooltips read as percentages
league["three_share"] = (league["fg3a_pg"] / league["fga_pg"] * 100).round(1)
league["ts_pct_display"] = (league["ts_pct"] * 100).round(1)

zones["pct_display"] = (zones["pct_of_fga"] * 100).round(1)
zones["fg_pct_display"] = (zones["fg_pct"] * 100).round(1)

positions["fg3_pct_display"] = (positions["fg3_pct"] * 100).round(1)
positions["ts_pct_display"] = (positions["ts_pct"] * 100).round(1)

ZONE_ORDER = ["0-3 ft", "3-10 ft", "10-16 ft", "16 ft - 3PT", "3-Point"]
ZONE_COLORS = ["#b91c1c", "#f97316", "#eab308", "#0ea5e9", "#1e40af"]
POSITION_ORDER = ["PG", "SG", "SF", "PF", "C"]
ERA_ORDER = ["1990s", "2000s", "2010s", "2020s"]
ERA_COLORS = ["#cbd5e1", "#94a3b8", "#2563eb", "#1e1b4b"]


alt.data_transformers.disable_max_rows()
base_config = {
    "view": {"stroke": None},
    "axis": {
        "labelFont": "Arial",
        "titleFont": "Arial",
        "labelColor": "#333333",
        "titleColor": "#333333",
        "gridColor": "#e6e6e6",
    },
    "legend": {
        "labelFont": "Arial",
        "titleFont": "Arial",
        "labelColor": "#333333",
        "titleColor": "#333333",
    },
    "title": {"font": "Arial", "color": "#222222"},
}


# Chart 1: rise of the three-point shot
rule_changes = pd.DataFrame(
    [
        (1979, "3-point line added"),
        (1994, "line shortened"),
        (1997, "line moved back"),
        (2004, "hand-check banned"),
        (2015, "pace-and-space era"),
    ],
    columns=["season_start", "label"],
)

chart1_rules = (
    alt.Chart(rule_changes)
    .mark_rule(color="#9ca3af", strokeDash=[4, 4])
    .encode(x="season_start:Q")
)

chart1_text = (
    alt.Chart(rule_changes)
    .mark_text(align="left", dx=5, dy=-4, fontSize=10, color="#6b7280")
    .encode(x="season_start:Q", y=alt.value(14), text="label:N")
)

chart1_line = (
    alt.Chart(league)
    .mark_line(strokeWidth=3, color="#1d4ed8", point=True)
    .encode(
        x=alt.X("season_start:Q", title="Season", axis=alt.Axis(format="d")),
        y=alt.Y("fg3a_pg:Q", title="3-point attempts per game"),
        tooltip=[
            alt.Tooltip("season:N", title="Season"),
            alt.Tooltip("fg3a_pg:Q", title="3PA/game"),
            alt.Tooltip("three_share:Q", title="% of all shots", format=".1f"),
        ],
    )
)

chart1 = (
    (chart1_rules + chart1_text + chart1_line)
    .properties(
        width=720,
        height=320,
        title="Chart 1. The three-point shot went from novelty to default offense",
    )
    .configure(**base_config)
)


# Chart 2: pace, scoring, and efficiency (pick one with the radio)
metric_names = {
    "pts_pg": "Points per game",
    "pace": "Pace (possessions per 48)",
    "ortg": "Offensive rating (pts per 100 poss.)",
    "ts_pct_display": "True shooting % (league)",
}

c2_long = league.melt(
    id_vars=["season", "season_start"],
    value_vars=list(metric_names.keys()),
    var_name="metric_key",
    value_name="value",
)
c2_long["metric"] = c2_long["metric_key"].map(metric_names)

metric_select = alt.selection_point(
    fields=["metric"],
    bind=alt.binding_radio(options=list(metric_names.values()), name="Show: "),
    value="Offensive rating (pts per 100 poss.)",
)

chart2 = (
    alt.Chart(c2_long)
    .mark_line(strokeWidth=3, color="#0d9488")
    .encode(
        x=alt.X("season_start:Q", title="Season", axis=alt.Axis(format="d")),
        y=alt.Y("value:Q", title="Value", scale=alt.Scale(zero=False)),
        tooltip=[
            alt.Tooltip("season:N", title="Season"),
            alt.Tooltip("metric:N", title="Metric"),
            alt.Tooltip("value:Q", title="Value", format=".1f"),
        ],
    )
    .transform_filter(metric_select)
    .add_params(metric_select)
    .properties(
        width=720,
        height=320,
        title="Chart 2. Scoring, pace, and efficiency each tell a different part of the story",
    )
    .configure(**base_config)
)


# Chart 3: where shots come from (stacked area of shot zones)
chart3 = (
    alt.Chart(zones)
    .mark_area(opacity=0.92)
    .encode(
        x=alt.X(
            "season_start:Q",
            title="Season",
            axis=alt.Axis(format="d"),
            scale=alt.Scale(domain=[1996, 2023]),
        ),
        y=alt.Y(
            "pct_of_fga:Q",
            stack="normalize",
            title="Share of all shot attempts",
            axis=alt.Axis(format="%"),
        ),
        color=alt.Color(
            "zone:N",
            sort=ZONE_ORDER,
            scale=alt.Scale(domain=ZONE_ORDER, range=ZONE_COLORS),
            title="Shot zone",
            legend=alt.Legend(orient="right"),
        ),
        order=alt.Order("zone:N", sort="ascending"),
        tooltip=[
            alt.Tooltip("season:N", title="Season"),
            alt.Tooltip("zone:N", title="Zone"),
            alt.Tooltip("pct_display:Q", title="% of all shots", format=".1f"),
            alt.Tooltip("fg_pct_display:Q", title="FG% from zone", format=".1f"),
        ],
    )
    .properties(
        width=700,
        height=340,
        title="Chart 3. The mid-range shot has nearly disappeared",
    )
    .configure(**base_config)
)


# Chart 4: per-position 3-point attempts by era
era_select = alt.selection_point(
    fields=["era"],
    bind=alt.binding_select(options=ERA_ORDER, name="Highlight era: "),
    value="2020s",
)

chart4 = (
    alt.Chart(positions)
    .mark_bar()
    .encode(
        x=alt.X("position:N", sort=POSITION_ORDER, title="Position"),
        y=alt.Y("fg3a_pg:Q", title="Average 3-point attempts per game"),
        color=alt.Color(
            "era:N",
            sort=ERA_ORDER,
            scale=alt.Scale(domain=ERA_ORDER, range=ERA_COLORS),
            title="Era",
        ),
        xOffset=alt.XOffset("era:N", sort=ERA_ORDER),
        opacity=alt.condition(era_select, alt.value(1.0), alt.value(0.25)),
        tooltip=[
            alt.Tooltip("era:N", title="Era"),
            alt.Tooltip("position:N", title="Position"),
            alt.Tooltip("fg3a_pg:Q", title="3PA/game", format=".1f"),
            alt.Tooltip("fg3_pct_display:Q", title="3P%", format=".1f"),
            alt.Tooltip("ts_pct_display:Q", title="TS%", format=".1f"),
        ],
    )
    .add_params(era_select)
    .properties(
        width=720,
        height=320,
        title="Chart 4. Every position moved outward \u2014 even centers now shoot threes",
    )
    .configure(**base_config)
)


# Wrap an Altair chart into a small <div> + vegaEmbed snippet we can
# drop straight into the HTML article below.
def embed_chart(chart: alt.Chart, div_id: str) -> str:
    spec = chart.to_json(indent=None)
    return f"""
    <div id=\"{div_id}\" class=\"chart\"></div>
    <script>
      vegaEmbed('#{div_id}', {spec}, {{actions: false}});
    </script>
    """


html = f"""
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>How the NBA Changed Its Game</title>
  <script src=\"https://cdn.jsdelivr.net/npm/vega@5\"></script>
  <script src=\"https://cdn.jsdelivr.net/npm/vega-lite@5\"></script>
  <script src=\"https://cdn.jsdelivr.net/npm/vega-embed@6\"></script>
  <style>
    body {{
      font-family: Georgia, 'Times New Roman', serif;
      margin: 0;
      background: #fafafa;
      color: #1f2937;
      line-height: 1.7;
    }}
    .page {{
      max-width: 860px;
      margin: 0 auto;
      padding: 36px 22px 60px 22px;
      background: white;
    }}
    .kicker {{
      color: #6b7280;
      text-transform: uppercase;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 12px;
      letter-spacing: 0.1em;
      margin-bottom: 10px;
    }}
    h1 {{
      font-size: 40px;
      line-height: 1.15;
      margin: 0 0 12px 0;
      font-weight: 700;
    }}
    .dek {{
      font-size: 20px;
      color: #374151;
      margin-bottom: 20px;
      line-height: 1.45;
    }}
    .byline {{
      font-family: Arial, Helvetica, sans-serif;
      font-size: 14px;
      color: #6b7280;
      padding-bottom: 20px;
      border-bottom: 1px solid #e5e7eb;
      margin-bottom: 26px;
    }}
    .note {{
      background: #eef2ff;
      border-left: 4px solid #4338ca;
      padding: 14px 16px;
      margin: 22px 0 30px 0;
      font-size: 15px;
      font-family: Arial, Helvetica, sans-serif;
    }}
    h2 {{
      margin-top: 40px;
      margin-bottom: 10px;
      font-size: 26px;
      line-height: 1.25;
    }}
    p {{
      margin-top: 0;
      margin-bottom: 16px;
      font-size: 17px;
    }}
    .chart {{
      margin: 14px 0 10px 0;
    }}
    .caption {{
      color: #6b7280;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 13px;
      margin-bottom: 28px;
    }}
    ul.refs {{
      font-family: Arial, Helvetica, sans-serif;
      font-size: 14px;
      padding-left: 20px;
    }}
    ul.refs li {{
      margin-bottom: 10px;
    }}
    .glossary {{
      background: #f9fafb;
      border: 1px solid #e5e7eb;
      border-radius: 6px;
      padding: 12px 16px;
      margin: 20px 0 24px 0;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 14px;
    }}
    .glossary strong {{ color: #111827; }}
    .footer {{
      margin-top: 44px;
      padding-top: 22px;
      border-top: 1px solid #e5e7eb;
      color: #6b7280;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 13px;
    }}
    a {{ color: #1d4ed8; }}
  </style>
</head>
<body>
  <div class=\"page\">
    <div class=\"kicker\">SI 649 \u00b7 Narrative Visualization</div>
    <h1>How the NBA Changed Its Game</h1>
    <div class=\"dek\">
      Over the last half-century the NBA has rebuilt itself around the three-point line.
      Rule changes opened up the perimeter, and analytics and roster design turned that opening
      into a new style of basketball \u2014 one with fewer mid-range jumpers, more shooters at every
      position, and higher scoring than ever before.
    </div>
    <div class=\"byline\">
      By Mustada A-Ogaili, Ali Al-Ogaili, Mohammad Farhat, and Lamonte Nunn
    </div>

    <div class=\"note\">
      <strong>What this article covers:</strong> how shot selection, pace, and efficiency in the
      NBA changed between the 1979\u201380 season (when the three-point line was added) and
      2023\u201324. The charts are interactive \u2014 hover for season values, toggle a metric, or
      pick an era to focus on.
    </div>

    <h2>The three-point shot took decades to become the default</h2>
    <p>
      When the NBA added the three-point line in 1979, teams did not really use it.
      Early in the 1980s, league averages sat around three attempts per game. By 2023\u201324,
      the league averaged more than 35 threes per team per game \u2014 about a ten-fold jump.
      The rise was not smooth. It spiked in 1994 when the line was shortened, dropped
      again when the line was moved back in 1997, and then took off for good after the
      mid-2000s rule changes that made perimeter defense harder.
    </p>
    <p>
      We track the overall 3PA per game below, with dashed lines for the rule changes
      that seemed to matter most. One thing worth flagging up front: league three-point
      accuracy has only drifted between about 34% and 37% this whole time. The change in
      the NBA is not that players learned to shoot \u2014 it is that teams kept deciding
      to shoot more threes anyway.
    </p>
    {embed_chart(chart1, "chart1")}
    <div class=\"caption\">Dashed lines mark key rule changes. Hover to see season values.</div>

    <div class=\"glossary\">
      <strong>Quick glossary.</strong>
      <em>True shooting % (TS%)</em> counts threes and free throws alongside regular field goals,
      so it reflects how efficiently a team scores from every kind of shot.
      <em>Effective FG% (eFG%)</em> credits a made three as 1.5 made twos.
      <em>Offensive rating (ORtg)</em> is points scored per 100 possessions \u2014 a pace-neutral
      view of how good an offense is.
    </div>

    <h2>Pace crashed, then came back \u2014 and offense kept getting more efficient</h2>
    <p>
      People sometimes describe the modern NBA as just faster. That is only part of it.
      Pace actually collapsed in the late 1990s and early 2000s, when rough perimeter
      defense slowed games down. The 2003\u201304 season hit a low of 93.4 points per game
      and 90.1 possessions per 48 minutes. Today pace is roughly back to where it was
      in the 1980s, but offensive rating \u2014 points per 100 possessions \u2014 has climbed
      to an all-time high near 115.
    </p>
    <p>
      The radio buttons below switch between four measures. Points per game and pace
      move together, which makes sense: more possessions means more chances to score.
      But offensive rating and TS% tell a different story. Even on a per-possession
      basis, modern offenses are the most efficient in league history.
    </p>
    {embed_chart(chart2, "chart2")}
    <div class=\"caption\">
      Offensive rating and TS% are the pace-adjusted ways to compare eras \u2014 both show the 2020s
      as the most efficient era on record.
    </div>

    <h2>The mid-range jumper nearly disappeared</h2>
    <p>
      Maybe the clearest single chart of the modern NBA is a breakdown of where shots
      come from. The league started tracking shot location in 1996\u201397. Back then,
      about a third of all shots came from mid-range \u2014 the 10\u201316 ft zone or the long two.
      Those shots converted around 40% of the time, which was basically the same expected
      value as a three, only without the extra point.
    </p>
    <p>
      Teams eventually did the math. Over the next 25 years the mid-range share
      collapsed. By 2023\u201324 the 10\u201316 ft zone was barely 5% of shots, and long twos
      fell from about 20% of attempts to under 10%. Those shots did not vanish, they
      moved \u2014 out to the three-point line, which now produces close to 40% of every
      shot the league takes, and in to the rim.
    </p>
    {embed_chart(chart3, "chart3")}
    <div class=\"caption\">
      Hover any band for zone share and field-goal percentage that season.
      Shot-location tracking began in 1996\u201397, so the chart starts there.
    </div>

    <h2>Every position moved outward \u2014 even the centers</h2>
    <p>
      The league-wide shift shows up most clearly in what each position is asked to do.
      In the 1990s, a typical center basically did not shoot threes. Power forwards took
      a handful a week. Today a starting center averages more than two three-point
      attempts per game, and power forwards launch more than four. Point guards nearly
      tripled their three-point volume between the 1990s and the 2020s.
    </p>
    <p>
      Again, this is not really a story about everyone learning to shoot. Three-point
      accuracy has barely moved in three decades. What changed is the expectation: every
      position is now asked to shoot from deep, and the bigs who can stretch to the arc
      give teams the spacing that makes the rest of the offense work.
    </p>
    {embed_chart(chart4, "chart4")}
    <div class=\"caption\">
      Select an era with the dropdown to highlight it. Tooltip shows 3PA per game, 3P%, and TS%.
    </div>

    <h2>What changed, really</h2>
    <p>
      The four charts together tell a pretty consistent story. Rules changed first:
      the three-point line in 1979, the elimination of illegal defense in 2001, and the
      hand-check ban in 2004 all rewarded perimeter movement. Analytics followed: once
      teams could measure shot efficiency at scale, long twos lost their justification.
      Rosters changed last: centers added threes because the spacing math demanded it,
      and point guards became primary scorers instead of just passers.
    </p>
    <p>
      The easy version of this story is that the modern NBA just got faster and more
      skilled. That is true, but it misses the bigger shift. The deeper change is that
      the whole definition of a good shot got rewritten, one rule change and one roster
      at a time.
    </p>

    <h2>Sources</h2>
    <ul class=\"refs\">
      <li>
        Basketball-Reference. <em>NBA League Averages \u2013 Per Game</em>.
        <a href=\"https://www.basketball-reference.com/leagues/NBA_stats_per_game.html\">basketball-reference.com/leagues/NBA_stats_per_game.html</a>
      </li>
      <li>
        Basketball-Reference. <em>NBA League Averages \u2013 Advanced</em> (pace, ORtg, TS%, eFG%).
        <a href=\"https://www.basketball-reference.com/leagues/NBA_stats_advanced.html\">basketball-reference.com/leagues/NBA_stats_advanced.html</a>
      </li>
      <li>
        Basketball-Reference. <em>NBA League Averages \u2013 Shooting</em> (zone distribution).
        <a href=\"https://www.basketball-reference.com/leagues/NBA_stats_shooting.html\">basketball-reference.com/leagues/NBA_stats_shooting.html</a>
      </li>
      <li>
        NBA.com. <em>This Day in History \u2013 the first three-point field goal</em>.
        <a href=\"https://www.nba.com/news/this-day-in-history-oct-12-the-first-3-point-field-goal\">nba.com/news/this-day-in-history-oct-12-the-first-3-point-field-goal</a>
      </li>
      <li>
        NBA Video Rulebook. <em>Handcheck</em>.
        <a href=\"https://videorulebook.nba.com/rule/handcheck/\">videorulebook.nba.com/rule/handcheck</a>
      </li>
      <li>
        Skinner, B. (2012). <em>The Problem of Shot Selection in Basketball</em>. PLOS ONE.
        <a href=\"https://pmc.ncbi.nlm.nih.gov/articles/PMC3266291/\">pmc.ncbi.nlm.nih.gov/articles/PMC3266291</a>
      </li>
      <li>
        Z\u0105j\u0105c et al. (2023). <em>Long-Term Trends in Shooting Performance in the NBA</em>.
        <a href=\"https://pmc.ncbi.nlm.nih.gov/articles/PMC9915101/\">pmc.ncbi.nlm.nih.gov/articles/PMC9915101</a>
      </li>
    </ul>

    <div class=\"footer\">
      Built with Python + Altair. Data loaded from bundled CSVs under <code>/data</code>;
      rebuild with <code>python nba_story.py</code>.
    </div>
  </div>
</body>
</html>
"""

out_path = Path(__file__).parent / "index.html"
out_path.write_text(textwrap.dedent(html), encoding="utf-8")
print(f"Wrote {out_path.resolve()}")
