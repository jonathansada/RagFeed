import time
from RagFeed import RagFeed
app = RagFeed()

waittime = 3600 # 1h
force = True
while True:
    print(f"{time.ctime()} - Start cronJob execution")
    result = app.cronJob(force=force) 
    print(f"{time.ctime()} - Result: {result}")
    time.sleep(waittime)
    force = False # Force update only in first execution
