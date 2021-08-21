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
- 300 started running within <SLA> minutes of launching the job.
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
+------------------------------+----------------------+----------------------+---------------+----------+
| Job ID                       | Start Time           | Completed Time       | Duration      |          |
+------------------------------+----------------------+----------------------+---------------+----------+
| 1730                         | 2021-07-23T16:18:17Z | 2021-07-23T16:22:25Z | 247.913       |          |
+------------------------------+----------------------+----------------------+---------------+----------+
|                              |                      |                      |               |          |
+------------------------------+----------------------+----------------------+---------------+----------+
| Node Start Delay Statistics  | Delay                | Units                |               |          |
+------------------------------+----------------------+----------------------+---------------+----------+
| 90th Percentile              | 86.0                 | Seconds              |               |          |
+------------------------------+----------------------+----------------------+---------------+----------+
| 50th Percentile              | 0.0                  | Seconds              |               |          |
+------------------------------+----------------------+----------------------+---------------+----------+
| 10th Percentile              | 0.0                  | Seconds              |               |          |
+------------------------------+----------------------+----------------------+---------------+----------+
|                              |                      |                      |               |          |
+------------------------------+----------------------+----------------------+---------------+----------+
| Node Job Duration Statistics | Duration             | Units                |               |          |
+------------------------------+----------------------+----------------------+---------------+----------+
| 90th Percentile              | 209.493              | Seconds              |               |          |
+------------------------------+----------------------+----------------------+---------------+----------+
| 50th Percentile              | 118.065              | Seconds              |               |          |
+------------------------------+----------------------+----------------------+---------------+----------+
| 10th Percentile              | 65.061               | Seconds              |               |          |
+------------------------------+----------------------+----------------------+---------------+----------+
|                              |                      |                      |               |          |
+------------------------------+----------------------+----------------------+---------------+----------+
| Nodename                     | Start Time           | Finish Time          | Duration(sec) | Status   |
+------------------------------+----------------------+----------------------+---------------+----------+
| node_01.some.org             | 2021-07-23T16:19:15Z | 2021-07-23T16:21:15Z | 119.103       | finished |
+------------------------------+----------------------+----------------------+---------------+----------+
| node_02.some.org             | 2021-07-23T16:18:17Z | 2021-07-23T16:19:43Z | 85.563        | finished |
+------------------------------+----------------------+----------------------+---------------+----------+
| node_03.some.org             | 2021-07-23T16:18:17Z | 2021-07-23T16:20:26Z | 128.384       | finished |
+------------------------------+----------------------+----------------------+---------------+----------+
| node_04.some.org             | 2021-07-23T16:18:17Z | 2021-07-23T16:21:47Z | 209.493       | finished |
+------------------------------+----------------------+----------------------+---------------+----------+
| node_05.some.org             | 2021-07-23T16:18:17Z | 2021-07-23T16:22:25Z | 247.594       | finished |
+------------------------------+----------------------+----------------------+---------------+----------+
| node_06.some.org             |                      | 2021-07-23T16:18:18Z |               | errored  |
+------------------------------+----------------------+----------------------+---------------+----------+
| node_07.some.org             | 2021-07-23T16:18:18Z | 2021-07-23T16:19:23Z | 65.061        | finished |
+------------------------------+----------------------+----------------------+---------------+----------+
| node_08.some.org             | 2021-07-23T16:18:17Z | 2021-07-23T16:20:16Z | 118.797       | failed   |
+------------------------------+----------------------+----------------------+---------------+----------+
| node_09.some.org             | 2021-07-23T16:18:17Z | 2021-07-23T16:20:16Z | 118.852       | finished |
+------------------------------+----------------------+----------------------+---------------+----------+
| node_10.some.org             | 2021-07-23T16:19:23Z | 2021-07-23T16:21:21Z | 118.065       | finished |
+------------------------------+----------------------+----------------------+---------------+----------+
| node_11.some.org             | 2021-07-23T16:18:17Z | 2021-07-23T16:19:15Z | 58.065        | finished |
+------------------------------+----------------------+----------------------+---------------+----------+
| node_12.some.org             | 2021-07-23T16:20:16Z | 2021-07-23T16:21:31Z | 75.19         | finished |
+------------------------------+----------------------+----------------------+---------------+----------+
| node_14.some.org             | 2021-07-23T16:19:43Z | 2021-07-23T16:21:31Z | 107.753       | finished |
+------------------------------+----------------------+----------------------+---------------+----------+
~~~~