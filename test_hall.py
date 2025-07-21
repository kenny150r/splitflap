# test_hall.py - Simple Hall Effect sensor test
import time
from machine import Pin

# LED setup for status indication
led = Pin("LED", Pin.OUT)

# Hall Effect sensor setup
HALL_PIN = 18
hall_sensor = Pin(HALL_PIN, Pin.IN, Pin.PULL_UP)  # Internal pull-up resistor

def read_hall_sensor_enhanced(samples=5):
    """Read Hall sensor multiple times and return average for better sensitivity."""
    readings = []
    for _ in range(samples):
        readings.append(hall_sensor.value())
        time.sleep_ms(1)  # Brief delay between readings
    
    # Return the most common value (majority vote)
    return 1 if sum(readings) > len(readings) // 2 else 0

# Toggle LED to indicate script is starting
print("Starting Hall Effect Sensor Test...")
for _ in range(3):  # Blink 3 times
    led.on()
    time.sleep(0.2)
    led.off()
    time.sleep(0.2)

print("Hall Effect Sensor Test")
print("Reading sensor value every 0.5 seconds...")
print("Value 1 = No magnet, Value 0 = Magnet detected")
print("Press Ctrl+C to stop")
print("-" * 40)

# Initialize timing
last_print = time.ticks_ms()
print_interval = 5  # 0.5 seconds in milliseconds

while True:
    current_time = time.ticks_ms()
    
    # Print Hall sensor value every 0.5 seconds
    if time.ticks_diff(current_time, last_print) >= print_interval:
        hall_value = read_hall_sensor_enhanced()
        print(f"Hall sensor value: {hall_value}")
        
        # LED on when magnet detected (value = 0), off when no magnet (value = 1)
        if hall_value == 0:
            led.on()
        else:
            led.off()
            
        last_print = current_time
