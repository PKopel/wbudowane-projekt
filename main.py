import utime
import machine
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
from dht import DHT11
from bmx280 import BMX280
from mq7 import MQ7
from BaseMQ import BaseMQ

I2C_ADDR_LCD = 0x27
I2C_ADDR_BMP = 0x76
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

print("Zaczynam działanie")
        
sensorPin = machine.Pin(28, machine.Pin.OUT, machine.Pin.PULL_DOWN)
sensor = DHT11(sensorPin)

mq7sensor = MQ7(pinData = 27, baseVoltage = 3.3, measuringStrategy=BaseMQ.STRATEGY_FAST)

button1 = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_DOWN)
button2 = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_DOWN)
button3 = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_DOWN)
button4 = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_DOWN)

i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
i2c_scan = i2c.scan()
print(i2c_scan)

i2c_bmp = machine.I2C(1, sda=machine.Pin(6), scl=machine.Pin(7), freq=400000)
i2c_bmp_scan = i2c_bmp.scan()
print(i2c_bmp_scan)

save_file = open("measurements.txt", "a")

def save_measurement(measurement: str):
    (year, month, mday, hour, minute, second, _, _) = utime.localtime()
    timestamp = "{}.{}.{} {}:{}:{}".format(mday,month,year,hour,minute,second)
    msg = "{}\n{}\n".format(timestamp, measurement)
    save_file.write(msg)
    save_file.flush()
    utime.sleep(20)

print_fun = save_measurement

if len(i2c_scan) > 0 and i2c_scan[0] == I2C_ADDR_LCD:
    lcd = I2cLcd(i2c, I2C_ADDR_LCD, I2C_NUM_ROWS, I2C_NUM_COLS)
    def print_lcd(msg: str):
        lcd.clear()
        lcd.putstr(msg)
        utime.sleep(2)
    print_fun = print_lcd

press_fun = None

if len(i2c_bmp_scan) > 0 and i2c_bmp_scan[0] == I2C_ADDR_BMP:
    bmp = BMX280(i2c_bmp, I2C_ADDR_BMP)
    def press():
        return bmp.pressure
    press_fun = press

def fahr_format(temp: float) -> str:
    return "Temp: {} F".format(round(temp*1.8 + 32, 2))

def celsius_format(temp: float) -> str:
    return "Temp: {} C".format(temp)

def hum_format(hum: float) -> str:
    return "Hum: {} %".format(hum)

def press_format(press: float) -> str:
    return "Press.: {} hPa".format(press)

def co_format(co: float) -> str:
    if co == -1:
        return "Wait until first\nmeasure is done"
    
    return "CO level:\n{} ppm".format(co)

def run_station():
    current = "celsius"
    print_fun("It works!")
    mq7sensor.calibrate()
    
    #main loop
    while True:
        if button1.value():
            current = "celsius"
        elif button2.value():
            current = "fahr"
        elif button3.value() and press_fun != None:
            current = "press"
        elif button4.value():
            current = "co"
        
        if current == "press":
            output = "{}\n".format(press_format(round(press_fun()/100)))
        elif current == "co":
            co_level = round(mq7sensor.readCarbonMonoxide(), 2)
            output = "{}".format(co_format(co_level))
        else:
            temp = round(sensor.temperature, 2)
            hum = round(sensor.humidity, 2)
            output_temp = fahr_format(temp) if current == "fahr" else celsius_format(temp)
            output_hum = hum_format(hum)
            output = "{}\n{}".format(output_temp, output_hum)
            
        print_fun(output)
        
run_station()
