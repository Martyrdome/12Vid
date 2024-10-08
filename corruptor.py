import tw_vid as tv
import kee_api

import sys

tv.import_vid.save(sys.argv[1], folder="corruptor_frames")
config = tv.export_vid.read_config("frame_", "corruptor_frames")
for i in range(0, int(config["frames"])):
    kee_api.encrypt_file("corruptor_frames/frame_" + str(i), sys.argv[2], False)
    # print("Encrypted frame " + str(i))
tv.export_vid.save("corruption_result.avi", folder="corruptor_frames")
for i in range(0, int(config["frames"])):
    kee_api.encrypt_file("corruptor_frames/frame_" + str(i), sys.argv[2], True)
    # print("Decrypted frame " + str(i))