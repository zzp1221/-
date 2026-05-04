"""Batch 4 Part 4: 40 VIDEO resources."""
from knowledge.import_pipeline import run_import

RESOURCES = []

# ═══════════════════════════════════════════════════════════════
# 1. 操作系统 (3 resources)
# ═══════════════════════════════════════════════════════════════

RESOURCES.append({
    "title": "王道考研操作系统全程精讲",
    "description": "王道考研操作系统经典全程班视频，覆盖操作系统五大核心模块：进程管理、内存管理、文件系统、I/O系统、死锁与同步。408考研必看课程，讲解透彻，例题丰富。",
    "course": "操作系统", "chapter": "操作系统概论", "difficulty": "INTERMEDIATE",
    "type": "VIDEO",
    "tags": ["操作系统", "考研", "进程管理", "内存管理", "文件系统", "PV操作", "银行家算法"],
    "source_url": "https://www.bilibili.com/video/BV1YE411D7nH",
    "content": """# 王道考研操作系统全程精讲

**视频来源**: bilibili — 王道计算机教育
**时长**: 约50小时（含全部章节）
**语言**: 中文
**内容概要**:
- 操作系统概论：OS定义、发展历程、分类与结构
- 进程与线程：进程状态、PCB、上下文切换、线程模型
- 处理机调度：FCFS/SJF/HRRN/时间片轮转/多级反馈队列
- 进程同步：临界区、信号量、PV操作、经典同步问题
- 死锁：必要条件、预防、避免（银行家算法）、检测与恢复
- 内存管理：连续分配、分页、分段、段页式、虚拟内存
- 页面置换：OPT/FIFO/LRU/Clock/改进Clock算法
- 文件系统：文件结构、目录、inode、空闲空间管理
- I/O系统：I/O控制方式、缓冲、SPOOLing技术
- 历年408真题精讲与考点总结

**适合人群**: 计算机考研学生、操作系统入门学习者、准备面试的开发者
**推荐理由**: 王道考研系列是408计算机考研的标杆课程，讲解体系化、重点突出、例题贴近真题。适合考研复习第一轮系统学习使用。

---
*来源: https://www.bilibili.com/video/BV1YE411D7nH*"""
})

RESOURCES.append({
    "title": "MIT 6.828 Operating System Engineering",
    "description": "MIT经典操作系统课程，通过实现一个完整的操作系统内核（xv6），深入理解进程管理、虚拟内存、文件系统、中断处理等核心机制。2020年更新版本6.S081基于RISC-V架构。",
    "course": "操作系统", "chapter": "操作系统设计与实现", "difficulty": "ADVANCED",
    "type": "VIDEO",
    "tags": ["操作系统", "MIT", "内核", "xv6", "RISC-V", "虚拟内存", "系统调用"],
    "source_url": "https://ocw.mit.edu/courses/6-828-operating-system-engineering-fall-2012/",
    "content": """# MIT 6.828 Operating System Engineering

**视频来源**: MIT OpenCourseWare — Frans Kaashoek, Robert Morris
**时长**: 约45小时（26讲，每讲约100分钟）
**语言**: 英文（含英文字幕）
**内容概要**:
- OS架构概述：微内核vs宏内核设计哲学
- x86/RISC-V硬件基础：内存管理单元、中断控制器、特权级
- 进程管理：fork/exec实现、上下文切换汇编代码
- 地址空间与虚拟内存：页表机制、TLB、按需调页
- 中断与异常处理：IDT、trap frame、系统调用路径
- 并发与同步：自旋锁、睡眠锁、信号量在内核中的实现
- 文件系统设计：buffer cache、日志、inode、目录结构
- 用户态与内核态切换机制
- Lab 1-6：从bootloader到完整OS内核的逐步实现
- 网络协议栈简介（lwIP集成）

**适合人群**: 有C语言和计算机组成基础的高年级本科生、研究生
**推荐理由**: MIT 6.828是全球操作系统教学的金标准课程。通过动手实验编写xv6内核代码，将操作系统理论转化为实际工程能力，是深入理解操作系统的最佳路径。

---
*来源: https://ocw.mit.edu/courses/6-828-operating-system-engineering-fall-2012/*"""
})

RESOURCES.append({
    "title": "Linux内核设计与实现视频课程",
    "description": "深入Linux内核核心子系统：进程调度器（CFS）、内存管理（buddy/slab）、VFS虚拟文件系统、中断处理、内核同步机制（RCU/spinlock/mutex）、系统调用实现等。",
    "course": "操作系统", "chapter": "Linux内核", "difficulty": "ADVANCED",
    "type": "VIDEO",
    "tags": ["Linux内核", "进程调度", "内存管理", "VFS", "RCU", "内核同步", "系统调用"],
    "source_url": "https://www.youtube.com/playlist?list=PLQqyLaMGjRGWCK9CHWLz4MpSRMnxGqRFa",
    "content": """# Linux内核设计与实现视频课程

**视频来源**: YouTube — Bootlin / Free Electrons
**时长**: 约20小时
**语言**: 英文
**内容概要**:
- Linux内核架构概览：整体模块划分与源码目录结构
- 进程管理与CFS调度器：vruntime计算、红黑树调度队列
- 内存管理子系统：伙伴系统（buddy allocator）、slab/slub分配器
- 内核地址空间：vmalloc、ioremap、DMA映射
- 虚拟文件系统VFS：super_block、inode、dentry、file四大对象
- 内核同步机制：自旋锁、互斥锁、RCU、读写信号量
- 中断处理：顶半部/底半部（tasklet/workqueue）
- 系统调用：syscall表、参数传递、追踪机制
- 内核模块开发：insmod/rmmod、module_init
- 设备驱动模型：字符设备、块设备、网络设备框架

**适合人群**: 有操作系统理论基础和C语言编程经验的开发者
**推荐理由**: Bootlin的Linux内核课程以工程实战为导向，结合源码阅读，是从事Linux驱动开发或内核开发的入门必看资料。

---
*来源: https://www.youtube.com/playlist?list=PLQqyLaMGjRGWCK9CHWLz4MpSRMnxGqRFa*"""
})

# ═══════════════════════════════════════════════════════════════
# 2. 数据结构 (3 resources)
# ═══════════════════════════════════════════════════════════════

RESOURCES.append({
    "title": "王道考研数据结构全程精讲",
    "description": "王道考研数据结构经典课程，涵盖线性表、栈队列、树、图、查找、排序六大模块。408考研核心课程，代码演示严谨，算法动画直观。",
    "course": "数据结构", "chapter": "数据结构基础", "difficulty": "INTERMEDIATE",
    "type": "VIDEO",
    "tags": ["数据结构", "考研", "线性表", "二叉树", "图", "排序", "查找"],
    "source_url": "https://www.bilibili.com/video/BV1b7411N798",
    "content": """# 王道考研数据结构全程精讲

**视频来源**: bilibili — 王道计算机教育
**时长**: 约45小时（含全部章节）
**语言**: 中文
**内容概要**:
- 绪论：算法时间复杂度与空间复杂度分析
- 线性表：顺序表、单链表、双链表、循环链表及其操作
- 栈与队列：顺序栈/链栈、循环队列/链队列、栈在括号匹配和表达式求值中的应用
- 串：KMP算法与next数组推导
- 树与二叉树：遍历（前/中/后/层序）、线索二叉树、Huffman树、并查集
- 图：邻接矩阵/邻接表、BFS/DFS、最小生成树、最短路径、拓扑排序、关键路径
- 查找：顺序查找、折半查找、分块查找、B树与B+树、哈希表、开放定址法与链地址法
- 排序：插入/希尔/冒泡/快排/选择/堆排/归并/基数排序对比
- 408真题分类精讲

**适合人群**: 计算机考研学生、数据结构入门学习者
**推荐理由**: 王道数据结构以408考研为导向，每个算法都配有伪代码和动画演示，讲解循序渐进，是考研复习和数据结构基础学习的高效选择。

---
*来源: https://www.bilibili.com/video/BV1b7411N798*"""
})

RESOURCES.append({
    "title": "浙江大学数据结构——陈越、何钦铭主讲",
    "description": "浙江大学国家级精品课程《数据结构》，由陈越、何钦铭教授主讲。以C语言实现为核心，强调算法效率分析与编程实践能力，MOOC平台评分极高。",
    "course": "数据结构", "chapter": "数据结构与算法分析", "difficulty": "INTERMEDIATE",
    "type": "VIDEO",
    "tags": ["数据结构", "浙江大学", "陈越", "C语言", "算法分析", "MOOC", "编程实践"],
    "source_url": "https://www.bilibili.com/video/BV1JW411i731",
    "content": """# 浙江大学数据结构——陈越、何钦铭主讲

**视频来源**: bilibili/中国大学MOOC — 陈越教授、何钦铭教授（浙江大学）
**时长**: 约48小时（共12周课程）
**语言**: 中文
**内容概要**:
- 第一周：基本概念、算法复杂度、最大子列和问题
- 第二周：线性结构（线性表、堆栈、队列）
- 第三周：树（二叉树、遍历、二叉搜索树、平衡二叉树AVL）
- 第四周：堆与哈夫曼树
- 第五周：图（邻接矩阵/邻接表、DFS/BFS）
- 第六周：最短路径（Dijkstra/Floyd）、最小生成树（Prim/Kruskal）
- 第七周：拓扑排序、关键路径
- 第八周：查找（哈希表、冲突处理）
- 第九周：排序算法与综合对比
- 第十至十二周：综合练习与PAT/蓝桥杯真题

**适合人群**: 计算机专业本科生、编程竞赛备考生
**推荐理由**: 陈越教授的课程以「理论-实践-题库」三位一体著称，配套PAT（Programming Ability Test）在线判题系统，让数据结构从纸面走向代码，是理论与编程能力双提升的标杆课程。

---
*来源: https://www.bilibili.com/video/BV1JW411i731*"""
})

