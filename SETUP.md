# Profile README

The animated profile is published at [github.com/Veeru19252/Veeru19252](https://github.com/Veeru19252/Veeru19252). GitHub displays it on the profile because the public repository name matches the username.

## Update

Run these commands from this directory to refresh the contribution data and regenerate all SVGs:

```sh
python3 scripts/fetch_contributions.py
python3 scripts/render_profile.py
```

Commit and push changes to `main`; the included workflow refreshes the contribution heatmap daily. The ASCII portrait is a monochrome rendering of the public GitHub avatar. Only the generated ASCII art is stored in this repository, not the source photo. To change the portrait, replace `ASCII_PORTRAIT` in `scripts/render_profile.py` and rerun the renderer.

The info card's role and stack are starter text; update the rows in `render_info_card()` in `scripts/render_profile.py` to match your current focus. The contribution fetcher reads GitHub's public contribution-calendar HTML and needs no personal access token. The workflow has `contents: write` permission to commit refreshed contribution data and the heatmap SVG.
