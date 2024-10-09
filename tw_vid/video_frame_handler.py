import os
import shutil
import cv2
import numpy as np
from tqdm import tqdm
# i am not commenting this shit, sorry.


class FileVideoFrameHandler:
    def __init__(self, prefix="frame_", folder="tw_frames", corruption_function: callable = None):
        self.prefix = prefix
        self.folder = folder
        self.fps = None
        self.frames = 0
        self.height = 0
        self.width = 0
        self.corruption_function = corruption_function

    def fresh_folder(self):
        """Create a fresh directory for storing frames."""
        if os.path.exists(self.folder):
            shutil.rmtree(self.folder)
        os.mkdir(self.folder)

    def write_frame_file(self, count: int, hex_digits: bytes):
        """Write a single frame's hex data to a binary file."""
        frame_path = os.path.join(self.folder, f"{self.prefix}{count}")
        with open(frame_path, "wb") as file:
            file.write(hex_digits)

    def preload_metadata(self, path: str):
        """Preload metadata from a video file."""
        capture = cv2.VideoCapture(path)
        self.fps = capture.get(cv2.CAP_PROP_FPS)
        self.width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        capture.release()

    def extract_frames(self, path: str):
        """Capture video frames and save them as hex data."""
        self.fresh_folder()
        capture = cv2.VideoCapture(path)

        if not capture.isOpened():
            print("Error: Could not open video.")
            return

        self.fps = capture.get(cv2.CAP_PROP_FPS)
        self.width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        frame_counter = 0
        frames_total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

        ret, first_frame = capture.read()
        if not ret:
            print("Error: Could not read the first frame.")
            return

        first_frame_size = first_frame.nbytes

        total_size_bytes = frames_total * first_frame_size
        total_size_gb = total_size_bytes / (1024 ** 3)

        if total_size_bytes > 5 * 1024**3:
            print(f"The total size of the frames will exceed 5GB ({
                  total_size_gb:.2f} GB).")
            confirmation = input("Do you want to continue? (y/n): ")
            if confirmation.lower() != 'y':
                print("Operation canceled by user.")
                capture.release()
                quit()
                return
        with tqdm(total=frames_total, desc="Extracting frames") as pbar:
            hex_digits = first_frame.flatten().tobytes()
            self.write_frame_file(frame_counter, hex_digits)
            frame_counter += 1
            pbar.update(1)

            while True:
                ret, frame = capture.read()
                if not ret:
                    break
                hex_digits = frame.flatten().tobytes()
                self.write_frame_file(frame_counter, hex_digits)

                frame_counter += 1
                pbar.update(1)

        capture.release()
        cv2.destroyAllWindows()
        self.frames = frame_counter

    def read_frame(self, count: int) -> np.array:
        """Read a single frame from binary data."""
        frame_path = os.path.join(self.folder, f"{self.prefix}{count}")
        with open(frame_path, "rb") as file:
            hex_data = file.read()
            np_array = np.frombuffer(hex_data, dtype=np.uint8).reshape(
                self.height, self.width, 3)
        return np_array

    def corrupt_frames(self):
        if self.corruption_function is None:
            return
        for i in tqdm(range(self.frames), desc="Corrupting frames"):
            frame = self.read_frame(i)
            corrupted_frame = self.corruption_function(frame)
            hex_digits = corrupted_frame.flatten().tobytes()
            self.write_frame_file(i, hex_digits)

    def save(self, output_path: str):
        """Create a video from saved frames."""
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video = cv2.VideoWriter(output_path, fourcc,
                                self.fps, (self.width, self.height))

        for i in tqdm(range(self.frames), desc="Collecting frames"):
            frame = self.read_frame(i)
            video.write(frame)

        video.release()

    def process(self, path: str, output_path: str):
        self.extract_frames(path)
        self.corrupt_frames()
        self.save(output_path)
        print("Done!")


class MemoryVideoFrameHandler:
    def __init__(self, corruption_function: callable = None):
        self.fps = None
        self.frames = 0
        self.height = 0
        self.width = 0
        self.corruption_function = corruption_function
        self.hex_frames = []

    def preload_metadata(self, path: str):
        """Preload metadata from a video file."""
        capture = cv2.VideoCapture(path)
        self.fps = capture.get(cv2.CAP_PROP_FPS)
        self.width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        capture.release()

    def extract_frames(self, path: str):
        """Capture video frames and store them in memory."""
        capture = cv2.VideoCapture(path)

        if not capture.isOpened():
            print("Error: Could not open video.")
            return

        self.fps = capture.get(cv2.CAP_PROP_FPS)
        self.width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        frame_counter = 0
        frames_total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

        with tqdm(total=frames_total, desc="Extracting frames") as pbar:
            self.hex_frames = []
            while True:
                ret, frame = capture.read()
                if not ret:
                    self.frames = frame_counter
                    break

                self.hex_frames.append(frame)
                frame_counter += 1
                pbar.update(1)

        capture.release()
        cv2.destroyAllWindows()
        self.frames = frame_counter

    def read_frame(self, count: int) -> np.array:
        """Read a single frame from memory."""
        return self.hex_frames[count]

    def corrupt_frames(self):
        if self.corruption_function is None:
            return
        for i in tqdm(range(self.frames), desc="Corrupting frames"):
            frame = self.read_frame(i)
            corrupted_frame = self.corruption_function(frame)
            self.hex_frames[i] = corrupted_frame

    def save(self, output_path: str):
        """Create a video from frames stored in memory."""
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video = cv2.VideoWriter(output_path, fourcc,
                                self.fps, (self.width, self.height))

        for i in tqdm(range(self.frames), desc="Collecting frames"):
            frame = self.read_frame(i)
            video.write(frame)

        video.release()

    def process(self, path: str, output_path: str):
        self.extract_frames(path)
        self.corrupt_frames()
        self.save(output_path)
        print("Done!")
