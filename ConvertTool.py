#coding=utf-8 
from crc import crc
from split import split,G_Dict


G_Start_Address = 0x0000E000
G_File_Lenght = 0x00032000
G_End_Address = G_Start_Address + G_File_Lenght
G_COMPATIBILTY = 0x0000A100
G_CRC_START = G_Start_Address
G_CRC_END = G_End_Address - 4

G_Data = []
G_LineStr = []
Next_Address = G_Start_Address


OriginFile = input("Enter S19 file name:")
temp = OriginFile.find('.')
while (temp == -1):
    print("Invalid file name~ Please input again~\r\n")
    OriginFile = input("Enter S19 file name:")
    temp = OriginFile.find('.')

NewFile = 'Converted_' + OriginFile[:temp] + '.s19'
print('Source file name is : ',OriginFile)
print('New source file name is : ',NewFile)

infile = open(OriginFile, "r")
outfile = open(NewFile, "w+")
count = 0

ll = infile.readline()
while ll != '':
    count += 1
    SpitFlag = split(ll)
    #print('ll =',ll)
    if SpitFlag == 0:
        pass
    else: 
        if G_Dict['StoreAddress'] < Next_Address:
            pass
        elif G_Dict['StoreAddress'] == Next_Address:
            if Next_Address < (G_Start_Address + G_File_Lenght):          
                for i in range(len(G_Dict['Code'])):
                    G_Data.append(G_Dict['Code'][i])
                Next_Address = G_Dict['StoreAddress'] + len(G_Dict['Code'])      
        else:
            Ommitbyte = G_Dict['StoreAddress'] - Next_Address
            for i in range(Ommitbyte):
                G_Data.append(255)
            Next_Address = G_Dict['StoreAddress']
            if Next_Address < (G_Start_Address + G_File_Lenght):                
                for i in range(len(G_Dict['Code'])):
                    G_Data.append(G_Dict['Code'][i])
                Next_Address = G_Dict['StoreAddress'] + len(G_Dict['Code'])   
    ll = infile.readline()

if Next_Address < G_End_Address:
    for i in range(G_End_Address - Next_Address):
        G_Data.append(255)

G_Data[-16] = (G_COMPATIBILTY&0xff000000) >> 24
G_Data[-15] = (G_COMPATIBILTY&0x00ff0000) >> 16
G_Data[-14] = (G_COMPATIBILTY&0x0000ff00) >> 8
G_Data[-13] = (G_COMPATIBILTY&0x000000ff) 
G_Data[-12] = (G_CRC_START&0xff000000) >> 24
G_Data[-11] = (G_CRC_START&0x00ff0000) >> 16
G_Data[-10] = (G_CRC_START&0x0000ff00) >> 8
G_Data[-9] = (G_CRC_START&0x000000ff) 
G_Data[-8] = (G_CRC_END&0xff000000) >> 24
G_Data[-7] = (G_CRC_END&0x00ff0000) >> 16
G_Data[-6] = (G_CRC_END&0x0000ff00) >> 8
G_Data[-5] = (G_CRC_END&0x000000ff) 
G_Data[-4] = 0x00
G_Data[-3] = 0x00
CRC16 = crc(G_Data, G_File_Lenght-4, 0xffff)
G_Data[-1] = CRC16&0x00ff
G_Data[-2] = (CRC16&0xff00)>>8


for i in range(int(G_File_Lenght/32)):
    linetype = 'S224'
    tempaddr = i*32 + G_Start_Address
    Addr0 = (tempaddr & 0x00ff0000) >> 16
    Addr1 = (tempaddr & 0x0000ff00) >> 8
    Addr2 = tempaddr & 0x000000ff
    tempdata = G_Data[i*32:i*32+32]
    checksum = 0

    Linestring = linetype
    Linestring += str(hex(Addr0))[2:].zfill(2).upper()
    Linestring += str(hex(Addr1))[2:].zfill(2).upper()
    Linestring += str(hex(Addr2))[2:].zfill(2).upper()

    for j in range(len(tempdata)):
        checksum += tempdata[j]
        Linestring += str(hex(tempdata[j]))[2:].zfill(2).upper()

    checksum = 255 - (checksum + 36 + Addr0 + Addr1 + Addr2)&0xff
    Linestring += str(hex(checksum))[2:].zfill(2).upper()
    Linestring += '\n'
    G_LineStr.append(Linestring)

