from . import *

import threading
import time
from datetime import datetime
import urllib2
import json


class Schedule(object):

    data_pulls = 0

    def __init__(self, route, stop, label, dir, min_time, max_time, api_key):
        self.lock = threading.Lock()
        self.route = route
        self.stop = stop
        self.label = label
        self.dir = dir
        self.min_time = min_time
        self.max_time = max_time
        self.api_key = api_key
        self.next = []

    def update(self):
        Schedule.data_pulls += 1
        self.log(
            "Pull updated data (pull #{} for day".format(Schedule.data_pulls))
        next_buses = self.get_next_times()

        self.log("Waiting for lock")
        self.lock.acquire()

        try:
            self.log("Acquired lock")
            self.next = next_buses
        finally:
            self.log("Released lock")
            self.lock.release()

    def pull_data(self):
        url_call = 'http://api.translink.ca/rttiapi/v1/stops/{}/estimates?routeNo={}&apikey={}&count=3'
        url = url_call.format(self.stop, self.route, self.api_key)
        self.log("Download data from {}".format(url))

        try:
            req = urllib2.Request(url, None, headers={
                'Content-type': 'application/json', 'Accept': 'application/json'})
            response = urllib2.urlopen(req)
            json_list = json.loads(response.read())
            if len(json_list) > 0:
                return json_list[0]

        except urllib2.HTTPError as ex:
            self.log("Error pulling new bus data from URL '{}', error code '{}'".format(url, ex.code), True)
        except Exception as ex:
            self.log("Error pulling new bus data from URL '{}'".format(url), True)

        return None

    def get_next_times(self):
        data = None
        try:
            data = self.pull_data()
        except Exception as ex:
            self.log("Error pulling new bus data for route '{}', stop '{}'".format(self.route, self.stop), True)

        next_buses = list()

        if data is not None:
            for s in data['Schedules']:
                try:
                    time_string = s['ExpectedLeaveTime']
                    if not s['CancelledStop']:
                        time_obj = self.parse_date_time(time_string)
                        self.log("Expected leave time: {} (parse of {})".format(
                            time_obj, time_string))
                        next_buses.append(time_obj)
                except Exception as ex:
                    self.log("Error parsing bus data '{}'".format(
                        time_string), True)

        return next_buses

    def parse_date_time(self, date_string, add_leading_zero=False):
        date = ""
        time = date_string

        if " " in date_string:
            time, date = date_string.split(" ")

        # Parse the time portion
        hour, min_xm = time.split(":")
        hour = int(hour)
        minute = int(min_xm[:-2])
        xm = min_xm[-2:]
        if xm == "pm" and hour < 12:
            hour += 12
        elif xm == "am" and hour == 12:
            hour = 0

        # Parse the date portion
        now = datetime.now()
        year = now.year
        month = now.month
        day = now.day

        if now.hour > hour:
            day += 1

        if date != "":
            year, month, day = date.split("-")
            year = int(year)
            month = int(month)
            day = int(day)

        dt = datetime(year, month, day, hour, minute)

        return dt

    def log(self, message, error_ind=False):
        if error_ind:
            LOG_HELPER.error("UPDATE %s/%s: %s",
                             self.route, self.stop, message)
        else:
            LOG_HELPER.debug("UPDATE %s/%s: %s",
                             self.route, self.stop, message)
