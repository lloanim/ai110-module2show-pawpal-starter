from pawpal_system import Owner, Pet, Task, Scheduler

owner = Owner("Abby", time_available=120)
dog = Pet("Buddy", species="dog", breed="Labrador", gender="male", age=3)
cat = Pet("Lola", species="cat", breed="Tabby", gender="female", age=5)

owner.add_pet(dog)
owner.add_pet(cat)

# Required tasks are unmissable and always scheduled.
breakfast = Task("Breakfast", 10, "daily", due_time="06:00", required=True)
walk = Task("Morning walk", 15, "daily", due_time="08:20", required=True)
vet = Task("Lola's vet appointment", 60, "monthly", due_time="17:30", required=True)

# Flexible tasks fill whatever time is left, ranked by priority.
play = Task("Play time!", 30, "daily", due_time="10:00", priority="low")
play2 = Task("Cat Play time!", 5, "weekly", due_time="10:00", priority="low")

dog.add_task(walk)
dog.add_task(play)
cat.add_task(vet)
dog.add_task(breakfast)
cat.add_task(play2)

print("Today's Schedule")
print("------------------")
scheduler = Scheduler(owner)
print(scheduler.explain())

print(scheduler.explain_conflicts())

