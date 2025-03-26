from pydobot import Dobot
import time

# Connect to Dobot
port = 'COM9'  # Change if needed
device = Dobot(port=port, verbose=True)
device.speed(130, 100)

# Define the full movement and suction sequence
sequence = [
    (355, 0, 40, 0),    # p1: above first pick
    (355, 0, 10, 0),    # p2: lower to pick
    'suction_on',       # pick
    (355, 0, 40, 0),    # p3: lift

    (220, 0, 40, 0),    # p4: above place
    (220, 0, -47, 0),   # p5: lower to place
    (220, 0, 0, 0),     # p6: lift a bit
    (150, -150, 0, 0),  # p7: move intermediate
    (0, -220, 0, 0),    # p8: final place
    'suction_off',      # release

    (150, -150, 0, 0),  # p9: move back to middle
    (220, -25, 0, 0),   # p10: move to next pick
    (220, -25, -52, 0), # p11: lower to pick
    'suction_on',       # pick
    (220, -25, 40, 0),  # p12: lift

    (355, 0, 40, 0),    # p13: above drop
    (355, 0, 15, 0),    # p14: drop point
    'suction_off',       # release
    (220, 0, 40, 0)
]

# Run sequence
for step in sequence:
    if step == 'suction_on':
        device.suck(True)
        print("🟢 Suction ON")
        time.sleep(1)
    elif step == 'suction_off':
        device.suck(False)
        print("🔴 Suction OFF")
        time.sleep(1)
    else:
        print(f"➡️ Moving to: {step}")
        device.move_to(*step, wait=True)
        time.sleep(0.5)

# Disconnect
device.close()
print("✅ Done.")
