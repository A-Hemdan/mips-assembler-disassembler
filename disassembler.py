from bitstring import BitArray

#helper conversion functions
def hex2bin(hex_str, n_bits):
    return bin(int(hex_str, 16))[2:].zfill(n_bits)

def dec2bin(dec, n_bits):
    if int(dec) < 0:
        dec = int(dec)
        b = BitArray(int=dec,length=n_bits)
        return b.bin
    else:
        return bin(int(dec))[2:].zfill(n_bits)

def bin2dec(bin_str, n_bits):
    sign = bin_str[0]
    if sign is '0':
        return int(bin_str,2)
    elif sign is '1':
        comp = int(bin_str[1:],2)
        dec = (2**(n_bits-1)) - comp
        return -1*dec
    

opcode_table = {}
opcode_table['0']   =   {'format':'R'}
opcode_table['8']   =   {'format': 'I', 'operation': 'addi', 'style': 1}
opcode_table['d']   =   {'format': 'I', 'operation': 'or', 'style': 1}
opcode_table['c']   =   {'format': 'I', 'operation': 'andi', 'style': 1}
opcode_table['4']   =   {'format': 'I', 'operation': 'beq', 'style': 5}
opcode_table['5']   =   {'format': 'I', 'operation': 'bne', 'style': 5}
opcode_table['2']   =   {'format': 'J', 'operation': 'j'}
opcode_table['3']   =   {'format': 'J', 'operation': 'jal'}
opcode_table['a']   =   {'format': 'I', 'operation': 'slti', 'style': 1}
opcode_table['2b']  =   {'format': 'I', 'operation': 'sw', 'style': 4}
opcode_table['23']  =   {'format': 'I', 'operation': 'lw', 'style': 4}

reg_table = {}
reg_table[0] = '$zero'
reg_table[1] = '$at'
reg_table[2] = '$v0'
reg_table[3] = '$v1'
reg_table[4] = '$a0'
reg_table[5] = '$a1'
reg_table[6] = '$a2'
reg_table[7] = '$a3'
reg_table[8] = '$t0'
reg_table[9] = '$t1'
reg_table[10] = '$t2'
reg_table[11] = '$t3'
reg_table[12] = '$t4'
reg_table[13] = '$t5'
reg_table[14] = '$t6'
reg_table[15] = '$t7'
reg_table[16] = '$s0'
reg_table[17] = '$s1'
reg_table[18] = '$s2'
reg_table[19] = '$s3'
reg_table[20] = '$s4'
reg_table[21] = '$s5'
reg_table[22] = '$s6'
reg_table[23] = '$s7'
reg_table[24] = '$t8'
reg_table[25] = '$t9'
reg_table[26] = '$k0'
reg_table[27] = '$k1'
reg_table[28] = '$gp'
reg_table[29] = '$sp'
reg_table[30] = '$fp'
reg_table[31] = '$ra'

funct_table = {}
funct_table['20'] = {'operation':'add','style': 0}
funct_table['22'] = {'operation':'sub','style': 0}
funct_table['24'] = {'operation':'and','style': 0}
funct_table['25'] = {'operation':'or','style': 0}
funct_table['27'] = {'operation':'nor','style': 0}
funct_table['2a'] = {'operation':'slt','style': 0}
funct_table['0'] = {'operation':'sll','style': 1}
funct_table['2'] = {'operation':'srl','style': 1}

print 'Welcome to MIPS Disassembler v1.00'
print 'You should input a text file containing MIPS machine code.'
print "Your machine code will be in 'assembly.txt' text file. "
filename = raw_input('Please enter the machine code text file name (e.g. mcode.txt) or its path: ')
mcode_file = open(filename, 'r')
init_address = raw_input('Please enter the initial address of your assembly code in hexadecimal: ')
init_address = int(init_address,16)
PC = init_address #initialize PC
inst_list = []
addresses_list = []
address_table = {} #hashtable containing addresses as keys and labels as values

for line in mcode_file:
    opcode = hex(int(line[0:6],2))[2:] #converting binary opcode to hex and removing leading '0x'
    data = opcode_table[opcode]
    PC += 4
    
    if data['format'] is 'R':
        rs = reg_table[int(line[6:11],2)]
        rt = reg_table[int(line[11:16],2)]
        rd = reg_table[int(line[16:21],2)]
        shamt = int(line[21:26],2)
        funct = hex(int(line[26:32],2))[2:]
        operation = funct_table[funct]['operation']
        style = funct_table[funct]['style']
        
        if style is 0:
            inst = [operation + ' ' + rd + ', ' + rs + ', ' + rt, None]
        if style is 1:
            inst = [operation + ' ' + rd + ', ' + rt + ', ' + str(shamt), None]
        if style is 2:
            inst = [operation + ' ' + rs, None] #list containing instruction (finishied or not) and jumping or branching address if any
        
       
        
    if data['format'] is 'I':
        operation =  data['operation']
        style = data['style']
        rs = reg_table[int(line[6:11],2)]
        rt = reg_table[int(line[11:16],2)]
        imm = str(bin2dec(line[16:],16))
        
        if style is 1:
            inst = [operation + ' ' + rt + ', ' + rs + ', ' + imm, None]
        if style is 3:
            inst = [operation + ' ' + rt + ', ' + imm, None]
        if style is 4:
            inst = [operation + ' ' + rt + ', ' + imm + '(' + rs + ')',None]
        if style is 5:
            address = PC + int(imm)*4
            if address not in addresses_list:
                addresses_list.append(address)
            inst = [operation + ' ' + rs + ', ' + rt + ', ' , address]
    
    if data['format'] is 'J':
        operation = data['operation']
        address = int(line[6:],2) << 2 #shifts address by 2
        address = dec2bin(address,28) #return it to binary form
        address = dec2bin(PC,32)[0:4] + address #concatenate 28 bits of address and the 4 MSBs of PC
        address = int(address,2)
        if address not in addresses_list:
            addresses_list.append(address)
        inst = [operation + ' ' , address]
            
    inst_list.append(inst)

addresses_list.sort() #sorting list of addresses in ascending order

#formulating the address table
i = 1
for address in addresses_list:
    address_table[address] = 'L%d'%i
    i += 1

assembly_file = open('assembly.txt','w') #opening the output file

line_num = 0
for inst in inst_list:
    inst_address = init_address + line_num
    if address_table.get(inst_address) is not None:
        label = address_table.get(inst_address)
    else:
        label = ''
    if inst[1] is None:
        if label is '':
            print inst[0]
            assembly_file.write(inst[0] + '\n')
        else:
            print label + ': ' + inst[0]
            assembly_file.write(label + ': ' + inst[0] + '\n')
    else:
        if label is '':
            print inst[0] + address_table[inst[1]]
            assembly_file.write(inst[0] + address_table[inst[1]] + '\n')
        else:
            print label + ': ' + inst[0] + address_table[inst[1]]
            assembly_file.write(label + ': ' + inst[0] + address_table[inst[1]] + '\n')
    line_num += 4        

assembly_file.close()
