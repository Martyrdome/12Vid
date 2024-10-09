import tw_vid as tv
import kee_api

import sys
import numpy as np

print("")

tv.import_vid.save(sys.argv[1], folder="corruptor_frames")
config = tv.export_vid.read_config("frame_", "corruptor_frames")

print("     Encrypting Frames with KEE...")
for i in range(0, int(config["frames"])):
    kee_api.encrypt_file("corruptor_frames/frame_" + str(i), sys.argv[2], False)

    percentage = i / int(config["frames"])
    print(
        "   |"+
        (np.clip(int(percentage*50), 0, 50)*"█")+
        (int(50-np.clip(int(percentage*50), 0, 50))*".")+
        "| " + str(int(percentage*100)) + "%",
        end="\r"
    )
print("   |"+50*"█"+"| Done!")

tv.export_vid.save("corruption_result.avi", folder="corruptor_frames")

print("")