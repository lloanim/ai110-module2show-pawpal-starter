"""Simple tests for PawPal+ core behavior."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    """Task Completion: mark_complete() flips a task from pending to done."""
    task = Task(description="Walk Buddy", time_minutes=30, frequency="daily")

    assert task.completed is False  # starts incomplete
    task.mark_complete()
    assert task.completed is True  # now marked done


def test_add_task_increases_pet_task_count():
    """Task Addition: adding a task grows the pet's task list by one."""
    pet = Pet(name="Buddy", species="dog", breed="Lab", gender="male", age=3)
    task = Task(description="Feed Buddy", time_minutes=10, frequency="daily")

    assert len(pet.tasks) == 0  # no tasks yet
    pet.add_task(task)
    assert len(pet.tasks) == 1  # one task after adding


def test_next_occurrence_advances_daily_by_one_day():
    """Recurring: completing a daily task's next occurrence is today + 1 day."""
    task = Task(description="Feed", time_minutes=10, frequency="daily")
    nxt = task.next_occurrence(today=date(2026, 7, 5))
    assert nxt is not None
    assert nxt.due_date == date(2026, 7, 6)
    assert nxt.completed is False


def test_next_occurrence_chains_from_own_due_date():
    """Recurring: a late-completed task advances from its scheduled due_date."""
    # Scheduled for Jul 5 but completed on Jul 9 -> next is Jul 6, not Jul 10.
    task = Task(description="Feed", time_minutes=10, frequency="daily", due_date=date(2026, 7, 5))
    nxt = task.next_occurrence(today=date(2026, 7, 9))
    assert nxt is not None
    assert nxt.due_date == date(2026, 7, 6)


def test_next_occurrence_advances_weekly_by_seven_days():
    """Recurring: a weekly task's next occurrence is today + 7 days."""
    task = Task(description="Groom", time_minutes=30, frequency="weekly", anchor_day=0)
    nxt = task.next_occurrence(today=date(2026, 7, 5))
    assert nxt is not None
    assert nxt.due_date == date(2026, 7, 12)


def test_next_occurrence_none_for_monthly():
    """Recurring: monthly tasks don't auto-regenerate on completion."""
    task = Task(description="Flea meds", time_minutes=5, frequency="monthly", anchor_day=31)
    assert task.next_occurrence(today=date(2026, 7, 5)) is None


def test_pet_complete_task_files_next_occurrence():
    """Recurring: completing a daily task through the pet auto-adds the next one."""
    pet = Pet(name="Buddy", species="dog", breed="Lab", gender="male", age=3)
    task = Task(description="Walk", time_minutes=20, frequency="daily")
    pet.add_task(task)

    nxt = pet.complete_task(task, today=date(2026, 7, 5))
    assert task.completed is True  # original marked done
    assert nxt in pet.tasks  # next occurrence filed automatically
    assert len(pet.tasks) == 2
    assert nxt.due_date == date(2026, 7, 6)


def test_scheduler_complete_task_delegates_to_owning_pet():
    """Recurring: Scheduler.complete_task files recurrence via the owning pet."""
    task = Task(description="Feed", time_minutes=10, frequency="daily")
    scheduler = Scheduler(owner=_owner_with_tasks(task))

    nxt = scheduler.complete_task(task, today=date(2026, 7, 5))
    assert task.completed is True
    assert nxt is not None
    assert nxt.due_date == date(2026, 7, 6)
    assert nxt in scheduler.owner.pets[0].tasks


def test_daily_task_is_always_due():
    """Recurring: a daily task fires on any date."""
    task = Task(description="Walk", time_minutes=20, frequency="daily")
    assert task.is_due_today(date(2026, 7, 5)) is True


def test_weekly_task_fires_only_on_anchor_weekday():
    """Recurring: a weekly task fires only on its anchor weekday."""
    # 2026-07-06 is a Monday (weekday 0); 2026-07-07 is a Tuesday.
    task = Task(description="Groom", time_minutes=30, frequency="weekly", anchor_day=0)
    assert task.is_due_today(date(2026, 7, 6)) is True
    assert task.is_due_today(date(2026, 7, 7)) is False


def test_monthly_task_clamps_to_month_end():
    """Recurring: a day-31 monthly task still fires on Feb's last day."""
    task = Task(description="Flea meds", time_minutes=5, frequency="monthly", anchor_day=31)
    assert task.is_due_today(date(2026, 2, 28)) is True  # clamped from 31
    assert task.is_due_today(date(2026, 2, 27)) is False


def test_display_time_formats_as_twelve_hour():
    """Display: due_time renders as a 12-hour AM/PM label without changing math."""
    cases = {
        "00:00": "12:00 AM",  # midnight
        "08:00": "8:00 AM",
        "12:00": "12:00 PM",  # noon
        "13:05": "1:05 PM",   # minutes keep leading zero
        "23:59": "11:59 PM",
    }
    for due_time, expected in cases.items():
        task = Task(description="Feed", time_minutes=10, frequency="daily", due_time=due_time)
        assert task.display_time() == expected
        # stored due_time stays 24-hour so scheduling math is untouched
        assert task.due_time == due_time


def _owner_with_tasks(*tasks: Task) -> Owner:
    owner = Owner(name="Jordan", time_available=240)
    pet = Pet(name="Mochi", species="cat", breed="mixed", gender="female", age=3)
    for t in tasks:
        pet.add_task(t)
    owner.add_pet(pet)
    return owner


def test_sort_by_time_orders_chronologically():
    """Sorting: sort_by_time() returns tasks earliest-start first."""
    late = Task(description="Evening walk", time_minutes=20, frequency="daily", due_time="18:00")
    early = Task(description="Breakfast", time_minutes=10, frequency="daily", due_time="07:00")
    scheduler = Scheduler(owner=_owner_with_tasks(late, early))

    ordered = scheduler.sort_by_time()
    assert [t.description for t in ordered] == ["Breakfast", "Evening walk"]


def test_filter_tasks_by_due_date():
    """Filtering: due_on surfaces only tasks occurring that day."""
    daily = Task(description="Feed", time_minutes=10, frequency="daily")
    weekly = Task(
        description="Groom", time_minutes=30, frequency="weekly", anchor_day=0
    )  # Mondays only
    scheduler = Scheduler(owner=_owner_with_tasks(daily, weekly))

    tuesday = scheduler.filter_tasks(due_on=date(2026, 7, 7))  # a Tuesday
    assert [t.description for t in tuesday] == ["Feed"]
