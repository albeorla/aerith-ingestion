---- MODULE TodoistIngestion ----
EXTENDS Integers, Sequences, TLC, FiniteSets

\* Constants for task attributes
CONSTANTS 
    MAX_TASKS,          \* Maximum number of tasks that can be processed
    MAX_RETRIES,        \* Maximum number of retry attempts for API calls
    VALID_PRIORITIES,   \* Set of valid priority values
    VALID_STATUSES     \* Set of valid status values

\* Variables representing system state
VARIABLES 
    todoist_tasks,      \* Tasks fetched from Todoist API
    stored_tasks,       \* Tasks stored in our system
    ingestion_lock,     \* Boolean indicating if ingestion is in progress
    retry_count,        \* Current retry count for API operations
    processing_state    \* Current state of task processing

\* Type definitions
TaskId == 1..MAX_TASKS
Status == VALID_STATUSES
Priority == VALID_PRIORITIES

\* Type invariant
TypeInvariant ==
    /\ todoist_tasks \subseteq [id: TaskId, status: Status, priority: Priority]
    /\ stored_tasks \subseteq [id: TaskId, status: Status, priority: Priority]
    /\ ingestion_lock \in BOOLEAN
    /\ retry_count \in 0..MAX_RETRIES
    /\ processing_state \in {"idle", "fetching", "processing", "storing", "error"}

\* Initial state
Init ==
    /\ todoist_tasks = {}
    /\ stored_tasks = {}
    /\ ingestion_lock = FALSE
    /\ retry_count = 0
    /\ processing_state = "idle"

\* Actions
StartIngestion ==
    /\ processing_state = "idle"
    /\ ingestion_lock = FALSE
    /\ ingestion_lock' = TRUE
    /\ processing_state' = "fetching"
    /\ UNCHANGED <<todoist_tasks, stored_tasks, retry_count>>

FetchTasks ==
    /\ processing_state = "fetching"
    /\ ingestion_lock = TRUE
    /\ \/ /\ Cardinality(todoist_tasks) < MAX_TASKS
          /\ \E task \in [id: TaskId, status: Status, priority: Priority]:
                /\ task.id \notin {t.id: t \in todoist_tasks}
                /\ todoist_tasks' = todoist_tasks \union {task}
          /\ processing_state' = "processing"
       \/ /\ todoist_tasks = {}
          /\ retry_count < MAX_RETRIES
          /\ retry_count' = retry_count + 1
          /\ UNCHANGED <<todoist_tasks, processing_state>>
    /\ UNCHANGED <<stored_tasks, ingestion_lock>>

ProcessTasks ==
    /\ processing_state = "processing"
    /\ ingestion_lock = TRUE
    /\ todoist_tasks # {}
    /\ processing_state' = "storing"
    /\ UNCHANGED <<todoist_tasks, stored_tasks, ingestion_lock, retry_count>>

StoreTasks ==
    /\ processing_state = "storing"
    /\ ingestion_lock = TRUE
    /\ \E task \in todoist_tasks:
        /\ task.id \notin {t.id: t \in stored_tasks}
        /\ stored_tasks' = stored_tasks \union {task}
    /\ IF \A task \in todoist_tasks: task.id \in {t.id: t \in stored_tasks'}
       THEN processing_state' = "idle"
       ELSE UNCHANGED processing_state
    /\ UNCHANGED <<todoist_tasks, ingestion_lock, retry_count>>

EndIngestion ==
    /\ processing_state = "idle"
    /\ ingestion_lock = TRUE
    /\ ingestion_lock' = FALSE
    /\ retry_count' = 0
    /\ UNCHANGED <<todoist_tasks, stored_tasks, processing_state>>

HandleError ==
    /\ processing_state = "error"
    /\ ingestion_lock = TRUE
    /\ processing_state' = "idle"
    /\ ingestion_lock' = FALSE
    /\ retry_count' = 0
    /\ UNCHANGED <<todoist_tasks, stored_tasks>>

\* Next state relation
Next ==
    \/ StartIngestion
    \/ FetchTasks
    \/ ProcessTasks
    \/ StoreTasks
    \/ EndIngestion
    \/ HandleError

\* Invariants
TaskNeverLost ==
    [](\A task \in todoist_tasks:
        <>(task.id \in {t.id: t \in stored_tasks}))

TaskNeverDuplicated ==
    [](\A t1, t2 \in stored_tasks:
        t1.id = t2.id => t1 = t2)

DataConsistency ==
    [](\A task \in stored_tasks:
        /\ task.id \in TaskId
        /\ task.status \in Status
        /\ task.priority \in Priority)

\* Temporal properties
Liveness ==
    /\ []<>(processing_state = "idle")
    /\ []<>(ingestion_lock = FALSE)
    /\ [](processing_state = "fetching" ~> <>(processing_state = "processing" \/ processing_state = "error"))
    /\ [](processing_state = "processing" ~> <>(processing_state = "storing" \/ processing_state = "error"))

\* Complete specification
Spec ==
    /\ Init
    /\ [][Next]_<<todoist_tasks, stored_tasks, ingestion_lock, retry_count, processing_state>>
    /\ WF_vars(Next)

\* Properties to check
THEOREM Spec => [](TypeInvariant /\ TaskNeverLost /\ TaskNeverDuplicated /\ DataConsistency)
==== 