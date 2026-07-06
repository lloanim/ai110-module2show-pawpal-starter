"""PawPal+ system skeleton.

Class stubs generated from diagrams/uml.mmd. Keep this file and the UML diagram in sync.
"""

from __future__ import annotations
import calendar
from dataclasses import dataclass, field, replace
from datetime import date, timedelta


@dataclass
class Task:
    """A single activity for a pet."""

    description: str
    time_minutes: int
    frequency: str                  # e.g. "daily", "weekly", "monthly"
    due_time: str = "08:00"         # "HH:MM" clock time the task starts
    required: bool = False          # unmissable commitment: appointments, meds
    priority: str = "medium"        # "high", "medium", "low" — ranks flexible tasks
    completed: bool = False
    anchor_day: int = 0             # Anchors a recurring task to a day
    due_date: date | None = None    # Calendar date this occurrence is due

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self, today: date | None = None) -> Task | None:
        """Return a fresh, incomplete copy scheduled for this task's next occurrence.

        Daily tasks recur the next day, weekly tasks a week later. The next date is
        computed from the scheduled ``due_date`` (falling back to ``today``), not from
        when the task was actually completed, so a late completion still advances on
        schedule. Returns None for frequencies that don't auto-regenerate (e.g. "monthly").
        """
        
        delta = {"daily": 1, "weekly": 7}.get(self.frequency.strip().lower())
        if delta is None:
            return None
        base = self.due_date or today or date.today()
        return replace(self, completed=False, due_date=base + timedelta(days=delta))


    def start_minutes(self) -> int:
        """Convert the task's start time to minutes since midnight (e.g. "08:30" -> 510)."""
        hours, minutes = (int(part) for part in self.due_time.split(":"))
        return hours * 60 + minutes

    def end_minutes(self) -> int:
        """Compute the task's finish time in minutes since midnight (start + duration)."""
        return self.start_minutes() + self.time_minutes

    def display_time(self) -> str:
        """Return ``due_time`` as a 12-hour label (e.g. "08:00" -> "8:00 AM").

        Formatting only — the stored ``due_time`` stays 24-hour so all
        scheduling math (``start_minutes``, ``overlaps``, sorting) is unchanged.
        """
        hours, minutes = (int(part) for part in self.due_time.split(":"))
        suffix = "AM" if hours < 12 else "PM"
        hour12 = hours % 12 or 12
        return f"{hour12}:{minutes:02d} {suffix}"

    def overlaps(self, other: Task) -> bool:
        """Return True if this task's time window overlaps "other" (another pet's task time) """
        return (
            self.start_minutes() < other.end_minutes()
            and other.start_minutes() < self.end_minutes()
        )

    def importance_level(self) -> int:
        """Map the ``priority`` string to an int, defaulting to medium."""
        levels = {"high": 3, "medium": 2, "low": 1}
        return levels.get(self.priority.strip().lower(), 2)

    def priority_score(self) -> int:
        """Return a numeric rank score: importance dominates, frequency breaks ties.

            Used to order *flexible* tasks (via priority density in ``sort_tasks``);
            required tasks are scheduled regardless of this score.
        """

        frequency = {"daily": 3, "weekly": 2, "monthly": 1}
        freq = frequency.get(self.frequency.strip().lower(), 0)
        return self.importance_level() * 10 + freq

    def is_due_today(self, today: date) -> bool:
        """Return True if this recurring task actually occurs on ``today``.

        "daily" is always due; "weekly" fires when the weekday matches
        ``anchor_day``; "monthly" fires on ``anchor_day`` of the month (clamped
        to the last day, so day 31 still fires in short months). Unknown
        frequencies are treated as always due.
        """
        freq = self.frequency.strip().lower()
        if freq == "weekly":
            return today.weekday() == self.anchor_day
        if freq == "monthly":
            last_day = calendar.monthrange(today.year, today.month)[1]
            target = min(max(self.anchor_day, 1), last_day)
            return today.day == target
        return True  


