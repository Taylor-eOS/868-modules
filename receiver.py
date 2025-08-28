import machine
import time
cs = machine.Pin(17, machine.Pin.OUT)
spi = machine.SPI(0, baudrate=500000, polarity=0, phase=0, sck=machine.Pin(18), mosi=machine.Pin(19), miso=machine.Pin(16))
gdo0 = machine.Pin(15, machine.Pin.IN)
def strobe(cmd):
    cs.value(0)
    buf = bytearray([cmd])
    spi.write_readinto(buf, buf)
    cs.value(1)
    return buf[0]
def write_reg(addr, value):
    cs.value(0)
    spi.write(bytearray([addr, value]))
    cs.value(1)
def read_status(addr):
    buf = bytearray([addr | 0x80, 0x00])
    res = bytearray(2)
    cs.value(0)
    spi.write_readinto(buf, res)
    cs.value(1)
    return res[1]
def read_reg_safe(addr):
    v1 = read_status(addr)
    v2 = read_status(addr)
    while v1 != v2:
        v1 = v2
        v2 = read_status(addr)
    return v1
def init():
    cs.value(1)
    time.sleep(0.01)
    strobe(0x30)
    time.sleep(0.02)
    write_reg(0x02, 0x06)
    write_reg(0x04, 0xD3)
    write_reg(0x05, 0x91)
    write_reg(0x06, 8)
    write_reg(0x07, 0x68)
    write_reg(0x08, 0x04)
    write_reg(0x0D, 0x21)
    write_reg(0x0E, 0x62)
    write_reg(0x0F, 0x76)
    write_reg(0x10, 0x8C)
    write_reg(0x11, 0x22)
    write_reg(0x12, 0x02)
    write_reg(0x13, 0x22)
    write_reg(0x15, 0x47)
    write_reg(0x17, 0x30)
    write_reg(0x18, 0x18)
    strobe(0x3A)
    strobe(0x3B)
    strobe(0x34)
def run():
    strobe(0x34)
    while True:
        rxbytes = read_reg_safe(0x3B) & 0x7F
        pktstatus = read_status(0x38)
        marc = read_status(0x35) & 0x1F
        rssi = read_status(0x34)
        lqi = read_status(0x33)
        if rxbytes>0:
            print("RXBYTES", rxbytes, "PKTSTATUS", hex(pktstatus), "MARC", hex(marc), "RSSI", rssi, "LQI", lqi, "GDO0", gdo0.value())
            strobe(0x3A)
            strobe(0x3B)
            strobe(0x34)
        time.sleep(0.05)
init()
run()

