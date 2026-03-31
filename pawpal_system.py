from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import List, Optional
import streamlit as st

"""Add one-line docstrings across pawpal_system methods

- Added concise single-line docstrings to Owner, Pet, Task, Scheduler, and Dashboard methods
- Improved method-level documentation without changing behavior

"""

@dataclass
class Owner:
    id: int
    name: str
    email: str
    _pets: List[Pet] = field(default_factory=list)

    def getId(self) -> int:
        """Return the owner's unique ID."""
        return self.id

    def getName(self) -> str:
        """Return the owner's name."""
        return self.name

    def getEmail(self) -> str:
        """Return the owner's email address."""
        return self.email

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self._pets.append(pet)

    def get_pets(self) -> List[Pet]:
        """Return a copy of the owner's pets."""
        return list(self._pets)

    def get_pet_ids(self) -> List[int]:
        """Return IDs for all pets owned by this owner."""
        return [pet.getId() for pet in self._pets]


@dataclass
class Pet:
    id: int
    name: str
    species: str
    age: int
    owner_id: int
    _tasks: List[Task] = field(default_factory=list)

    def getId(self) -> int:
        """Return the pet's unique ID."""
        return self.id

    def getName(self) -> str:
        """Return the pet's name."""
        return self.name

    def getSpecies(self) -> str:
        """Return the pet's species."""
        return self.species

    def getAge(self) -> int:
        """Return the pet's age in years."""
        return self.age

    def getOwnerId(self) -> int:
        """Return the ID of the pet's owner."""
        return self.owner_id

    def get_tasks(self) -> List[Task]:
        """Return a copy of this pet's tasks."""
        return list(self._tasks)


@dataclass
class Task:
    id: int
    description: str
    task_type: str
    due_time: datetime
    duration_mins: int
    pet_name: str = ""
    owner_name: str = ""
    priority: str = "medium"   # "low" | "medium" | "high"
    owner_id: int = 0
    pet_id: int = 0
    is_completed: bool = False
    frequency: str = "once"  # "once" | "daily" | "weekly"
    is_template: bool = False
    parent_task_id: int = 0
    generated_for: Optional[date] = None

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True

    def is_today(self) -> bool:
        """Return whether this task is due today."""
        return self.due_time.date() == date.today()

    def is_overdue(self) -> bool:
        """Return whether this task is overdue and incomplete."""
        return (not self.is_completed) and (self.due_time < datetime.now())


