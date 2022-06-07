import subprocess
import time

before = time.time()
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", "00:00:00", "-i", "temp.mp4", "-r", "1", "-q:v", "30", "temp_%04d.jpg"])
# subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", "00:00:00", "-i", "temp.mp4", "-frames:v", "1", "-q:v", "2", "temp5.jpg"])
print(time.time() - before)