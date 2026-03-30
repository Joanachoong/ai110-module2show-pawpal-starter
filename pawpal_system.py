from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional
import streamlit as st


@dataclass
class Owner:
    id: int
    name: str
    email: str
    _pets: List[Pet] = field(default_factory=list)

    def getId(self) -> int:
        return self.id

    def getName(self) -> str:
        return self.name

    def getEmail(self) -> str:
        return self.email

    def add_pet(self, pet: Pet) -> None:
        self._pets.append(pet)

    def get_pets(self) -> List[Pet]:
        return list(self._pets)

    def get_pet_ids(self) -> List[int]:
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
        return self.id

    def getName(self) -> str:
        return self.name

    def getSpecies(self) -> str:
        return self.species

    def getAge(self) -> int:
        return self.age

    def getOwnerId(self) -> int:
        return self.owner_id

    def get_tasks(self) -> List[Task]:
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

    def mark_complete(self) -> None:
        self.is_completed = True

    def is_today(self) -> bool:
        return self.due_time.date() == date.today()


class Scheduler:
    def __init__(self):
        self._tasks: List[Task] = []
        self._next_task_id: int = 1
        self._pet_registry: dict = {}  # pet_id -> Pet, for internal lookup

    def add_task(self, task: Task, owner: Owner, pet: Pet) -> None:
        task.id = self._next_task_id
        self._next_task_id += 1
        task.owner_id = owner.getId()
        task.pet_id = pet.getId()
        self._tasks.append(task)
        pet._tasks.append(task)
        self._pet_registry[pet.getId()] = pet

    def get_task(self, task_id: int) -> Optional[Task]:
        return next((t for t in self._tasks if t.id == task_id), None)

    def edit_task(self, task_id: int, **kwargs) -> bool:
        task = self.get_task(task_id)
        if task is None:
            return False
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        return True

    def remove_task(self, task_id: int) -> bool:
        task = self.get_task(task_id)
        if task is None:
            return False
        self._tasks = [t for t in self._tasks if t.id != task_id]
        pet = self._pet_registry.get(task.pet_id)
        if pet is not None:
            pet._tasks = [t for t in pet._tasks if t.id != task_id]
        return True

    def schedule_walk(
        self,
        pet: Pet,
        owner: Owner,
        due_time: datetime,
        duration_mins: int,
        priority: str = "medium",
    ) -> Task:
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
        return [task for pet in owner.get_pets() for task in pet.get_tasks()]

    def get_today_tasks(self, owner: Owner) -> List[Task]:
        return [
            t for t in self.get_all_tasks(owner)
            if t.is_today() and not t.is_completed
        ]

    def generate_schedule(self, owner: Owner, available_mins: int) -> List[Task]:
        priority_order = {"high": 0, "medium": 1, "low": 2}
        pending = self.get_today_tasks(owner)
        ranked = sorted(pending, key=lambda t: priority_order.get(t.priority, 1))
        scheduled, remaining = [], available_mins
        for task in ranked:
            if task.duration_mins <= remaining:
                scheduled.append(task)
                remaining -= task.duration_mins
        return scheduled


class Dashboard:
    def __init__(self, session_state: dict):
        self._session_state = session_state

    def render_owner_details(self, owner: Owner) -> None:
        st.subheader("Owner Details")
        st.write(f"**Name:** {owner.getName()}")
        st.write(f"**Email:** {owner.getEmail()}")

    def render_pet_details(self, pet: Pet) -> None:
        st.subheader("Pet Details")
        st.write(f"**Name:** {pet.getName()}")
        st.write(f"**Species:** {pet.getSpecies()}")
        st.write(f"**Age:** {pet.getAge()} year(s)")

    def render_schedule_details(self, tasks: List[Task]) -> None:
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
