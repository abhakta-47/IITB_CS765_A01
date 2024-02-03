# Architecture

## Event Simulation
### Class Event
- type: str, one of given enum
- created_at: timestamp
- actionable_at: timestamp
- action: fn pointer
- payload: fn arguments
- log_message: str

### Class Simulation
- clock
- event_queue: Queue<Event>
- def enqueue(event): 
    - add event to queue and sort by actionable_at
    - this can trigger more enqueue detect infinite recursion
- def dequeue():
    - once enqueue cascade stops dequeue event take action on the event
    - might trigger enqueue

## P2P network
### Peer/Node

### Transaction

### Block