RESOURCES.append({
    "title": "数据结构应用——红黑树与跳表深度解析",
    "description": "专题讲解工业级数据结构：红黑树的5条性质与插入/删除旋转修复全过程动画演示，跳表（SkipList）的概率平衡原理与Redis有序集合底层实现。",
    "course": "数据结构", "chapter": "高级数据结构", "difficulty": "ADVANCED",
    "type": "VIDEO",
    "tags": ["红黑树", "跳表", "SkipList", "Redis", "AVL树", "平衡树", "高级数据结构"],
    "source_url": "https://www.youtube.com/watch?v=qvZGUFHWChY",
    "content": """# 数据结构应用——红黑树与跳表深度解析

**视频来源**: YouTube — Michael Sambol (算法可视化系列)
**时长**: 约30分钟（合集）
**语言**: 英文（含英文字幕）
**内容概要**:
- 红黑树的5条性质详解：根黑、叶黑、红节点子为黑、同黑高
- 红黑树插入的三种case分析与修复动画
- 红黑树删除的四种case分析与颜色翻转
- AVL树与红黑树的性能对比（查找/插入/删除复杂度）
- 跳表的数据结构定义与层级生成算法
- 跳表的查找/插入/删除操作概率分析
- Redis Sorted Set跳表实现：score排序、rank查询
- 跳表与B+树的对比：不同场景下的选择策略
- LevelDB/LSM-Tree中跳表的应用
- Java ConcurrentSkipListMap并发安全设计

**适合人群**: 有基础数据结构知识、准备面试或从事系统开发的工程师
**推荐理由**: 红黑树和跳表是面试高频考点和工业系统常用结构，图文动画结合源码分析的教学方式让抽象概念变得直观易懂。

---
*来源: https://www.youtube.com/watch?v=qvZGUFHWChY*"""
})

# ═══════════════════════════════════════════════════════════════
# 3. 计算机网络 (3 resources)
# ═══════════════════════════════════════════════════════════════

RESOURCES.append({
    "title": "王道考研计算机网络全程精讲",
    "description": "王道考研计算机网络课程，按OSI七层/ TCP/IP五层体系逐层讲解，涵盖物理层到应用层全部知识点。408考研核心课程，配合大量计算题和协议分析。",
    "course": "计算机网络", "chapter": "计算机网络体系结构", "difficulty": "INTERMEDIATE",
    "type": "VIDEO",
    "tags": ["计算机网络", "考研", "TCP/IP", "OSI", "子网划分", "路由协议", "DNS"],
    "source_url": "https://www.bilibili.com/video/BV19E411D78Q",
    "content": """# 王道考研计算机网络全程精讲

**视频来源**: bilibili — 王道计算机教育
**时长**: 约35小时（含全部章节）
**语言**: 中文
**内容概要**:
- 计算机网络体系结构：OSI七层模型、TCP/IP四层模型
- 物理层：奈奎斯特定理、香农定理、编码与调制、物理层设备
- 数据链路层：组帧、差错检测（CRC/奇偶/海明码）、CSMA/CD、MAC帧格式
- 网络层：IPv4地址分类、CIDR子网划分、NAT、ARP、DHCP
- 路由协议：RIP距离向量、OSPF链路状态、BGP路径矢量
- 传输层：TCP三次握手/四次挥手、拥塞控制、UDP协议
- 应用层：DNS、HTTP/HTTPS、FTP、SMTP/POP3/IMAP
- 网络安全基础：对称/非对称加密、数字签名、SSL/TLS
- 408真题分类精讲与协议分析大题

**适合人群**: 计算机考研学生、网络工程初学者
**推荐理由**: 王道计算机网络以协议为主线串讲全部知识点，计算题和协议分析题的训练量充足，帮助构建完整的网络知识体系。

---
*来源: https://www.bilibili.com/video/BV19E411D78Q*"""
})

RESOURCES.append({
    "title": "Stanford CS144 Introduction to Computer Networking",
    "description": "斯坦福大学计算机网络导论课程，以自顶向下方法讲解TCP/IP协议栈。配套编程Lab实现完整的TCP协议栈，理论与实践深度结合。",
    "course": "计算机网络", "chapter": "TCP/IP协议栈", "difficulty": "ADVANCED",
    "type": "VIDEO",
    "tags": ["计算机网络", "Stanford", "TCP", "IP", "协议栈", "自顶向下", "Lab"],
    "source_url": "https://www.youtube.com/playlist?list=PLoCMsyE1cvdWKsLVyf6cPwCLDIZnOj0NS",
    "content": """# Stanford CS144 Introduction to Computer Networking

**视频来源**: YouTube/Stanford Online — Philip Levis, Keith Winstein
**时长**: 约30小时（22讲，每讲约75分钟）
**语言**: 英文（含英文字幕）
**内容概要**:
- 互联网架构设计原则：端到端原则、分层模型
- 应用层：HTTP/1.1与HTTP/2协议、DNS系统
- 传输层：TCP可靠传输机制、滑动窗口、流量控制、拥塞控制算法
- 网络层：IP数据报格式、分片与重组、路由协议
- 数据链路层：以太网、交换机、生成树协议
- Lab 0-4：从字节流重组到完整TCP实现（C++编程）
- TCP三次握手与四次挥手的有限状态机实现
- TCP重传超时（RTO）计算与Jacobson/Karels算法
- 网络性能分析：带宽、延迟、吞吐量、BDP
- 现代网络话题：QUIC协议、数据中心网络

**适合人群**: 有C/C++编程基础的计算机专业学生和工程师
**推荐理由**: CS144以自顶向下方法组织内容，逐步实现完整TCP协议栈，是全球最深入浅出的计算机网络课程之一。Lab设计精妙，做完后对TCP有透彻理解。

---
*来源: https://www.youtube.com/playlist?list=PLoCMsyE1cvdWKsLVyf6cPwCLDIZnOj0NS*"""
})

RESOURCES.append({
    "title": "湖科大教书匠计算机网络微课堂",
    "description": "B站知名UP主湖科大教书匠的计算机网络系列，以通俗易懂的动画和比喻讲解网络协议，涵盖IP子网划分、路由协议、网络层协议等核心考点。",
    "course": "计算机网络", "chapter": "网络层与传输层", "difficulty": "BASIC",
    "type": "VIDEO",
    "tags": ["计算机网络", "子网划分", "路由", "BGP", "OSPF", "NAT", "动画教学"],
    "source_url": "https://www.bilibili.com/video/BV1Hx411m7RH",
    "content": """# 湖科大教书匠计算机网络微课堂

**视频来源**: bilibili — 湖科大教书匠
**时长**: 约30小时（全系列合集）
**语言**: 中文
**内容概要**:
- IPv4地址分类与CIDR无类域间路由
- 子网划分、超网聚合、VLSM变长子网掩码
- NAT网络地址转换与端口映射原理
- ARP地址解析协议与ARP欺骗
- ICMP协议与Ping/Traceroute工具原理
- RIP距离向量路由协议与Bellman-Ford算法
- OSPF链路状态路由协议与Dijkstra SPF算法
- BGP边界网关协议与AS自治系统
- TCP流量控制与拥塞控制详解
- IPv6地址格式与过渡技术

**适合人群**: 计算机网络入门学习者、考研备考学生
**推荐理由**: 湖科大教书匠以精美动画和形象比喻著称，将复杂网络协议化繁为简。特别适合在复习教材后用来巩固理解和辨析易混淆概念。

---
*来源: https://www.bilibili.com/video/BV1Hx411m7RH*"""
})

# ═══════════════════════════════════════════════════════════════
# 4. 计算机组成原理 (3 resources)
# ═══════════════════════════════════════════════════════════════

RESOURCES.append({
    "title": "王道考研计算机组成原理全程精讲",
    "description": "王道考研计算机组成原理课程，覆盖数据表示、运算器、存储器、指令系统、CPU、总线、I/O七大模块。408考研核心课程，计算题和设计题训练充分。",
    "course": "计算机组成原理", "chapter": "计算机系统概述", "difficulty": "INTERMEDIATE",
    "type": "VIDEO",
    "tags": ["计算机组成原理", "考研", "CPU", "Cache", "指令系统", "存储器", "总线"],
    "source_url": "https://www.bilibili.com/video/BV1ps4y1d73V",
    "content": """# 王道考研计算机组成原理全程精讲

**视频来源**: bilibili — 王道计算机教育
**时长**: 约40小时（含全部章节）
**语言**: 中文
**内容概要**:
- 计算机系统概述：冯诺依曼结构、计算机性能指标
- 数据的表示与运算：原码/反码/补码/移码、浮点数IEEE 754标准
- 运算方法与运算器：定点加减乘除、ALU设计
- 存储器层次结构：SRAM/DRAM、Cache映射（直接/组相联/全相联）
- Cache替换算法与写策略：LRU/FIFO/随机、写直达/写回
- 指令系统：CISC vs RISC、寻址方式、MIPS/x86指令格式
- CPU数据通路：单周期/多周期/流水线CPU设计
- 指令流水线：数据冒险/控制冒险/结构冒险与解决策略
- 总线与I/O：总线仲裁、程序查询/中断/DMA方式
- 408真题分类精讲与设计题训练

**适合人群**: 计算机考研学生、计算机组成入门学习者
**推荐理由**: 王道组成原理将硬件抽象概念用图文并茂的方式呈现，Cache计算和流水线分析尤其讲得透彻，是408考研复习的首选资料。

---
*来源: https://www.bilibili.com/video/BV1ps4y1d73V*"""
})

RESOURCES.append({
    "title": "哈工大计算机组成原理——刘宏伟主讲",
    "description": "哈尔滨工业大学国家级精品课程《计算机组成原理》，刘宏伟教授主讲。从数字逻辑到CPU设计，完整讲述计算机硬件系统的设计与工作原理。",
    "course": "计算机组成原理", "chapter": "CPU设计与流水线", "difficulty": "ADVANCED",
    "type": "VIDEO",
    "tags": ["计算机组成原理", "哈工大", "CPU设计", "流水线", "Verilog", "数字逻辑", "精品课程"],
    "source_url": "https://www.bilibili.com/video/BV1WW411Q7PF",
    "content": """# 哈工大计算机组成原理——刘宏伟主讲

**视频来源**: bilibili/中国大学MOOC — 刘宏伟教授（哈尔滨工业大学）
**时长**: 约55小时（共14周课程）
**语言**: 中文
**内容概要**:
- 数字逻辑基础：布尔代数、组合逻辑、时序逻辑设计
- 计算机系统概述：冯诺依曼架构、性能评价
- 运算方法与运算器：定点数/浮点数运算、ALU设计与实现
- 指令系统设计：指令格式、操作码编码、寻址技术
- CPU结构与数据通路：单总线/双总线/三总线结构
- 微程序控制器：微指令格式、微程序流程图、微地址形成
- 硬布线控制器：组合逻辑控制信号生成
- 指令流水线技术：经典五段流水、流水线冲突与解决方法
- 存储系统：Cache原理（映射方式/替换策略/写策略）
- 虚拟存储器：页表、TLB、虚实地址转换
- 总线系统与I/O接口
- 课程配套实验：基于FPGA/Verilog的简单CPU设计

**适合人群**: 计算机专业本科生、对CPU设计感兴趣的硬件爱好者
**推荐理由**: 哈工大组成原理是国家精品课程，理论深度与工程实践并重。结合Verilog进行CPU设计实验，是理解计算机硬件工作原理的绝佳课程。

---
*来源: https://www.bilibili.com/video/BV1WW411Q7PF*"""
})

