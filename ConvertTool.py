#coding=utf-8 
from crc import crc
from split import split,G_Dict


'''
        #####
    config start
        ####
'''
info = '''
    Target partition:
        1: S32k144 MCU 64K-boot + 448K-app
        2: AC7811 MCU 64K-boot + 192K-app
        
    Please input your selection:'''

select = input(info)

if select == "1":
    #flash range for k144 mcu 512k(64k+448k)
    G_Start_Address = 0x00010000
    G_File_Lenght = 0x00070000
elif select == "2":
    #flash range for 7811 mcu 256k(64k+192k) 
    G_Start_Address = 0x00010000
    G_File_Lenght = 0x00030000
else:
    print("invalid input! Please restart")
    exit()

#define compatibilty value
G_COMPATIBILTY = 0x0000A100

'''
        #####
    config end
        ####
'''


G_End_Address = G_Start_Address + G_File_Lenght
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
    print('ll =',ll)
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

























































































































