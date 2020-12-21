
### overview

![framework](../img/fedvision.png)

There are two `role` associated in `FedVision`:

1. coordinator
    
2. Party


`Coordinator` is an independent role responsible for handling job publish and
distribute subtasks to proper parties that have subscribed to the `coordinator`.
Usually, the `coordinator` must be started before any party can subscribe to it.
The `party` will post the job of the specified `job_type` to the coordinator and wait for `proposal_waiting_time` seconds.
While waiting, all `party` subscribed to this `job_type` will received a message,
and then decide whether to participate or not. After the waiting time is over, the `coordinator` selects a group of `party`
as a participants in this job.

`Party` is an independent role that publishes or subscribe jobs. usually,
It has a `Cluster` to process assigned tasks, and a `submit service` to process work requests from `Users`,
a `coordinator clients publish jobs to `Coordinator` or subscribe jobs from "Coordinator" and, a `master` to mixes them up.