@dataclass
class Pet:
    """Stores pet details and the list of tasks for this pet."""

    name: str
    species: str
    breed: str
    gender: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task for this pet."""
        self.tasks.append(task)

    def complete_task(self, task: Task, today: date | None = None) -> Task | None:
        """Mark ``task`` done and auto-file its next occurrence (if recurring).

        Because the pet owns the task list, this is where completing a daily or
        weekly task actually schedules the next one. Returns the new task (or
        None if the frequency doesn't recur).
        """
        task.mark_complete()
        nxt = task.next_occurrence(today)
        if nxt is not None:
            self.add_task(nxt)
        return nxt

    def describe(self) -> str:
        """Return a human-readable description of this pet."""
        return (
            f"{self.name} is a {self.age}-year-old {self.gender} "
            f"{self.breed} {self.species}."
        )


@dataclass
class Owner:
    """Manages multiple pets and provides access to all their tasks."""

    name: str
    time_available: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def task_owner(self, task: Task) -> Pet | None:
        """Return the pet a given task belongs to (or None if not found)."""
        for pet in self.pets:
            if task in pet.tasks:
                return pet
        return None


@dataclass
class Scheduler:
    # Read from the Owner so tasks/time_available/preferences stay a single source of truth
    owner: Owner

    @property
    def tasks(self) -> list[Task]:
        """Gathers every task from all of owner's pets"""
        return self.owner.all_tasks()

    @property
    def time_available(self) -> int:
        """Total minutes the owner has available for their pets today"""
        return self.owner.time_available

    def complete_task(self, task: Task, today: date | None = None) -> Task | None:
        """Complete ``task`` via its owning pet so recurrence is auto-filed.

        Delegates to the pet that owns the task (found through the owner). If
        the task belongs to no pet, it's completed but nothing is regenerated.
        """
        pet = self.owner.task_owner(task)
        if pet is None:
            task.mark_complete()
            return None
        return pet.complete_task(task, today)

    def filter_tasks(
        self,
        *,
        pending_only: bool = False,
        frequency: str | None = None,
        pet: Pet | None = None,
        due_on: date | None = None ) -> list[Task]:

        """ Filtering Tasks

            Return the subset of tasks matching every supplied criterion
            ``pet`` selects the source list (that pet's own tasks instead of every task across the owner's pets) 
            ``pending_only`` keeps only incomplete tasks; 
            ``frequency`` keeps a given frequency; 
            ``due_on`` keeps tasks actually occurring on that date (via ``is_due_today``).
        """
                       
        result = pet.tasks if pet is not None else self.tasks
        if pending_only:
            result = [t for t in result if not t.completed]
        if frequency is not None:
            freq = frequency.strip().lower()
            result = [t for t in result if t.frequency.strip().lower() == freq]
        if due_on is not None:
            result = [t for t in result if t.is_due_today(due_on)]
        return result

    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Return tasks in chronological order (earliest start first).

        Ties on start time are broken by importance so the more urgent task
        lists first. Defaults to all pending tasks when none are supplied.
        """
        if tasks is None:
            tasks = self.filter_tasks(pending_only=True)
        return sorted(
            tasks, key=lambda t: (t.start_minutes(), -t.importance_level())
        )

    def sort_tasks(self) -> list[Task]:
        """ Sorting by priority 

        Required (unmissable) tasks come first, then flexible tasks ranked by
        priority *density* (priority_score / time_minutes) with a duration
        tiebreaker so short, high-value tasks aren't crowded out. Reuses
        ``filter_tasks`` to drop completed tasks.
        """

        def density(task: Task) -> float:
            if task.time_minutes <= 0:
                return float("inf")
            return task.priority_score() / task.time_minutes

        pending = self.filter_tasks(pending_only=True)
        return sorted(
            pending,
            key=lambda t: (not t.required, -density(t), t.time_minutes),
        )

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        """Scheduling-conflict detection.

        The owner can only be in one place at a time, so two pending tasks
        conflict when their time windows overlap — *even across different
        pets* 
        Returns each overlapping pair once, ordered by start time.
        """
        pending = self.sort_by_time()
        conflicts: list[tuple[Task, Task]] = []
        for i, task in enumerate(pending):
            for other in pending[i + 1:]:
                if other.start_minutes() >= task.end_minutes():
                    break
                if task.overlaps(other):
                    conflicts.append((task, other))
        return conflicts

    def build_plan(self) -> list[Task]:
        """ Greedy time-budget planning 

        Required tasks are unmissable, so they are always scheduled (even if
        that runs past ``time_available``). The remaining time is then greedily
        filled with flexible tasks, in priority order, that still fit.
        """
        plan: list[Task] = []
        remaining = self.time_available
        for task in self.sort_tasks():
            if task.required or task.time_minutes <= remaining:
                plan.append(task)
                remaining -= task.time_minutes
        return plan

    def explain_conflicts(self) -> str:
        """Return a human-readable report of overlapping tasks across pets."""
        conflicts = self.detect_conflicts()
        if not conflicts:
            return "No scheduling conflicts."

        lines = [f"{len(conflicts)} scheduling conflict(s) found:"]
        for first, second in conflicts:
            first_pet = self.owner.task_owner(first)
            second_pet = self.owner.task_owner(second)
            first_name = first_pet.name if first_pet else "unknown"
            second_name = second_pet.name if second_pet else "unknown"
            lines.append(
                f"  - {first.display_time()} \"{first.description}\" ({first_name}) "
                f"overlaps {second.display_time()} \"{second.description}\" ({second_name})"
            )
        return "\n".join(lines)

    def explain(self) -> str:
        """Return a human-readable explanation of the built plan."""
        plan = self.build_plan()
        if not plan:
            return f"No tasks fit within {self.time_available} minutes."

        used = sum(t.time_minutes for t in plan)
        over = ", over budget for required tasks" if used > self.time_available else ""
        lines = [
            f"Plan for {self.owner.name} "
            f"({used}/{self.time_available} minutes used{over}):"
        ]
        for task in self.sort_by_time(plan):
            pet = self.owner.task_owner(task)
            pet_name = pet.name if pet else "unknown"
            tag = " [required]" if task.required else ""
            lines.append(
                f"  {task.display_time()} {task.description} for {pet_name} "
                f"({task.frequency}, {task.time_minutes} min){tag}"
            )
        return "\n".join(lines)
