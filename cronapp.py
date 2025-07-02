import time, threading

from RagFeed import RagFeed
app = RagFeed()

waittime = 3600 # 1h
force = True
def cron():
    global force
    print(f"{time.ctime()} - Start cronJob execution")
    result = app.cronJob(force=force) 
    print(f"{time.ctime()} - Result: {result}")
    threading.Timer(waittime, cron).start()
    force = False # Force update only in first execution

cron()
