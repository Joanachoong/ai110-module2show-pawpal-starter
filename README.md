# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.


### UML Diagram (Refined)

```mermaid
classDiagram
direction TB

class Owner {
    - id: int
    - name: string
    - email: string
    - _pets: List~Pet~
    + getId(): int
    + getName(): string
    + getEmail(): string
    + add_pet(pet: Pet): void
    + get_pets(): List~Pet~
    + get_pet_ids(): List~int~
}

class Pet {
    - id: int
    - name: string
    - species: string
    - age: int
    - owner_id: int
    - _tasks: List~Task~
    + getId(): int
    + getName(): string
    + getSpecies(): string
    + getAge(): int
    + getOwnerId(): int
    + get_tasks(): List~Task~
}

class Task {
    - id: int
    - description: string
    - task_type: string
    - due_time: datetime
    - duration_mins: int
    - pet_name: string
    - owner_name: string
    - priority: string ~~low / medium / high~~
    - owner_id: int
    - pet_id: int
    - is_completed: bool
    + mark_complete(): void
    + is_today(): bool
}

class Scheduler {
    - _tasks: List~Task~
    - _next_task_id: int
    - _pet_registry: dict
    + add_task(task: Task, owner: Owner, pet: Pet): void
    + get_task(task_id: int): Task
    + edit_task(task_id: int, kwargs): bool
    + remove_task(task_id: int): bool
    + schedule_walk(pet, owner, due_time, duration_mins, priority): Task
    + get_all_tasks(owner: Owner): List~Task~
    + get_today_tasks(owner: Owner): List~Task~
    + generate_schedule(owner: Owner, available_mins: int): List~Task~
}

class Dashboard {
    - session_state: dict
    + render_owner_details(owner: Owner): void
    + render_pet_details(pet: Pet): void
    + render_schedule_details(tasks: List~Task~): void
    + run(): void
}

Owner "1" *--> "0..*" Pet : owns
Pet "1" *--> "0..*" Task : associated with
Scheduler "1" o-- "0..*" Task : manages

Dashboard ..> Owner : displays details
Dashboard ..> Pet : displays details
Dashboard ..> Scheduler : requests schedule
Dashboard ..> Task : renders tasks

```

Notes:
- **Owner** controls pet membership via `add_pet()` and provides read access through `get_pets()` / `get_pet_ids()`.
- **Pet** passively holds its associated tasks (`_tasks`); tasks are added/removed only by Scheduler.
- **Task** now carries a `pet_id` field so Scheduler can sync removals back to the correct Pet.
- **Scheduler** is the sole authority for task mutation (`add_task`, `remove_task`, `edit_task`). It retrieves tasks by walking `owner.get_pets()` → `pet.get_tasks()`, not from a flat internal list.


### Smarter Scheduling


The scheduling system now goes beyond a simple task list and actively manages daily planning, recurring care routines. It automatically creates today’s recurring tasks, prioritizes what matters most, and builds a realistic plan based on available time.


1. Recurring task templates

Supports daily and weekday-based weekly recurrences.
Generates concrete task instances from templates instead of reusing the template itself.
Prevents duplicate generated instances for the same template/day pair.

2. Automatic “today” task preparation

When loading today’s tasks, recurring items due today are generated first.
The list includes actionable tasks due today and overdue tasks.
Completed tasks and template-only records are excluded from the actionable view.

3. Smarter prioritization logic

Scheduling ranks tasks in this order:
Overdue tasks first
Completion status 
Pet name
This flow ensure pet owner's know what task needs to be resolve first and which pet's task is incomplete if owner have multiple pet in the house.

4. Completion-aware recurrence flow

Completing a recurring instance pre-spawns the next expected occurrence.
Undoing completion reverses that change and removes the pre-spawned future instance (if still incomplete).
Keeps recurring plans consistent with user actions.

### Testing PawPal+ 

To run the test case: `python -m pytest`

Confidence lebel : 4/5

1. Basic task lifecycle behavior  
Verifies core functionality like marking a task complete and successfully adding tasks to a pet.

2. Conflict and duplicate detection  
Checks that true duplicates are rejected, including normalized descriptions (case/whitespace), while valid non-duplicates are accepted.

3. Sorting correctness for scheduling  
Validates that schedule output follows expected ordering rules, including overdue precedence and tie-breaking for same-time tasks.

4. Recurrence logic on completion  
Confirms daily recurring behavior by ensuring completing a generated daily task creates the next day’s task exactly once.

5. Query/filter and empty-state reliability  
Covers task filtering by date, completion status, and pet name (including case-insensitive matching), plus edge behavior when a pet has no tasks.