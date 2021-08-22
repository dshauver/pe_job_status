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

#For enhancements to output to files in various formats.
#import pathlib
#import socket
#import tabulate

#FIXME Add input validation and usage message

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
results = [] #array for specific data to return
results_dict = {} #dictionary for results FIXME

job_start_time = None #Datestamp for overall job start time
node_start_time = None #Datestamp for per-node job start time

#Get JOB_ID from first CLI argument
JOB_ID = sys.argv[1]

#Get Ouput option from first CLI argument
if sys.argv[2]:
  OUTPUT = sys.argv[2]
else:
  print("Not output specificied ; defaulting to JSON file")

#Supress warnings about insecure requests.  Using self-signed certs in my environment
#and don't want to see the errors any more
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
results.append( #Headers for data
    [
      "Job ID", #Unique ID of the job
      "Start Time", #Start time of the job
      "Completed Time", #Compelted time of the job
      "Duration" # Overall duration of the job.
    ]
)

results_dict["Job ID"] = job_data["name"]
for k in ['created_timestamp','finished_timestamp','duration','node_count']:
  results_dict[k] = job_data[k]
results_dict["nodes_finished"] = job_data["node_states"]["finished"]

results.append( #Add data to results array
  [
    JOB_ID, #Job ID
    job_data["created_timestamp"], #Start time of the job
    job_data["finished_timestamp"], #Completed time of the job
    job_data["duration"] # Overall duration of the job
  ]
)

results.append([""]) #Blank row for separation

results.append( #Header for data
  [
    "Connected Nodes", #Total number of nodes on which job is run
    "Successful Jobs", #Total number of jobs completed successfully
    "Unsuccessful Jobs", #Total number of jobs not completed successfully
    "Percent Success" #Percent of per-node jobs successfully completed
  ]
)
results.append( #Add data to results array
  [
    job_data["node_count"], #Total number of nodes on which job is run
    job_data["node_states"]["finished"], #Total number of jobs completed successfully 
    job_data["node_count"] - job_data["node_states"]["finished"], #Total number of jobs not completed successfully,
    round(
      100 * (job_data["node_states"]["finished"] / job_data["node_count"]) #Percent of per-node jobs successfully completed
    )
  ]
)
results.append([""]) #Blank row for separation

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

results_dict["start_percentile"] = {}
for i in [90,50,10] :
  results_dict["start_percentile"][i] = numpy.percentile(start_delay, i) 

#Add percentiles for difference between overall job start time and node job start time to results
results.append( #Header row
  [
    "Node Start Delay Percentiles", #Perentile for node delays
    "Delay", #Delay between overall job start time and per-node job start time
    "Units" #Units for data
  ]
)
results.append( #90th percentile data
  [
    "90th", #Percentile
    numpy.percentile(start_delay, 90), #Calculate 90th percentile and add data to array
    "Seconds" #Units
  ]
)
results.append( #50th percentile data
  [
    "50th", #Percentile
    numpy.percentile(start_delay, 50), #Calculate 50th percentile and add data to array
    "Seconds" #Calculate 50th percentile and add data to array
  ]
)
results.append( #10th percentile data
  [
    "10th", #Percentile
    numpy.percentile(start_delay, 10), #Calculate 10th percentile and add data to array
    "Seconds" #Units
  ]
)
results.append([""]) #Blank row for separation

results_dict["job_duration"] = {}
for i in [90,50,10] :
  results_dict["job_duration"][i] = numpy.percentile(job_duration, i) 

#Add precentile scores for per-node job duration to results.  
results.append( #Header Row
  [
    "Node Job Duration Percentile", #Percentiles for per-node job duration data
    "Duration", #Duration of per-node jobs
    "Units" #Units for data
  ]
)
results.append( #90th percentile data
  [
    "90th", #Percentile
    numpy.percentile(job_duration, 90), #Calculate 90th percentile and add data to array
    "Seconds" #Units
  ]
)
results.append( #50th pecentile data
  [
    "50th", #Percentil3
    numpy.percentile(job_duration, 50), #Calculate 50th percentile and add data to array 
    "Seconds" #Units
  ]  
)
results.append( #10th percentile data
  [
    "10th", #Percentile
    numpy.percentile(job_duration, 10), #Calculate 10th percentile and add data to array
    "Seconds" #Units
  ]
)
results.append([""]) #Blank row for separation

#Add the per-node data fields to the results.
results.append( #Header Row
  [
    "Nodename", #Name of node
    "Start Time", #Start time for node's job run
    "Finish Time", #Finish time for node's job run
    "Duration(sec)", #Duration of node's job run
    "Status" #Completion status of node's job run
  ]
)
results_dict["nodes"] = {}
for i in node_data["items"]:
  nodename = i["name"]
  results_dict["nodes"][nodename] = {}
  for k in ["start_timestamp","finish_timestamp","duration","state"]:
    results_dict["nodes"][nodename][k] = i[k]  
    

for i in node_data["items"]: #Iterate through nodes
  results.append( # Add per-node data to results array
    [
      i["name"], #Name of node
      i["start_timestamp"], #Start time for node's job run
      i["finish_timestamp"], #Finish time for node's job run
      i["duration"], #Duration of node's job run
      i["state"] #Completion status of node's job run
    ]
  )

if OUTPUT == "console": #if OUTPUT = console, ONLY print to console
  print (json.dumps(results_dict, indent = 2))
elif OUTPUT == "all": #if OUTPUT = all, write to file and console
  print (json.dumps(results_dict, indent = 2))
  #FIXME add writing to JSON, CSV files
  print ("FIXME ouput to file.csv")
  print ("FIXME ouput to file.csv")
elif OUTPUT == "json": #Write JSON to file
  #FIXME add writing JSON to file
  print ("FIXME ouput to file.json")
elif OUTPUT == "csv": #write CSV to file
  #FIXME add CSV output to file
  print ("FIXME ouput to file.csv")

#print (tabulate.tabulate(results, tablefmt="grid")) #Print results to console as grid format table
#print (tabulate.tabulate(results, tablefmt="grid")) #Print results to console as grid format table