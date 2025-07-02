import struct
import subprocess
import re
import csv




'''
功能：根据GPU架构生成待测指令
输入：（1）arch是字符串，指示GPU的架构
输出：（1）instruction是生成的机器码列表，遍历操作码，其他固定为0
'''
def nv_generate(arch):
    if arch == 'Pascal':
        instruction = [-0x01,-0x10,0x00,0x00,0x00,0x00,0x00,0x00]
        for i in range(256):
            instruction[0] = instruction[0] + 0x01
            for j in range(16):
                instruction[1] = instruction[1] + 0x10
                yield instruction
            instruction[1]=-0x10
            
    else:
        print("instruction set architecture is illegal")




'''
功能：向可执行文件写入数据，写入成功返回0，写入失败返回1
输入：（1）instruction是生成测试的机器码列表
     （2）file_path是可执行文件的路径字符串
     （3）offset是写入指令在可执行文件中的偏移地址
输出：（1）写入成功返回0，写入失败返回1
参考：https://www.cnblogs.com/awsqsh/articles/4379017.html
'''
def nv_write(instruction, file_path, offset):
    with open(file_path, 'rb+') as f:
        f.seek(offset, 0) #设置读写指针
        ins_len = int(len(instruction)*8) #读取指令长度
        if ins_len == 64: #64位指令长度
            ins_byte = len(instruction)
            for i in range( ins_byte ):
                f.write( struct.pack('B', instruction[ins_byte-1-i]) ) 
        elif ins_len == 128: #128位指令长度
            instruction_h = instruction[:8] #128位指令的高64位
            instruction_l = instruction[-8:] #128位指令的低64位
            ins_byte = len(instruction_h)
            for i in range( ins_byte ):
                f.write( struct.pack('B', instruction_h[ins_byte-1-i]) ) 
            for i in range( ins_byte ):
                f.write( struct.pack('B', instruction_l[ins_byte-1-i]) ) 
        else:
            print("instruction length is illegal")
    #f.flush() #强制将缓冲区的数据写入到文件中，可能会导致较低的读写性能
    return 0




'''
功能：反汇编插入待测指令的可执行文件
输入：（1）file_path是可执行文件的路径字符串
输出：（1）反汇编成功返回0,反汇编失败返回1
参考：https://blog.51cto.com/u_16213455/7049281
'''
def nv_dump(file_path):
    #执行cuobjdump,将输出结果重定向到dump.txt文件,最后再读写该文件,效率比较低
    #dump_result = os.system(f'cuobjdump -sass {file_path} > dump.txt') 
    #file_path= r'C:\Users\Administrator\Desktop\NVHI\a.exe',字符串前面需要加r,不然\会被识别为转义符
    #['cuobjdump', '-sass', file_path]命令各个部分需要分开写,写在一起会出错
    #capture_output= True捕获标准输出, text= True输出为文本
    dump_result = subprocess.run( ['cuobjdump', '-sass', file_path], capture_output= True, text= True)
    if dump_result.returncode == 0:
        #print('executable file dump success in nv_dump fuction call')
        return 0, dump_result.stdout
    else:
        #print('executable file dump error in nv_dump fuction call')
        return 1, 'dump error'








'''
从反汇编文本中解析感兴趣的汇编指令,解析成功返回0,解析失败返回1
'''
def nv_extract(dump_file, line):
    if type(line) == type(int()): #参数line是整数类型
        addr = hex(line) #转十六进制字符串形式
    else: #参数line是字符串类型
        addr = line
    #addr=addr.replace('0x', '') #删除十六进制字符串开头的'0x'
    addr=addr[2:]
    
    #元字符*需要//进行转义
    # /\\*  0*  {addr_str}    .*    \\*/
    # /\\*  0*  {addr_str} 匹配每条指令的地址
    # .* 匹配中间的汇编指令和机器码
    # \\*/ 匹配每条指令的机器码的右边界
    assemble_machinecode = re.findall(f'/\\*0*{addr}.*\\*/', dump_file)   
    
    if assemble_machinecode == []: #在cuobjdump反汇编文本中没有匹配到指令
        return 1, 'line not exist'
    else:
        assemble_machinecode = assemble_machinecode[0]
        assemble_machinecode = re.sub('/\\*', '', assemble_machinecode) #替换/*为空格
        assemble_machinecode = re.sub('\\*/', '', assemble_machinecode) #替换*/为空格
        assemble_machinecode = re.sub(';', '', assemble_machinecode) #替换汇编指令末尾的;为空格
        assemble_machinecode = re.split(r'[\s]{2,}', assemble_machinecode) #行号、汇编指令和机器码的分割依据：空格至少出现两次
        #assemble_machinecode是由行号、汇编指令、机器码这3部分组成的列表
        assemble = assemble_machinecode[1]
        return 0, assemble