RESOURCES.append({
    "title": "Nand2Tetris——从逻辑门到计算机系统",
    "description": "著名的Nand2Tetris课程（又名「计算机系统要素」），从最基础的NAND门出发，逐步构建出完整的现代计算机系统，包括CPU、汇编器、编译器、操作系统。",
    "course": "计算机组成原理", "chapter": "计算机系统设计", "difficulty": "ADVANCED",
    "type": "VIDEO",
    "tags": ["Nand2Tetris", "计算机系统", "硬件设计", "HDL", "汇编", "编译器", "Shimon"],
    "source_url": "https://www.coursera.org/learn/build-a-computer",
    "content": """# Nand2Tetris——从逻辑门到计算机系统

**视频来源**: Coursera — Shimon Schocken, Noam Nisan (Hebrew University of Jerusalem)
**时长**: 约50小时（共12周，两部分课程）
**语言**: 英文（中英文字幕可用）
**内容概要**:
- 第1周：布尔逻辑——用NAND门构建基本逻辑门
- 第2周：布尔算术——构建半加器、全加器、ALU
- 第3周：时序逻辑——触发器、寄存器、RAM、计数器
- 第4周：机器语言——Hack计算机的指令集体系结构
- 第5周：计算机体系结构——CPU、内存、I/O设备集成
- 第6周：汇编器——符号解析、代码生成
- 第7周：虚拟机I——堆栈算术/内存访问命令
- 第8周：虚拟机II——程序流与函数调用
- 第9周：高级语言——Jack面向对象语言设计
- 第10周：编译器I——词法分析与语法分析
- 第11周：编译器II——代码生成与符号表
- 第12周：操作系统——数学库、内存管理、I/O

**适合人群**: 任何想从第一原理理解计算机系统的人，不要求硬件背景
**推荐理由**: Nand2Tetris是极少数能让你从零开始构建一台完整计算机的课程。它打破了「黑盒」思维，让你真正理解程序从源代码到硬件执行的每一层抽象。

---
*来源: https://www.coursera.org/learn/build-a-computer*"""
})

# ═══════════════════════════════════════════════════════════════
# 5. 编译原理 (2 resources)
# ═══════════════════════════════════════════════════════════════

RESOURCES.append({
    "title": "哈工大编译原理——陈鄞主讲",
    "description": "哈尔滨工业大学编译原理课程，陈鄞副教授主讲。系统讲解词法分析、语法分析、语义分析、中间代码生成与优化的完整流程，理论基础扎实。",
    "course": "编译原理", "chapter": "编译过程与中间代码", "difficulty": "ADVANCED",
    "type": "VIDEO",
    "tags": ["编译原理", "哈工大", "词法分析", "语法分析", "LL", "LR", "中间代码", "代码优化"],
    "source_url": "https://www.bilibili.com/video/BV1KW411j7GV",
    "content": """# 哈工大编译原理——陈鄞主讲

**视频来源**: bilibili/中国大学MOOC — 陈鄞副教授（哈尔滨工业大学）
**时长**: 约45小时（共12周课程）
**语言**: 中文
**内容概要**:
- 编译器概述：编译过程概览、编译器结构（前端/中端/后端）
- 词法分析：正则表达式→NFA→DFA→DFA最小化
- Lex/Flex工具使用与自动生成词法分析器
- 语法分析-自顶向下：LL(1)文法、FIRST/FOLLOW集合、预测分析表
- 递归下降分析器的手工实现
- 语法分析-自底向上：LR(0)/SLR(1)/LR(1)/LALR(1)分析
- Yacc/Bison工具使用与自动生成语法分析器
- 语法制导翻译SDD/SDT：综合属性与继承属性
- 中间代码生成：三地址码、四元式、控制流语句翻译
- 中间代码优化：基本块、流图、DAG优化
- 数据流分析：到达定值、活跃变量、可用表达式
- 循环优化：代码外提、强度削弱、归纳变量消除

**适合人群**: 计算机专业高年级本科生和研究生
**推荐理由**: 哈工大编译原理以经典龙书为参考教材，推导严谨，例题丰富。配套实验用C/C++实现小型编译器，是理论与实践均衡的优质课程。

---
*来源: https://www.bilibili.com/video/BV1KW411j7GV*"""
})

RESOURCES.append({
    "title": "Stanford CS143 Compilers",
    "description": "斯坦福大学编译原理课程，从词法分析到代码生成，实现一个完整的COOL语言编译器。讲解清晰，配套实验丰富，是编译原理领域最经典的公开课之一。",
    "course": "编译原理", "chapter": "编译器设计与实现", "difficulty": "ADVANCED",
    "type": "VIDEO",
    "tags": ["编译原理", "Stanford", "编译器", "COOL语言", "类型检查", "代码生成", "寄存器分配"],
    "source_url": "https://www.edx.org/learn/computer-science/stanford-university-compilers",
    "content": """# Stanford CS143 Compilers

**视频来源**: edX/Stanford Online — Alex Aiken
**时长**: 约40小时（16讲，每讲约75分钟）
**语言**: 英文（含英文字幕）
**内容概要**:
- 编译器架构概览：前端/优化/后端
- 词法分析：正则表达式、有限自动机、Flex
- 语法分析：上下文无关文法、自顶向下与自底向上分析
- 抽象语法树AST与语义分析
- 类型检查与类型推导
- 运行时环境：栈帧、调用约定、参数传递
- 中间代码生成：三地址码与控制流
- 代码优化技术：常量折叠、死代码消除、寄存器分配（图着色算法）
- PA1-PA5：逐步实现COOL（Classroom Object-Oriented Language）编译器
- 目标代码生成与指令选择

**适合人群**: 有编程语言理论基础的计算机专业学生
**推荐理由**: Alex Aiken教授是编译器领域的权威学者。CS143以其清晰的授课风格和循序渐进的实验设计成为全球学习编译原理的首选公开课。

---
*来源: https://www.edx.org/learn/computer-science/stanford-university-compilers*"""
})

# ═══════════════════════════════════════════════════════════════
# 6. 数据库原理 (3 resources)
# ═══════════════════════════════════════════════════════════════

RESOURCES.append({
    "title": "数据库系统概论——王珊、萨师煊配套视频",
    "description": "数据库经典教材《数据库系统概论》（第五版）官方配套视频课程，系统讲解关系代数、SQL、规范化理论、查询优化、事务管理、故障恢复等核心知识点。",
    "course": "数据库原理", "chapter": "数据库基础理论", "difficulty": "INTERMEDIATE",
    "type": "VIDEO",
    "tags": ["数据库", "关系代数", "SQL", "规范化", "事务", "ER模型", "查询优化"],
    "source_url": "https://www.bilibili.com/video/BV1h5411u7Pk",
    "content": """# 数据库系统概论——王珊、萨师煊配套视频

**视频来源**: bilibili — 中国人民大学信息学院
**时长**: 约40小时（共12章）
**语言**: 中文
**内容概要**:
- 数据库系统概述：数据模型、三层模式结构、DBMS
- 关系模型：关系代数（选择/投影/连接/除）、关系演算
- SQL语言：DDL/DML/DCL、连接查询、嵌套子查询、集合操作
- 数据库安全性：授权GRANT/REVOKE、审计
- 数据库完整性：实体完整性、参照完整性、用户定义完整性、触发器
- 关系规范化理论：函数依赖、范式（1NF/2NF/3NF/BCNF/4NF）
- 模式分解：无损连接、保持函数依赖
- 数据库设计：ER模型、概念结构→逻辑结构→物理结构设计
- 查询优化：代数优化、物理优化、等价变换规则
- 事务管理：ACID特性、隔离级别
- 故障恢复：日志、检查点、UNDO/REDO
- 并发控制：封锁、活锁/死锁、两段锁协议

**适合人群**: 数据库入门学习者、计算机考研学生
**推荐理由**: 《数据库系统概论》是国内数据库教学的标准教材，配套视频完美覆盖所有知识点，适合系统学习和考研复习。

---
*来源: https://www.bilibili.com/video/BV1h5411u7Pk*"""
})

RESOURCES.append({
    "title": "CMU 15-445/645 Database Systems",
    "description": "卡内基梅隆大学数据库系统课程（Andy Pavlo主讲），深入讲解存储引擎、索引、查询执行、查询优化、并发控制、故障恢复等数据库内核技术，是数据库方向最顶级的公开课。",
    "course": "数据库原理", "chapter": "数据库系统实现", "difficulty": "ADVANCED",
    "type": "VIDEO",
    "tags": ["数据库", "CMU", "存储引擎", "B+树", "查询优化", "MVCC", "Andy Pavlo"],
    "source_url": "https://www.youtube.com/playlist?list=PLSE8ODhjZXjbj8BMuIrRcacnQh80hmY9l",
    "content": """# CMU 15-445/645 Database Systems

**视频来源**: YouTube — Andy Pavlo (Carnegie Mellon University)
**时长**: 约50小时（26讲，每讲约75分钟）
**语言**: 英文（含英文字幕）
**内容概要**:
- 关系模型与关系代数
- SQL高级查询与窗口函数
- 存储管理：堆文件、页布局、元组存储（N-ary vs PAX）
- 缓冲池管理：Clock/LRU/LRU-K替换策略
- 哈希表与布隆过滤器在数据库中的实现
- B+树索引：插入/删除/分裂、前缀压缩
- 排序与聚合：外部归并排序、哈希聚合
- 查询执行：迭代器模型、向量化执行
- 查询优化：代价模型、动态规划、Selinger优化器
- 并发控制：两阶段锁2PL、时间戳排序T/O
- MVCC多版本并发控制：WriteSet、ReadView
- 故障恢复：ARIES算法（WAL、REDO/UNDO）
- 分布式数据库：两阶段提交2PC、Raft共识

**适合人群**: 具备C++编程能力的高年级本科生和研究生
**推荐理由**: CMU 15-445是全球公认最优秀的数据库系统课程，Andy Pavlo激情四射的授课风格和深入内核的代码剖析让学员对数据库实现有透彻理解。配套BusTub实验框架可动手实现一个简单DBMS。

---
*来源: https://www.youtube.com/playlist?list=PLSE8ODhjZXjbj8BMuIrRcacnQh80hmY9l*"""
})

