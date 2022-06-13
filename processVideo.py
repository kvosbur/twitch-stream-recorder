from csv import reader
import subprocess
import os
import time
import shutil
import streamlink
import threading
import queue

def remove_file_if_exists(file):
    if os.path.exists(file):
        os.remove(file)

def clear_folder(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.mkdir(folder)

class FFMPEGReader():

    seek_time = 0  # second to seek to
    mp4_file = "" # mp4 file to read from (absolute path)
    output_directory = "" # directory to write mp4 files to (absolute path)
    process = None  # process doing frame capture

    def __init__(self, mp4_file, output_directory):
        self.mp4_file = mp4_file
        self.output_directory = output_directory

    def _get_seek_string(self, seek_time):
        seconds = seek_time % 60
        minutes = (seek_time // 60) % 60
        hours = seek_time // 60 // 60
        return f"{hours}:{minutes:02}:{seconds:02}"

    def is_seek_finished(self):
        return self.process is None or self.process.poll() is not None

    def seek(self, seek_time):
        print("SEEKING", seek_time)
        output_file_name = os.path.join(self.output_directory, "%05d.jpg")
        seek_string = self._get_seek_string(seek_time)
        self.process = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", seek_string, "-i", self.mp4_file, "-r", "1", "-q:v", "1", output_file_name])


class FileTracker:
    frame_count = 0  # count of number of frames seen
    # next_seek = 0  # the second to do next seek at
    reader = None  # reader object
    working_directory = ""  # directory the reader will output files to
    output_directory = ""  # directory that files will be moved to
    interval = 10 # minimum amount of seconds till next reader seek
    end_queue = None # queue to check whether work should continue

    def __init__(self, reader: FFMPEGReader, working_directory, output_directory, end_queue):
        self.reader = reader
        self.working_directory = working_directory
        self.output_directory = output_directory
        self.end_queue = end_queue

    def move_file(self, source, dest):
        try:
            shutil.move(source, dest)
        except:
            time.sleep(0.05)
            self.move_file(source, dest)

    def remove_file(self, file):
        try:
            os.remove(file)
        except:
            time.sleep(0.05)
            self.remove_file(file)

    def work(self):
        skip_frames = self.frame_count > 6
        print("skip framges, count", skip_frames, self.frame_count)
        seek_val = self.frame_count - 6 if skip_frames else self.frame_count
        print("seek value", seek_val)
        self.reader.seek(seek_val)
        begin = time.time()
        iteration_count = 1
        while not self.reader.is_seek_finished():
            if len(os.listdir(self.working_directory)) > 0:
                next_file = os.path.join(self.working_directory, f"{iteration_count:05}.jpg")
                # check if next expected file exists
                if os.path.exists(next_file):
                    # delete first file found since it is duplicate of second
                    if iteration_count == 1 or (skip_frames and iteration_count <= 6):
                        self.remove_file(next_file)
                        iteration_count += 1
                        continue

                    # move file to destination to be processed
                    new_file_name = os.path.join(self.output_directory, f"{self.frame_count:05}.jpg")
                    self.move_file(next_file, new_file_name)
                    self.frame_count += 1
                    iteration_count += 1
                    print("MOVED", next_file, " TO ", new_file_name)

        elapsed = time.time() - begin
        wait_for = self.interval - elapsed
        if wait_for > 0:
            print(wait_for)
            time.sleep(wait_for)
        
        print(self.frame_count, iteration_count)
        if self.end_queue.qsize() == 0:
            self.work()
        else:
            print("FINISH")


shoot_stream = "https://twitch.tv/shoot2thr1ll284"
temp_stream = "https://www.twitch.tv/shivfps"
wanted_stream = '1080p60'

def get_stream_data(q):
    streams = streamlink.streams(shoot_stream)

    my_stream = streams[wanted_stream]
    count = 0

    with open("temp.mp4", 'ab') as g:
        with my_stream.open() as f:
            while q.qsize() == 0:
                g.write(f.read(1000000))
                count += 1


def stop_all(q):
    time.sleep(120*60)
    q.put(1)


remove_file_if_exists("temp.mp4")
clear_folder("data")
clear_folder("result_images")


q = queue.Queue()
t = threading.Thread(target=get_stream_data, args=(q,))
t.start()

t = threading.Thread(target=stop_all, args=(q,))
t.start()

reader = FFMPEGReader("temp.mp4", "data")
tracker = FileTracker(reader, "data", "result_images", q)
tracker.work()

