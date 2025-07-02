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

|  ID  | Opcode | Destination Register | Source Register | **Description** |
| :--: | :----: | :------------------: | :-------------: | :-------------: |
|  1   |        |                      |                 |                 |























(4) Step 4: Run the victim application again, and we can find that the result has been modified.

```
cd /POC/victim_app
make
./image_segment.o
```

![GPU2](https://github.com/uestc-cyberlab/gpu_kernel_hijack/blob/main/images/malicious.png)

# <font size=5> Conclusion </font>

In the end, we provide an animation to present the above attack process. We can find that our attack method is covert and able to cause malicious code execution.

![GPU3](https://github.com/uestc-cyberlab/gpu_kernel_hijack/blob/main/images/animation.gif)

## Contact

We wrote a paper (A Novel Kernel Hijacking and Trojan Injection Method on Graphics Processing Units) to illustrate this vulnerability. Please contact zhangyang1003@std.uestc.edu.cn for any questions. 

