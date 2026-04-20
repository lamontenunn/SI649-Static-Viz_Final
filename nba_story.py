"""
SI 649 Narrative Visualization Project Draft

This script builds one single HTML page for our NBA narrative visualization.
We kept it intentionally simple:
- one Python file
- data written directly in the file
- Altair for the charts
- output is one index.html that can be uploaded to GitHub Pages

How to run locally:
    pip install altair pandas
    python nba_story_altair.py

What it makes:
    index.html

Notes:
- We are using league-level data first because it is easier to verify and
  helps us avoid data-cleaning problems too late in the semester.
"""

from pathlib import Path
import textwrap

import altair as alt
import pandas as pd


# -----------------------------
# Core league data
# -----------------------------
# Source: Basketball-Reference league averages
# https://www.basketball-reference.com/leagues/NBA_stats_per_game.html
# https://www.basketball-reference.com/leagues/NBA_stats_advanced.html
RAW = [
    ("1979-80", 108.2, 2.8, 85.8, 97.0, 0.280),
    ("1980-81", 108.1, 3.3, 86.4, 97.6, 0.284),
    ("1981-82", 108.6, 2.9, 85.7, 98.3, 0.279),
    ("1982-83", 109.2, 3.0, 86.8, 99.8, 0.280),
    ("1983-84", 110.1, 3.2, 87.8, 100.0, 0.283),
    ("1984-85", 110.8, 3.4, 88.9, 101.4, 0.282),
    ("1985-86", 110.2, 3.6, 88.3, 99.9, 0.283),
    ("1986-87", 109.9, 4.0, 88.2, 99.4, 0.301),
    ("1987-88", 109.0, 4.5, 87.0, 98.0, 0.295),
    ("1988-89", 109.2, 5.1, 87.8, 98.9, 0.310),
    ("1989-90", 107.0, 5.3, 85.8, 96.9, 0.333),
    ("1990-91", 106.3, 6.0, 86.2, 97.8, 0.333),
    ("1991-92", 105.3, 6.3, 85.8, 96.6, 0.333),
    ("1992-93", 105.3, 7.1, 86.5, 97.2, 0.340),
    ("1993-94", 101.5, 7.4, 83.5, 94.8, 0.337),
    ("1994-95", 101.4, 11.6, 84.8, 95.8, 0.361),
    ("1995-96", 100.8, 14.9, 84.3, 94.0, 0.361),
    ("1996-97", 101.9, 15.4, 84.8, 95.7, 0.363),
    ("1997-98", 96.9, 11.1, 82.1, 91.3, 0.350),
    ("1998-99", 91.6, 9.9, 78.0, 88.9, 0.343),
    ("1999-00", 97.5, 13.0, 82.2, 93.1, 0.353),
    ("2000-01", 94.8, 13.7, 80.7, 91.3, 0.352),
    ("2001-02", 95.5, 14.0, 81.1, 90.9, 0.352),
    ("2002-03", 95.1, 14.9, 80.8, 91.0, 0.358),
    ("2003-04", 93.4, 14.9, 80.2, 90.1, 0.357),
    ("2004-05", 97.2, 16.3, 81.7, 90.9, 0.356),
    ("2005-06", 97.1, 17.2, 82.0, 90.4, 0.358),
    ("2006-07", 98.7, 17.3, 83.0, 91.9, 0.360),
    ("2007-08", 99.9, 18.1, 83.7, 92.4, 0.360),
    ("2008-09", 100.0, 18.0, 82.2, 91.7, 0.360),
    ("2009-10", 100.4, 18.0, 82.7, 92.7, 0.358),
    ("2010-11", 99.6, 18.0, 82.6, 92.1, 0.355),
    ("2011-12", 96.3, 18.4, 81.3, 91.3, 0.349),
    ("2012-13", 98.1, 19.4, 82.5, 92.0, 0.359),
    ("2013-14", 101.8, 20.0, 83.9, 93.9, 0.361),
    ("2014-15", 100.0, 22.4, 84.6, 93.9, 0.354),
    ("2015-16", 104.6, 24.9, 85.4, 95.8, 0.358),
    ("2016-17", 105.6, 27.0, 85.4, 96.4, 0.358),
    ("2017-18", 106.3, 29.0, 85.8, 97.3, 0.362),
    ("2018-19", 111.2, 32.0, 88.3, 100.0, 0.355),
    ("2019-20", 111.8, 34.1, 88.8, 100.0, 0.358),
    ("2020-21", 112.1, 34.6, 88.4, 99.2, 0.368),
    ("2021-22", 112.5, 35.2, 88.0, 98.2, 0.354),
    ("2022-23", 114.7, 34.2, 88.7, 99.1, 0.366),
    ("2023-24", 114.3, 35.1, 89.2, 99.9, 0.364),
]