RESOURCES.append({
    "title": "数据库索引优化与执行计划分析实战",
    "description": "聚焦MySQL/PostgreSQL索引优化实战：B+树索引底层原理、覆盖索引、索引下推、执行计划EXPLAIN解读、SQL优化10大经典案例。",
    "course": "数据库原理", "chapter": "数据库性能优化", "difficulty": "INTERMEDIATE",
    "type": "VIDEO",
    "tags": ["数据库优化", "SQL调优", "索引", "EXPLAIN", "MySQL", "PostgreSQL", "慢查询"],
    "source_url": "https://www.bilibili.com/video/BV1if4y1d7GC",
    "content": """# 数据库索引优化与执行计划分析实战

**视频来源**: bilibili — 黑马程序员/尚硅谷
**时长**: 约8小时（合集系列）
**语言**: 中文
**内容概要**:
- MySQL InnoDB索引结构：聚簇索引、二级索引、页分裂
- 回表查询与覆盖索引（Using index）优化
- 最左前缀原则与复合索引设计
- 索引下推（ICP）与Multi-Range Read优化原理
- EXPLAIN输出字段详解：id/select_type/type/possible_keys/key/rows/Extra
- type访问类型排序：system > const > eq_ref > ref > range > index > ALL
- Extra信息解读：Using index/Using filesort/Using temporary
- 慢查询日志配置：long_query_time、pt-query-digest分析
- SQL优化十大实战案例（LIMIT大偏移量、JOIN顺序、IN vs EXISTS）
- PostgreSQL pg_stat_statements与auto_explain
- 索引失效场景大全：函数/计算/类型转换/OR
- 分库分表后的索引设计策略

**适合人群**: 后端开发工程师、DBA初学者
**推荐理由**: 将数据库理论知识转化为实际调优能力的关键桥梁课程。通过真实业务场景的SQL优化案例，掌握索引设计与执行计划解读的核心技能。

---
*来源: https://www.bilibili.com/video/BV1if4y1d7GC*"""
})

# ═══════════════════════════════════════════════════════════════
# 7. 软件工程 (2 resources)
# ═══════════════════════════════════════════════════════════════

RESOURCES.append({
    "title": "MIT 6.031 Software Construction",
    "description": "麻省理工学院软件构造课程，聚焦于编写安全、可读、可维护的复杂软件系统。涵盖设计模式、抽象数据类型、并发编程、测试驱动开发、形式化规约等核心主题。",
    "course": "软件工程", "chapter": "软件构造与设计", "difficulty": "ADVANCED",
    "type": "VIDEO",
    "tags": ["软件工程", "MIT", "设计模式", "TDD", "ADT", "并发", "代码质量"],
    "source_url": "https://ocw.mit.edu/courses/6-005-software-construction-spring-2016/",
    "content": """# MIT 6.031 Software Construction

**视频来源**: MIT OpenCourseWare — Rob Miller, Max Goldman
**时长**: 约36小时（21讲，每讲约80分钟）
**语言**: 英文（含英文字幕）
**内容概要**:
- 代码安全：静态检查、动态检查、避免常见Bug的模式
- 测试驱动开发TDD：单元测试、集成测试、回归测试
- 规约设计：前置条件/后置条件/不变量、规约强度
- 抽象数据类型ADT：表示独立性、抽象函数AF、表示不变量RI
- 面向对象编程：接口/类/继承/多态的设计原则
- 设计模式：工厂方法、建造者、观察者、策略、装饰器
- 并发编程：线程安全、锁、死锁、消息传递模型
- 函数式编程：不可变类型、高阶函数
- 语法分析：Parser组合子、ANTLR
- 团队协作：Git工作流、代码审查

**适合人群**: 有1-2年编程经验的计算机专业学生
**推荐理由**: 不同于传统软件工程课的重文档/重流程，6.031聚焦于代码质量本身——如何写出「正确、安全、可维护」的代码。Java编程实验设计精巧，是软件工程实践入门的极佳选择。

---
*来源: https://ocw.mit.edu/courses/6-005-software-construction-spring-2016/*"""
})

RESOURCES.append({
    "title": "软件工程——敏捷开发与DevOps实践",
    "description": "现代软件工程实践课程，涵盖敏捷开发（Scrum/Kanban）、DevOps工具链（CI/CD/Docker/K8s）、微服务架构设计、代码重构、软件测试策略等实用主题。",
    "course": "软件工程", "chapter": "现代软件开发实践", "difficulty": "INTERMEDIATE",
    "type": "VIDEO",
    "tags": ["软件工程", "敏捷开发", "Scrum", "DevOps", "CI/CD", "微服务", "代码重构"],
    "source_url": "https://www.youtube.com/playlist?list=PLBm97hOigcNkFT4NA3DEQNeVj1xT6Ddxg",
    "content": """# 软件工程——敏捷开发与DevOps实践

**视频来源**: YouTube — Google Tech Talks / Continuous Delivery
**时长**: 约15小时（合集系列）
**语言**: 英文/中文双语
**内容概要**:
- 敏捷宣言与12条原则：个体与交互 > 流程和工具
- Scrum框架：Sprint/Product Backlog/Daily Standup/Sprint Review
- 看板Kanban：WIP限制、累积流图、瓶颈识别
- 用户故事与故事点估算（Planning Poker）
- 持续集成CI：自动化构建、静态分析、单元测试
- 持续交付CD：部署流水线、蓝绿部署、金丝雀发布
- 容器化与Docker基础
- Kubernetes编排基础
- 微服务架构设计原则：服务拆分、API网关、服务发现
- 代码重构红宝书：坏味道识别、重构手法分类
- 软件测试金字塔：单元/集成/端到端测试策略
- 技术债务管理与代码质量度量

**适合人群**: 初级至中级软件工程师、计算机专业高年级学生
**推荐理由**: 将软件工程课堂理论与工业界最佳实践相结合，涵盖从需求管理到自动化部署的全流程，是连接「学」与「做」的实用课程集合。

---
*来源: https://www.youtube.com/playlist?list=PLBm97hOigcNkFT4NA3DEQNeVj1xT6Ddxg*"""
})

# ═══════════════════════════════════════════════════════════════
# 8. 算法设计与分析 (3 resources)
# ═══════════════════════════════════════════════════════════════

RESOURCES.append({
    "title": "MIT 6.046 Design and Analysis of Algorithms",
    "description": "MIT经典算法设计与分析课程，由Erik Demaine、Srini Devadas等教授主讲。涵盖分治、动态规划、贪心、网络流、线性规划、近似算法、随机算法等高级算法主题。",
    "course": "算法设计与分析", "chapter": "高级算法设计", "difficulty": "ADVANCED",
    "type": "VIDEO",
    "tags": ["算法设计", "MIT", "动态规划", "网络流", "近似算法", "随机算法", "NP完全"],
    "source_url": "https://ocw.mit.edu/courses/6-046j-design-and-analysis-of-algorithms-spring-2015/",
    "content": """# MIT 6.046 Design and Analysis of Algorithms

**视频来源**: MIT OpenCourseWare — Erik Demaine, Srini Devadas, Nancy Lynch
**时长**: 约50小时（24讲，每讲约80分钟）
**语言**: 英文（含英文字幕）
**内容概要**:
- 算法分析基础：渐近符号、主定理、平摊分析
- 分治算法：矩阵乘法（Strassen）、最近点对、快速傅里叶变换FFT
- 动态规划：矩阵链乘、LCS、背包、编辑距离
- 贪心算法：Huffman、MST、拟阵理论
- 最短路径：Dijkstra、Bellman-Ford、Johnson重加权
- 最大流：Ford-Fulkerson、Edmonds-Karp、Dinic
- 线性规划：单纯形法、对偶性
- NP完全性理论：归约、Cook-Levin定理
- 近似算法：顶点覆盖、TSP、集合覆盖的近似比
- 随机算法：随机快排、Min-Cut、哈希
- 在线算法：竞争比分析、页面置换

**适合人群**: 有基础算法知识的计算机专业高年级学生和研究生
**推荐理由**: 6.046是MIT算法系列的高阶课程，覆盖从经典算法到现代算法设计范式的全景图。Erik Demaine教授极富感染力的教学方式让复杂算法变得生动有趣。

---
*来源: https://ocw.mit.edu/courses/6-046j-design-and-analysis-of-algorithms-spring-2015/*"""
})

RESOURCES.append({
    "title": "北大算法设计与分析——屈婉玲主讲",
    "description": "北京大学算法设计与分析经典课程，屈婉玲教授主讲。以「问题-算法-分析」为主线，系统讲解分治、动态规划、贪心、回溯、分支限界等核心算法设计策略。",
    "course": "算法设计与分析", "chapter": "算法设计策略", "difficulty": "INTERMEDIATE",
    "type": "VIDEO",
    "tags": ["算法设计", "北京大学", "分治", "动态规划", "贪心", "回溯", "分支限界"],
    "source_url": "https://www.bilibili.com/video/BV1Ls411W7jB",
    "content": """# 北大算法设计与分析——屈婉玲主讲

**视频来源**: bilibili — 屈婉玲教授（北京大学）
**时长**: 约40小时
**语言**: 中文
**内容概要**:
- 算法分析基础：复杂度计算、递推方程求解
- 分治策略：二分检索、归并排序、快速排序、大整数乘法
- 动态规划：矩阵链乘、最优BST、0/1背包、TSP
- 贪心策略：活动选择、分数背包、Dijkstra、Prim、Kruskal
- 回溯法：n皇后、图着色、Hamilton圈、子集和
- 分支限界法：FIFO/LIFO/优先队列搜索策略
- 概率算法：数值概率、Las Vegas、Monte Carlo
- 近似算法：顶点覆盖、TSP近似
- NP完全理论：P/NP/NPC/NP-hard分类与归约
- 平摊分析：聚集法、记账法、势能法

**适合人群**: 计算机专业本科生、算法竞赛备考生
**推荐理由**: 屈婉玲教授是国内算法教学领域的权威。课程逻辑严密，例题丰富，每个算法都有详细的正确性证明和复杂度分析，是建立扎实算法功底的基础课程。

---
*来源: https://www.bilibili.com/video/BV1Ls411W7jB*"""
})

