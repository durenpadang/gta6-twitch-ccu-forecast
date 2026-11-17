# gta6-twitch-ccu-forecast

Entry for the make.fun bounty "Forecast GTA VI's launch-day Twitch viewers hour by hour"
(`gta6-twitch-ccu-forecast-01`).

`main.py` (Python 3.13, standard library only) reads every `<id>.in` case in the input directory and
writes `<id>.out`, five quantiles (5%, 25%, 50%, 75%, 95%) for each of the hours 2..24 of the launch
day: an analog ensemble over the case's comparable launches, in log-ratio space against each launch's
own hour-1 print, per-hour empirical quantiles blended with a pooled standardised shape, smoothed
across neighbouring hours.

    MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py

Licensed under the MIT license (see `LICENSE`).