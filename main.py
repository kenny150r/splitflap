import network, time, socket, machine, random

led = machine.Pin("LED", machine.Pin.OUT)

# Blink while connecting
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("YOUR_SSID", "YOUR_PASSWORD")
while not wlan.isconnected():
    led.toggle()
    time.sleep(random.uniform(0.1, 1.0))
    print("checking connection")
led.on()
print("IP:", wlan.ifconfig()[0])

# Tiny HTTP fetch
addr = socket.getaddrinfo("example.com", 80)[0][-1]
s = socket.socket()
s.connect(addr)
s.send(b"GET / HTTP/1.0\r\nHost: example.com\r\n\r\n")
print(s.recv(200))
s.close()
