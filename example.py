from tw_vid import FileVideoFrameHandler
# FileVideoFrameHandler saves the frames as files, and thus works on larger videos but is slow.
# MemoryVideoFrameHandler saves the frames in memory, and thus only works on smaller videos but is fast.
import numpy as np


def corrupt(frame, _path):
    # frame is a numpy array of shape (height, width, 3).
    # path is the path to the frame file, only available in FileVideoFrameHandler corruption function.
    # Simple corruption function. Invert the color of each pixel.
    return np.invert(frame)


if __name__ == "__main__":
    handler = FileVideoFrameHandler(corruption_function=corrupt)
    handler.process("test.mp4", "test.avi")
    # Alternatively, you can call each step manually. This is mainly used with FileVideoFrameHandler, for using external corruption methods.
    # handler.extract_frames("test.mp4")
    # handler.corrupt_frames() or do.something.else()
    # handler.save("test.avi")
