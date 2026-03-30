import streamlit as st
from datetime import datetime, date
from pawpal_system import Owner, Pet, Task, Scheduler, Dashboard

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

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

# ── Owner ──────────────────────────────────────────────────────────────────────
st.subheader("Owner")
oc1, oc2 = st.columns(2)
with oc1:
    owner_name = st.text_input("Name", value="Alex Rivera")
with oc2:
    owner_email = st.text_input("Email", value="alex@pawpal.com")

if st.button("Set Owner"):
    st.session_state.owner = Owner(id=1, name=owner_name, email=owner_email)
    for pet in st.session_state.pets.values():
        st.session_state.owner.add_pet(pet)
    st.success(f"Owner set: {owner_name} ({owner_email})")

if st.session_state.owner is None:
    st.info("Set an owner above to get started.")
    st.stop()

st.divider()

# ── Pets ───────────────────────────────────────────────────────────────────────
st.subheader("Pets")

if st.session_state.pets:
    for pet in st.session_state.pets.values():
        task_count = len(pet.get_tasks())
        st.write(
            f"- **{pet.getName()}** — {pet.getSpecies()}, age {pet.getAge()} "
            f"| {task_count} task(s)"
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
        frequency = st.selectbox("Frequency", ["once", "daily", "weekdays"])
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
            for task in st.session_state.scheduler.get_all_tasks(st.session_state.owner)
        )

        if duplicate_exists:
            st.warning("Duplicate task detected for this pet with the same details.")
            st.error("Task failed: An exact same task has already been added.")
        else:
            new_task = Task(
                id=0,
                description=task_description,
                task_type=task_type,
                due_time=due_dt,
                duration_mins=int(duration),
                pet_name=selected_pet.getName(),
                owner_name=st.session_state.owner.getName(),
                priority=priority,
                frequency=frequency,
                is_template=is_template_task,
            )
            st.session_state.scheduler.add_task(new_task, st.session_state.owner, selected_pet)
            st.rerun()

# Task list with mark-complete buttons
st.session_state.scheduler.get_today_tasks(st.session_state.owner)
all_tasks = [
    task
    for task in st.session_state.scheduler.get_all_tasks(st.session_state.owner)
    if not task.is_template
]
if all_tasks:
    st.write("**All tasks:**")
    priority_badge = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    for task in sorted(all_tasks, key=lambda t: t.due_time):
        status = "✅" if task.is_completed else "🕐"
        badge = priority_badge.get(task.priority, "")
        col_info, col_btn, col_remove = st.columns([5, 1, 1])
        with col_info:
            st.write(
                f"{status} {badge} **{task.task_type.capitalize()}** — {task.description} "
                f"| {task.pet_name} | {task.due_time.strftime('%I:%M %p')} | {task.duration_mins} min"
            )
        with col_btn:
            label = "Undo" if task.is_completed else "Done"
            if st.button(label, key=f"toggle_{task.id}"):
                if task.is_completed:
                    task.is_completed = False
                else:
                    task.mark_complete()
                st.rerun()
        with col_remove:
            if st.button("Remove", key=f"remove_{task.id}"):
                st.session_state.scheduler.remove_task(task.id)
                st.rerun()
else:
    st.info("No tasks yet. Add one above.")

templates = [
    task
    for task in st.session_state.scheduler.get_all_tasks(st.session_state.owner)
    if task.is_template
]
if templates:
    st.write("**Recurring templates:**")
    for template in sorted(templates, key=lambda t: (t.pet_name, t.due_time.time())):
        col_template, col_delete = st.columns([5, 1])
        with col_template:
            st.write(
                f"🔁 **{template.task_type.capitalize()}** — {template.description} "
                f"| {template.pet_name} | {template.frequency} | {template.due_time.strftime('%I:%M %p')}"
            )
        with col_delete:
            if st.button("Delete", key=f"delete_template_{template.id}"):
                st.session_state.scheduler.remove_task(template.id)
                st.rerun()

st.divider()

st.subheader("Build Schedule")
available_mins = st.number_input(
    "Available time today (minutes)", min_value=10, max_value=480, value=120
)

if st.button("Generate schedule"):
    scheduled_tasks = st.session_state.scheduler.generate_schedule(
        st.session_state.owner,
        available_mins=int(available_mins),
    )
    dashboard = Dashboard(st.session_state)
    dashboard.render_schedule_details(scheduled_tasks)
