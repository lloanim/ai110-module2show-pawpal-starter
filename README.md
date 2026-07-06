# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Today's Schedule
# ------------------
# Plan for Abby (120/120 minutes used):
#  6:00 AM Breakfast for Buddy (daily, 10 min) [required]
#  8:20 AM Morning walk for Buddy (daily, 15 min) [required]
#  10:00 AM Cat Play time! for Lola (weekly, 5 min)
#  10:00 AM Play time! for Buddy (daily, 30 min)
#  5:30 PM Lola's vet appointment for Lola (monthly, 60 min) [required]
# 1 scheduling conflict(s) found:
#  - 10:00 AM "Play time!" (Buddy) overlaps 10:00 AM "Cat Play time!" (Lola)
```

## 🧪 Testing PawPal+

 Tests for recurrence logic, sorting correctness, and conflict detection.

 Confidence Level: 4 stars out of 5

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# collected 16 items                                                                                             
# 
# tests/test_pawpal.py ................                                                                    [100%]
# 
# ============================================== 16 passed in 0.10s ==============================================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | sort_tasks(), sort_by_time() | By priority *density* (value/minute), or chronologically by start time |
| Filtering | filter_tasks() | By pet, frequency, pending-only, or due date |
| Conflict handling | detect_conflicts() | Overlapping time-window detection, even across different pets |
| Recurring tasks | next_occurrence(), is_due_today() | Daily/weekly auto-regenerate; monthly anchored to day-of-month |
| Time-budget planning | build_plan() | Greedy fill: required tasks first, then highest-density tasks that fit |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. You can input your own name and available time (to do pet tasks) as an owner
2. You can then add a pet by adding their name, species, breed, gender, and age. A small description of your pet is added below. 
3. You can add another pet if you like
4. Tasks can then be added based on the pet you want it to apply, description of task, frequency, duration (minutes), priority, you can check off if its a required task, and add the due time of the task. Multiple can be added for different pets. 
5. Below the tasks added are displayed which can be filtered by frequency. It displays the number of tasks, total minutes of the tasks, and how many tasks are required. 
6. The task itself shows what pet it applies to, description, due time, priority, if its required, and a button to check off, if it is done. 
7. If there is a conflict then a message is displayed below tasks and below generated schedule
8. You can click on the build schedule button where it takes all the tasks filters it, sorts it, and displays the best schedule for today. It tells you the plan of the owner for their pets. It gives the time, description, its frequency, duration, and if its required.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
