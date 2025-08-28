import machine,time
cs=machine.Pin(17,machine.Pin.OUT)
spi=machine.SPI(0,baudrate=500000,polarity=0,phase=0,sck=machine.Pin(18),mosi=machine.Pin(19),miso=machine.Pin(16))
def strobe(cmd):
    cs.value(0)
    b=bytearray([cmd])
    spi.write_readinto(b,b)
    cs.value(1)
    return b[0]
def write_reg(a,v):
    cs.value(0)
    spi.write(bytearray([a,v]))
    cs.value(1)
def write_burst(a,data):
    cs.value(0)
    spi.write(bytearray([a|0x40])+data)
    cs.value(1)
def init():
    cs.value(1)
    time.sleep_ms(20)
    strobe(0x30)
    time.sleep_ms(20)
    write_reg(0x02,0x06)
    write_reg(0x04,0xD3)
    write_reg(0x05,0x91)
    write_reg(0x06,8)
    write_reg(0x07,0x68)
    write_reg(0x08,0x04)
    write_reg(0x0D,0x21)
    write_reg(0x0E,0x62)
    write_reg(0x0F,0x76)
    write_reg(0x10,0x8C)
    write_reg(0x11,0x22)
    write_reg(0x12,0x02)
    write_reg(0x13,0x22)
    write_reg(0x15,0x47)
    write_reg(0x17,0x30)
    write_reg(0x18,0x18)
init()
i=0
while True:
    pkt=f"MSG{i:05d}".encode()[:8]
    if len(pkt)<8:
        pkt=pkt+b'\x00'*(8-len(pkt))
    write_burst(0x3F,pkt)
    time.sleep_ms(5)
    strobe(0x35)
    t0=time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(),t0)<2000:
        s=strobe(0x3D)
        marc=s&0x1F
        if marc==0 and (strobe(0x3D)&0x0F)==0:
            break
        time.sleep_ms(2)
    i+=1
    time.sleep(3)

