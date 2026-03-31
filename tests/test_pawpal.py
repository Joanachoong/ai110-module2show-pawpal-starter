import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, date, timedelta
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


def test_schedule_still_returns_today_tasks_after_duplicate_failure():
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
        priority="high",
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
        priority="high",
        frequency="once",
        is_template=False,
    )

    scheduler.add_task(daily_task, owner, pet)

    with pytest.raises(ValueError, match="adding task failed"):
        scheduler.add_task(once_task_same_details, owner, pet)

    # Even after the duplicate add failure, the scheduler should still generate
    # and return today's schedule from the daily template.
    today_schedule = scheduler.generate_schedule(owner, available_mins=60)

    assert len(today_schedule) == 1
    assert today_schedule[0].description == "Morning walk around the block"
    assert today_schedule[0].due_time.date() == datetime.today().date()


# --- filter_tasks test helpers ---

def make_filter_setup():
    """Create owner, two pets (Buddy, Luna), and three tasks for filter tests."""
    owner = Owner(id=1, name="Alex", email="alex@pawpal.com")
    buddy = Pet(id=1, name="Buddy", species="Dog", age=3, owner_id=owner.getId())
    luna = Pet(id=2, name="Luna", species="Cat", age=2, owner_id=owner.getId())
    owner.add_pet(buddy)
    owner.add_pet(luna)
    scheduler = Scheduler()

    today = datetime.today().replace(hour=10, minute=0, second=0, microsecond=0)

    task_buddy_incomplete = Task(
        id=0, description="Walk Buddy", task_type="walk",
        due_time=today, duration_mins=20,
        pet_name="Buddy", owner_name="Alex",
    )
    task_buddy_complete = Task(
        id=0, description="Feed Buddy", task_type="feeding",
        due_time=today, duration_mins=10,
        pet_name="Buddy", owner_name="Alex",
    )
    task_luna_incomplete = Task(
        id=0, description="Play with Luna", task_type="play",
        due_time=today, duration_mins=15,
        pet_name="Luna", owner_name="Alex",
    )

    scheduler.add_task(task_buddy_incomplete, owner, buddy)
    scheduler.add_task(task_buddy_complete, owner, buddy)
    scheduler.add_task(task_luna_incomplete, owner, luna)

    task_buddy_complete.mark_complete()

    return scheduler, owner, today.date()


# --- filter_tasks tests ---

def test_filter_tasks_by_completion_true():
    scheduler, owner, today = make_filter_setup()
    result = scheduler.filter_tasks(owner, today, is_completed=True)
    assert len(result) == 1
    assert result[0].description == "Feed Buddy"


def test_filter_tasks_by_completion_false():
    scheduler, owner, today = make_filter_setup()
    result = scheduler.filter_tasks(owner, today, is_completed=False)
    assert len(result) == 2
    descriptions = {t.description for t in result}
    assert descriptions == {"Walk Buddy", "Play with Luna"}


def test_filter_tasks_by_pet_name():
    scheduler, owner, today = make_filter_setup()
    result = scheduler.filter_tasks(owner, today, pet_name="Buddy")
    assert len(result) == 2
    assert all(t.pet_name == "Buddy" for t in result)


def test_filter_tasks_by_pet_name_case_insensitive():
    scheduler, owner, today = make_filter_setup()
    result = scheduler.filter_tasks(owner, today, pet_name="buddy")
    assert len(result) == 2
    assert all(t.pet_name == "Buddy" for t in result)


def test_filter_tasks_by_both_completion_and_pet_name():
    scheduler, owner, today = make_filter_setup()
    result = scheduler.filter_tasks(owner, today, is_completed=False, pet_name="Buddy")
    assert len(result) == 1
    assert result[0].description == "Walk Buddy"


def test_filter_tasks_due_date_only():
    scheduler, owner, today = make_filter_setup()
    result = scheduler.filter_tasks(owner, today)
    assert len(result) == 3


# --- scheduler behavior tests: sorting, recurrence, conflict detection ---

def make_owner_pet_scheduler():
    owner = Owner(id=1, name="Alex", email="alex@pawpal.com")
    pet = Pet(id=1, name="Buddy", species="Dog", age=3, owner_id=owner.getId())
    owner.add_pet(pet)
    scheduler = Scheduler()
    return owner, pet, scheduler


def test_pet_with_no_tasks_returns_empty_today_and_schedule():
    owner, pet, scheduler = make_owner_pet_scheduler()

    assert pet.get_tasks() == []
    assert scheduler.get_today_tasks(owner) == []
    assert scheduler.generate_schedule(owner, available_mins=60) == []


def test_generate_schedule_orders_by_due_time_then_duration_for_same_priority():
    owner, pet, scheduler = make_owner_pet_scheduler()
    now = datetime.now().replace(second=0, microsecond=0)
    same_time = now + timedelta(hours=2)

    task_earlier = Task(
        id=0,
        description="Earliest in time",
        task_type="walk",
        due_time=now + timedelta(hours=1),
        duration_mins=20,
        pet_name=pet.getName(),
        owner_name=owner.getName(),
        priority="medium",
    )
    task_same_time_longer = Task(
        id=0,
        description="Same time longer",
        task_type="feeding",
        due_time=same_time,
        duration_mins=30,
        pet_name=pet.getName(),
        owner_name=owner.getName(),
        priority="medium",
    )
    task_same_time_shorter = Task(
        id=0,
        description="Same time shorter",
        task_type="play",
        due_time=same_time,
        duration_mins=10,
        pet_name=pet.getName(),
        owner_name=owner.getName(),
        priority="medium",
    )

    scheduler.add_task(task_earlier, owner, pet)
    scheduler.add_task(task_same_time_longer, owner, pet)
    scheduler.add_task(task_same_time_shorter, owner, pet)

    ordered = scheduler.generate_schedule(owner, available_mins=120)
    descriptions = [t.description for t in ordered]
    assert descriptions == ["Earliest in time", "Same time shorter", "Same time longer"]


