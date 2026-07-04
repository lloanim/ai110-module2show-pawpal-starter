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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

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
