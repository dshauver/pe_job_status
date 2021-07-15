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
#Specify the Puppet Enterprise Primary server hosting the Orchestrator endpoint
ORCH_HOST = "https://puppet:8143"
#Specify the Orchestrator endpoint port
#Specify the jobs endpoint for job details
JOBS_ENDPOINT = "orchestrator/v1/jobs/"
#Specify the inventory endpoint for inventory detilas
INVENTORY_ENDPOINT = "orchestrator/v1/inventory"
PE_TOKEN = None
JOB_ID = None

#The following commands are used to access the relevant details for a particular job from the CLI.  
#Note that the orch inventory endpoint will ONLY list nodes that are currently connected. 
#curl --insecure --header "X-Authentication: <TOKEN>" "https://puppet:8143/orchestrator/v1/inventory"

#This gives the basic details of a job, in this case #1701
#curl --insecure --header "X-Authentication: <TOKEN>" "https://puppet:8143/orchestrator/v1/jobs/1701"

#The nodes detail endpoint for a job will list all nodes targeted by the job, regardless of connection status.
#Compare this with the output from inventory to determine which nodes were not online when the job was launched
#curl --insecure --header "X-Authentication: <TOKEN>" "https://puppet:8143/orchestrator/v1/jobs/1701/nodes"

#First pass at grabbing node inventory. Note that verify=False is not recommended, but is required for
#self-signed certs without additional effort

#Grab the token from the file "token" in the same directory as the script
with open('token', 'r') as file:
	PE_TOKEN = file.read().replace('\n', '')

node_inventory = requests.get("https://puppet:8143/orchestrator/v1/inventory", verify=False,
  headers={"X-Authentication": PE_TOKEN}
)

#FIXME Need to get job_id from CLI or from user input
JOB_ID = "1701"

#FIXME Build the URL from variables rather than specify it here.
job_status = requests.get("https://puppet:8143/orchestrator/v1/jobs/1701", verify=False,
  headers={"X-Authentication": PE_TOKEN}
)

#FIXME Build the URL from variables rather than specify it here.
# Should be https://PRIMARY_HOST:ORCH_PORT/JOBS_ENDPOINT/JOB_ID/nodes
node_status = requests.get("https://puppet:8143/orchestrator/v1/jobs/1701/nodes", verify=False,
  headers={"X-Authentication": PE_TOKEN}
)

print (node_inventory.text)
print (job_status.text)
print (node_status.text)