'''
功能：执行插入待测指令的可执行文件
输入：（1）file_path是可执行文件的路径字符串
输出：（1）执行成功返回0,执行失败返回1
'''
def nv_execute(file_path):
    exec_result = subprocess.run( [file_path], capture_output= True, text= True)
    #print('returncode:', exec_result.returncode)
    if exec_result.returncode == 715: #非法指令错误码
        #print('executable file execute error in nv_exec fuction call')
        return 1
    else: #包含执行成功0，非法内存访问714
        #print('executable file execute success in nv_exec fuction call')
        return 0







'''
保存隐藏指令,写入成功返回0,写入失败返回1
'''
'''
功能：保存测试指令到表格
输入：（1）save_path是可执行文件的路径字符串
     （2）instruction是测试指令的机器码
     （3）dump_en是指示测试指令是否能反汇编
     （4）assemble是测试指令的汇编代码，非法指令的汇编代码是'non-disassemble'
输出：（1）保存成功返回0,保存失败返回1
'''
def nv_save(save_path, instruction, assemble):
    #instruction是列表，将元素合并成字符串
    ins_string = '0x'
    for ins_element in instruction:
        ins_element = hex(ins_element)[2:].zfill(2)#转十六进制字符串形式,并保留前导零
        ins_string = ins_string + ins_element
    
    write_context = [assemble, ins_string]
    
    with open(save_path, 'a+', newline='') as f:
        csv_file = csv.writer(f)
        csv_file.writerow(write_context)












if __name__ == '__main__' :

#暗指令挖掘主要流程
    if 1:
        file_path = r'./cuda_project/a.exe'
        save_path = r'result.csv'
        offset = 0x496A8 #待测指令插入在第一行
        it = nv_generate('Pascal')
        while True: 
            try:
                #1.生成待测指令
                instruction = next(it)  
                print('generate: ', instruction)
                
                #2.写入待测指令到可执行文件
                res = nv_write(instruction, file_path, offset) 
                #print(res)
                
                #3.反汇编可执行文件
                res, stdout = nv_dump(file_path) 
                print(stdout)
                
                #4.反汇编可执行文件
                if res == 0: #可反汇编
                    res,assemble = nv_extract(stdout, line='0x08') #测试指令插在指令流的第一行
                else:#不可反汇编
                    res = nv_execute(file_path)
                    if res == 0: #执行成功，隐藏指令
                        assemble='undocumented'
                    else: #执行失败，无效指令
                        assemble='invalid'
                
                #5.保存测试指令结果
                print(assemble)
                nv_save(save_path, instruction, assemble)
                
            except StopIteration:
                print("StopIteration")
                break
    if 0:
        file_path = r'./cuda_project/a.exe'
        save_path = r'result.csv'
        offset = 0x496A8 #待测指令插入在第一行
        instruction = [0x00, 77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        res = nv_write(instruction, file_path, offset)
        res, stdout = nv_dump(file_path)
        print(stdout)
        if res == 0: #可反汇编
            res,assemble = nv_extract(stdout, line='0x08') #测试指令插在指令流的第一行
        else:#不可反汇编
            res = nv_execute(file_path)
            print(res)
            if res == 0: #执行成功，隐藏指令
                assemble='undocumented'
            else: #执行失败，无效指令
                assemble='invalid'
        print(assemble)
        

    
    