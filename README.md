# job_status

Working to provide Job Status details based on a specific customer request. The customer is looking to report on meeting an SLA that 99% of nodes managed by Puppet Enterprise can have action taken against them within 60 minutes.  This essentially means using a task, plan, or agent run to make a change on a set of managed nodes.  The task, plan, or agent run should launch on all connected nodes within 60 minutes.  This effort is to build reporting for the request.

Success Metric:

- Initiate change - via task, plan, or agent run - to 99% of nodes within 60 minutes
- This means to start a job, not complete a job
- nodes == nodes connected to PE at time of job launch

Need reporting that shows :

- number of nodes connected v not connected @ job start time
- Job launch time
- Individual node kickoff times
- node completion times

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