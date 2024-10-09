"""VideoFrameHandler implementations. Should be imported with `from tw_vid import <type>VideoFrameHandler`."""
import os
import shutil
import cv2
import numpy as np
from tqdm import tqdm
# i am not commenting this shit, sorry.
# you can have some docstrings though :3


class FileVideoFrameHandler:
    """
    A VideoFrameHandler that stores frames in a file system folder.

    Although slower than MemoryVideoFrameHandler, it works on larger videos.

    External corruption methods are supported.

    Attributes
    ----------
    prefix : str
        The prefix to give to the generated frame files.
    folder : str
        The folder to store the frame files in.
    fps : int
        The number of frames per second in the video.
    frames : int
        The number of frames in the video.
    height : int
        The height of the video.
    width : int
        The width of the video.
    corruption_function : callable
        The corruption function to apply to the frames.
    """

    def __init__(self, prefix="frame_", folder="tw_frames", corruption_function: callable = None):
        self.prefix = prefix
        self.folder = folder
        self.fps = None
        self.frames = 0
        self.height = 0
        self.width = 0
        self.corruption_function = corruption_function

    def fresh_folder(self):
        """
        Create a fresh directory for storing frames.

        Remove any existing directory with the same name, and then create a new one.
        """
        if os.path.exists(self.folder):
            shutil.rmtree(self.folder)
        os.mkdir(self.folder)

    def write_frame_file(self, count: int, hex_digits: bytes):
        """
        Write a single frame's hex data to a binary file.

        Parameters
        ----------
        count : int
            The number of the frame to write.
        hex_digits : bytes
            The hex data of the frame to write.

        Returns
        -------
        None
        """
        frame_path = os.path.join(self.folder, f"{self.prefix}{count}")
        with open(frame_path, "wb") as file:
            file.write(hex_digits)

    def preload_metadata(self, path: str):
        """
        Preload metadata from a video file.

        Parameters
        ----------
        path : str
            The path to the video file that you want to process.

        Returns
        -------
        None
        """
        capture = cv2.VideoCapture(path)
        self.fps = capture.get(cv2.CAP_PROP_FPS)
        self.width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        capture.release()

    def extract_frames(self, path: str):
        """
        Capture video frames and save them as hex data.

        This function takes a video file and extracts its frames, saving them
        as binary files. The files are named as '<prefix><number>' and are saved
        in the folder specified in the constructor.

        Parameters
        ----------
        path : str
            The path to the video file to process.

        Returns
        -------
        None
        """
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

        print("Frame extraction complete!")

        capture.release()
        cv2.destroyAllWindows()
        self.frames = frame_counter

    def read_frame(self, count: int) -> np.array:
        """
        Read a single frame from binary data.

        Parameters
        ----------
        count : int
            The number of the frame to read.

        Returns
        -------
        np.array
            The frame as a numpy array.
        """
        frame_path = os.path.join(self.folder, f"{self.prefix}{count}")
        with open(frame_path, "rb") as file:
            hex_data = file.read()
            np_array = np.frombuffer(hex_data, dtype=np.uint8).reshape(
                self.height, self.width, 3)
        return np_array

    def corrupt_frames(self):
        """
        Corrupt the video's frames using this VideoFrameHandler's corruption function.

        This function takes the frames that were extracted from the video
        and saved to files, and uses them to create a new video file with
        the corruption applied.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        if self.corruption_function is None:
            return
        for i in tqdm(range(self.frames), desc="Corrupting frames"):
            frame = self.read_frame(i)
            corrupted_frame = self.corruption_function(
                frame, os.path.join(self.folder, f"{self.prefix}{i}"))
            hex_digits = corrupted_frame.flatten().tobytes()
            self.write_frame_file(i, hex_digits)

        print("Frame corruption complete!")

    def save(self, output_path: str):
        """
        Create a video from saved frames.

        This function takes the frames that were extracted from the video
        and saved to files, and uses them to create a new video file.

        Parameters
        ----------
        output_path : str
            The path to the new video file that will be created.
        """
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video = cv2.VideoWriter(output_path, fourcc,
                                self.fps, (self.width, self.height))

        for i in tqdm(range(self.frames), desc="Collecting frames"):
            frame = self.read_frame(i)
            video.write(frame)

        print("Frame collection complete!")
        video.release()

    def process(self, path: str, output_path: str):
        """
        Do all processing steps, in one function!

        This function will extract frames from a video, corrupt them, and
        then save the corrupted frames to a new video file.

        Parameters
        ----------
        path : str
            The path to the video file that you want to process.
        output_path : str
            The path to the new video file that will be created.

        Returns
        -------
        None
        """
        self.extract_frames(path)
        self.corrupt_frames()
        self.save(output_path)
        print("All processes done!")


class MemoryVideoFrameHandler:
    """
    A VideoFrameHandler that stores frames in memory.

    This is faster than using FileVideoFrameHandler, but only works on smaller videos.

    External corruption methods are not supported.

    Attributes
    ----------
    fps : float
        The frames per second of the video.
    frames : int
        The total number of frames in the video.
    height : int
        The height of the video in pixels.
    width : int
        The width of the video in pixels.
    corruption_function : callable
        A function that takes a frame and returns a corrupted version of the frame.
    hex_frames : list
        A list of the frames as hex data.
    """

    def __init__(self, corruption_function: callable = None):
        self.fps = None
        self.frames = 0
        self.height = 0
        self.width = 0
        self.corruption_function = corruption_function
        self.hex_frames = []

    def preload_metadata(self, path: str):
        """
        Preload metadata from a video file.

        This function is used to preload metadata from a video file without
        actually extracting the frames.

        Parameters
        ----------
        path : str
            The path to the video file that you want to process.

        Returns
        -------
        None
        """
        capture = cv2.VideoCapture(path)
        self.fps = capture.get(cv2.CAP_PROP_FPS)
        self.width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        capture.release()

    def extract_frames(self, path: str):
        """
        Capture video frames and store them in memory.

        This function takes a video file and captures its frames, storing
        them in memory.

        Parameters
        ----------
        path : str
            The path to the video file that you want to process.

        Returns
        -------
        None
        """
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

        print("Frame extraction complete!")

        capture.release()
        cv2.destroyAllWindows()
        self.frames = frame_counter

    def read_frame(self, count: int) -> np.array:
        """
        Read a single frame from memory.

        Parameters
        ----------
        count : int
            The number of the frame to read.

        Returns
        -------
        np.array
            The frame as a numpy array.
        """
        return self.hex_frames[count]

    def corrupt_frames(self):
        """
        Corrupt the video's frames using this VideoFrameHandler's corruption function.

        This function takes the frames that were extracted from the video
        and saved to memory, and uses them to create a new video file with
        the corruption applied.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        if self.corruption_function is None:
            return
        for i in tqdm(range(self.frames), desc="Corrupting frames"):
            frame = self.read_frame(i)
            corrupted_frame = self.corruption_function(frame)
            self.hex_frames[i] = corrupted_frame

        print("Frame corruption complete!")

    def save(self, output_path: str):
        """
        Create a video from frames stored in memory.

        This function takes the frames that were extracted from the video
        and stored in memory, and uses them to create a new video file.

        Parameters
        ----------
        output_path : str
            The path to the new video file that will be created.

        Returns
        -------
        None
        """
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video = cv2.VideoWriter(output_path, fourcc,
                                self.fps, (self.width, self.height))

        for i in tqdm(range(self.frames), desc="Collecting frames"):
            frame = self.read_frame(i)
            video.write(frame)

        print("Frame collection complete!")

        video.release()

    def process(self, path: str, output_path: str):
        """
        Do all processing steps, in one function!

        This function will extract frames from a video, corrupt them, and
        then save the corrupted frames to a new video file.

        Parameters
        ----------
        path : str
            The path to the video file that you want to process.
        output_path : str
            The path to the new video file that will be created.

        Returns
        -------
        None
        """
        self.extract_frames(path)
        self.corrupt_frames()
        self.save(output_path)
        print("All processes done!")
