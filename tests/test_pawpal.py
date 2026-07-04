"""Simple tests for PawPal+ core behavior."""

from pawpal_system import Pet, Task


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