RESOURCES.append({
    "title": "Princeton Algorithms——Robert Sedgewick主讲",
    "description": "普林斯顿大学算法课程（Coursera），由《算法（第四版）》作者Robert Sedgewick亲自讲授。两学期课程涵盖基础数据结构和高级图算法，配套丰富的Java编程作业。",
    "course": "算法设计与分析", "chapter": "算法与数据结构综合", "difficulty": "INTERMEDIATE",
    "type": "VIDEO",
    "tags": ["算法", "Princeton", "Sedgewick", "Java", "图算法", "排序", "数据结构"],
    "source_url": "https://www.coursera.org/learn/algorithms-part1",
    "content": """# Princeton Algorithms——Robert Sedgewick主讲

**视频来源**: Coursera — Robert Sedgewick, Kevin Wayne (Princeton University)
**时长**: 约30小时（Part I + Part II，各6周）
**语言**: 英文（中英文字幕）
**内容概要**:
- Part I（基础）:
  - Union-Find并查集：Quick Find/Quick Union/加权/WPC
  - 算法分析：tilde记法、order-of-growth
  - 栈与队列：链表/数组/可调整大小数组实现
  - 排序：选择/插入/希尔/归并/快排、3-way快排、堆排序
  - 优先队列与堆：二叉堆、堆排序、索引优先队列
  - 符号表：BST、2-3树、红黑树
  - 哈希表：分离链接法、线性探测法
- Part II（高级）:
  - 图：无向图DFS/BFS、连通分量
  - 有向图：强连通分量（Kosaraju/Tarjan）
  - 最小生成树：Prim/Kruskal
  - 最短路径：Dijkstra、Bellman-Ford
  - 最大流：Ford-Fulkerson
  - 字符串算法：字符串排序、Trie树、子字符串搜索（KMP/Boyer-Moore/Rabin-Karp）
  - 正则表达式匹配与数据压缩

**适合人群**: 有Java编程基础的数据结构与算法学习者
**推荐理由**: 作者亲自授课，配套可视化算法动画和无代码评测系统，学习体验极佳。是Coursera上评分最高的计算机课程之一。

---
*来源: https://www.coursera.org/learn/algorithms-part1*"""
})

# ═══════════════════════════════════════════════════════════════
# 9. 程序设计 (3 resources)
# ═══════════════════════════════════════════════════════════════

RESOURCES.append({
    "title": "Harvard CS50——计算机科学导论",
    "description": "哈佛大学传奇课程CS50，被誉为全球最好的编程入门课。David Malan教授以极具感染力的教学方式，从C语言到Python到Web开发，构建完整的计算机科学视野。",
    "course": "程序设计", "chapter": "编程基础", "difficulty": "BASIC",
    "type": "VIDEO",
    "tags": ["CS50", "哈佛", "C语言", "Python", "Web开发", "计算机科学", "编程入门", "David Malan"],
    "source_url": "https://www.edx.org/learn/computer-science/harvard-university-cs50s-introduction-to-computer-science",
    "content": """# Harvard CS50——计算机科学导论

**视频来源**: edX/YouTube — David J. Malan (Harvard University)
**时长**: 约35小时（11周课程，每周约3小时授课）
**语言**: 英文（中英文字幕）
**内容概要**:
- 第0周：Scratch图形化编程——计算思维入门
- 第1周：C语言——编译、类型、条件、循环、函数
- 第2周：数组——字符串处理、命令行参数、密码学基础
- 第3周：算法——线性搜索、二分搜索、冒泡/选择/归并排序
- 第4周：内存——指针、malloc/free、内存布局、文件I/O
- 第5周：数据结构——链表、哈希表、Trie树
- 第6周：Python——语法对比、面向对象、数据处理
- 第7周：SQL——关系数据库、CRUD操作、SQL注入防御
- 第8周：HTML/CSS/JavaScript——前端Web开发基础
- 第9周：Flask框架——后端路由、模板渲染、Session
- 第10周：网络安全与道德——伦理讨论、Final Project指导

**适合人群**: 零基础编程入门者、跨专业转计算机的学生
**推荐理由**: CS50不仅仅是一门编程课，它传递对计算机科学的热爱。David Malan教授的授课充满激情，课程制作精良（TED级别制作），是全球最具影响力的计算机科学入门课程。

---
*来源: https://www.edx.org/learn/computer-science/harvard-university-cs50s-introduction-to-computer-science*"""
})

RESOURCES.append({
    "title": "MIT 6.0001 Introduction to CS and Programming in Python",
    "description": "MIT计算机科学与Python编程导论课程（Ana Bell, Eric Grimson主讲），以计算思维为核心，通过Python语言教授算法设计、数据结构、面向对象编程和软件工程基础。",
    "course": "程序设计", "chapter": "Python编程", "difficulty": "BASIC",
    "type": "VIDEO",
    "tags": ["Python", "MIT", "编程导论", "算法", "调试", "面向对象", "计算思维"],
    "source_url": "https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/",
    "content": """# MIT 6.0001 Introduction to CS and Programming in Python

**视频来源**: MIT OpenCourseWare — Ana Bell, Eric Grimson
**时长**: 约30小时（12讲，每讲约50分钟）
**语言**: 英文（含英文字幕）
**内容概要**:
- 第1讲：什么是计算——声明式知识与命令式知识
- 第2讲：Python基础——变量、类型、分支与循环
- 第3讲：字符串操作、输入/输出、逼近与二分查找
- 第4讲：函数的分解、抽象与递归
- 第5讲：元组、列表、别名与可变性
- 第6讲：字典与键值存储
- 第7讲：测试与调试——黑盒测试、白盒测试、异常处理
- 第8讲：面向对象编程——类、实例、继承
- 第9讲：程序效率与算法复杂度分析
- 第10讲：搜索与排序算法
- 第11讲：算法设计策略——分治法与动态规划
- 第12讲：课程总结与软件工程实践

**适合人群**: 编程零基础但数学基础较好的学生
**推荐理由**: 不同于一般编程课侧重于语法教学，6.0001以「计算思维」为主线，帮助学生建立抽象、分解、算法设计的思维方式。是编程入门与计算思维训练兼具的优质课程。

---
*来源: https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/*"""
})

RESOURCES.append({
    "title": "C++面向对象编程与STL深度实战",
    "description": "C++核心编程课程，涵盖面向对象四大特性（封装/继承/多态/抽象）、模板编程、STL标准库容器与算法、智能指针、移动语义、并发编程等现代C++特性。",
    "course": "程序设计", "chapter": "C++高级编程", "difficulty": "INTERMEDIATE",
    "type": "VIDEO",
    "tags": ["C++", "面向对象", "STL", "智能指针", "模板", "多态", "泛型编程"],
    "source_url": "https://www.youtube.com/playlist?list=PLlrATfBNZ98dudnM48yfGUldqGD0S4FFb",
    "content": """# C++面向对象编程与STL深度实战

**视频来源**: YouTube — The Cherno (C++系列)
**时长**: 约25小时（合集）
**语言**: 英文（含英文字幕）
**内容概要**:
- C++编译链接全过程：预处理、编译、汇编、链接
- 内存模型：栈/堆/静态区、new/delete与内存泄漏
- 智能指针：unique_ptr、shared_ptr、weak_ptr的用法与内部实现
- 左值与右值、移动语义、完美转发
- 面向对象编程：构造函数/析构函数、拷贝控制、运算符重载
- 继承与多态：虚函数表（vtable）实现原理
- 模板编程：函数模板、类模板、变参模板
- STL容器深度解析：vector扩容/string SSO/deque底层
- STL算法：sort/partition/nth_element/accumulate
- Lambda表达式与函数对象
- 多线程编程：std::thread/mutex/condition_variable
- RAII与异常安全保证
- CMake构建系统基础

**适合人群**: 有C语言基础的C++学习者、需要进行系统级开发的工程师
**推荐理由**: The Cherno的C++系列以工程视角深入剖析语言特性背后的实现原理，从vtable内存布局到STL源码级讲解，是C++进阶学习的宝贵资源。

---
*来源: https://www.youtube.com/playlist?list=PLlrATfBNZ98dudnM48yfGUldqGD0S4FFb*"""
})

# ═══════════════════════════════════════════════════════════════
# 10. 离散数学 (2 resources)
# ═══════════════════════════════════════════════════════════════

RESOURCES.append({
    "title": "MIT 6.042J Mathematics for Computer Science",
    "description": "MIT计算机科学数学基础课程（Tom Leighton主讲），涵盖命题逻辑、集合论、数论、图论、组合数学、概率论等计算机科学必需的离散数学工具。",
    "course": "离散数学", "chapter": "计算机科学中的数学", "difficulty": "ADVANCED",
    "type": "VIDEO",
    "tags": ["离散数学", "MIT", "图论", "数论", "概率", "组合", "逻辑", "归纳法"],
    "source_url": "https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/",
    "content": """# MIT 6.042J Mathematics for Computer Science

**视频来源**: MIT OpenCourseWare — Tom Leighton, Marten van Dijk
**时长**: 约40小时（25讲，每讲约60分钟）
**语言**: 英文（含英文字幕）
**内容概要**:
- 命题逻辑与谓词逻辑：真值表、逻辑等价、量词
- 证明方法：直接证明、反证法、归纳法（数学归纳、强归纳、结构归纳）
- 集合论：集合操作、幂集、无限集（可数与不可数）
- 关系与函数：等价关系、偏序、函数复合
- 数论：模算术、欧几里得算法、RSA公钥密码
- 图论：图的遍历、连通性、欧拉路径、哈密顿回路
- 图着色与匹配：二分图匹配、Hall婚姻定理
- 树与生成树：Cayley公式、最小生成树
- 组合计数：排列组合、容斥原理、鸽巢原理
- 生成函数与递推关系求解
- 概率论基础：条件概率、贝叶斯定理、随机变量与期望
- 离散随机过程：马尔可夫链、随机游走

**适合人群**: 计算机专业本科生、需要提升数学基础的研究生
**推荐理由**: 6.042J去掉了传统数学课程中与计算机科学无关的内容，聚焦于算法分析、密码学、机器学习等领域的数学基础。Tom Leighton教授（Akamai联合创始人）将数学理论与CS应用紧密结合。

---
*来源: https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/*"""
})

