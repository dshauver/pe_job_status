#!/usr/local/bin/python3

# Can enable debug output by uncommenting:
#import logging
#logging.basicConfig(level=logging.DEBUG)

#Import required libraries
import sys
import datetime
import time
import requests
import urllib3
import urllib.parse
import numpy
import json
import csv

#For enhancements to output to files in various formats.
#import pathlib
#import socket
#import tabulate


#Set up some defaults.  Using ALL CAPS for variables
ORCH_HOST = "https://puppet:8143" #host:port for orchestrator API
JOBS_ENDPOINT = "orchestrator/v1/jobs/" #jobs endpoint 
INVENTORY_ENDPOINT = "orchestrator/v1/inventory" #inventory endpoint for inventory detilas
PE_TOKEN = None #Variable to store PE Token
JOB_ID = None #Variable to store Job ID
JOBS_URI = None #Full uri for Jobs endpoint ; will build later
JOB_URI = None #URI for specific job ; will build later
OUTPUT = "json" #Where should the results go?  Defaults to json file & console

job_status = [] #array for job status from JOBS_URI
job_data = [] #array for dictionary from job_status
node_status = [] #array for per-node job data from JOB_URI
node_data = [] #array for dictionary from node_status
job_duration = [] #array for node job duration data
start_delay = [] #array for node start delay data
results_dict = {} #dictionary for results FIXME

job_start_time = None #Datestamp for overall job start time
node_start_time = None #Datestamp for per-node job start time

#FIXME Complete input validation and usage message
#Get JOB_ID from first CLI argument
try:
  sys.argv[1]
except:
  sys.exit("Usage: python3 job_setup.py JOBID OUTPUT(optional)")
else:
  JOB_ID = sys.argv[1]

#Get Ouput option from first CLI argument, or accept default
try:
  sys.argv[2]
except:
  print("No output specificied ; defaulting to JSON file")
else:
  OUTPUT = sys.argv[2]
  
#Supress warnings about insecure requests.  Using self-signed certs in my environment
#and don't want to see the warnings any more
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Grab the token from the file "token" in the same directory as the script
with open('token', 'r') as file:
	PE_TOKEN = file.read().replace('\n', '')

#Build the job URI from the variables above ; this is in case we ever need to list all jobs,
#plus it servers as a basis for the specific job in which we're interested
JOBS_URI = urllib.parse.urljoin(ORCH_HOST, JOBS_ENDPOINT)

#Build the URI for the specific job we want to know about
JOB_URI = urllib.parse.urljoin(JOBS_URI, JOB_ID)

#Query the API for Data.  Returns JSON
job_status = requests.get(JOB_URI, verify=False, headers={"X-Authentication": PE_TOKEN})
#print(json.dumps(job_status.json(), indent=2)) #print statement for inspecting JSON

#Status of 200 is success ; check for that before proceeding
#If succcesful, convert the JSON results to python dictionary ; otherwise exit with an error code.
if job_status.status_code == 200:
  job_data = job_status.json()
else:
  sys.exit("\"request.get(",JOB_URI,", verify=False, headers={\"X-Authentication\": <TOKEN>)\" returned status code:", job_status.status_code)

#Add the specific data points we want to return to the results array
results_dict["Job ID"] = job_data["name"]
for k in ['created_timestamp','finished_timestamp','duration','node_count']:
  results_dict[k] = job_data[k]
results_dict["nodes_finished"] = job_data["node_states"]["finished"]

#results.append( #Add data to results array
  #[
    #job_data["node_count"], #Total number of nodes on which job is run
    #job_data["node_states"]["finished"], #Total number of jobs completed successfully 
    #job_data["node_count"] - job_data["node_states"]["finished"], #Total number of jobs not completed successfully,
    #round(
      #100 * (job_data["node_states"]["finished"] / job_data["node_count"]) #Percent of per-node jobs successfully completed
    #)
  #]
#)

#FIXME Report on # of nodes NOT connected at time of job launch

#Default Puppet report time stamps are in this format: 2021-07-23T16:18:18Z
#convert the start time for the job into a datestamp for calculations later
job_start_time = time.mktime(datetime.datetime.strptime(job_data["created_timestamp"], "%Y-%m-%dT%XZ").timetuple())

#The URI for the node-specific results for job is included in the output from the jobs endpoint
#referencing that data element here to get the node-specific data.
#Go get the per-node details.  returns JSON.
node_status = requests.get(job_data["nodes"]["id"], verify=False, headers={"X-Authentication": PE_TOKEN})

#print(json.dumps(node_status.json(), indent=2)) #print statement for inspecting JSON

#Status of 200 is success ; check for that before proceeding
#If succcesful, convert the JSON results to python dictionary ; otherwise exit with an error code.
if node_status.status_code == 200:
  node_data = node_status.json()
else:
  sys.exit("\"request.get(",job_data["nodes"]["id"],", verify=False, headers={\"X-Authentication\": <TOKEN>)\" returned status code:", node_status.status_code)

#Iterate through the nodes, and for each succesful run:
#Extract the job duration into an array
#Compute the per-node job start delay
#Jobs that didn't finish successfully may have UNDEF or bad job duration, so do not add those to the computation
for i in node_data["items"]:
    if i["state"] == "finished": #Check for successful completion
      job_duration.append(i["duration"]) #Add duraction to array
      node_start_time = time.mktime(datetime.datetime.strptime(i["start_timestamp"], "%Y-%m-%dT%XZ").timetuple()) #convert to datestamp
      start_delay.append(node_start_time - job_start_time) #Add delay between job and node start time to array

#Add percentiles for difference between overall job start time and node job start time to results
results_dict["start_percentile"] = {}
for i in [90,50,10] :
  results_dict["start_percentile"][i] = numpy.percentile(start_delay, i) 

#Add precentile scores for per-node job duration to results.  
results_dict["job_duration"] = {}
for i in [90,50,10] :
  results_dict["job_duration"][i] = numpy.percentile(job_duration, i) 

#Add per-node job data to results
results_dict["nodes"] = {}
for i in node_data["items"]:
  nodename = i["name"]
  results_dict["nodes"][nodename] = {}
  for k in ["start_timestamp","finish_timestamp","duration","state"]:
    results_dict["nodes"][nodename][k] = i[k]  
    
if OUTPUT == "console": #if OUTPUT = console, ONLY print to console
  print (json.dumps(results_dict, indent = 2))
elif OUTPUT == "all": #if OUTPUT = all, write to file and console
  print (json.dumps(results_dict, indent = 2))
  json_out = open(("JOB_" + JOB_ID + ".json"), "w")
  json_out.write(json.dumps(results_dict, indent = 2))
  json_out.close()
elif OUTPUT == "json": #Write JSON to file
  json_out = open(("JOB_" + JOB_ID + ".json"), "w")
  json_out.write(json.dumps(results_dict, indent = 2))
  json_out.close()
#elif OUTPUT == "csv": #write CSV to file
  #FIXME add CSV output to file
  #csv_out = open(("JOB_" + JOB_ID + ".csv"), "w")
  #csv_write = csv.DictWriter(csv_out, results_dict.keys())
  #csv_write.writeheader()
  #csv_write.writerow(results_dict)
  #csv_out.close()