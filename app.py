import streamlit as st
from datetime import datetime, date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


def _date_label(due: datetime) -> str:
    """Return a human-readable date label for a task's due time."""
    today = date.today()
    tomorrow = today + timedelta(days=1)
    if due.date() == today:
        return f"Today {due.strftime('%I:%M %p')}"
    if due.date() == tomorrow:
        return f"Tomorrow {due.strftime('%I:%M %p')}"
    return due.strftime('%a %b %d, %I:%M %p')


def _find_conflicts(tasks):
    """Return pairs of tasks whose time windows overlap."""
    conflicts = []
    sorted_t = sorted(tasks, key=lambda t: t.due_time)
    for i in range(len(sorted_t) - 1):
        a, b = sorted_t[i], sorted_t[i + 1]
        a_end = a.due_time + timedelta(minutes=a.duration_mins)
        if b.due_time < a_end:
            conflicts.append((a, b))
    return conflicts


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Pet care planning assistant — schedule, prioritize, and track your pet tasks.")

st.divider()

# ── Session state ──────────────────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None

if "pets" not in st.session_state:
    st.session_state.pets = {}          # pet_id -> Pet

if "next_pet_id" not in st.session_state:
    st.session_state.next_pet_id = 1

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

if "scheduled_tasks" not in st.session_state:
    st.session_state.scheduled_tasks = None

# ── Owner ──────────────────────────────────────────────────────────────────────
st.subheader("Owner")
oc1, oc2 = st.columns(2)
with oc1:
    owner_name = st.text_input("Name", value="Alex Rivera")
with oc2:
    owner_email = st.text_input("Email", value="alex@pawpal.com")

if st.button("Set Owner"):
    normalized_owner_name = owner_name.strip().lower()
    normalized_owner_email = owner_email.strip().lower()
    existing_owner = st.session_state.owner

    is_duplicate_owner = (
        existing_owner is not None
        and existing_owner.getName().strip().lower() == normalized_owner_name
        and existing_owner.getEmail().strip().lower() == normalized_owner_email
    )

    if is_duplicate_owner:
        st.warning("Duplicate owner detected with the same name and email.")
        st.error("Owner failed: Duplicate owner information was found.")
    else:
        st.session_state.owner = Owner(id=1, name=owner_name, email=owner_email)
        for pet in st.session_state.pets.values():
            st.session_state.owner.add_pet(pet)
        st.success(f"Owner set: {owner_name} ({owner_email})")

if st.session_state.owner is None:
    st.info("Set an owner above to get started.")
    st.stop()

st.divider()

# ── Pets ──────────────────────────────────────────────────────────────────────
st.subheader("Pets")

if st.session_state.pets:
    st.table(
        [
            {
                "Name": pet.getName(),
                "Species": pet.getSpecies(),
                "Age (yrs)": pet.getAge(),
                "Tasks": len(pet.get_tasks()),
            }
            for pet in st.session_state.pets.values()
        ]
    )
else:
    st.info("No pets yet. Add one below.")

with st.expander("Add a pet"):
    pc1, pc2, pc3 = st.columns(3)
    with pc1:
        new_pet_name = st.text_input("Pet name", value="Buddy")
    with pc2:
        new_pet_species = st.selectbox("Species", ["Dog", "Cat", "Other"])
    with pc3:
        new_pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)

    if st.button("Add pet"):
        normalized_pet_name = new_pet_name.strip().lower()
        duplicate_pet_exists = any(
            pet.getName().strip().lower() == normalized_pet_name
            and pet.getSpecies().strip().lower() == new_pet_species.strip().lower()
            and pet.getAge() == int(new_pet_age)
            and pet.getOwnerId() == st.session_state.owner.getId()
            for pet in st.session_state.pets.values()
        )

        if duplicate_pet_exists:
            st.warning("Duplicate pet detected with the same details.")
            st.error("Pet failed: Duplicate pet information was found.")
        else:
            pet_id = st.session_state.next_pet_id
            new_pet = Pet(
                id=pet_id,
                name=new_pet_name,
                species=new_pet_species,
                age=int(new_pet_age),
                owner_id=st.session_state.owner.getId(),
            )
            st.session_state.pets[pet_id] = new_pet
            st.session_state.owner.add_pet(new_pet)
            st.session_state.next_pet_id += 1
            st.rerun()

