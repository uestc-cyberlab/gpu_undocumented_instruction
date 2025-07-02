# <center><font size=5> An Instruction-Level Vulnerability on NVIDIA GPUs</font></center>

## <font size=5> I. Introduction</font>

We find an instruction-level vulnerability on NVIDIA Pascal GPUs. Specifically, we apply our testing tool to NVIDIA GTX1050, and have found several undocumented instructions. These undocumented instructions do not belong to the official Pascal Instruction Set (https://docs.nvidia.com/cuda/cuda-binary-utilities/index.html#maxwell-and-pascal-instruction-set), which means they are illegal instructions. However, these instructions can be executed on NVIDIA GPUs without raising any exception, and have strange functions. With this vulnerability, it can cause a calculation error. 

## <font size=5> II. Experiments</font>

We provide a Proof of Concept (POC) to demonstrate this vulnerability. In the POC folder, we provide an undocumented instruction testing tool "NVHI".

**Experimental Setup**

| Operating System |              GPU Model              | CUDA Version |
| :--------------: | :---------------------------------: | :----------: |
|    Windows 10    | NVIDIA GTX1050 (Pascal Arch, SM_61) |     12.2     |

**Undocumented Instruction Mining**

Run the Python script /POC/NVHI/nvhi.py. This tool can generate testing instructions and identify undocumented instructions automatically. Finally, it will report the mining result in /POC/NVHI/result.csv.

```
cd /POC/NVHI
python nvhi.py
```

**Undocumented Instruction Analysis**

From /POC/NVHI/result.cvs, we find several undocumented instructions and list them in the following table. Note that, the instruction length of NVIDIA Pascal GPUs is 64 bits, and the opcode bit field contains 51-63 bits.

|  ID  | Opcode |  Destination Register   |     Source Register      | **Description** |
| :--: | :----: | :---------------------: | :----------------------: | :-------------: |
|  1   | 0x1C8  | Rx, x∈(0~255); 0-7 bits | Ry, y∈(0~255); 8-15 bits |    Rx=Ry - 4    |
|  2   | 0x1CC  | Rx, x∈(0~255); 0-7 bits | Ry, y∈(0~255); 8-15 bits |    Rx=Ry - 4    |
|  3   | 0x1C9  | Rx, x∈(0~255); 0-7 bits | Ry, y∈(0~255); 8-15 bits |    Rx=Ry - 5    |
|  4   | 0x1CA  | Rx, x∈(0~255); 0-7 bits | Ry, y∈(0~255); 8-15 bits |    Rx=Ry - 5    |
|  5   | 0x1CB  | Rx, x∈(0~255); 0-7 bits | Ry, y∈(0~255); 8-15 bits |    Rx=Ry - 4    |
|  6   | 0x1CD  | Rx, x∈(0~255); 0-7 bits | Ry, y∈(0~255); 8-15 bits |    Rx=Ry - 4    |
|  7   | 0x1CE  | Rx, x∈(0~255); 0-7 bits | Ry, y∈(0~255); 8-15 bits |    Rx=Ry - 5    |
|  8   | 0x1CF  | Rx, x∈(0~255); 0-7 bits | Ry, y∈(0~255); 8-15 bits |    Rx=Ry - 5    |

For example, we run the /POC/undocumented instruction analysis//IADD/a.exe, which uses an instruction "IADD R0, R2, R4 ;" (machine code is 0x1800000000470200, and 0x180 is the opcode) to implement integer addition. And its result is "{1,2,3,4,5}+{10,20,30,40,50}={11,22,33,44,55}".

Then, we use the NVIDIA Compilation tool "cuobjdump" (https://docs.nvidia.com/cuda/cuda-binary-utilities/index.html#cuobjdump) to disassemble the above program a.exe. We can find that it uses an instruction "IADD R0, R2, R4 ;" (machine code is 0x1800000000470200, and 0x180 is the opcode) to implement integer addition. 

Next, we modify the IADD's opcode "0x180" to an undocumented instruction's opcode "0x1C8". 

Finally, we run the modified program /POC/undocumented instruction analysis//undocumented instruction analysis/a.exe. We can find that the result has been changed, and the program does not raise any error information.

We provide an animation to present the above process. 

![GPU3](https://github.com/uestc-cyberlab/gpu_undocumented_instruction/blob/main/POC/image/animation.gif)

## Contact

Please contact zhangyang1003@std.uestc.edu.cn for any questions. 

