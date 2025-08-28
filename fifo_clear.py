import machine
import time
cs = machine.Pin(17, machine.Pin.OUT)
spi = machine.SPI(0, baudrate=500000, polarity=0, phase=0, sck=machine.Pin(18), mosi=machine.Pin(19), miso=machine.Pin(16))
gdo0 = machine.Pin(15, machine.Pin.IN)
cs.value(1)
time.sleep(0.2)

def strobe(cmd):
    cs.value(0)
    buf = bytearray([cmd])
    spi.write_readinto(buf, buf)
    cs.value(1)
    return buf[0]

def read_status(addr):
    buf_out = bytearray([addr | 0xC0, 0x00])
    buf_in = bytearray(2)
    cs.value(0)
    time.sleep_us(5)
    spi.write_readinto(buf_out, buf_in)
    cs.value(1)
    return buf_in[1]

def read_reg(addr):
    buf_out = bytearray([addr | 0x80, 0x00])
    buf_in = bytearray(2)
    cs.value(0)
    time.sleep_us(5)
    spi.write_readinto(buf_out, buf_in)
    cs.value(1)
    return buf_in[1]

def write_reg(addr, value):
    cs.value(0)
    time.sleep_us(5)
    spi.write(bytearray([addr, value]))
    cs.value(1)
    time.sleep_us(5)

def write_burst(addr, data):
    cs.value(0)
    time.sleep_us(5)
    spi.write(bytearray([addr | 0x40]) + data)
    cs.value(1)
    time.sleep_us(5)

def errata_fifo_recovery():
    for attempt in range(6):
        print("recovery attempt", attempt+1)
        strobe(0x36)
        time.sleep_ms(10)
        marc = read_status(0x35) & 0x1F
        print("  MARCSTATE =", hex(marc))
        strobe(0x3A)
        strobe(0x3B)
        time.sleep_ms(10)
        rx = read_status(0x3B) & 0x7F
        tx = read_status(0x3A) & 0x7F
        print("  after flush RX/TX =", rx, tx)
        if rx == 0 and tx == 0:
            return True
        print("  not cleared, issuing SRES and retrying")
        strobe(0x30)
        time.sleep_ms(80)
        strobe(0x36)
        time.sleep_ms(10)
    return False

def test_fifo_cycle():
    print("initial status readback")
    rx0 = read_status(0x3B) & 0x7F
    tx0 = read_status(0x3A) & 0x7F
    print("  RX0/TX0 =", rx0, tx0)
    ok = errata_fifo_recovery()
    print("recovery finished:", ok)
    rx1 = read_status(0x3B) & 0x7F
    tx1 = read_status(0x3A) & 0x7F
    print("  RX1/TX1 =", rx1, tx1)
    pkt = b'PING1234'
    write_burst(0x3F, pkt)
    time.sleep_ms(10)
    tx2 = read_status(0x3A) & 0x7F
    print("  After write TX count =", tx2)
    strobe(0x3A)
    strobe(0x3B)
    time.sleep_ms(10)
    rx3 = read_status(0x3B) & 0x7F
    tx3 = read_status(0x3A) & 0x7F
    print("  After final flush RX/TX =", rx3, tx3)
    return ok and tx2 > 0

print("running FIFO clear test")
result = test_fifo_cycle()
print("test result =", result)

