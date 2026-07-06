import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A pet care planning assistant — set up your owner and pets, add tasks, and build a daily plan.")

# --- Session state -----------------------------------------------------------
# The Owner is our single source of truth. It lives in st.session_state so it
# (and all its pets/tasks) persists across Streamlit reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", time_available=120)

owner = st.session_state.owner  # the actual persisted object — mutating it sticks

# --- Owner setup -------------------------------------------------------------
st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    owner.time_available = st.number_input(
        "Time available today (minutes)", min_value=0, max_value=1440, value=owner.time_available
    )

st.divider()

# --- Add a pet ---------------------------------------------------------------
st.subheader("Pets")
with st.form("add_pet", clear_on_submit=True):
    st.markdown("**Add a pet**")
    pcol1, pcol2, pcol3 = st.columns(3)
    with pcol1:
        pet_name = st.text_input("Name", value="Mochi")
        pet_gender = st.selectbox("Gender", ["female", "male", "unknown"])
    with pcol2:
        pet_species = st.selectbox("Species", ["dog", "cat", "other"])
        pet_age = st.number_input("Age (years)", min_value=0, max_value=40, value=3)
    with pcol3:
        pet_breed = st.text_input("Breed", value="mixed")
    if st.form_submit_button("Add pet"):
        owner.add_pet(
            Pet(
                name=pet_name,
                species=pet_species,
                breed=pet_breed,
                gender=pet_gender,
                age=int(pet_age),
            )
        )

if owner.pets:
    for pet in owner.pets:
        st.write(f"• {pet.describe()}  — {len(pet.tasks)} task(s)")
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Add a task --------------------------------------------------------------
st.subheader("Tasks")
if not owner.pets:
    st.info("Add a pet before adding tasks.")
else:
    with st.form("add_task", clear_on_submit=True):
        st.markdown("**Add a task**")
        # Map each pet's label to its object so we attach the task to the right one.
        pet_labels = {f"{p.name} ({p.species})": p for p in owner.pets}
        chosen_label = st.selectbox("For which pet?", list(pet_labels))

        tcol1, tcol2 = st.columns(2)
        with tcol1:
            description = st.text_input("Description", value="Morning walk")
            time_minutes = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            due_time = st.text_input("Due time (HH:MM)", value="08:00")
        with tcol2:
            frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly"])
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
            required = st.checkbox("Required (unmissable)", value=False)

        if st.form_submit_button("Add task"):
            pet = pet_labels[chosen_label]
            pet.add_task(
                Task(
                    description=description,
                    time_minutes=int(time_minutes),
                    frequency=frequency,
                    due_time=due_time,
                    required=required,
                    priority=priority,
                )
            )

# Show every task across all pets (owner.all_tasks gathers them for us).
tasks = owner.all_tasks()
if tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "pet": owner.task_owner(t).name if owner.task_owner(t) else "?",
                "description": t.description,
                "due": t.due_time,
                "minutes": t.time_minutes,
                "frequency": t.frequency,
                "priority": t.priority,
                "required": t.required,
            }
            for t in tasks
        ]
    )

st.divider()

# --- Build schedule ----------------------------------------------------------
st.subheader("Build Schedule")
if st.button("Generate schedule", type="primary", disabled=not tasks):
    scheduler = Scheduler(owner=owner)  # reads tasks/time straight from the owner
    st.text(scheduler.explain())
    st.text(scheduler.explain_conflicts())
