import os, shutil, cv2, numpy as np

def fresh_folder(folder: str):
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.mkdir(folder)

def write_frame_file(count: int, prefix: str, folder: str, hex_digits: str):
    with open(folder+"/"+prefix+str(count), "wb") as file:
        for byte_chunk in [hex_digits[i:i+2] for i in range(0, len(hex_digits), 2)]:
            file.write(bytes([int(byte_chunk,16)]))

def write_config_file(prefix: str, folder: str, fps: int, frames: int, height: int, width: int):
    def write_value(name, value):
        file.write(name + "..." + str(value) + "\n")
    with open(folder+"/"+prefix+"cfg", "w") as file:
        write_value("fps", fps)
        write_value("frames", frames)
        write_value("height", height)
        write_value("width", width)

def save(path: str, prefix="frame_", folder="tw_frames"):
    fresh_folder(folder)

    capture = cv2.VideoCapture(path)
    if not capture.isOpened(): exit()

    print("     Importing Frames...")
    frame_counter = 0
    fps = capture.get(cv2.CAP_PROP_FPS)
    frame_count = capture.get(cv2.CAP_PROP_FRAME_COUNT)

    while True:
        ret, frame = capture.read()
        if not ret:
            print("   |"+50*"█"+"| Done!")
            write_config_file(prefix, folder, fps, frame_counter, height, width)
            break
        height, width, _ = frame.shape

        pixels = []
        hex_content = ""

        for y in range(height):
            for x in range(width):
                pixel = frame[y, x]  # Access pixel (BGR format by default in OpenCV)
                blue, green, red = pixel  # Separate the B, G, R values

                pixels.append(int(red/16))
                pixels.append(int(green/16))
                pixels.append(int(blue/16))
        
        for pixel in pixels:
            hex_content += hex(pixel)[2]
        if (len(hex_content)%2) < 2:
            hex_content += "0"

        write_frame_file(frame_counter, prefix, folder, hex_content)
        frame_counter += 1

        percentage = frame_counter / frame_count

        print(
            "   |"+
            (np.clip(int(percentage*50), 0, 50)*"█")+
            (int(50-np.clip(int(percentage*50), 0, 50))*".")+
            "| " + str(int(percentage*100)) + "%",
            end="\r"
        )

        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break