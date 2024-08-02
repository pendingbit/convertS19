#coding=utf-8 
from crc import crc
from split import split,G_Dict
import os
import glob

'''
        #####
    config start
        ####
'''

#flash range for 7811 mcu 256k(64k+192k) 
G_Start_Address = 0x08010000
G_File_Lenght = 0x00030000

#define compatibilty value
G_COMPATIBILTY = 0x0000A100

G_End_Address = G_Start_Address + G_File_Lenght
G_CRC_START = G_Start_Address
G_CRC_END = G_End_Address - 4

G_Data = []
G_LineStr = []
Next_Address = G_Start_Address

print("")
print(f"Start convert for EH32 Project with AC7811 MCU...\nAPP Start Address = {hex(G_Start_Address)} \nAPP File Lenght = {hex(G_File_Lenght)} \nAPP END Address = {hex(G_End_Address)}")

'''
        #####
    config end
        ####
'''

#Get the target file name
current_path =  os.getcwd()
target_file = glob.glob(os.path.join(current_path, '**', '*.s19'), recursive=True)

if len(target_file) == 0:
    print("No target file, Please add one")
    exit()
elif len(target_file) > 1:
    print("Too many target file, Please remove others")
    exit()

OriginFile = os.path.basename(target_file[0])
temp = OriginFile.find('.')
NewFile = 'Converted_' + OriginFile[:temp] + '.s19'
print('Source file name is : ',OriginFile)
print('New source file name is : ',NewFile)


#open target file and convert file
infile = open(OriginFile, "r")
outfile = open(NewFile, "w+")
count = 0

ll = infile.readline()
while ll != '':
    count += 1
    SpitFlag = split(ll)
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
    linetype = 'S325'
    tempaddr = i*32 + G_Start_Address
    Addr0 = (tempaddr & 0xff000000) >> 24
    Addr1 = (tempaddr & 0x00ff0000) >> 16
    Addr2 = (tempaddr & 0x0000ff00) >> 8
    Addr3 = tempaddr & 0x000000ff

    tempdata = G_Data[i*32:i*32+32]
    checksum = 0

    Linestring = linetype
    Linestring += str(hex(Addr0))[2:].zfill(2).upper()
    Linestring += str(hex(Addr1))[2:].zfill(2).upper()
    Linestring += str(hex(Addr2))[2:].zfill(2).upper()
    Linestring += str(hex(Addr3))[2:].zfill(2).upper()

    for j in range(len(tempdata)):
        checksum += tempdata[j]
        Linestring += str(hex(tempdata[j]))[2:].zfill(2).upper()

    checksum = 255 - (checksum + 37 + Addr0 + Addr1 + Addr2 + Addr3)&0xff
    Linestring += str(hex(checksum))[2:].zfill(2).upper()
    Linestring += '\n'
    G_LineStr.append(Linestring)

str_s19 = ''.join(G_LineStr)
outfile.writelines(str_s19)
outfile.flush()
outfile.close()
print("######\nConvert Target Successful\n######")

























































































































