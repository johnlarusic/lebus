from . import *
from datetime import datetime


def timer_debug(s, msg):
    LOG_HELPER.debug("%s/%s: %s", s.route, s.stop, msg)


def timer(s, min_time=2, max_time=5):
    while True:
        s.update()

        if len(s.next) == 0:
            timer_debug(s, "No scheduled stops are available")
            sleep_min = max_time
        else:
            now = datetime.now()
            next_bus = s.next[0]

            timer_debug(s, "Next bus is at {}".format(next_bus))

            if next_bus < now:
                sleep_min = min_time
            else:
                delta = next_bus - now
                delta_min = delta.seconds / 60 - 2

                if delta_min > max_time:
                    sleep_min = max_time
                elif delta_min <= min_time:
                    sleep_min = min_time
                else:
                    sleep_min = delta_min

        timer_debug(s, "Sleeping {} minutes".format(sleep_min))
        time.sleep(sleep_min * 60)