st.divider()

# ── Today's Overview ───────────────────────────────────────────────────────────
st.subheader("Today's Overview")

owner = st.session_state.owner
scheduler = st.session_state.scheduler

today_tasks = scheduler.get_today_tasks(owner)
overdue_tasks = [t for t in today_tasks if t.is_overdue()]
all_owner_tasks = scheduler.get_all_tasks(owner)
completed_today = [
    t for t in all_owner_tasks
    if t.is_completed and not t.is_template and t.is_today()
]

m1, m2, m3 = st.columns(3)
m1.metric("Due Today", len(today_tasks))
m2.metric("Overdue", len(overdue_tasks))
m3.metric("Completed Today", len(completed_today))

if overdue_tasks:
    priority_badge = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    for task in sorted(overdue_tasks, key=lambda t: t.due_time):
        badge = priority_badge.get(task.priority, "")
        st.warning(
            f"⚠️ Overdue: {badge} **{task.task_type.capitalize()}** — {task.description} "
            f"| {task.pet_name} | {_date_label(task.due_time)} | {task.duration_mins} min"
        )
elif today_tasks:
    st.success("No overdue tasks — you're on track!")
else:
    st.info("No tasks due today. Add tasks below to get started.")

st.divider()

# ── Tasks ──────────────────────────────────────────────────────────────────────
st.subheader("Tasks")

if not st.session_state.pets:
    st.info("Add a pet before adding tasks.")
else:
    pet_names = {pet.getName(): pid for pid, pet in st.session_state.pets.items()}

    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        task_description = st.text_input("Description", value="Morning walk around the block")
        task_type = st.selectbox("Task type", ["walk", "feeding", "grooming", "vet", "play", "other"])
    with tc2:
        task_pet_name = st.selectbox("For pet", list(pet_names.keys()))
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=30)
    with tc3:
        priority = st.selectbox("Priority", ["high", "medium", "low"])
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
        freq_hints = {
            "once": "Due: Today",
            "daily": "Repeats every day",
            "weekly": "Repeats Mon – Fri",
        }
        st.caption(freq_hints[frequency])
        due_time_input = st.time_input(
            "Due time",
            value=datetime.now().replace(hour=8, minute=0, second=0, microsecond=0).time(),
        )

    if st.button("Add task"):
        pet_id = pet_names[task_pet_name]
        selected_pet = st.session_state.pets[pet_id]
        due_dt = datetime.combine(date.today(), due_time_input)
        normalized_description = task_description.strip().lower()
        is_template_task = frequency != "once"

        duplicate_exists = any(
            task.pet_id == selected_pet.getId()
            and task.task_type == task_type
            and task.description.strip().lower() == normalized_description
            and task.duration_mins == int(duration)
            and task.due_time == due_dt
            and task.is_template == is_template_task
            and (not is_template_task or task.frequency == frequency)
            for task in scheduler.get_all_tasks(owner)
        )

        if duplicate_exists:
            st.warning("Task not added: A duplicate task for this pet already exists.")
        else:
            new_task = Task(
                id=0,
                description=task_description,
                task_type=task_type,
                due_time=due_dt,
                duration_mins=int(duration),
                pet_name=selected_pet.getName(),
                owner_name=owner.getName(),
                priority=priority,
                frequency=frequency,
                is_template=is_template_task,
            )
            try:
                scheduler.add_task(new_task, owner, selected_pet)
                st.rerun()
            except ValueError:
                st.warning("Task not added: A duplicate task for this pet already exists.")

# ── Task library ───────────────────────────────────────────────────────────────
all_library_tasks = sorted(
    [t for t in scheduler.get_all_tasks(owner)
     if t.is_template or (t.frequency == "once" and t.parent_task_id == 0)],
    key=lambda t: (t.due_time.time(), t.pet_name),
)

