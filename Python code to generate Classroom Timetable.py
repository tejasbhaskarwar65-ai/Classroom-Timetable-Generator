DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
days = int(input("Days: "))
per_day = int(input("Periods per day: "))
n = int(input("Number of subjects: "))

left = {}                                   # subject -> periods left
for i in range(n):
    name = input("Subject name: ")
    left[name] = int(input("Periods: "))

total = sum(left.values())
if total != days * per_day:
    print(f"Error: Total weekly periods ({total}) must equal available slots ({days * per_day}).")
elif max(left.values()) > days * 2:
    bad = max(left, key=left.get)
    print(f"Timetable cannot be generated: {bad} needs {left[bad]} periods in {days} day, but the limit is 2 per day.")
else:
    for d in range(days):
        today = []
        for _ in range(per_day):
            options = [s for s in left if left[s] > 0 and today.count(s) < 2]
            best = max(options, key=left.get)   # most periods left; ties -> entered first
            today.append(best)
            left[best] -= 1
        print(DAYS[d] + ": " + ", ".join(today))