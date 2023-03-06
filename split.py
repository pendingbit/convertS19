G_Dict = {'RecordType':'S0', 'RecordLength':0, 'StoreAddress':0, 'Code':[0,0,0], 'CheckSum':0}

def split(S_Line):
    G_Dict['RecordType'] = S_Line[0:2]
    temp = list(bytearray.fromhex(S_Line[2:4]))
    G_Dict['RecordLength'] = temp[0]

    S_Type = int(S_Line[1])
    S_AddrLen = (S_Type+1)*2
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