if all_library_tasks:
    freq_icon = {"once": "1️⃣", "daily": "🔁", "weekly": "📅"}
    priority_badge = {"high": "🔴", "medium": "🟡", "low": "🟢"}

    st.write("**Task library:**")
    # Header row
    hc1, hc2 = st.columns([6, 1])
    with hc1:
        st.caption("Freq · Priority · Type — Description | Pet | Time | Duration")
    with hc2:
        st.caption("Action")

    for task in all_library_tasks:
        badge = priority_badge.get(task.priority, "")
        ficon = freq_icon.get(task.frequency, "")
        col_info, col_remove = st.columns([6, 1])
        with col_info:
            st.write(
                f"{ficon} {badge} **{task.task_type.capitalize()}** — {task.description} "
                f"| {task.pet_name} | {task.frequency} | {task.due_time.strftime('%I:%M %p')} | {task.duration_mins} min"
            )
        with col_remove:
            if st.button("Remove", key=f"remove_{task.id}"):
                scheduler.remove_task(task.id)
                st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ── Schedule ───────────────────────────────────────────────────────────────────
st.subheader("Build Schedule")

available_mins = st.number_input(
    "Available time today (minutes)", min_value=10, max_value=480, value=120
)

if st.button("Generate schedule"):
    st.session_state.scheduled_tasks = scheduler.generate_schedule(
        owner,
        available_mins=int(available_mins),
    )

if st.session_state.scheduled_tasks is not None:
    scheduled = st.session_state.scheduled_tasks

    # ── Conflict warnings ──────────────────────────────────────────────────────
    conflicts = _find_conflicts(scheduled)
    if conflicts:
        for a, b in conflicts:
            st.warning(
                f"⚠️ Conflict: **{a.description}** overlaps with **{b.description}** "
                f"({a.due_time.strftime('%I:%M %p')} + {a.duration_mins} min vs {b.due_time.strftime('%I:%M %p')})"
            )

    # ── Summary metrics ────────────────────────────────────────────────────────
    total_mins_used = sum(t.duration_mins for t in scheduled)
    done_count = sum(1 for t in scheduled if t.is_completed)
    sm1, sm2, sm3 = st.columns(3)
    sm1.metric("Tasks Scheduled", len(scheduled))
    sm2.metric("Time Used", f"{total_mins_used} min")
    sm3.metric("Completed", done_count)

    # ── Filters ────────────────────────────────────────────────────────────────
    st.write("**Filter schedule:**")
    fc1, fc2 = st.columns(2)
    with fc1:
        completion_filter = st.selectbox(
            "By completion status",
            ["All", "Incomplete", "Completed"],
            key="sched_completion_filter",
        )
    with fc2:
        pet_options = ["All"] + sorted({t.pet_name for t in scheduled if t.pet_name})
        pet_filter = st.selectbox(
            "By pet name",
            pet_options,
            key="sched_pet_filter",
        )

    # Use filter_tasks for date+completion+pet filtering when possible,
    # then intersect with scheduled task IDs to stay within the generated schedule.
    scheduled_ids = {t.id for t in scheduled}

    is_completed_filter = None
    if completion_filter == "Completed":
        is_completed_filter = True
    elif completion_filter == "Incomplete":
        is_completed_filter = False

    pet_name_filter = None if pet_filter == "All" else pet_filter

    filtered = scheduler.filter_tasks(
        owner,
        due_date=date.today(),
        is_completed=is_completed_filter,
        pet_name=pet_name_filter,
    )
    # Keep only tasks that are in the current schedule
    filtered_ids = {t.id for t in filtered}
    tasks_to_show = [t for t in scheduled if t.id in filtered_ids]

    # ── Schedule rows ──────────────────────────────────────────────────────────
    st.subheader("Today's Schedule")
    if not tasks_to_show:
        st.info("No tasks match the current filters.")
    else:
        priority_badge = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        for task in sorted(tasks_to_show, key=lambda t: t.due_time):
            badge = priority_badge.get(task.priority, "")
            row_text = (
                f"**{task.task_type.capitalize()}** — {task.description} "
                f"| {task.pet_name} | {_date_label(task.due_time)} | {task.duration_mins} min {badge}"
            )
            col_info, col_btn = st.columns([6, 1])
            with col_info:
                if task.is_completed:
                    st.success(f"✅ {row_text}")
                elif task.is_overdue():
                    st.error(f"🔴 Overdue: {row_text}")
                else:
                    st.write(f"🕐 {row_text}")
            with col_btn:
                label = "Undo" if task.is_completed else "Done"
                if st.button(label, key=f"sched_toggle_{task.id}"):
                    if task.is_completed:
                        scheduler.undo_complete_task(task.id)
                    else:
                        scheduler.complete_task(task.id, owner)
                    st.rerun()
