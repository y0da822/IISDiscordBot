#!/usr/bin/env python3
import time
import glob
import os
import configparser
from datetime import datetime
import pytz
from tzlocal import get_localzone
from discord import Webhook, RequestsWebhookAdapter

# config parser - to read from config file
parser = configparser.ConfigParser()
parser.read('iisdiscordbot.config')

# connect to log file path and find latest file
log_file_path = parser.get('iis', 'logfilepath')
log_file_path_files = glob.glob(log_file_path + "/*.log")
log_file_latest = max(log_file_path_files, key=os.path.getctime)
log_file = open(log_file_latest, "r")

# get local timezone for utc conversion
local_tz = get_localzone()

# connect to discord webhook
webhook = Webhook.partial(parser.get('discord', 'webhookid'), parser.get('discord', 'webhooktoken'), \
                          adapter=RequestsWebhookAdapter())

while 1:
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
            print(
                log_file_latest + ": " + user + " has downloaded " + file_downloaded + " on " + dt_downloaded.strftime("%Y-%m-%d %H:%M:%S %Z%z") + " from " + file_path)
            webhook.send(user + " has downloaded " + file_path + " on " + dt_downloaded.strftime("%Y-%m-%d %H:%M:%S %Z%z"))
        elif "STOR" in log_line:
            log_line_list = log_line.split()
            user = log_line_list[3]
            file_uploaded = log_line_list[7].replace("+", " ")
            dt_str = log_line_list[0] + " " + log_line_list[1]
            datetime_obj = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            dt_uploaded = datetime_obj.replace(tzinfo=pytz.utc).astimezone(local_tz)
            file_path = log_line_list[len(log_line_list) - 1].replace("+", " ")
            print(
                log_file_latest + ": " + user + " has uploaded " + file_uploaded + " on " + dt_uploaded.strftime("%Y-%m-%d %H:%M:%S %Z%z") + " from " + file_path)
            webhook.send(user + " has uploaded " + file_path + " on " + dt_uploaded.strftime("%Y-%m-%d %H:%M:%S %Z%z"))