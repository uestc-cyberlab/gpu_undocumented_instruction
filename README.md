# <center><font size=5> A Kernel Hijacking Vulnerability on NVIDIA GPUs</font></center>

## <font size=5> I. Introduction</font>

We found a kernel hijacking vulnerability on NVIDIA GPUs. Through manipulating the invocation mechanism of the CUDA driver functions, attackers can craft a disguised CUDA kernel loading API (**cuModuleLoad()**) to hijack the GPU kernel. With this vulnerability, attacks can implant malicious logic into the hijacked kernel, causing malicious code execution. 

## <font size=5> II. Exploitation</font>

We provide a Proof of Concept (POC) to demonstrate this vulnerability. In the POC folder, we provide a GPU-based victim application and an attack tool to hijack the victim's GPU kernel.

**Experimental Setup**

| Operating System |              GPU Model              | CUDA Version |
| :--------------: | :---------------------------------: | :----------: |
|  Ubuntu 2022.04  | NVIDIA GTX1050 (Pascal Arch, SM_61) |     12.2     |

**Reproduction Steps**

(1) Step 1: Run the victim application. We provide an image processing case in /POC/victim_app.

```
cd /POC/victim_app
make
./image_segment.o
```

![GPU1](https://github.com/uestc-cyberlab/gpu_kernel_hijack/blob/main/images/reference.png)

(2) Step 2: Compile the attack tool and generate a disguised CUDA kernel loading API (**cuModuleLoad()**). In the disguised API, we implant a Trojan into the hijacked kernel. In addition, we package the disguised API into a dynamic link library (image_hijack.so).

```
cd /POC/hijack_tool
make
```

(3) Step 3: Manipulate the invocation mechanism of the dynamic link library (DLL), and preload the malicious API to replace the legitimate API call.

​	(3.1) Manipulate the DLL preloading environment variable (LD_PRELOAD), or

```
LD_PRELOAD=./image_hijack.so
```

​	(3.2) Manipulate the DLL preloading configuration file (ld.so.preload).

```
cp image_hijack.so /usr/lib
vim /etc/ld.so.preload
/usr/lib/image_hijack.so
```

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

