import time
import random

print("--- Python script started! ---")

# Simulate some work
sleep_time = random.randint(1, 3)
print(f"Simulating a task that takes {sleep_time} seconds...")
time.sleep(sleep_time)

# Simulate a calculation
result = 19 * 22
print(f"Calculation complete. The result is {result}.")

print("--- Python script finished! ---")