RESOURCES.append({
    "title": "北大离散数学——数理逻辑与图论",
    "description": "北京大学离散数学经典课程，系统讲解命题逻辑与一阶谓词逻辑的语法语义、推理系统，以及图论中的连通性、着色、匹配、平面图等核心概念。",
    "course": "离散数学", "chapter": "数理逻辑与图论", "difficulty": "INTERMEDIATE",
    "type": "VIDEO",
    "tags": ["离散数学", "北京大学", "数理逻辑", "图论", "谓词逻辑", "推理", "平面图"],
    "source_url": "https://www.bilibili.com/video/BV1BW411n7Jb",
    "content": """# 北大离散数学——数理逻辑与图论

**视频来源**: bilibili/中国大学MOOC — 北京大学信息科学技术学院
**时长**: 约35小时（共10周课程）
**语言**: 中文
**内容概要**:
- 命题逻辑：命题符号化、联结词、真值表、范式（合取/析取）
- 命题逻辑推理：推理规则、自然演绎系统、归结原理
- 一阶谓词逻辑：谓词、量词、谓词公式、解释与赋值
- 谓词演算：前束范式、Skolem标准型
- 谓词逻辑的推理与理论
- 集合论基础：集合运算、笛卡尔积、关系、函数
- 代数系统：运算律、代数结构（半群/幺半群/群）
- 格与布尔代数
- 图论基础：图的概念、握手定理、连通性
- 欧拉图与哈密顿图
- 树与生成树
- 平面图与欧拉公式
- 图的着色与匹配
- 图论算法应用

**适合人群**: 计算机专业本科生、考研备考学生
**推荐理由**: 北大离散数学课程内容体系完整，逻辑推导严谨，例题丰富。数理逻辑和图论部分是考研和算法设计的重要基础，配合课后习题训练效果更佳。

---
*来源: https://www.bilibili.com/video/BV1BW411n7Jb*"""
})

# ═══════════════════════════════════════════════════════════════
# 11. 人工智能 (3 resources)
# ═══════════════════════════════════════════════════════════════

RESOURCES.append({
    "title": "UC Berkeley CS188 Introduction to Artificial Intelligence",
    "description": "UC Berkeley人工智能导论课程，覆盖搜索、约束满足、博弈、马尔可夫决策过程、强化学习、贝叶斯网络、隐马尔可夫模型、机器学习基础等AI核心主题。",
    "course": "人工智能", "chapter": "人工智能导论", "difficulty": "INTERMEDIATE",
    "type": "VIDEO",
    "tags": ["人工智能", "UC Berkeley", "搜索", "MDP", "贝叶斯网络", "强化学习", "AI导论"],
    "source_url": "https://www.edx.org/learn/artificial-intelligence/the-university-of-california-berkeley-cs188-1x-artificial-intelligence",
    "content": """# UC Berkeley CS188 Introduction to Artificial Intelligence

**视频来源**: edX/YouTube — Pieter Abbeel, Dan Klein (UC Berkeley)
**时长**: 约48小时（24讲，每讲约80分钟）
**语言**: 英文（含英文字幕）
**内容概要**:
- 智能Agent与环境模型：PEAS框架
- 无信息搜索：BFS/DFS/UCS/迭代加深/双向搜索
- 启发式搜索：贪心最佳优先、A*算法、可纳性与一致性
- 对抗搜索：Minimax、Alpha-Beta剪枝、Expectimax
- 约束满足问题CSP：回溯搜索、前向检验、弧一致性AC-3
- 马尔可夫决策过程MDP：Bellman方程、价值迭代/策略迭代
- 强化学习：TD学习、Q-Learning、探索与利用权衡
- 概率推理：贝叶斯网络表示与独立性
- 贝叶斯网络精确推理：变量消元、信念传播
- 隐马尔可夫模型HMM：前向/后向算法、Viterbi算法
- 粒子滤波与动态贝叶斯网络
- 机器学习：朴素贝叶斯、感知器、逻辑回归、神经网络基础
- Pac-Man编程实验：搜索、多Agent、RL、分类

**适合人群**: 有编程基础和概率论基础的学生
**推荐理由**: CS188以精心设计的Pac-Man吃豆人实验贯穿课程全部主题，在每个AI技术点上都有可编程实现的游戏化项目，是理论趣味与实践深度兼具的AI入门最佳选择。

---
*来源: https://www.edx.org/learn/artificial-intelligence/the-university-of-california-berkeley-cs188-1x-artificial-intelligence*"""
})

RESOURCES.append({
    "title": "Stanford CS221 Artificial Intelligence: Principles and Techniques",
    "description": "斯坦福大学人工智能原理与技术课程，Percy Liang主讲。从搜索、逻辑推理、规划到深度学习、自然语言处理，覆盖现代AI的核心技术栈。",
    "course": "人工智能", "chapter": "AI核心技术", "difficulty": "ADVANCED",
    "type": "VIDEO",
    "tags": ["人工智能", "Stanford", "搜索", "逻辑", "NLP", "深度学习", "知识表示"],
    "source_url": "https://www.youtube.com/playlist?list=PLoROMvodv4rO1NB9TD4iUZ3qghGEGtqNX",
    "content": """# Stanford CS221 Artificial Intelligence: Principles and Techniques

**视频来源**: YouTube/Stanford Online — Percy Liang, Dorsa Sadigh
**时长**: 约40小时（20讲，每讲约80分钟）
**语言**: 英文（含英文字幕）
**内容概要**:
- AI模型范式：Reflex模型、State模型、Variable模型、Logic模型
- 搜索问题：树搜索、图搜索、一致代价、A*及其变体
- 马尔可夫决策过程：价值迭代、策略迭代、Q-Learning
- 博弈论基础：零和博弈、纳什均衡
- 约束满足问题CSP：回溯+约束传播
- 贝叶斯网络：参数学习、结构学习
- 变量消元与连接树算法
- 最大似然估计MLE与最大后验估计MAP
- 逻辑推理：命题逻辑、一阶逻辑、归结原理
- 知识图谱与关系学习
- 深度学习：CNN/RNN/Transformer
- 强化学习：Deep Q-Network、策略梯度、Actor-Critic
- 自然语言处理：词嵌入、序列模型、Attention机制
- 计算机视觉与多模态学习

**适合人群**: 有良好编程和数学基础的AI方向学生
**推荐理由**: CS221以统一的数学框架串联AI各分支——搜索、推理、学习，帮助学生建立AI领域的全景知识图谱。Percy Liang教授的前沿研究视角让课程紧跟AI最新发展。

---
*来源: https://www.youtube.com/playlist?list=PLoROMvodv4rO1NB9TD4iUZ3qghGEGtqNX*"""
})

RESOURCES.append({
    "title": "人工智能导论——知识表示与专家系统",
    "description": "AI导论经典内容专题：知识表示方法（语义网络/框架/产生式）、确定性推理与不确定性推理、专家系统结构、自然语言处理基础、计算机视觉入门。",
    "course": "人工智能", "chapter": "知识表示与推理", "difficulty": "INTERMEDIATE",
    "type": "VIDEO",
    "tags": ["人工智能", "知识表示", "推理", "专家系统", "语义网络", "产生式", "NLP"],
    "source_url": "https://www.bilibili.com/video/BV19q4y197Lh",
    "content": """# 人工智能导论——知识表示与专家系统

**视频来源**: bilibili — 中科院/中国大学MOOC
**时长**: 约25小时
**语言**: 中文
**内容概要**:
- 人工智能历史：图灵测试、符号主义与连接主义
- 知识表示：产生式系统、语义网络、框架表示法
- 状态空间搜索：盲目搜索与启发式搜索
- 博弈树搜索与Alpha-Beta剪枝
- 确定性推理：归结原理、基于规则的演绎推理
- 不确定性推理：主观贝叶斯方法、可信度方法（CF模型）
- 证据理论（Dempster-Shafer理论）
- 专家系统：MYCIN、PROSPECTOR案例分析
- 专家系统开发工具与知识获取瓶颈
- 机器学习概述：归纳学习、决策树（ID3/C4.5）
- 自然语言处理基础：词法分析、句法分析、语义分析
- 计算机视觉基础：图像特征提取与模式识别
- AI伦理与社会影响

**适合人群**: AI方向初学者、计算机科学与技术专业本科生
**推荐理由**: 传统AI课程侧重于符号主义方法与知识推理，是理解AI发展历史和奠基性技术的重要入口。知识与深度学习结合（Neuro-Symbolic AI）是当前研究前沿。

---
*来源: https://www.bilibili.com/video/BV19q4y197Lh*"""
})

# ═══════════════════════════════════════════════════════════════
# 12. 机器学习 (3 resources)
# ═══════════════════════════════════════════════════════════════

