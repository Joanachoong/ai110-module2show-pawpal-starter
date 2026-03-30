# THHIS IS THE TESTING GROUND OF THE LOGIC AND SEE ID IT RUNS IN THE TERMINAL

from datetime import datetime
from pawpal_system import Owner, Pet, Task, Scheduler

# --- Create Owner ---
owner = Owner(id=1, name="Alex Rivera", email="alex@pawpal.com")

# --- Create Pets ---
buddy = Pet(id=1, name="Buddy", species="Dog", age=3, owner_id=owner.getId())
whiskers = Pet(id=2, name="Whiskers", species="Cat", age=5, owner_id=owner.getId())

owner.add_pet(buddy)
owner.add_pet(whiskers)

# --- Set up Scheduler ---
scheduler = Scheduler()

today = datetime.today()

# Task 1: Morning walk for Buddy
task1 = Task(
    id=0,
    description="Morning walk around the block",
    task_type="walk",
    due_time=today.replace(hour=8, minute=0, second=0, microsecond=0),
    duration_mins=30,
    pet_name=buddy.getName(),
    owner_name=owner.getName(),
    priority="high",
)
scheduler.add_task(task1, owner, buddy)

# Task 2: Feeding Whiskers at noon
task2 = Task(
    id=0,
    description="Feed wet food",
    task_type="feeding",
    due_time=today.replace(hour=12, minute=0, second=0, microsecond=0),
    duration_mins=10,
    pet_name=whiskers.getName(),
    owner_name=owner.getName(),
    priority="high",
)
scheduler.add_task(task2, owner, whiskers)

# Task 3: Afternoon walk for Buddy
task3 = Task(
    id=0,
    description="Afternoon walk at the park",
    task_type="walk",
    due_time=today.replace(hour=15, minute=30, second=0, microsecond=0),
    duration_mins=45,
    pet_name=buddy.getName(),
    owner_name=owner.getName(),
    priority="medium",
)
scheduler.add_task(task3, owner, buddy)

# Task 4: Grooming Whiskers in the evening
task4 = Task(
    id=0,
    description="Brush fur and check ears",
    task_type="grooming",
    due_time=today.replace(hour=18, minute=0, second=0, microsecond=0),
    duration_mins=20,
    pet_name=whiskers.getName(),
    owner_name=owner.getName(),
    priority="low",
)
scheduler.add_task(task4, owner, whiskers)

# --- Print Today's Schedule ---
today_tasks = scheduler.get_today_tasks(owner)
today_tasks_sorted = sorted(today_tasks, key=lambda t: t.due_time)

priority_label = {"high": "[HIGH]", "medium": "[MED] ", "low": "[LOW] "}

print("=" * 50)
print("         TODAY'S SCHEDULE")
print(f"         Owner: {owner.getName()}")
print("=" * 50)

for task in today_tasks_sorted:
    badge = priority_label.get(task.priority, "      ")
    time_str = task.due_time.strftime("%I:%M %p")
    print(
        f"{badge} {time_str}  {task.task_type.upper():10}  "
        f"{task.pet_name} — {task.description} ({task.duration_mins} min)"
    )

print("=" * 50)
print(f"Total tasks: {len(today_tasks_sorted)}")
