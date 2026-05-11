"""
Generate language/programming wiki topics and append to wiki_topics.json.
Each topic has real CS content with official sources.
"""
import json
from pathlib import Path

# ── Topic specifications: (course, chapter, difficulty, title_suffix, file_stem, tags, aliases, source, sections)
# sections is list of (heading, content) tuples

LANG_TOPICS = {
    "C语言深入": [
        ("指针与内存", "ADVANCED",
         "C语言-指针算术与内存模型", "指针算术与内存模型",
         ["C语言", "指针", "内存模型", "undefined behavior"],
         ["C Pointers", "Memory Model"],
         "C11 Standard ISO/IEC 9899:2011 §6.5.6; K&R《The C Programming Language》第5章",
         [
             ("核心定义", "C语言的指针算术基于对象大小自动缩放。对T*类型的指针p，p+1的地址增加sizeof(T)字节。数组名在大多数表达式中退化为指向首元素的指针，但sizeof和&操作例外。指针算术合法范围：从数组首元素到末尾后一个位置（one-past-the-end），解引用one-past-the-end是未定义行为。"),
             ("内存模型", "C11将内存模型分为：对象(object)、值(value)、存储期(storage duration)、生命周期(lifetime)、有效类型(effective type)。严格别名规则(strict aliasing)禁止通过不兼容类型的指针访问同一内存位置（char* 例外）。违反严格别名规则导致UB。"),
             ("常见UB", "1. 空指针解引用 2. 数组越界 3. 有符号整数溢出 4. 使用已释放内存(use-after-free) 5. 多次释放(double-free) 6. 违反有效类型/严格别名规则 7. 返回局部变量的地址"),
             ("关联知识点", "[[C语言-位域与内存对齐]] [[C语言-预处理器宏与条件编译]] [[C语言-标准IO与文件操作]]"),
         ]),
        ("指针与内存", "INTERMEDIATE",
         "C语言-内存对齐与位域详解", "内存对齐与位域",
         ["C语言", "内存对齐", "位域", "struct布局", "pragma pack"],
         ["Memory Alignment", "Bit Fields"],
         "C11 Standard §6.7.2.1; GCC Manual §6.36 Structure-Packing Pragmas",
         [
             ("核心定义", "内存对齐(alignment)要求每个数据类型的地址必须是其对齐值的整数倍。自然对齐：N字节类型的地址必须是N的倍数（32位x86）。不对齐访问在某些架构(ARM/MIPS)上导致总线错误，在x86上通常有性能惩罚。struct成员按声明顺序排列，编译器插入padding以满足对齐约束。"),
             ("位域详解", "位域(struct bit-field)允许指定成员占用的位数。位域存储单元(通常是unsigned int)的分配受ABI约束。跨存储单元边界时可能产生padding。位域的顺序（little-endian/big-endian）、符号（signed vs unsigned）都是ABI相关的，不可移植。"),
             ("对齐优化", "按对齐值降序排列成员可减少padding（largest-first策略）。alignas(C11)或__attribute__((aligned))可以显式指定对齐。packed属性#pragma pack(1)消除padding但可能导致不对齐访问。"),
             ("关联知识点", "[[C语言-指针算术与内存模型]] [[C语言-联合体与类型双关]]"),
         ]),
        ("编译与链接", "ADVANCED",
         "C语言-链接器与ABI详解", "链接器与ABI",
         ["C语言", "链接器", "ABI", "ELF", "符号表", "动态链接"],
         ["Linker", "ABI", "ELF", "Dynamic Linking"],
         "ELF Specification (System V ABI); Levine《Linkers and Loaders》",
         [
             ("核心定义", "链接器将多个目标文件(.o)合并为可执行文件或共享库。主要任务：1.)符号解析(symbol resolution) 2.)重定位(relocation)。ABI(应用二进制接口)定义了：类型大小与对齐、调用约定(calling convention)、name mangling、异常处理和栈展开规则。"),
             ("ELF格式", "ELF(Executable and Linkable Format)是Linux/Unix的标准二进制格式。.text节存放代码，.data存放已初始化全局变量，.bss存放未初始化全局变量(零填充)，.rodata存放只读数据。PLT(Procedure Linkage Table)和GOT(Global Offset Table)实现延迟绑定动态链接。"),
             ("动态链接过程", "1.)execve加载ELF→2.)动态链接器ld.so映射依赖库→3.)执行重定位(RELOC/GLOB_DAT/JUMP_SLOT)→4.)执行.init段→5.)调用main()。RTLD_LAZY(使用时解析)优于RTLD_NOW(加载时全部解析)但可能触发运行时错误。"),
             ("关联知识点", "[[C语言-静态库与动态库构建]] [[C语言-预处理器宏与条件编译]]"),
         ]),
        ("预处理器", "INTERMEDIATE",
         "C语言-预处理器宏与条件编译", "预处理器宏与条件编译",
         ["C语言", "预处理器", "宏", "#define", "#ifdef", "条件编译"],
         ["Preprocessor", "Macros", "Conditional Compilation"],
         "C11标准 §6.10; GCC Manual §3 Macros",
         [
             ("核心定义", "C预处理器在编译前处理源代码文本。核心指令：#include（文件包含）、#define/#undef（宏定义/取消）、#if/#ifdef/#ifndef/#elif/#else/#endif（条件编译）、#pragma/#error/#line。宏展开遵循递归展开规则：先展开宏参数（非#或##相邻），再展开宏体，已展开的宏不会递归展开。"),
             ("宏技巧与陷阱", "1.)do{...}while(0)确保宏在if-else中的正确行为 2.)宏参数的多次求值问题(#define MAX(a,b) ((a)>(b)?(a):(b))对MAX(x++,y++)导致两次自增) 3.)字符串化(#)和标记粘贴(##)操作符 4.)可变参数宏__VA_ARGS__和##__VA_ARGS__(GNU扩展)"),
             ("条件编译", "#ifndef/#define HEADER_GUARD防止重复包含。_DEBUG vs NDEBUG控制assert()。__GNUC__/__STDC_VERSION__/__cplusplus等预定义宏用于跨平台适配。"),
             ("关联知识点", "[[C语言-链接器与ABI详解]] [[C语言-静态库与动态库构建]]"),
         ]),
    ],

    "程序设计语言原理": [
        ("类型系统", "ADVANCED",
         "程序设计语言-类型系统总览", "类型系统总览",
         ["程序设计语言", "类型系统", "Hindley-Milner", "多态", "子类型"],
         ["Type System", "Hindley-Milner", "Polymorphism"],
         "Pierce《Types and Programming Languages》; Wikipedia: Type system",
         [
             ("核心定义", "类型系统是一组给程序的各项赋予类型的形式规则。核心作用：1.)在编译期检测类型错误（type safety） 2.)指导编译器优化（类型信息消除运行时检查） 3.)程序设计与文档化。类型系统可分为：静态类型(Static)、动态类型(Dynamic)、强类型(Strong)、弱类型(Weak)。"),
             ("多态分类", "参数多态(Parametric): 函数/类型接受类型参数，如List<T>。特设多态(Ad-hoc): 函数重载，同名为不同类型实现不同行为。子类型多态(Subtype): 面向对象中的继承层次，基类指针调用派生类方法。行多态(Row): 记录类型扩展，如{a:int; b:string}兼容{a:int}。"),
             ("Hindley-Milner", "HM类型推导是ML系语言的标准算法。核心思想：为每个表达式生成类型变量，收集约束（unification constraints），求解constraint set。let多态允许泛化：let f = fun x -> x in ...中f被泛化为'a->'a。值限制(value restriction)处理mut-ref的安全泛化问题。"),
             ("关联知识点", "[[程序设计语言-静态与动态类型对比]] [[程序设计语言-结构化类型vs名义类型]]"),
         ]),
        ("求值与范式", "INTERMEDIATE",
         "程序设计语言-求值策略与副作用控制", "求值策略与副作用控制",
         ["程序设计语言", "求值策略", "惰性求值", "副作用", "引用透明"],
         ["Evaluation Strategy", "Lazy Evaluation", "Referential Transparency"],
         "Wikipedia: Evaluation strategy; Haskell Wiki: Lazy Evaluation",
         [
             ("核心定义", "求值策略决定函数参数何时被计算：1.)Call-by-Value(CBV/严格求值): 参数先求值再传入。C/Java/Python默认。2.)Call-by-Name(CBN): 参数原样传入，每次使用时求值。3.)Call-by-Need(惰性求值): CBN+memoization，第一次使用求值后缓存结果。Haskell默认。4.)Call-by-Reference: 传递变量地址。C++引用、Fortran。"),
             ("惰性求值优势", "1.)无限数据结构(如[1..]) 2.)短路求值在CBN下自然获得 3.)函数组合优化(融合transformation无需创建中间列表) 4.)默认=纯函数+惰性的Haskell模型。代价：1.)内存开销(thunk分配) 2.)时间不可预测性(space leak)"),
             ("引用透明", "引用透明(Referential Transparency): 表达式可以被其值替换而不改变程序语义。没有副作用的纯函数自然满足引用透明。RT使等式推理(equational reasoning)和编译器优化(公共子表达式消除)成为可能。"),
             ("关联知识点", "[[程序设计语言-闭包与词法作用域]] [[程序设计语言-Monad与纯函数式编程]]"),
         ]),
        ("并发模型", "ADVANCED",
         "程序设计语言-并发编程模型对比", "并发编程模型对比",
         ["程序设计语言", "并发", "Actor", "CSP", "STM", "异步"],
         ["Concurrency Models", "Actor Model", "CSP", "STM"],
         "Wikipedia: Actor model; Hoare《Communicating Sequential Processes》; Peyton Jones《Beautiful Concurrency》",
         [
             ("核心定义", "现代编程语言提供多种并发编程模型：1.)共享内存+锁(传统模型): C/Java的mutex/synchronized 2.)Actor模型: 每个actor独立状态，通过异步消息通信。Erlang/Akka。3.)CSP(通信顺序进程): 通道(channel)作为通信原语，select多路选择。Go的goroutine+channel。4.)STM(软件事务内存): 内存操作打包为原子事务提交。Clojure/Haskell。"),
             ("Actor vs CSP", "Actor关注点：谁接收消息（identity addressing），actor有邮箱(mailbox)，receive模式匹配。CSP关注点：谁发送数据（channel addressing），通道是匿名队列，发送方和接收方通过通道同步。Actor天然容错（supervisor hierarchy），CSP天然组合（pipeline/fan-out/fan-in pattern）。"),
             ("异步模型", "async/await语法糖将异步I/O表达为类同步代码。Rust的Future+trait Executor、JavaScript的Promise+事件循环、Go的goroutine+GMP调度、Python的asyncio coroutine。核心是：暂停点(yield point)→调度器换出→I/O完成→换入→继续执行。"),
             ("关联知识点", "[[程序设计语言-求值策略与副作用控制]] [[Rust语言-所有权与生命周期]]"),
         ]),
        ("闭包与作用域", "INTERMEDIATE",
         "程序设计语言-闭包与词法作用域", "闭包与词法作用域",
         ["程序设计语言", "闭包", "词法作用域", "自由变量", "捕获"],
         ["Closure", "Lexical Scope", "Free Variables"],
         "Wikipedia: Closure (computer programming); SICP §3.2 The Environment Model of Evaluation",
         [
             ("核心定义", "闭包(closure)是一等公民函数+其词法环境(自由变量绑定)的组合。词法作用域(静态作用域)指变量引用绑定到语法上最近的声明处。自由变量(free variable)是在函数内使用但未在函数内声明的变量，闭包捕获这些变量的绑定。"),
             ("捕获方式", "1.)按值捕获: 捕获变量在创建闭包时的值（Rust的move闭包）2.)按引用捕获: 捕获变量的引用，后续修改可见（JS默认、Python）3.)捕获可变引用: Rust的&mut闭包。捕获粒度：整体捕获 vs 按字段捕获（Rust 2021+）。"),
             ("实现技术", "闭包的底层实现：1.)flat closure: 将自由变量拷贝到闭包结构体(Rust/Golang)2.)linked closure: 嵌套作用域通过访问链(access link)实现(经典实现)3.)display closure: 所有闭包共享同一个值(不实用)。"),
             ("关联知识点", "[[程序设计语言-求值策略与副作用控制]] [[Rust语言-所有权与生命周期]]"),
         ]),
    ],

    "Java深入": [
        ("JVM", "ADVANCED",
         "Java-JVM架构与字节码", "JVM架构与字节码",
         ["Java", "JVM", "字节码", "类加载", "JIT编译"],
         ["JVM Architecture", "Bytecode", "Class Loading"],
         "Oracle JVM Specification SE 17; Wikipedia: Java virtual machine",
         [
             ("核心定义", "JVM(Java Virtual Machine)是运行Java字节码的虚拟机。核心组件：1.)类加载器(ClassLoader)子系统：Bootstrap→Extension→Application→用户自定义，遵循双亲委派模型 2.)运行时数据区：堆(所有线程共享)、方法区/元空间(Metaspace JDK8+)、虚拟机栈(每线程一栈)、PC寄存器、本地方法栈 3.)执行引擎：解释器+JIT编译器(C1/C2/Graal)"),
             ("字节码", ".class文件中的每条指令占1字节操作码+0~N操作数。典型指令：aload_0/iload_1(局部变量入栈)、invokevirtual(虚方法调用)、invokespecial(构造器/私有方法)、invokedynamic(动态语言支持JDK7+)。操作数栈+局部变量表架构(stack-based)，与寄存器的x86物理架构形成层次差异。"),
             ("类加载过程", "加载(Loading): 从.class文件读取字节流→链接(Linking): 验证(verify)+准备(prepare: 分配静态字段默认值)+解析(resolve: 符号引用→直接引用)→初始化(Initialization): 执行<clinit>静态初始化器。同一个类由不同ClassLoader加载视为不同类。"),
             ("关联知识点", "[[Java-GC算法与调优]] [[Java-JIT编译与性能优化]]"),
         ]),
        ("内存管理", "ADVANCED",
         "Java-GC算法与调优", "GC算法与调优",
         ["Java", "GC", "垃圾回收", "G1", "ZGC", "JVM调优"],
         ["Garbage Collection", "G1GC", "ZGC"],
         "Oracle G1 GC Documentation; Plumbr GC Handbook",
         [
             ("核心定义", "JVM的自动内存管理通过GC(垃圾回收)实现。Serial GC: 单线程标记-清除-整理，适合客户端应用。Parallel GC(JDK5): 多线程并行Stop-The-World回收，吞吐量优先。CMS(JDK5-14): 并发标记清除，低延迟目标但可能碎片化。G1(JDK7+, JDK9默认): 区域化(Region)GC，可预测暂停时间，并发标记+STW整理。ZGC(JDK11+): 亚毫秒暂停时间(<1ms)，染色指针(colored pointers)无需读屏障停顿，JDK15转为production-ready。"),
             ("G1详解", "G1将堆划分为大小相等的Region。Young GC(Eden/Survivor Region): STW复制到空Region。Mixed GC: 在Young GC基础上额外回收部分Old Region(Garbage-first: 优先回收垃圾最多的Region)。并发标记周期(Concurrent Mark): 初始标记(STW很短)→根区域扫描(并发)→并发标记→重新标记(STW快)→清除(并发)。"),
             ("调优参数", "-Xms/-Xmx: 初始/最大堆。G1: -XX:MaxGCPauseMillis=200ms, -XX:InitiatingHeapOccupancyPercent=45(IHOP阈值触发并发标记)。ZGC: -XX:ZCollectionInterval(两次GC最小间隔)。开启GC日志分析: -Xlog:gc*:file=gc.log+GCViewer/GCeasy可解析可视化。"),
             ("关联知识点", "[[Java-JVM架构与字节码]] [[Java-内存模型JMM]]"),
         ]),
        ("并发", "ADVANCED",
         "Java-AQS与JUC并发框架", "AQS与JUC并发框架",
         ["Java", "并发", "AQS", "JUC", "Lock", "线程池"],
         ["AQS", "AbstractQueuedSynchronizer", "JUC"],
         "Java SE Documentation java.util.concurrent; Doug Lea《Java并发编程实战》",
         [
             ("核心定义", "AQS(AbstractQueuedSynchronizer)是JUC包的核心框架，基于FIFO双向队列+int state实现同步器。CLH变体节点：线程被封装为Node加入等待队列，自旋+信号的方式等待。state>0表示被占有，state=0表示可用。模板方法：tryAcquire/tryRelease/tryAcquireShared/tryReleaseShared由子类定义获取/释放语义。"),
             ("基于AQS的实现", "ReentrantLock: tryAcquire通过CAS设置state从0→1，重入时state++。CountDownLatch: state=count，await等待state=0，countDown()通过CAS减state。Semaphore: state=permits，tryAcquireShared当state>0时CAS减state。CyclicBarrier不使用AQS而是ReentrantLock+Condition。"),
             ("线程池原理", "ThreadPoolExecutor: corePoolSize核心线程常驻，最大线程数maximumPoolSize，超过corePoolSize的线程空闲keepAliveTime后被回收。workQueue: 无界队列/有界队列/SynchronousQueue直传模式。拒绝策略: CallerRuns/Abort/Discard/DiscardOldest。"),
             ("关联知识点", "[[Java-内存模型JMM]] [[Java-JVM架构与字节码]]"),
         ]),
    ],

    "Go语言": [
        ("并发模型", "ADVANCED",
         "Go语言-GMP调度器与goroutine", "GMP调度器与goroutine",
         ["Go", "goroutine", "GMP", "调度器", "并发"],
         ["GMP Scheduler", "Goroutine Scheduling"],
         "Go Runtime Source Code (src/runtime/proc.go); Go Blog: The Go Scheduler",
         [
             ("核心定义", "Go的并发模型基于GMP调度器：G(Goroutine)=轻量级协程，M(Machine)=操作系统线程，P(Processor)=逻辑处理器(默认=GOMAXPROCS=CPU核数)。每个P持有本地runq(环形队列，容量256)，M绑定P后从P的runq取G执行。全局runq+Network Poller作为补充调度源。当一个G阻塞（系统调用/网络IO/channel操作），P与当前M解绑，寻找新的M或新建M。"),
             ("抢占调度", "Go 1.14+基于信号的抢占：sysmon监控线程定期给长时间运行的G发送SIGURG信号，触发异步抢占点。抢占点(checkpoint): 函数调用前检查stackguard0标记，若需要抢占则进入调度循环。1.13以前只能协作式抢占（函数调用处），导致紧密循环不调度。"),
             ("Work Stealing", "当P的本地runq为空，随机选择其他P的runq窃取一半G。Net Poller充当'全局网络G循环队列'的角色：当netpoller检测到fd就绪，将等待的G插入就绪队列。"),
             ("关联知识点", "[[Go语言-channel实现原理]] [[Go语言-内存管理与GC]]"),
         ]),
        ("Channel", "ADVANCED",
         "Go语言-channel实现原理", "channel实现原理",
         ["Go", "channel", "CSP", "hchan", "select"],
         ["Channel Implementation", "hchan"],
         "Go Runtime source (src/runtime/chan.go); Go Blog: Share Memory By Communicating",
         [
             ("核心定义", "Go的channel基于CSP模型。底层数据结构hchan(runtime/chan.go)：buf=环形缓冲区，sendx/recvx=发送/接收指针，sendq/recvq=等待发送/接收的goroutine队列(FIFO)，lock=互斥锁保护。无缓冲channel(synchronous): buf为空，发送方阻塞直到接收方取走，接收方阻塞直到发送方提供值。有缓冲channel(asynchronous): buf有容量，仅当buf满时发送方阻塞，当buf空时接收方阻塞。"),
             ("Select实现", "select语句编译为runtime.selectgo调用：随机化case顺序(公平性保证)→遍历所有case检查就绪(channel有数据/可写入/closed/无default)→若有就绪case，随机选择一个执行→若无就绪case且有default，执行default→若无就绪且无default，将当前goroutine入队所有case的等待队列，阻塞。"),
             ("关闭与广播", "close(c)将hchan.closed置为1，立即唤醒recvq中所有G。向已关闭channel发送会panic。从已关闭channel接收：buf中已缓冲的数据可正常接收，读完后返回零值+ok=false。利用关闭的广播特性可实现通知所有等待者。"),
             ("关联知识点", "[[Go语言-GMP调度器与goroutine]] [[Go语言-接口与类型系统]]"),
         ]),
        ("内存管理", "INTERMEDIATE",
         "Go语言-内存管理与GC", "内存管理与GC",
         ["Go", "GC", "内存分配", "三色标记", "逃逸分析"],
         ["Go GC", "Tricolor Mark-and-Sweep", "Escape Analysis"],
         "Go Blog: A Guide to the Go Garbage Collector; Go Runtime src/runtime/mgc.go",
         [
             ("核心定义", "Go的GC采用并发三色标记清扫(Concurrent Tri-color Mark-Sweep)。三色抽象：白色(初始/未标记，可能回收)、灰色(已标记但其引用的对象未扫描)、黑色(已标记且引用的对象确定已找到)。GC过程：1.)STW写屏障启用+栈扫描 2.)并发标记(无STW) 3.)STW重扫描栈 4.)(可选STW终止) 5.)并发清扫。"),
             ("GC触发", "GC触发条件：1.)GOGC=100(默认): 堆增长到上次存活量的200%时触发GC 2.)目标CPU时间: runtime.GC强制触发 3.)2分钟定时触发(如果一直未GC)。Go 1.19+支持软内存限制GOMEMLIMIT(通过SetMemoryLimit API)，防止OOM。"),
             ("逃逸分析", "逃逸分析(escape analysis)决定对象分配在栈上还是堆。若编译器证明对象在函数返回后未被引用(未逃逸)，栈上分配(函数返回时自动释放，无GC开销)。反之则堆上分配。常见逃逸场景：1.)返回局部变量的指针 2.)将变量存入interface{} 3.)闭包捕获变量 4.)发送到channel。"),
             ("关联知识点", "[[Go语言-GMP调度器与goroutine]] [[Go语言-接口与类型系统]]"),
         ]),
    ],

    "Rust语言": [
        ("所有权", "ADVANCED",
         "Rust语言-所有权与生命周期", "所有权与生命周期",
         ["Rust", "所有权", "借用", "生命周期", "RAII", "Drop"],
         ["Ownership", "Borrowing", "Lifetimes", "RAII"],
         "The Rust Reference §4 Ownership; Rust Book (Brown University version) §4-10",
         [
             ("核心定义", "Rust的所有权系统通过三条核心规则在编译期消除内存错误：1.)每个值有唯一的所有者(owner) 2.)同一时刻只能有一个不可变引用&或一个可变引用&mut，两者不能共存 3.)引用必须总是有效的（生命周期约束）。RAII: 当所有者离开作用域，自动调用drop()释放资源。移动语义默认：赋值/传参会转移所有权(move)，原所有者不可再用。"),
             ("复制与克隆", "实现了Copy trait的类型(基本数值类型/不可变引用)赋值时自动按位复制而非移动。Clone trait提供显式深拷贝。Rc/Arc提供共享所有权（引用计数），Rc不是线程安全(非原子计数)，Arc是线程安全(原子计数)。"),
             ("生命周期标注", "生命周期参数'a不改变运行时行为，纯粹是编译器的静态分析工具。三条省略规则：1.)每个引用参数获得自己独立的生命周期 2.)如果只有一个输入生命周期参数，输出引用使用它 3.)如果方法有&self/&mut self，输出使用self的生命周期。违反生命周期时编译器给出精确错误和修复建议。"),
             ("关联知识点", "[[Rust语言-智能指针与内部可变性]] [[Rust语言-Trait系统与泛型]]"),
         ]),
        ("类型系统", "ADVANCED",
         "Rust语言-Trait系统与泛型", "Trait系统与泛型",
         ["Rust", "trait", "泛型", "静态分发", "动态分发", "关联类型"],
         ["Traits", "Generics", "Static Dispatch", "Dynamic Dispatch"],
         "The Rust Reference §10-11; Rust RFC 0195 (Associated Items)",
         [
             ("核心定义", "Rust的Trait定义了类型间共享的行为契约。类似Haskell的typeclass但更接近OOP接口的思想。trait约束：fn f<T: Trait1 + Trait2>(x: T)限制T必须实现这些trait。Blanket implementations：为满足条件的类型自动实现trait (impl<T: Display> ToString for T)。Orphan rule：实现trait时至少trait或类型之一必须在当前crate中定义，防止上游库冲突。"),
             ("静态分发 vs 动态分发", "静态分发(monomorphization): 编译器为每种具体类型生成特化代码，完全消除trait调用开销(类C++模板)。动态分发: trait object (dyn Trait)使用胖指针(数据指针+vtable指针)，调用通过vtable间接跳转。Sized默认约束：大多数泛型参数默认要求Sized。?Sized放宽约束允许DST(Dynamically Sized Types)。"),
             ("关联类型与GAT", "关联类型(type Item/type Output): 将trait的类型参数提升为类型成员，减少类型推导复杂度。GAT(Generic Associated Types, Rust 1.65+): 关联类型可以有自己的生命周期和类型参数，如trait LendingIterator { type Item<'a> where Self: 'a; ... }。"),
             ("关联知识点", "[[Rust语言-所有权与生命周期]] [[Rust语言-智能指针与内部可变性]]"),
         ]),
        ("智能指针", "INTERMEDIATE",
         "Rust语言-智能指针与内部可变性", "智能指针与内部可变性",
         ["Rust", "Box", "Rc", "Arc", "Cell", "RefCell", "Mutex"],
         ["Smart Pointers", "Interior Mutability", "RefCell"],
         "Rust Book §15 Smart Pointers; std::cell documentation",
         [
             ("核心定义", "智能指针(smart pointer)除管理底层数据外还有额外能力。Box<T>: 堆分配，单一所有者。Rc<T>: 单线程引用计数共享所有权(retain_count)。Arc<T>: 原子引用计数，线程安全但原子操作有开销。Weak<T>: 弱引用不增加强计数，防止循环引用。Deref trait: 重载*操作符使智能指针透明使用。Drop trait: 定义资源清理行为。"),
             ("内部可变性", "Rust的共享引用(&T)默认不可变。内部可变性允许多个共享引用仍然修改数据：Cell<T>: 通过get/set原子替换整个值(要求Copy或按值替换)。RefCell<T>: 运行期借用检查(borrow/borrow_mut返回Ref/RefMut)，违反借用规则时panic。Mutex<T>: 多线程互斥锁+内部可变性。RwLock<T>: 读写锁(多读者/单一写者)。"),
             ("引用循环", "Rc/Arc的循环引用导致内存泄漏(Rust不认为是UB)。解决方案：1.)Weak<T>打破循环，典型场景parent→child用Rc，child→parent用Weak 2.)Arena分配器批量释放 3.)drop bomb(#[deprecated])在测试中检测未释放的循环。"),
             ("关联知识点", "[[Rust语言-所有权与生命周期]] [[Rust语言-并发原语与async]]"),
         ]),
    ],
}

# Additional topics for Python, JS/TS, and supplements will follow the same pattern


def main():
    json_path = Path(__file__).with_name("wiki_topics.json")
    with open(json_path, "r", encoding="utf-8") as f:
        existing = json.load(f)

    before = len(existing)
    print(f"Existing topics: {before}")

    new_topics = []

    for course, topic_list in LANG_TOPICS.items():
        for chapter, difficulty, title, file_stem, tags, aliases, source, sections in topic_list:
            sections_json = [{"heading": h, "content": c} for h, c in sections]
            new_topics.append({
                "dir_name": course,
                "file_stem": file_stem,
                "title": title,
                "course": course,
                "chapter": chapter,
                "difficulty": difficulty,
                "tags": tags,
                "aliases": aliases,
                "source": source,
                "sections": sections_json,
            })

    existing.extend(new_topics)
    after = len(existing)
    print(f"New topics added: {after - before}")
    print(f"Total topics: {after}")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print("Written to wiki_topics.json")


if __name__ == "__main__":
    main()