league = pd.DataFrame(
    RAW,
    columns=["season", "pts_pg", "fg3a_pg", "fga_pg", "pace", "fg3_pct"],
)
league["season_start"] = league["season"].str[:4].astype(int)
league["three_share"] = (league["fg3a_pg"] / league["fga_pg"] * 100).round(1)
league["fg3_pct_display"] = (league["fg3_pct"] * 100).round(1)


def era_label(year: int) -> str:
    if year <= 2003:
        return "Before 2004 rule changes"
    if year <= 2014:
        return "Transition years"
    return "Modern spacing era"


league["era"] = league["season_start"].apply(era_label)


# Simple position chart data.
# These are rough decade-level values meant for a supporting chart,
# not the main statistical claim of the piece.
position_data = pd.DataFrame(
    [
        ("1990s", "Point Guard", 3.8),
        ("1990s", "Shooting Guard", 2.9),
        ("1990s", "Small Forward", 1.1),
        ("1990s", "Power Forward", 0.4),
        ("1990s", "Center", 0.0),
        ("2010s", "Point Guard", 5.2),
        ("2010s", "Shooting Guard", 4.8),
        ("2010s", "Small Forward", 3.2),
        ("2010s", "Power Forward", 1.8),
        ("2010s", "Center", 0.3),
        ("2020s", "Point Guard", 8.1),
        ("2020s", "Shooting Guard", 7.4),
        ("2020s", "Small Forward", 6.1),
        ("2020s", "Power Forward", 4.2),
        ("2020s", "Center", 2.9),
    ],
    columns=["era", "position", "fg3a_pg"],
)


# -----------------------------
# Altair setup
# -----------------------------
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

# Chart 1: rise of threes
hover1 = alt.selection_point(fields=["season"], nearest=True, on="mouseover", empty=False)

chart1_line = (
    alt.Chart(league)
    .mark_line(color="#2b6cb0", strokeWidth=3)
    .encode(
        x=alt.X("season_start:Q", title="Season"),
        y=alt.Y("fg3a_pg:Q", title="Three-point attempts per game"),
        tooltip=[
            alt.Tooltip("season:N", title="Season"),
            alt.Tooltip("fg3a_pg:Q", title="3PA/game"),
            alt.Tooltip("three_share:Q", title="3PA share of all shots (%)"),
        ],
    )
)

chart1_points = chart1_line.mark_circle(size=55).encode(opacity=alt.condition(hover1, alt.value(1), alt.value(0)))
chart1_rule = (
    alt.Chart(league)
    .mark_rule(color="#999999")
    .encode(x="season_start:Q")
    .transform_filter(hover1)
)

chart1_annotations = pd.DataFrame(
    [
        (1979, 4.5, "3-point line added"),
        (1995, 14.5, "line shortened"),
        (1998, 12.0, "line restored"),
        (2015, 24.0, "pace-and-space takes off"),
    ],
    columns=["season_start", "fg3a_pg", "label"],
)

chart1_text = (
    alt.Chart(chart1_annotations)
    .mark_text(align="left", dx=6, dy=-8, fontSize=11, color="#555555")
    .encode(x="season_start:Q", y="fg3a_pg:Q", text="label:N")
)

