Relish Signal Strength
===

This is a quick script which helps when finding the best location for a 4G router (specifically the Gemtek 4G router provided by Relish). It polls an unauthenticated informational endpoint which the router provides, parses the data, and displays the key statistics. Unfortunately it's still quite a manual chore to test many locations.

Dependencies
===

The project is Python 3 (tested on 3.5), and requires the `requests` package (`npm install requests`).

Usage
===

Start polling with:

    python main.py

This will poll every half-second (the router appears to update values approximately once per second), and print key values to the terminal (stdout). You can stop it at any time using the normal Ctrl+C key combination. It expects to find the router at its default address: http://192.168.15.1/

Description of output
---

The most important values for signal strength are the CINR0/1 values (Carrier to Interface+Noise Ratio, measured in dBm - decibel-milliwatts). The router contains 2 antenna, with CINR0 corresponding to the first and CINR1 the second.

Due to the use of MIMO (Multiple-Input and Multiple-Output) in the 4G standard, it is best to get **both** CINR0 and CINR1 as high as possible (i.e. balanced). For example, a result of 12/14 is likely to be better than 3/17. This can usually be accomplished by turning the router slightly.

A third column is also provided; "Combination". This has no real meaning, but can be used as a quick reference when checking multiple locations, as it varies less with rotation. It represents the euclidean distance from 0,0 to CINR0,CINR1 after accounting for the logarithmic scale (the full formula is equivalent to `log10(sqrt((10^CINR0)^2+(10^CINR1)^2))`). It's a formula I've pulled from thin air and somebody with more knowledge of signal processing could certainly produce a better formula for this task.

The combination value roughly corresponds to the signal strength displayed on the router. It has the advantage of being more fine-grained and visible even when the router's display isn't, but will have slightly more latency in its updates.

The final 3 columns are rolling window averages of the first 3 columns. Currently they are the average of the past 10 samples (5 seconds).

Tips for finding a good signal
---

* Use a long extension lead so that you can move the router around without switching it off and on repeatedly (it takes a long time to switch on and find a signal)
* Start this polling script and keep it running (you can stop and restart it whenever you want to, but you don't need to)
* Good candidate locations are places with a good line-of-sight out of the building
* Signal strength varies dramatically with small changes to location (even 5cm can make a big difference sometimes), and can vary with time too (e.g. due to the weather)
* Large containers of water (e.g. You) can have a big impact on the signal, so you may need to try standing in more than 1 location
* It's a good idea to check at least 4 directions (e.g. N/E/S/W) in each location. Checking 8 is better.
* For each candidate location & direction, wait for 5 seconds then check the averaged Comb value (far-right column)
* Once you have found the best location (largest Comb value in a practical location), turn the router until CINR0 and CINR1 are reasonably well balanced
