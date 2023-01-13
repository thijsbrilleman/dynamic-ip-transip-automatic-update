#!/usr/bin/env python3

# Updates a Transip DNS record to current public ip address.
# Handy for those who run a home server on a dynamic address.
# Use crontab to execute, say, every 5 minutes.

import transip # pip install python-transip
import requests
import sys
import socket
import os
import datetime

LOGIN = 'transip_username'
DOMAIN = 'example.com'
RECORD_TYPE = 'A'
RECORD_NAME = '@'
LOGFILE = 'location/of/logfile/to/write/to'
PRIVATE_KEY = '''-----BEGIN PRIVATE KEY-----
.... (paste api key here) ....
-----END PRIVATE KEY-----
'''

# Generate temporary api token and connect to API in one go
client = transip.TransIP(login=LOGIN, private_key=PRIVATE_KEY, global_key=True)

# Exit if IP is invalid
try:
    response = requests.get('https://api.ipify.org')
    response.raise_for_status()
    actual_ip = response.text.strip()
    socket.inet_aton(actual_ip)
except requests.exceptions.RequestException as e:
    print("Could not find global ip address: ", e)
except socket.error as e:
    print("Invalid ip address: ", e)

# Get the current DNS records
domain = client.domains.get(DOMAIN)
dns_records = domain.dns.list()

# Update record if necessary
updated = False
for dns_record in dns_records:
    if dns_record.type == RECORD_TYPE and dns_record.name == RECORD_NAME and dns_record.content != actual_ip:
        incorrect_ip = dns_record.content
        message = "Updating incorrect A-record from {} to {}".format(incorrect_ip, actual_ip)
        dns_record.content = actual_ip
        domain.dns.replace(dns_records)
        # Print message to console and to file
        print(message)
        with open(LOGFILE, "a") as f:
            f.write("[" + str(datetime.datetime.now()) + "] " + message + "\n")
        exit()

print("Current {}-record ip ({}) is already correct and thus not updated.".format(RECORD_TYPE, actual_ip))