chart1 = (chart1_line + chart1_points + chart1_rule + chart1_text).add_params(hover1).properties(
    width=720,
    height=300,
    title="Chart 1. The three-point shot went from novelty to default offense",
).configure(**base_config)


# Chart 2: pace and scoring after the early-2000s slowdown
long_pace = league[["season_start", "season", "pace", "pts_pg"]].melt(
    id_vars=["season_start", "season"],
    value_vars=["pace", "pts_pg"],
    var_name="metric",
    value_name="value",
)
metric_labels = ["pace", "pts_pg"]
metric_names = {"pace": "Pace (possessions per 48)", "pts_pg": "Points per game"}
long_pace["metric_label"] = long_pace["metric"].map(metric_names)

metric_select = alt.selection_point(
    fields=["metric_label"],
    bind=alt.binding_radio(options=list(metric_names.values()), name="Show: "),
    value="Points per game",
)

chart2 = (
    alt.Chart(long_pace)
    .mark_line(strokeWidth=3)
    .encode(
        x=alt.X("season_start:Q", title="Season"),
        y=alt.Y("value:Q", title="Value"),
        color=alt.Color(
            "metric_label:N",
            scale=alt.Scale(domain=list(metric_names.values()), range=["#1f9d8a", "#d97706"]),
            legend=None,
        ),
        tooltip=[
            alt.Tooltip("season:N", title="Season"),
            alt.Tooltip("metric_label:N", title="Metric"),
            alt.Tooltip("value:Q", title="Value"),
        ],
    )
    .transform_filter(metric_select)
    .add_params(metric_select)
    .properties(
        width=720,
        height=300,
        title="Chart 2. The dead-ball low point in the early 2000s did not last",
    )
    .configure(**base_config)
)


# Chart 3: era comparison for 3PA/game and 3P%
era_select = alt.selection_point(
    fields=["era"],
    bind=alt.binding_select(options=sorted(league["era"].unique()), name="Focus era: "),
    value="Modern spacing era",
)

chart3_a = (
    alt.Chart(league)
    .mark_circle(size=90, color="#7c3aed")
    .encode(
        x=alt.X("fg3a_pg:Q", title="3PA per game"),
        y=alt.Y("fg3_pct_display:Q", title="3-point percentage"),
        tooltip=[
            alt.Tooltip("season:N", title="Season"),
            alt.Tooltip("fg3a_pg:Q", title="3PA/game"),
            alt.Tooltip("fg3_pct_display:Q", title="3P%"),
            alt.Tooltip("era:N", title="Era"),
        ],
        opacity=alt.condition(era_select, alt.value(1), alt.value(0.18)),
    )
    .add_params(era_select)
)

chart3_b = (
    alt.Chart(league)
    .mark_line(color="#c084fc", strokeDash=[5, 5])
    .encode(
        x="fg3a_pg:Q",
        y="fg3_pct_display:Q",
        detail="era:N",
    )
    .transform_filter(era_select)
)

chart3 = (chart3_a + chart3_b).properties(
    width=720,
    height=300,
    title="Chart 3. Teams kept shooting more threes even when accuracy stayed fairly stable",
).configure(**base_config)


# Chart 4: position shift
chart4 = (
    alt.Chart(position_data)
    .mark_bar()
    .encode(
        x=alt.X("position:N", sort=["Point Guard", "Shooting Guard", "Small Forward", "Power Forward", "Center"], title="Position"),
        y=alt.Y("fg3a_pg:Q", title="Approx. three-point attempts per game"),
        color=alt.Color(
            "era:N",
            scale=alt.Scale(domain=["1990s", "2010s", "2020s"], range=["#c7d2fe", "#60a5fa", "#1d4ed8"]),
            title="Era",
        ),
        xOffset="era:N",
        tooltip=[
            alt.Tooltip("era:N", title="Era"),
            alt.Tooltip("position:N", title="Position"),
            alt.Tooltip("fg3a_pg:Q", title="3PA/game"),
        ],
    )
    .properties(
        width=720,
        height=300,
        title="Chart 4. The job description of every position moved outward",
    )
    .configure(**base_config)
)


