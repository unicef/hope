from subprocess import Popen
from subprocess import call


class RecorderMethod:
    def __init__(self):
        self.ffmpeg_process = None
        self.video_recording = None

    def recorder_start(self, res: str, name: str):
        self.ffmpeg_process = Popen(
            ["ffmpeg", "-video_size", "1920x1080", "-framerate", "30", "-f", "x11grab", "-i", "host.docker.internal:0", "-c:v", "libx264",
             "-preset", "ultrafast", "/code/report/output.mp4"])

    def recorder_stop(self):
        self.ffmpeg_process.terminate()
