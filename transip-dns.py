#!/usr/bin/env python3

# Updates a Transip DNS record to current public ip address.
# Handy for those who run a home server on a dynamic address.
# Use crontab to execute, say, every 5 minutes.

import transip # pip install python-transip
import requests
import socket
import logging
import json
import ipaddress

LOGIN = 'transip_username'
DOMAIN = 'example.com'
RECORD_NAME = '@'
LOGFILE = 'location/of/logfile/to/write/to'
LOGLEVEL = 'ERROR'  # Used levels are: "INFO" and "ERROR"
PRIVATE_KEY = '''-----BEGIN PRIVATE KEY-----
.... (paste api key here) ....
-----END PRIVATE KEY-----
'''


# setup the logging
LOGLEVEL = logging.getLevelNamesMapping()[LOGLEVEL]
logging.basicConfig(filename=LOGFILE, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', level=LOGLEVEL)

# First lets get our own IP adress(es)

# Exit if IP4 is invalid
try:
    response = requests.get('https://api.ipify.org?format=json')
    response.raise_for_status()
    actual4 = json.loads(response.text)
    ipaddress.ip_address(actual4['ip'])
except requests.exceptions.RequestException as e:
    logging.error(f"Could not find global ip4 address: {e}")
except socket.error as e:
    logging.error(f"Invalid ip4 address: {e}")

# Exit if IP6 is invalid
try:
    response = requests.get('https://api64.ipify.org?format=json')
    response.raise_for_status()
    actual6 = json.loads(response.text)
    ipaddress.ip_address(actual6['ip'])
except requests.exceptions.RequestException as e:
    logging.error(f"Could not find global ip6 address: {e}")
except ValueError as e:
    logging.error(f"Invalid ip6 address: {e}")

# Generate temporary api token and connect to API in one go
client = transip.TransIP(login=LOGIN, private_key=PRIVATE_KEY, global_key=True)

# Get the current DNS records
domain = client.domains.get(DOMAIN)
dns_records = domain.dns.list()

# Update records if necessary
for dns_record in dns_records:
    if isinstance(ipaddress.ip_address(actual4['ip']), ipaddress.IPv4Address):
        if dns_record.type == 'A' and dns_record.name == RECORD_NAME and dns_record.content != actual4['ip']:
            incorrect_ip = dns_record.content
            message = "Updating incorrect A-record from {} to {}".format(incorrect_ip, actual4['ip'])
            dns_record.content = actual4['ip']
            domain.dns.replace(dns_records)
            logging.info(message)
        elif dns_record.type == 'A' and dns_record.name == RECORD_NAME and dns_record.content == actual4['ip']:
            logging.info(f"Current A-record ip4 ({actual4['ip']}) is already correct and thus not updated.")

    if isinstance(ipaddress.ip_address(actual6['ip']), ipaddress.IPv6Address):
        if dns_record.type == 'AAAA' and dns_record.name == RECORD_NAME and dns_record.content != actual6['ip']:
            incorrect_ip = dns_record.content
            message = "Updating incorrect AAAA-record from {} to {}".format(incorrect_ip, actual6['ip'])
            dns_record.content = actual6['ip']
            domain.dns.replace(dns_records)
            logging.info(message)
        elif dns_record.type == 'AAAA' and dns_record.name == RECORD_NAME and dns_record.content == actual6['ip']:
            logging.info(f"Current AAAA-record ip6 ({actual6['ip']}) is already correct and thus not updated.")

