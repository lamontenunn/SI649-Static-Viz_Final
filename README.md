# How the NBA Changed Its Game

SI 649 Narrative Visualization Project, Winter 2026.

By Mustada A-Ogaili, Ali Al-Ogaili, Mohammad Farhat, and Lamonte Nunn.

A data-driven article on how the NBA shifted from a post-heavy, mid-range game
into a perimeter- and efficiency-driven league between 1979-80 and 2023-24.
The story is delivered through four interactive Altair visualizations:

1. Rise of the three-point shot (volume vs. efficiency toggle)
2. Pace, scoring, and offensive rating over time (4-metric radio)
3. Where shots come from — the near-disappearance of the mid-range
4. Per-position 3-point attempts across four decades

## Project structure

```
.
├── nba_story.py          single build script: loads CSVs, renders index.html
├── index.html            generated narrative page (upload this to GitHub Pages)
├── data/
│   ├── league_seasons.csv      per-season league averages, 1979-80 → 2023-24
│   ├── shot_zones.csv          per-season shot-zone share of FGA, 1996-97+
│   └── position_shooting.csv   per-position 3PA/3P%/TS% by decade
└── README.md
```

## Build

```bash
pip install altair pandas
python nba_story.py
```

This regenerates `index.html` from the CSVs in `/data`.

## Data sources

All three CSVs were compiled from Basketball-Reference league pages:

- Per-game averages and three-point volume: <https://www.basketball-reference.com/leagues/NBA_stats_per_game.html>
- Advanced metrics (pace, ORtg, TS%, eFG%): <https://www.basketball-reference.com/leagues/NBA_stats_advanced.html>
- Shot-zone distribution and per-zone FG%: <https://www.basketball-reference.com/leagues/NBA_stats_shooting.html>

Shot-location tracking began in 1996-97, so `shot_zones.csv` starts there.
Pre-1997 seasons appear only in `league_seasons.csv`.

## Deployment

The page is a single static `index.html` with Vega-Lite loaded from a CDN,
so it can be hosted anywhere. To publish on GitHub Pages:

1. Push to the `main` branch.
2. Repo *Settings → Pages → Build and deployment → Deploy from a branch*.
3. Select `main` / root `/`.
4. GitHub will serve the page at `https://<user>.github.io/<repo>/`.

Verify the deployed page loads in an **incognito** browser window so the
page is tested without any cached auth or cookies.
