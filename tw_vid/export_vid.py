import binascii
import cv2, numpy as np

def read_config(prefix: str, folder: str) -> object:
    result = {}
    with open(folder+"/"+prefix+"cfg", "r") as file:
        for line in file.read().split("\n"):
            if line == "": continue
            line = line.split("...")
            result[line[0]] = float(line[1])
    return result

def read_frame(count: int, prefix: str, folder: str, config: dict) -> np.array:
    result = []
    with open(folder+"/"+prefix+str(count), "rb") as file:
        hex_data = binascii.hexlify(file.read())
        hex_codes = [hex_data[i:i+3] for i in range(0, len(hex_data), 3)]
        for color in hex_codes:
            color = str(color)[2:5]
            if color[2] != "'": # fuck single quotes (this took us 30 fucking minutes)
                result.append([int(color[2], 16)*16, int(color[1], 16)*16, int(color[0], 16)*16])
    np_array = np.array(result, dtype=np.uint8)
    np_array = np_array.reshape(int(config["height"]), int(config["width"]), 3)
    return np_array

def save(path: str, prefix="frame_", folder="tw_frames"):
    config = read_config(prefix, folder)
    frames = []
    for i in range(0, int(config["frames"])):
        frames.append(read_frame(i, prefix, folder, config))
        #print("Finished frame " + str(i))

        cv2.imshow("frame", frames[-1])
        if cv2.waitKey(1) & 0xFF == ord("q"):
           break
    
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoWriter(path, fourcc, config["fps"], (int(config["width"]), int(config["height"])))
    for frame in frames:
        video.write(frame)
    video.release()
