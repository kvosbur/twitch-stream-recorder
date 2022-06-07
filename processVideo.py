import subprocess
import os
# import time

# before = time.time()
# subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", "00:00:00", "-i", "temp.mp4", "-r", "1", "-q:v", "1", "temp_%04d.jpg"])
# # subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", "00:00:00", "-i", "temp.mp4", "-frames:v", "1", "-q:v", "2", "temp5.jpg"])
# print(time.time() - before)

class FFMPEGReader():

    seek_time = 0  # second to seek to
    mp4_file = "" # mp4 file to read from (absolute path)
    output_directory = "" # directory to write mp4 files to (absolute path)

    def __init__(self, mp4_file, output_directory):
        self.mp4_file = mp4_file
        self.output_directory = output_directory

    def _get_seek_string(self, seek_time):
        seconds = seek_time % 60
        minutes = (seek_time // 60) % 60
        hours = seek_time // 60 // 60
        return f"{hours}:{minutes:02}:{seconds:02}"


    def seek(self, seek_time):
        output_file_name = os.path.join(self.output_directory, "%04d.jpg")
        p = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", "00:00:00", "-i", self.mp4_file, "-r", "1", "-q:v", "1", output_file_name])


t = FFMPEGReader("temp.mp4", ".")
t.seek(0)

