import time
import random

temp = 0
Humid = 0

start = time.time()
print(f"Start time: {start}")
time.sleep(5)
end = time.time()
print(f"Elapsed : {end - start:.2f} second")

num = random.randint(1,10)
print(f"Random number: {num}")