# -----------------------------
# HTML output
# -----------------------------
def embed_chart(chart: alt.Chart, div_id: str) -> str:
    spec = chart.to_json(indent=None)
    return f"""
    <div id=\"{div_id}\" class=\"chart\"></div>
    <script>
    const spec_{div_id} = {spec};
    vegaEmbed('#{div_id}', spec_{div_id}, {{actions: false}});
    </script>
    """


html = f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>How the NBA Changed Its Game</title>
  <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
  <style>
    body {{
      font-family: Arial, Helvetica, sans-serif;
      margin: 0;
      background: #fafafa;
      color: #222;
      line-height: 1.6;
    }}
    .page {{
      max-width: 850px;
      margin: 0 auto;
      padding: 32px 20px 60px 20px;
      background: white;
    }}
    .kicker {{
      color: #666;
      text-transform: uppercase;
      font-size: 12px;
      letter-spacing: 0.08em;
      margin-bottom: 10px;
    }}
    h1 {{
      font-size: 36px;
      line-height: 1.15;
      margin: 0 0 10px 0;
    }}
    .dek {{
      font-size: 18px;
      color: #444;
      margin-bottom: 18px;
    }}
    .byline {{
      font-size: 14px;
      color: #666;
      padding-bottom: 18px;
      border-bottom: 1px solid #e5e5e5;
      margin-bottom: 24px;
    }}
    .note {{
      background: #f3f4f6;
      border-left: 4px solid #2563eb;
      padding: 12px 14px;
      margin: 20px 0 28px 0;
      font-size: 15px;
    }}
    h2 {{
      margin-top: 34px;
      margin-bottom: 8px;
      font-size: 24px;
    }}
    p {{
      margin-top: 0;
      margin-bottom: 14px;
    }}
    .chart {{
      margin: 16px 0 24px 0;
    }}
    .small {{
      color: #666;
      font-size: 14px;
    }}
    ul {{
      padding-left: 20px;
    }}
    .refs li {{
      margin-bottom: 10px;
    }}
    .footer {{
      margin-top: 40px;
      padding-top: 20px;
      border-top: 1px solid #e5e5e5;
      color: #666;
      font-size: 14px;
    }}
    a {{
      color: #1d4ed8;
    }}
  </style>