class Scheduler:
    def __init__(self):
        """Initialize scheduler state and internal task storage."""
        self._tasks: List[Task] = []
        self._next_task_id: int = 1
        self._pet_registry: dict = {}  # pet_id -> Pet, for internal lookup

    def _is_duplicate_task_for_pet(self, task: Task, pet: Pet) -> bool:
        """Return whether an equivalent task already exists for the pet."""
        existing_tasks = pet.get_tasks()

        # Generated recurring instances should only be unique per template per day.
        if task.parent_task_id > 0 and task.generated_for is not None:
            return any(
                existing.parent_task_id == task.parent_task_id
                and existing.generated_for == task.generated_for
                for existing in existing_tasks
            )

        # Manual/user-entered tasks keep strict duplicate checks.
        incoming_description = task.description.strip().lower()
        return any(
            existing.task_type == task.task_type
            and existing.description.strip().lower() == incoming_description
            and existing.duration_mins == task.duration_mins
            and existing.due_time == task.due_time
            for existing in existing_tasks
        )


    def add_task(self, task: Task, owner: Owner, pet: Pet) -> None:
        """Assign IDs and register a task for an owner and pet."""
        if self._is_duplicate_task_for_pet(task, pet):
            raise ValueError("adding task failed: duplicate task for pet with same details")

        task.id = self._next_task_id
        self._next_task_id += 1
        task.owner_id = owner.getId()
        task.pet_id = pet.getId()
        self._tasks.append(task)
        pet._tasks.append(task)
        self._pet_registry[pet.getId()] = pet

    def _should_generate_for_day(self, template: Task, target_day: date) -> bool:
        """Return whether a template should generate an instance for the given day.

        - daily: every day
        - weekly: every weekday (Mon–Fri); skips Saturday and Sunday
        """
        if template.frequency == "daily":
            return True
        if template.frequency == "weekly":
            return target_day.weekday() < 5  # Mon=0 … Fri=4
        return False

    @staticmethod
    def _next_weekday(from_day: date) -> date:
        """Return the next weekday (Mon–Fri) strictly after from_day."""
        next_day = from_day + timedelta(days=1)
        while next_day.weekday() >= 5:  # skip Sat=5, Sun=6
            next_day += timedelta(days=1)
        return next_day

    def _spawn_instance_from_template(self, template: Task, owner: Owner, target_day: date) -> None:
        """Spawn a single instance from a template for the given day, if not already generated."""
        pet = self._pet_registry.get(template.pet_id)
        if pet is None:
            return
        already_generated = any(
            t.parent_task_id == template.id and t.generated_for == target_day
            for t in pet.get_tasks()
        )
        if already_generated:
            return
        due_dt = datetime.combine(target_day, template.due_time.time())
        generated_task = Task(
            id=0,
            description=template.description,
            task_type=template.task_type,
            due_time=due_dt,
            duration_mins=template.duration_mins,
            pet_name=template.pet_name,
            owner_name=template.owner_name,
            priority=template.priority,
            frequency="once",
            is_template=False,
            parent_task_id=template.id,
            generated_for=target_day,
        )
        self.add_task(generated_task, owner, pet)

    def _spawn_recurring_tasks_for_date(self, owner: Owner, target_day: date) -> None:
        """Generate task instances from recurring templates for the given day."""
        for pet in owner.get_pets():
            for template in [t for t in pet.get_tasks() if t.is_template]:
                if self._should_generate_for_day(template, target_day):
                    self._spawn_instance_from_template(template, owner, target_day)

    def get_task(self, task_id: int) -> Optional[Task]:
        """Return the task with the given ID, if found."""
        return next((t for t in self._tasks if t.id == task_id), None)

    def complete_task(self, task_id: int, owner: Owner) -> None:
        """Mark a task complete and spawn the next occurrence for that task's template only."""
        task = self.get_task(task_id)
        if task is None or task.is_completed:
            return
        task.mark_complete()

        # Only recurring instances (spawned from a template) need a follow-up spawn.
        if task.parent_task_id <= 0:
            return
        template = self.get_task(task.parent_task_id)
        if template is None:
            return

        if template.frequency == "daily":
            next_day = date.today() + timedelta(days=1)
            self._spawn_instance_from_template(template, owner, next_day)
        elif template.frequency == "weekly":
            next_day = self._next_weekday(date.today())
            self._spawn_instance_from_template(template, owner, next_day)

    def undo_complete_task(self, task_id: int) -> None:
        """Reverse a completion: mark the task incomplete and remove the next-day instance that was pre-spawned."""
        task = self.get_task(task_id)
        if task is None or not task.is_completed:
            return
        task.is_completed = False

        if task.parent_task_id <= 0:
            return
        template = self.get_task(task.parent_task_id)
        if template is None:
            return

        if template.frequency == "daily":
            next_day = date.today() + timedelta(days=1)
        elif template.frequency == "weekly":
            next_day = self._next_weekday(date.today())
        else:
            return

        # Remove the pre-spawned next-day instance only if it hasn't been completed yet.
        to_remove = [
            t.id for t in self._tasks
            if t.parent_task_id == template.id
            and t.generated_for == next_day
            and not t.is_completed
        ]
        for tid in to_remove:
            self.remove_task(tid)

    def edit_task(self, task_id: int, **kwargs) -> bool:
        """Update editable task fields by task ID."""
        task = self.get_task(task_id)
        if task is None:
            return False
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        return True

    def remove_task(self, task_id: int) -> bool:
        """Remove a task from scheduler and pet task lists."""
        task = self.get_task(task_id)
        if task is None:
            return False

        child_ids: List[int] = []
        if task.is_template:
            child_ids = [t.id for t in self._tasks if t.parent_task_id == task.id]

        self._tasks = [t for t in self._tasks if t.id != task_id]
        pet = self._pet_registry.get(task.pet_id)
        if pet is not None:
            pet._tasks = [t for t in pet._tasks if t.id != task_id]

        for child_id in child_ids:
            self.remove_task(child_id)
        return True

    def schedule_walk(
        self,
        pet: Pet,
        owner: Owner,
        due_time: datetime,
        duration_mins: int,
        priority: str = "medium",
    ) -> Task:
        """Create and register a walk task for a pet."""
        task = Task(
            id=0,  # assigned by add_task
            description=f"Walk {pet.getName()}",
            task_type="walk",
            due_time=due_time,
            duration_mins=duration_mins,
            pet_name=pet.getName(),
            owner_name=owner.getName(),
            priority=priority,
        )
        self.add_task(task, owner, pet)
        return task

    def get_all_tasks(self, owner: Owner) -> List[Task]:
        """Return all tasks across the owner's pets."""
        return [task for pet in owner.get_pets() for task in pet.get_tasks()]

    def filter_tasks(
        self,
        owner: Owner,
        due_date: date,
        is_completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> List[Task]:
        """Return tasks for the owner filtered by due date, with optional filters for completion status and pet name."""
        tasks = self.get_all_tasks(owner)
        tasks = [t for t in tasks if t.due_time.date() == due_date]
        if is_completed is not None:
            tasks = [t for t in tasks if t.is_completed == is_completed]
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name.lower() == pet_name.lower()]
        return tasks

    def get_today_tasks(self, owner: Owner) -> List[Task]:
        """Return incomplete tasks due today plus overdue tasks."""
        self._spawn_recurring_tasks_for_date(owner, date.today())
        seen: set = set()
        result = []
        for t in self.get_all_tasks(owner):
            if (
                not t.is_template
                and not t.is_completed
                and t.due_time.date() <= date.today()
                and t.id not in seen
            ):
                seen.add(t.id)
                result.append(t)
        return result

    def generate_schedule(self, owner: Owner, available_mins: int) -> List[Task]:
        """Build a schedule that prioritizes overdue and high-priority tasks."""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        now = datetime.now()
        pending = self.get_today_tasks(owner)
        ranked = sorted(
            pending,
            key=lambda t: (
                0 if t.due_time < now else 1,
                priority_order.get(t.priority, 1),
                t.due_time,
                t.duration_mins,
            ),
        )
        scheduled, remaining = [], available_mins
        for task in ranked:
            if task.duration_mins <= remaining:
                scheduled.append(task)
                remaining -= task.duration_mins
        return scheduled


