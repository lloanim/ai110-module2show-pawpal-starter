import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A pet care planning assistant — set up your owner and pets, add tasks, and build a daily plan.")

# --- Session state -----------------------------------------------------------
# The Owner is our single source of truth. It lives in st.session_state so it
# (and all its pets/tasks) persists across Streamlit reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="", time_available=0)

owner = st.session_state.owner  # the actual persisted object — mutating it sticks

# --- Owner setup -------------------------------------------------------------
st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name, placeholder="e.g. Jordan")
with col2:
    time_input = st.number_input(
        "Time available today (minutes)",
        min_value=0,
        max_value=1440,
        value=owner.time_available or None,
        placeholder="e.g. 120",
    )
    owner.time_available = int(time_input) if time_input is not None else 0

st.divider()

# --- Add a pet ---------------------------------------------------------------
st.subheader("Pets")
with st.form("add_pet", clear_on_submit=True):
    st.markdown("**Add a pet**")
    pcol1, pcol2, pcol3 = st.columns(3)
    with pcol1:
        pet_name = st.text_input("Name", value="", placeholder="e.g. Mochi")
        pet_gender = st.selectbox("Gender", ["Female", "Male"])
    with pcol2:
        pet_species = st.selectbox("Species", ["Dog", "Cat", "Other"])
        pet_age = st.number_input("Age (years)", min_value=0, max_value=40, value=None, placeholder="e.g. 3")
    with pcol3:
        pet_breed = st.text_input("Breed", value="", placeholder="e.g. mixed")
    if st.form_submit_button("Add pet"):
        if not pet_name.strip():
            st.warning("Please enter a pet name.")
        else:
            owner.add_pet(
                Pet(
                    name=pet_name,
                    species=pet_species,
                    breed=pet_breed,
                    gender=pet_gender,
                    age=int(pet_age) if pet_age is not None else 0,
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
            description = st.text_input("Description", value="", placeholder="e.g. Morning walk")
            time_minutes = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=None, placeholder="e.g. 20")
            st.markdown("Due time")
            hcol, mcol, apcol = st.columns(3)
            with hcol:
                due_hour = st.selectbox("Hour", list(range(1, 13)), index=7, label_visibility="collapsed")
            with mcol:
                due_minute = st.selectbox("Min", [f"{m:02d}" for m in range(0, 60, 5)], label_visibility="collapsed")
            with apcol:
                due_period = st.selectbox("AM/PM", ["AM", "PM"], label_visibility="collapsed")
            # Convert 12-hour selection to the 24-hour "HH:MM" the scheduler stores.
            hour24 = due_hour % 12 + (12 if due_period == "PM" else 0)
            due_time = f"{hour24:02d}:{due_minute}"
        with tcol2:
            frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly"])
            priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=2)
            required = st.checkbox("Required Task", value=False)

        if st.form_submit_button("Add task"):
            if not description.strip():
                st.warning("Please enter a task description.")
            elif time_minutes is None:
                st.warning("Please enter a duration.")
            else:
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

# The Scheduler reads tasks/time straight from the owner, so it's our single
# source of truth for anything ordering- or conflict-related below.
scheduler = Scheduler(owner=owner)

# Show every task across all pets. The Scheduler filters and orders the data;
# Streamlit components make the result read like a real dashboard.
tasks = owner.all_tasks()
if tasks:
    st.markdown("**Current tasks**")

    # Surface feedback from the last "Done" click (set just before st.rerun).
    if "completed_msg" in st.session_state:
        st.toast(st.session_state.pop("completed_msg"))

    # Filter control — driven straight by Scheduler.filter_tasks().
    freq_filter = st.selectbox(
        "Filter by frequency", ["all", "daily", "weekly", "monthly"]
    )

    # Filter first, then sort chronologically (earliest start first).
    filtered = scheduler.filter_tasks(
        frequency=None if freq_filter == "all" else freq_filter,
    )
    visible = scheduler.sort_by_time(filtered)

    # At-a-glance summary of whatever is currently in view.
    mcol1, mcol2, mcol3 = st.columns(3)
    mcol1.metric("Tasks shown", len(visible))
    mcol2.metric("Total minutes", sum(t.time_minutes for t in visible))
    mcol3.metric("Required", sum(1 for t in visible if t.required))

    if visible:
        # Column layout shared by the header and every task row. A trailing
        # "action" column holds the per-task "Done" button.
        col_weights = [1.5, 3, 1.5, 1, 1.5, 0.9, 1.4]
        header = st.columns(col_weights)
        for c, label in zip(
            header, ["Pet", "Description", "Due", "Min", "Priority", "Req", ""]
        ):
            c.markdown(f"**{label}**")

        for i, t in enumerate(visible):
            pet = owner.task_owner(t)
            row = st.columns(col_weights)
            row[0].write(pet.name if pet else "?")
            row[1].write(t.description)
            row[2].write(t.display_time())
            row[3].write(t.time_minutes)
            row[4].write(t.priority)
            row[5].write("✓" if t.required else "")
            # "Done" removes the task outright — it drops off the list and out
            # of the schedule immediately.
            if row[6].button("Done", key=f"done_{i}"):
                if pet is not None:
                    pet.tasks.remove(t)
                st.session_state.completed_msg = f"✓ '{t.description}' done."
                st.rerun()
    else:
        st.info("No tasks match the current filters.")

    # Conflict status up front: green when clear, amber when tasks overlap.
    if scheduler.detect_conflicts():
        st.warning(scheduler.explain_conflicts())
    else:
        st.success("✅ No scheduling conflicts.")

st.divider()

# --- Build schedule ----------------------------------------------------------
st.subheader("Build Schedule")
if st.button("Generate schedule", type="primary", disabled=not tasks):
    plan = scheduler.build_plan()
    used = sum(t.time_minutes for t in plan)
    if used > scheduler.time_available:
        st.warning(
            f"⚠️ {used}/{scheduler.time_available} min used — over budget for required tasks."
        )
    else:
        st.success(
            f"✅ Plan ready — {used}/{scheduler.time_available} min used, "
            f"{len(plan)} task(s) scheduled."
        )
    st.code(scheduler.explain(), language=None)

    if scheduler.detect_conflicts():
        st.warning(scheduler.explain_conflicts())