def test_generate_schedule_ranks_overdue_before_not_overdue():
    owner, pet, scheduler = make_owner_pet_scheduler()
    now = datetime.now().replace(second=0, microsecond=0)

    future_high = Task(
        id=0,
        description="Future high",
        task_type="walk",
        due_time=now + timedelta(hours=3),
        duration_mins=10,
        pet_name=pet.getName(),
        owner_name=owner.getName(),
        priority="high",
    )
    overdue_medium = Task(
        id=0,
        description="Overdue medium",
        task_type="feeding",
        due_time=now - timedelta(hours=1),
        duration_mins=10,
        pet_name=pet.getName(),
        owner_name=owner.getName(),
        priority="medium",
    )

    scheduler.add_task(future_high, owner, pet)
    scheduler.add_task(overdue_medium, owner, pet)

    ordered = scheduler.generate_schedule(owner, available_mins=60)
    assert [t.description for t in ordered][:2] == ["Overdue medium", "Future high"]


def test_generate_schedule_respects_available_minutes_greedy_fit():
    owner, pet, scheduler = make_owner_pet_scheduler()
    now = datetime.now().replace(second=0, microsecond=0)

    t1 = Task(
        id=0,
        description="Task 1",
        task_type="walk",
        due_time=now + timedelta(minutes=30),
        duration_mins=20,
        pet_name=pet.getName(),
        owner_name=owner.getName(),
        priority="high",
    )
    t2 = Task(
        id=0,
        description="Task 2",
        task_type="feeding",
        due_time=now + timedelta(minutes=40),
        duration_mins=15,
        pet_name=pet.getName(),
        owner_name=owner.getName(),
        priority="high",
    )
    t3 = Task(
        id=0,
        description="Task 3",
        task_type="play",
        due_time=now + timedelta(minutes=50),
        duration_mins=30,
        pet_name=pet.getName(),
        owner_name=owner.getName(),
        priority="high",
    )

    scheduler.add_task(t1, owner, pet)
    scheduler.add_task(t2, owner, pet)
    scheduler.add_task(t3, owner, pet)

    selected = scheduler.generate_schedule(owner, available_mins=35)
    assert [t.description for t in selected] == ["Task 1", "Task 2"]
    assert sum(t.duration_mins for t in selected) <= 35


def test_complete_daily_generated_task_spawns_next_day_once():
    owner, pet, scheduler = make_owner_pet_scheduler()
    due_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)

    daily_template = Task(
        id=0,
        description="Morning walk",
        task_type="walk",
        due_time=due_time,
        duration_mins=20,
        pet_name=pet.getName(),
        owner_name=owner.getName(),
        priority="medium",
        frequency="daily",
        is_template=True,
    )
    scheduler.add_task(daily_template, owner, pet)

    today_tasks = scheduler.get_today_tasks(owner)
    generated_today = next(t for t in today_tasks if t.parent_task_id == daily_template.id)
    scheduler.complete_task(generated_today.id, owner)

    tomorrow = date.today() + timedelta(days=1)
    spawned = [
        t for t in scheduler.get_all_tasks(owner)
        if t.parent_task_id == daily_template.id and t.generated_for == tomorrow
    ]
    assert len(spawned) == 1


def test_same_time_different_task_types_are_not_duplicates():
    owner, pet, scheduler = make_owner_pet_scheduler()
    same_due_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)

    walk_task = Task(
        id=0,
        description="Care routine",
        task_type="walk",
        due_time=same_due_time,
        duration_mins=20,
        pet_name=pet.getName(),
        owner_name=owner.getName(),
    )
    feeding_task = Task(
        id=0,
        description="Care routine",
        task_type="feeding",
        due_time=same_due_time,
        duration_mins=20,
        pet_name=pet.getName(),
        owner_name=owner.getName(),
    )

    scheduler.add_task(walk_task, owner, pet)
    scheduler.add_task(feeding_task, owner, pet)

    assert len(pet.get_tasks()) == 2


def test_duplicate_same_time_same_details_is_rejected_with_normalized_description():
    owner, pet, scheduler = make_owner_pet_scheduler()
    same_due_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)

    original = Task(
        id=0,
        description="Morning walk around the block",
        task_type="walk",
        due_time=same_due_time,
        duration_mins=20,
        pet_name=pet.getName(),
        owner_name=owner.getName(),
    )
    duplicate = Task(
        id=0,
        description="  morning walk around the block  ",
        task_type="walk",
        due_time=same_due_time,
        duration_mins=20,
        pet_name=pet.getName(),
        owner_name=owner.getName(),
    )

    scheduler.add_task(original, owner, pet)
    with pytest.raises(ValueError, match="adding task failed"):
        scheduler.add_task(duplicate, owner, pet)
