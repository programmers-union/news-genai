import itertools
import threading
import sys
import time

def spinning_cursor():
    spinner = itertools.cycle(["|", "/", "-", "\\"])
    while not stop_loading:
        sys.stdout.write(f"\rLoading... {next(spinner)}")
        sys.stdout.flush()
        time.sleep(0.1)

stop_loading = False
spinner_thread = threading.Thread(target=spinning_cursor)
spinner_thread.start()

# Simulate a long task
time.sleep(5)

stop_loading = True
spinner_thread.join()
sys.stdout.write("\rDone!      \n")
