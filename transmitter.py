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
def write_burst(addr, data):
    cs.value(0)
    spi.write(bytearray([addr | 0x40]) + data)
    cs.value(1)
def read_status(addr):
    buf = bytearray([addr | 0x80, 0x00])
    res = bytearray(2)
    cs.value(0)
    spi.write_readinto(buf, res)
    cs.value(1)
    return res[1]
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
    write_burst(0x3E, bytearray([0x60,0x00,0x00,0x00,0x00,0x00,0x00,0x00]))
    strobe(0x36)
    strobe(0x3B)
    strobe(0x3A)
def tx_once(counter):
    pkt = f"MSG{counter:05d}".encode()
    pkt = pkt[:8] + b'\x00'*(8 - len(pkt))
    if not (strobe(0x36) or True):
        pass
    write_burst(0x3F, pkt)
    time.sleep(0.005)
    strobe(0x35)
    timeout = 2000
    while timeout>0:
        s = strobe(0x3D)
        marc = s & 0x1F
        txbytes = read_status(0x3A) & 0x7F
        if marc==0x13:
            print("TX state")
        if marc==0x01 and txbytes==0:
            return True
        timeout -= 1
        time.sleep(0.001)
    return False
init()
i = 0
while True:
    ok = tx_once(i)
    if ok:
        print("sent", i)
    else:
        print("tx fail", i)
    i += 1
    time.sleep(3)

