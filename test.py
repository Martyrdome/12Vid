import time

for i in range(0,51):
    print("   |"+i*"█"+(50-i)*" "+"| " + str(i*2) + "%", end="\r")
    time.sleep(1)
print("\n")