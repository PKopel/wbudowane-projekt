import utime

import machine
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
from dht import DHT11

I2C_ADDR     = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

print("Zaczynam działanie")
        
sensorPin = machine.Pin(28, machine.Pin.OUT, machine.Pin.PULL_DOWN)
sensor = DHT11(sensorPin)

button1 = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_DOWN)
button2 = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_DOWN)

i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
i2c_scan = i2c.scan()

save_file = open("measurements.txt", "a")

def save_measurement(measurement: str):
    (year, month, mday, hour, minute, second, _, _) = utime.localtime()
    timestamp = "{}.{}.{} {}:{}:{}".format(mday,month,year,hour,minute,second)
    msg = "{}\n{}\n".format(timestamp, measurement)
    save_file.write(msg)
    save_file.flush()
    utime.sleep(20)

print_fun = save_measurement

if len(i2c_scan) > 0 and i2c_scan[0] == I2C_ADDR:
    lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
    def print_lcd(msg: str):
        lcd.clear()
        lcd.putstr(msg)
        utime.sleep(2)
    print_fun = print_lcd

def fahr_format(temp: float) -> str:
    return "Temp: {} F".format(temp*1.8 + 32)

def celsius_format(temp: float) -> str:
    return "Temp: {} C".format(temp)

def hum_format(hum: float) -> str:
    return "Hum: {} %".format(hum)

def run_station():
    current = "celsius"
    print_fun("Działa!")
    utime.sleep(2)
    #main loop
    while True:
        if button1.value():
            current = "celsius"
        elif button2.value():
            current = "fahr"
        
        temp = sensor.temperature
        hum = sensor.humidity
        output_temp = fahr_format(temp) if current == "fahr" else celsius_format(temp)
        output_hum = hum_format(hum)
        
        output = "{}\n{}".format(output_temp, output_hum)
            
        print_fun(output)

run_station()