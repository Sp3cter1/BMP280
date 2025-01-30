import smbus
from time import sleep

bmp_addr = 0x77
i2c = smbus.SMBus(1)

# Set up the sensor
i2c.write_byte_data(bmp_addr, 0xf5, (5 << 5))  # Standby time 1000 ms
i2c.write_byte_data(bmp_addr, 0xf4, ((5 << 5) | (3 << 0)))  # Normal mode, oversampling x16

# Read calibration data
dig_T1 = i2c.read_word_data(bmp_addr, 0x88)
dig_T2 = i2c.read_word_data(bmp_addr, 0x8A)
dig_T3 = i2c.read_word_data(bmp_addr, 0x8C)
dig_P1 = i2c.read_word_data(bmp_addr, 0x8E)
dig_P2 = i2c.read_word_data(bmp_addr, 0x90)
dig_P3 = i2c.read_word_data(bmp_addr, 0x92)
dig_P4 = i2c.read_word_data(bmp_addr, 0x94)
dig_P5 = i2c.read_word_data(bmp_addr, 0x96)
dig_P6 = i2c.read_word_data(bmp_addr, 0x98)
dig_P7 = i2c.read_word_data(bmp_addr, 0x9A)
dig_P8 = i2c.read_word_data(bmp_addr, 0x9C)
dig_P9 = i2c.read_word_data(bmp_addr, 0x9E)

# Convert to signed integers if needed
if dig_T2 > 32767: dig_T2 -= 65536
if dig_T3 > 32767: dig_T3 -= 65536
if dig_P2 > 32767: dig_P2 -= 65536
if dig_P3 > 32767: dig_P3 -= 65536
if dig_P4 > 32767: dig_P4 -= 65536
if dig_P5 > 32767: dig_P5 -= 65536
if dig_P6 > 32767: dig_P6 -= 65536
if dig_P7 > 32767: dig_P7 -= 65536
if dig_P8 > 32767: dig_P8 -= 65536
if dig_P9 > 32767: dig_P9 -= 65536

while True:
    # Read temperature
    d1 = i2c.read_byte_data(bmp_addr, 0xfa)
    d2 = i2c.read_byte_data(bmp_addr, 0xfb)
    d3 = i2c.read_byte_data(bmp_addr, 0xfc)
    
    adc_T = ((d1 << 16) | (d2 << 8) | d3) >> 4
    
    var1 = ((((adc_T >> 3) - (dig_T1 << 1))) * (dig_T2)) >> 11
    var2 = (((((adc_T >> 4) - (dig_T1)) * ((adc_T >> 4) - (dig_T1))) >> 12) * (dig_T3)) >> 14
    t_fine = var1 + var2
    T = (t_fine * 5 + 128) >> 8
    T = T / 100

    # Read pressure
    p1 = i2c.read_byte_data(bmp_addr, 0xf7)
    p2 = i2c.read_byte_data(bmp_addr, 0xf8)
    p3 = i2c.read_byte_data(bmp_addr, 0xf9)

    adc_P = ((p1 << 16) | (p2 << 8) | p3) >> 4

    var1 = t_fine - 128000
    var2 = var1 * var1 * dig_P6
    var2 = var2 + ((var1 * dig_P5)<<17)
    var2 = var2 + ((dig_P4) << 35)
    var1 = ((var1 * var1 * dig_P3)>>8) + ((var1 * dig_P2)<<12)
    var1 = ((((1)<<47)+ var1)) * (dig_P1)>>33
    if var1 == 0:
            print("var1 is 0")
            
    p = (1048576 - adc_P)
    p = (((p<<31) - var2) * 3125)/ var1
    print(type(p))
    var1 = ((dig_P9) * (int(p) >> 13) * (int(p) >> 13)) >> 25
    var2 = ((dig_P8) * int(p)) >> 19
    p = ((int(p) + var1 + var2) >> 8) + ((dig_P7)<<4)
    
    # Correct the pressure range if necessary
    if p < 1000:  # pressure should be above 1000 Pa
        p = 101325  # default to sea level pressure if calculation fails

    # Calculate altitude
    P0 = 101325  # Sea level pressure in Pa (adjust based on location)
    altitude = 44330 * (1 - (p / P0) ** (1 / 5.255))

    print(f"Temperature: {T:.2f} °C")
    print(f"Pressure: {p:.2f} Pa")
    print(f"Altitude: {altitude:.2f} meters")
    
    sleep(1)
