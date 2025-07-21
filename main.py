import time
from machine import Pin

IN_PINS = [14, 15, 16, 17]
coil = [Pin(p, Pin.OUT) for p in IN_PINS]

# Hall Effect sensor setup
HALL_PIN = 18
hall_sensor = Pin(HALL_PIN, Pin.IN, Pin.PULL_UP)  # Internal pull-up resistor

# User flag: set to True for half-step mode, False for full-step mode
USE_HALF_STEP = True

STEP_DELAY_MS = 2

if USE_HALF_STEP:
    SEQ = [
        (1, 0, 0, 0),
        (1, 1, 0, 0),
        (0, 1, 0, 0),
        (0, 1, 1, 0),
        (0, 0, 1, 0),
        (0, 0, 1, 1),
        (0, 0, 0, 1),
        (1, 0, 0, 1),
    ]
    STEPS_PER_REV = 4096  # 28BYJ-48 half-step
    STEP_MOD = 8
else:
    SEQ = [
        (1, 0, 0, 0),
        (0, 1, 0, 0),
        (0, 0, 1, 0),
        (0, 0, 0, 1),
    ]
    STEPS_PER_REV = 2048  # 28BYJ-48 full-step
    STEP_MOD = 4

FLAPS = 36
STEPS_PER_FLAP = STEPS_PER_REV // FLAPS  # ≈114 (half-step) or ≈57 (full-step)
step_index = 0

# Flap mapping: 0=Z, 1=Y, ..., 19=G (home), ..., 25=A, 26=9, ..., 35=0
FLAP_CHARS = [str(i) for i in range(10)] + [chr(ord('A') + i) for i in range(26)]
# So: 0=Z, 1=Y, ..., 19=G (home), ..., 25=A, 26=9, ..., 35=0
HOME_INDEX = FLAP_CHARS.index('H')  # 'G' is home

# Remove HOME_OFFSET, add fine-step offset
HOME_OFFSET_STEPS = 30  # Positive = extra steps counterclockwise, negative = clockwise


def step_once(direction=1):
    global step_index
    step_index = (step_index + direction) % STEP_MOD   # wrap-around for 4 or 8 steps
    for pin, val in zip(coil, SEQ[step_index]):
        pin.value(val)

def advance_flap(direction=-1):
    for _ in range(STEPS_PER_FLAP):
        step_once(direction)
        time.sleep_ms(STEP_DELAY_MS)

def release_motor():
    for p in coil:
        p.value(0)

def read_hall_sensor_enhanced(samples=5):
    readings = []
    for _ in range(samples):
        readings.append(hall_sensor.value())
        time.sleep_ms(1)
    return 1 if sum(readings) > len(readings) // 2 else 0

FAST_STEP_DELAY_MS = 1   # Fast approach (try 1 ms or less)
SLOW_STEP_DELAY_MS = 5   # Slow, precise approach (try 5 ms or more)

def home_motor():
    print("Homing motor (fast phase)...")
    release_motor()
    time.sleep_ms(100)
    steps_moved = 0
    max_steps = STEPS_PER_REV * 2

    # Fast phase: move quickly until sensor is triggered
    while steps_moved < max_steps:
        if read_hall_sensor_enhanced() == 0:
            print(f"Sensor triggered after {steps_moved} steps. Switching to slow phase.")
            break
        step_once(-1)
        # time.sleep_ms(FAST_STEP_DELAY_MS)
        steps_moved += 1
    else:
        print("Warning: Could not find home position (fast phase)")
        return False

    # Back off a bit to ensure we approach from the same direction
    for _ in range(5):
        step_once(1)
        time.sleep_ms(SLOW_STEP_DELAY_MS)

    # Slow phase: approach home slowly for precision
    print("Homing motor (slow phase)...")
    for _ in range(STEPS_PER_FLAP):  # Should be more than enough
        if read_hall_sensor_enhanced() == 0:
            print("Precise home found.")
            # Apply fine offset if needed
            for _ in range(abs(HOME_OFFSET_STEPS)):
                step_once(-1 if HOME_OFFSET_STEPS > 0 else 1)
                time.sleep_ms(SLOW_STEP_DELAY_MS)
            print("Pausing at home. Ready for input.")
            return True
        step_once(-1)
        time.sleep_ms(SLOW_STEP_DELAY_MS)
    print("Warning: Could not find home position (slow phase)")
    return False

def get_flap_index_for_char(char):
    char = char.upper()
    if char in FLAP_CHARS:
        return FLAP_CHARS.index(char)
    return None

def move_to_flap(current_index, target_index):
    # Always move counterclockwise (direction = -1)
    delta = (current_index - target_index) % FLAPS
    steps = delta
    direction = -1  # Always counterclockwise
    print(f"[DEBUG] Moving from {FLAP_CHARS[current_index]} (index {current_index}) to {FLAP_CHARS[target_index]} (index {target_index})")
    print(f"[DEBUG] Steps to move (counterclockwise): {steps}")
    for i in range(steps):
        advance_flap(direction)
        print(f"[DEBUG] Step {i+1}/{steps}: Now at index {(current_index - (i+1)) % FLAPS} ({FLAP_CHARS[(current_index - (i+1)) % FLAPS]})")
    return target_index

# At startup, print the flap mapping for verification
print("[DEBUG] Flap mapping (counterclockwise order):")
for idx, char in enumerate(FLAP_CHARS):
    print(f"  Index {idx}: {char}")

print("Split-flap interactive mode. Homing...")

# Home and set current position to HOME_INDEX (no offset)
if not home_motor():
    print("Homing failed. Exiting.")
    release_motor()
    raise SystemExit
current_index = HOME_INDEX

while True:
    user_input = input(f"Enter a letter (A-Z), number (0-9), or HOME to re-home (current: {FLAP_CHARS[current_index]}): ").strip().upper()
    if user_input == '':
        continue
    if user_input == 'HOME':
        print("Re-homing...")
        if home_motor():
            print("Re-homing complete.")
            current_index = HOME_INDEX
        else:
            print("Homing failed. Position may be inaccurate.")
        continue
    target_index = get_flap_index_for_char(user_input)
    if target_index is None:
        print("Invalid input. Please enter A-Z, 0-9, or HOME.")
        continue
    if target_index == current_index:
        print(f"Already at {user_input}.")
        continue
    print(f"Moving to {user_input}...")
    current_index = move_to_flap(current_index, target_index)
    print(f"Now displaying {FLAP_CHARS[current_index]}.")
    release_motor()