str_s19 = ''.join(G_LineStr)
outfile.writelines(str_s19)
outfile.flush()
outfile.close()


























































































































###########################################################
'''
S_Start_Line = 'S01100000000486578766965772056312E3108'
S_End_Line = 'S705A0018000D9'
G_Start_Address = 0xA0018000
G_End_Address = 0xA006ffe0
G_Dict = {'RecordType':'S0', 'RecordLength':0, 'StoreAddress':0, 'Code':[0,0,0], 'CheckSum':0}
G_LastLine = 'S325A006FFE0FFFFFFFFFFFFFFFFFFFFFFFFA0018000A006FFEB000012340000A1000000C100BD'
list_s19 = []
code_s19 = []


def S19_CodeSpit(S_Line):
    G_Dict['RecordType'] = S_Line[0:2]
    temp = list(bytearray.fromhex(S_Line[2:4]))
    G_Dict['RecordLength'] = temp[0]

    S_Type = int(S_Line[1])
    S_AddrLen = (S_Type+1)*2
    #S_CodeLen = (int(S_Line[2])*16+int(S_Line[3]))*2 - 2
    S_CodeLen = G_Dict['RecordLength']*2 - 2 

    if S_Type < 1:
        return 0
    elif S_Type > 6:
        return 0
    else:
        G_Dict['StoreAddress'] = bytearray.fromhex(S_Line[4:(4+S_AddrLen)])
        temp = list(G_Dict['StoreAddress'])
        G_Dict['StoreAddress'] = 0
        for i in range(S_Type+1):
            G_Dict['StoreAddress'] += temp[i] << ((S_Type-i) * 8)
    G_Dict['Code'] = list(bytearray.fromhex(S_Line[(4+S_AddrLen):(4+S_CodeLen)]))
    temp = list(bytearray.fromhex(S_Line[(4+S_CodeLen):(4+S_CodeLen+2)]))
    G_Dict['CheckSum'] = temp[0]

    return 1


OriginFile = input("Enter S19 file name:")
NewFile = 'Converted' + OriginFile
print('Source file name is : ',OriginFile)

infile = open(OriginFile,"r")
NewS19 = open(NewFile,"w+")


def S19_Crc16(pdata, DataLen, InitVal):
    i = 0
    index = 0
    crc = InitVal
    
    while DataLen != 0:
        i = 0x80
        #print('index = ',index)
       # print('crc = ',crc)
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
    
    #print('index =',index)
    #print('DataLen =',DataLen)
    #print('CRC =',hex(crc))
    return crc                    
    
def main():
    SpitFlag = 0
    Ommitbyte = 0
    WriteFlag = 1
    crc_byte = []
    
    Next_Address = G_Start_Address
    
    ll = infile.readline()
    while ll != '':

        SpitFlag = S19_CodeSpit(ll)
        #print('ll = ', ll)
        #print('g_dict = ', G_Dict)
        if SpitFlag == 0:
            #list_s19.append(ll)
            pass
        else:      
            if G_Dict['StoreAddress'] < Next_Address:
                #list_s19.append(ll) 
                WriteFlag = 1      
            elif Next_Address == G_Dict['StoreAddress']: 
                if Next_Address < G_End_Address:
                    list_s19.append(ll)
                    WriteFlag = 1
                    Next_Address = G_Dict['RecordLength'] + G_Dict['StoreAddress'] - 5
            else:
                WriteFlag = 0
                Ommitbyte = G_Dict['StoreAddress'] - Next_Address
                CurrentAdd = Next_Address
                zs = Ommitbyte // 32
                ys = Ommitbyte % 32

                for i in range(zs):    
                    CurrentAdd0 = (CurrentAdd & 0xff000000) >> 24
                    CurrentAdd1 = (CurrentAdd & 0x00ff0000) >> 16 
                    CurrentAdd2 = (CurrentAdd & 0x0000ff00) >> 8 
                    CurrentAdd3 = (CurrentAdd & 0x000000ff)       
                    tempcheck = 37 + CurrentAdd0 + CurrentAdd1 + CurrentAdd2 + CurrentAdd3 + 255*32
                    check = 255 - tempcheck & 255                    
                  
                    Add0str = str(hex(CurrentAdd0))[2:].zfill(2).upper()
                    Add1str = str(hex(CurrentAdd1))[2:].zfill(2).upper()
                    Add2str = str(hex(CurrentAdd2))[2:].zfill(2).upper()
                    Add3str = str(hex(CurrentAdd3))[2:].zfill(2).upper()
                    CheckStr = str(hex(check))[2:].zfill(2).upper()

                    tempstr = 'S325' + Add0str + Add1str + Add2str + Add3str + 'FF'*32 + CheckStr + '\n'
                    list_s19.append(tempstr)
                    #print('tempstr = ',tempstr)

                    CurrentAdd += 32

                if ys > 0 :
                    RecordLen = ys + 5
                    CurrentAdd0 = (CurrentAdd & 0xff000000) >> 24
                    CurrentAdd1 = (CurrentAdd & 0x00ff0000) >> 16 
                    CurrentAdd2 = (CurrentAdd & 0x0000ff00) >> 8 
                    CurrentAdd3 = (CurrentAdd & 0x000000ff)       
                    tempcheck = RecordLen + CurrentAdd0 + CurrentAdd1 + CurrentAdd2 + CurrentAdd3 + 255*ys
                    check = 255 - tempcheck & 255         

                    Lenstr = str(hex(RecordLen))[2:].zfill(2).upper()
                    Add0str = str(hex(CurrentAdd0))[2:].zfill(2).upper()
                    Add1str = str(hex(CurrentAdd1))[2:].zfill(2).upper()
                    Add2str = str(hex(CurrentAdd2))[2:].zfill(2).upper()
                    Add3str = str(hex(CurrentAdd3))[2:].zfill(2).upper()
                    CheckStr = str(hex(check))[2:].zfill(2).upper()

                    tempstr = 'S3' + Lenstr + Add0str + Add1str + Add2str + Add3str + 'FF'*ys + CheckStr + '\n'                                        
                    list_s19.append(tempstr)                    
                Next_Address = G_Dict['StoreAddress']                
        
        #read the new line 
        if WriteFlag == 1:
            ll = infile.readline()

    if Next_Address < G_End_Address:
        Ommitbyte = G_End_Address - Next_Address        
        CurrentAdd = Next_Address
        zs = Ommitbyte // 32
        ys = Ommitbyte % 32        
        for i in range(zs):    
            CurrentAdd0 = (CurrentAdd & 0xff000000) >> 24
            CurrentAdd1 = (CurrentAdd & 0x00ff0000) >> 16 
            CurrentAdd2 = (CurrentAdd & 0x0000ff00) >> 8 
            CurrentAdd3 = (CurrentAdd & 0x000000ff)       
            tempcheck = 37 + CurrentAdd0 + CurrentAdd1 + CurrentAdd2 + CurrentAdd3 + 255*32
            check = 255 - tempcheck & 255                    
            
            Add0str = str(hex(CurrentAdd0))[2:].zfill(2).upper()
            Add1str = str(hex(CurrentAdd1))[2:].zfill(2).upper()
            Add2str = str(hex(CurrentAdd2))[2:].zfill(2).upper()
            Add3str = str(hex(CurrentAdd3))[2:].zfill(2).upper()
            CheckStr = str(hex(check))[2:].zfill(2).upper()

            tempstr = 'S325' + Add0str + Add1str + Add2str + Add3str + 'FF'*32 + CheckStr + '\n'
            list_s19.append(tempstr)
            #print('tempstr = ',tempstr)

            CurrentAdd += 32

        if ys > 0 :
            RecordLen = ys + 5
            CurrentAdd0 = (CurrentAdd & 0xff000000) >> 24
            CurrentAdd1 = (CurrentAdd & 0x00ff0000) >> 16 
            CurrentAdd2 = (CurrentAdd & 0x0000ff00) >> 8 
            CurrentAdd3 = (CurrentAdd & 0x000000ff)       
            tempcheck = RecordLen + CurrentAdd0 + CurrentAdd1 + CurrentAdd2 + CurrentAdd3 + 255*ys
            check = 255 - tempcheck & 255         

            Lenstr = str(hex(RecordLen))[2:].zfill(2).upper()
            Add0str = str(hex(CurrentAdd0))[2:].zfill(2).upper()
            Add1str = str(hex(CurrentAdd1))[2:].zfill(2).upper()
            Add2str = str(hex(CurrentAdd2))[2:].zfill(2).upper()
            Add3str = str(hex(CurrentAdd3))[2:].zfill(2).upper()
            CheckStr = str(hex(check))[2:].zfill(2).upper()

            tempstr = 'S3' + Lenstr + Add0str + Add1str + Add2str + Add3str + 'FF'*ys + CheckStr + '\n'                                        
            list_s19.append(tempstr)   

    list_s19.append(G_LastLine)
    str_s19 = ''.join(list_s19)
    NewS19.writelines(str_s19)
    NewS19.flush()            


    NewS19.seek(0,0)
    ss = NewS19.readline()
    Next_Address = G_Start_Address
    while ss != '':
        SpitFlag = S19_CodeSpit(ss)
        if SpitFlag == 0:
            pass
        else:      
            if G_Dict['StoreAddress'] < Next_Address:
                pass
            else:
                crc_byte += G_Dict['Code']  
        ss = NewS19.readline()                


    f = open(NewFile+'.txt', "w+")
    f.writelines(str(crc_byte))
    f.close
    print('check data start = ', crc_byte[:40])
    print('check data = ...',crc_byte[-40:])
    print('data len', len(crc_byte))

    #calculate crc value
    crc = S19_Crc16(crc_byte, (len(crc_byte) - 20), 0xffff) 
    print('new crc =',crc)

    S19_CodeSpit(G_LastLine)
    G_Dict['Code'][-9] = crc & 0xff
    G_Dict['Code'][-10] = (crc & 0xff00) >> 8

    Addr0 = (G_Dict['StoreAddress'] & 0xff000000 ) >> 24
    Addr1 = (G_Dict['StoreAddress'] & 0x00ff0000 ) >> 16
    Addr2 = (G_Dict['StoreAddress'] & 0x0000ff00 ) >> 8
    Addr3 = (G_Dict['StoreAddress'] & 0x000000ff)
    tempcheck = G_Dict['RecordLength'] + Addr0 + Addr1 + Addr2 + Addr3

    for i in range(len(G_Dict['Code'])):
        tempcheck += G_Dict['Code'][i]
    check = 255 - tempcheck & 255
    G_Dict['CheckSum'] = check

    crcstr_H = str(hex(G_Dict['Code'][-10]))[2:].zfill(2).upper()
    crcstr_L = str(hex(G_Dict['Code'][-9]))[2:].zfill(2).upper()
    CheckStr = str(hex(check))[2:].zfill(2).upper()

    tempstr = G_LastLine[:-22] + crcstr_H + crcstr_L + G_LastLine[-18:-2] + CheckStr + '\n'
    #print('last line = ',tempstr)

    NewS19.seek(0,0)
    ss = NewS19.readline()

    #code_s19.append(S_Start_Line)
    while ss != '':
        if ss[4:12] == 'A006FFE0':
            code_s19.append(tempstr)
        else:
            code_s19.append(ss)
        ss = NewS19.readline()    
    #code_s19.append(S_End_Line)

    lastS19 = ''.join(code_s19)
    NewS19.close()
    LastS19 = open(NewFile,"w+")
    LastS19.writelines(lastS19)
    LastS19.flush()
    LastS19.close()  

main()        
'''
