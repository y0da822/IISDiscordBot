#!/usr/bin/env python3
# y0da822
import time
import glob
import os
import configparser
from datetime import datetime
import pytz
from tzlocal import get_localzone
from discord import Webhook, RequestsWebhookAdapter


# local log file function
def write_log(log_msg, file_name):
    print("In write_log function - " + file_name)

    with open(file_name, 'a') as log:
        log.write("{0},{1}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), str(log_msg)))


# create local log file
my_log_file = "LOG-" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".csv"
print("My log file is " + my_log_file)

# config parser - to read from config file
parser = configparser.ConfigParser()
parser.read('iisdiscordbot.config')

# connect to log file path and find latest file
log_file_path = parser.get('iis', 'logfilepath')
log_file_path_files = glob.glob(log_file_path + "/*.log")
log_file_latest = max(log_file_path_files, key=os.path.getctime)
log_file = open(log_file_latest, "r")
write_log("Opened IIS log file " + log_file.name)

# get local timezone for utc conversion
local_tz = get_localzone()
write_log("Getting local timezone for IIS log date/time conversion")

# connect to discord webhook
webhook = Webhook.partial(parser.get('discord', 'webhookid'), parser.get('discord', 'webhooktoken'), \
                          adapter=RequestsWebhookAdapter())
write_log("Connected to Discord webhook ID (" + parser.get('discord', 'webhookid') + ")")

while 1:
    # check for the latest log file each iteration
    log_file_latest = max(log_file_path_files, key=os.path.getctime)
    if log_file.name != log_file_latest:
        log_file.close()
        log_file = open(log_file_latest, "r")
        write_log("Log file has been rotated to new one " + log_file.name)
    where = log_file.tell()
    log_line = log_file.readline()
    if not log_line:
        time.sleep(1)
        log_file.seek(where)
    else:
        # if a file is downloaded
        if "RETR" in log_line:
            log_line_list = log_line.split()
            user = log_line_list[3]
            file_downloaded = log_line_list[7].replace("+", " ")
            dt_str = log_line_list[0] + " " + log_line_list[1]
            datetime_obj = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            dt_downloaded = datetime_obj.replace(tzinfo=pytz.utc).astimezone(local_tz)
            file_path = log_line_list[len(log_line_list) - 1].replace("+", " ")
            write_log(
                log_file_latest + ": " + user + " has downloaded " + file_downloaded + " on " + dt_downloaded.strftime(
                    "%Y-%m-%d %H:%M:%S %Z%z") + " from " + file_path)
            webhook.send(
                user + " has downloaded " + file_path + " on " + dt_downloaded.strftime("%Y-%m-%d %H:%M:%S %Z%z"))
        elif "STOR" in log_line:
            log_line_list = log_line.split()
            user = log_line_list[3]
            file_uploaded = log_line_list[7].replace("+", " ")
            dt_str = log_line_list[0] + " " + log_line_list[1]
            datetime_obj = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            dt_uploaded = datetime_obj.replace(tzinfo=pytz.utc).astimezone(local_tz)
            file_path = log_line_list[len(log_line_list) - 1].replace("+", " ")
            write_log(
                log_file_latest + ": " + user + " has uploaded " + file_uploaded + " on " + dt_uploaded.strftime(
                    "%Y-%m-%d %H:%M:%S %Z%z") + " from " + file_path)
            webhook.send(user + " has uploaded " + file_path + " on " + dt_uploaded.strftime("%Y-%m-%d %H:%M:%S %Z%z"))
