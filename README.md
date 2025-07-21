# Split-Flap Display





## Wiring: Raspberry Pi Pico W → ULN2003 → 28BYJ‑48

| ULN2003 Pin | Purpose (Motor Coil) | Connect to Pico W | Notes |
|-------------|----------------------|-------------------|-------|
| **IN1**     | Coil A              | **GP14** (physical 19) | Any four consecutive GPIOs work; these are grouped together on the right header. |
| **IN2**     | Coil B              | **GP15** (20) | |
| **IN3**     | Coil C              | **GP16** (21) | |
| **IN4**     | Coil D              | **GP17** (22) | |
| **VCC**     | +5 V motor power    | Pico’s 5 V pin **or** external 5 V/6 V supply | A single 28BYJ‑48 draws ≤ 240 mA; USB power is usually OK. For multiple motors, use a separate 5 V ≥ 1 A adapter. |
| **GND**     | Common ground       | **Any GND** on Pico | **Mandatory** common ground if you power the driver from an external supply. |
| **5‑pin JST** | Motor leads to 28BYJ‑48 | *(already wired)* | No changes needed. |

> **Tip:** If the motor spins the wrong direction, either  
> * swap any two adjacent IN wires **or**  
> * reverse the step sequence in code.

Keep BOOTSEL / GPIO1 free so you don’t accidentally hold the Pico in bootloader mode.