RESOURCES.append({
    "title": "Andrew Ng Machine Learning (Coursera)",
    "description": "吴恩达（Andrew Ng）的机器学习经典课程，被誉为全球最受欢迎的ML入门课。从线性回归到神经网络再到推荐系统，用MATLAB/Octave实现算法，教学细致入微。",
    "course": "机器学习", "chapter": "机器学习基础", "difficulty": "BASIC",
    "type": "VIDEO",
    "tags": ["机器学习", "吴恩达", "线性回归", "神经网络", "SVM", "推荐系统", "Coursera"],
    "source_url": "https://www.coursera.org/learn/machine-learning",
    "content": """# Andrew Ng Machine Learning (Coursera)

**视频来源**: Coursera — Andrew Ng (Stanford University/DeepLearning.AI)
**时长**: 约55小时（11周课程）
**语言**: 英文（中文字幕）
**内容概要**:
- 第1周：引言——监督学习vs无监督学习、线性回归、梯度下降
- 第2周：多变量线性回归、特征缩放、正规方程
- 第3周：逻辑回归、正则化、过拟合与欠拟合
- 第4周：神经网络表示——前向传播、反向传播
- 第5周：神经网络训练——梯度检查、随机初始化
- 第6周：应用建议——偏差/方差诊断、学习曲线、误差分析
- 第7周：支持向量机SVM——大间隔分类器、核函数
- 第8周：无监督学习——K-Means、主成分分析PCA
- 第9周：异常检测与推荐系统——协同过滤
- 第10周：大规模机器学习——随机梯度下降、MapReduce
- 第11周：应用案例——OCR（滑动窗口检测+人工数据合成）

**适合人群**: 有线性代数和程序设计基础的机器学习初学者
**推荐理由**: 这是全球最具影响力的ML课程，累计超过500万学习者。吴恩达以深入浅出的方式讲解数学直觉和工程实践，是进入机器学习领域的最佳起点。

---
*来源: https://www.coursera.org/learn/machine-learning*"""
})

RESOURCES.append({
    "title": "李宏毅机器学习深度学习教程",
    "description": "台湾大学李宏毅教授的机器学习和深度学习课程，以生动幽默的教学风格著称，涵盖监督学习、自监督学习、Transformer、GAN、扩散模型等现代ML/DL核心技术。",
    "course": "机器学习", "chapter": "深度学习与生成模型", "difficulty": "INTERMEDIATE",
    "type": "VIDEO",
    "tags": ["机器学习", "深度学习", "李宏毅", "Transformer", "GAN", "自监督学习", "扩散模型"],
    "source_url": "https://www.bilibili.com/video/BV1TD4y137mP",
    "content": """# 李宏毅机器学习深度学习教程

**视频来源**: bilibili/YouTube — 李宏毅教授（台湾大学）
**时长**: 约60小时（2023版完整课程）
**语言**: 中文（繁体/简体字幕）
**内容概要**:
- 机器学习基本概念：函数、损失、优化
- 深度学习基础：反向传播、梯度消失/爆炸、激活函数
- 训练技巧：Dropout、BatchNorm、残差连接
- 卷积神经网络CNN：感受野、权值共享、经典架构
- 自注意力机制与Transformer架构详解
- BERT、GPT系列预训练语言模型
- 自监督学习：SimCLR、BYOL、MAE
- 生成对抗网络GAN：WGAN、StyleGAN、CycleGAN
- 扩散模型DDPM与Stable Diffusion原理
- 强化学习：Policy Gradient、PPO
- 链式提示与上下文学习
- 模型压缩：知识蒸馏、量化、剪枝
- 机器学习可解释性

**适合人群**: 有Python编程基础、希望系统学习ML/DL的学习者
**推荐理由**: 李宏毅教授是华语地区最具影响力的ML教学者之一。课程紧跟前沿（每年更新），从数学直觉到最新论文解读，配合生动的PPT动画，让深度学习不再是「黑盒」。

---
*来源: https://www.bilibili.com/video/BV1TD4y137mP*"""
})

RESOURCES.append({
    "title": "Stanford CS229 Machine Learning",
    "description": "斯坦福大学机器学习课程（Andrew Ng经典完整版），以数学严谨性著称。从概率论与线性代数的ML视角出发，系统推导监督学习、无监督学习、学习理论等核心算法。",
    "course": "机器学习", "chapter": "机器学习理论", "difficulty": "ADVANCED",
    "type": "VIDEO",
    "tags": ["机器学习", "Stanford", "数学推导", "学习理论", "EM算法", "因子分析", "强化学习"],
    "source_url": "https://www.youtube.com/playlist?list=PLoROMvodv4rMiGQp3WXShtMGgzqpfVfbU",
    "content": """# Stanford CS229 Machine Learning

**视频来源**: YouTube/Stanford Online — Andrew Ng
**时长**: 约30小时（20讲，每讲约75分钟）
**语言**: 英文（含英文字幕）
**内容概要**:
- 线性回归的概率解释与locally weighted回归
- 逻辑回归与广义线性模型GLM
- 生成学习算法：高斯判别分析GDA、朴素贝叶斯
- 核方法与支持向量机SVM：对偶问题、SMO算法
- 学习理论：偏差/方差分解、VC维、Hoeffding不等式
- 模型选择与特征选择
- 集成方法：Bagging、Boosting（AdaBoost、GBDT）
- EM算法与混合高斯模型
- 因子分析：概率PCA、期望最大化
- 独立成分分析ICA
- 强化学习：MDP、价值函数近似、策略梯度
- 主成分分析PCA与奇异值分解SVD
- 变分自编码器VAE与自回归模型

**适合人群**: 有扎实数学基础（线性代数+概率论+微积分）的机器学习方向学生
**推荐理由**: CS229是ML领域最严谨的理论课程之一。不同于Coursera版的应用导向，CS229深入推导每一个算法的数学基础，是ML研究者必学的理论基石。

---
*来源: https://www.youtube.com/playlist?list=PLoROMvodv4rMiGQp3WXShtMGgzqpfVfbU*"""
})

# ═══════════════════════════════════════════════════════════════
# 13. 信息安全 (2 resources)
# ═══════════════════════════════════════════════════════════════

RESOURCES.append({
    "title": "Stanford Cryptography I (Coursera)",
    "description": "斯坦福大学Dan Boneh教授的密码学课程（Coursera），全球最受欢迎的密码学入门课。从流密码、分组密码到公钥密码、数字签名，理论深度与实践意识兼备。",
    "course": "信息安全", "chapter": "密码学基础", "difficulty": "ADVANCED",
    "type": "VIDEO",
    "tags": ["信息安全", "密码学", "加密", "AES", "RSA", "数字签名", "Dan Boneh"],
    "source_url": "https://www.coursera.org/learn/crypto",
    "content": """# Stanford Cryptography I (Coursera)

**视频来源**: Coursera — Dan Boneh (Stanford University)
**时长**: 约25小时（6周课程）
**语言**: 英文（中文字幕）
**内容概要**:
- 第1周：密码学概述、历史密码与一次一密、流密码
- 第2周：分组密码——AES/DES、Feistel网络、PRG/PRF/PRP
- 第3周：消息完整性——MAC、CBC-MAC、PMAC、碰撞抵抗
- 第4周：认证加密——GCM模式、TLS记录协议
- 第5周：密钥交换——Merkle谜题、Diffie-Hellman协议
- 第6周：公钥加密——RSA、ElGamal、陷门函数
- 数字签名——RSA/FDH、PKCS1方案
- 基于身份的加密与属性加密简介
- 安全概念：IND-CPA、IND-CCA
- 随机预言机模型

**适合人群**: 有离散数学基础的信息安全方向学生和从业者
**推荐理由**: Dan Boneh是密码学领域的顶级学者。课程以数学推导和安全性证明为主线，配合真实攻击案例分析，让学生在理解算法原理的同时建立安全工程意识。

---
*来源: https://www.coursera.org/learn/crypto*"""
})

RESOURCES.append({
    "title": "Web安全攻防实战与渗透测试入门",
    "description": "Web安全实战课程，覆盖OWASP Top 10漏洞原理与利用：SQL注入、XSS跨站脚本、CSRF、SSRF、文件上传、反序列化漏洞等，以及渗透测试方法论和工具实战。",
    "course": "信息安全", "chapter": "Web安全", "difficulty": "INTERMEDIATE",
    "type": "VIDEO",
    "tags": ["信息安全", "Web安全", "SQL注入", "XSS", "CSRF", "渗透测试", "OWASP", "CTF"],
    "source_url": "https://www.youtube.com/playlist?list=PLyRiR1qH3lCyDG8E2fNDc2MQ0Zb9DP1bQ",
    "content": """# Web安全攻防实战与渗透测试入门

**视频来源**: YouTube — LiveOverflow / Portswigger Web Security Academy
**时长**: 约20小时（合集系列）
**语言**: 英文
**内容概要**:
- Web安全基础：HTTP协议安全、同源策略、CORS
- SQL注入：Error-based/Union/Blind/Time-based注入、sqlmap工具
- XSS跨站脚本：反射型/存储型/DOM型、CSP防御、HttpOnly Cookie
- CSRF跨站请求伪造：Token同步、SameSite Cookie
- SSRF服务端请求伪造：内网探测与协议利用
- 文件上传漏洞：扩展名绕过、MIME绕过、内容检测绕过
- 命令注入与代码注入
- 反序列化漏洞：PHP/Java反序列化利用链
- XXE外部实体注入
- 逻辑漏洞与越权（IDOR）
- 渗透测试方法论：信息收集、漏洞扫描、漏洞利用、后渗透
- 常用工具：Burp Suite、nmap、Metasploit基础
- CTF竞赛Web题目解法

**适合人群**: 对Web安全感兴趣的后端开发者和安全初学者
**推荐理由**: 以攻促防的学习路线，通过实际漏洞复现和CTF题目训练，帮助开发者和安全爱好者理解Web应用的主要威胁和防御策略。

---
*来源: https://www.youtube.com/playlist?list=PLyRiR1qH3lCyDG8E2fNDc2MQ0Zb9DP1bQ*"""
})

# ═══════════════════════════════════════════════════════════════
# 14. 分布式系统 (3 resources)
# ═══════════════════════════════════════════════════════════════

