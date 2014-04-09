from pyparsing import *
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

#MIPS Instruction Set hashtable

#style indicates the number of operands and their type as follows:-
#style : 0 -> operation reg,reg,reg
#style : 1 -> operation reg,reg,integer
#style : 2 -> operation reg
#style : 3 -> operation reg,integer
#style : 4 -> operation reg,intger(reg)
#style : 5 -> operation reg,reg,address

operations = {}
operations['add']   =   {'format': 'R', 'opcode': '0', 'style': 0, 'funct': '20'}
operations['addi']  =   {'format': 'I', 'opcode': '8', 'style': 1}
operations['addiu'] =   {'format': 'I', 'opcode': '9', 'style': 1}
operations['addu']  =   {'format': 'R', 'opcode': '0', 'style': 0, 'funct': '21'}
operations['and']   =   {'format': 'R', 'opcode': '0', 'style': 0, 'funct': '24'}
operations['andi']  =   {'format': 'I', 'opcode': 'c', 'style': 1}
operations['beq']   =   {'format': 'I', 'opcode': '4', 'style': 5}
operations['bne']   =   {'format': 'I', 'opcode': '5', 'style': 5}
operations['j']     =   {'format': 'J', 'opcode': '2'}
operations['jal']   =   {'format': 'J', 'opcode': '3'}
operations['jr']    =   {'format': 'R', 'opcode': '0', 'style': 2, 'funct': '08'}
operations['lbu']   =   {'format': 'I', 'opcode': '24', 'style': 4}
operations['lhu']   =   {'format': 'I', 'opcode': '25', 'style': 4}
operations['ll']    =   {'format': 'I', 'opcode': '30', 'style': 1}
operations['lui']   =   {'format': 'I', 'opcode': 'f', 'style': 3}
operations['lw']    =   {'format': 'I', 'opcode': '23', 'style': 4}
operations['nor']   =   {'format': 'R', 'opcode': '0', 'style': 0, 'funct': '27'}
operations['or']    =   {'format': 'R', 'opcode': '0', 'style': 0, 'funct': '25'}
operations['ori']   =   {'format': 'I', 'opcode': 'd', 'style': 1}
operations['slt']   =   {'format': 'R', 'opcode': '0', 'style': 0, 'funct': '2a'}
operations['slti']  =   {'format': 'I', 'opcode': 'a', 'style': 1}
operations['sltu']  =   {'format': 'R', 'opcode': '0', 'style': 0, 'funct': '2b'}
operations['sll']   =   {'format': 'R', 'opcode': '0', 'style': 1, 'funct': '00'}
operations['srl']   =   {'format': 'R', 'opcode': '0', 'style': 1, 'funct': '02'}
operations['sb']    =   {'format': 'I', 'opcode': '28', 'style': 4}
operations['sc']    =   {'format': 'I', 'opcode': '38', 'style': 4}
operations['sh']    =   {'format': 'I', 'opcode': '29', 'style': 4}
operations['sw']    =   {'format': 'I', 'opcode': '2b', 'style': 4}
operations['sub']   =   {'format': 'R', 'opcode': '0', 'style': 0, 'funct': '22'}
operations['subu']  =   {'format': 'R', 'opcode': '0', 'style': 0, 'funct': '23'}

valid_operations = operations.keys()

#Classifying operations
R0 = []
R1 = []
R2 = []
I1 = []
I3 = []
I4 = []
I5 = []
J = []
for oper in valid_operations:
    current_oper = operations[oper]
    if current_oper['format'] is 'R':
        if current_oper['style'] is 0: R0.append(oper)
        if current_oper['style'] is 1: R1.append(oper)
        if current_oper['style'] is 2: R2.append(oper)
        
    if current_oper['format'] is 'I':
        if current_oper['style'] is 1: I1.append(oper)
        if current_oper['style'] is 3: I3.append(oper)
        if current_oper['style'] is 4: I4.append(oper)
        if current_oper['style'] is 5: I5.append(oper)
    
    if current_oper['format'] is 'J': J.append(oper) 


#Registers hashtable
regs = {}
regs['$zero']=0
regs['$at']=1
regs['$v0']=2
regs['$2']=2
regs['$v1']=3
for x in range(0,4):
    regs['$a%d'%x]= (x+4)
for x in range(0,8):
    regs['$t%d'%x]= (x+8)
    regs['$s%d'%x]= (x+16)
for y in range(8,10):
    regs['$t%d'%y]=(y+24)
for z in range(0,2):
    regs['$k%d'%z]=(z+26)
regs['$gp']=28
regs['$sp']=29
regs['$fp']=30
regs['$ra']=31
for s in range(0,31):
    regs['$%d'%s]=s
