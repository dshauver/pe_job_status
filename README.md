# job_status.py

## Specification
A customer is looking to report on meeting an SLA that 99% of nodes managed by Puppet Enterprise can have action taken against them within 60 minutes.  This essentially means using a task, plan, or agent run to make a change on a set of managed nodes.  The task, plan, or agent run should launch on all connected nodes within 60 minutes.  This effort is to provide a reporting example leveraging Puppet APIs.  Python was chosen as the scripting language for the effort

Success Metric:

- Initiate change - via task, plan, or agent run - to 99% of nodes within 60 minutes
- This means to start a job, not complete a job
- nodes == nodes connected to PE at time of job launch

Need reporting that shows :

- number of nodes connected v not connected @ job start time (This is not done yet)
- Job launch time (Done)
- Individual node launch times (Done)
- node completion times (Done)

End desired state:

For JobID XXXX:

- 357 nodes were connected at the time of the job launch, and of those,
- 300 started running within `SLA` minutes of launching the job.
- 350 nodes completed successfully
- 7 nodes reported failures
- All jobs completed in ## minutes 
- An additional 44 nodes were not connected at the time the job was launched. 

Initial investigation shows that data will be required from these endpoints :

- curl --insecure --header "X-Authentication: <TOKEN>" "https://puppet:8143/orchestrator/v1/jobs/1701"
- curl --insecure --header "X-Authentication: <TOKEN>" "https://puppet:8143/orchestrator/v1/jobs/1701/nodes

## Execution
The script expects Python3 with the following libraries

- sys
- datetime
- time
- requests
- urllib3
- urllib.parse
- numpy
- tabulate
- logging (If debugging is necessary)
- pathlib (Future enhacements)
- socket (Future Enhancements)
- json (Future Enhancements)

It is written to expect a file, called `token`, in the same directory as the script itself.  The script was developed with token with full administrative access.  Using a more limited token is a future effort.

Sample script execution for Job # 1730:

$ python3 job_status.py 1730

Current version of script returns results similar to this:
~~~~
{
  "Job ID": "1730",
  "created_timestamp": "2021-07-23T16:18:17Z",
  "finished_timestamp": "2021-07-23T16:22:25Z",
  "duration": 247.913,
  "node_count": 13,
  "nodes_finished": 11,
  "start_percentile": {
    "90": 86.0,
    "50": 0.0,
    "10": 0.0
  },
  "job_duration": {
    "90": 209.493,
    "50": 118.065,
    "10": 65.061
  },
  "nodes": {
    "node_01.org.com": {
      "start_timestamp": "2021-07-23T16:19:15Z",
      "finish_timestamp": "2021-07-23T16:21:15Z",
      "duration": 119.103,
      "state": "finished"
    },
    "node_02.org.com": {
      "start_timestamp": "2021-07-23T16:18:17Z",
      "finish_timestamp": "2021-07-23T16:19:43Z",
      "duration": 85.563,
      "state": "finished"
    },
    "node_03.org.com": {
      "start_timestamp": "2021-07-23T16:18:17Z",
      "finish_timestamp": "2021-07-23T16:20:26Z",
      "duration": 128.384,
      "state": "finished"
    },
    "node_04.org.com": {
      "start_timestamp": "2021-07-23T16:18:17Z",
      "finish_timestamp": "2021-07-23T16:21:47Z",
      "duration": 209.493,
      "state": "finished"
    },
    "node_05.org.com": {
      "start_timestamp": "2021-07-23T16:18:17Z",
      "finish_timestamp": "2021-07-23T16:22:25Z",
      "duration": 247.594,
      "state": "finished"
    },
    "node_06.org.com": {
      "start_timestamp": null,
      "finish_timestamp": "2021-07-23T16:18:18Z",
      "duration": null,
      "state": "errored"
    },
    "node_07.org.com": {
      "start_timestamp": "2021-07-23T16:18:18Z",
      "finish_timestamp": "2021-07-23T16:19:23Z",
      "duration": 65.061,
      "state": "finished"
    },
    "node_08.org.com": {
      "start_timestamp": "2021-07-23T16:18:17Z",
      "finish_timestamp": "2021-07-23T16:20:16Z",
      "duration": 118.797,
      "state": "failed"
    },
    "node_09.org.com": {
      "start_timestamp": "2021-07-23T16:18:17Z",
      "finish_timestamp": "2021-07-23T16:20:16Z",
      "duration": 118.852,
      "state": "finished"
    },
    "node_10.org.com": {
      "start_timestamp": "2021-07-23T16:19:23Z",
      "finish_timestamp": "2021-07-23T16:21:21Z",
      "duration": 118.065,
      "state": "finished"
    },
    "node_11.org.com": {
      "start_timestamp": "2021-07-23T16:18:17Z",
      "finish_timestamp": "2021-07-23T16:19:15Z",
      "duration": 58.065,
      "state": "finished"
    },
    "node_11.org.com": {
      "start_timestamp": "2021-07-23T16:20:16Z",
      "finish_timestamp": "2021-07-23T16:21:31Z",
      "duration": 75.19,
      "state": "finished"
    },
    "node_12.org.com": {
      "start_timestamp": "2021-07-23T16:19:43Z",
      "finish_timestamp": "2021-07-23T16:21:31Z",
      "duration": 107.753,
      "state": "finished"
    }
  }
}
~~~~