RESOURCES.append({
    "title": "MIT 6.824 Distributed Systems",
    "description": "MIT分布式系统工程课程（Robert Morris主讲），全球最具影响力的分布式系统课程。深入讲解一致性协议（Raft/Paxos）、分布式事务、复制、容错、MapReduce等核心主题。",
    "course": "分布式系统", "chapter": "分布式一致性", "difficulty": "ADVANCED",
    "type": "VIDEO",
    "tags": ["分布式系统", "MIT", "Raft", "Paxos", "MapReduce", "一致性", "容错", "分布式事务"],
    "source_url": "https://ocw.mit.edu/courses/6-824-distributed-computer-systems-engineering-spring-2015/",
    "content": """# MIT 6.824 Distributed Systems

**视频来源**: MIT OpenCourseWare — Robert Morris
**时长**: 约50小时（24讲，每讲约80分钟）
**语言**: 英文（含英文字幕）
**内容概要**:
- 分布式系统概述：CAP理论、拜占庭将军问题
- MapReduce编程模型与容错设计
- GFS/Google File System：master/chunkserver架构
- Raft共识协议：Leader选举、日志复制、安全性证明
- 分布式事务：两阶段提交2PC、三阶段提交3PC
- 并发控制：乐观锁、悲观锁、时间戳排序
- 复制与一致性：主从复制、Quorum读写、链复制
- Paxos协议：Basic Paxos、Multi-Paxos
- 分布式一致性：线性一致性、顺序一致性、因果一致性
- Spanner：TrueTime、原子钟、外部一致性
- FaRM：RDMA加速的分布式内存计算
- 拜占庭容错BFT：PBFT协议
- Zookeeper：分布式协调服务、ZAB协议
- CRAQ链复制：读性能优化
- 区块链与Bitcoin共识机制

**适合人群**: 有网络编程和操作系统基础的研究生和高级工程师
**推荐理由**: 6.824是全球分布式系统领域最权威的教学课程。Raft协议的Lab是分布式系统面试的「敲门砖」，完整实现后将深刻理解一致性、复制和容错的设计哲学。

---
*来源: https://ocw.mit.edu/courses/6-824-distributed-computer-systems-engineering-spring-2015/*"""
})

RESOURCES.append({
    "title": "Distributed Systems——Martin Kleppmann讲座系列",
    "description": "《Designing Data-Intensive Applications》作者Martin Kleppmann的分布式系统讲座，涵盖共识算法、分布式事务、流处理、事件溯源等领域的前沿实践。",
    "course": "分布式系统", "chapter": "数据密集型应用设计", "difficulty": "ADVANCED",
    "type": "VIDEO",
    "tags": ["分布式系统", "DDIA", "Kleppmann", "共识", "流处理", "CRDT", "事务"],
    "source_url": "https://www.youtube.com/playlist?list=PLyzOVJj3bHQuz2jR6MmWx5uBKGaKb6rPH",
    "content": """# Distributed Systems——Martin Kleppmann讲座系列

**视频来源**: YouTube — Martin Kleppmann (University of Cambridge)
**时长**: 约15小时（合集系列）
**语言**: 英文
**内容概要**:
- 分布式系统的谬误与真实世界的挑战
- 时间、时钟与事件排序：Lamport时钟、向量时钟
- 共识协议演进：Paxos → Raft → EPaxos
- 分布式事务与Saga模式
- 事件驱动架构：CQRS与事件溯源（Event Sourcing）
- CRDT无冲突复制数据类型原理
- 流处理框架：Kafka Streams、Apache Flink
- 变更数据捕获CDC与Debezium
- 协调与共识的开销分析
- Consistency as Logical Monotonicity理论
- 本地优先软件Local-First Software理念
- 协作编辑系统（如Google Docs）的OT与CRDT实现对比

**适合人群**: 有分布式系统基础知识的系统架构师和后端工程师
**推荐理由**: Kleppmann是《数据密集型应用系统设计》的作者，其讲座深入浅出地将学术界的最新分布式共识理论与工业界大规模系统的实践经验融会贯通。

---
*来源: https://www.youtube.com/playlist?list=PLyzOVJj3bHQuz2jR6MmWx5uBKGaKb6rPH*"""
})

RESOURCES.append({
    "title": "分布式系统原理与实践——微服务架构深度解析",
    "description": "分布式系统工程实践课程，涵盖微服务拆分策略、服务注册与发现、API网关、配置中心、分布式追踪、消息队列、容器化部署等现代分布式系统核心技术栈。",
    "course": "分布式系统", "chapter": "微服务架构", "difficulty": "INTERMEDIATE",
    "type": "VIDEO",
    "tags": ["分布式系统", "微服务", "服务发现", "API网关", "消息队列", "分布式追踪", "Kubernetes"],
    "source_url": "https://www.youtube.com/playlist?list=PLmZ8mO6qWFlfBJlsYXBRfB8hV-lq4Rpbq",
    "content": """# 分布式系统原理与实践——微服务架构深度解析

**视频来源**: YouTube — InfoQ / GOTO Conferences
**时长**: 约12小时（精选讲座合集）
**语言**: 英文/中文
**内容概要**:
- 单体到微服务的演进策略与DDD领域驱动设计
- 服务注册与发现：Consul、Eureka、Nacos对比
- API网关：Kong、Zuul、Spring Cloud Gateway
- 配置中心：Apollo、Nacos原理
- 负载均衡：客户端/服务端负载均衡、一致性哈希
- 服务间通信：REST/gRPC/消息队列选型
- 分布式事务：Seata（AT/TCC/Saga模式）
- 消息队列：Kafka/RocketMQ/RabbitMQ对比
- 分布式链路追踪：Jaeger/Zipkin/SkyWalking
- 熔断与限流：Sentinel/Hystrix、令牌桶/漏桶算法
- 容器编排：Kubernetes核心概念与微服务部署
- 可观测性三支柱：Metrics/Tracing/Logging
- 混沌工程与分布式系统测试

**适合人群**: 从事后端开发与架构设计的工程师
**推荐理由**: 不在于讲分布式理论，而在于展示工业界如何用实际技术栈落地分布式架构。多场GOTO和QCon演讲精选，演讲者来自Netflix、Uber、阿里巴巴等一线互联网公司。

---
*来源: https://www.youtube.com/playlist?list=PLmZ8mO6qWFlfBJlsYXBRfB8hV-lq4Rpbq*"""
})

# ═══════════════════════════════════════════════════════════════
# 15. 计算机图形学 (2 resources)
# ═══════════════════════════════════════════════════════════════

RESOURCES.append({
    "title": "GAMES101——现代计算机图形学入门",
    "description": "闫令琪教授的GAMES101课程，华语地区最具影响力的计算机图形学入门课。从线性代数基础到光线追踪、光栅化、几何处理、动画模拟，覆盖图形学四大核心领域。",
    "course": "计算机图形学", "chapter": "图形学基础", "difficulty": "INTERMEDIATE",
    "type": "VIDEO",
    "tags": ["计算机图形学", "GAMES101", "闫令琪", "光线追踪", "光栅化", "渲染", "几何"],
    "source_url": "https://www.bilibili.com/video/BV1X7411F744",
    "content": """# GAMES101——现代计算机图形学入门

**视频来源**: bilibili — 闫令琪教授（UCSB / 原UCSB，现为...）
**时长**: 约35小时（22讲，每讲约65分钟）
**语言**: 中文
**内容概要**:
- 图形学概述与应用领域
- 线性代数复习：向量/矩阵/变换（模型/视图/投影）
- 光栅化：Bresenham算法、三角形光栅化、反走样（MSAA/FXAA/TAA）
- 着色：Blinn-Phong光照模型、着色频率（Flat/Gouraud/Phong）
- 图形管线：顶点/几何/片元着色器
- 纹理映射：重心坐标插值、Mipmap、各向异性过滤
- 几何表示：隐式表面（SDF）、显式表面（网格）、贝塞尔曲线
- 曲面：贝塞尔曲面、曲面细分、细分曲面（Catmull-Clark）
- 光线追踪：Whitted-style光线追踪、光线-物体求交
- 加速结构：BVH包围盒层次、KD-Tree
- 辐射度量学：Radiant Flux/Irradiance/Radiance
- 路径追踪：蒙特卡洛积分、俄罗斯轮盘、重要性采样
- 材质：微表面模型（Cook-Torrance）、BRDF
- 计算机动画基础：质点弹簧系统、粒子系统

**适合人群**: 有线性代数基础的计算机图形学初学者
**推荐理由**: GAMES101是华语图形学社区的教学标杆。闫令琪教授以清晰的数学推导和精美的渲染图片，将图形学四大领域娓娓道来。配套作业从零实现软渲染器，学习曲线平滑，成就感极强。

---
*来源: https://www.bilibili.com/video/BV1X7411F744*"""
})

RESOURCES.append({
    "title": "UC San Diego CSE 167 Computer Graphics",
    "description": "加州大学圣地亚哥分校计算机图形学课程，Ravi Ramamoorthi教授主讲。深入讲解真实感渲染的物理基础与数学原理，涵盖光线追踪、辐射度量学、蒙特卡洛渲染等高阶主题。",
    "course": "计算机图形学", "chapter": "真实感渲染", "difficulty": "ADVANCED",
    "type": "VIDEO",
    "tags": ["计算机图形学", "渲染", "光线追踪", "蒙特卡洛", "BRDF", "辐射度量学", "UCSD"],
    "source_url": "https://www.edx.org/learn/computer-graphics/uc-san-diegox-cse167x-computer-graphics",
    "content": """# UC San Diego CSE 167 Computer Graphics

**视频来源**: edX/YouTube — Ravi Ramamoorthi (UC San Diego)
**时长**: 约30小时（16讲，每讲约75分钟）
**语言**: 英文（含英文字幕）
**内容概要**:
- 图形学数学基础：向量/矩阵/变换/四元数旋转
- OpenGL与着色器编程（GLSL）
- 光栅化管线：视口变换、裁剪、背面剔除、深度测试
- 纹理映射与过滤技术
- 光照与着色模型：Phong反射模型、Gouraud/Phong着色
- 辐射度量学基础：Radiometry、Photometry
- BRDF反射模型与渲染方程
- 光线追踪：递归光线追踪、分布式光线追踪
- 蒙特卡洛路径追踪：重要性采样、分层采样
- 光子映射与辐射度方法
- 几何处理：网格简化、细分曲面
- 阴影生成：Shadow Map、Shadow Volume
- 全局光照：路径追踪、光子映射、Instant Radiosity
- 参与介质与次表面散射

**适合人群**: 有图形学基础和高等数学背景的研究生
**推荐理由**: Ravi Ramamoorthi是SIGGRAPH最佳论文奖得主，课程在真实感渲染的物理原理讲解上深入透彻，是学习PBR（Physically Based Rendering）和离线渲染的理论基础课程。

---
*来源: https://www.edx.org/learn/computer-graphics/uc-san-diegox-cse167x-computer-graphics*"""
})

if __name__ == "__main__":
    run_import(RESOURCES, "batch4_part4")