class Dashboard:
    def __init__(self, session_state: dict):
        """Store session state for rendering dashboard sections."""
        self._session_state = session_state

    def render_owner_details(self, owner: Owner) -> None:
        """Render owner details in the Streamlit UI."""
        st.subheader("Owner Details")
        st.write(f"**Name:** {owner.getName()}")
        st.write(f"**Email:** {owner.getEmail()}")

    def render_pet_details(self, pet: Pet) -> None:
        """Render pet details in the Streamlit UI."""
        st.subheader("Pet Details")
        st.write(f"**Name:** {pet.getName()}")
        st.write(f"**Species:** {pet.getSpecies()}")
        st.write(f"**Age:** {pet.getAge()} year(s)")

    def render_schedule_details(self, tasks: List[Task]) -> None:
        """Render today's task schedule in priority order."""
        st.subheader("Today's Schedule")
        if not tasks:
            st.info("No tasks scheduled for today.")
            return
        priority_badge = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        for task in sorted(tasks, key=lambda t: t.due_time):
            status = "✅" if task.is_completed else "🕐"
            badge = priority_badge.get(task.priority, "")
            st.markdown(
                f"{status} {badge} **{task.task_type.capitalize()}** — {task.description} "
                f"({task.duration_mins} min) at {task.due_time.strftime('%H:%M')}"
            )

    def run(self) -> None:
        """Render all dashboard sections from session state."""
        scheduler: Optional[Scheduler] = self._session_state.get("scheduler")
        owner: Optional[Owner] = self._session_state.get("owner")
        pet: Optional[Pet] = self._session_state.get("pet")

        if owner:
            self.render_owner_details(owner)
        if pet:
            self.render_pet_details(pet)
        if scheduler and owner:
            today_tasks = scheduler.get_today_tasks(owner)
            self.render_schedule_details(today_tasks)
