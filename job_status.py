#!/usr/local/bin/python3

# Can enable debug output by uncommenting:
#import logging
#logging.basicConfig(level=logging.DEBUG)

#Import required libraries
import sys
import socket
import json
import datetime
import time
import requests
import urllib.parse
import pathlib

#Set up some defaults.  Using ALL CAPS for variables
#Specify the host/port for orchestrator API
ORCH_HOST = "https://puppet:8143"
#Specify the jobs endpoint for job details
JOBS_ENDPOINT = "orchestrator/v1/jobs/"
#Specify the inventory endpoint for inventory detilas
INVENTORY_ENDPOINT = "orchestrator/v1/inventory"
PE_TOKEN = None
JOB_ID = None

#First pass at grabbing node inventory. Note that verify=False is not recommended, but is required for
#self-signed certs without additional effort

#Grab the token from the file "token" in the same directory as the script
with open('token', 'r') as file:
	PE_TOKEN = file.read().replace('\n', '')

#FIXME Need to think about this again - fine for small environments, likely breaks at scale.
#might work better to just parse results from node_status and report based on specific status
#inventory_uri = urllib.parse.urljoin(ORCH_HOST, INVENTORY_ENDPOINT)
#Don't think this will be required ; commenting out for now likely deleting later.
#node_inventory = requests.get("https://puppet:8143/orchestrator/v1/inventory", verify=False,
#node_inventory = requests.get(inventory_uri, verify=False,
#  headers={"X-Authentication": PE_TOKEN}
#)

#FIXME Need to get job_id from CLI or from user input
JOB_ID = "1704"

jobs_uri = urllib.parse.urljoin(ORCH_HOST, JOBS_ENDPOINT)
job_uri = urllib.parse.urljoin(jobs_uri, JOB_ID)
job_status = requests.get(job_uri, verify=False,
  headers={"X-Authentication": PE_TOKEN}
)

nodes_uri = job_uri + "/nodes" 
node_status = requests.get(nodes_uri, verify=False,
  headers={"X-Authentication": PE_TOKEN}
)

#Print Statements for Debugging.
#print (node_inventory.text)
print (job_status.text)
print (node_status.text)