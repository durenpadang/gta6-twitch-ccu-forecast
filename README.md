# gta6-twitch-ccu-forecast

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/durenpadang/gta6-twitch-ccu-forecast/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/durenpadang/gta6-twitch-ccu-forecast/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

Entry for the [make.fun bounty](https://make.fun/bounty/gta6-twitch-ccu-forecast-01)
"Forecast GTA VI's launch-day Twitch viewers hour by hour" (`gta6-twitch-ccu-forecast-01`).

`main.py` (Python 3.13, standard library only) reads every `<id>.in` case in the input directory and
writes `<id>.out`: five quantiles (5%, 25%, 50%, 75%, 95%) for each of the hours 2..24 of the launch
day. It is an analog ensemble over the case's comparable launches, worked in log-ratio space against
each launch's own hour-1 print — per-hour empirical quantiles blended with a pooled standardised
shape, then smoothed across neighbouring hours.

    MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py

Licensed under the MIT license (see `LICENSE`).