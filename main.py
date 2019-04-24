import lebus
import logging
import threading
import time
import argparse
import os
import sys
import json

DEFAULT_IMG_FILE = "sched.png"

# Import configuration file
with open('lebus_config.json') as f:
    data = json.load(f)

p_api_key = data['api_key']
p_refresh_rate = data['refresh_rate']
p_send_to_led = data['send_to_led']
p_send_to_file = data['send_to_file']
p_default_image_file = data['default_image_file']
p_stops = data['stops']

p_led = data['led']
p_led_width = p_led['width']
p_led_height = p_led['height']
p_brightness = p_led['brightness']

p_timer = data['data_pull_timer']
p_min_time = p_timer['min']
p_max_time = p_timer['max']

p_colours = data['colours']
p_c_bg = p_colours['background']
p_c_text = p_colours['text']
p_c_t_default = p_colours['time_default']
p_c_t_warn = p_colours['time_warning']
p_c_t_crit = p_colours['time_critical']


# Setup logging
logger = logging.getLogger("lebus")
logging.getLogger("PIL").setLevel(logging.CRITICAL)
logger.info('Starting lebus!!!')


# Setup the schedules
stops = []
for s in p_stops:
    k = lebus.Schedule(s['bus'], s['stop'], s['display_bus'], s['display_direction'],
                       s['tminus_warning'], s['tminus_critical'], p_api_key)
    stops.append(k)

# Parse colours
c_bg = lebus.parse_colour_string(p_c_bg)
c_text = lebus.parse_colour_string(p_c_text)
c_t_default = lebus.parse_colour_string(p_c_t_default)
c_t_warn = lebus.parse_colour_string(p_c_t_warn)
c_t_crit = lebus.parse_colour_string(p_c_t_crit)

# Setup matrix
matrix = None
if p_send_to_led:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
    options = RGBMatrixOptions()
    options.rows = 32
    options.chain_length = 1
    options.parallel = 1
    options.brightness = p_brightness
    matrix = RGBMatrix(options=options)

# Start the scheduled timer pulls
for stop in stops:
    t = threading.Thread(target=lebus.timer, args=(stop, p_min_time, p_max_time, ))
    t.setDaemon(True)
    t.start()

# Print out the latest schedules every thirty seconds
img = None
orig_stops = stops[:]  # Make duplicate copy of list
while True:
    lebus.print_schedule(orig_stops)

    if p_send_to_file or p_send_to_led:
        img = lebus.graphic_schedule(stops, p_led_width, p_led_height, c_bg, c_text, c_t_default, c_t_warn, c_t_crit)

    if p_send_to_file:
        img.save(p_default_image_file)

    if p_send_to_led:
        matrix.SetImage(img.convert('RGB'))

    if(len(stops) > 2):
        stops.append(stops.pop(0))
    time.sleep(p_refresh_rate)