regs[''] = 0
    
valid_regs = list(regs.keys())
valid_regs.remove('')


#setting grammer rules for parsing

identifier =  Word(alphas+"_",alphanums+"_")
reg = oneOf(valid_regs)
comma = Suppress(',')
number = Combine(Optional('-') + Word(nums))
EOL = OneOrMore(LineEnd())

Label = identifier.setResultsName("label") + Suppress(":")
reg_rs = reg.setResultsName('rs')
reg_rt = reg.setResultsName('rt')
reg_rd = reg.setResultsName('rd')
imm_value = number.setResultsName('imm')
addr = identifier.setResultsName("address")

R_format = (oneOf(R0).setResultsName('operation') + White() + reg_rd + comma + reg_rs + comma + reg_rt) ^\
           (oneOf(R1).setResultsName('operation') + White() + reg_rd + comma + reg_rt + comma + number.setResultsName('shamt')) ^\
           (oneOf(R2).setResultsName('operation') + White() + reg_rs)

I_format = (oneOf(I1).setResultsName('operation') + White() + reg_rt + comma + reg_rs + comma + imm_value) ^\
           (oneOf(I3).setResultsName('operation') + White() + reg_rt + comma + imm_value) ^\
           (oneOf(I4).setResultsName('operation') + White() + reg_rt + comma + imm_value + Suppress('(') + reg_rs + Suppress(')')) ^\
           (oneOf(I5).setResultsName('operation') + White() + reg_rs + comma + reg_rt + comma + addr)

J_format = oneOf(J).setResultsName('operation') + White() + addr

Instruction =   ((Label) + (R_format ^ I_format ^ J_format)) ^\
                (Label) ^ (R_format ^ I_format ^ J_format) ^ EOL.setResultsName('EOL')

Instruction.ignore(pythonStyleComment)

#Reading and Parsing assembly input file

print 'Welcome to MIPS Assembler v1.00'
print 'You should input a text file containing MIPS assembly code.'
print "Your machine code will be in 'mcode_file.txt' text file while Hex code will be printed on console. "
filename = raw_input('Please enter the assembly text file name (e.g. assembly.txt) or path: ')
init_address = raw_input('Please enter the initial address of your assembly code in hexadecimal: ')

assembly_file = open(filename, 'r')

Memory = []
Labels = {}

line_address = int(init_address,16)
for line in assembly_file:
    current_inst = Instruction.parseString(line)
    if len(current_inst) == 0: 
        continue
    if current_inst[0] == '\n': 
        continue
    Memory.append(current_inst)
    if current_inst.label is not '':
        if current_inst.operation is not '': 
            Labels[current_inst.label] = line_address
        else :  
            Labels[current_inst.label] = line_address
            continue
    line_address += 4 

assembly_file.close()

#Assembling the parsed code

mcode_file = open('mcode_file.txt','w') #opening the output file
PC = int(init_address,16)   #converting PC to decimal for ease of use to be used in arithmatic operations
for inst in Memory:
    if inst.operation is '':
        continue
    op = operations[inst.operation]
    PC += 4
    
    if op['format'] is 'R':
        opcode = op['opcode']
        funct = op['funct']
        if inst.shamt is not '': shamt = inst.shamt
        else: shamt = 0
        rs_code = regs[inst.rs]
        rt_code = regs[inst.rt]
        rd_code = regs[inst.rd]
        inst_mcode = hex2bin(opcode,6) + dec2bin(rs_code,5) + dec2bin(rt_code,5) + dec2bin(rd_code,5) +\
                     dec2bin(shamt,5) + hex2bin(funct,6)
        mcode_file.write(inst_mcode + '\n')
        print hex(int(inst_mcode,2))
        
    if op['format'] is 'I':
        opcode = op['opcode']
        rs_code = regs[inst.rs]
        rt_code = regs[inst.rt]
        if inst.imm is not '': imm = inst.imm
        else:
            address = Labels[inst.address]
            imm = (address - PC)/4
        inst_mcode = hex2bin(opcode,6) + dec2bin(rs_code,5) + dec2bin(rt_code,5) + dec2bin(imm,16)
        mcode_file.write(inst_mcode + '\n')
        print hex(int(inst_mcode,2))
        
    if op['format'] is 'J':
        opcode = op['opcode']
        address = Labels[inst.address]
        address = dec2bin(address,32)
        address = address[4:]
        address = int(address,2)
        address = address/4
        address = dec2bin(address,26)
        inst_mcode = hex2bin(opcode,6) + address
        mcode_file.write(inst_mcode + '\n')
        print hex(int(inst_mcode,2))
        
mcode_file.close()
