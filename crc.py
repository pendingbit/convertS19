
#crc function
def S19_Crc16(pdata, DataLen, InitVal):
    i = 0
    index = 0
    crc = InitVal
    
    while DataLen != 0:
        i = 0x80
        while i != 0:
            #print('i =',i)
            if (crc & 0x8000) != 0:
                crc <<= 1
                crc ^= 0x1021
            else:
                crc <<= 1
                
            if (pdata[index] & i) != 0:
                crc ^= 0x1021
            crc &= 0xffff    
                
            i >>= 1
            
        index += 1    
        DataLen -= 1
    
    return crc       


def crc(pdata, DataLen, InitVal):    
    return S19_Crc16(pdata, DataLen, InitVal)
