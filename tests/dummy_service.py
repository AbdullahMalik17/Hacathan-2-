import time
import sys
import signal
import os

def handle_sig(sig, frame):
    print("Dummy service received signal, exiting")
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sig)

print("Dummy service started")
# Write PID to file for test verification
with open("dummy_service.pid", "w") as f:
    f.write(str(os.getpid()))

while True:
    time.sleep(1)
