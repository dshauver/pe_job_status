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
#Don't think this will be required ; commenting out for now likely deleting later.

#Build Inventory URI from variables
#inventory_uri = urllib.parse.urljoin(ORCH_HOST, INVENTORY_ENDPOINT)

#Query URI from inventory - returns JSON
#node_inventory = requests.get(inventory_uri, verify=False,
#  headers={"X-Authentication": PE_TOKEN}
#)

#FIXME Need to get job_id from CLI or from user input
JOB_ID = "1701"

#Build the job URI from tje variables above ; this is in case we ever need to list all jobs,
#plus it servers as a basis for the specific job in which we're interested
jobs_uri = urllib.parse.urljoin(ORCH_HOST, JOBS_ENDPOINT)

#Build the URI for the specific job we want to know about
job_uri = urllib.parse.urljoin(jobs_uri, JOB_ID)

#Query the API for Data.  Returns JSON
job_status = requests.get(job_uri, verify=False,
  headers={"X-Authentication": PE_TOKEN}
)

#Convert the JSON to a python dictionary so we can do interesting things with it
job_data = job_status.json()

#The URI for the node-specific results for job is included in the output from the jobs endpoint
#referencing that data element here to get the node-specific data.
#Go get the per-node details, againg returning JSON
node_status = requests.get(job_data["nodes"]["id"], verify=False,
  headers={"X-Authentication": PE_TOKEN}
)

#Convert the JSON to a python dictionary so we can do interesting things with it
node_data = node_status.json()

#Print Statements for Debugging.
#print (node_inventory.text)
#print (job_status.text)
#print (node_status.text)
#print (json.dumps(job_data, indent=2))
#print (json.dumps(node_data, indent=2))

print("Job ID", JOB_ID, sep=',')
print("Start_time", job_data["created_timestamp"], sep=',')
print("Start_time", job_data["finished_timestamp"], sep=',')
print("Duration", job_data["duration"], sep=',')

print("Nodename,Start Time,Finish Time,Duration(sec),Status")
for i in node_data["items"]:
  print(i["name"],i["start_timestamp"],i["finish_timestamp"],i["duration"],i["state"], sep=',')