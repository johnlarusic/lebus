from . import *
from datetime import datetime


def print_schedule(stops):
    now = datetime.now()

    print "Schedule as of {}".format(now)

    for stop in stops:
        print stop.route,

        if len(stop.next) > 0:
            for s in stop.next:
                val = "now"

                if s > now:
                    delta = (s - now).seconds / 60
                    if delta > 0:
                        val = delta

                print " {}".format(val),
            print
        else:
            print " ?"
    print
