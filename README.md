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
    + getId(): int
    + getName(): string
    + getEmail(): string
}

class Pet {
    - id: int
    - name: string
    - species: string
    - age: int
    - owner_id: int
    + getId(): int
    + getName(): string
    + getSpecies(): string
    + getAge(): int
    + getOwnerId(): int
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
    - is_completed: bool
    + mark_complete(): void
    + is_today(): bool
}

class Scheduler {
    - pets: List~Pet~
    - tasks: List~Task~
    - next_task_id: int
    + add_pet(pet: Pet): void
    + add_task(task: Task, owner: Owner): void
    + get_task(task_id: int): Task
    + edit_task(task_id: int, kwargs): bool
    + remove_task(task_id: int): bool
    + schedule_walk(pet, owner, due_time, duration_mins, priority): Task
    + get_today_tasks(owner: Owner): List~Task~
    + generate_schedule(owner: Owner, available_mins: int): List~Task~
    + get_all_pets(): List~Pet~
}

class Dashboard {
    - session_state: dict
    + render_owner_details(owner: Owner): void
    + render_pet_details(pet: Pet): void
    + render_schedule_details(tasks: List~Task~): void
    + run(): void
}

Owner "1" *-- "0..*" Pet : owns
Scheduler "1" o-- "0..*" Pet : manages
Scheduler "1" o-- "0..*" Task : manages

Dashboard ..> Owner : displays details
Dashboard ..> Pet : displays details
Dashboard ..> Scheduler : requests schedule
Dashboard ..> Task : renders tasks

```

Notes:
- The original `Schedule` and `Scheduler` responsibilities are merged into `Scheduler`.
- `Dashboard` is a presentation layer that displays owner, pet, and task schedule details.
- `Scheduler` is the orchestration layer that manages pets/tasks and returns daily plans.
