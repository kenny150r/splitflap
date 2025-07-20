import time
from machine import Pin

IN_PINS = [14, 15, 16, 17]
coil = [Pin(p, Pin.OUT) for p in IN_PINS]

SEQ = [                       # full‑step, two‑coil
    (1, 0, 0, 0),
    (0, 1, 0, 0),
    (0, 0, 1, 0),
    (0, 0, 0, 1),
]

STEP_DELAY_MS = 4             # 4 ms ≈ 10 RPM
STEPS_PER_REV = 2048         # 28BYJ-48 full-step
FLAPS = 36
STEPS_PER_FLAP = STEPS_PER_REV // FLAPS  # ≈57 steps per flap
step_index = 0

def step_once(direction=1):
    global step_index
    step_index = (step_index + direction) & 3   # 0‑3 wrap‑around
    for pin, val in zip(coil, SEQ[step_index]):
        pin.value(val)

def advance_one_flap():
    """Advance exactly one flap."""
    for _ in range(STEPS_PER_FLAP):
        step_once(-1)  # Counter-clockwise
        time.sleep_ms(STEP_DELAY_MS)

def release_motor():
    for p in coil:
        p.value(0)

print("One flap every 10 seconds, 36 flaps per revolution")
while True:
    advance_one_flap()
    release_motor()
    time.sleep(0.3)
