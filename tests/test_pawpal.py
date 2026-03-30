import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime
import pytest
from pawpal_system import Owner, Pet, Task, Scheduler


def make_task(id=0):
    return Task(
        id=id,
        description="Test task",
        task_type="walk",
        due_time=datetime.today().replace(hour=9, minute=0, second=0, microsecond=0),
        duration_mins=20,
    )


def test_mark_complete_changes_status():
    task = make_task()
    assert task.is_completed is False
    task.mark_complete()
    assert task.is_completed is True


def test_add_task_increases_pet_task_count():
    owner = Owner(id=1, name="Alex", email="alex@pawpal.com")
    pet = Pet(id=1, name="Buddy", species="Dog", age=3, owner_id=owner.getId())
    scheduler = Scheduler()

    assert len(pet.get_tasks()) == 0
    scheduler.add_task(make_task(), owner, pet)
    assert len(pet.get_tasks()) == 1


def test_add_same_task_daily_then_once_should_fail():
    owner = Owner(id=1, name="Alex", email="alex@pawpal.com")
    pet = Pet(id=1, name="Buddy", species="Dog", age=3, owner_id=owner.getId())
    owner.add_pet(pet)
    scheduler = Scheduler()

    same_due_time = datetime.today().replace(hour=9, minute=0, second=0, microsecond=0)

    daily_task = Task(
        id=0,
        description="Morning walk around the block",
        task_type="walk",
        due_time=same_due_time,
        duration_mins=20,
        pet_name=pet.getName(),
        owner_name=owner.getName(),
        frequency="daily",
        is_template=True,
    )

    once_task_same_details = Task(
        id=0,
        description="Morning walk around the block",
        task_type="walk",
        due_time=same_due_time,
        duration_mins=20,
        pet_name=pet.getName(),
        owner_name=owner.getName(),
        frequency="once",
        is_template=False,
    )

    scheduler.add_task(daily_task, owner, pet)

    with pytest.raises(ValueError, match="adding task failed"):
        scheduler.add_task(once_task_same_details, owner, pet)

    assert len(pet.get_tasks()) == 1
