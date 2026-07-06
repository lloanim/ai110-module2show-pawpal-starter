# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial UML design consisted of the owner, pet, task, and scheduler. The owner class contains name, time_availablity, prefeerences, pets, tasks, methods add_pet and add_task. The pet class contains name, specied, breed, gender, age, and method description of pet. The task class contains title, duration_minutes, priority, and method priority_score. The last class is scheduler where it contains tasks, time_available, methods sort_tasks, build_plan, and explain. Relationships between the classes are one owner owns many pets, one owner adds multiple tasks, and one scheduler schedules multiple tasks.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

One of the changes made was adding gender to class pet. Another was adding pet to task, so one task is assinged to one pet. Owner was added to scheduler. The relationship changed was one scheduler plans for one owner. This is so the schedule listens from the owner directly on tasks and time_available. A relationship added for multiple tasks assigned to one pet.


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers three things of the task: whether it is required (eg. medication, feeding, or vet appointments), its priority (low/medium/high), and its duration. Required tasks are unmissable so its always scheduled even if the owner runs over their available time. Flexible tasks are scheduled based on priority density (priority score/duration), so a short high-value task is scheduled rather than a long task. Clock time (due_time) is used separately to detect and alert of scheduling conflicts between pet's tasks. I decided that required tasks mattered more than flexible tasks because missing the task of giving medication is a major consequence. The flexible tasks can be adjusted for the next day. 

**b. Tradeoffs**

One tradeoff my scheduler makes is that the ranking flexible tasks by priority density can dismiss long, important tasks in favor of several shorter high value ones. This is a reasonable tradeoff because the required tasks are safe in that it is scheduled and the rest of the time window available can be used by the quicker tasks. 

---

## 3. AI Collaboration

**a. How you used AI**

I had made an initial design of the UML and used AI to make suggestion changes that may be needed. At the beginning I was confused as to what exactly I needed to make this app do but as I went along with AI and the project. I got a better understanding of each class and their methods should do. It helped with debugging the issue of how the tasks should be prioritized and go along with what I wanted to be prioritized more. I did use AI to also refactor the build_plan which made a good suggestion of simplifing it from doing three loops to sort tasks and use sort_tasks() where it has one loop to do the same thing. 
The kind of prompts that where most helpful where the ones where I asked AI to explain the changes it would make. From there I would decide if it fits with what I want to do. 

**b. Judgment and verification**

One moment where I did not accept an AI suggestion was when it suggested to change the logic of the frequency of tasks and how that schedules tasks. It would not prioritize important tasks like a vet appointment because it was labled as a monthly task. So I had it reevaluate the logic of how tasks with frequency are scheduled. But as I went along if I did not understand what it was doing I would ask to explain further.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
