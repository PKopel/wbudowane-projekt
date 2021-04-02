import utime

import machine
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
from dht import DHT11

I2C_ADDR     = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

print("Zaczynam działanie")
i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
print(i2c.scan())

lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

sensorPin = machine.Pin(28, machine.Pin.OUT, machine.Pin.PULL_DOWN)
sensor = DHT11(sensorPin)

button1 = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_DOWN)
button2 = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_DOWN)
button3 = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_DOWN)

current = "celsius"

lcd.putstr("Działa!")
utime.sleep(2)
lcd.clear()

while True:
    if button1.value():
        current = "celsius"
    elif button2.value():
        current = "fahr"
    elif button3.value():
        current = "hum"
        
    lcd.clear()
    
    output = "Temp: {} C".format(sensor.temperature)
    
    if current == "fahr":
        output = "Temp: {} F".format(sensor.temperature*1.8 + 32)
    elif current == "hum":
        output = "Hum: {} %".format(sensor.humidity)
        
    lcd.putstr(output)
    utime.sleep(2)
