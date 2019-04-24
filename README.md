# lebus
lebus (light emiting bus whatever the name is dumb shut up!!) is a simple Python library for pulling real-time schedules from Translink (Vancouver BC) and displaying them on a 32x32 LED matrix.  There's not a heck of a lot of features yet, but maybe that will change in the author's interest.  

## Helpful links

This project was inspired by the [MLB LED Scoreboard](https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard) project, which has a lot of useful information that is related to setting up these sorts of devices.

I used the Python bindings of the [RPI RGB LED Matrix](https://github.com/hzeller/rpi-rgb-led-matrix/) library. Again, lots of good things to dig into there.

Finally, Adafruit (where I purchased all the hardware from) has a [pretty good setup guide](https://learn.adafruit.com/adafruit-rgb-matrix-plus-real-time-clock-hat-for-raspberry-pi) as well.


## Hardware list
Adventurous folks can choose their own path, but here's what I used to build by transit clock.  All my parts were ordered from [Adafruit](https://www.adafruit.com/), and I've included the price I paid at the time (Jun 30, 2018 in USD).

  1. [Adafruit RGB Matrix Bonnet for Raspberry Pi](https://www.adafruit.com/product/3211) [ID:3211] = $14.95
  2. [32x32 RGB LED Matrix Panel - 6mm pitch](https://www.adafruit.com/product/1484) [ID:1484] = $39.95
  3. [MicroUSB to 5.5/2.1mm DC Barrel Jack Adapter](https://www.adafruit.com/product/2789) [ID:2789] = $1.95
  4. [2-Way 2.1mm DC Barrel Jack Splitter Squid](https://www.adafruit.com/product/1351) [ID:1351] = $2.95
  5. [Raspberry Pi Zero WH (Zero W with Headers)](https://www.adafruit.com/product/3708) [ID:3708] = $14.00
  6. [5V 10A switching power supply](https://www.adafruit.com/product/658) [ID:658] = $25.00
  7. [8GB SD Card w/ Stretch Lite](https://www.adafruit.com/product/2820) [ID:2820] = $9.95

Note that you it's a good idea to be able to write to the Micro SD card from your normal computer if something goes wrong.  In that case, a [USB MicroSD Card Reader](https://www.adafruit.com/product/939) ($5.95) is a good investment.

These parts from to about $110 USD before shipping and taxes.  For a Canadian like me, once you've factored in duty, shipping, taxes, and the dollar, it came out to just under $200 CAD.  

So, uh, make sure this is something that's **really** going to change your life, 'cause your phone probably does this for free.

Note that I obviously used a Raspberry Pi to power this, but I don't see why you couldn't do the same with an Arduino board.


## Translink interface
You need to register at https://developer.translink.ca/ to receive an API key (it will display in the top-right corner after you log-in, and will be a jumble of 20 characters or so).

From there, you need to identify bus numbers and stops that you want to display by pulling the number from the stop itself, or searching for the stop at translink.ca.

e.g. The UBC 99 B-Line stop is at stop #61935, so the 3-digit bus number is `099` and the stop is `61935`.

Note that a stop can have multiple buses, but at this point in time you need to specify each individually (i.e. the software 'as is' will not parse the list of buses for a particular stop -- you also need to supply a specific bus number as well).


## Software setup

1. Bake Raspbian Stretch Lite (November 2018) to SD card via Apple Pi Baker
2. Setup Pi as desired  `> sudo raspi-config`
   1. Connect to wifi network
   2. Enable SSH server
   3. Change password
   4. Change hostname
3. Disable built-in audio (see https://www.instructables.com/id/Disable-the-Built-in-Sound-Card-of-Raspberry-Pi/)
   1. `cd /etc/modprobe.d`
   2. `sudo vi alsa-blacklist.conf`
   3. Enter the line `blacklist snd_bcm2835`
   4. Ctrl-x to save the file
   5. Reboot with `sudo reboot`
4. Setup rgb-matrix software (see: https://learn.adafruit.com/adafruit-rgb-matrix-plus-real-time-clock-hat-for-raspberry-pi/driving-matrices)
   1. `curl https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/rgb-matrix.sh >rgb-matrix.sh`
   2. `sudo bash rgb-matrix.sh`
   3. Continue? `y`
   4. Interface board type: `1. (Adafruit RGB Matrix Bonnet)`
   5. Quality vs Convenience: `2. Convenience (sound on, no soldering)`
   6. Continue? `y`
   7. Reboot? `y`
5. Edit lib Makefile to point to adafruit-hat
   1. `cd ~/rpi-rgb-led-matrix/lib`
   2. `nano Makefile`
   3. Edit line 27 to be `ARDWARE_DESC?=adafruit-hat`
   4. Ctrl-x to save Makefile
   5. `make clean`
   6. `make`
6. Test demos in `~/rpi-rgb-led-matrix/examples-api-use`
   1. `sudo ./demo -D [0-11] (ok!)`
7. Compiling led-image-viewer in `~/rpi-rgb-led-matrix/utils` (see: https://github.com/hzeller/rpi-rgb-led-matrix/tree/master/utils)
   1. `sudo apt-get update`
   2. `sudo apt-get install libgraphicsmagick++-dev libwebp-dev -y`
   3. `HARDWARE_DESC=adafruit-hat make`
8. Install python, pillow, and python bindings:
   1. `sudo apt-get update && sudo apt-get install python2.7-dev python-pillow -y`
   2. `make build-python`
   3. `sudo make install-python`
9. Install git and pull this code:
   1. `sudo apt-get install git`
   2. `git clone https://github.com/johnlarusic/lebus.git`
   3. `git config credential.helper store`
1. Set the date/time: `sudo dpkg-reconfigure tzdata`
2. Edit `lebus_config.json` to your liking (see more details below)
   1. You are going to need to supply the API key Translink provided you in the `api_key` field
   2. Of course, the stops you wish to display need to be provided in the `stops` array
   3. Finally, if you want this to actually send to the LED display, you'll need to flip `send_to_led` to `true`
3. Set up a systemd service to run on startup:
   1. Edit `lebus.service` as desired
   2. `sudo cp lebus.service /lib/systemd/system/`
   3. `sudo systemctl enable lebus.service`
   4. `sudo service lebus start [restart|stop]`
4. (optional) Use crontab to start and stop the LED from running between midnight at 6am:
   1. `crontab -e` and then enter the following lines:
   2. `0 0 * * * sudo service lebus stop`
   3. `0 6 * * * sudo service lebus start`


## Configuration file notes
Boo JSON for lack of comments, so here's an annotated version of the config file...

```

    "api_key": "123456789ABCDEFGHIJK",  // API key supplied by Translink 
    "refresh_rate": 5,                  // Rate at which you want everyting to refresh (in seconds)
    "send_to_led": false,               // Set to true to have the LED receive the generated image 
    "send_to_file": true,               // Set to true to have the generated image saved to disk
    "default_image_file": "sched.png",  // If send_to_file is true, this is the filename written
    "led": {
        "width": 32,                    // LED width
        "height": 32,                   // LED height
        "brightness": 20                // LED brightness value (100 is the max)
    },
    "data_pull_timer": {                // As you have max 1,000 data pulls/day, adjust these to stay in your limit!
        "min": 2,                       // Minimum time between new data pulls for stop
        "max": 5                        // Maximum time between new data pulls for stop
    },
    "stops": [
        {
            "bus": "099",               // 3-digit bus identifier
            "stop": "61935",            // 5-digit stop identifier
            "display_bus": "99",         // Display name
            "display_direction": "E",   // Display direciton (N,S,E,W)
            "tminus_warning": 8,        // Times at/below this value will be coloured 'warnings'
            "tminus_critical": 3        // Times at/below this value will be coloured 'critical'
        },
        ...
        // One definition per bus and stop
    ],
    "colours": {                        // All in RGBA format!
        "background": "0,0,0,255",      // Graphic background
        "text": "255,255,255",          // Text for stop displays/direction
        "time_default": "77,148,255",   // Default stop time text colour
        "time_warning": "255,255,153",  // Colour 'warning' times
        "time_critical": "255,204,204"  // Colour for 'critical' times
    }
}

```

## Future ideas
Time/interest permitting, the author would like to explore...

1. Add an actual clock display
2. Pull weather data and display that at the same time.
3. Add in Blue Jays baseball scores 'cause why not.


## License (MIT License)
Copyright (c) 2019 Johnny LaRusic

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