</head>
<body>
  <div class="page">
    <div class="kicker">SI 649 · Narrative Visualization Draft</div>
    <h1>How the NBA Changed Its Game</h1>
    <div class="dek">
      The modern NBA did not appear overnight. Rule changes opened the perimeter,
      and then analytics and roster design turned that opening into a new style of basketball.
    </div>
    <div class="byline">
      By Mustada A-Ogaili, Ali Al-Ogaili, Mohammad Farhat, and Lamonte Nunn
    </div>

    <div class="note">
      <strong>Audience:</strong> This project is written for readers who know the basics of basketball
      but may not follow advanced stats closely. Our goal is to explain <em>why</em> the game changed,
      not just show that more threes are being taken.
    </div>

    <h2>What makes this project different</h2>
    <p>
      Sports visualizations often stop at a familiar conclusion: teams shoot more threes than they used to.
      We want to push one step further. Our article argues that the style shift happened because the league
      changed what kinds of offense were rewarded. Rule changes made it easier to attack from the perimeter,
      and later, analytics made those shots easier to justify and teach.
    </p>
    <p>
      To keep the project manageable, we are starting with league-level data that we can verify quickly.
      If time allows, we can add a few player- or team-level examples later, but the main narrative already
      works with the data in this draft.
    </p>

    <h2>1) The three-point line was added in 1979, but teams were slow to fully use it</h2>
    <p>
      The first chart shows the long rise of the three-point shot. For years the line was part of the court,
      but not yet the center of offense. The big jumps come later, especially after teams started treating the
      three as a normal part of half-court offense instead of a specialty shot.
    </p>
    {embed_chart(chart1, "chart1")}
    <p class="small">
      This chart uses league averages from Basketball-Reference. The labels mark a few historical checkpoints,
      but our larger point is that adoption was gradual and then suddenly accelerated.
    </p>

    <h2>2) The early 2000s were a low point for pace and scoring</h2>
    <p>
      The second chart focuses on the slow, low-scoring stretch in the early 2000s. Instead of saying one single
      rule changed everything, we are using this section to show that style is partly shaped by incentives.
      Once the league became friendlier to perimeter offense, the game opened up again.
    </p>
    {embed_chart(chart2, "chart2")}
    <p class="small">
      Use the radio button above the chart to switch between points per game and pace.
      This keeps the interaction simple and readable.
    </p>

    <h2>3) Accuracy stayed fairly steady, but volume kept climbing</h2>
    <p>
      One reason the modern game feels so different is that teams did not wait for three-point percentage to explode.
      Instead, they kept increasing volume. That is part of the analytics story: even a similar percentage can become
      more valuable if the shot is worth an extra point and creates more spacing.
    </p>
    {embed_chart(chart3, "chart3")}
    <p class="small">
      This view lets the reader focus on one broad era at a time.
    </p>

    <h2>4) Positions became more flexible</h2>
    <p>
      Our last chart is a supporting comparison. It is not the main proof of the article, but it helps connect the
      earlier league trends to something readers can picture on the court. If every position is expected to shoot and
      move in space, then the old position labels start to matter less.
    </p>
    {embed_chart(chart4, "chart4")}
    <p class="small">
      These position values are rough era-level comparison values for the draft. In the final version,
      we can either keep this as a broad illustration or replace it with a cleaner sourced positional table.
    </p>

    <h2>Conclusion</h2>
    <p>
      The easiest way to describe the modern NBA is to say that players just got smarter and started shooting more threes.
      But that explanation is incomplete. The game changed because rules, strategy, and player development all pushed in the
      same direction. The result was not just more threes. It was a different idea of what good offense looks like.
    </p>

    <h2>Works cited / source list</h2>
    <ul class="refs">
      <li>
        Basketball-Reference. <em>NBA League Averages - Per Game</em>.
        <a href="https://www.basketball-reference.com/leagues/NBA_stats_per_game.html">https://www.basketball-reference.com/leagues/NBA_stats_per_game.html</a>
      </li>
      <li>
        Basketball-Reference. <em>NBA League Averages - Advanced Stats</em>.
        <a href="https://www.basketball-reference.com/leagues/NBA_stats_advanced.html">https://www.basketball-reference.com/leagues/NBA_stats_advanced.html</a>
      </li>
      <li>
        NBA.com. <em>This Day in History: Oct. 12 - The first 3-point field goal</em>.
        <a href="https://www.nba.com/news/this-day-in-history-oct-12-the-first-3-point-field-goal">https://www.nba.com/news/this-day-in-history-oct-12-the-first-3-point-field-goal</a>
      </li>
      <li>
        NBA Video Rulebook. <em>Handcheck</em>.
        <a href="https://videorulebook.nba.com/rule/handcheck/">https://videorulebook.nba.com/rule/handcheck/</a>
      </li>
      <li>
        Skinner, Brian. 2012. <em>The Problem of Shot Selection in Basketball</em>.
        <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC3266291/">https://pmc.ncbi.nlm.nih.gov/articles/PMC3266291/</a>
      </li>
      <li>
        Zając, T. et al. 2023. <em>Long-Term Trends in Shooting Performance in the NBA</em>.
        <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC9915101/">https://pmc.ncbi.nlm.nih.gov/articles/PMC9915101/</a>
      </li>
    </ul>

    <div class="footer">
      Draft built in one Python file with Altair. Intended for GitHub Pages as a single HTML page.
    </div>
  </div>
</body>
</html>
"""

out_path = Path("index.html")
out_path.write_text(textwrap.dedent(html), encoding="utf-8")
print(f"Wrote {out_path.resolve()}")
