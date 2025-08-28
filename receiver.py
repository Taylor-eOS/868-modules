import machine,time
cs=machine.Pin(17,machine.Pin.OUT)
spi=machine.SPI(0,baudrate=500000,polarity=0,phase=0,sck=machine.Pin(18),mosi=machine.Pin(19),miso=machine.Pin(16))
gdo0=machine.Pin(15,machine.Pin.IN)
def strobe(cmd):
    cs.value(0)
    b=bytearray([cmd])
    spi.write_readinto(b,b)
    cs.value(1)
    return b[0]
def read_status_once(addr):
    out=bytearray([addr|0xC0,0x00])
    inp=bytearray(2)
    cs.value(0)
    spi.write_readinto(out,inp)
    cs.value(1)
    return inp[1]
def read_status_stable(addr,tries=8):
    a=read_status_once(addr)
    b=read_status_once(addr)
    while a!=b and tries>0:
        a=b
        b=read_status_once(addr)
        tries-=1
    return b
def write_reg(a,v):
    cs.value(0)
    spi.write(bytearray([a,v]))
    cs.value(1)
def rssi_to_dbm(r):
    if r>=128:
        r=r-256
    return (r/2.0)-72.0
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
    strobe(0x36)
    strobe(0x3A)
    strobe(0x3B)
    strobe(0x34)
init()
while True:
    rx=read_status_stable(0x3B)&0x7F
    pktst=read_status_stable(0x38)
    marc=read_status_stable(0x35)&0x1F
    r=read_status_stable(0x34)
    l=read_status_stable(0x33)
    crc_ok=(l>>7)&1
    if rx>0:
        print("RXBYTES",rx,"PKTSTATUS",hex(pktst),"MARC",hex(marc),"RSSI_dbm",rssi_to_dbm(r),"LQI",l&0x7F,"CRC_OK",crc_ok,"GDO0",gdo0.value())
        strobe(0x36)
        strobe(0x3A)
        strobe(0x3B)
        strobe(0x34)
    time.sleep_ms(50)

