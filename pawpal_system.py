"""PawPal+ system skeleton.

Class stubs generated from diagrams/uml.mmd. Fill in the method bodies as you
implement each feature. Keep this file and the UML diagram in sync.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single activity for a pet."""

    description: str
    time_minutes: int
    frequency: str  # e.g. "daily", "weekly", "monthly"
    due_time: str = "08:00"  # "HH:MM" clock time the task starts
    required: bool = False  # unmissable commitment (appointments, meds, feedings)
    priority: str = "medium"  # "high", "medium", "low" — ranks flexible tasks
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def start_minutes(self) -> int:
        """Return ``due_time`` as minutes since midnight (e.g. "08:30" -> 510)."""
        hours, minutes = (int(part) for part in self.due_time.split(":"))
        return hours * 60 + minutes

    def end_minutes(self) -> int:
        """Return the minute-of-day this task finishes (start + duration)."""
        return self.start_minutes() + self.time_minutes

    def overlaps(self, other: Task) -> bool:
        """Return True if this task's time window overlaps ``other``'s."""
        return (
            self.start_minutes() < other.end_minutes()
            and other.start_minutes() < self.end_minutes()
        )

    def importance_level(self) -> int:
        """Map the ``priority`` string to an int, defaulting to medium."""
        levels = {"high": 3, "medium": 2, "low": 1}
        return levels.get(self.priority.strip().lower(), 2)

    def priority_score(self) -> int:
        """Return a numeric score used to rank this task.

        Importance dominates; frequency breaks ties within the same importance
        tier. (Scaling importance by 10 keeps every high task above every
        medium one.) Used to order *flexible* tasks — required tasks are
        scheduled regardless of this score.
        """
        frequency = {"daily": 3, "weekly": 2, "monthly": 1}
        freq = frequency.get(self.frequency.strip().lower(), 0)
        return self.importance_level() * 10 + freq


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
    # Read from the Owner so tasks/time_available/preferences stay a single
    # source of truth instead of being copied (and drifting) here.
    owner: Owner

    @property
    def tasks(self) -> list[Task]:
        return self.owner.all_tasks()

    @property
    def time_available(self) -> int:
        return self.owner.time_available

    def filter_tasks(
        self,
        *,
        pending_only: bool = False,
        frequency: str | None = None,
        pet: Pet | None = None,
    ) -> list[Task]:
        """Filtering Tasks -

        Return the subset of tasks matching every supplied criterion:
        incomplete-only, a given frequency, and/or belonging to a given pet.
        """
        result = self.tasks
        if pending_only:
            result = [t for t in result if not t.completed]
        if frequency is not None:
            freq = frequency.strip().lower()
            result = [t for t in result if t.frequency.strip().lower() == freq]
        if pet is not None:
            result = [t for t in result if t in pet.tasks]
        return result

    def sort_tasks(self) -> list[Task]:
        """Sorting by priority -

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
        # Required first; then highest density; then shorter duration.
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
        pending = sorted(
            self.filter_tasks(pending_only=True),
            key=lambda t: t.start_minutes(),
        )
        conflicts: list[tuple[Task, Task]] = []
        for i, task in enumerate(pending):
            for other in pending[i + 1:]:
                # Sorted by start, so once `other` starts after `task` ends,
                # nothing later can overlap `task` either.
                if other.start_minutes() >= task.end_minutes():
                    break
                if task.overlaps(other):
                    conflicts.append((task, other))
        return conflicts

    def build_plan(self) -> list[Task]:
        """Greedy time-budget planning -

        Required tasks are unmissable, so they are always scheduled (even if
        that runs past ``time_available``). The remaining time is then greedily
        filled with flexible tasks, in priority order, that still fit.
        """
        pending = self.filter_tasks(pending_only=True)
        required = [t for t in pending if t.required]
        flexible = [t for t in self.sort_tasks() if not t.required]

        plan: list[Task] = list(required)
        remaining = self.time_available - sum(t.time_minutes for t in required)
        for task in flexible:
            if task.time_minutes <= remaining:
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
                f"  - {first.due_time} {first.description} ({first_name}) "
                f"overlaps {second.due_time} {second.description} ({second_name})"
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
        for task in sorted(plan, key=lambda t: t.start_minutes()):
            pet = self.owner.task_owner(task)
            pet_name = pet.name if pet else "unknown"
            tag = " [required]" if task.required else ""
            lines.append(
                f"  {task.due_time} {task.description} for {pet_name} "
                f"({task.frequency}, {task.time_minutes} min){tag}"
            )
        return "\n".join(lines)
