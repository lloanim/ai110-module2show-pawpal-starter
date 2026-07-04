"""PawPal+ system skeleton.

Class stubs generated from diagrams/uml.mmd. Fill in the method bodies as you
implement each feature. Keep this file and the UML diagram in sync.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int

    def describe(self) -> str:
        """Return a human-readable description of this pet."""
        ...


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str

    def priority_score(self) -> int:
        """Return a numeric score used to rank this task."""
        ...


@dataclass
class Owner:
    name: str
    time_available: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        ...

    def add_task(self, task: Task) -> None:
        """Add a task to this owner."""
        ...


@dataclass
class Scheduler:
    tasks: list[Task] = field(default_factory=list)
    time_available: int = 0

    def sort_tasks(self) -> list[Task]:
        """Return the tasks sorted by priority."""
        ...

    def build_plan(self) -> list[Task]:
        """Return the subset of tasks that fit within time_available."""
        ...

    def explain(self) -> str:
        """Return a human-readable explanation of the built plan."""
        ...
