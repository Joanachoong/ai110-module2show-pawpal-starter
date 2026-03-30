from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Optional
import streamlit as st


@dataclass
class Owner:
    id: int
    name: str
    email: str

    def getId(self) -> int:
        return self.id

    def getName(self) -> str:
        return self.name

    def getEmail(self) -> str:
        return self.email


@dataclass
class Pet:
    id: int
    name: str
    species: str
    age: int
    owner_id: int

    def getId(self) -> int:
        return self.id

    def getName(self) -> str:
        return self.name

    def getSpecies(self) -> str:
        return self.species

    def getAge(self) -> int:
        return self.age


@dataclass
class Task:
    id: int
    description: str
    task_type: str
    due_time: datetime
    duration_mins: int
    owner_id: int = 0
    is_completed: bool = False

    def mark_complete(self) -> None:
        self.is_completed = True

    def is_today(self) -> bool:
        return self.due_time.date() == date.today()


class Scheduler:
    def __init__(self):
        self._pets: List[Pet] = []
        self._tasks: List[Task] = []

    def add_pet(self, pet: Pet) -> None:
        self._pets.append(pet)

    def add_task(self, task: Task, owner: Owner) -> None:
        task.owner_id = owner.getId()
        self._tasks.append(task)

    def schedule_walk(
        self,
        pet: Pet,
        owner: Owner,
        due_time: datetime,
        duration_mins: int,
    ) -> Task:
        task = Task(
            id=len(self._tasks) + 1,
            description=f"Walk {pet.getName()}",
            task_type="walk",
            due_time=due_time,
            duration_mins=duration_mins,
            owner_id=owner.getId(),
        )
        self._tasks.append(task)
        return task

    def get_today_tasks(self, owner: Owner) -> List[Task]:
        return [
            t for t in self._tasks
            if t.owner_id == owner.getId() and t.is_today()
        ]

    def get_all_pets(self) -> List[Pet]:
        return list(self._pets)


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
        for task in sorted(tasks, key=lambda t: t.due_time):
            status = "✅" if task.is_completed else "🕐"
            st.markdown(
                f"{status} **{task.task_type.capitalize()}** — {task.description} "
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
