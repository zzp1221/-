"""
Append Go语言 deep topics, Rust语言 deep topics, C语言深入 additional topics,
Java深入 additional topics, and 65 supplemental CS course topics to wiki_topics.json.

Total new topics: 18 (Go) + 18 (Rust) + 20 (C) + 13 (Java) + 65 (supplement) = 134
"""
import json
from pathlib import Path

NEW_TOPICS = [
    # ═══════════════════════════════════════════════════════════════
    # Go语言 — 18 new topics (to reach 30 total)
    # ═══════════════════════════════════════════════════════════════
    {
        "dir_name": "Go语言",
        "file_stem": "接口与类型系统",
        "title": "Go语言-接口与类型系统",
        "course": "Go语言",
        "chapter": "类型系统",
        "difficulty": "ADVANCED",
        "tags": ["Go语言", "interface", "类型断言", "鸭子类型"],
        "aliases": ["Go Interfaces", "Type Assertions"],
        "source": "The Go Programming Language (Donovan & Kernighan) Ch 7; Go Spec: Interface types",
        "sections": [
            {"heading": "核心定义",
             "content": """""Go的接口是隐式满足的(implicit satisfaction)：类型只要实现了接口的所有方法就自动实现了该接口，无需显式声明。接口值在运行时由两个指针组成：(type, value)对，称为接口的动态类型和动态值。nil接口值意味着type和value均为nil; nil接口包含nil指针时接口本身不为nil,这是Go面试的经典陷阱。"""""},
            {"heading": "接口内部表示",
             "content": """""接口值的底层结构为iface(含方法)和eface(空接口interface{}): iface由itab指针(指向接口表,包含接口类型信息和方法表)和data指针组成; eface仅由_type和data组成。类型断言v.(T)和类型switch v.(type)在运行时检查itab中存储的实际类型。接口转换可能涉及内存分配。"""""},
            {"heading": "关键结论",
             "content": """""1. 接口值可比较,仅当动态类型和动态值都相等时才相等 2. 接口值不能与nil比较除非动态类型也为nil 3. 接受接口,返回结构体是Go设计的核心哲学 4. 接口污染(定义过多小接口)是常见的过度设计 5. io.Reader和io.Writer是Go中最著名的接口组合范例"""""},
            {"heading": "关联知识点",
             "content": """""[[Go语言-标准库io.Reader/Writer]] [[Go语言-错误处理哲学]] [[Go语言-泛型与类型约束]]"""""}
        ]
    },
    {
        "dir_name": "Go语言",
        "file_stem": "编译与链接过程",
        "title": "Go语言-编译与链接过程",
        "course": "Go语言",
        "chapter": "编译原理",
        "difficulty": "INTERMEDIATE",
        "tags": ["Go语言", "compiler", "SSA", "escape analysis", "linker"],
        "aliases": ["Go Compilation", "go build", "Go Toolchain"],
        "source": "Go官方文档 cmd/compile; Go Blog: Introduction to the Go compiler; Draven《Go语言底层原理剖析》",
        "sections": [
            {"heading": "核心定义",
             "content": """""Go编译器gc(Go compiler)的执行流程：1.)词法分析与语法解析生成AST 2.)类型检查(typecheck) 3.)AST转换为中间表示(Syntax→SSA) 4.)SSA优化passes(数十个pass,包括逃逸分析、内联、死代码消除) 5.)生成机器码。Go 1.7开始使用基于SSI(Static Single Information)形式的新后端。"""""},
            {"heading": "逃逸分析详解",
             "content": """""逃逸分析(escape analysis)是Go编译器最关键的优化之一：决定变量分配在栈(stack)还是堆(heap)。编译器分析每个变量在其生命周期内是否逃离了当前goroutine栈帧。参数-m参数可查看逃逸分析结果(go build -gcflags='-m')。常见逃逸情况：返回局部变量的指针、将变量赋值给接口类型、闭包引用的外部变量。"""""},
            {"heading": "关键结论",
             "content": """""1. 栈分配远比堆分配快——无GC负担，随栈帧自动回收 2. 逃逸分析在编译期完成，不影响运行时性能 3. 链接阶段执行死代码消除、函数去重(duff zero/copy、string interning)、重定位 4. Go默认使用内部链接器(internal linker),也可选用外部链接器(gold/lld)。"""""},
            {"heading": "关联知识点",
             "content": """""[[Go语言-unsafe与内存布局]] [[Go语言-Go运行时调度器GPM]] [[操作系统-链接与加载]]"""""}
        ]
    },
    {
        "dir_name": "Go语言",
        "file_stem": "Context与取消传播",
        "title": "Go语言-Context与取消传播",
        "course": "Go语言",
        "chapter": "并发编程",
        "difficulty": "INTERMEDIATE",
        "tags": ["Go语言", "context", "取消传播", "超时控制", "并发"],
        "aliases": ["Go Context", "Cancellation Propagation"],
        "source": "Go官方博客: Go Concurrency Patterns: Context; Go标准库context包文档",
        "sections": [
            {"heading": "核心定义",
             "content": """""context.Context是Go中跨goroutine传递请求范围值的机制。核心类型：context.Background()(根context), context.TODO()(占位), context.WithCancel(可取消), context.WithDeadline/WithTimeout(超时), context.WithValue(值传递)。Context形成树结构：父context取消时自动取消所有子context。"""""},
            {"heading": "取消传播机制",
             "content": """""context.Done()返回只读channel，当context被取消时该channel关闭，所有监听它的goroutine收到广播信号。内部实现使用propagateCancel父子链：父取消时遍历所有child canceler并依次调用cancel。WithDeadline内部使用timer实现自动取消。Context的Err()方法返回取消原因(context.Canceled或context.DeadlineExceeded)。"""""},
            {"heading": "关键结论",
             "content": """""1. Context应作为函数的第一个参数(context.Context, error模式) 2. 不要将Context存储在struct字段中(除了少数基础设施代码) 3. WithValue仅用于传递请求范围的元数据(trace ID、user id)，不用于传递业务参数 4. 永远不要用nil传递context，应使用context.TODO()"""""},
            {"heading": "关联知识点",
             "content": """""[[Go语言-Goroutine与通道]] [[Go语言-sync包深入]] [[分布式系统-分布式追踪]]"""""}
        ]
    },
    {
        "dir_name": "Go语言",
        "file_stem": "sync包深入",
        "title": "Go语言-sync包深入",
        "course": "Go语言",
        "chapter": "并发编程",
        "difficulty": "ADVANCED",
        "tags": ["Go语言", "sync", "Mutex", "WaitGroup", "atomic"],
        "aliases": ["Go sync package", "sync.Mutex", "sync/atomic"],
        "source": "Go标准库sync包文档; Go Blog: Go 1.18 sync additions; Go Memory Model",
        "sections": [
            {"heading": "核心定义",
             "content": """""sync包提供基本同步原语。sync.Mutex(互斥锁)：Lock()阻塞直到获取锁,Unlock()释放。sync.RWMutex(读写锁)：RLock/RUnlock允许并发读,Lock()写锁排斥所有读锁和写锁。sync.WaitGroup：Add(1)增计数,Done()减计数,Wait()阻塞直到计数归零。sync.Once：确保函数只执行一次,基于原子操作实现。sync.Cond：条件变量,Wait()释放锁并等待Signal/Broadcast。"""""},
            {"heading": "sync/atomic详解",
             "content": """""sync/atomic提供硬件级别的原子操作：AddInt64/AddUint64(原子加),LoadInt64(原子读),StoreInt64(原子写),CompareAndSwapInt64(CAS),SwapInt64(原子交换)。Go 1.19新增atomic.Int64等类型安全包装。原子操作不用锁，性能极高(~1ns级别)，但不能替代互斥锁用于保护多个变量的不变式。atomic.Value提供任意类型的原子存储与加载。"""""},
            {"heading": "关键结论",
             "content": """""1. Mutex零值即可用 2. 不可复制Mutex(go vet检测) 3. WaitGroup的Add必须在goroutine外调用 4. atomic不能替代channel进行goroutine同步 5. Go 1.18的sync.Map优化了高并发读多写少场景"""""},
            {"heading": "关联知识点",
             "content": """""[[Go语言-Goroutine与通道]] [[Go语言-Context与取消传播]] [[操作系统-同步与死锁]]"""""}
        ]
    },
    {
        "dir_name": "Go语言",
        "file_stem": "unsafe与内存布局",
        "title": "Go语言-unsafe与内存布局",
        "course": "Go语言",
        "chapter": "系统编程",
        "difficulty": "ADVANCED",
        "tags": ["Go语言", "unsafe", "内存布局", "指针", "cgo"],
        "aliases": ["Go unsafe", "Memory Layout", "unsafe.Pointer"],
        "source": "Go官方文档 unsafe包; Go Spec: unsafe.Pointer; Go Blog: unsafe.Pointer rules",
        "sections": [
            {"heading": "核心定义",
             "content": """""unsafe.Pointer是通用指针类型，可与其他任意指针类型互转(类似于C的void*)。unsafe.Sizeof(x)返回变量x占用的字节数(不含其引用数据),unsafe.Offsetof(f)返回结构体字段f距结构体开头的偏移量,unsafe.Alignof(x)返回对齐要求。unsafe.Pointer的四条合法规则：T1→unsafe.Pointer→T2转换(仅T1和T2内存布局兼容时安全)；unsafe.Pointer→uintptr(用于打印/调试)。"""""},
            {"heading": "内存布局详解",
             "content": """""Go结构体内存布局遵循对齐规则：每个字段的偏移量必须是其对齐大小的倍数，结构体整体大小必须是最大对齐的倍数。空struct{}大小为0(zero-width type)，常作为map的value用于实现set(map[T]struct{})。slice、string、interface、map、channel的底层结构都是header+pointer组合。unsafe.Sizeof(string)在64位系统为16字节(data ptr + len)。"""""},
            {"heading": "关键结论",
             "content": """""1. uintptr不被GC追踪——保存uintptr期间若原对象不再被引用可能导致悬挂指针 2. 严禁对Go托管内存进行指针算术 3. cgo调用会将Go指针传给C需要特殊处理(Go 1.6引入的cgocheck机制) 4. reflect.SliceHeader/StringHeader是unsafe的reflect版等价物"""""},
            {"heading": "关联知识点",
             "content": """""[[Go语言-Slice内部实现]] [[Go语言-String与[]byte转换]] [[Go语言-cgo与FFI]]"""""}
        ]
    },
    {
        "dir_name": "Go语言",
        "file_stem": "reflect与类型反射",
        "title": "Go语言-reflect与类型反射",
        "course": "Go语言",
        "chapter": "元编程",
        "difficulty": "INTERMEDIATE",
        "tags": ["Go语言", "reflect", "反射", "struct tags", "元编程"],
        "aliases": ["Go Reflection", "reflect.Type", "reflect.Value"],
        "source": "Go官方文档 reflect包; Go Blog: The Laws of Reflection; Effective Go",
        "sections": [
            {"heading": "核心定义",
             "content": """""reflect包提供运行时类型检查(reflection)。reflect.Type(接口)表示Go类型的元信息，通过reflect.TypeOf(x)获取。reflect.Value表示值的运行时表示，可获取、设置、调用。reflect.Type和reflect.Value都区分Kind(基础类别int/struct/ptr/...)和具体类型名。reflect.Indirect(v)获取指针指向的值，reflect.New(typ)分配新零值并返回指针。"""""},
            {"heading": "Struct Tag与JSON映射",
             "content": """""Go的结构体标签(struct tags)通过reflect.StructTag获取。标签格式：`key1:\"value1\" key2:\"value2\"`。encoding/json、gorm等库通过反射读取标签实现序列化映射、ORM映射。Tag.Get(key)按key查找值。反射的基本定律：1. 从接口值可得反射对象 2. 从反射对象可得接口值 3. 要修改反射对象其值必须可设置(Settable)。"""""},
            {"heading": "关键结论",
             "content": """""1. 反射比直接访问慢10~100倍 2. 反射代码更脆弱，编译期检查丧失 3. Value.IsValid()/IsZero()需要先检查 4. 调用Call时方法签名必须完全匹配 5. 大量使用reflect的代码应抽象为代码生成工具替代 6. 不要对未导出的字段进行Set操作——会panic"""""},
            {"heading": "关联知识点",
             "content": """""[[Go语言-接口与类型系统]] [[Go语言-泛型与类型约束]] [[Java深入-反射与动态代理]]"""""}
        ]
    },
    {
        "dir_name": "Go语言",
        "file_stem": "测试与基准测试",
        "title": "Go语言-测试与基准测试",
        "course": "Go语言",
        "chapter": "工程质量",
        "difficulty": "BASIC",
        "tags": ["Go语言", "testing", "benchmark", "表驱动测试", "test"],
        "aliases": ["Go Testing", "Benchmark", "Table-Driven Tests"],
        "source": "Go官方文档 testing包; Go Blog: TableDrivenTests; Effective Go",
        "sections": [
            {"heading": "核心定义",
             "content": """""Go的测试框架内置于testing包。测试函数签名：func TestXxx(t *testing.T)。运行命令：go test ./...。基准测试函数签名：func BenchmarkXxx(b *testing.B),运行方式go test -bench=.。表驱动测试(table-driven tests)是Go社区的标准风格：创建[]struct{name, input, want}切片，循环调用t.Run执行子测试。go test -run=REGEX可筛选特定测试。"""""},
            {"heading": "表驱动测试范式",
             "content": """""表驱动测试将测试用例数据与测试逻辑分离：tests := []struct{name string; input Type; want Type}{{...},{...}}; for _, tt := range tests { t.Run(tt.name, func(t *testing.T) { got := Func(tt.input); if got != tt.want { t.Errorf('...') } })}。每个子测试独立运行，支持-parallel并行。t.Cleanup可以注册清理函数。"""""},
            {"heading": "关键结论",
             "content": """""1. 测试文件以_test.go结尾 2. 基准测试需要ResetTimer排除准备时间 3. TestMain(m *testing.M)可做全局设置/清理 4. golden file测试常用于复杂输出 5. 覆盖率profile: go test -coverprofile=coverage.out 6. 竞态检测: go test -race"""""},
            {"heading": "关联知识点",
             "content": """""[[Go语言-错误处理哲学]] [[软件工程-软件测试策略]] [[Go语言-Go运行时调度器GPM]]"""""}
        ]
    },
    {
        "dir_name": "Go语言",
        "file_stem": "网络编程net-http",
        "title": "Go语言-网络编程net/http",
        "course": "Go语言",
        "chapter": "网络编程",
        "difficulty": "INTERMEDIATE",
        "tags": ["Go语言", "net/http", "HTTP/2", "中间件", "ServeMux"],
        "aliases": ["Go HTTP", "net/http", "Middleware"],
        "source": "Go标准库net/http文档; RFC 7540 (HTTP/2); Go Blog: HTTP/2 in Go",
        "sections": [
            {"heading": "核心定义",
             "content": """""Go的net/http包提供生产级HTTP客户端和服务器实现。Server结构体包含Handler字段(接口,含ServeHTTP方法)。DefaultServeMux是全局路由,可通过http.HandleFunc注册。http.HandlerFunc(f)将普通函数适配为Handler。http.ListenAndServe(':8080', nil)使用DefaultServeMux启动服务器。http.Transport管理连接池和HTTP/2多路复用。"""""},
            {"heading": "中间件模式",
             "content": """""Go的HTTP中间件通过Handler包装实现：func middleware(next http.Handler) http.Handler。常见模式：logMiddleware→authMiddleware→rateLimitMiddleware→actualHandler。http.TimeoutHandler包装超时控制。第三方库如chi/gorilla/mux提供更灵活的路由。http/httputil.ReverseProxy提供反向代理能力。Go 1.22的新ServeMux支持方法路由和方法变量。"""""},
            {"heading": "关键结论",
             "content": """""1. 默认HTTP服务器不支持优雅关闭——需shutdown context 2. http.Client不设置Timeout可能导致goroutine泄漏 3. Response.Body必须关闭 4. 生产环境建议使用http.Server结构体而非http.ListenAndServe快捷函数"""""},
            {"heading": "关联知识点",
             "content": """""[[Go语言-Context与取消传播]] [[计算机网络-HTTP协议与HTTPS]] [[Go语言-错误处理哲学]]"""""}
        ]
    },
    {
        "dir_name": "Go语言",
        "file_stem": "错误处理哲学",
        "title": "Go语言-错误处理哲学",
        "course": "Go语言",
        "chapter": "语言设计",
        "difficulty": "BASIC",
        "tags": ["Go语言", "error", "panic", "defer", "错误处理"],
        "aliases": ["Go Error Handling", "errors.Is", "errors.As"],
        "source": "Go官方文档 errors包; Go Blog: Error handling and Go; Effective Go",
        "sections": [
            {"heading": "核心定义",
             "content": """""Go使用显式错误返回而非异常。error是内建接口：type error interface { Error() string }。函数通常返回(value, error)元组。Go 1.13引入错误包装：fmt.Errorf('%w', err)将原始err包装，errors.Is(err, target)沿错误链检查类型，errors.As(err, &target)沿错误链提取特定类型。errors.Unwrap()返回被包装的错误。"""""},
            {"heading": "panic与recover",
             "content": """""panic用于不可恢复的严重错误(空指针、数组越界)。recover只能在defer函数中调用，捕获panic并返回panic参数。规范：库函数不应panic(应返回error)，只有在初始化阶段的不可恢复错误才允许panic。recover后重新panic需保留原始调用栈。并发panic只影响当前goroutine，会导致整个进程崩溃。"""""},
            {"heading": "关键结论",
             "content": """""1. 不要忽略错误返回值——使用vet检查 2. 区分sentinel errors(errors.New常量)和自定义错误类型 3. 避免重复包装同一个错误(产生重复信息) 4. panic不是其他语言的异常——不要用于常规流控制 5. errors.Join(Go1.20)可合并多个错误"""""},
            {"heading": "关联知识点",
             "content": """""[[Go语言-defer与调用栈]] [[Go语言-接口与类型系统]] [[Go语言-测试与基准测试]]"""""}
        ]
    },
    {
        "dir_name": "Go语言",
        "file_stem": "Module与依赖管理",
        "title": "Go语言-Module与依赖管理",
        "course": "Go语言",
        "chapter": "工程构建",
        "difficulty": "BASIC",
        "tags": ["Go语言", "go.mod", "modules", "依赖管理", "GOPROXY"],
        "aliases": ["Go Modules", "Semantic Import Versioning", "GOPROXY"],
        "source": "Go官方文档 Modules; Go Blog: Using Go Modules; Go Wiki: Modules",
        "sections": [
            {"heading": "核心定义",
             "content": """""Go Modules是Go 1.11引入的依赖管理系统(Go 1.16后默认启用)。模块由go.mod文件定义：module声明模块路径,go声明Go版本,require列出直接依赖,replace(gomod补丁),exclude(排除版本)。语义化导入版本(semantic import versioning)：大版本号>=2时路径必须包含/vN后缀(github.com/foo/bar/v2)。"""""},
            {"heading": "最小版本选择MVS",
             "content": """""Go使用最小版本选择(Minimal Version Selection, MVS)而非SAT求解器。MVS规则：选择所有require中出现的最低符合版本。当存在多个依赖不同版本时，选择最高者(保守升版)。go.sum文件保存所有依赖内容的哈希值确保可重现构建。GOPROXY(如goproxy.cn)缓存模块下载加速。GONOSUMDB跳过私有模块校验。"""""},
            {"heading": "关键结论",
             "content": """""1. go mod tidy清理未使用的依赖并添加缺失的 2. go mod vendor创建vendor目录做离线构建 3. semantic import versioning >v2时必须更改import路径 4. 使用replace指令替代fork 5. go clean -modcache清理mod缓存"""""},
            {"heading": "关联知识点",
             "content": """""[[Go语言-编译与链接过程]] [[软件工程-版本控制与Git]] [[Rust语言-cargo与依赖管理]]"""""}
        ]
    },
    {
        "dir_name": "Go语言",
        "file_stem": "cgo与FFI",
        "title": "Go语言-cgo与FFI",
        "course": "Go语言",
        "chapter": "系统编程",
        "difficulty": "ADVANCED",
        "tags": ["Go语言", "cgo", "FFI", "CGO_ENABLED", "外部函数接口"],
        "aliases": ["Go cgo", "Foreign Function Interface", "CGo"],
        "source": "Go官方文档 cmd/cgo; Go Blog: C? Go? Cgo!; Go Wiki: cgo",
        "sections": [
            {"heading": "核心定义",
             "content": """""cgo是Go的C语言互操作机制。通过在Go文件顶部import 'C'(必须紧随特殊注释块中的C代码)，可以在Go中调用C函数和使用C类型。CGo将Go+C代码分开编译处理：Go编译为Go目标文件，C编译为C目标文件，最后链接。调用C函数有明显开销：每调用约40ns vs 直接Go调用~1ns(goroutine切换和栈切换)。"""""},
            {"heading": "内存管理与性能",
             "content": """""cgo调用不可在goroutine间任意迁移(锁定OS线程)。C.malloc分配的内存不受Go GC管理，必须用C.free手动释放。C.CString将Go字符串复制到C堆(需手动free)。Go 1.6+的指针传递规则：不能将Go指针(含引用的Go内存)存储到C内存中超过一次调用(cgocheck检测)。大量cgo调用可设置runtime.LockOSThread()绑定goroutine到特定OS线程。"""""},
            {"heading": "关键结论",
             "content": """""1. cgo是工具不是包——CGO_ENABLED=0可禁用 2. CGo不是Go对象链接格式，导致编译慢、交叉编译困难 3. 考虑用纯Go替代方案(golang.org/x/sys替代cgo syscall) 4. 批量cgo调用可减少开销 5. CGo代码通常性能显著低于纯Go实现"""""},
            {"heading": "关联知识点",
             "content": """""[[Go语言-unsafe与内存布局]] [[C语言深入-链接器与ABI详解]] [[Rust语言-FFI与unsafe Rust]]"""""}
        ]
    },
    {
        "dir_name": "Go语言",
        "file_stem": "泛型与类型约束",
        "title": "Go语言-泛型与类型约束",
        "course": "Go语言",
        "chapter": "类型系统",
        "difficulty": "ADVANCED",
        "tags": ["Go语言", "generics", "type parameters", "constraints", "Go 1.18"],
        "aliases": ["Go Generics", "Type Parameters", "Type Constraints"],
        "source": "Go Spec: Type Parameters; Go Blog: An Introduction to Generics; Type Parameters Proposal",
        "sections": [
            {"heading": "核心定义",
             "content": """""Go 1.18引入类型参数(type parameters)支持泛型编程。语法：func F[T any](x T) T。类型约束通过接口定义：interface{ ~int|~float64 }表示底层类型为int或float64。constraints包(已废弃,现移至标准库预声明标识符)定义了Ordered(可排序)、Signed、Unsigned等内置约束。泛型函数参数和返回值类型由编译器推断，调用时可选显式指定F[int](x)。"""""},
            {"heading": "类型约束设计",
             "content": """""约束接口可以包含类型项(type term)——通过~T或T|U语法定义允许的类型集合。any约束(=interface{})接受所有类型。comparable约束允许==和!=比较。泛型类型(如type Stack[T any] struct{data []T})必须为每个类型参数实例化：Go采用GCShape stenciling实现——相同底层布局的类型共享代码以减少代码膨胀。这与C++模板的monomorphization不同。"""""},
            {"heading": "关键结论",
             "content": """""1. Go泛型不支持运算符重载——通过约束接口+方法实现 2. 约束接口中不能使用类型声明为方法的方法 3. 泛型代码可读性优先于性能 4. 类型推断从参数类型推导类型参数 5. 泛型函数的类型不能在运行时通过反射获取(GCShape丢失信息)"""""},
            {"heading": "关联知识点",
             "content": """""[[Go语言-接口与类型系统]] [[Go语言-reflect与类型反射]] [[Java深入-泛型擦除与类型安全]]"""""}
        ]
    },
    {
        "dir_name": "Go语言",
        "file_stem": "Slice内部实现",
        "title": "Go语言-Slice内部实现",
        "course": "Go语言",
        "chapter": "数据结构",
        "difficulty": "INTERMEDIATE",
        "tags": ["Go语言", "slice", "内存管理", "append", "slice header"],
        "aliases": ["Go Slice Internals", "Slice Header", "Append Mechanics"],
        "source": "Go Blog: Go Slices: usage and internals; Go runtime源码 slice.go; Effective Go",
        "sections": [
            {"heading": "核心定义",
             "content": """""Go的Slice是动态数组的抽象，底层由3字段的header结构表示：type slice struct { array unsafe.Pointer; len int; cap int }。Slice不拥有底层数组(底层数组可能被多个slice共享)。make([]T, len, cap)创建一个新切片和底层数组。切片操作s[i:j]截取底层数组的一段，新slice与原slice共享同一底层数组。len=s[j]-s[i], cap=从i到原切片末尾。"""""},
            {"heading": "Append扩容机制",
             "content": """""append(s, x...)向slice追加元素。如果cap足够则直接在底层数组后添加(原地); cap不足时分配新底层数组(通常翻倍扩容)，复制原数据，添加新元素。Go 1.18后扩容策略更平滑：小于256时翻倍，大于256时以(1.63-2.0)之间逐步过渡。扩容后原slice的底层数组不变(可能成为垃圾)，新slice指向新数组。append始终返回新header值(即使原地也可能改变len)。"""""},
            {"heading": "关键结论",
             "content": """""1. 函数传递slice只复制header(24字节),修改元素影响原slice 2. append可能导致底层数组分离——不要同时依赖新旧slice 3. 多slice共享底层数组时修改需小心 4. copy()可避免共享底层数组 5. full slice expression s[a:b:c]控制cap"""""},
            {"heading": "关联知识点",
             "content": """""[[Go语言-Map内部实现]] [[Go语言-String与[]byte转换]] [[Go语言-unsafe与内存布局]]"""""}
        ]
    },
    {
        "dir_name": "Go语言",
        "file_stem": "Map内部实现",
        "title": "Go语言-Map内部实现",
        "course": "Go语言",
        "chapter": "数据结构",
        "difficulty": "INTERMEDIATE",
        "tags": ["Go语言", "map", "hmap", "哈希表", "bucket"],
        "aliases": ["Go Map Internals", "hmap", "Hash Map"],
        "source": "Go runtime源码 map.go; Go Blog: Go maps in action; Effective Go",
        "sections": [
            {"heading": "核心定义",
             "content": """""Go map是基于哈希表的关联容器。底层结构hmap包含：count(元素数量)、B(桶数量的log_2, 共2^B个桶)、buckets(桶数组指针)、hash0(哈希种子,每次运行随机生成防止hash DoS攻击)。桶(bucket)存储8个键值对(top hash+key+value)，通过overflow指针链接溢出桶。超过6.5的平均负载因子(load factor)触发扩容。"""""},
            {"heading": "哈希冲突与扩容",
             "content": """""Go使用链表法(separate chaining)解决哈希冲突：每个桶的8个位置满后创建overflow bucket并链接。扩容分两阶段：1. 增量扩容(gradual grow):翻倍B,数据逐步从旧桶迁移到新桶(每次mapassign/mapaccess迁移1-2个桶) 2. 等量扩容(same-size grow):溢出桶过多时清理(不翻倍,重新哈希分布)。hash seed随机化每进程不同防止DoS。"""""},
            {"heading": "关键结论",
             "content": """""1. map不是并发安全的——并发读写会panic(通过race检测) 2. 遍历顺序随机化(mapiterinit的随机start offset) 3. map的key必须可比较(==),slice/map/function不行 4. 删除不缩容——map只能增长,delete只标记删除 5. nil map可以读但不能写"""""},
            {"heading": "关联知识点",
             "content": """""[[Go语言-Slice内部实现]] [[Go语言-sync包深入]] [[数据结构-哈希表]]"""""}
        ]
    },
    {
        "dir_name": "Go语言",
        "file_stem": "String与byte转换",
        "title": "Go语言-String与[]byte转换",
        "course": "Go语言",
        "chapter": "数据结构",
        "difficulty": "INTERMEDIATE",
        "tags": ["Go语言", "string", "[]byte", "零拷贝", "StringHeader"],
        "aliases": ["Go String Interning", "Zero-Copy Conversion", "StringHeader"],
        "source": "Go runtime源码 string.go; Go Blog: Strings, bytes, runes and characters in Go",
        "sections": [
            {"heading": "核心定义",
             "content": """""Go字符串是不可变(immutable)的UTF-8编码字节序列。底层结构reflect.StringHeader(与slice header类似)：Data指针+Len长度。string与[]byte转换通常涉及内存拷贝：string([]byte)分配新内存并拷贝，[]byte(string)同样拷贝。原因：string不可变而[]byte可变，共享底层内存将破坏字符串的不变性保证。"""""},
            {"heading": "零拷贝技巧",
             "content": """""在高性能场景中可通过unsafe零拷贝转换(但危险且非法——违反Go内存模型)：*(*string)(unsafe.Pointer(&bs))。strings.Builder是构建字符串的高效方式(内部使用[]byte积累，最后ToString零拷贝返回)。字符串比较：字面量相同的字符串在编译期可能内化(interning)，运行时不自动内化。for range遍历string产生rune(Unicode code point)而非byte。"""""},
            {"heading": "关键结论",
             "content": """""1. 标准转换因不可变性保证而必须拷贝——这是设计决定 2. 使用strings.Builder而非+=拼接(避免O(n²)) 3. string切片操作O(1)返回新string(共享底层) 4. string索引返回byte不是rune(中文一个字符3字节) 5. len(s)返回字节数, utf8.RuneCountInString(s)返回字符数"""""},
            {"heading": "关联知识点",
             "content": """""[[Go语言-Slice内部实现]] [[Go语言-unsafe与内存布局]] [[Rust语言-字符串与str/String]]"""""}
        ]
    },
    {
        "dir_name": "Go语言",
        "file_stem": "defer与调用栈",
        "title": "Go语言-defer与调用栈",
        "course": "Go语言",
        "chapter": "语言设计",
        "difficulty": "BASIC",
        "tags": ["Go语言", "defer", "调用栈", "资源管理", "恐慌恢复"],
        "aliases": ["Go Defer", "Call Stack", "Resource Management"],
        "source": "Go官方文档 defer; Go Blog: Defer, Panic, and Recover; Effective Go",
        "sections": [
            {"heading": "核心定义",
             "content": """""defer将函数调用推迟到包含它的函数返回之前执行。参数在defer语句处求值(非调用时)。多个defer遵循LIFO(后进先出)顺序——像一个栈。defer常用于资源释放(关闭文件、释放锁、关闭连接)和panic恢复。在Go 1.14前defer有一定开销(约35ns)，Go 1.14引入开放编码defer(open-coded defer)将性能提升到约6ns(接近直接调用的成本)。"""""},
            {"heading": "defer陷阱与最佳实践",
             "content": """""1. 循环中的defer会累积(使用闭包或提取函数避免) 2. 命名返回值中defer可以修改返回值 3. defer f.Close()时忽略了Close的错误返回(应包装处理) 4. defer func(){...}()参数在defer处求值，闭包捕获的是外部变量的最新值 5. Go 1.18+的defer在函数中不会创建新的defer frame，性能开销更低"""""},
            {"heading": "关联知识点",
             "content": """""[[Go语言-错误处理哲学]] [[Go语言-Go运行时调度器GPM]] [[C语言深入-指针算术与内存模型]]"""""}
        ]
    },
    {
        "dir_name": "Go语言",
        "file_stem": "io-Reader-Writer",
        "title": "Go语言-标准库io.Reader/Writer",
        "course": "Go语言",
        "chapter": "标准库",
        "difficulty": "BASIC",
        "tags": ["Go语言", "io.Reader", "io.Writer", "组合", "标准库"],
        "aliases": ["Go io.Reader", "io.Writer", "Composability"],
        "source": "Go标准库io包文档; Go Blog: io.Reader in depth; Effective Go",
        "sections": [
            {"heading": "核心定义",
             "content": """""Go的标准IO抽象围绕两个最小接口：type Reader interface { Read(p []byte) (n int, err error) } 和 type Writer interface { Write(p []byte) (n int, err error) }。这两个单一方法接口构成了Go生态的核心协议——一切数据源(Object Storage、HTTP Body、File)实现Reader,一切数据接收方实现Writer。Read的约定：n可能小于len(p), err==io.EOF表示结束。"""""},
            {"heading": "组合式IO设计",
             "content": """""通过接口组合构建强大的抽象层：io.MultiReader串联多个Reader；io.TeeReader同时读取并写入(类似Unix tee)；io.LimitReader限制读取字节数；io.Pipe()创建内存管道(io.PipeReader/io.PipeWriter)；io.Copy/io.CopyBuffer高效地从Reader到Writer传输(使用32KB默认缓冲区,内部调用ReadFrom/WriteTo优化)；bufio包提供带缓冲区的Reader/Writer。"""""},
            {"heading": "关键结论",
             "content": """""1. 永远检查n>0——即使返回error也可能有部分数据 2. io.ReadAll替代ioutil.ReadAll(Go 1.16+) 3. io.NopCloser将Reader包装为ReadCloser 4. 实现Reader时通过io.Copy和bufio自动获得缓冲和优化 5. 接口组合而非继承是Go设计的核心范式"""""},
            {"heading": "关联知识点",
             "content": """""[[Go语言-接口与类型系统]] [[Go语言-网络编程net/http]] [[Go语言-Context与取消传播]]"""""}
        ]
    },
    {
        "dir_name": "Go语言",
        "file_stem": "netpoll与网络模型",
        "title": "Go语言-netpoll与网络模型",
        "course": "Go语言",
        "chapter": "运行时",
        "difficulty": "ADVANCED",
        "tags": ["Go语言", "netpoll", "epoll", "网络模型", "异步IO"],
        "aliases": ["Go Netpoll", "Epoll Integration", "Goroutine Network Model"],
        "source": "Go runtime源码 netpoll.go/netpoll_epoll.go; Go Blog: Go's work-stealing scheduler; Draven《Go并发编程实战》",
        "sections": [
            {"heading": "核心定义",
             "content": """""Go的网络IO模型基于netpoll——一个对操作系统多路复用机制(epoll/kqueue/IOCP)的封装。netpoll将非阻塞IO与goroutine调度集成：当goroutine在socket上读写阻塞时，runtime将其挂起，将文件描述符注册到netpoller，goroutine让出P(逻辑处理器)。IO就绪后netpoller将该goroutine标记为可运行并放回运行队列。"""""},
            {"heading": "netpoll与调度器集成",
             "content": """""netpoll的核心优势是goroutine级别的阻塞而非线程级别——一个OS线程可以运行数千个goroutine,当一个goroutine阻塞在网络IO上,线程可以立即切换到其他goroutine。关键函数：runtime.netpoll(轮询就绪fd), runtime.netpollblock(挂起当前g直到IO就绪)。Goroutine阻塞在IO时不消耗CPU。findrunnable()在寻找可运行goroutine时会调用netpoll检查就绪的IO。"""""},
            {"heading": "关键结论",
             "content": """""1. Go的goroutine IO模型提供同步编程的简单性和异步IO的性能 2. netpoller是Go高并发网络服务的核心基础 3. 文件IO(O_DIRECT以外)不走netpoller——文件阻塞会占用OS线程 4. net.Dialer的Timeout/Deadline设置通过timer+netpoll实现 5. Go HTTP服务器的并发处理能力(百万连接级别)依赖netpoller"""""},
            {"heading": "关联知识点",
             "content": """""[[Go语言-Go运行时调度器GPM]] [[Go语言-网络编程net/http]] [[计算机网络-epoll与I/O多路复用]]"""""}
        ]
    },

    # ═══════════════════════════════════════════════════════════════
    # Rust语言 — 18 new topics (to reach 30 total)
    # ═══════════════════════════════════════════════════════════════
    {
        "dir_name": "Rust语言",
        "file_stem": "async-await与Future",
        "title": "Rust语言-async/await与Future",
        "course": "Rust语言",
        "chapter": "异步编程",
        "difficulty": "ADVANCED",
        "tags": ["Rust", "async", "await", "Future", "Pin", "Executor"],
        "aliases": ["Rust Async", "Future Trait", "Pin/Unpin"],
        "source": "Rust Async Book; Rust Reference: async/await; Tokio官方文档; RFC 2394",
        "sections": [
            {"heading": "核心定义",
             "content": """""Rust的async/await提供零成本异步编程：async关键字将函数/代码块转换为实现Future trait的匿名状态机。Future trait核心：fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>。async fn在被.await调用前不执行任何代码。编译器将async块转换为枚举(每个await点对应一个variant)，状态在poll调用间保持。"""""},
            {"heading": "Pin与自引用结构",
             "content": """""Pin<&mut T>保证被固定的值不会在内存中移动。async生成的状态机是自引用(self-referential)结构——一个字段是另一个字段的引用(等待的future被当前状态机持有引用)。Pin阻止move破坏这些引用。Unpin auto trait标记类型在Pin后仍可安全移动。!Unpin类型的Pin<&mut T>无法获取&mut T(除非通过unsafe)。Pin::new_unchecked和Pin::as_mut提供安全封装。"""""},
            {"heading": "关键结论",
             "content": """""1. async fn返回impl Future——名称是不能直接被引用的不透明类型 2. 没有executor时Future什么也不做(需要tokio/async-std轮询) 3. .await让出当前任务给executor 4. Send trait决定Future是否能跨线程移动 5. async move block获得所有权的变量而非引用"""""},
            {"heading": "关联知识点",
             "content": """""[[Rust语言-所有权与借用]] [[Rust语言-并发原语与Send/Sync]] [[Rust语言-闭包与Fn特征]]"""""}
        ]
    },
    {
        "dir_name": "Rust语言",
        "file_stem": "并发原语与Send-Sync",
        "title": "Rust语言-并发原语与Send/Sync",
        "course": "Rust语言",
        "chapter": "并发编程",
        "difficulty": "ADVANCED",
        "tags": ["Rust", "Send", "Sync", "Arc", "Mutex", "Channel", "并发"],
        "aliases": ["Send/Sync Auto Traits", "Arc<Mutex<T>>", "Rust Channels"],
        "source": "The Rustonomicon: Send and Sync; Rust Reference: Send/Sync; Mara Bos《Rust Atomics and Locks》",
        "sections": [
            {"heading": "核心定义",
             "content": """""Send和Sync是Rust并发安全的两大auto trait。Send：类型值的所有权可以安全转移到另一个线程(几乎所有类型都Send,除了Rc/RefCell/裸指针)。Sync：类型的共享引用&T可以在多个线程间安全共享(当&T: Send时T: Sync)。Mutex<T>让T: Send成为Mutex<T>: Send+Sync(提供了内部同步)。Arc<T>: Send+Sync当T: Send+Sync。这实现了编译期数据竞争消除。"""""},
            {"heading": "Arc与Mutex实战",
             "content": """""Arc<Mutex<T>>是Rust并发中最常见的共享可变状态模式：Arc提供共享所有权+引用计数,Mutex提供内部可变性和互斥访问。Mutex::lock()返回LockResult<MutexGuard<T>>,MutexGuard实现了Deref/DerefMut和Drop(自动解锁)。std::sync::mpsc提供多生产者单消费者通道——Sender可克隆(多线程发送),Receiver只能由一个线程接收。crossbeam提供的MPMC通道性能更优。"""""},
            {"heading": "关键结论",
             "content": """""1. Send/Sync是unsafe auto trait——标准库类型为它们提供安全抽象 2. 手动实现Send/Sync需要unsafe impl 3. 编译器自动为composite type推导Send/Sync 4. Poisoning：持有Mutex的线程panic时Mutex被毒化(poisoned) 5. Barrier/RwLock/Condvar使用频率更低但有特定场景"""""},
            {"heading": "关联知识点",
             "content": """""[[Rust语言-所有权与借用]] [[Rust语言-async/await与Future]] [[操作系统-同步与死锁]]"""""}
        ]
    },
    {
        "dir_name": "Rust语言",
        "file_stem": "模式匹配与枚举",
        "title": "Rust语言-模式匹配与枚举",
        "course": "Rust语言",
        "chapter": "语言设计",
        "difficulty": "INTERMEDIATE",
        "tags": ["Rust", "match", "enum", "if let", "模式匹配"],
        "aliases": ["Rust Pattern Matching", "Match Expression", "Algebraic Data Types"],
        "source": "The Rust Book Ch 6 & 18; Rust Reference: Match expressions; Rust by Example",
        "sections": [
            {"heading": "核心定义",
             "content": """""Rust的模式匹配系统基于代数数据类型(ADT)：enum可以携带数据(将类型加法与类型乘法统一)。match表达式是Rust最强大的控制流结构：编译器验证穷举性(exhaustiveness)——所有可能的variant必须被覆盖，否则编译错误。模式可解构嵌套结构(enum variant/struct/tuple)。match分支必须为同类型。if let是match的单臂语法糖。matches!宏返回bool。"""""},
            {"heading": "匹配守卫与绑定",
             "content": """""模式守卫：match arm + if条件(x if x > 5 => ...)进一步约束模式。@绑定：name @ pattern同时绑定变量和做模式匹配(Some(x @ 3..=7)同时提取值和做范围检查)。ref关键字在模式中获取引用而非移动。|模式提供或匹配(1 | 2 => ...)。_通配符匹配任何值但不绑定。..忽略剩余字段。解构时的move vs ref行为取决于变量后续使用——编译器自动推导最小权限。"""""},
            {"heading": "关键结论",
             "content": """""1. 穷举检查消除遗漏bug 2. match在release模式下生成最优跳转表(类似switch但更强大) 3. Option<T>和Result<T,E>是枚举体系的核心 4. irrefutable模式(总是匹配的)只能用于let/函数参数/for循环 5. 对引用类型match需使用ref模式或匹配前解引用"""""},
            {"heading": "关联知识点",
             "content": """""[[Rust语言-错误处理与Result]] [[Rust语言-所有权与借用]] [[程序设计语言原理-类型系统总览]]"""""}
        ]
    },
    {
        "dir_name": "Rust语言",
        "file_stem": "迭代器与组合器",
        "title": "Rust语言-迭代器与组合器",
        "course": "Rust语言",
        "chapter": "函数式编程",
        "difficulty": "INTERMEDIATE",
        "tags": ["Rust", "Iterator", "组合器", "惰性求值", "适配器"],
        "aliases": ["Rust Iterators", "Combinators", "Lazy Evaluation"],
        "source": "The Rust Book Ch 13; Rust标准库std::iter文档; Rust by Example: Iterators",
        "sections": [
            {"heading": "核心定义",
             "content": """""Iterator trait是Rust迭代器体系的核心：type Item; fn next(&mut self) -> Option<Self::Item>。所有迭代器都是惰性的——在调用next()或消耗适配器(consuming adaptor)之前不执行任何计算。迭代器分为三种：消耗型(consumers — collect/sum/count/for_each最终驱动计算)，适配器(adaptors — map/filter/take构造新迭代器)，复合型(flat_map/fold/scan带状态)。"""""},
            {"heading": "零成本抽象",
             "content": """""Rust迭代器的零成本抽象保证迭代器组合器被LLVM优化为等价的朴素循环：v.iter().filter(|x| *x > 5).map(|x| x * 2).collect::<Vec<_>>()生成的机器码与手写for循环相同。关键：Iterator是为&T/T实现,IntoIterator将容器转为迭代器。iter()返回&T的迭代器(不可变引用,不消耗容器)，into_iter()消耗容器并返回T。双重引用迭代器.flatten()展平嵌套Option/Result。"""""},
            {"heading": "关键结论",
             "content": """""1. 迭代器链的长度取决于组合器数量而非数据量 2. enumerate/zip/chain提供遍历结构 3. rev()要求DoubleEndedIterator trait 4. fold是通用还原器(左折叠) 5. collect支持类型推断(turbo fish: collect::<Vec<_>>()) 6. Iterator的size_hint()指导collect预分配内存"""""},
            {"heading": "关联知识点",
             "content": """""[[Rust语言-闭包与Fn特征]] [[Rust语言-模式匹配与枚举]] [[Go语言-泛型与类型约束]]"""""}
        ]
    },
    {
        "dir_name": "Rust语言",
        "file_stem": "错误处理与Result",
        "title": "Rust语言-错误处理与Result",
        "course": "Rust语言",
        "chapter": "语言设计",
        "difficulty": "BASIC",
        "tags": ["Rust", "Result", "?", "错误传播", "Option"],
        "aliases": ["Rust Error Handling", "Result<T,E>", "? operator"],
        "source": "The Rust Book Ch 9; Rust标准库std::result/std::error文档; RFC 1937 (? operator)",
        "sections": [
            {"heading": "核心定义",
             "content": """""Rust没有异常机制，使用Result<T,E>枚举表达可恢复错误(Ok(T)或Err(E)),panic!表达不可恢复错误。?操作符(早期返回)自动解包Ok值或将Err向上传播：let x = f()?; 等价于 let x = match f() { Ok(v) => v, Err(e) => return Err(e.into()) };。?操作符调用From trait自动转换错误类型。main函数可返回Result<(), Box<dyn Error>>。"""""},
            {"heading": "错误类型设计",
             "content": """""std::error::Error trait是基础错误接口：fn source(&self) -> Option<&(dyn Error + 'static)>支持错误链(链式包装)。thiserror派生宏提供自动Error实现(derive(Error) + Display)。anyhow提供类型擦除的错误容器(anyhow::Result<T> = Result<T, anyhow::Error>)适合应用层。thiserror适合库的精确错误类型，anyhow适合应用的通用错误处理。错误不应被吞掉——_.unwrap()/_.expect()在库代码中不推荐。"""""},
            {"heading": "关键结论",
             "content": """""1. ?操作符仅可用于返回Result/Option的函数中 2. Result的ok()/err()方法转换为Option 3. map_err()修改错误类型但不影响Ok值 4. unwrap_or()/unwrap_or_else()提供默认值 5. 组合Result: and_then/flat_map式的链组合"""""},
            {"heading": "关联知识点",
             "content": """""[[Rust语言-模式匹配与枚举]] [[Rust语言-Option与空值安全]] [[Go语言-错误处理哲学]]"""""}
        ]
    },
    {
        "dir_name": "Rust语言",
        "file_stem": "宏系统",
        "title": "Rust语言-宏系统",
        "course": "Rust语言",
        "chapter": "元编程",
        "difficulty": "ADVANCED",
        "tags": ["Rust", "macro", "proc_macro", "derive", "声明宏"],
        "aliases": ["Rust Macros", "Declarative Macros", "Procedural Macros"],
        "source": "The Rust Book Ch 19; The Little Book of Rust Macros; Rust Reference: Macros",
        "sections": [
            {"heading": "核心定义",
             "content": """""Rust宏系统分两大类。声明宏(declarative/macro_rules!)：基于模式匹配的声明式代码生成器——(pattern) => { expansion }，在AST层操作TokenStream，卫生性(hygiene)防止意外命名冲突(标识符在宏定义和调用处的命名空间独立)。过程宏(procedural)：执行Rust代码来操作TokenStream的函数，三种类型——#[derive]派生宏/Attribute-like属性宏/Function-like函数宏。"""""},
            {"heading": "过程宏详解",
             "content": """""过程宏作为独立crate编译(proc-macro = true)。签名：#[proc_macro_derive(TraitName)] pub fn derive(input: TokenStream) -> TokenStream。proc_macro2和quote/syn是核心生态系统：syn解析TokenStream为Rust AST，quote生成TokenStream。派生宏分析struct/enum结构自动生成trait实现(如serde::Serialize/Deserialize)。属性宏额外接收属性参数。过程宏在编译期执行(类似编译器插件)。"""""},
            {"heading": "关键结论",
             "content": """""1. 声明宏适合重复代码消除，过程宏适合复杂代码生成 2. 宏展开发生在AST→HIR阶段 3. 过程宏crate不能导出宏以外的任何东西 4. 卫生性不是默认在所有场景完美(可以$crate::避坑) 5. proc_macro_span提供调试信息和错误检查 6. 宏的过度使用降低可读性——先考虑泛型和trait"""""},
            {"heading": "关联知识点",
             "content": """""[[Rust语言-泛型与Trait]] [[Rust语言-迭代器与组合器]] [[编译原理-语法树与中间表示]]"""""}
        ]
    },
    {
        "dir_name": "Rust语言",
        "file_stem": "模块与Crate组织",
        "title": "Rust语言-模块与Crate组织",
        "course": "Rust语言",
        "chapter": "工程构建",
        "difficulty": "BASIC",
        "tags": ["Rust", "module", "crate", "visibility", "workspace"],
        "aliases": ["Rust Module System", "Crate Organization", "pub/use"],
        "source": "The Rust Book Ch 7; Rust Reference: Crates and source files; Cargo Book",
        "sections": [
            {"heading": "核心定义",
             "content": """""Rust的模块系统有三层：crate(编译单元, lib或bin)、module(命名空间,用mod声明/引入)、use(导入路径别名)。每个Rust文件隐式创建同名的module(lib.rs是库根,main.rs是二进制根)。mod关键字定义新模块(可内联或关联文件/目录)。可见性：pub使项公开，pub(crate)限制crate内可见，pub(super)父模块可见，pub(in path)特定路径可见，默认私有。"""""},
            {"heading": "Re-export与use惯用法",
             "content": """""use语句导入路径作为快捷方式(use std::collections::HashMap;)。惯用风格：函数导入到父模块级别(use my_mod::some_func;)，struct/enum导入到类型级别(use my_mod::MyStruct;)。pub use(重新导出)改变公开API的路径——可对外隐藏内部结构重新组织。use path::{self, A, B}同时导入模块和子项。prelude模式在lib.rs中集中导出常用类型。"""""},
            {"heading": "关键结论",
             "content": """""1. 模块不通过文件系统反射——Rust文件路径需匹配mod声明而非目录 2. use as提供别名 3. glob导入(use xxx::*)不推荐在公开API中使用 4. extern crate语法已过时(2018 edition) 5. Cargo workspace管理多crate项目共享受依赖"""""},
            {"heading": "关联知识点",
             "content": """""[[Rust语言-cargo与依赖管理]] [[Rust语言-泛型与Trait]] [[软件工程-软件架构设计]]"""""}
        ]
    },
    {
        "dir_name": "Rust语言",
        "file_stem": "测试与文档测试",
        "title": "Rust语言-测试与文档测试",
        "course": "Rust语言",
        "chapter": "工程质量",
        "difficulty": "BASIC",
        "tags": ["Rust", "test", "doctest", "cargo test", "集成测试"],
        "aliases": ["Rust Testing", "Cargo Test", "Doc Tests"],
        "source": "The Rust Book Ch 11; Cargo Book: Tests; Rust Reference: Test attributes",
        "sections": [
            {"heading": "核心定义",
             "content": """""Rust测试框架内置在cargo中，由#[test]属性标记测试函数。单元测试通常与源码放在同一文件中，用#[cfg(test)]模块隔离。cargo test运行所有测试(默认并行,通过--test-threads=1串行)。断言宏：assert!(布尔条件), assert_eq!(left, right)(需PartialEq+Debug), assert_ne!。should_panic(expected='msg')验证panic发生。#[ignore]标记默认跳过的测试。"""""},
            {"heading": "文档测试与集成测试",
             "content": """""文档测试(doctest)是Rust的独特优势：在文档注释(///)中写代码示例会被cargo test编译并执行作为测试，确保文档与代码同步。集成测试放在tests/目录下，作为外部crate测试公开API(每个文件作为独立crate)。benchmark测试使用#[bench]属性(需nightly)或criterion crate(stable替代)。测试输出：cargo test -- --nocapture显示标准输出。"""""},
            {"heading": "关键结论",
             "content": """""1. doctest文档过期会直接编译失败 2. 单元测试可访问私有API,集成测试仅公开API 3. #[cfg(test)]模块不编译进release二进制 4. test utilities可放在tests/common/mod.rs(非测试文件) 5. proptest提供property-based testing(PBT)"""""},
            {"heading": "关联知识点",
             "content": """""[[Rust语言-模块与Crate组织]] [[Go语言-测试与基准测试]] [[软件工程-软件测试策略]]"""""}
        ]
    },
    {
        "dir_name": "Rust语言",
        "file_stem": "FFI与unsafe-Rust",
        "title": "Rust语言-FFI与unsafe Rust",
        "course": "Rust语言",
        "chapter": "系统编程",
        "difficulty": "ADVANCED",
        "tags": ["Rust", "FFI", "unsafe", "extern C", "C ABI"],
        "aliases": ["Rust FFI", "Unsafe Rust", "Foreign Function Interface"],
        "source": "The Rustonomicon; Rust Reference: Unsafe operations; RFC 2045 (target_feature 1.1)",
        "sections": [
            {"heading": "核心定义",
             "content": """""Rust的unsafe块是超级用户模式(superpowers)：可执行5种额外操作——1.解引用裸指针 2.调用unsafe函数/方法 3.访问/修改可变全局变量 4.实现unsafe trait 5.访问union字段。unsafe并不意味着不安全——它表示由程序员而非编译器保证安全。unsafe块应封装在安全抽象后并用// SAFETY注释解释安全理由。extern块声明FFI接口：extern \"C\" fn。"""""},
            {"heading": "FFI实践与ABI",
             "content": """""Rust通过extern声明与C ABI互操作。#[no_mangle]禁止名称修饰(mangling)。extern 'C'使用C调用约定。#[repr(C)]确保结构体布局与C兼容。将Rust回调传递给C时需注意生命周期——Box::into_raw+Box::from_raw管理堆分配。libc crate提供C类型别名。cbindgen工具自动生成C头文件。Deref强化将*mut T/&mut T自动转换。Rust的无效值优化(null pointer optimization)使Option<&T>与&T同大小。"""""},
            {"heading": "关键结论",
             "content": """""1. unsafe缩小范围——越小的unsafe块越容易审查 2. 确保FFI中所有权不跨语言边界泄漏 3. catch_unwind在FFI边界防止panic穿越(panic unwind over FFI is UB) 4. std::ffi::CStr/CString管理C字符串 5. null_mut()/NonNull提供非空裸指针保证"""""},
            {"heading": "关联知识点",
             "content": """""[[Rust语言-所有权与借用]] [[Rust语言-并发原语与Send/Sync]] [[C语言深入-链接器与ABI详解]]"""""}
        ]
    },
    {
        "dir_name": "Rust语言",
        "file_stem": "字符串与str-String",
        "title": "Rust语言-字符串与str/String",
        "course": "Rust语言",
        "chapter": "数据结构",
        "difficulty": "INTERMEDIATE",
        "tags": ["Rust", "String", "&str", "UTF-8", "OsString"],
        "aliases": ["Rust Strings", "&str vs String", "UTF-8 Encoding"],
        "source": "The Rust Book Ch 8; Rust标准库std::string/std::str文档; Rustomicon: String representation",
        "sections": [
            {"heading": "核心定义",
             "content": """""Rust有两种字符串类型：&str(字符串切片)——不可变的UTF-8字节序列引用，(ptr, len)组成。String——可变、可增长的UTF-8字符串，(ptr, len, cap)组成。String可解引用强制转换(Deref)为&str(String: Deref<Target=str>)。Rust字符串保证内容永远是合法UTF-8(NonZero结尾优化zero-sized类型除外)。OsString/OsStr处理平台原生的可能非UTF-8的文件路径。"""""},
            {"heading": "UTF-8与索引",
             "content": """""Rust不支持直接索引字符串s[i](因为UTF-8中一个char可能占1-4字节)。必须通过边界明确的迭代器：.chars()(Unicode标量值)、.bytes()(原始字节)、.char_indices()。切片s[a..b]必须落在char边界上否则panic(使用s.get(a..b)安全返回Option)。String内部是Vec<u8>的包装，所有ASCII操作在Rust字符串上O(1)完成(但需要边界检查)。"""""},
            {"heading": "关键结论",
             "content": """""1. 函数参数优先使用&str(更通用——可接受&String和字面量) 2. String -> &str 通过Deref隐式完成(零成本) 3. &str -> String 需要.to_owned()或.to_string()(分配内存) 4. format!宏构建String 5. Cow<str>提供写时复制的智能字符串(Copy-on-Write)"""""},
            {"heading": "关联知识点",
             "content": """""[[Rust语言-切片与Deref强制]] [[Rust语言-所有权与借用]] [[Go语言-String与[]byte转换]]"""""}
        ]
    },
    {
        "dir_name": "Rust语言",
        "file_stem": "闭包与Fn特征",
        "title": "Rust语言-闭包与Fn特征",
        "course": "Rust语言",
        "chapter": "函数式编程",
        "difficulty": "INTERMEDIATE",
        "tags": ["Rust", "闭包", "Fn", "FnMut", "FnOnce"],
        "aliases": ["Rust Closures", "Fn traits", "Move Closures"],
        "source": "The Rust Book Ch 13; Rust Reference: Closure expressions; Rust标准库std::ops",
        "sections": [
            {"heading": "核心定义",
             "content": """""Rust闭包是捕获环境的匿名函数：|params| { body }。编译器为每个闭包生成唯一的匿名类型(不能直接命名)，该类型实现Fn/FnMut/FnOnce trait中的至少一个。Fn调用通过&self(不可变引用)访问捕获变量。FnMut通过&mut self(可变引用)。FnOnce通过self(所有权转移)。闭包自动(且保守地)推导实现哪些trait——如果闭包消耗了捕获变量只能FnOnce,修改了捕获变量可以FnMut。"""""},
            {"heading": "move闭包与捕获",
             "content": """""move关键字强制闭包获取所有引用变量的所有权(而非借用)。使用场景：线程spawn、异步任务、所有权逃离当前作用域的闭包。闭包捕获的方式：1.捕获不可变引用(最宽松) 2.捕获可变引用 3.按值移动(所有权转移)。编译器遵循最小权限原则选择捕获方式。函数指针fn(i32) -> i32和闭包是不同的——但非捕获闭包可自动强制转换为fn指针。"""""},
            {"heading": "关键结论",
             "content": """""1. FnOnce是三个trait的父trait——所有闭包至少FnOnce 2. 接受闭包的函数用泛型+where约束最灵活 3. Box<dyn Fn()>存储不同类型闭包的堆分配 4. 迭代器适配器接受FnMut闭包(map/filter) 5. 闭包默认不要求Send/Sync除非推导要求(如tokio::spawn)"""""},
            {"heading": "关联知识点",
             "content": """""[[Rust语言-迭代器与组合器]] [[Rust语言-async/await与Future]] [[Rust语言-所有权与借用]]"""""}
        ]
    },
    {
        "dir_name": "Rust语言",
        "file_stem": "HashMap与BTreeMap",
        "title": "Rust语言-HashMap与BTreeMap",
        "course": "Rust语言",
        "chapter": "数据结构",
        "difficulty": "BASIC",
        "tags": ["Rust", "HashMap", "BTreeMap", "哈希算法", "集合"],
        "aliases": ["Rust HashMap", "BTreeMap", "Hashing"],
        "source": "Rust标准库std::collections文档; Rust Hashmap源码(swisstable port); Google SwissTable",
        "sections": [
            {"heading": "核心定义",
             "content": """""Rust的HashMap<K,V,S=RandomState>使用Google SwissTable作为底层实现(Go也是)——SIMD加速的开放寻址哈希表。默认哈希器RandomState使用SipHash-1-3(抵抗HashDoS的密码学安全哈希算法,但非加密强度)。如果哈希算法不需要DoS保护可用FxHash(更快的非加密哈希,基于乘法+移位)。BTreeMap<K,V>是B树实现的有序映射——键必须Ord(有序)，所有操作O(log n)。"""""},
            {"heading": "选择指南与操作",
             "content": """""HashMap vs BTreeMap选择：HashMap更快(平均O(1)访问)，但键无序且迭代顺序不确定。BTreeMap支持有序遍历(range查询)、最小/最大查询(first_entry/last_entry)。Entry API优雅处理'存在即更新，不存在即插入'：map.entry(key).or_insert(val)/and_modify(|v| *v+=1)。HashSet/BTreeSet是value为()的Map特化。保留插入顺序可使用indexmap crate。"""""},
            {"heading": "关键结论",
             "content": """""1. HashMap的DefaultHasher每次运行使用随机种子 2. Entry API一次哈希查找完成or_insert/remove 3. .get()返回Option<&V> 4. HashMap保留值不保留键——remove需要完整键所有权 5. Eq trait != PartialEq(浮点NaN场景) 6. BTreeMap实现sorted_map,适合数据库索引类操作"""""},
            {"heading": "关联知识点",
             "content": """""[[Rust语言-迭代器与组合器]] [[Rust语言-所有权与借用]] [[数据结构-哈希表]]"""""}
        ]
    },
    {
        "dir_name": "Rust语言",
        "file_stem": "Drop与资源管理",
        "title": "Rust语言-Drop与资源管理",
        "course": "Rust语言",
        "chapter": "内存管理",
        "difficulty": "INTERMEDIATE",
        "tags": ["Rust", "Drop", "RAII", "资源管理", "ManuallyDrop"],
        "aliases": ["Rust Drop Trait", "RAII", "ManuallyDrop"],
        "source": "The Rust Book Ch 15; Rust Reference: Destructors; The Rustonomicon: Drop check",
        "sections": [
            {"heading": "核心定义",
             "content": """""Rust通过RAII(Resource Acquisition Is Initialization)管理资源：资源在获取时绑定到变量的生命周期，在变量离开作用域时自动释放。Drop trait定义释放逻辑：fn drop(&mut self)——编译器自动插入drop调用。释放顺序：结构体字段按声明顺序逆序释放。std::mem::drop(v)主动释放变量(将所有权移入drop函数使变量提前离开作用域,drop函数的空body触发实际Drop)。"""""},
            {"heading": "drop检查与Pin",
             "content": """""drop checker防止释放悬垂引用：检查结构体释放时其字段是否仍被其他作用域引用。否则编译报错。ManuallyDrop<T>包装器跳过Drop(用于FFI或复制语义的场景)。Pin<&mut T>与drop的交互——!Unpin的值在Pin后不能安全移动,包括提前drop(需要unsafe Pin::into_inner_unchecked)。mem::forget(v)泄漏内存(消费所有权但不drop),用于FFI所有权转移场景。"""""},
            {"heading": "关键结论",
             "content": """""1. 不能显式调用drop(编译器调用)——使用std::mem::drop预防 2. 实现Copy trait的类型不应实现Drop(Copy语义与Drop冲突) 3. Vec::clear()调用所有元素的drop 4. std::mem::replace/swap可以安全清理资源 5. 递归drop可能导致栈溢出(链表——改用迭代式drop)"""""},
            {"heading": "关联知识点",
             "content": """""[[Rust语言-所有权与借用]] [[Rust语言-FFI与unsafe Rust]] [[C语言深入-指针算术与内存模型]]"""""}
        ]
    },
    {
        "dir_name": "Rust语言",
        "file_stem": "no_std与嵌入式Rust",
        "title": "Rust语言-no_std与嵌入式Rust",
        "course": "Rust语言",
        "chapter": "嵌入式开发",
        "difficulty": "ADVANCED",
        "tags": ["Rust", "no_std", "嵌入式", "PAC", "HAL", "bare metal"],
        "aliases": ["Rust Embedded", "no_std", "PAC/HAL Pattern"],
        "source": "The Embedded Rust Book; Rust Reference: #![no_std]; Rust Embedded Working Group",
        "sections": [
            {"heading": "核心定义",
             "content": """""#![no_std]属性移除标准库依赖(操作系统抽象的集合)，仅保留core库(语言特性的最小子集)。core提供：基础类型(Option/Result/Iterator)、内存操作(mem/manually_drop)、fmt/格式化、Future trait、基本宏。core不提供：堆分配(Box/Vec)、IO(File/println)、线程(thread)。嵌入式Rust使用两抽象层：PAC(Peripheral Access Crate)——内存映射寄存器的薄封装。HAL(Hardware Abstraction Layer)——高层次的硬件抽象。"""""},
            {"heading": "no_std生态",
             "content": """""alloc crate提供堆分配(String/Vec/Box/Rc等需要全局分配器的类型)——比std更轻量且不需要操作系统。全局分配器通过#[global_allocator]设置。embedded-hal trait定义跨芯片通用的硬件接口(spi/i2c/serial/digital IO)，允许驱动的一次编写到处可用。panic_handler和exception handler必须在no_std中定义。cortex-m/riscv crate为各自架构提供启动代码和中断处理。"""""},
            {"heading": "关键结论",
             "content": """""1. no_std无panic unwind(默认panic=abort节省闪存) 2. 格式化宏(write!/format!)在core中可用但需要实现fmt::Write 3. 浮点运算不保证硬件支持(soft-float) 4. .cargo/config.toml指定target和三元组 5. 链接脚本控制内存布局(ld file)"""""},
            {"heading": "关联知识点",
             "content": """""[[Rust语言-Drop与资源管理]] [[Rust语言-FFI与unsafe Rust]] [[计算机组成原理-嵌入式系统基础]]"""""}
        ]
    },
    {
        "dir_name": "Rust语言",
        "file_stem": "cargo与依赖管理",
        "title": "Rust语言-cargo与依赖管理",
        "course": "Rust语言",
        "chapter": "工程构建",
        "difficulty": "BASIC",
        "tags": ["Rust", "cargo", "Cargo.toml", "features", "依赖管理"],
        "aliases": ["Cargo", "Dependencies", "Workspaces", "Features"],
        "source": "The Cargo Book; Rust官方文档: Cargo; RFC 2953 (features v2)",
        "sections": [
            {"heading": "核心定义",
             "content": """""Cargo是Rust的构建系统和包管理器。Cargo.toml定义项目元数据和依赖(语义版本控制SemVer——^1.2.3表示>=1.2.3且<2.0.0)。Cargo.lock锁定精确版本(库不提交lock忽略,二进制应提交lock文件)。cargo build --release启用优化。cargo check快速验证编译(不生成二进制)。RUSTFLAGS环境变量传递额外编译器参数。cargo doc --open生成并打开文档。"""""},
            {"heading": "Features与Workspace",
             "content": """""Cargo features实现条件编译和可选依赖(在Cargo.toml的[features]段定义)。Feature依赖树通过cfg(feature='xxx')和#[cfg(feature='xxx')]在代码中条件启用。default features通过default-features=false禁用。Workspace管理多crate：Cargo.toml[workspace]段列出成员。工作区共享一个顶层target目录和Cargo.lock。patch段替换依赖源(ex:替换为本地路径或git仓库)。"""""},
            {"heading": "关键结论",
             "content": """""1. 库不应提交Cargo.lock(应被忽略) 2. Feature additive原则——feature应纯增加功能而非改变行为 3. cargo tree查看依赖树 4. cargo audit检查安全漏洞 5. cargo vendor创建离线依赖缓存 6. crates.io的readme和categories提升可发现性"""""},
            {"heading": "关联知识点",
             "content": """""[[Rust语言-模块与Crate组织]] [[Go语言-Module与依赖管理]] [[软件工程-版本控制与Git]]"""""}
        ]
    },
    {
        "dir_name": "Rust语言",
        "file_stem": "类型转换与From-Into",
        "title": "Rust语言-类型转换与From/Into",
        "course": "Rust语言",
        "chapter": "类型系统",
        "difficulty": "BASIC",
        "tags": ["Rust", "From", "Into", "TryFrom", "类型转换"],
        "aliases": ["Rust Type Conversion", "From/Into traits", "TryFrom"],
        "source": "The Rust Book Ch 9; Rust标准库std::convert文档; Rust Reference: Type coercions",
        "sections": [
            {"heading": "核心定义",
             "content": """""Rust的类型转换体系围绕标准trait：From<T>(不可出错的转换), Into<T>(From的反向,自动派生——impl<T,U:From<T>> Into<U> for T), TryFrom<T>/TryInto<T>(可出错的转换,返回Result)。实现From自动获得Into。使用场景：?操作符通过From转换错误类型, collect()通过FromIterator收集,函数参数通过Into接受多种类型(impl Into<String>接受&str/String)。"""""},
            {"heading": "类型强制转换(Type Coercions)",
             "content": """""编译器在特定位置自动执行类型强制转换(coercion)：1. &T到&dyn Trait(unsized coercion) 2. &mut T到&mut dyn Trait 3. &T到*const T, &mut T到*mut T 4. 非捕获闭包到fn指针 5. Deref强制——&String到&str(通过Deref trait)。as关键字执行显式转换(数字类型转换、指针互转、enum到整数)。as不会像C那样静默截断有符号/无符号转换。"""""},
            {"heading": "关键结论",
             "content": """""1. 库应实现From<T>而非Into(因泛型Into自动派生) 2. 从自己crate的类型到外部类型的From不能实现(孤儿规则) 3. 数值as转换可能产生意外(overflow cast在debug panic,release wrap) 4. transmute是unsafe的类型转换终极武器(仅重新解释内存) 5. 调用arg.into()可接受多种输入类型"""""},
            {"heading": "关联知识点",
             "content": """""[[Rust语言-错误处理与Result]] [[Rust语言-切片与Deref强制]] [[Rust语言-泛型与Trait]]"""""}
        ]
    },
    {
        "dir_name": "Rust语言",
        "file_stem": "const泛型与编译期计算",
        "title": "Rust语言-const泛型与编译期计算",
        "course": "Rust语言",
        "chapter": "类型系统",
        "difficulty": "ADVANCED",
        "tags": ["Rust", "const generics", "const fn", "编译期计算"],
        "aliases": ["Rust Const Generics", "Const fn", "Compile-time Computation"],
        "source": "Rust Reference: Const generics; RFC 2000 (const generics); Rust Blog: const generics MVP",
        "sections": [
            {"heading": "核心定义",
             "content": """""Const泛型(const generics)允许将编译期已知的常量值作为类型参数：fn foo<const N: usize>() -> [i32; N]。这使得编译期确定大小的数组成为一等公民(如[T; N]实现所有需要的trait)。Rust 1.51+支持基础const泛型。const fn可以在编译期执行(如计算数组初始化值、const上下文中的函数调用)。const表达式中可用的操作有限(不能使用for/loop/while/if let)。"""""},
            {"heading": "编译期计算能力",
             "content": """""const fn中可用：基本算术、分支(if/else)、match、const泛型参数、其他const fn调用。不能使用迭代器(部分可用在nightly)、可变引用、分配内存。const泛型可配合typenum crate进行类型级Nat数运算。数组[0; N]属于const泛型的基础用例。const_evaluatable_unchecked提供更多编译期计算。CTFE(Compile-Time Function Evaluation)在MIR层面进行。"""""},
            {"heading": "关键结论",
             "content": """""1. const泛型实现数组大小泛型化——之前只能通过宏或impl_for_len! 2. const fn不能分配堆内存 3. 不稳定特性const_generic_defaults支持const参数的默认值 4. const block(在稳定化中)允许在非const函数中执行const求值 5. 编译期计算不会影响运行时性能(完全在编译期完成)"""""},
            {"heading": "关联知识点",
             "content": """""[[Rust语言-泛型与Trait]] [[Rust语言-所有权与借用]] [[编译原理-静态分析与优化]]"""""}
        ]
    },
    {
        "dir_name": "Rust语言",
        "file_stem": "切片与Deref强制",
        "title": "Rust语言-切片与Deref强制",
        "course": "Rust语言",
        "chapter": "类型系统",
        "difficulty": "INTERMEDIATE",
        "tags": ["Rust", "切片", "Deref", "unsized coercion", "&[T]"],
        "aliases": ["Rust Slices", "Deref Coercions", "Unsized Coercion"],
        "source": "The Rust Book Ch 15; Rust Reference: Type coercions; The Rustonomicon: Exotic Sizes",
        "sections": [
            {"heading": "核心定义",
             "content": """""切片(slice)是对连续序列[T]的引用视图：&[T](不可变切片)和&mut [T](可变切片)。切片不拥有数据——它仅是(ptr, len)的fat pointer(胖指针,16字节在64位系统——相比普通指针8字节)。Vec<T>可Deref到&[T],因此所有接受&[T]的函数同时接受&Vec<T>。str类型是[u8]切片的不同UTF-8保证的'视图'——&str是切片引用(Deref: String→&str)。"""""},
            {"heading": "Deref强制详解",
             "content": """""Deref trait(fn deref(&self) -> &Self::Target)允许类型在被解引用时返回另一个类型的引用。编译器在函数调用、方法调用、字段访问时自动插入*和解引用操作(最多应用一次Deref)。DerefMut对应可变解引用。Deref强制允许：&T到&U(当T: Deref<Target=U>)、&mut T到&mut U、&mut T到&U。Box<T>通过Deref获得T的所有方法(Rust中'智能指针'的运作方式)。"""""},
            {"heading": "关键结论",
             "content": """""1. Deref不是继承——不会改变类型本质(fn签名仍要求具体类型) 2. 切片可被索引(s[i])但通过Index trait而非切片本身 3. 数组[T; N]自动强制为&[T] 4. 胖指针(&[T]/&dyn Trait)占用两个usize 5. 实现Deref仅在语义上是某种智能指针时——滥用破坏可读性"""""},
            {"heading": "关联知识点",
             "content": """""[[Rust语言-字符串与str/String]] [[Rust语言-所有权与借用]] [[Rust语言-类型转换与From/Into]]"""""}
        ]
    },

    # ═══════════════════════════════════════════════════════════════
    # C语言深入 — 20 additional topics (to reach 35 total)
    # ═══════════════════════════════════════════════════════════════
    {
        "dir_name": "C语言深入",
        "file_stem": "联合体与类型双关",
        "title": "C语言-联合体与类型双关",
        "course": "C语言深入",
        "chapter": "数据结构",
        "difficulty": "INTERMEDIATE",
        "tags": ["C语言", "union", "type punning", "内存布局"],
        "aliases": ["C Union", "Type Punning"],
        "source": "C11 Standard §6.7.2.1 §6.5.2.3; GCC Manual §4.9 Unions; K&R Ch 6 & 8",
        "sections": [
            {"heading": "核心定义",
             "content": """""联合体(union)是一块共享内存区域，不同时刻可以存储不同类型的值。联合体大小等于最大成员的大小。C11规定在任一时刻只有最后赋值的成员处于激活状态。读取非激活成员在C中是未定义行为(UB)，但通过联合体进行类型双关(type punning)是GCC和MSVC的通用扩展(实践中被广泛使用)。匿名联合体(C11)允许在结构体内创建联合作作用域成员。"""""},
            {"heading": "类型双关合法方案",
             "content": """""合法的类型双关(将一个位模式解释为不同的类型)方法：1.)char*例外——任何类型的对象都可以通过char*访问其字节表示 2.)C11的memcpy技巧——memcpy字节复制的类型双关被编译器优化为零开销 3.)union双关在C99(非C++)中可能是合法的实现定义行为 4.)GCC的-Wno-strict-aliasing可禁用严格别名警告。使用union处理浮点字节表示、字节序检测(网络序vs主机序)是常见实践。"""""},
            {"heading": "关键结论",
             "content": """""1. union不能同时存储多个成员、无类型安全机制 2. 读取非活跃成员(UB警告)——用memcpy安全替代 3. union常用于实现variant/tagged union(类型标记+union) 4. 嵌套在struct内部的union可节省内存(同时使用的字段共享内存)"""""},
            {"heading": "关联知识点",
             "content": """""[[C语言深入-指针算术与内存模型]] [[C语言深入-内存对齐与位域详解]] [[C语言深入-内联汇编]]"""""}
        ]
    },
    {
        "dir_name": "C语言深入",
        "file_stem": "静态库与动态库构建",
        "title": "C语言-静态库与动态库构建",
        "course": "C语言深入",
        "chapter": "编译与链接",
        "difficulty": "INTERMEDIATE",
        "tags": ["C语言", "静态库", "动态库", ".a", ".so", "rpath"],
        "aliases": ["Static Library", "Shared Library", "rpath"],
        "source": "GCC Manual §3.14 Options for Linking; Ulrich Drepper《How To Write Shared Libraries》; ELF Spec",
        "sections": [
            {"heading": "核心定义",
             "content": """""静态库(.a, archive)是编译后的目标文件(.o)的归档集合：ar rcs libfoo.a foo.o bar.o。链接时静态库的代码被复制到最终可执行文件，增大文件尺寸但无需运行时依赖。动态库(.so/.dll)在运行时加载：gcc -shared -fPIC -o libfoo.so foo.c。链接动态库时需要-lfoo(链接时)和LD_LIBRARY_PATH(运行时)。相对位置独立代码(fPIC)使得代码段可被多个进程共享。"""""},
            {"heading": "rpath与动态加载",
             "content": """""rpath(RUNPATH)是嵌入在可执行文件中的运行时库搜索路径：-Wl,-rpath,'$ORIGIN/../lib'(相对于可执行文件位置的路径)。ldconfig管理系统级库缓存(/etc/ld.so.cache)。dlopen/dlsym/dlerror/dlclose提供运行时动态加载机制——插件系统的基础。符号可见性(__attribute__((visibility('default'/'hidden'))))控制动态库的公共API——默认隐藏+显式导出是最佳实践。"""""},
            {"heading": "关键结论",
             "content": """""1. 静态库无版本兼容问题但无法热更新 2. 动态库符号版本管理(symbol versioning)防止ABI不兼容 3. -Bsymbolic绑定符号到库内(减少GOT重定位) 4. ldd命令查看动态库依赖 5. 跨平台差异显著——Windows DLL不同机制(需要__declspec(dllexport/dllimport))"""""},
            {"heading": "关联知识点",
             "content": """""[[C语言深入-链接器与ABI详解]] [[C语言深入-预处理器宏与条件编译]] [[C语言深入-跨平台移植要点]]"""""}
        ]
    },
    {
        "dir_name": "C语言深入",
        "file_stem": "setjmp-longjmp与异常处理",
        "title": "C语言-setjmp/longjmp与异常处理",
        "course": "C语言深入",
        "chapter": "错误处理",
        "difficulty": "ADVANCED",
        "tags": ["C语言", "setjmp", "longjmp", "跳转", "异常"],
        "aliases": ["Non-local Jumps", "setjmp/longjmp"],
        "source": "C11 Standard §7.13; APUE §7.10; CERT C ERR04-C",
        "sections": [
            {"heading": "核心定义",
             "content": """""setjmp/longjmp提供非局部跳转(non-local goto)能力：setjmp(jmp_buf env)在调用点保存当前执行环境(寄存器、栈指针、程序计数器)，返回0。longjmp(env, val)恢复保存的环境使setjmp重新\"返回\"值为val。典型的异常模拟模式——在深层调用栈中检测到错误时跳长距离返回到已保存的安全点。jmp_buf通常是平台相关的寄存器保存区数组。"""""},
            {"heading": "陷阱与限制",
             "content": """""1.)longjmp后自动变量的值不确定(若在setjmp和longjmp间被修改)——volatile可缓解 2.)longjmp不触发栈展开——不会调用对象的析构函数(C无析构但资源泄漏风险高) 3.)信号处理器中调用longjmp不够安全——使用siglongjmp 4.)longjmp激活的跳转不能返回到已退出的函数。现代C代码越来越少使用，倾向于使用返回值链或errno——但交互式解释器和coroutine实现仍有使用。"""""},
            {"heading": "关键结论",
             "content": """""1. setjmp/longjmp是C的goto on steroids 2. 不推荐在C++中使用(绕过析构函数) 3. Ruby、Lua等语言的协程/异常由setjmp实现 4. POSIX规定longjmp在信号处理器中必须配合sigsetjmp/siglongjmp 5. 性能：setjmp约15-30ns(寄存器保存),longjmp类似"""""},
            {"heading": "关联知识点",
             "content": """""[[C语言深入-信号处理与异步安全]] [[C语言深入-错误处理errno]] [[C语言深入-递归与尾递归]]"""""}
        ]
    },
    {
        "dir_name": "C语言深入",
        "file_stem": "信号处理与异步安全",
        "title": "C语言-信号处理与异步安全",
        "course": "C语言深入",
        "chapter": "系统编程",
        "difficulty": "ADVANCED",
        "tags": ["C语言", "signal", "sigaction", "异步安全", "信号"],
        "aliases": ["POSIX Signals", "sigaction", "Async-Signal-Safe"],
        "source": "POSIX.1-2017; signal(7) man page; APUE §10; TLPI Ch 20-22",
        "sections": [
            {"heading": "核心定义",
             "content": """""信号是UNIX/Linux系统中进程间异步通知机制。signal()注册信号处理函数(不可移植——应使用sigaction)。sigaction()提供精细控制：sa_handler(处理器)、sa_mask(处理期间阻塞的信号集)、sa_flags(SA_RESTART自动重启被中断的系统调用、SA_SIGINFO接收附加数据)。信号分为标准信号(1-31)和实时信号(SIGRTMIN-SIGRTMAX)。SIGKILL/SIGSTOP不能被捕获或忽略。"""""},
            {"heading": "异步信号安全",
             "content": """""异步信号安全函数(async-signal-safe)列表是信号处理器中唯一可安全调用的函数(由POSIX定义)。核心安全函数：write/read、_exit、signal、sigprocmask、sem_post、fcntl。不安全函数(在信号处理器中调用会导致UB)：printf/malloc(可能死锁,因为信号可能中断了正在执行的malloc,导致内部锁不一致)。使用volatile sig_atomic_t传递状态。替代方案：self-pipe trick——信号处理器仅向管道写1字节,主事件循环读取。"""""},
            {"heading": "关键结论",
             "content": """""1. 永远不应从信号处理器调用printf/malloc/exit 2. sigsuspend/ppoll提供原子化的解阻塞+等待信号 3. signalfd(Linux特有)将信号转为文件描述符——更适合event loop 4. real-time信号支持队列(sigqueue)而非合并 5. SIGCHLD+waitpid处理子进程退出"""""},
            {"heading": "关联知识点",
             "content": """""[[C语言深入-setjmp/longjmp与异常处理]] [[C语言深入-多线程pthread]] [[操作系统-进程间通信IPC]]"""""}
        ]
    },
    {
        "dir_name": "C语言深入",
        "file_stem": "volatile与内存映射IO",
        "title": "C语言-volatile与内存映射IO",
        "course": "C语言深入",
        "chapter": "嵌入式与系统编程",
        "difficulty": "INTERMEDIATE",
        "tags": ["C语言", "volatile", "MMIO", "内存映射", "编译器优化"],
        "aliases": ["Volatile Keyword", "Memory-Mapped IO"],
        "source": "C11 Standard §6.7.3; GCC volatile documentation; Linux Device Drivers Ch 9",
        "sections": [
            {"heading": "核心定义",
             "content": """""volatile关键字告诉编译器：变量可能在任何时刻被外部因素改变(硬件寄存器、信号处理器、另一个线程)，禁止对该变量的所有优化(常量折叠、死代码消除、重排序)。在嵌入式编程中，volatile用于访问内存映射IO(MMIO)寄存器——硬件设备将寄存器映射到特定的物理内存地址，通过volatile指针访问。volatile不提供原子性：只有sig_atomic_t被保证在volatile下对信号处理器是原子的。"""""},
            {"heading": "volatile误解",
             "content": """""常见误解：volatile不能替代内存屏障(memory barrier/fence)或原子操作：volatile仅禁止编译器重排序，但不禁止CPU的运行时重排序(乱序执行)。在多核并发编程中volatile完全不够——需要用C11 atomic types或内存屏障。volatile也不保证volatile操作的可见性能跨越CPU cache。C11已区分volatile(设备访问)和_Atomic(并发访问)的角色——两个概念在旧代码中常被混用。"""""},
            {"heading": "关键结论",
             "content": """""1. volatile读取每个操作都从内存重读(而非寄存器缓存) 2. volatile ≠ atomic ≠ thread-safe 3. 主要用于：MMIO、信号处理器共享标志、setjmp后安全访问 4. 现代C代码的信号标志应使用_Atomic sig_atomic_t 5. Linux内核使用READ_ONCE/WRITE_ONCE宏包装volatile(语义更清晰)"""""},
            {"heading": "关联知识点",
             "content": """""[[C语言深入-C11原子操作]] [[C语言深入-编译优化选项]] [[操作系统-设备驱动基础]]"""""}
        ]
    },
    {
        "dir_name": "C语言深入",
        "file_stem": "restrict限定符",
        "title": "C语言-restrict限定符",
        "course": "C语言深入",
        "chapter": "编译器优化",
        "difficulty": "ADVANCED",
        "tags": ["C语言", "restrict", "别名分析", "编译优化"],
        "aliases": ["Restrict Qualifier", "Pointer Aliasing", "Strict Aliasing"],
        "source": "C11 Standard §6.7.3.1; GCC Manual: -fstrict-aliasing; K&R 2nd ed §A.8.2",
        "sections": [
            {"heading": "核心定义",
             "content": """""restrict限定符是程序员给编译器的承诺(promise)：在指针/引用的生命周期内，只有该指针(或从其直接派生的指针)访问所指对象。这消除了指针别名(pointer aliasing)——编译器可以因此做更激进的优化(如SIMD向量化、循环展开、指令重排)。最经典的用法：memcpy(void *restrict dst, const void *restrict src, size_t n)保证dst和src不重叠。出现重叠时行为未定义。"""""},
            {"heading": "别名分析与性能",
             "content": """""别名分析(alias analysis)是编译器中最关键的分析之一——两个指针是否可能指向同一位置决定了编译器能否安全重排读写操作。restrict在C11中仅为函数参数而定义。违反restrict由程序员负责——编译器不诊断。restrict无法替代noalias的所有场景(如跨函数分析)。Fortran默认假定数组参数不重叠(no aliasing),这是Fortran在某些场景下比C快的重要原因。"""""},
            {"heading": "关键结论",
             "content": """""1. restrict不等于const——restrict防止别名,const防止修改 2. restrict约束仅适用于指针,不适用于标量 3. GCC/Clang都充分优化restrict标注的代码(尤其是循环向量化) 4. restrict误用导致极难调试的bug(只有特定优化级别下才触发) 5. C++无restrict等效物(需__restrict编译器扩展)"""""},
            {"heading": "关联知识点",
             "content": """""[[C语言深入-指针算术与内存模型]] [[C语言深入-编译优化选项]] [[编译原理-静态分析与优化]]"""""}
        ]
    },
    {
        "dir_name": "C语言深入",
        "file_stem": "C11原子操作",
        "title": "C语言-C11原子操作",
        "course": "C语言深入",
        "chapter": "并发编程",
        "difficulty": "ADVANCED",
        "tags": ["C语言", "stdatomic.h", "原子操作", "内存序", "C11"],
        "aliases": ["C11 Atomics", "stdatomic.h", "Memory Order"],
        "source": "C11 Standard §7.17; C++ Concurrency in Action (Williams) Ch 5; GCC atomic builtins",
        "sections": [
            {"heading": "核心定义",
             "content": """""C11引入<stdatomic.h>提供语言级别的原子操作。_Atomic类型限定符声明原子变量(_Atomic int counter)。原子操作函数：atomic_store(&a, val, order)——原子写, atomic_load(&a, order)——原子读, atomic_compare_exchange_weak/strong——CAS操作, atomic_fetch_add/sub/and/or/xor——原子读-改-写。原子操作保证操作的不可分割性(不会被其他线程中断)和内存序。"""""},
            {"heading": "内存序模型",
             "content": """""C11定义六种内存序(memory order)：memory_order_relaxed(无同步,仅原子性)、memory_order_consume(数据依赖排序,C++17不推荐)、memory_order_acquire(获取:后续读写不能重排到此读之前)、memory_order_release(释放:之前的读写不能重排到此写之后)、memory_order_acq_rel(获取+释放,用于RMW操作)、memory_order_seq_cst(顺序一致性——默认,性能最差但最易推理)。lock-free property由atomic_is_lock_free检查——某些平台可能需要锁实现原子。"""""},
            {"heading": "关键结论",
             "content": """""1. 默认memory_order_seq_cst提供最强保证但开销最大(需要全局顺序) 2. fence(atomic_thread_fence)单独建立内存序而不依赖原子操作 3. CAS操作区分strong(虚假失败概率低)和weak(可能因spurious fail) 4. atomic_flag是唯一保证在每个平台都无锁的类型 5. 避免在信号处理器中使用非lock-free的_atomic类型"""""},
            {"heading": "关联知识点",
             "content": """""[[C语言深入-volatile与内存映射IO]] [[C语言深入-多线程pthread]] [[操作系统-同步与死锁]]"""""}
        ]
    },
    {
        "dir_name": "C语言深入",
        "file_stem": "多线程pthread",
        "title": "C语言-多线程pthread",
        "course": "C语言深入",
        "chapter": "并发编程",
        "difficulty": "INTERMEDIATE",
        "tags": ["C语言", "pthread", "POSIX", "多线程"],
        "aliases": ["POSIX Threads", "pthread API"],
        "source": "POSIX.1-2017; Butenhof《Programming with POSIX Threads》; pthreads(7) manual",
        "sections": [
            {"heading": "核心定义",
             "content": """""POSIX线程(pthread)是UNIX系统的标准多线程API。核心函数：pthread_create(&tid, attr, func, arg)创建线程，pthread_join(tid, &ret)等待线程结束回收资源，pthread_exit(ret)线程退出。pthread_self()返回自身ID。线程属性pthread_attr_init/attr_setstacksize控制线程栈大小等。线程数过多可能超出系统资源(pthread默认栈8MB Linux,每个线程消耗虚拟地址空间)。"""""},
            {"heading": "同步原语",
             "content": """""pthread提供三种同步机制：互斥锁——pthread_mutex_init/lock/trylock/unlock/destroy。读写锁——pthread_rwlock_rdlock/wrlock(读者优先或写者优先策略)。条件变量——pthread_cond_wait/signal/broadcast(配合mutex解决特定条件的等待)。pthread_once确保函数在进程中仅执行一次。pthread_key_create建立线程局部存储(TLS)。屏障(pthread_barrier)确保多线程同步于某点。"""""},
            {"heading": "关键结论",
             "content": """""1. 线程安全函数列表由POSIX定义——printf不加锁但线程安全 2. 每个线程有独立的errno(通过TLS实现) 3. pthread_cancel异步取消线程可能导致资源泄漏(使用cleanup handler) 4. 不能fork正在运行的线程(子进程仅复制调用线程) 5. 线程ID复用——使用pthread_equal比较而非== 6. 信号与线程：信号发送给整个进程但由任意线程处理"""""},
            {"heading": "关联知识点",
             "content": """""[[C语言深入-C11原子操作]] [[C语言深入-信号处理与异步安全]] [[操作系统-进程与线程]]"""""}
        ]
    },
    {
        "dir_name": "C语言深入",
        "file_stem": "标准IO缓冲机制",
        "title": "C语言-标准IO缓冲机制",
        "course": "C语言深入",
        "chapter": "标准库",
        "difficulty": "INTERMEDIATE",
        "tags": ["C语言", "stdio", "缓冲", "FILE", "setvbuf"],
        "aliases": ["C stdio buffering", "FILE*", "setvbuf"],
        "source": "C11 Standard §7.21; APUE §5.4; GNU C Library manual §12.20",
        "sections": [
            {"heading": "核心定义",
             "content": """""C标准IO库(FILE*)在用户空间维护缓冲区以减少系统调用次数。三种缓冲模式：1.)_IOFBF(全缓冲)——缓冲区满才write(磁盘文件默认,通常4KB-8KB) 2.)_IOLBF(行缓冲)——遇到换行符时write(终端stdout默认) 3.)_IONBF(无缓冲)——每次写都是write系统调用(stderr默认)。setvbuf(fp, buf, mode, size)可设置缓冲模式和自定义缓冲区。未调用setvbuf前缓冲区大小未定义但通常为BUFSIZ(8192)。"""""},
            {"heading": "缓冲陷阱",
             "content": """""常见错误：1.)fork前未fflush——子进程重复父进程的缓冲区数据(缓冲复制) 2.)同一文件使用FILE*和裸fd操作导致数据交错 3.)_exit()不刷新缓冲区(exit()会) 4.)输出重定向使stdout从行缓冲变为全缓冲(导致输出不显示) 5.)setvbuf的buf参数在关闭前不应被释放(fclose后不可再使用)。不同FILE*共享同一个打开的文件描述符(dup)可能导致缓冲问题。"""""},
            {"heading": "关键结论",
             "content": """""1. stderr无缓冲——错误消息即时输出 2. fflush(NULL)刷新所有输出流 3. glibc中stdout的缓冲模式检测isatty()自动调整 4. 自定义缓冲可实现完全无锁写入(ring buffer) 5. FILE*的缓冲不可跨进程(与mmap不同) 6. fclose隐式fflush——防止数据丢失"""""},
            {"heading": "关联知识点",
             "content": """""[[C语言深入-错误处理errno]] [[C语言深入-跨平台移植要点]] [[操作系统-文件系统与IO基础]]"""""}
        ]
    },
    {
        "dir_name": "C语言深入",
        "file_stem": "可变参数与stdarg",
        "title": "C语言-可变参数与stdarg",
        "course": "C语言深入",
        "chapter": "语言特性",
        "difficulty": "INTERMEDIATE",
        "tags": ["C语言", "可变参数", "stdarg", "va_list", "variadic"],
        "aliases": ["C Variadic Functions", "va_list", "stdarg.h"],
        "source": "C11 Standard §7.16; K&R 2nd ed §7.3; GCC Manual: Variable Argument Macros",
        "sections": [
            {"heading": "核心定义",
             "content": """""可变参数函数(如printf)通过<stdarg.h>的宏实现。声明：int func(int cnt, ...)(至少一个固定参数)。函数内：va_list ap; va_start(ap, last_named_param)初始化；va_arg(ap, type)提取下一个参数(类型必须与实际匹配否则UB); va_end(ap)清理；va_copy用于保存/复制va_list状态。可变参数调用约定(cdecl)：参数从右向左入栈，调用者负责清理(支持可变参数)。"""""},
            {"heading": "实现机制与陷阱",
             "content": """""在x86-64 ABI中，前6个整型参数通过寄存器传递(rdi/rsi/rdx/rcx/r8/r9)，前8个浮点参数通过xmm0-7。可变参数通过寄存器保存区(register save area)和栈同时传递——编译器生成代码将所有整数和浮点寄存器dump到栈上的固定偏移。printf的实现需解析格式串以推断参数类型。类型不匹配(va_arg(ap, long)从int)导致数据错位。va_arg(ap, float)提升为double(默认参数提升)。"""""},
            {"heading": "关键结论",
             "content": """""1. 可变参数宏__VA_ARGS__提供宏级别的可变参数 2. va_copy是C99新增——不可直接赋值va_list 3. 不可在longjmp后访问已跳过的va_list 4. C23引入va_start的简化形式(void省略last param) 5. 可变参数类型检查无编译器保证——使用format属性(__attribute__((format)))辅助"""""},
            {"heading": "关联知识点",
             "content": """""[[C语言深入-预处理器宏与条件编译]] [[C语言深入-错误处理errno]] [[C语言深入-链接器与ABI详解]]"""""}
        ]
    },
    {
        "dir_name": "C语言深入",
        "file_stem": "递归与尾递归",
        "title": "C语言-递归与尾递归",
        "course": "C语言深入",
        "chapter": "程序设计",
        "difficulty": "BASIC",
        "tags": ["C语言", "递归", "尾递归", "TCO", "调用栈"],
        "aliases": ["C Recursion", "Tail Call Optimization"],
        "source": "K&R §4.10; SICP §1.2.1; GCC Manual: -foptimize-sibling-calls; C11 Standard §6.5.2.2",
        "sections": [
            {"heading": "核心定义",
             "content": """""递归函数是直接或间接调用自身的函数。每次递归调用在调用栈上分配新的栈帧(保存局部变量、返回地址)。尾递归(tail recursion)是递归调用的特例——return f(args)是函数的最后操作(无后续计算)。尾调用优化(TCO/Tail Call Optimization)：编译器识别尾调用，复用当前栈帧而非新建栈帧，将调用转换为跳转(jmp)——将O(n)空间降为O(1)，避免栈溢出。"""""},
            {"heading": "C与尾递归",
             "content": """""GCC和Clang都支持尾递归优化(-foptimize-sibling-calls, -O2以上默认开启)。但C标准不保证TCO——不能依赖它实现无限循环。限制TCO的因素：调用者与被调者参数类型不匹配、返回类型不同、可变参数函数、包含C++析构函数场景。递归转迭代是通用方法(使用显式栈结构)。二分查找、快速排序、DFS等经典算法的递归形式在TCO后等价于迭代。"""""},
            {"heading": "关键结论",
             "content": """""1. 尾递归=compile-time checkable迭代 2. 非尾递归的递推式必须为每个调用分配新栈帧 3. 编译器不能TCO的场景静默回退为普通调用(栈深度危险) 4. 基于continuation-passing style(CPS)可将任何递归转为尾递归 5. 线性递归vs树递归——后者无法完全TCO(但可部分)"""""},
            {"heading": "关联知识点",
             "content": """""[[C语言深入-指针算术与内存模型]] [[C语言深入-setjmp/longjmp与异常处理]] [[算法设计与分析-分治与递归]]"""""}
        ]
    },
    {
        "dir_name": "C语言深入",
        "file_stem": "内联汇编",
        "title": "C语言-内联汇编",
        "course": "C语言深入",
        "chapter": "系统编程",
        "difficulty": "ADVANCED",
        "tags": ["C语言", "内联汇编", "GCC", "asm", "clobber"],
        "aliases": ["GCC Inline Assembly", "Extended Asm", "Clobber List"],
        "source": "GCC Manual §6.45 How to Use Inline Assembly; Intel/AMD Software Developer Manuals",
        "sections": [
            {"heading": "核心定义",
             "content": """""GCC扩展内联汇编语法：asm [volatile] ( AssemblerTemplate : OutputOperands : InputOperands : Clobbers : GotoLabels)。输出操作数约束='=r'(寄存器)或'=m'(内存)或'=&r'(earlyclobber——不与输入共享寄存器)。输入操作数约束'r'(寄存器)/'m'(内存)/'i'(立即数)。clobber列表声明被修改的寄存器('cc'条件码, 'memory'内存屏障)。asm volatile阻止编译器消除看似无副作用的汇编块。"""""},
            {"heading": "约束与技巧",
             "content": """""操作数约束字母映射到机器寄存器：x86: a(eax),b(ebx),c(ecx),d(edx),S(esi),D(edi), r(通用寄存器)；ARM: r(通用),w(VFP),t(thumb)。+前缀标记输入输出双向操作数。%0-%n引用操作数(按出现顺序)。memory clobber是最强的编译器屏障——阻止跨内联汇编的load/store重排序和寄存器缓存(相当于full compiler barrier)。GCC也支持Basic asm(简单asm块)但不应使用(无法与控制流集成)。"""""},
            {"heading": "关键结论",
             "content": """""1. 内联汇编破坏跨平台性——应为每个目标架构提供C备选实现 2. 错误声明clobber导致极难调试的奇怪bug(寄存器损坏) 3. volatile asm不一定能替代原子操作 4. GCC 4.x+允许标记goto labels实现跳转到C标签 5. 用宏包装内联汇编以提供类型检查 6. MSVC的内联汇编(__asm{})与GCC不兼容(非__asm__)"""""},
            {"heading": "关联知识点",
             "content": """""[[C语言深入-链接器与ABI详解]] [[C语言深入-volatile与内存映射IO]] [[计算机组成原理-指令集架构]]"""""}
        ]
    },
    {
        "dir_name": "C语言深入",
        "file_stem": "错误处理errno",
        "title": "C语言-错误处理errno",
        "course": "C语言深入",
        "chapter": "错误处理",
        "difficulty": "BASIC",
        "tags": ["C语言", "errno", "错误处理", "perror", "strerror"],
        "aliases": ["C errno", "Error Handling", "perror/strerror"],
        "source": "C11 Standard §7.5; POSIX.1-2017 errno.h; APUE §1.7; CERT C ERR30-C",
        "sections": [
            {"heading": "核心定义",
             "content": """""errno是C/POSIX标准错误报告机制——一个线程局部(thread-local)整数变量。库函数和系统调用在失败时设置errno为特定的错误码(EACCES权限拒绝、ENOENT文件不存在、EINTR被信号中断、EAGAIN资源暂时不可用等)。仅在函数返回-1或NULL时才检查errno——成功的函数也可能修改errno。perror(msg)输出msg+errno文本到stderr。strerror(errno)返回错误描述字符串。"""""},
            {"heading": "线程安全与errno",
             "content": """""现代系统中errno通过宏实现，展开为获取线程局部errno的函数调用：(*__errno_location())。这意味着errno在多线程程序中每个线程独立——不需要互斥。不应在信号处理器中设置errno(使用SA_SIGINFO的si_errno字段)。检查errno前应保存其值(可能在下一个函数调用中被覆盖)。在write的EINTR处理中errno和restart语义需小心处理。"""""},
            {"heading": "关键结论",
             "content": """""1. errno永远不应清零(由库函数设置) 2. 函数成功时errno的值不确定 3. 调用strerror之前应立即保存errno(非线程安全的某些实现) 4. 检查特定errno前应先确认函数返回错误 5. EINTR是'友好的'错误——提示重新调用而非失败 6. CERT C禁止依赖errno的值来区分错误"""""},
            {"heading": "关联知识点",
             "content": """""[[C语言深入-信号处理与异步安全]] [[C语言深入-多线程pthread]] [[C语言深入-标准IO缓冲机制]]"""""}
        ]
    },
    {
        "dir_name": "C语言深入",
        "file_stem": "编译优化选项",
        "title": "C语言-编译优化选项",
        "course": "C语言深入",
        "chapter": "编译器",
        "difficulty": "INTERMEDIATE",
        "tags": ["C语言", "编译优化", "-O2", "LTO", "PGO"],
        "aliases": ["Compiler Optimization", "-O0/-O2/-O3", "LTO", "PGO"],
        "source": "GCC Manual §3.10 Options That Control Optimization; LLVM Passes documentation",
        "sections": [
            {"heading": "核心定义",
             "content": """""GCC/Clang优化级别：-O0(无优化,调试默认)、-O1(基本优化,减少代码体积和执行时间)、-O2(推荐的全面优化——包括所有无需做空间/速度权衡的优化,大多数项目的发布默认)、-O3(-O2+激进优化:循环展开/函数内联/SIMD向量化,可能增加代码体积)、-Os(针对体积优化——等价于-O2但禁用体积不利的优化)、-Ofast(-O3+非标准行为优化,包括-ffast-math、可能违反IEEE浮点)。"""""},
            {"heading": "LTO与PGO",
             "content": """""链接时优化(LTO/Link-Time Optimization)——-flto在链接时做整个程序的优化：跨文件的函数内联、死代码消除、常量传播。LTO将IR/字节码保留在.o文件中而非目标代码，链接时一次性全程序编译。反馈导向优化(PGO/Profile-Guided Optimization)：-fprofile-generate生成运行时profile,-fprofile-use用profile指导——优化分支预测、缓存对齐、函数排序(热函数靠近caller)。PGO可在-O2基础上提升10-30%性能。"""""},
            {"heading": "关键结论",
             "content": """""1. -O2是大多数项目的正确选择(-O3有时产生更慢的代码) 2. -O0不初始化局部变量(零填充) 3. -march=native为当前CPU优化(牺牲跨CPU可移植性) 4. volatile、inline asm阻止一些优化 5. 调试信息-g可与优化共存(但调试体验受影响)"""""},
            {"heading": "关联知识点",
             "content": """""[[C语言深入-链接器与ABI详解]] [[C语言深入-restrict限定符]] [[编译原理-程序优化]]"""""}
        ]
    },
    {
        "dir_name": "C语言深入",
        "file_stem": "sanitizer工具链",
        "title": "C语言-sanitizer工具链",
        "course": "C语言深入",
        "chapter": "调试与测试",
        "difficulty": "ADVANCED",
        "tags": ["C语言", "ASAN", "UBSAN", "TSAN", "sanitizer"],
        "aliases": ["AddressSanitizer", "UndefinedBehaviorSanitizer", "ThreadSanitizer"],
        "source": "LLVM Compiler documentation; Google Sanitizers Wiki; GCC Instrumentation Options",
        "sections": [
            {"heading": "核心定义",
             "content": """""Sanitizer是编译器提供的运行时检测工具。AddressSanitizer(ASAN, -fsanitize=address)——检测堆/栈/全局内存越界、use-after-free、double-free、内存泄漏(需要LSan)。使用shadow memory(影子内存)：每8字节应用内存有1字节影子内存记录访问状态。开销：~2x执行时间、~20%内存。UndefinedBehaviorSanitizer(UBSAN, -fsanitize=undefined)——检测有符号整数溢出、除零、空指针解引用、越界数组索引、非法类型转换。"""""},
            {"heading": "TSAN与其他工具",
             "content": """""ThreadSanitizer(TSAN, -fsanitize=thread)——检测数据竞争(data race)、互斥锁误用。基于happens-before关系分析。开销：~5-15x运行速度、~5-10x内存。MemorySanitizer(MSAN, -fsanitize=memory,仅Linux)——检测未初始化内存的读取(ASAN不检测这个问题)。LeakSanitizer(LSAN)——检测内存泄漏(通常与ASAN集成)。sanitizer可以同时启用多个但可能冲突(ASAN+TSAN不可同时)。GCC version 4.8+均支持。"""""},
            {"heading": "关键结论",
             "content": """""1. sanitizer是C/C++最重要的调试工具——覆盖各类内存错误 2. ASAN应与测试套件一起运行(detect heap buffer overflow) 3. UBSAN发现看似'work'但UB的代码(如shift>bitwidth) 4. TSAN可能检测到程序逻辑正确但仍存在的数据竞争 5. 生产环境非特殊场景不应使用sanitizer(安全与性能成本) 6. 可设置ASAN_OPTIONS=abort_on_error=1在检测到错误时崩溃"""""},
            {"heading": "关联知识点",
             "content": """""[[C语言深入-指针算术与内存模型]] [[C语言深入-编译优化选项]] [[软件工程-软件调试技术]]"""""}
        ]
    },
    {
        "dir_name": "C语言深入",
        "file_stem": "C与汇编混合编程",
        "title": "C语言-C与汇编混合编程",
        "course": "C语言深入",
        "chapter": "系统编程",
        "difficulty": "ADVANCED",
        "tags": ["C语言", "汇编", "调用约定", "栈帧", "ABI"],
        "aliases": ["C and Assembly", "Calling Convention", "Stack Frame"],
        "source": "x86-64 System V ABI; AMD64 Architecture Programmer's Manual; Agner Fog calling convention",
        "sections": [
            {"heading": "核心定义",
             "content": """""C与汇编混合编程基于ABI约定。x86-64 System V ABI规定：前6个整数/指针参数在rdi/rsi/rdx/rcx/r8/r9寄存器中传递，前8个SSE浮点参数在xmm0-7中，余下参数入栈(从右到左)。返回值：整数/指针在rax(64位内)和rdx(辅助)，浮点在xmm0。调用者保存(caller-saved)寄存器：rax/rcx/rdx/rsi/rdi/r8-r11(函数可随意修改)。被调用者保存(callee-saved)：rbx/rbp/r12-r15(函数必须恢复原值)。"""""},
            {"heading": "栈帧与入口",
             "content": """""函数入口前序(prologue)：push rbp; mov rbp, rsp; sub rsp, N——保存旧栈帧指针,建立新帧,分配局部变量空间。返回前序(epilogue): leave(=mov rsp,rbp; pop rbp); ret。红色区域(Red Zone)——x86-64 ABI中rsp以下128字节无需显式分配即可使用(信号处理器不被中断时)。确保栈在CALL前16字节对齐(ABI要求)。ret指令从栈弹出返回地址并跳转。可以通过asm在内联中手工构造栈帧。"""""},
            {"heading": "关键结论",
             "content": """""1. 从不假设调用约定的细节在不同编译器间一致(Windows x64使用不同的ABI) 2. 汇编代码中访问C全局变量通过符号引用(声明extern) 3. position-independent code(PIC)使用GOT间接引用全局符号 4. 混合编程需要完整的寄存器clobber列表 5. unwind tables(.eh_frame)实现C++异常处理穿越汇编代码"""""},
            {"heading": "关联知识点",
             "content": """""[[C语言深入-内联汇编]] [[C语言深入-链接器与ABI详解]] [[C语言深入-跨平台移植要点]]"""""}
        ]
    },
    {
        "dir_name": "C语言深入",
        "file_stem": "安全编码规范",
        "title": "C语言-安全编码规范",
        "course": "C语言深入",
        "chapter": "安全实践",
        "difficulty": "INTERMEDIATE",
        "tags": ["C语言", "安全编码", "MISRA C", "CERT C"],
        "aliases": ["MISRA C", "CERT C", "Secure Coding"],
        "source": "MISRA C:2012; CERT C Coding Standard; ISO/IEC TS 17961; SEI CERT C Wiki",
        "sections": [
            {"heading": "核心定义",
             "content": """""MISRA C(英国汽车行业软件可靠性协会)是汽车/航空/医疗等高安全领域的C语言子集规范。MISRA C:2012有143条规则(16条mandatory,127条advisory)——禁止动态内存分配(规则21.3)、禁止递归(规则17.2)、禁止goto(规则15.1)、char必须指定有符号/无符号(规则6.1)。CERT C(卡内基梅隆)覆盖更广的安全编码规则——共98条。ISO/IEC TS 17961定义了C的安全编码边界(缓冲区溢出、整数溢出、格式串漏洞等)。"""""},
            {"heading": "核心规则示例",
             "content": """""缓冲区保护：使用安全字符串函数(strncpy/strncat)。整数安全：CERT INT30-C(无符号整数回绕)/INT32-C(有符号溢出)/INT33-C(除零)。输入验证：CERT STR07-C(验证所有输入大小)。资源管理：CERT FIO42-C(fclose后置NULL)/MEM30-C(free后不重新引用)。并发：CERT CON33-C(避免数据竞争)。MISRA强制静态分析——所有违背都需证明动机。商业编译器(Green Hills、IAR)提供MISRA合规性检查。"""""},
            {"heading": "关键结论",
             "content": """""1. MISRA不是'写更安全的代码'而是'写绝对正确的代码' 2. CERT规则分 prioritized levels: L1(所有场景)/L2(大多数)/L3(建议) 3. 工具：Coverity、CodeSonar、Polyspace自动化检查 4. MISRA豁免需要code review记录和追溯 5. 使用-Wall -Wextra -Wconversion -Werror作为基础防线"""""},
            {"heading": "关联知识点",
             "content": """""[[C语言深入-指针算术与内存模型]] [[C语言深入-sanitizer工具链]] [[信息安全-代码安全审计]]"""""}
        ]
    },
    {
        "dir_name": "C语言深入",
        "file_stem": "C23新特性",
        "title": "C语言-C23新特性",
        "course": "C语言深入",
        "chapter": "语言标准",
        "difficulty": "BASIC",
        "tags": ["C语言", "C23", "新标准", "ISO C"],
        "aliases": ["C23", "ISO/IEC 9899:2024"],
        "source": "ISO/IEC 9899:2024 (C23); WG14 N3047 (working draft); cppreference C23",
        "sections": [
            {"heading": "核心定义",
             "content": """""C23(ISO/IEC 9899:2024)是C语言的最新标准，2024年发布。重大变化：1.)#embed——编译时嵌入二进制文件(替代xxd生成.c) 2.)nullptr常量(typeof(nullptr_t))替代NULL宏的类型安全空指针 3.)十进制浮点类型(Decimal32/64/128,符合IEEE 754-2008 DFP) 4.)typeof和typeof_unqual——从C++23实现移植的编译期类型提取 5.){}空初始化(统一初始化语法) 6.)auto类型推导(类似C++但更受限)。"""""},
            {"heading": "其他变化",
             "content": """""7.)constexpr——标记编译期可求值的对象(更接近C++语义) 8.)位属性——[[unsequenced]]/[[reproducible]]标记无副作用/可复现函数(帮助编译器优化) 9.)#elifdef/#elifndef——条件编译的便捷语法 10.)memset_explicit——保证不被优化消除的memset(安全擦除敏感数据) 11.)strdup/strndup成为标准库函数(之前仅POSIX) 12.)%b二进制printf格式 13.)带溢出检查的整数运算。C23废弃了K&R声明语法(老式函数声明)。"""""},
            {"heading": "关键结论",
             "content": """""1. #embed是C23最受欢迎的特性(内核/固件开发者期待已久) 2. nullptr消除了NULL可能的int歧义(int x=0;ptr=NULL后的f(x)错误) 3. typeof促进泛型编程(类型安全宏) 4. auto避免了难看的复杂类型声明 5. C23移除了一部分obsolete特性(如gets早已被C11移除) 6. 完全实现C23的编译器仍需要数年(GCC 14和Clang 17部分支持)"""""},
            {"heading": "关联知识点",
             "content": """""[[C语言深入-预处理器宏与条件编译]] [[C语言深入-编译优化选项]] [[程序设计语言原理-语言标准演进]]"""""}
        ]
    },
    {
        "dir_name": "C语言深入",
        "file_stem": "跨平台移植要点",
        "title": "C语言-跨平台移植要点",
        "course": "C语言深入",
        "chapter": "工程实践",
        "difficulty": "INTERMEDIATE",
        "tags": ["C语言", "跨平台", "endianness", "移植", "POSIX vs Win32"],
        "aliases": ["Cross-Platform C", "Endianness", "Portability"],
        "source": "APUE §2; CERT C MSC30-C; GCC Manual §2.1 Platform-specific Options; POSIX.1-2017",
        "sections": [
            {"heading": "核心定义",
             "content": """""C的跨平台挑战来源于未定义行为(UB)、实现定义行为(implementation-defined)和未指定行为(unspecified behavior)。移植性问题：1.)字节序(endianness)——大端整数的字节表示在小端系统完全不同(使用htons/htonl网络序API) 2.)数据类型大小——int可能16/32/64位(使用<stdint.h>的int32_t、size_t等固定宽度类型) 3.)对齐要求——结构体padding依赖于目标架构的ABI 4.)char的有符号性——ARM默认unsigned char, x86默认signed char, 比较前转换。"""""},
            {"heading": "POSIX vs Win32",
             "content": """""POSIX和Win32之间的差异是C移植的主要痛点：1.)文件路径——'/' vs '\\\\', Drive Letters 2.)fork——Windows无fork(使用CreateProcess) 3.)signal——完全不同的信号模型(Windows有结构化异常处理SEH) 4.)网络IO——BSD socket vs Winsock(WSAStartup/WSACleanup, closesocket vs close) 5.)动态库——dlopen/dlsym vs LoadLibrary/GetProcAddress。使用<windows.h>和<unistd.h>条件编译(#ifdef _WIN32)管理差异。"""""},
            {"heading": "关键结论",
             "content": """""1. 使用<stdint.h>和<inttypes.h>替代char/short/int/long 2. 字节序无关代码：位移操作而非直接位域访问 3. 从不假设struct布局(使用#pragma pack或align) 4. 用CMake的检测能力(test_big_endian, check_type_size) 5. CI应自动构建所有目标平台(至少x86_64 Windows/Linux/macOS)"""""},
            {"heading": "关联知识点",
             "content": """""[[C语言深入-编译优化选项]] [[C语言深入-链接器与ABI详解]] [[软件工程-持续集成与持续部署]]"""""}
        ]
    },
    {
        "dir_name": "C语言深入",
        "file_stem": "性能剖析工具",
        "title": "C语言-性能剖析工具",
        "course": "C语言深入",
        "chapter": "性能优化",
        "difficulty": "BASIC",
        "tags": ["C语言", "profiling", "gprof", "perf", "valgrind"],
        "aliases": ["C Profiling", "gprof", "perf", "valgrind/callgrind"],
        "source": "GNU gprof manual; Linux perf wiki; Valgrind User Manual; Intel VTune文档",
        "sections": [
            {"heading": "核心定义",
             "content": """""性能剖析(profiling)是定位程序热点(hot spot)的技术。gprof(GNU profiler)——编译期插入计数代码(-pg)，运行时采样，gprof生成函数调用图。perf(Linux perf_events)——基于CPU硬件性能计数器的采样profiler，perf record录制事件，perf report/annotate查看源码级热点。Valgrind/Callgrind——缓存和分支预测仿真(模拟CPU行为)，KCachegrind图形化分析。Intel VTune——商业级性能分析(可定位微架构后端停顿)。"""""},
            {"heading": "工具选择与原理",
             "content": """""采样vs插桩：采样(perf)低开销(<5%)但统计精度有限；插桩(gprof)精确但有函数调用开销。perf stat查看基本CPU事件(指令数、缓存未命中、分支预测失败、IPC)。perf top实时查看热点。valgrind --tool=callgrind提供缓存模拟(比硬件计数更详细信息，但慢约20x)。火焰图(FlameGraph, Brendan Gregg)可视化调用栈——每个框宽度代表CPU占比。热点分析后使用微基准测试(microbenchmark)验证优化。"""""},
            {"heading": "关键结论",
             "content": """""1. 先在perf stat上看缓存命中率/分支预测/指令数——硬件事件是指标基础 2. perf annotate将事件映射到汇编代码 3. callgrind的I1/D1/LL缓存模拟诊断缓存问题(比硬件计数器更稳定) 4. Cachegrind annotate显示每一行的缓存未命中数 5. 不同的剖析工具互补——单一工具不足以定位所有性能问题"""""},
            {"heading": "关联知识点",
             "content": """""[[C语言深入-编译优化选项]] [[C语言深入-sanitizer工具链]] [[计算机组成原理-CPU缓存与局部性原理]]"""""}
        ]
    },

    # ═══════════════════════════════════════════════════════════════
    # Java深入 — 13 additional topics (to reach 35 total)
    # ═══════════════════════════════════════════════════════════════
    {
        "dir_name": "Java深入",
        "file_stem": "泛型擦除与类型安全",
        "title": "Java深入-泛型擦除与类型安全",
        "course": "Java深入",
        "chapter": "类型系统",
        "difficulty": "INTERMEDIATE",
        "tags": ["Java", "泛型", "类型擦除", "桥方法", "类型安全"],
        "aliases": ["Java Type Erasure", "Bridge Methods", "Generics"],
        "source": "Java Language Specification §4.6 Type Erasure; Bloch《Effective Java》Item 26-28; Angelika Langer Java Generics FAQ",
        "sections": [
            {"heading": "核心定义", "content": "Java泛型通过类型擦除(type erasure)在编译期实现：编译器将泛型类型参数替换为其边界(默认Object)，在需要类型安全的地方插入checkcast。这意味着ArrayList<String>和ArrayList<Integer>在运行时是同一种类型(Class对象相同)。桥方法(bridge method)是编译器为协变返回类型和方法覆盖自动生成的合成方法。类型擦除的设计初衷是与Java 1.4及以前的非泛型代码保持向后兼容。"},
            {"heading": "PECS原则", "content": "PECS(Producer extends, Consumer super)是Java泛型通配符的助记：频繁读取的集合用<? extends T>(作为生产者，能安全取出类型T但只能写入null)；频繁写入的集合用<? super T>(作为消费者，能安全写入T但取出只能得到Object)。通配符捕获(wildcard capture)在泛型方法调用时编译器赋值特定但不可见的类型变量。List<?>不能写入(除了null——类型安全)。"},
            {"heading": "关键结论", "content": "1. instanceof不能检查参数化类型(instanceof ArrayList<String>编译错误) 2. 不能创建泛型数组(new T[10]或new ArrayList<String>[10]) 3. 不要混用原始类型和参数化类型(raw type warning) 4. 堆污染(heap pollution)由可变参数泛型方法产生(@SafeVarargs注解) 5. 类型擦除也意味着不能重载泛型参数仅不同的方法"},
            {"heading": "关联知识点", "content": "[[Java深入-JVM架构与字节码]] [[Java深入-反射与动态代理]] [[Go语言-泛型与类型约束]]"}
        ]
    },
    {
        "dir_name": "Java深入",
        "file_stem": "注解处理与APT",
        "title": "Java深入-注解处理与APT",
        "course": "Java深入",
        "chapter": "元编程",
        "difficulty": "INTERMEDIATE",
        "tags": ["Java", "注解", "APT", "Lombok", "编译期处理"],
        "aliases": ["Annotation Processing", "APT", "Lombok"],
        "source": "JSR 269 (Pluggable Annotation Processing API); Lombok官方文档; Java注解处理器指南",
        "sections": [
            {"heading": "核心定义", "content": "Java注解处理器(Annotation Processing Tool, APT)是在javac编译期运行的插件。通过实现javax.annotation.processing.AbstractProcessor，在编译的特定轮次(round)扫描注解生成额外的Java源文件。处理器通过ServiceLoader注册(META-INF/services/javax.annotation.processing.Processor)。lombok走的是非标准API(通过ECJ/javac内部API直接修改AST，允许修改已有类)。"},
            {"heading": "实战场景", "content": "典型APT应用：1.)Dagger 2(编译期依赖注入) 2.)AutoValue/Immutables(自动生成value type) 3.)MapStruct(基于接口的映射代码生成) 4.)Room(编译期SQL验证) 5.)Butter Knife(R.id绑定，已被ViewBinding取代)。Annotation不能修改已有代码——Lombok通过侵入编译器内部实现(非标准)。APT生成的源码在.generated_sources目录，javac自动编译它们。"},
            {"heading": "关键结论", "content": "1. APT仅能生成新文件——不能修改现有类(除Lombok的hack) 2. 处理轮次(delta rounds)限制——第n轮只能看到第n-1轮及之前生成的文件 3. processingEnv.getFiler()创建源文件，processingEnv.getMessager()报告错误 4. @SupportedAnnotationTypes和@SupportedSourceVersion标注处理器 5. Gradle/Kotlin KAPT将注解处理适配到Kotlin编译"},
            {"heading": "关联知识点", "content": "[[Java深入-反射与动态代理]] [[Java深入-设计模式实战]] [[编译原理-语法树与中间表示]]"}
        ]
    },
    {
        "dir_name": "Java深入",
        "file_stem": "反射与动态代理",
        "title": "Java深入-反射与动态代理",
        "course": "Java深入",
        "chapter": "元编程",
        "difficulty": "ADVANCED",
        "tags": ["Java", "反射", "Proxy", "InvocationHandler", "动态代理"],
        "aliases": ["Java Reflection", "Dynamic Proxy", "InvocationHandler"],
        "source": "Java官方文档 java.lang.reflect; Bloch《Effective Java》Item 65; Oracle反射教程",
        "sections": [
            {"heading": "核心定义", "content": "Java反射(reflection)允许运行时检查类、接口、字段、方法。核心类：Class<?>(类符号)、Field(字段——get/set、setAccessible绕过可见性)、Method(方法——invoke调用)、Constructor(构造器——newInstance实例化)。反射破坏封装和类型安全(编译期检查变为运行时检查)。动态代理(Proxy.newProxyInstance)在运行时创建实现接口的匿名类——所有调用被委派到InvocationHandler.invoke方法。"},
            {"heading": "内部机制", "content": "动态代理基于生成的$Proxy类(在native层通过ProxyGenerator生成字节码并定义类)。每个代理对象持有InvocationHandler引用,k通过方法签名分派。CGLIB(Code Generation Library)是更高性能的代理框架——通过生成目标类的子类(而非接口)实现。Spring AOP默认使用JDK动态代理(接口)或CGLIB(类)。MethodHandle(Java 7+的invokedynamic实现)比反射更快但更底层(更接近字节码级别)。"},
            {"heading": "关键结论", "content": "1. 反射性能较差(~10-50x slower)——MethodHandle是更好的替代(invokedynamic) 2. setAccessible需谨慎——绕过模块系统限制(Java 9+的--add-opens需要) 3. 反射不要在热路径使用 4. 动态代理仅支持接口代理(CGLIB用ASM直接操作字节码) 5. 反射在JDK内部使用受限(强封装——add-opens才能访问)"},
            {"heading": "关联知识点", "content": "[[Java深入-泛型擦除与类型安全]] [[Java深入-注解处理与APT]] [[Java深入-JVM架构与字节码]]"}
        ]
    },
    {
        "dir_name": "Java深入",
        "file_stem": "模块系统JPMS",
        "title": "Java深入-模块系统JPMS",
        "course": "Java深入",
        "chapter": "语言特性",
        "difficulty": "INTERMEDIATE",
        "tags": ["Java", "JPMS", "模块", "Jigsaw", "module-info"],
        "aliases": ["Java Platform Module System", "Project Jigsaw", "module-info"],
        "source": "JSR 376 (Java Platform Module System); Oracle: Java 9 Modularity; Nicolai Parlog《The Java Module System》",
        "sections": [
            {"heading": "核心定义", "content": "Java模块系统(JPMS, Project Jigsaw, Java 9+)通过模块描述文件(module-info.java)定义模块：module com.example { requires java.sql; exports com.example.api; opens com.example.dto to jackson.databind; provides Service with Impl; uses Service; }。requires声明依赖，exports公开包(默认所有包隐藏)，opens允许深度反射访问。模块路径(module path)取代classpath的扁平可见性——通过强封装实现可靠性。"},
            {"heading": "模块层次", "content": "模块分为：命名模块(named module——有module-info)、自动模块(automatic module——无module-info的Jar，推导名源自Manifest或文件名)、未命名模块(unnamed module——classpath上的所有类,可访问所有命名模块但被所有模块反向访问)。JDK本身被拆分成约70个模块(java.base是根模块——所有模块自动requires它)。模块化增强了安全性(内部API不再可访问除非opens)。"},
            {"heading": "关键结论", "content": "1. java.base导出java.lang/java.util等基本包——隐式requires 2. requires static表示编译时依赖(运行时可选——类似Maven optional) 3. requires transitive传递依赖到使用方(类似Maven compile scope) 4. --add-exports/--add-opens命令行参数在模块系统边界打洞 5. 遗留代码可逐步迁移——先放在classpath上(未命名模块)"},
            {"heading": "关联知识点", "content": "[[Java深入-反射与动态代理]] [[Java深入-类加载器与双亲委派]] [[软件工程-软件架构设计]]"}
        ]
    },
    {
        "dir_name": "Java深入",
        "file_stem": "Stream与并发流",
        "title": "Java深入-Stream与并发流",
        "course": "Java深入",
        "chapter": "函数式编程",
        "difficulty": "INTERMEDIATE",
        "tags": ["Java", "Stream", "parallelStream", "函数式编程", "并行"],
        "aliases": ["Java Stream API", "Parallel Streams", "Stream Pipeline"],
        "source": "Java官方文档 java.util.stream; Urma et al.《Modern Java in Action》; Oracle Stream教程",
        "sections": [
            {"heading": "核心定义", "content": "Stream API(Java 8)提供声明式集合处理。核心结构：源(source) → 0+中间操作(intermediate,惰性——filter/map/sorted/distinct) → 终端操作(terminal——collect/forEach/reduce/count)。Stream不存储数据(仅是计算视图),不可重用(一个Stream只能消费一次)。中间操作是惰性的——在终端操作触发后才执行。Stream并行度默认是ForkJoinPool.commonPool()线程数(availableProcessors - 1)。"},
            {"heading": "并行流陷阱", "content": "parallelStream使用Fork/Join框架自动分解工作。但并行不一定更快——影响因素:数据大小(数据太少,分解开销>并行收益)、装箱(原始类型流IntStream/LongStream优于Stream<Integer>)、collect的可合并性(ArrayList合并需复制,ConcatCollectors更差)。状态中间操作(sorted/distinct)在并行流中开销显著。并行流不应在共享的ForkJoinPool中被阻塞(IO操作)——应使用自定义executor。"},
            {"heading": "关键结论", "content": "1. 永远在并行流和非并行流版本间基准对比 2. 原始类型流(IntStream/DoubleStream)和collect更适合并行 3. 不要在并行流中使用非线程安全的累加器(改用collect) 4. forEachOrdered保证顺序但牺牲并行度 5. Spliterator特性(ORDERED/SIZED/SUBSIZED)影响并行拆分效率 6. reduce是有偏关联操作时并行结果非确定"},
            {"heading": "关联知识点", "content": "[[Java深入-泛型擦除与类型安全]] [[Rust语言-迭代器与组合器]] [[算法设计与分析-分治与递归]]"}
        ]
    },
    {
        "dir_name": "Java深入",
        "file_stem": "NIO与零拷贝",
        "title": "Java深入-NIO与零拷贝",
        "course": "Java深入",
        "chapter": "IO与网络",
        "difficulty": "ADVANCED",
        "tags": ["Java", "NIO", "零拷贝", "ByteBuffer", "FileChannel"],
        "aliases": ["Java NIO", "Zero Copy", "sendfile"],
        "source": "Java NIO官方文档; Ron Hitchens《Java NIO》; Linux sendfile(2) man page",
        "sections": [
            {"heading": "核心定义", "content": "Java NIO(java.nio)提供非阻塞IO基础。核心概念：Channel(双向通信通道——FileChannel/SocketChannel/ServerSocketChannel)、Buffer(数据容器——ByteBuffer/CharBuffer等)、Selector(多路复用——单线程管理多个Channel)。Direct Buffer分配在native堆外内存(allocateDirect())——避免JVM堆到native堆的拷贝，适合长生命周期的IO缓冲。ByteBuffer维护position/limit/capacity三指针和flip/clear/compact操作。"},
            {"heading": "零拷贝与sendfile", "content": "Java的零拷贝通过FileChannel.transferTo/transferFrom实现——底层调用sendfile()系统调用(2.6.33后为splice)。数据从page cache直接传输到socket buffer而无需经过用户空间(真正的0次CPU拷贝在支持DMA scatter-gather的网卡下)。Netty使用CompositeByteBuf和FileRegion实现零拷贝。ByteBuffer.slice()创建共享底层数据的视图(零拷贝子Buffer)。MappedByteBuffer实现内存映射文件(map-reduce read——mmap syscall)。"},
            {"heading": "关键结论", "content": "1. Direct Buffer分配/回收成本高——使用对象池复用 2. transferTo一次最多传输2GB(需循环) 3. MappedByteBuffer不受GC控制——通过Cleaner手动释放 4. NIO在连接数>1000时显著优于传统BIO(thread-per-connection) 5. Selector实现因操作系统而异(epoll在Linux,kqueue在macOS/BSD)"},
            {"heading": "关联知识点", "content": "[[Java深入-JVM架构与字节码]] [[计算机网络-epoll与I/O多路复用]] [[Go语言-netpoll与网络模型]]"}
        ]
    },
    {
        "dir_name": "Java深入",
        "file_stem": "类加载器与双亲委派",
        "title": "Java深入-类加载器与双亲委派",
        "course": "Java深入",
        "chapter": "JVM",
        "difficulty": "ADVANCED",
        "tags": ["Java", "ClassLoader", "双亲委派", "类加载", "JVM"],
        "aliases": ["ClassLoader Hierarchy", "Parent Delegation", "Class Loading"],
        "source": "Java虚拟机规范 §5.3; 周志明《深入理解Java虚拟机》Ch 7; Oracle: ClassLoader文档",
        "sections": [
            {"heading": "核心定义", "content": "Java类加载器按层次组织为双亲委派模型(Parents Delegation Model)——加载类的请求沿父加载器链向上传递。标准三层次：Bootstrap ClassLoader(C++实现,加载rt.jar/java.base)、Extension/Platform ClassLoader(加载jre/lib/ext或java.platform模块)、Application ClassLoader(加载classpath)。当一个类加载器接收加载请求时，先委托父加载器(避免重复加载JVM核心类)，父无法加载时才自己尝试。"},
            {"heading": "破坏双亲委派", "content": "双亲委派被破坏的经典案例：1.)线程上下文类加载器(Thread Context ClassLoader)——SPI场景中ServiceLoader需要访问应用类(先在Ext中无法找到) 2.)Tomcat的WebappClassLoader(先尝试自己从WEB-INF加载，隔离不同webapp的类) 3.)OSGi模块系统(网状委派图而非树)。findLoadedClass检查已加载类——每个类由其全限定名+定义它的ClassLoader唯一确定(同一字节码被两个ClassLoader加载时产生两个不同的类,导致ClassCastException)。"},
            {"heading": "关键结论", "content": "1. defineClass将字节码转为Class<?>实例(在方法区和运行时常量池中分配) 2. 类加载触发时机:new/反射/父类/main(加载+链接+初始化=类的完整生命周期) 3. 类加载阶段有5个:加载→验证→准备→解析→初始化→使用→卸载 4. 类不会再次初始化——初始化锁保证线程安全 5. 自定义类加载器的典型场景:热部署、字节码加密、从非classpath源加载"},
            {"heading": "关联知识点", "content": "[[Java深入-JVM架构与字节码]] [[Java深入-JIT编译与热点编译]] [[Java深入-模块系统JPMS]]"}
        ]
    },
    {
        "dir_name": "Java深入",
        "file_stem": "JIT编译与热点",
        "title": "Java深入-JIT编译与热点",
        "course": "Java深入",
        "chapter": "JVM",
        "difficulty": "ADVANCED",
        "tags": ["Java", "JIT", "HotSpot", "C1/C2", "编译优化"],
        "aliases": ["JIT Compilation", "HotSpot", "Tiered Compilation"],
        "source": "OpenJDK HotSpot Runtime documentation; Oracle: Java Just-In-Time compilation; 周志明《深入理解Java虚拟机》Ch 11",
        "sections": [
            {"heading": "核心定义", "content": "Java程序从解释执行开始，HotSpot JVM监控热点代码并JIT编译为原生代码。分层编译(tiered compilation)有5个级别——Level 0(解释器)、Level 1-3(C1编译器,带profiling)、Level 4(C2编译器,激进优化)。编译触发基于两个计数器：方法调用计数器+回边计数器(循环迭代)。热点代码经过profiling积累类型分布和分支概率数据后再被C2编译(Profile-Guided Optimization)。"},
            {"heading": "C1 vs C2编译器", "content": "C1(Client Compiler)——快速编译，较少激进优化(简单内联、寄存器分配、基本窥孔优化)，较慢的生成代码但快速的编译时间——适合客户端应用。C2(Server Compiler)——缓慢编译，更全面的优化：代数简化、逃逸分析(栈上分配+同步消除+标量替换)、虚方法调用去虚拟化(CHA, Class Hierarchy Analysis)、循环展开/向量化、范围检查消除。Graal(GraalVM的JIT, Java编写)正逐渐替代C2。"},
            {"heading": "关键结论", "content": "1. 预热效应(warm-up)——JVM启动后前N次调用慢(解释/JIT编译中)但稳态极快 2. 去优化(deoptimization)——当C2基于不正确的profiling做出的优化假设被打破时回退到解释 3. -XX:+PrintCompilation查看编译事件 4. -XX:CompileThreshold调整触发阈值 5. OSR(On-Stack Replacement)在循环中途将解释的代码替换为编译的代码 6. 内联是最重要的JIT优化(消除调用开销并启用更多优化)"},
            {"heading": "关联知识点", "content": "[[Java深入-JVM架构与字节码]] [[Java深入-类加载器与双亲委派]] [[编译原理-代码优化]]"}
        ]
    },
    {
        "dir_name": "Java深入",
        "file_stem": "设计模式实战",
        "title": "Java深入-设计模式实战",
        "course": "Java深入",
        "chapter": "软件设计",
        "difficulty": "INTERMEDIATE",
        "tags": ["Java", "设计模式", "GoF", "Spring", "实践"],
        "aliases": ["Design Patterns in Java", "GoF Patterns", "Java Design Patterns"],
        "source": "Gamma et al.《Design Patterns》(GoF); Kerievsky《Refactoring to Patterns》; Spring Framework源码",
        "sections": [
            {"heading": "核心定义", "content": "设计模式是常见设计问题的可重用解决方案。GoF的23个经典模式分三类：创建型(Singleton/Factory/Builder/Prototype)、结构型(Adapter/Decorator/Proxy/Facade/Composite/Bridge)、行为型(Observer/Strategy/Command/Template Method/Chain of Responsibility)。Java生态中的天然体现——Iterator模式被内置于foreach和Iterable接口、Observer模式(已被淘汰——用响应式流代替)被内置于PropertyChangeListener。"},
            {"heading": "模式在Java8+的演进", "content": "经典模式的Java 8+替代：Strategy模式用@FunctionalInterface(lambda)替代策略类(Comparator/IntPredicate)；Command模式可用Runnable/method reference；Observer模式已被Flow API(java.util.concurrent.Flow)和Reactive Streams取代；Decorator模式在java.io中大量使用(BufferedInputStream包装FileInputStream)；Template Method可用于接口的default方法实现骨架算法；Factory模式可以使用Supplier<T>传递构造逻辑。"},
            {"heading": "关键结论", "content": "1. 不要为模式而模式——YAGNI(You Aren't Gonna Need It) 2. 适配器模式是集成遗留代码与旧API的主力 3. Builder模式在受控对象构造中仍无可替代(Lombok @Builder) 4. Spring框架内部大量使用Template Method和Proxy模式 5. Singleton有严重问题(全局状态、测试困难)——应使用依赖注入替代"},
            {"heading": "关联知识点", "content": "[[Java深入-注解处理与APT]] [[Java深入-反射与动态代理]] [[软件工程-设计模式]]"}
        ]
    },
    {
        "dir_name": "Java深入",
        "file_stem": "安全与沙箱",
        "title": "Java深入-安全与沙箱",
        "course": "Java深入",
        "chapter": "安全",
        "difficulty": "INTERMEDIATE",
        "tags": ["Java", "沙箱", "SecurityManager", "AccessController", "安全管理"],
        "aliases": ["Java Security", "Sandbox", "SecurityManager"],
        "source": "Java安全架构文档; Oracle Java安全指南; Java Cryptography Architecture(JCA) Reference Guide",
        "sections": [
            {"heading": "核心定义", "content": "Java安全模型建立在语言级别的安全之上(内存安全、类型安全、数组边界检查)——消除了C典型的缓冲区溢出漏洞。应用级安全通过Permission类层次和SecurityManager执行：SecurityManager.checkPermission(perm)在try块中被调用——若无授权则抛出AccessControlException。策略文件(.policy)将代码源(codebase+签名证书)映射到权限集。Java沙箱曾允许浏览器安全运行Applet(已弃用)但基本原理仍在Java EE容器和插件系统中使用。"},
            {"heading": "现状与替代", "content": "SecurityManager在Java 17+已被标记为废弃(for removal)——现代Java应用更多依赖容器/OS级别的隔离。替代安全实践：1.)模块系统的强封装(防止反射访问内部) 2.)ProcessBuilder而非Runtime.exec() 3.)Path API安全文件访问 4.)Security Exception的精细处理和记录 5.)JCA/JCE用于加密(AES-GCM)和PKI 6.)OWASP对Java的安全建议——防范注入/XXE/反序列化漏洞。序列化是Java最大的安全弱点(任意代码执行)。"},
            {"heading": "关键结论", "content": "1. SecurityManager将在未来JDK版本移除——不应用于新项目 2. 反序列化不安全——使用JSON/Protobuf替代，或使用validateObject 3. AccessController.doPrivileged在旧代码中用于提升权限 4. 永远不应信任外部提供的序列化数据(JEP 290: serialization filter) 5. Spring Security提供认证(authentication)+授权(authorization)+CSRF防护"},
            {"heading": "关联知识点", "content": "[[Java深入-模块系统JPMS]] [[信息安全-Web安全与OWASP Top 10]] [[软件工程-安全开发生命周期]]"}
        ]
    },
    {
        "dir_name": "Java深入",
        "file_stem": "单元测试与Mock",
        "title": "Java深入-单元测试与Mock",
        "course": "Java深入",
        "chapter": "工程质量",
        "difficulty": "BASIC",
        "tags": ["Java", "JUnit", "Mockito", "单元测试", "TDD"],
        "aliases": ["JUnit", "Mockito", "Java Testing"],
        "source": "JUnit 5 User Guide; Mockito官方文档; Meszaros《xUnit Test Patterns》",
        "sections": [
            {"heading": "核心定义", "content": "JUnit 5是Java主流测试框架。核心注解：@Test标记测试方法、@BeforeEach/@AfterEach(每个测试前后)、@BeforeAll/@AfterAll(所有测试前后,必须static)、@DisplayName(人类可读的测试名)、@ParameterizedTest(参数化测试配合@ValueSource/@CsvSource)、@RepeatedTest(重复测试)。断言：assertEquals/assertTrue/assertThrows/assertTimeout/asserAll。Mockito提供模拟(mocking)对象：Mockito.mock()创建伪对象,when().thenReturn()预设行为,verify()检查调用。"},
            {"heading": "测试最佳实践", "content": "FIRST原则：Fast(快速)、Independent(独立)、Repeatable(可重复)、Self-validating(自验证)、Timely(及时编写)。测试金字塔：单元测试(大量,快,不依赖外部)→集成测试(中等,依赖DB/IO)→端到端测试(少量,全链路,慢脆)。单元测试验证行为而非方法——测试公共API的逻辑而非每个setter。测试命名：shouldExpectedBehavior_whenCondition()。mock只在被测试单元有外部协作者时使用——mock自己类型的测试是反模式。"},
            {"heading": "关键结论", "content": "1. 不要mock你不拥有的类型(用test double的wrapper或fake) 2. ArgumentCaptor在需要验证传递给mock的参数中的值 3. thenReturn vs thenAnswer——后者提供动态响应(根据输入计算返回值) 4. @InjectMocks自动注入mock依赖(Spring的@MockBean替代) 5. 每个测试只验证一个行为(单一断言虽好但非铁律——简洁>绝对) 6. 测试覆盖率(行覆盖率/分支覆盖率)达到80%合格"},            {"heading": "关联知识点", "content": "[[Java深入-设计模式实战]] [[Go语言-测试与基准测试]] [[软件工程-软件测试策略]]"}        ]    },    {        "dir_name": "Java深入",        "file_stem": "构建工具Maven-Gradle",        "title": "Java深入-构建工具(Maven/Gradle)",        "course": "Java深入",        "chapter": "工程构建",        "difficulty": "BASIC",        "tags": ["Java", "Maven", "Gradle", "构建", "依赖管理"],        "aliases": ["Maven", "Gradle", "Build Lifecycle"],        "source": "Maven官方文档; Gradle User Manual; Sonatype《Maven: The Complete Reference》",        "sections": [            {"heading": "核心定义", "content": "Maven使用声明式XML(pom.xml)描述项目。核心概念：坐标(GAV——groupId/artifactId/version唯一定位一个artifact)、依赖范围(compile/runtime/test/provided/system)、生命周期(clean/default/site——由插件目标goal绑定到phase执行)、传递依赖(nearest wins——基于版本冲突的依赖仲裁)。Maven Central Repository是默认构件库。settings.xml配置仓库认证、代理、镜像。"},            {"heading": "Maven vs Gradle", "content": "Gradle使用Groovy/Kotlin DSL构建脚本(build.gradle/build.gradle.kts)，提供灵活性和性能。Gradle的构建缓存(up-to-date checks)和增量构建显著超越Maven。依赖解析使用丰富版本声明(动态版本1.+、版本范围[1.0,2.0))。Maven的BOM(Bill of Materials)在dependencyManagement中管理版本(Spring Boot Starter Parent典型)。Gradle的多项目构建(settings.gradle的include)管理大型项目。"},            {"heading": "关键结论", "content": "1. maven-enforcer-plugin强制执行依赖收敛(依赖版本冲突检查) 2. 永远不要将credentials放在pom.xml(settings.xml或环境变量) 3. Maven Wrapper(mvnw)和Gradle Wrapper(gradlew)确保CI和开发环境一致性 4. Maven的scope provided用于容器提供的依赖(servlet-api) 5. 发布到Maven Central需要PGP签名、Javadoc、Sources Jar"},            {"heading": "关联知识点", "content": "[[Java深入-模块系统JPMS]] [[Go语言-Module与依赖管理]] [[软件工程-持续集成与持续部署]]"}        ]    },    {        "dir_name": "Java深入",        "file_stem": "日志框架SLF4J-Logback",        "title": "Java深入-日志框架(SLF4J/Logback)",        "course": "Java深入",        "chapter": "工程质量",        "difficulty": "BASIC",        "tags": ["Java", "SLF4J", "Logback", "MDC", "日志"],        "aliases": ["SLF4J", "Logback", "MDC", "Java Logging"],        "source": "SLF4J官方手册; Logback Manual; Ceki Gulcu《Logback 手册》",        "sections": [            {"heading": "核心定义", "content": "SLF4J(Simple Logging Facade for Java)是日志门面，提供统一的日志API而允许在部署时替换底层实现(Logback,Log4j2,JDK Logging)。LoggerFactory.getLogger()获取Logger实例。日志级别从高到低：ERROR(系统错误), WARN(警告), INFO(关键业务流程), DEBUG(诊断信息), TRACE(极细粒度调试)。Logger hierarchy由名称决定('com.example'是'com.example.Service'的父)——父级的level和appender影响子级。"},            {"heading": "MDC与结构化日志", "content": "MDC(Mapped Diagnostic Context)在当前线程的日志上下文中存储键值对(TraceId/UserId/SessionId)——所有日志语句自动携带这些字段。使用模式：MDC.put('traceId', uuid); try {...} finally { MDC.remove('traceId'); }。Logback的PatternLayout中的%X{traceId}引用MDC字段。异步日志(Appender通过AsyncAppender或Logstash appender直接发送到Kafka/Elasticsearch)消除IO等待。结构化日志(JSON格式——LogstashEncoder)使日志在ELK/Grafana中可查询。"},            {"heading": "关键结论", "content": "1. 永远不要直接使用底层实现(log4j)——永远通过SLF4J facade 2. 参数化日志——logger.info('user {} login', username)替代字符串拼接(防JIT后仍评估——防性能损失) 3. 生产环境INFO级别,(重要服务组件的日志级别可调整为DEBUG) 4. JUL-to-SLF4J桥接(jul-to-slf4j)统一整个依赖树的日志 5. Log4Shell(CVE-2021-44228)事件警示——保持日志库最新极重要"},            {"heading": "关联知识点", "content": "[[Java深入-单元测试与Mock]] [[信息安全-Web安全与OWASP Top 10]] [[软件工程-可观测性]]"}        ]    },

    # ═══════════════════════════════════════════════════════════════
    # 操作系统 — 5 supplemental topics
    # ═══════════════════════════════════════════════════════════════
    {
        "dir_name": "操作系统",
        "file_stem": "CPU亲和性与NUMA",
        "title": "CPU亲和性与NUMA",
        "course": "操作系统",
        "chapter": "CPU调度与架构",
        "difficulty": "ADVANCED",
        "tags": ["操作系统", "CPU亲和性", "NUMA", "调度", "内存架构"],
        "aliases": ["CPU Affinity", "NUMA", "Non-Uniform Memory Access"],
        "source": "Linux kernel documentation: cpusets; Drepper《What Every Programmer Should Know About Memory》; ACPI NUMA specification",
        "sections": [
            {"heading": "核心定义", "content": "CPU亲和性(CPU affinity)指进程/线程绑定到特定CPU核心的机制。Linux通过taskset命令或sched_setaffinity()系统调用设置。硬亲和性由用户指定，软亲和性由调度器维护(尽量让进程留在同一CPU以利用缓存热数据)。NUMA(Non-Uniform Memory Access)在大规模多处理器系统中，每个CPU有自己的本地内存——本地内存访问快(1x)，远程内存访问慢(1.5-3x)。NUMA-aware调度目标是让进程使用本地内存和执行CPU。"},
            {"heading": "NUMA实战", "content": "Linux的NUMA感知通过numactl查看和设置。libnuma提供API控制内存分配策略(MPOL_BIND绑定到特定节点、MPOL_INTERLEAVE均匀分布在节点之间、MPOL_PREFERRED偏好节点但不强制)。numa_alloc_onnode分配特定节点上的内存。典型的NUMA调度策略：mbind将线程的内存页面迁移到本地节点。大型数据库(PostgreSQL/Oracle)和Java GC(ZGC/Shenandoah)对NUMA友好以实现更好的性能。"},
            {"heading": "关键结论", "content": "1. 双socket服务器的NUMA效果显著——需明确管理内存和CPU亲和 2. 宿主线程和目标内存必须位于同一NUMA节点最优 3. 虚拟化环境中NUMA拓扑映射复杂(vNUMA) 4. Intel的SAP(Sub-NUMA Clustering)在socket内创建NUMA域 5. /proc/PID/numa_maps展示每个VMA的NUMA分布"},
            {"heading": "关联知识点", "content": "[[操作系统-多级反馈队列调度MLFQ]] [[操作系统-虚拟内存与TLB]] [[计算机组成原理-多核处理器架构]]"}
        ]
    },
    {
        "dir_name": "操作系统",
        "file_stem": "CFS调度器实现细节",
        "title": "CFS调度器实现细节",
        "course": "操作系统",
        "chapter": "进程调度",
        "difficulty": "ADVANCED",
        "tags": ["操作系统", "CFS", "调度器", "红黑树", "vruntime"],
        "aliases": ["Completely Fair Scheduler", "CFS", "vruntime"],
        "source": "Linux kernel sched/fair.c源码; Robert Love《Linux Kernel Development》Ch 4; Linux kernel CFS documentation",
        "sections": [
            {"heading": "核心定义", "content": "CFS(Completely Fair Scheduler, Linux 2.6.23+)是Linux的默认调度器。核心思想：每个任务获得虚拟运行时间(vruntime)与nice权重的比例时间。CFS使用红黑树(red-black tree)组织可运行任务——键值为vruntime(最小vruntime的任务在最左叶节点)。调度器选择最左节点执行。vruntime增量=实际运行时间×(NICE_0_LOAD/权重)——nice值越低(优先级高)权重越高,因此vruntime增长更慢从而获得更多CPU时间。"},
            {"heading": "实现机制", "content": "CFS调度粒度和延迟：sched_min_granularity_ns(最小调度粒度——避免过于频繁切换)、sched_latency_ns(目标调度延迟——一个调度周期内所有可运行任务至少执行一次)。cgroup的CFS带宽控制通过cpu.cfs_quota_us/cpu.cfs_period_us限制CPU使用率。cfs_rq(每个CPU的CFS运行队列)跟踪运行统计数据。load_tracking(PELT——Per-Entity Load Tracking)将任务对CPU load的历史贡献按衰减指数计算以指导负载均衡。"},
            {"heading": "关键结论", "content": "1. CFS是无时钟的(tickless)工作模式——动态计算时间片而非固定HZ 2. 新唤醒的任务vruntime设置为min(min_vruntime, se->vruntime - sysctl_sched_latency)以快速获得CPU(交互式任务) 3. CFS的负载均衡数个子任务在每个核心上执行(load_balance/pick_next_task) 4. Linux 6.6引入了EEVDF替代CFS(Earliest Eligible Virtual Deadline First)——更好的延迟保证"},
            {"heading": "关联知识点", "content": "[[操作系统-多级反馈队列调度MLFQ]] [[操作系统-实时调度算法RMS与EDF]] [[操作系统-CPU亲和性与NUMA]]"}
        ]
    },
    {
        "dir_name": "操作系统",
        "file_stem": "eBPF内核虚拟机",
        "title": "eBPF内核虚拟机",
        "course": "操作系统",
        "chapter": "内核扩展",
        "difficulty": "ADVANCED",
        "tags": ["操作系统", "eBPF", "内核", "虚拟机", "可观测性"],
        "aliases": ["Extended Berkeley Packet Filter", "BPF", "Kernel VM"],
        "source": "Linux kernel Documentation/bpf; Brendan Gregg《BPF Performance Tools》; Cilium eBPF文档",
        "sections": [
            {"heading": "核心定义", "content": "eBPF(extended Berkeley Packet Filter)是Linux内核中的通用虚拟机，允许用户空间程序在内核态安全运行沙箱化代码。BPF程序被编译为eBPF指令集(RISC-like 64位VM)，经过验证器(verifier)保证安全性(无死循环、无越界内存访问、有限复杂度)后JIT编译为原生指令。挂钩点(hook)通过BPF程序类型定义：kprobe/kretprobe(内核函数入口/出口)、tracepoint(内核静态插桩点)、XDP(网络驱动层)、cgroup hook等。"},
            {"heading": "应用与生态", "content": "eBPF应用领域：1.)可观测性——BCC/bpftrace工具(Greg Kroah-Hartman)、Pixie/parca持续profiling 2.)网络安全——Cilium的eBPF-based容器网络(替代iptables/ipvs) 通过BPF maps在用户空间和内核间交换数据(hash map/array/ring buffer)。CO-RE(Compile Once, Run Everywhere)——使用BTF(BPF Type Format)使pre-compiled BPF程序可跨内核版本运行(无需为每个内核编译)。Linux安全模块(LSM)BPF挂钩强制安全策略。"},
            {"heading": "关键结论", "content": "1. eBPF被视作Linux内核最有意义的创新之一(类比JavaScript在浏览器中的角色) 2. 验证器约100k+行代码——保证BPF程序不会破坏内核稳定性 3. eBPF指令集最多100万条指令(复杂程序仍受限) 4. bpf_loop辅助可帮助实现有限循环(防止长暂停) 5. eBPF的可编程性令内核变得前所未有地可观测与可扩展"},
            {"heading": "关联知识点", "content": "[[操作系统-容器隔离(cgroups/namespace)深度]] [[计算机网络-内核旁路DPDK/XDP]] [[编译原理-虚拟机与字节码]]"}
        ]
    },
    {
        "dir_name": "操作系统",
        "file_stem": "安全启动与TPM",
        "title": "安全启动与TPM",
        "course": "操作系统",
        "chapter": "安全",
        "difficulty": "ADVANCED",
        "tags": ["操作系统", "安全启动", "TPM", "信任链", "硬件安全"],
        "aliases": ["Secure Boot", "TPM", "Trusted Platform Module", "Measured Boot"],
        "source": "UEFI Specification §27 Secure Boot; TCG TPM 2.0 Specification; Linux integrity subsystem文档",
        "sections": [
            {"heading": "核心定义", "content": "安全启动(Secure Boot)是UEFI固件的安全特性：启动链中的每个组件(固件→bootloader→OS kernel→驱动)的签名在加载前被验证。只有被平台信任的密钥签名的二进制才被允许执行。信任锚是Platform Key(PK)——平台所有者密钥。TPM(Trusted Platform Module, 可信平台模块)是硬件安全元件，通过PCR(Platform Configuration Register)记录系统启动测量链(measured boot)实现远程证明(remote attestation)——向远程方证明系统运行在可信状态。"},
            {"heading": "实现与Linux IMA", "content": "Linux Integrity Measurement Architecture(IMA)将启动安全扩展到运行时——每个被执行/读取/映射的文件进行哈希验证。EVM(Extended Verification Module)保护文件元数据的完整性。dm-verity提供块设备级别的完整性检查——Android的verified boot使用它。TPM的sealing功能将数据(密钥)绑定到特定的PCR状态(仅在特定系统配置下释放)。硬件TPM被fTPM(固件TPM,Intel PTT/AMD fTPM)补充但fTPM曾有稳定性问题。"},
            {"heading": "关键结论", "content": "1. Secure Boot ≠ 只运行微软签名代码——用户可以加入自己的MOK(Machine Owner Key) 2. TPM密钥永不离开芯片——私钥密封在硬件的防篡改存储中 3. 远程证明依赖quote——对指定PCR的TPM签名值 4. user-space stack(tss2/tpm2-tools)与TPM交互 5. 完全的安全启动实现非常复杂——许多生产系统仅实现了部分链"},
            {"heading": "关联知识点", "content": "[[操作系统-容器隔离(cgroups/namespace)深度]] [[信息安全-侧信道攻击防御]] [[计算机组成原理-可信执行环境TEE]]"}
        ]
    },
    {
        "dir_name": "操作系统",
        "file_stem": "容器隔离cgroups-namespace深度",
        "title": "容器隔离(cgroups/namespace)深度",
        "course": "操作系统",
        "chapter": "虚拟化",
        "difficulty": "ADVANCED",
        "tags": ["操作系统", "cgroups", "namespace", "容器", "隔离"],
        "aliases": ["cgroups v2", "Linux Namespaces", "Container Isolation"],
        "source": "Linux kernel文档 cgroups v2; Michael Kerrisk《Namespaces in operation》; Docker/containerd源码",
        "sections": [
            {"heading": "核心定义", "content": "Linux容器依赖两大内核机制实现隔离。cgroups(Control Groups, v2已取代v1)：控制器(controller)控制进程组的资源使用——cpu(带宽/shares)、memory(硬限制+软限制、oom_group)、io(bfq/throttle)、pids(防fork炸弹)、cpuset(亲和性)。namespace：8种独立的命名空间——Mount(独立的文件系统视图/overlay2)、PID(独立的PID树)、Net(独立的网络栈/veth pair)、User(UID/GID映射,允许rootless容器)、UTS(hostname)、IPC、Cgroup、Time。"},
            {"heading": "安全边界分析", "content": "容器不是完整的虚拟化——共享内核意味着容器间的攻击面：微架构侧信道(Spectre/Meltdown——容器的内核共享特性令其成为目标)、内核漏洞(容器逃逸漏洞如Dirty COW、Dirty Pipe)、共享资源消耗(写时拷贝的攻击)。Seccomp(secure computing)允许容器过滤系统调用减少攻击面。user namespace将容器中的root(UID 0)映射为主机上的非特权UID(安全隔离——免root容器)。gVisor/Kata Containers提供更强的安全隔离(为每个容器提供轻量级内核)。"},
            {"heading": "关键结论", "content": "1. Kubernetes的QoS类(Guaranteed/Burstable/BestEffort)基于cgroups配置 2. OOM score基于当前+历史内存使用量(oom_score_adj调整) 3. cgroup v2去除了v1的forked hierarchy混乱(统一层级结构——每个控制器仅有一个实例) 4. 容器的资源限制不能超过实际资源容量否则形成资源过度承诺 5. Docker的default seccomp profile禁止约44个不安全的系统调用(约300+个总体调用)"},
            {"heading": "关联知识点", "content": "[[操作系统-虚拟内存与TLB]] [[操作系统-eBPF内核虚拟机]] [[分布式系统-容器编排Kubernetes基础]]"}
        ]
    },

    # ═══════════════════════════════════════════════════════════════
    # 数据结构 — 5 supplemental topics
    # ═══════════════════════════════════════════════════════════════
    {
        "dir_name": "数据结构",
        "file_stem": "Treap与Splay-Tree",
        "title": "Treap与Splay Tree",
        "course": "数据结构",
        "chapter": "高级数据结构",
        "difficulty": "ADVANCED",
        "tags": ["数据结构", "Treap", "Splay Tree", "平衡树", "随机化"],
        "aliases": ["Treap", "Splay Tree"],
        "source": "Aragon & Seidel 1989 (Treap); Sleator & Tarjan 1985 (Splay Tree); CP3 (Halim) Ch 8",
        "sections": [
            {"heading": "核心定义", "content": "Treap(Tree+Heap)是二叉搜索树(BST)与堆的结合：每个节点有两个键——BST键(满足搜索树性质)和随机优先级(满足max-heap性质)。Treap通过旋转维护堆性质，期望高度O(log n)，插入/删除/查找均为O(log n)期望时间。Splay Tree是自调整(self-adjusting)二叉搜索树——每次访问(查找、插入、删除)后将访问节点splay旋转到根。splay操作依赖zig、zig-zig和zig-zag三种旋转模式的组合。"},
            {"heading": "分摊分析", "content": "Splay Tree没有显式的平衡条件——通过splay操作隐式改善结构。分摊时间O(log n)通过势能方法(potential method)证明：势能定义为各节点size=log(子树大小)之和。splay使访问频率高的节点更接近根——实现工作集性质(working set property)和静态最优性(static optimality)。Treap的随机性保证了期望高度O(log n)——不需rebalancing操作。Treap支持快速的split(按key)/merge(合并两棵树——要求最大key<最小key)。"},
            {"heading": "关键结论", "content": "1. Treap是最容易实现的平衡树结构(无complex rotation逻辑) 2. Splay的摊销O(log n)不保证每个操作都是O(log n) 3. Splay Tree不适合实时系统(单个操作可能退化O(n)) 4. Treap可用来实现可持久化BST(因旋转是局部的) 5. Implicit Treap用树位置显式建立数组——支持split/merge的数组实现"},
            {"heading": "关联知识点", "content": "[[数据结构-平衡二叉搜索树AVL与红黑树]] [[数据结构-Disjoint Set Union深度]] [[算法设计与分析-摊销分析]]"}
        ]
    },
    {
        "dir_name": "数据结构",
        "file_stem": "QuadTree与R-Tree",
        "title": "QuadTree与R-Tree",
        "course": "数据结构",
        "chapter": "空间数据结构",
        "difficulty": "ADVANCED",
        "tags": ["数据结构", "QuadTree", "R-Tree", "空间索引", "GIS"],
        "aliases": ["Quadtree", "R-Tree", "Spatial Index"],
        "source": "Finkel & Bentley 1974 (Quadtree); Guttman 1984 (R-Tree); Samet《Foundations of Multidimensional Structures》",
        "sections": [
            {"heading": "核心定义", "content": "Quadtree(四叉树)将2D空间递归划分为4个象限：NW/NE/SW/SE，直到每一象限中的点数<=1。插入：跟踪象限直到叶子——分裂如果超过容量。范围搜索：检查每个象限是否与查询矩形相交。时间复杂度：插入/删除O(log N)平均(均匀分布)。R-Tree(矩形树)是B树在空间维度上的扩展：每个节点包含一组MBR(Minimum Bounding Rectangle,最小包围矩形)，搜索和插入按面积扩展最小的原则选择合适的子节点分裂。"},
            {"heading": "应用与变体", "content": "R-tree是多数空间数据库(SpatiaLite/PostGIS的GiST索引)的底层结构。R*-tree通过强制重插入(forced reinsert)改进空间利用率。STR tree(Sort-Tile-Recursive)提供批量加载方案。Quadtree变体：Point Quadtree(分裂部分)、PR Quadtree(基于矩形分裂)、PM Quadtree(多边形地图)。OctTree是四叉树在3D的扩展(每个节点8个子空间)——用于3D游戏引擎的空间分区和点云处理。"},
            {"heading": "关键结论", "content": "1. R-tree适合存储静态空间数据(建筑/道路)——插入后索引质量在单次加载最好 2. R-tree的删除导致重叠增加需要定期重建 3. 四叉树擅长均匀分布的点数据(城市poi分布) 4. Hilbert R-tree以Hilbert曲线顺序存储——提高空间局部性 5. KD-tree是另一种空间索引——基于k维二分而非象限划分"},
            {"heading": "关联知识点", "content": "[[数据结构-B树与B+树]] [[数据结构-A*算法与启发式搜索]] [[计算机图形学-空间数据结构与加速]]"}
        ]
    },
    {
        "dir_name": "数据结构",
        "file_stem": "Disjoint-Set-Union深度",
        "title": "Disjoint Set Union深度",
        "course": "数据结构",
        "chapter": "高级数据结构",
        "difficulty": "INTERMEDIATE",
        "tags": ["数据结构", "并查集", "DSU", "路径压缩", "按秩合并"],
        "aliases": ["Union-Find", "DSU", "Path Compression"],
        "source": "Tarjan 1975 (Union-Find); CLRS §21; Sedgewick《Algorithms》Ch 1.5",
        "sections": [
            {"heading": "核心定义", "content": "Disjoint Set Union(DSU/并查集/Union-Find)维护不相交集合的集合。核心操作：MakeSet(x)(创建新集合)、Find(x)(找到x所在集合的代表元/根)、Union(x,y)(合并两集合)。基础实现使用parent数组(parent[x]=父节点)。路径压缩(path compression)——Find时将x到根的路径上所有节点直接指向根。按秩合并(union by rank)——总将rank小的树接在rank大的树下(保持树浅)。组合两种优化得到O(alpha(N))的近乎线性的均摊时间。alpha(N)是阿克曼函数的逆——对所有实际N < 5。"},
            {"heading": "高级扩展", "content": "带权并查集(weighted DSU)在边上存储信息(如食物链中的'x eats y'关系)——Find时沿着路径累积权重。可回滚并查集(rollback DSU)——仅使用按秩合并(不用路径压缩)以支持撤销操作(使用栈记录合并操作)。可持久化并查集(persistent DSU)——用持久化数组实现。在线/离线版本——处理动态连接的连接性查询(加边+查询连通性)。按元素数量(size)合并有时比按秩(height)更常用(效果相近但更简单)。"},
            {"heading": "关键结论", "content": "1. 实际中只用路径压缩或只用按秩合并都是O(log N)级 2. 按大小合并保证树高不超过logN 3. DSU不能高效处理删边——边删除是困难问题(需用动态树Link-Cut Tree) 4. 离线DSU解决'在一段时间内存在边'的问题(通过扫描时间线) 5. DSU是Kruskal算法和许多图处理算法的基础"},
            {"heading": "关联知识点", "content": "[[数据结构-图的最小生成树]] [[数据结构-Treap与Splay Tree]] [[算法设计与分析-在线算法与竞争比]]"}
        ]
    },
    {
        "dir_name": "数据结构",
        "file_stem": "A-star算法与启发式搜索",
        "title": "A*算法与启发式搜索",
        "course": "数据结构",
        "chapter": "图算法",
        "difficulty": "INTERMEDIATE",
        "tags": ["数据结构", "A*", "启发式", "寻路", "最短路径"],
        "aliases": ["A* Search", "Heuristic Search", "Pathfinding"],
        "source": "Hart, Nilsson & Raphael 1968 (A*); Russell & Norvig《AI: Modern Approach》Ch 3; Amit Patel的A* Introduction",
        "sections": [
            {"heading": "核心定义", "content": "A*搜索是最优优先最佳优先搜索算法的代表。评价函数f(n)=g(n)+h(n)：g(n)是从起点到n的实际代价，h(n)是从n到目标的启发式估计代价(heuristic)。使用优先队列(最小二叉堆)不断扩展f最小的节点。可接受性(admissibility)：h(n)不高估实际代价时A*找到最优解(h应乐观)。一致性/单调性(consistency)：满足三角不等式h(n)<=cost(n,n')+h(n')。一致性保证图搜索不需要重打开已关闭的节点。"},
            {"heading": "启发函数设计", "content": "常见启发式：网格寻路——曼哈顿距离、对角线距离、欧几里得距离。欧几里得距离可接受但不一致(计算浮点误差可丢失一致性)。有效分支因子(b*)衡量启发式的质量——b*越接近1越好。打破路径平局(tie-breaking)：给h略微增加(仍保持可接受)——使搜索偏向目标方向减少探索节点。Jump Point Search(JPS)通过对称消除和强制neighbors剪枝在均匀网格上极大加速A*(不扩展无关节点)。"},
            {"heading": "关键结论", "content": "1. 启发式越好(h更精确)搜索节点越少 2. A*的空间复杂度O(b^d)是主要瓶颈——IDA*(迭代加深A*)缓解 3. A*在游戏寻路、拼图求解、DNA序列对齐等领域有广泛应用 4. 具有monotone heuristic的A*等价于在re-weighted图上的Dijkstra 5. epsilon-A*通过放松最优性显著减少搜索时间"},
            {"heading": "关联知识点", "content": "[[数据结构-最短路径算法Dijkstra/Bellman-Ford]] [[算法设计与分析-动态规划]] [[人工智能-搜索算法]]"}
        ]
    },
    {
        "dir_name": "数据结构",
        "file_stem": "后缀自动机与后缀数组",
        "title": "后缀自动机与后缀数组",
        "course": "数据结构",
        "chapter": "字符串",
        "difficulty": "ADVANCED",
        "tags": ["数据结构", "后缀自动机", "后缀数组", "字符串", "SAM"],
        "aliases": ["Suffix Automaton", "Suffix Array", "LCP Array"],
        "source": "Ukkonen 1995 (后缀树); Gusfield《Algorithms on Strings, Trees and Sequences》; CP Algorithms",
        "sections": [
            {"heading": "核心定义", "content": "后缀自动机(SAM/Suffix Automaton)是接受字符串S的所有后缀的最小确定性有限自动机。SAM的大小O(|S|)、构造时间O(|S|)。每个状态对应一个endpos等价类——所有出现结束位置相同的子串的集合。转移边按字符添加，link边指向后缀链接。后缀数组(Suffix Array/SA)是S的所有后缀的排序索引数组。SA[i]=j表示字典序第i小的后缀开始于位置j。Rank数组是SA的逆——Rank[j]=i意味着从j开始的后缀排名为i。"},
            {"heading": "LCP与后缀树", "content": "LCP数组(Longest Common Prefix)存储相邻后缀(按字典序)的最长公共前缀长度：LCP[i]=LCP(suffix[SA[i-1]],suffix[SA[i]])。LCP通过Kasai算法在O(n)时间计算(利用Rank数组减少比对)。后缀树(Suffix Tree)是S的所有后缀的压缩trie——每个节点代表一个内部子串。后缀数组+LCP可以模拟后缀树的大部分功能(RMQ over LCP=两个后缀的LCP)。后缀自动机可以解决子串统计、最长重复子串、不同子串数量等问题。"},
            {"heading": "关键结论", "content": "1. SAM是终极字符串数据结构——可以解决几乎所有线性时间的字符串问题 2. 后缀数组比后缀树更节省空间(O(n) vs O(n log n)) 3. SA+LCP+RMQ可替代后缀树做子串搜索(O(|P|+log n)) 4. SAM的每个状态维护：len(最长串长度)、link(后缀链接)、next转移 5. 后缀数组通常最常用于竞赛编程和基因组学"},
            {"heading": "关联知识点", "content": "[[数据结构-字符串匹配KMP/Boyer-Moore]] [[数据结构-Trie与字符串检索]] [[算法设计与分析-字符串算法]]"}
        ]
    },

    # ═══════════════════════════════════════════════════════════════
    # 计算机网络 — 5 supplemental topics
    # ═══════════════════════════════════════════════════════════════
    {
        "dir_name": "计算机网络",
        "file_stem": "BBR拥塞控制",
        "title": "BBR拥塞控制",
        "course": "计算机网络",
        "chapter": "传输层",
        "difficulty": "ADVANCED",
        "tags": ["计算机网络", "BBR", "拥塞控制", "TCP", "瓶颈带宽"],
        "aliases": ["BBR Congestion Control", "Bottleneck Bandwidth and RTT"],
        "source": "Cardwell et al. 2016 (BBR paper, ACM Queue); Google BBR GitHub; RFC 9438 (BBR v2)",
        "sections": [
            {"heading": "核心定义", "content": "BBR(Bottleneck Bandwidth and Round-trip propagation time)是Google于2016年提出的拥塞控制算法。不同于传统基于丢包的算法(CUBIC/Reno)，BBR基于网络路径模型：持续测量交付速率(瓶颈带宽估计)和最小RTT(往返传播时间)。发送速率=BBR.BtlBw * pacing_gain，拥塞窗口=BBR.BDP* cwnd_gain。BBR不再将丢包作为拥塞信号——丢包可能是噪声或竞争引起。"},
            {"heading": "状态机与v2改进", "content": "BBR状态机循环四个阶段：STARTUP(指数搜索带宽,2.5x pacing增益——快速填满管道)、DRAIN(排空STARTUP期间积累的队列)、PROBE_BW(周期8个RTT——大部分时间1x pacing+每8 RTT一个5/4增益探测更多带宽)、PROBE_RTT(每10s减少cwnd到4个包以探测更小的RTT基线)。BBR v2增加了对ECN(显式拥塞通知)和丢包的明确反应(轻度丢包减窗)，解决了v1在浅缓冲区或与损耗型算法公平性的问题。"},
            {"heading": "关键结论", "content": "1. BBR在高丢包长RTT链路上表现优于CUBIC达2700倍 2. BBR v1在竞争fairness上有问题(可能会'撑死'其他流)——v2改进 3. YouTube采用BBR后中位吞吐量增加了4%(2016) 4. BBR仅需发送方支持(接收方无需改动) 5. TCP pacing是实现BBR的基础——即将数据包均匀分布在整个RTT而非突发"},
            {"heading": "关联知识点", "content": "[[计算机网络-TCP拥塞控制]] [[计算机网络-QUIC与HTTP/3]] [[计算机网络-软件定义网络SDN]]"}
        ]
    },
    {
        "dir_name": "计算机网络",
        "file_stem": "软件定义网络SDN",
        "title": "软件定义网络SDN",
        "course": "计算机网络",
        "chapter": "网络架构",
        "difficulty": "ADVANCED",
        "tags": ["计算机网络", "SDN", "OpenFlow", "控制面", "转发面"],
        "aliases": ["Software-Defined Networking", "OpenFlow", "SDN"],
        "source": "ONF (Open Networking Foundation) SDN Architecture; McKeown et al. 2008 (OpenFlow); RFC 7426 SDN Layers",
        "sections": [
            {"heading": "核心定义", "content": "SDN(软件定义网络)将网络设备的控制面(control plane,决定如何转发)与数据面(data plane,执行转发)分离。控制面集中部署在SDN控制器(如OpenDaylight, ONOS, Ryu)中，通过南向接口协议(如OpenFlow)下发流表规则到交换机。数据面交换机仅根据流表匹配和转发数据包。这使得网络行为可通过软件编程——无需逐台配置网络设备。SDN的三个核心原则：开放接口、网络虚拟化、网络可编程。"},
            {"heading": "OpenFlow协议", "content": "OpenFlow 1.3/1.5定义了流表(flow table)、组表(group table)和计量表(meter table)。每个流表项包含：匹配字段(12元组——入端口、src/dst MAC、src/dst IP、src/dst Port、EtherType等)、优先级、计数器、指令集(输出到端口、转到下一流表、改写头部字段)。多级流表(pipeline)处理包——先匹配表0再表1...。OpenFlow通道是控制器与交换机间的TLS连接。P4(Programming Protocol-independent Packet Processors)更进一步发展——允许自定义包转发处理逻辑。"},
            {"heading": "关键结论", "content": "1. SDN的核心价值在数据中心网络中体现最充分(Google的B4 WAN使用SDN获得近乎100%链路利用率) 2. OpenFlow的匹配依赖TCAM(三态内容寻址内存)——昂贵且有限(通常几千条) 3. 控制器的单点故障(SPOF)需通过集群化解决 4. SDN+NFV(网络功能虚拟化)实现端到端可编程网络 5. White-box交换机+开源NOS(SONiC/Stratum)推动网络硬件解耦"},
            {"heading": "关联知识点", "content": "[[计算机网络-网络命名空间]] [[计算机网络-Anycast与GeoDNS]] [[分布式系统-软件定义存储SDS]]"}
        ]
    },
    {
        "dir_name": "计算机网络",
        "file_stem": "网络命名空间",
        "title": "网络命名空间",
        "course": "计算机网络",
        "chapter": "网络虚拟化",
        "difficulty": "INTERMEDIATE",
        "tags": ["计算机网络", "namespace", "虚拟化", "veth pair", "容器网络"],
        "aliases": ["Network Namespace", "veth pair", "Container Networking"],
        "source": "Linux kernel net namespace文档; man ip-netns(8); Docker networking documentation",
        "sections": [
            {"heading": "核心定义", "content": "Linux网络命名空间(Network Namespace)是隔离的网络栈实例——每个ns有自己独立的路由表、iptables规则、网络设备列表、socket、邻居表。默认每个进程属于host网络命名空间(全局)。创建新ns：ip netns add ns1，在其中运行命令：ip netns exec ns1 bash。ns之间通过veth pair(虚拟以太网对)连接——一端在ns1另一端在ns2，数据包从一端进入自动从另一端输出。虚拟bridge(linux bridge)连接多个ns实现多容器网络。"},
            {"heading": "容器网络实现", "content": "Docker的bridge网络模型：每个容器获得自己独立的ns，通过veth pair连接到docker0网桥。容器MAC/IP在网桥上学习。Docker的host网络模式——容器共享host ns(无隔离)。Docker的overlay网络——在多主机间使用VXLAN隧道实现跨节点容器直接通信。Kubernetes的CNI(Container Network Interface)规范定义容器网络的接入方式——Calico(BGP路由)、Flannel(overlay VXLAN)、Cilium(eBPF-based,取代传统网络栈)。"},
            {"heading": "关键结论", "content": "1. 网络命名空间是实现容器网络隔离的基础 2. veth pair的开销极低——仅需额外的一次DMA copy 3. ip link set dev veth1 netns ns1将veth移动到命名空间 4. 容器网络性能关键——overlay(加VXLAN)增加~10%开销+MTU减50字节 5. macvlan/ipvlan提供直接暴露物理接口的替代(无需网桥/NAT,但IP可管理性下降)"},
            {"heading": "关联知识点", "content": "[[操作系统-容器隔离(cgroups/namespace)深度]] [[计算机网络-软件定义网络SDN]] [[分布式系统-容器编排Kubernetes基础]]"}
        ]
    },
    {
        "dir_name": "计算机网络",
        "file_stem": "内核旁路DPDK-XDP",
        "title": "内核旁路DPDK/XDP",
        "course": "计算机网络",
        "chapter": "高性能网络",
        "difficulty": "ADVANCED",
        "tags": ["计算机网络", "DPDK", "XDP", "内核旁路", "高性能"],
        "aliases": ["DPDK", "XDP", "Kernel Bypass", "eXpress Data Path"],
        "source": "DPDK官方文档; Linux kernel XDP文档; Cilium's BPF and XDP Reference Guide",
        "sections": [
            {"heading": "核心定义", "content": "内核旁路(kernel bypass)是高性能网络的关键技术——网络包直接由用户空间程序处理而不经过内核网络协议栈。DPDK(Data Plane Development Kit, Intel主导)提供用户空间的poll-mode驱动(PMD)——持续轮询网卡RX队列替代中断驱动的收包。XDP(eXpress Data Path)是Linux内核中的eBPF挂钩点，在数据包到达网络栈之前(i40e驱动的RX队列之后, skb之前)处理，实现了接近内核旁路的性能而无需专用用户态驱动。"},
            {"heading": "DPDK vs XDP", "content": "DPDK：完整用户空间TCP/IP栈(如mTCP/TLDK/f-stack)，应用程序直接操作物理NIC(Hugepages内存映射网卡DMA区,排除内核),NUMA-aware内存分配。单核可处理100+Mpps。未通过标准socket——应用需要专门为DPDK编写。XDP：运行在内核中(无上下文切换)，但利用eBPF提供的安全保障。支持XDP_DROP/XDP_TX/XDP_REDIRECT/XDP_PASS动作。AF_XDP socket提供接近DPDK的信道到用户空间(zero-copy)——绕过sk_buff但保留socket接口。"},
            {"heading": "关键结论", "content": "1. DPDK适合云服务商接入网关/流量清洗/DDoS缓解(Cloudflare的Spectrum使用DPDK) 2. XDP适合DDoS缓解和负载均衡(内核集成,无需重编译) 3. 内核旁路的主要代价是失去标准的socket生态(DPDK不兼容标准TCP) 4. ScyllaDB/Seastar使用DPDK网络层的用户态TCP(NIC>DPDK>Seastar>App) 5. AF_XDP是DPDK与标准socket之间的中间地带——提供DPDK级性能+标准socket-like接口"},
            {"heading": "关联知识点", "content": "[[操作系统-eBPF内核虚拟机]] [[计算机网络-BBR拥塞控制]] [[Java深入-NIO与零拷贝]]"}
        ]
    },
    {
        "dir_name": "计算机网络",
        "file_stem": "Anycast与GeoDNS",
        "title": "Anycast与GeoDNS",
        "course": "计算机网络",
        "chapter": "网络基础设施",
        "difficulty": "INTERMEDIATE",
        "tags": ["计算机网络", "Anycast", "GeoDNS", "CDN", "负载均衡"],
        "aliases": ["Anycast", "GeoDNS", "Global Server Load Balancing"],
        "source": "RFC 4786 (Anycast); RFC 1794 (DNS负载均衡); Cloudflare/CDN architecture docs",
        "sections": [
            {"heading": "核心定义", "content": "Anycast是IP路由技术——多个节点广播同一IP地址，BGP路由选择最近的节点交付数据包(基于AS Path长度)。典型应用：DNS根服务器(13个IP地址但数千个物理节点——全部使用Anycast)。GeoDNS将DNS解析结果基于用户地理位置返回——用户查询www.example.com，权威DNS根据查询源IP选择最近的数据中心IP返回。不同于anycast的IP BGP路由，GeoDNS在DNS层做智能调度(能考虑更复杂的策略)。"},
            {"heading": "CDN中的使用", "content": "CDN(内容分发网络)中Anycast和GeoDNS通常分层使用：用户→DNS查询→GeoDNS解析(基于用户IP位置)→返回边缘CDN节点的Anycast IP→TCP连接到最近的CDN边缘节点。Anycast在网络层做粗粒度优化(用户到最近的PoP/Points of Presence)，GeoDNS在应用层做精细调度(健康检查、负载、成本)。Unicast vs Anycast：Anycast的优势——自动故障切换(节点离线时路由自动收敛)；挑战——TCP连接在Anycast变更时可能中断(不同节点不同状态)。"},
            {"heading": "关键结论", "content": "1. Anycast+TCP不安全——连接中路由变更将导致RST 2. DNS使用Anycast极好(UDP简单查询)——这正是根服务器如此可靠的原因 3. Cloudflare通过Anycast防御DDoS——攻击流量被分散到全球各节点 4. GeoDNS返回的TTL越低切换越快但查询负载越高 5. BGP Anycast的精细化控制有限(只能影响路由策略不能完全控制)"},
            {"heading": "关联知识点", "content": "[[计算机网络-DNS协议详解]] [[计算机网络-BGP与自治系统]] [[分布式系统-负载均衡策略]]"}
        ]
    },

    # ═══════════════════════════════════════════════════════════════
    # 算法设计与分析 — 5 supplemental topics
    # ═══════════════════════════════════════════════════════════════
    {
        "dir_name": "算法设计与分析",
        "file_stem": "线性规划与单纯形法",
        "title": "线性规划与单纯形法",
        "course": "算法设计与分析",
        "chapter": "优化算法",
        "difficulty": "ADVANCED",
        "tags": ["算法", "线性规划", "单纯形法", "对偶", "优化"],
        "aliases": ["Linear Programming", "Simplex Algorithm", "Duality"],
        "source": "Dantzig 1947 (Simplex); CLRS §29; Vanderbei《Linear Programming: Foundations and Extensions》",
        "sections": [
            {"heading": "核心定义", "content": "线性规划(LP)是优化问题：在m个线性约束(Ax<=b)下最大化/最小化线性目标函数(c^Tx)。单纯形法(Dantzig 1947, 被列为20世纪Top10算法之一)的核心思想——在可行域的多面体顶点间沿着边移动，每一步改进目标函数。标准形式引入松弛变量(slack variable)将不等式转为等式。初始可行解由两阶段法获得。主元(pivot)操作在单纯形表上执行：选择入基变量(最大reduced cost)和出基变量(最小ratio test)。"},
            {"heading": "对偶与复杂度", "content": "对偶定理(Duality Theorem)：若原始问题有最优解，则对偶问题有相同最优值。弱对偶性(任何可行解的对偶下界<=原始上界)提供最优性的certificate。互补松弛条件(complementary slackness)刻画原始-对偶最优对。单纯形法的最坏指数时间可通过Klee-Minty立方体构造，但实际表现接近线性——属于smoothed complexity。内点法(Interior Point Method, Karmarkar 1984)提供多项式复杂度替代(O(n^3.5L))。"},
            {"heading": "关键结论", "content": "1. 整数规划是NP-hard(不能简单取LP的最优解四舍五入) 2. 对偶在支持向量机(SVM)和网络流问题中有核心应用 3. 单纯形在稀疏约束矩阵上极高效(通常O(m) iteration) 4. LP的可解性可通过Farkas引理刻画 5. 现代LP求解器(Gurobi/CPLEX)混合单纯形+内点法"},
            {"heading": "关联知识点", "content": "[[算法设计与分析-NP完全性理论与归约]] [[算法设计与分析-极大流算法(Dinic/HLPP)]] [[离散数学-线性代数]]"}
        ]
    },
    {
        "dir_name": "算法设计与分析",
        "file_stem": "极大流算法Dinic-HLPP",
        "title": "极大流算法(Dinic/HLPP)",
        "course": "算法设计与分析",
        "chapter": "图算法",
        "difficulty": "ADVANCED",
        "tags": ["算法", "网络流", "Dinic", "HLPP", "最大流"],
        "aliases": ["Maximum Flow", "Dinic's Algorithm", "HLPP"],
        "source": "Dinic 1970; Goldberg & Tarjan 1988 (Push-Relabel); CLRS §26; Ahuja, Magnanti & Orlin《Network Flows》",
        "sections": [
            {"heading": "核心定义", "content": "网络最大流问题：有向图G=(V,E)，源点s汇点t，每条边有容量c，求从s到t的最大可行流量。Ford-Fulkerson方法(O(E max_flow)，整形容量)不断找增广路径——但可通过反边(back edge)取消之前的流量分配。Edmonds-Karp用BFS寻找最短增广路径保证O(VE^2)复杂度。Dinic算法通过分层图(level graph)在一次BFS后执行多次DFS(blocking flow)推送流量，复杂度O(EV^2)一般图/O(E sqrt(V))单位容量图。"},
            {"heading": "Push-Relabel/HLPP", "content": "Push-Relabel(推进-重标记)颠覆了传统增广路径方法。每个节点有高度(height label)和超额流量(excess flow)。Push操作将溢出流推送到高度低的邻居。Relabel操作提升节点高度使push可能。Highest Label Preflow-Push(HLPP,最高标号先出)选择最高高度的溢出节点处理达到O(V^2 sqrt(E))复杂度。理论优势明显——但常数大。Gap heuristics(间隙启发式)极大加速实际运行。HLPP在并行化上有独特优势(局部push不依赖全局路径)。"},
            {"heading": "关键结论", "content": "1. Dinic在竞赛编程中广泛应用(易于实现,实践中非常快) 2. Push-Relabel的泛化可做更一般的minimum cost flow 3. 最大流=最小割(Min-Cut Max-Flow Theorem)有深刻的组合意义 4. 动态树(Link-Cut Tree)可加速Dinic到O(VE log V) 5. 当前实际最快的实现一般基于IBFS(incremental BFS)的变体"},
            {"heading": "关联知识点", "content": "[[算法设计与分析-图算法总览]] [[算法设计与分析-线性规划与单纯形法]] [[数据结构-图的最小生成树]]"}
        ]
    },
    {
        "dir_name": "算法设计与分析",
        "file_stem": "质数测试与RSA",
        "title": "质数测试与RSA",
        "course": "算法设计与分析",
        "chapter": "数论算法",
        "difficulty": "ADVANCED",
        "tags": ["算法", "质数测试", "RSA", "数论", "Miller-Rabin"],
        "aliases": ["Primality Testing", "Miller-Rabin", "RSA"],
        "source": "Rivest, Shamir & Adleman 1978 (RSA); Miller 1976 & Rabin 1980; CLRS §31",
        "sections": [
            {"heading": "核心定义", "content": "质数测试(primality testing)判断一个大整数是否为质数。Miller-Rabin概率测试(O(k log^3 n))：利用费马小定理(a^(p-1)≡1 mod p)的细化版本——将n-1分解为d*2^s，若a^d≠1(mod n)且a^(d*2^r)≠-1(mod n)对所有r<s，则n为合数(否则'可能是质数')。k轮后错误概率<(1/4)^k，通常使用k=40达到<2^-80。RSA密钥生成依赖寻找大质数(p和q, 2048-4096 bits)——通过Miller-Rabin筛选候选。"},
            {"heading": "RSA与数论", "content": "RSA安全性基于大整数分解难题。核心计算：选定大质数p,q → n=pq → φ(n)=(p-1)(q-1) → 选公钥e满足gcd(e,φ(n))=1(常用65537) → 计算私钥d≡e^(-1) mod φ(n)(扩展的欧几里得算法)。加密c=m^e mod n，解密m=c^d mod n。中国剩余定理(CRT)加速解密(分开模p和模q)。AKS(Agrawal-Kayal-Saxena, 2002)是里程碑——第一个确定性质数测试算法(O(log^7.5 n))。"},
            {"heading": "关键结论", "content": "1. Miller-Rabin单轮极快(约微秒级对1024位) 2. 质数在整数中密度~1/ln(n)——筛选1/ln(n)个随机数可找到一个质数(需检查) 3. Pollard's rho和P-1算法分解中等的合数 4. 整数分解至今无多项式算法——Shor的量子算法(量子计算威胁) 5. RSA padding(OAEP)防止直接RSA的语义安全攻击"},
            {"heading": "关联知识点", "content": "[[算法设计与分析-图算法总览]] [[信息安全-密码学基础]] [[离散数学-数论基础]]"}
        ]
    },
    {
        "dir_name": "算法设计与分析",
        "file_stem": "拟阵与贪心理论根基",
        "title": "拟阵与贪心理论根基",
        "course": "算法设计与分析",
        "chapter": "算法理论",
        "difficulty": "ADVANCED",
        "tags": ["算法", "拟阵", "贪心", "算法理论"],
        "aliases": ["Matroid Theory", "Greedy Algorithm Foundation"],
        "source": "Whitney 1935 (Matroid); CLRS §16; Lawler《Combinatorial Optimization: Networks and Matroids》",
        "sections": [
            {"heading": "核心定义", "content": "拟阵(matroid)是线性代数和图论共同推广的组合结构。定义：有限集E和独立集族I满足——1.)空集独立 2.)独立集的任意子集独立(遗传性质hereditary) 3.)对任何子集,所有极大独立集(基,base)有相同大小(增广性质augmentation)。拟阵的秩函数(r(A)=A的最大独立子集大小)满足次模性(submodularity)。向量拟阵(一组向量的线性无关子集形成独立集族)和图形拟阵(森林的无环子图)是两类经典拟阵。"},
            {"heading": "贪心与拟阵", "content": "拟阵是贪心算法能求得最优解的最小假设结构。定理：对于带权拟阵的元素，每次选择最小权重的可扩展独立集的贪心算法确实产生全局最小的基。这就是Kruskal算法(最小生成树，在图形拟阵)的数学根基。但并非所有能用贪心解决的问题都有拟阵结构——调度问题(单位时间任务+截止时间+惩罚)的贪心策略是拟阵的交(matroid intersection)。两个拟阵的交集仍为独立集族但不再是拟阵。"},
            {"heading": "关键结论", "content": "1. 拟阵解释了'为什么'某些贪心算法正确——不是巧合 2. 许多实际优化问题可建模为拟阵交问题 3. 三个拟阵的交是NP-hard(多项式时间不可能) 4. 拟阵划分(matroid partition)将元素分到最少的独立集 5. 子模函数最优化是拟阵理论的现代泛化(离散凸性)"},
            {"heading": "关联知识点", "content": "[[算法设计与分析-贪心算法]] [[算法设计与分析-线性规划与单纯形法]] [[离散数学-组合数学]]"}
        ]
    },
    {
        "dir_name": "算法设计与分析",
        "file_stem": "在线算法与竞争比",
        "title": "在线算法与竞争比",
        "course": "算法设计与分析",
        "chapter": "算法理论",
        "difficulty": "ADVANCED",
        "tags": ["算法", "在线算法", "竞争比", "对手论证"],
        "aliases": ["Online Algorithms", "Competitive Ratio", "Adversary Argument"],
        "source": "Sleator & Tarjan 1985 (Competitive analysis); Borodin & El-Yaniv《Online Computation and Competitive Analysis》",
        "sections": [
            {"heading": "核心定义", "content": "在线算法(online algorithm)必须在不完全知道未来的情况下逐步做决策。竞争比(competitive ratio)是衡量在线算法质量的标准：对任何输入序列，在线算法结果<=最优离线算法的c倍(min问题)或>=1/c倍(max问题)。最著名的在线问题：缓存分页(paging)——LRU(Least Recently Used)达到k-competitive(k=缓存大小)，这是确定性在线策略能获得的最优竞争比(下界k)。标记算法(Marking algorithm)提供了O(log k)对比的随机化替代。"},
            {"heading": "对手论证方法", "content": "对手论证(adversary argument)是一类标准下界证明技术。构造者(adversary)根据在线算法的决策动态构造输入确保在线算法的表现尽可能差。例如滑雪租赁问题(ski rental)：滑雪板(买断)vs租赁——确定性算法的竞争比≥2，最优随机化策略是e/(e-1)≈1.58(基于概率递减的租赁)。k-server问题要求服务器在度量空间移动为请求服务——Competitive conjecture：确定性k-server竞争比=k。"},
            {"heading": "关键结论", "content": "1. 在线算法在不可预测的现实世界中非常有意义(cache/调度/资源预留) 2. 竞争比是最坏情况度量——实际表现通常更好 3. 使用随机化可以显著改进竞争比 4. 资源增广(resource augmentation)通过给予在线算法更多资源换取更优竞争比 5. 运动规划的在线版本(如在未知地图中行进)与在线图探索相关"},
            {"heading": "关联知识点", "content": "[[算法设计与分析-近似算法]] [[算法设计与分析-摊销分析]] [[数据结构-缓存替换策略LRU/LFU]]"}
        ]
    },

    # ═══════════════════════════════════════════════════════════════
    # 计算机组成原理 — 5 supplemental topics
    # ═══════════════════════════════════════════════════════════════
    {
        "dir_name": "计算机组成原理",
        "file_stem": "分支预测器深度",
        "title": "分支预测器深度",
        "course": "计算机组成原理",
        "chapter": "CPU微架构",
        "difficulty": "ADVANCED",
        "tags": ["计算机组成", "分支预测", "微架构", "流水线"],
        "aliases": ["Branch Predictor", "TAGE", "Perceptron"],
        "source": "Hennessy & Patterson《Computer Architecture》Ch 3; Intel 64 and IA-32 Optimization Manual; Seznec TAGE paper 2006",
        "sections": [
            {"heading": "核心定义", "content": "分支预测器(branch predictor)是高性能CPU流水线的关键组件——在分支指令的结果(跳转/不跳转)确定之前猜测其方向，避免流水线停顿(分支造成的流水线气泡导致IPC急剧下降)。现代CPU的分支预测准确率>97%。Gshare(全局历史XOR PC形成索引)补偿了2-level预测器中的混叠问题(aliasing)。Tournament predictor(Alpha 21264)结合局部和全局两个预测器——选择器根据历史正确性选择更优者。"},
            {"heading": "TAGE与现代预测器", "content": "TAGE(TAgged GEometric length predictor, Seznec 2006)是当今最佳的分支预测器，被Intel(2013+)、AMD(Zen+)采用。TAGE使用多个历史长度几何级数增长的表(1,2,4,8,16...),每个表项包含非饱和计数器和tag。长的历史预测基本循环，短历史适应变化快的分支。Perceptron predictor(Academic,2001)将分支预测建模为线性决策问题——用神经元网络训练特定权重(AMD采用感知器版本)。循环预测器(loop predictor)专门预测循环迭代数。"},
            {"heading": "关键结论", "content": "1. 分支预测失误的代价(约15-20个周期)——远大于指令cache miss(无miss时单个周期) 2. 间接分支(如虚函数调用)比条件分支难预测(需要BTB+IAP——Indirect target predictor) 3. Spectre v2(Branch Target Injection)攻击利用分支预测器的训练-预测间隙 4. 两个分支用1位历史vs使用长历史效果差异极大(数据相关分支需要模式识别) 5. 编译器优化(profile-guided optimization)帮助CPU分支预测——概率性分支移至冷路径"},
            {"heading": "关联知识点", "content": "[[计算机组成原理-乱序执行与ROB]] [[计算机组成原理-流水线与冒险]] [[操作系统-eBPF内核虚拟机]]"}
        ]
    },
    {
        "dir_name": "计算机组成原理",
        "file_stem": "乱序执行与ROB",
        "title": "乱序执行与ROB",
        "course": "计算机组成原理",
        "chapter": "CPU微架构",
        "difficulty": "ADVANCED",
        "tags": ["计算机组成", "乱序执行", "ROB", "微架构", "寄存器重命名"],
        "aliases": ["Out-of-Order Execution", "Reorder Buffer", "Tomasulo"],
        "source": "Tomasulo 1967 (IBM 360/91); H&P《Computer Architecture》Ch 3; Intel Optimization Manual §2.1",
        "sections": [
            {"heading": "核心定义", "content": "乱序执行(Out-of-Order, OoO)允许CPU不按程序顺序执行指令——只要操作数就绪且功能单元可用就发射执行。核心数据结构：Reorder Buffer(ROB/重排序缓冲区)——按程序顺序存储所有正在执行的指令，确保指令按程序顺序提交(commit)；Register Alias Table(RAT)——将体系结构寄存器映射到物理寄存器(寄存器重命名)，消除写后读(WAW)和读后写(WAR)假数据冒险。Tomasulo算法(IBM 360/91)是乱序执行的奠基——通过保留站(reservation station)仲裁并分发就绪的指令。"},
            {"heading": "数据流与ROB深度", "content": "乱序执行核心流程：Fetch→Decode→Rename→Dispatch到保留站→Issue(操作数就绪后)→Execute→Write Result广播到公共数据总线(CDB,Common Data Bus)→Complete→Commit(按ROB顺序写入寄存器文件和PC)。ROB深度决定飞行中(in-flight)指令的最大数量——现代CPU(Skylake:224, Zen4:320条目)。ROB满时前端必须停顿。Store Buffer和Load Queue解决内存访问重排序——先加载(load)可越过之前的store当无别名(内存消岐/分预测)。"},
            {"heading": "关键结论", "content": "1. 乱序执行由WAR和WAW促发(真数据依赖RAW不能用Rename解决) 2. 推测执行(speculation)在分支预测后执行未来的指令(可能被抛弃——错误路径squash) 3. 乱序执行的验证难点——正确恢复精确异常(precise exceptions) 4. 存储前向(Store-to-Load Forwarding)减少数据要通过缓存的时间 5. 超标量(多发射)+乱序执行协同交付高IPC"},
            {"heading": "关联知识点", "content": "[[计算机组成原理-分支预测器深度]] [[计算机组成原理-流水线与冒险]] [[编译原理-代码生成与优化]]"}
        ]
    },
    {
        "dir_name": "计算机组成原理",
        "file_stem": "SIMD与向量化",
        "title": "SIMD与向量化",
        "course": "计算机组成原理",
        "chapter": "指令集",
        "difficulty": "INTERMEDIATE",
        "tags": ["计算机组成", "SIMD", "向量化", "AVX", "NEON"],
        "aliases": ["SIMD", "Vectorization", "AVX-512", "NEON"],
        "source": "Intel Intrinsics Guide; ARM NEON Programmer's Guide; H&P《Computer Architecture》Ch 4",
        "sections": [
            {"heading": "核心定义", "content": "SIMD(Single Instruction Multiple Data,单指令多数据流)是数据级并行模式——一条指令同时处理多个数据元素。x86系列：MMX(64位, 1997)→SSE(128位)→AVX(256位, Sandy Bridge 2011)→AVX-512(512位, Skylake-SP 2017)。ARM系列：NEON(128位, ARMv7+)。SIMD寄存器(DIR,XMM/YMM/ZMM寄存器或V寄存器)按lane划分——每个lane对应一个独立操作。编译器的自动向量化(automatic vectorization)将标量循环转换为SIMD指令——受限于指针别名和循环依赖。"},
            {"heading": "强制向量化技巧", "content": "手动SIMD编程通过编译器intrinsics(如_mm_add_ps SSE加法)或直接用汇编。Intel ISPC(Implicit SPMD Program Compiler)提供C变种语言编译为SIMD代码。常见向量化模式：map(逐元素运算: f(x+1)→SIMD add)、reduce(求和:使用vector→shuffle reduction→横向加法)、scatter/gather(AVX2的vgatherdps根据索引向量加载不连续元素)。内存对齐(align to vector width——32/64字节对齐)减少跨cache line访问惩罚。Masked操作(AVX-512)按mask选择性应用操作——替代分支。"},
            {"heading": "关键结论", "content": "1. AVX-512频率降低(CPU降频CPU基频以补偿功率)——这被称为AVX-512 offset 2. 编译器自动向量化通常被别名和复杂控制流阻挡(使用__restrict关键字) 3. 循环展开和reduction模式是自动向量化的关键 4. 向量长度增加和CPU频率的关系需要考虑(轻量SIMD在多数任务上优于重SIMD的降频困境) 5. 许多典型算法(矩阵乘法/sum/histogram)在SIMD下可见2x-16x加速"},
            {"heading": "关联知识点", "content": "[[计算机组成原理-乱序执行与ROB]] [[计算机组成原理-GPU渲染管线与GPGPU]] [[C语言深入-restrict限定符]]"}
        ]
    },
    {
        "dir_name": "计算机组成原理",
        "file_stem": "RISC-V特权架构",
        "title": "RISC-V特权架构",
        "course": "计算机组成原理",
        "chapter": "指令集架构",
        "difficulty": "INTERMEDIATE",
        "tags": ["计算机组成", "RISC-V", "特权架构", "指令集"],
        "aliases": ["RISC-V Privileged Architecture", "Machine Mode", "Supervisor Mode"],
        "source": "RISC-V Privileged Specification v1.12; Patterson & Waterman《The RISC-V Reader》; RISC-V International",
        "sections": [
            {"heading": "核心定义", "content": "RISC-V特权架构定义了三个(或四个)特权级(Modes)：Machine Mode(M-mode,最高权限——固件/安全管理器)，Supervisor Mode(S-mode,操作系统内核)，User Mode(U-mode,应用程序)。可选Hypervisor Mode(H-mode,H扩展——虚拟机监视器)。每个级别有独立的CSR(Control and Status Register)集合。模式切换通过异常(exception)和中断(interrupt)触发——mret/sret指令从陷阱处理返回。物理内存保护(PMP)在M-mode配置以约束低特权模式的物理内存访问。"},
            {"heading": "中断与虚拟内存", "content": "RISC-V的中断有三种：软件中断(通过设置CSR中的相应位进而触发)、定时器中断(timer)、外部中断(PLIC——Platform-Level Interrupt Controller)。AI(AIA Advanced Interrupt Architecture)引入了MSI(Message-signaled Interrupts)。虚拟内存支持Sv32(两级页表, 32位)、Sv39(三级页表, 39位VA, RV64)、Sv48和Sv57(更大的虚拟地址空间)。TLB的管理通过SFENCE.VMA指令同步——将VA或ASID指定的TLB条目失效。每个页表项包含accessed(A)和dirty(D)位(硬件管理或软件模拟)。"},
            {"heading": "关键结论", "content": "1. RISC-V的开放性令其特权架构极适用于教学和定制处理器 2. M-mode在简单的嵌入式系统中可以实现全部功能(无OS——裸机/bare metal) 3. 可选ISA扩展(Vector/Kryptography等)可通过CSR的misa寄存器检测 4. 调试支持(JTAG触发模块——trigger module) 5. 不同于x86的ring模型,RISC-V的固定三模式相对更简单一致"},
            {"heading": "关联知识点", "content": "[[计算机组成原理-指令集架构]] [[计算机组成原理-分支预测器深度]] [[操作系统-虚拟内存与TLB]]"}
        ]
    },
    {
        "dir_name": "计算机组成原理",
        "file_stem": "GPU渲染管线与GPGPU",
        "title": "GPU渲染管线与GPGPU",
        "course": "计算机组成原理",
        "chapter": "并行架构",
        "difficulty": "INTERMEDIATE",
        "tags": ["计算机组成", "GPU", "GPGPU", "渲染管线", "CUDA"],
        "aliases": ["GPU Architecture", "GPGPU", "SIMT", "CUDA"],
        "source": "NVIDIA CUDA Programming Guide; H&P《Computer Architecture》Ch 4 GPU; Akeley & Hanrahan《Real-Time Graphics》",
        "sections": [
            {"heading": "核心定义", "content": "GPU(Graphics Processing Unit)是大规模并行多线程架构。图形渲染管线阶段：顶点处理(vertex shader)→图元装配→光栅化(rasterization)→像素处理(fragment shader)→输出合并。GPGPU(General-Purpose GPU)将GPU用于非图形计算。NVIDIA的CUDA编程模型基于SIMT(Single Instruction Multiple Threads)——一组32个线程(warp)锁定在同一指令上执行(SIMD-like)。SM(Streaming Multiprocessor)是核心执行单元——每个SM有多个warp scheduler和大量的计算单元以及寄存器文件。"},
            {"heading": "CUDA核心抽象", "content": "CUDA的核心概念：grid→blocks→threads层次——所有线程在相同代码（kernel）但通过threadIdx/blockIdx区分各自处理的数据。共享内存(shared memory, 每个block可见, 约48-164KB/SM)是程序员管理的快速on-chip存储器(类似L1 cache但需显式同步——__syncthreads)。Glowal memory访问必须对齐(optimal alignment)且合并(coalesced)——相邻线程访问相邻地址才有效率(否则导致多次transaction)。Occupancy(占用率——活跃warp/SM上最大warp)是隐藏memory latency的关键(高占用>延迟容忍)。"},
            {"heading": "关键结论", "content": "1. GPU不适合分支密集型算法(同一warp内分支diverge——损失性能) 2. GPU的寄存器压力(register pressure)限制活跃线程数 3. Tensor Core(Volta+)提供专门的矩阵乘法加速(适合深度学习) 4. 与CPU的同步需通过事件/stream(cudaMemcpyAsync/cudaStreamSynchronize) 5. Compute Capability决定了可用的CUDA特性版本"},
            {"heading": "关联知识点", "content": "[[计算机组成原理-SIMD与向量化]] [[计算机组成原理-CPU缓存与局部性原理]] [[计算机图形学-PBR材质系统]]"}
        ]
    },

    # ═══════════════════════════════════════════════════════════════
    # 编译原理 — 5 supplemental topics
    # ═══════════════════════════════════════════════════════════════
    {
        "dir_name": "编译原理",
        "file_stem": "LLVM-IR与优化Pass",
        "title": "LLVM IR与优化Pass",
        "course": "编译原理",
        "chapter": "编译器框架",
        "difficulty": "ADVANCED",
        "tags": ["编译原理", "LLVM", "IR", "Pass", "优化"],
        "aliases": ["LLVM IR", "Optimization Pass", "SIL"],
        "source": "LLVM官方文档; Lattner & Adve 2004 (LLVM paper);《Getting Started with LLVM Core Libraries》",
        "sections": [
            {"heading": "核心定义", "content": "LLVM IR(中间表示)是LLVM编译框架的核心——基于SSA(Static Single Assignment)形式的类型化低级表示。每个变量精确赋值一次(通过phi节点在控制流合并处选择不同来源的值)。LLVM IR三级：内存表示(in-memory——C++ API)、bitcode(.bc——磁盘存储)、汇编文本(.ll——可读格式)。Pass系统将优化组织为模块化的pass——每pass读取/修改IR然后传递到下一pass。Pass Manager(新PM)按依赖和阶段管理pass调度——Analysis passes提供分析结果(别名/支配树/loop info)。"},
            {"heading": "经典Pass范例", "content": "最重要的LLVM优化pass：1.)mem2reg——将alloca/load/store提升为SSA寄存器(将栈变量转为虚寄存器) 2.)GVN(Global Value Numbering)——消除冗余计算(值等价) 3.)LICM(Loop Invariant Code Motion)——将循环不变量移到循环前 4.)Loop Unswitch——将循环内条件分支提升为循环外的两个循环 5.)InstCombine——指令级别的窥孔优化(千条规则)。LTO(Link-Time Optimization)通过IR在链接时重新应用全程序优化pass(ThinLTO平衡优化效果和可伸缩性)。"},
            {"heading": "关键结论", "content": "1. LLVM IR不是可移植汇编——它是编译器优化的输入/输出语言 2. PGO(Profile-Guided Optimization)向优化pass提供运行时数据 3. 自定义pass可编写(如添加特定领域的优化) 4. LLVM的IR独立性将前端(Clang, Rust, Swift)和后端(x86/ARM/RISC-V)彻底解耦 5. Opaque pointer(LLVM 15+)简化IR——不再需要每个指针声明类型"},
            {"heading": "关联知识点", "content": "[[编译原理-JIT编译原理]] [[编译原理-语法树与中间表示]] [[C语言深入-编译优化选项]]"}
        ]
    },
    {
        "dir_name": "编译原理",
        "file_stem": "JIT编译原理",
        "title": "JIT编译原理",
        "course": "编译原理",
        "chapter": "运行时编译",
        "difficulty": "ADVANCED",
        "tags": ["编译原理", "JIT", "即时编译", "JVM", "V8"],
        "aliases": ["Just-In-Time Compilation", "JIT", "Adaptive Compilation"],
        "source": "OpenJDK HotSpot源码; V8 Blog: How V8 measures real-world performance; Aycock 2003 (JIT survey)",
        "sections": [
            {"heading": "核心定义", "content": "JIT(Just-In-Time,即时编译)在运行时将字节码或中间代码编译为原生机器码——结合了解释执行的灵活性与AOT编译的性能。触发编译的条件：方法调用计数(热点阈值)、循环迭代计数(OSR,On-Stack Replacement——将解释执行的循环体中途替换为编译版本)。分层编译(tiered compilation)在快速编译+基础优化(代码热)和慢编译+激进优化(真正热点)之间平衡。Deoptimization——当JIT基于乐观假设(如类型固定)生成的代码假设被打破时回退到解释模式。"},
            {"heading": "编译器技术比较", "content": "HotSpot(JVM)使用模板解释器(template interpreter——通过宏汇编为每个字节码生成机器码片段)，C1(快速编译+基本优化)和C2(基于sea-of-nodes IR的重型优化)。V8(Chrome/Node.js)使用Ignition(字节码解释器)+TurboFan(多级优化JIT)。V8之前使用Crankshaft和Full-Codegen但已被淘汰。LuaJIT的trace compiler(追踪编译器)——在运行时记录热路径的执行轨迹生成专门化代码(只需优化被执行的路径，不用处理整个函数)。Inline caching缓存类型分发结果——也是JIT技术的一种。"},
            {"heading": "关键结论", "content": "1. JIT的预热成本(warm-up costs)在实验对比中不可忽略——稳态性能分析需要排除预热 2. 去优化(deopt)的粒度影响——不能太粗(roll-back path太大)也不能太细(检查开销大) 3. AOT+JIT混合(PGO驱动)正在成为趋势(Graal Native Image/PGO、OpenJDK Leyden项目) 4. JIT使得profile-guided optimization在运行时自动完成(动态profiling) 5. JIT使Java/C#虚拟机性能接近(有时超过)C/C++静态编译"},
            {"heading": "关联知识点", "content": "[[编译原理-LLVM IR与优化Pass]] [[编译原理-字节码虚拟机设计]] [[Java深入-JIT编译与热点]]"}
        ]
    },
    {
        "dir_name": "编译原理",
        "file_stem": "垃圾回收算法深度",
        "title": "垃圾回收算法深度",
        "course": "编译原理",
        "chapter": "运行时系统",
        "difficulty": "ADVANCED",
        "tags": ["编译原理", "GC", "垃圾回收", "内存管理"],
        "aliases": ["Garbage Collection", "GC Algorithms", "Tracing GC"],
        "source": "Jones, Hosking & Moss《The Garbage Collection Handbook》; Wilson 1992 (GC survey); OpenJDK GC源码",
        "sections": [
            {"heading": "核心定义", "content": "垃圾回收(GC/Garbage Collection)自动释放不可达对象占用的内存。三大Tracing GC基本算法：标记-清除(Mark-Sweep——标记所有从根可达对象,释放未标记); 标记-复制(Mark-Compact/Copy——将幸存对象移动到新区域,原地回收整个旧区域); 引用计数(Reference Counting——每个对象的引用计数归零即释放,无法处理循环引用)。分代假设(Generational Hypothesis)：大多数对象年轻时死亡——因此对新生代频繁回收(小区域,使用Copy),老生代不频繁回收(大区域,使用Mark-Sweep-Compact)。"},
            {"heading": "现代GC实现", "content": "JVM的GC进化：Serial(单线程)→Parallel(多线程并行STW)→CMS(并发,尽量与mutator并行——已废弃)→G1(区域化region,增量回收,预测暂停时间)→ZGC(着色指针,亚毫秒暂停,16TB堆)→Shenandoah(并发压实)。G1将堆化分为等大小的region(Eden/Survivor/Old)，Young GC(新生代复制到survivor)，Mixed GC(部分老年代回收,选择垃圾最多的region)。Barrier(write barrier——SATB for G1, read barrier——ZGC的load barrier)在mutator执行时追踪对象引用变化。"},
            {"heading": "关键结论", "content": "1. Stop-The-World(STW)不能完全消除——只能最小化(GC根扫描+部分references update需要STW) 2. GC暂停时间vs吞吐量的平衡是GC选择的根本冲突 3. 弱引用(WeakReference/ReferenceQueue)是GC-感知的应用优化(java.lang.ref) 4. Pointer bumping(碰撞指针——简单地将指针移动分配内存)合并到copying GC效率极高 5. GC的并发实现复杂——需要解决mutator与collector间的race(tri-color写前屏障/读屏障)"},
            {"heading": "关联知识点", "content": "[[编译原理-字节码虚拟机设计]] [[Java深入-JVM架构与字节码]] [[Go语言-编译与链接过程]]"}
        ]
    },
    {
        "dir_name": "编译原理",
        "file_stem": "字节码虚拟机设计",
        "title": "字节码虚拟机设计",
        "course": "编译原理",
        "chapter": "虚拟机",
        "difficulty": "ADVANCED",
        "tags": ["编译原理", "字节码", "虚拟机", "JVM", "WASM"],
        "aliases": ["Bytecode VM Design", "JVM", "WASM", "Stack vs Register VM"],
        "source": "JVM Spec §2 (The Structure of the JVM); WASM Spec; Shi et al. 2005 (Virtual machine showdown)",
        "sections": [
            {"heading": "核心定义", "content": "字节码虚拟机(bytecode VM)是在硬件和软件之间提供一层抽象的运行时系统。两大架构：栈式虚拟机(JVM/WASM/CPython)——指令零操作数,隐式从操作数栈push/pop(mnemonic: iconst_1, iload, iadd)；寄存器式虚拟机(Dalvik/Lua 5+/V8 Ignition)——指令携带寄存器号,显式操作数(mnemonic: add r0, r1, r2)。栈式VM代码更紧凑(无操作数字段)，寄存器式VM指令数更少(快约47%在解释模式评测但会导致每条指令更宽)。"},
            {"heading": "WASM设计", "content": "WebAssembly(WASM)以安全沙箱为第一优先设计目标。结构化控制流(无任意jump——block/loop/if阶梯式结构替代JVM的goto)；线性内存模型(单个内存区域的字节数组——安全性通过边界检查保证)；类型安全验证(单次通过的字节码验证——验证后的任何指令不可能破坏安全)。紧凑的二进制格式(LEB128编码整数——每条指令1-3字节)。JVM字节码约205条指令，WASM约200条指令，但两者的设计理念显著不同(WASM为安全优先，JVM为OO优先)。"},
            {"heading": "关键结论", "content": "1. 栈式VM的指令密度大——总代码尺寸可能更小 2. 寄存器式VM需要更大的指令但通常因使用更少dispatch而更快 3. WASM的非结构化控制流被限制(安全性胜过性能——不能表达不可约循环) 4. 直接线程解释器(Direct Threaded Interpreter/DTI——使用汇编尾部跳转表)显著加速解释 5. AOT编译WASM在all现代引擎中都得到支持(绕过解释器)"},
            {"heading": "关联知识点", "content": "[[编译原理-JIT编译原理]] [[编译原理-垃圾回收算法深度]] [[Java深入-JVM架构与字节码]]"}
        ]
    },
    {
        "dir_name": "编译原理",
        "file_stem": "静态分析工具链",
        "title": "静态分析工具链",
        "course": "编译原理",
        "chapter": "程序分析",
        "difficulty": "ADVANCED",
        "tags": ["编译原理", "静态分析", "抽象解释", "lint", "安全"],
        "aliases": ["Static Analysis", "Abstract Interpretation", "Lint"],
        "source": "Cousot & Cousot 1977 (Abstract Interpretation); CodeSonar/Coverity文档; Nielson et al.《Principles of Program Analysis》",
        "sections": [
            {"heading": "核心定义", "content": "静态分析(static analysis)在不运行程序的情况下推理程序行为。抽象解释(abstract interpretation, Cousot 1977)提供了理论基础——程序语义在抽象域(abstract domain)中进行计算：将无限的concrete state空间映射到有限的abstract state空间。抽象域的选取决定精度和代价——符号域(Sign——正/负/零/混合/未知)、区间域(Interval——[a,b])、多面体域(Polyhedron——线性不等式约束)、八边形域(Octagon——±x±y<=c形式约束)由粗略到精确递进。"},
            {"heading": "工具分类", "content": """数据流分析(Data-flow Analysis)框架：reaching definitions/live variables/available expressions → 求解固定点方程(forward/backward may/must analysis)。AST分析工具：clang-analyzer(LLVM,路径敏感的bug查找——内存泄漏/使用已释放内存)、Infer(Facebook,分离逻辑——生成模块化报告/适合增量检测)、flow-sensitive(考虑控制流顺序)/path-sensitive(跟踪路径条件)增加精度。Taint Analysis(污点分析)追踪"tainted"数据传播——安全漏洞检测(SQL注入/XSS)。Modern linters(SonarQube, PMD)往往混用不同技术。"""},
            {"heading": "关键结论", "content": "1. 静态分析永远不能完美(归约到停机问题)——存在漏报(false negative)和误报(false positive)的权衡 2. Sound(不遗漏)与Complete(无假警)不可兼得 3. 抽象解释是编译器的正确性理论基础之一(Airbus A380就用抽象解释证明关键飞控软件无运行时错误) 4. 静态分析的时间成本通常远小于测试——在开发早期快速发现bug 5. LSP(Language Server Protocol)使分析工具编辑器中即时反馈(如Rust Analyzer/Clangd)"},
            {"heading": "关联知识点", "content": "[[编译原理-语法树与中间表示]] [[编译原理-LLVM IR与优化Pass]] [[软件工程-代码审查与质量保证]]"}
        ]
    },

    # ═══════════════════════════════════════════════════════════════
    # 数据库原理 — 5 supplemental topics
    # ═══════════════════════════════════════════════════════════════
    {
        "dir_name": "数据库原理",
        "file_stem": "查询优化器深度",
        "title": "查询优化器深度",
        "course": "数据库原理",
        "chapter": "查询处理",
        "difficulty": "ADVANCED",
        "tags": ["数据库", "查询优化器", "连接顺序", "基数估计", "成本模型"],
        "aliases": ["Query Optimizer", "Join Ordering", "Cardinality Estimation"],
        "source": "Selinger et al. 1979 (System R Optimizer); Garcia-Molina et al. Ch 15-16; PostgreSQL optimizer源码",
        "sections": [
            {"heading": "核心定义", "content": "查询优化器(query optimizer)是关系数据库最重要的组件——将声明式SQL转换为有效率的执行计划。代价模型(cost model)考虑IO(磁盘页读取数——seq scan vs random access)、CPU(过滤计算)和网络(分布式表)。经典的System R算法使用自底向上的动态规划枚举所有可能的连接顺序(join ordering)：对n个关系,搜索空间是Catalan(n)≈4^n/(n^(3/2)),实际优化通常将n限制在12(默认)并将其中的子集预处理为interesting orders。基数估计(cardinality estimation)预测操作输出的行数。"},
            {"heading": "现代优化器架构", "content": "PostgreSQL使用的优化器是System R的直接后代。连接方式：Nested Loop(小表驱动大表+内表有索引)、Hash Join(构建哈希表→探测)、Merge Join(双排序后双指针扫描)。CBO(Cost-Based Optimizer) vs RBO(Rule-Based——简单的启发式规则)。Cascades优化器(The Volcano/Cascades framework)提供更灵活的模式：使用transformation rule(逻辑等价改写)和implementation rule(逻辑操作→物理操作)在待搜索空间中拓扑式扩展。memo结构存储已搜索的优化中间结果。"},
            {"heading": "关键结论", "content": "1. 基数估计错误是优化器选择坏计划的主要原因(misestimation——基数偏估10倍可能导致执行时间偏1000x) 2. 统计信息(histograms——MCV,distinct度)需要ANALYZE更新(避免过期数据导致错误的join order) 3. 优化器超时——大型join(~20关系)使用启发式(genetic query optimization/GEQO) 4. 现代优化器也考虑参数化查询——prepared statement的计划固定vs re-plan 5. 机器学习驱动的基数估计(learned cardinality estimation)是热门研究方向"},
            {"heading": "关联知识点", "content": "[[数据库原理-SQL基础与查询]] [[数据库原理-索引B+树与哈希索引]] [[算法设计与分析-动态规划]]"}
        ]
    },
    {
        "dir_name": "数据库原理",
        "file_stem": "LSM-Tree与LevelDB",
        "title": "LSM-Tree与LevelDB",
        "course": "数据库原理",
        "chapter": "存储引擎",
        "difficulty": "ADVANCED",
        "tags": ["数据库", "LSM-Tree", "LevelDB", "RocksDB", "存储引擎"],
        "aliases": ["Log-Structured Merge-Tree", "LSM", "LevelDB"],
        "source": "O'Neil et al. 1996 (LSM-Tree); LevelDB/RocksDB源码; Luo & Carey 2020 (LSM-based storage survey)",
        "sections": [
            {"heading": "核心定义", "content": "LSM-Tree(Log-Structured Merge-Tree)是针对写密集型工作负载优化的存储结构。核心思想：将随机写转化为顺序写——新写入首先在内存排序缓冲区(MemTable,通常使用跳表skiplist实现)，写满后刷入磁盘形成不可变的有序文件(SSTable)。后台compaction(合并compaction)持续合并多层SSTable——删除重复键和已标记删除的记录。读操作需检查MemTable+最近的SSTable(通过bloom filter过滤不在的SSTable)+更深层的SSTable(因合并延迟)。"},
            {"heading": "Leveled vs Tiered", "content": "LSM合并策略分两大类：Tiered(分层合并——LevelDB/RocksDB,各层大小按倍数增长(level0:256MB,level1:1GB,level2:10GB...),一定大小触发compaction合并到下一层，读取最差需检查O(log N)个SSTable) vs Tiered(Tiered合并——Cassandra/ScyllaDB,合并一组SSTable成为一个更大的SSTable)。RocksDB(LevelDB的优化版)通过多线程compaction/压缩字典/prefix bloom filter实现极高性能——是许多现代数据库(TiKV/MyRocks/ArangoDB)的存储引擎。"},
            {"heading": "关键结论", "content": "1. LSM-Tree牺牲读性能换取写性能——适合写密集型场景(日志/时序数据/IoT) 2. 写放大(write amplification)是LSM的主要代价——每个key可能因compaction被写多次 3. 读放大(read amplification)由需要搜索多层引起——bloom filter缓解但可能误报 4. Compaction的IO风暴(compaction storm)导致性能抖动——需要限速 5. B+树更适合读密集事务(OLTP)，LSM适合写密集日志和时序数据(特别是append-only场景)"},
            {"heading": "关联知识点", "content": "[[数据库原理-索引B+树与哈希索引]] [[数据库原理-事务与并发控制]] [[操作系统-文件系统与IO基础]]"}
        ]
    },
    {
        "dir_name": "数据库原理",
        "file_stem": "列存储与OLAP",
        "title": "列存储与OLAP",
        "course": "数据库原理",
        "chapter": "存储引擎",
        "difficulty": "ADVANCED",
        "tags": ["数据库", "列存储", "OLAP", "压缩", "数据仓库"],
        "aliases": ["Column Store", "OLAP", "Data Warehouse"],
        "source": "Stonebraker et al. 2005 (C-Store); Abadi et al. 2008 (Column-Stores vs Row-Stores); ClickHouse文档",
        "sections": [
            {"heading": "核心定义", "content": "列存储(column store)将每一列的数据独立存储(而非行式存储的每行连续存储)。OLAP(Online Analytical Processing)查询通常扫描全表但只涉及少数列——列存储只需读取涉及的列(减少IO)，且对单列有更好的压缩效果(列内数据域高度重复)。核心压缩编码：字典编码(Dictionary Encoding——将值映射为整数ID)、游程编码(Run-Length——连续相同值：value+count)、Delta编码(存储相邻值的差值)、位图编码(Bitmap——对每个可能值建bit向量)。"},
            {"heading": "向量化执行", "content": "列存储通常采用向量化执行(vectorized execution)——一次处理整个数据块(如1024行vector)而非逐行处理。这确保CPU的SIMD和循环流水充分发挥。ClickHouse和MonetDB是向量化执行的典型。C-Store的projection结构物化了部分列的预计算——满足频繁查询模式的覆盖索引。列存储压缩效果极好(通常10x-100x缩小)，因为列数据往往重复值多。现代混合系统中，列存储常作为行存储HTAP(Hybrid Transactional/Analytical Processing)的辅助结构。"},
            {"heading": "关键结论", "content": "1. 列存储不适用于频繁点查询/小范围行查询(因读取整个列但仅需几行) 2. 列存储对聚合计算(sum/avg/count)极高效(只需扫描所需列) 3. Parquet/ORC是开放格式的列存储文件格式(适用于数据湖Hive/Spark) 4. 列存储结合SIMD在分析场景中可达到接近内存带宽极限的性能 5. 列存储的更新(in-place update)昂贵——通常通过追加+合并结构(LSM-like compaction)"},
            {"heading": "关联知识点", "content": "[[数据库原理-LSM-Tree与LevelDB]] [[数据库原理-查询优化器深度]] [[计算机组成原理-SIMD与向量化]]"}
        ]
    },
    {
        "dir_name": "数据库原理",
        "file_stem": "数据库日志与恢复",
        "title": "数据库日志与恢复",
        "course": "数据库原理",
        "chapter": "事务管理",
        "difficulty": "ADVANCED",
        "tags": ["数据库", "日志", "恢复", "WAL", "ARIES"],
        "aliases": ["Write-Ahead Logging", "ARIES", "Crash Recovery"],
        "source": "Mohan et al. 1992 (ARIES); Gray & Reuter《Transaction Processing》Ch 9; PostgreSQL WAL文档",
        "sections": [
            {"heading": "核心定义", "content": "WAL(Write-Ahead Logging,预写日志)是数据库崩溃恢复的基础。规则：日志记录必须在数据页面写入磁盘之前先写入稳定的日志存储(write-ahead)。日志记录(LSN, Log Sequence Number)为每次日志写入分配单调递增的编号。ARIES(Algorithm for Recovery and Isolation Exploiting Semantics, 1992)是WAL-based恢复的标准算法。三个步骤：分析(Analysis——从最近的checkpoint开始正向扫描日志重建脏页表和事务状态)、重做(Redo——从最老脏页的最小LSN开始重复历史,确保所有已提交的更改到达磁盘)、撤销(Undo——逆向扫描日志撤销未提交事务的更改,写入补偿日志记录CLR)。"},
            {"heading": "Checkpoint与优化", "content": "Checkpoint(检查点)定期将脏页刷新到磁盘并记录checkpoint日志——减少恢复时需要回放的日志量。Fuzzy checkpoint(模糊检查点)允许在ckpt进行时系统继续运行——记录当前脏页列表的快照而不是将所有脏页立即flush。PostgreSQL的WAL采用段文件(segment file, 16MB each)。日志归档(archiving)用于PITR(Point-In-Time Recovery)。MVCC+WAL组合在PostgreSQL中：WAL记录tuple的修改操作——热备用(streaming replication)将WAL流应用到备用服务器。"},
            {"heading": "关键结论", "content": "1. WAL有性能成本(必须sync日志)但消除数据损坏风险 2. 日志记录必须幂等——重做期间可能已部分应用但不完整 3. 恢复时间与检查点的频率权衡(更多检查点=更短恢复但更多普通操作开销) 4. ARIES的compensation log records(CLR)处理系统在undo期间崩溃 5. 日志压缩(Vacuum WAL)对控制磁盘使用很重要"},
            {"heading": "关联知识点", "content": "[[数据库原理-事务与并发控制]] [[数据库原理-LSM-Tree与LevelDB]] [[操作系统-文件系统与IO基础]]"}
        ]
    },
    {
        "dir_name": "数据库原理",
        "file_stem": "数据库安全与SQL注入防御",
        "title": "数据库安全与SQL注入防御",
        "course": "数据库原理",
        "chapter": "安全",
        "difficulty": "INTERMEDIATE",
        "tags": ["数据库", "安全", "SQL注入", "访问控制", "加密"],
        "aliases": ["Database Security", "SQL Injection Defense", "Access Control"],
        "source": "OWASP Top Ten; SQL标准ISO/IEC 9075; PostgreSQL安全管理文档; Bell-La Padula模型",
        "sections": [
            {"heading": "核心定义", "content": "数据库安全层次：1.)访问控制(GRANT/REVOKE——基于角色的访问控制RBAC) 2.)行级安全(RLS/Row-Level Security——基于用户属性的过滤条件自动附加到查询) 3.)数据加密(透明数据加密TDE——加密文件/表空间——后丢失密钥数据永久不可用) 4.)加密传输(TLS between client and DB server) 5.)审计日志(audit——记录所有敏感查询的who/when/what)。SQL注入是OWASP #1:注入攻击——不信任的输入直接拼接SQL字符串导致攻击者任意执行SQL。"},
            {"heading": "注入防御", "content": "SQL注入防御的黄金法则：1.)永远参数化查询(prepared statement——?占位符,将查询编译阶段与参数绑定阶段分离,防止SQL语法注入) 2.)输入验证(严格的类型和格式验证——白名单,黑名单不够) 3.)最小权限原则(应用程序的数据库账户仅拥有必需的权限) 4.)ORM的正确使用(虽然使用ORM也不能完全免疫注入——对native SQL查询仍要参数化)。存储过程调用也需要参数化。二阶SQL注入——攻击数据首先存储在数据库中(looks clean),随后被其他查询读取和执行——需全部数据始终参数化(不使用拼接)。"},
            {"heading": "关键结论", "content": "1. 永远不要信任输入——always parameterize 2. 数据库应用账户绝不应是owner(db_owner)账户 3. WAF(Web Application Firewall)可以检测注入攻击特征但不保证全面防御 4. 信息安全标准(PCI DSS/HIPAA/GDPR)要求对数据库中的PII加密或假名化 5. 安全扫描(静态分析/动态测试/渗透测试)应定期进行"},
            {"heading": "关联知识点", "content": "[[数据库原理-查询优化器深度]] [[信息安全-SQL注入与XSS防御]] [[信息安全-访问控制与身份认证]]"}
        ]
    },

    # ═══════════════════════════════════════════════════════════════
    # 离散数学 — 5 supplemental topics
    # ═══════════════════════════════════════════════════════════════
    {
        "dir_name": "离散数学",
        "file_stem": "有限状态机与正则语言",
        "title": "有限状态机与正则语言",
        "course": "离散数学",
        "chapter": "自动机理论",
        "difficulty": "INTERMEDIATE",
        "tags": ["离散数学", "有限状态机", "正则语言", "DFA", "NFA"],
        "aliases": ["Finite State Machine", "Regular Language", "DFA/NFA"],
        "source": "Sipser《Introduction to the Theory of Computation》Ch 1; Hopcroft, Motwani & Ullman《自动机理论》Ch 2; Kleene 1956",
        "sections": [
            {"heading": "核心定义", "content": "有限状态机(FSM)是具有有限状态的抽象计算模型。DFA(确定有限自动机)由五元组(Q,Σ,δ,q0,F)定义：有限状态集、有限字母表、转移函数(δ:Q×Σ→Q，每个状态和输入符号的下一状态唯一确定)、初始状态、接受状态集。NFA(非确定有限自动机)的转移函数映射到状态集(允许多选)。NFAs可模拟DFA——通过子集构造(Subset Construction)转换：状态数可能从n扩展到2^n。正则语言是能被DFA/NFA识别的语言类——也是能用正则表达式描述的语言。"},
            {"heading": "泵引理与界限", "content": "正则语言的泵引理(Pumping Lemma)：对于正则语言L，存在泵常量p，使任何长度>=p的串w∈L可分解为w=xyz满足|xy|<=p, |y|>0, 对任意i>=0，xy^iz∈L。泵引理用于证明一个语言非正则(如{a^n b^n | n>=0}不是正则——需要'记忆'的有限状态无法计数到无限)。正则语言的封闭性：并、交、补、反转、同态。Myhill-Nerode定理刻画正则语言——等价类数有限。DFA最小化算法合并等价的不可区分状态。"},
            {"heading": "关键结论", "content": "1. DFA和正则表达式在表达能力上等价(Kleene定理) 2. 任何正则语言都有唯一的(同构)最小DFA 3. NFA→DFA是指数膨胀——最坏情况2^n状态 4. 正则表达式在grep/lexer/模式匹配中有重要实际应用 5. 非正则语言的示例平衡括号语言(需要栈存储——下推自动机PDA)"},
            {"heading": "关联知识点", "content": "[[离散数学-Church-Turing论题]] [[编译原理-词法分析与语法分析]] [[离散数学-自动机与形式语言]]"}
        ]
    },
    {
        "dir_name": "离散数学",
        "file_stem": "Church-Turing论题",
        "title": "Church-Turing论题",
        "course": "离散数学",
        "chapter": "可计算性理论",
        "difficulty": "ADVANCED",
        "tags": ["离散数学", "Church-Turing", "可计算性", "图灵机"],
        "aliases": ["Church-Turing Thesis", "Computability", "Turing Machine"],
        "source": "Turing 1936 (On Computable Numbers); Church 1936; Sipser Ch 3-5; Copeland《The Essential Turing》",
        "sections": [
            {"heading": "核心定义", "content": "Church-Turing论题断言：所有直观上可计算的函数正好是λ演算可定义的函数(Church)和图灵机可计算的函数(Turing)。这些形式定义等价地刻画了'可计算'——即图灵完备性。物理Church-Turing论题：任何物理上可实现的计算过程都可以被标准图灵机模拟。量子计算不违反Church-Turing论题——量子图灵机等价于普通图灵机(在可计算性上——计算能力完全相同，仅在效率上有潜在优势(量子加速))。"},
            {"heading": "图灵机详解", "content": "图灵机(TM)由无穷长的纸带(tape)、读写头(head)、有限状态控制器组成。一条指令:(当前状态,读取符号)→(新状态,写入符号,左移/右移)。通用图灵机(UTM)可以通过编码任何TM的描述在带子上模拟该TM——是'存储程序'概念的数学根基。可变体:多带图灵机、非确定图灵机(NTM)、oracle machine(带玄机的TM——超越可计算函数)。停止问题(Halting Problem)是图灵机不可判定的——证明：假设推导出矛盾(对角线法)。"},
            {"heading": "关键结论", "content": "1. Church-Turing论题不是数学定理——它是关于物理实在的假设 2. λ演算、递归函数、寄存器机、Post系统都与图灵机等价 3. 图灵完备性(Turing-completeness)成为衡量计算系统能力的标准 4. 不可计算问题天然存在于计算机科学中(如死锁检测、最小程序长度) 5. 超计算(hypercomputation)模型试图定义超越图灵的机器——目前仅存在于理论中"},
            {"heading": "关联知识点", "content": "[[离散数学-有限状态机与正则语言]] [[离散数学-自动机与形式语言]] [[算法设计与分析-NP完全性理论与归约]]"}
        ]
    },
    {
        "dir_name": "离散数学",
        "file_stem": "拉姆齐理论",
        "title": "拉姆齐理论",
        "course": "离散数学",
        "chapter": "组合数学",
        "difficulty": "ADVANCED",
        "tags": ["离散数学", "拉姆齐理论", "组合数学", "Ramsey"],
        "aliases": ["Ramsey Theory", "Ramsey Numbers"],
        "source": "Ramsey 1930 (On a problem of formal logic); Graham, Rothschild & Spencer《Ramsey Theory》; van der Waerden 1927",
        "sections": [
            {"heading": "核心定义", "content": "拉姆齐理论(Ramsey Theory)揭示'完全的混沌不存在'——任何足够大的结构中必然存在有序的子结构。拉姆齐定理(图论版本)：给定正整数r和s，存在最小整数R(r,s)使得任何具有R(r,s)个顶点的完全图(每条边染红或蓝)，必定包含全红Kr或全蓝Ks子图。R(3,3)=6(6个人的聚会必存在3个互相认识或互相不认识的人)，R(4,4)=18，R(5,5)至今未知——仅知道界43到48，R(6,6)更未知(Paul Erdos:'如果外星人入侵并要求我们精确计算R(5,5)否则就摧毁地球,所有人都应贡献计算力;若要R(6,6)则应直接攻击外星人')。"},
            {"heading": "van der Waerden与推广", "content": "Van der Waerden定理(1927)：对任意k和r，存在W(k,r)使得任何{1,2,...,W}的r染色必然包含同花色的长k等差数列。类似地，Schur定理：将正整数分为有限数目的和集时，某集合必有x+y=z的三元组。Erdos-Szekeres定理：任何n^2+1个不同实数的序列包含长度>n的单调子序列。Hales-Jewett定理推广和高维化n个player的tictactoe(组合游戏)。Ramsey数极小上界由Erdos的概率方法给出(非构造性)。"},
            {"heading": "关键结论", "content": "1. 拉姆齐数计算极端困难——即使是小参数组合也可能超出目前的计算能力 2. 拉姆齐理论具有深刻的哲学内涵——完全的混沌不存在 3. 概率方法(非构造性)虽然在Ramsey下界证明有力但仍不足确定精确值 4. 理论在计算机科学的证明复杂性、通信复杂度和类型论方面有应用 5. Graham提出用Ramsey类型参数描述'大'数——如Graham's number"},
            {"heading": "关联知识点", "content": "[[离散数学-组合数学]] [[算法设计与分析-概率算法]] [[离散数学-有限状态机与正则语言]]"}
        ]
    },
    {
        "dir_name": "离散数学",
        "file_stem": "自动机与形式语言",
        "title": "自动机与形式语言",
        "course": "离散数学",
        "chapter": "形式语言",
        "difficulty": "INTERMEDIATE",
        "tags": ["离散数学", "自动机", "形式语言", "Chomsky谱系"],
        "aliases": ["Automata Theory", "Formal Languages", "Chomsky Hierarchy"],
        "source": "Chomsky 1956 (Three models); Hopcroft et al. Ch 4-8; Sipser Ch 2",
        "sections": [
            {"heading": "核心定义", "content": "Chomsky谱系按生成能力将形式语言分为四类：类型0(递归可枚举语言——图灵机)包含类型1(上下文有关语言CSL——线性有界自动机LBA)包含类型2(上下文无关语言CFL——下推自动机PDA)包含类型3(正则语言——有限自动机)。Context-Free Grammar(CFG)由(V,Σ,R,S)定义，产生式A→α(A为非终结符,α为任意串)。CFL中最重要的是括号匹配、回文和编程语言语法(通常近似CFL但不完全是)。"},
            {"heading": "下推自动机", "content": "Pushdown Automaton(PDA)= NFA + 栈(无限但LIFO)。PDA接受上下文无关语言：操作取决于状态、输入符号和栈顶符号，栈可以push/pop多个元素。上下文无关语言的泵引理(Pumping Lemma for CFL)：长字符串可抽出两段同步膨胀(uvwxy——u v^i w x^i y保持语言，v和x同时膨胀/收缩相同次数)。CFL的封闭性：并、连接、Kleene*——但交和补不封闭。CYK算法(O(n^3))在CNF形式(Chomsky Normal Form)中解析字符串。"},
            {"heading": "关键结论", "content": "1. 任何CFG可以转换为Chomsky标准化形式(产生式A→BC或A→a) 2. 大部分的编程语言句法接近但非完全CFL(C/Java需要symbol table分析——上下文有关) 3. 确定性PDA不能接受所有CFL(确定性DPDA ⊂ 非确定性NPDA) 4. LALR/SLR解析器是工程上对某些子类CFG的实现约束(更具实用型) 5. Chomsky谱系展示了语法和机器能力的完美对应——递增生成能力对应递增识别能力"},
            {"heading": "关联知识点", "content": "[[离散数学-有限状态机与正则语言]] [[离散数学-Church-Turing论题]] [[编译原理-词法分析与语法分析]]"}
        ]
    },
    {
        "dir_name": "离散数学",
        "file_stem": "模态逻辑",
        "title": "模态逻辑",
        "course": "离散数学",
        "chapter": "逻辑学",
        "difficulty": "ADVANCED",
        "tags": ["离散数学", "模态逻辑", "可能世界语义", "时序逻辑"],
        "aliases": ["Modal Logic", "Possible Worlds", "Temporal Logic"],
        "source": "Kripke 1963 (Semantics); Blackburn, de Rijke & Venema《Modal Logic》; Huth & Ryan《Logic in Computer Science》Ch 5",
        "sections": [
            {"heading": "核心定义", "content": "模态逻辑扩展经典命题逻辑以包含模态算子：必然□(box,necessarily)和可能◇(diamond,possibly)。标准语义基于Kripke框架(Kripke frames)——有向图(W,R)的'可能世界'集(W=worlds, R=accessibility relation)。□φ在世界w为真当所有从w可访问的世界中φ为真(必然性);◇φ当某些可访问世界中φ为真(可能性)。K是最弱的标准模态逻辑系统(仅规范化公理——□(φ→ψ)→(□φ→□ψ)和必然化规则——若φ是定理则□φ是定理)。"},
            {"heading": "逻辑间的对应", "content": "不同公理对应不同accessibility关系：D公理(□φ→◇φ)对应seriality(每世界至少有一个可访问世界)；T公理(□φ→φ)对应reflexivity(自反性——现实世界)即所有世界可访问自己；B公理(φ→□◇φ)对应symmetry(对称性)；4公理(□φ→□□φ)对应transitivity(传递性)——内部自省(正introspection)；5公理(◇φ→□◇φ)对应Euclidean性质——外部自省(负introspection)。通过相应子句的不同组合获得逻辑系统如S4(T+4)、S5(T+4+5/B)。CTL模态μ演算在硬件和协议验证中应用。"},
            {"heading": "关键结论", "content": "1. 时序逻辑(LTL/CTL)——将□理解为'for all future states'(一直)和◇为'eventually'(最终)是模态逻辑的直接应用 2. 知识逻辑(epistemic logic)中□读为'agent knows'——在分散系统和AI中有应用 3. 证明论模态逻辑的correspondence theory桥接语法和语义 4. S5被广泛用于知识表达(等价关系accessibility——perfect reasoning about knowledge) 5. 模态逻辑用于形式验证——specification逻辑描述系统需求(LTL/CTL是工业标准)"},
            {"heading": "关联知识点", "content": "[[离散数学-命题逻辑与谓词逻辑]] [[离散数学-Church-Turing论题]] [[软件工程-形式化方法与模型检测]]"}
        ]
    },

    # ═══════════════════════════════════════════════════════════════
    # 软件工程 — 5 supplemental topics
    # ═══════════════════════════════════════════════════════════════
    {
        "dir_name": "软件工程",
        "file_stem": "混沌工程",
        "title": "混沌工程",
        "course": "软件工程",
        "chapter": "质量保证",
        "difficulty": "INTERMEDIATE",
        "tags": ["软件工程", "混沌工程", "弹性", "故障注入", "Netflix"],
        "aliases": ["Chaos Engineering", "Resilience Testing"],
        "source": "Basiri et al. 2016 (Chaos Engineering at Netflix);《Chaos Engineering》(Rosenthal et al.); Gremlin文档",
        "sections": [
            {"heading": "核心定义", "content": "混沌工程(Chaos Engineering)是主动在生产环境中注入受控故障来检验系统弹性的学科。核心假设：复杂系统难以完全预测故障模式——因此需要经验性地测试。流程：1.)定义'稳态'(steady state)——度量正常行为的指标(throughput/latency/error rate) 2.)注射故障(chaos experiment——关闭节点/延迟注入/资源耗尽)形成试验组和对照组 3.)观察对比试验组指标以发现隐藏依赖和薄弱点。Chaos Monkey(Netflix,2011)是混沌工程的鼻祖——在AdWords(AWS)上的生产中随机终止实例。"},
            {"heading": "故障注入层级与工具", "content": "混沌工程的分层模型：基础设施层(Kubernetes节点故障——chaos-mesh/litmus/ChaosBlade随机终止pod/节点)、网络层(TC/iptables注入延迟和丢包——模拟网络分区)、应用层(HTTP fault injection——特定API返回错误)、业务逻辑层(定制故障)。最小爆炸半径(blast radius)原则——尽量小范围开始以求最小影响。现代工具(Chaos Mesh/Gremlin/Chaos Toolkit/dDosify)提供声明式、渐进式和平台原生的故障注入。"},
            {"heading": "关键结论", "content": "1. 混沌工程的第一条规则：永远选择最小的试验组实验(生产故障不应惊吓'用户') 2. 自动回滚机制是最重要的配套(需要保险措施中止实验) 3. 没有稳态检验指标的实验不是混沌工程——仅仅是制造混乱 4. 混沌工程需要安全和权限(如SOC2/GDPR合规故障可能伤害生产环境) 5. Large-scale故障实验通常安排在dev/QA/staging环境以及相对低影响的生产时间段"},
            {"heading": "关联知识点", "content": "[[软件工程-SRE与可观测性]] [[分布式系统-分布式共识深度(Paxos/Raft对比)]] [[软件工程-持续集成与持续部署]]"}
        ]
    },
    {
        "dir_name": "软件工程",
        "file_stem": "契约式设计DbC",
        "title": "契约式设计DbC",
        "course": "软件工程",
        "chapter": "软件设计",
        "difficulty": "INTERMEDIATE",
        "tags": ["软件工程", "DbC", "契约式设计", "断言", "Eiffel"],
        "aliases": ["Design by Contract", "DbC", "Precondition/Postcondition/Invariant"],
        "source": "Meyer 1988《Object-Oriented Software Construction》; Eiffel文档; Java Modeling Language (JML)",
        "sections": [
            {"heading": "核心定义", "content": "契约式设计(DbC/Design by Contract)是Meyer1988提出的命名式设计哲学。每个软件组件有明确的契约：前置条件(precondition)——调用者必须满足的条件(若违反,被调用方不负责任)；后置条件(postcondition)——被调用方在完成后必须保证的条件(若违反,调用方可拒绝接受)；类不变式(class invariant)——通过所有public操作始终保持的条件(操作前后不变式保持)。DbC将'接口即契约'的精神强化到方法论核心：如果前置满足而后置违反——唯一职责在被调用方存在bug。"},
            {"heading": "实现与实践", "content": "Eiffel语言原生支持require(pre)/ensure(post — 可引用old变量检查变化后关系)/invariant关键字。在C++/Java中通过断言(assert)模拟——但无语言级支持削弱了契约的文档化效果。iContract/JML(Java Modeling Language)增加了语法糖但仍需额外工具。Kotlin的contract{}是有限DbC——允许函数内声明对调用者的某些保证(如callsInPlace)。Rust的类型系统(特别是trait bounds)可以部分表达pre/post conditions(在编译期)。Dafny/SPARK通过证明自动验证契约完备性。"},
            {"heading": "关键结论", "content": "1. 前置条件!=输入验证——前置应可在调用前检查而不消耗额外资源 2. Liskov替换原则是DbC在继承中的契约表达——子类只能弱化前置、强化后置(持续保持超类契约) 3. 公共方法的所有断言允许在client检查断言的启用(而非在private内部代码) 4. 契约不仅仅是断言——更是形式的文档说明和责任分配 5. Z/VDM(B method)提升到完整的形式化验证级别"},
            {"heading": "关联知识点", "content": "[[软件工程-形式化方法与模型检测]] [[软件工程-设计模式]] [[离散数学-模态逻辑]]"}
        ]
    },
    {
        "dir_name": "软件工程",
        "file_stem": "特性开关FeatureFlag",
        "title": "特性开关FeatureFlag",
        "course": "软件工程",
        "chapter": "DevOps",
        "difficulty": "INTERMEDIATE",
        "tags": ["软件工程", "FeatureFlag", "特性开关", "渐进部署"],
        "aliases": ["Feature Toggles", "Feature Flags", "Canary Releases"],
        "source": "Fowler 2010 (FeatureToggle); LaunchDarkly文档; Google SRE Book Ch 16 (Canarying)",
        "sections": [
            {"heading": "核心定义", "content": "特性开关(feature flag/toggle)是在运行时决定是否启用某个功能片段的开关。四类活用：1.)发布开关(release toggles)——允许代码部署到生产但不马上激活(持续部署的使能器——解耦deployment和release) 2.)实验开关(experiment toggles)——A/B测试——根据用户分组展示不同版本收集反馈。3.)运维开关(ops toggles)——运维在系统压力大时关闭非关键功能。4.)权限开关(permission toggles)——仅特定用户(如内部用户)可见的preview功能。Trunk-Based Development + Feature Flag使得分支无需维持过长的生命周期。"},
            {"heading": "实现原则", "content": "特性标志管理平台(LaunchDarkly/ConfigCat/OpenFeature)提供集中管理、targeting规则(A/B/n% rollout)和多语言SDK。基于服务端而非客户端的flags更安全。Flag应该尽量短期存活(否则flag removal债务累积——旗标坟墓)。避免两个flags交互导致不可测状态(组合爆炸——可以通过设计不相交flags或集成测试覆盖关键组合)。Multivariate flags支持多值(非binary——如蓝色/红色/绿色三组A/B/C)。动态flag evaluation促进runtime变更(不重启服务)。"},
            {"heading": "关键结论", "content": "1. 每个flag有明确的主人(owner)和清除计划(sunset date) 2. flag的过度嵌套(super flags)导致维护灾难 3. stale flags(无人维护)引入安全和技术债务 4. 错误处理flag——若flag service不可用应fallback到安全默认值(default safe) 5. Canarying通过flag为新的部署逐步增加流量分配(并结合监控自动回滚)"},
            {"heading": "关联知识点", "content": "[[软件工程-持续集成与持续部署]] [[软件工程-混沌工程]] [[分布式系统-灰度发布与流量管理]]"}
        ]
    },
    {
        "dir_name": "软件工程",
        "file_stem": "领域事件与EventStorming",
        "title": "领域事件与EventStorming",
        "course": "软件工程",
        "chapter": "领域驱动设计",
        "difficulty": "INTERMEDIATE",
        "tags": ["软件工程", "EventStorming", "领域事件", "DDD"],
        "aliases": ["EventStorming", "Domain Events", "DDD"],
        "source": "Brandolini 2009 (EventStorming); Evans《Domain-Driven Design》; Vernon《Implementing DDD》",
        "sections": [
            {"heading": "核心定义", "content": "EventStorming是一种协作式领域建模工作坊，由Alberto Brandolini创建。核心概念：在大型墙面上用不同颜色的便签贴代表领域事件(变化已发生的记录,橙色)、命令(触发行为的动作,蓝色)、聚合(一致性边界内的事件处理单元,黄色)、外部系统(红色)、政策/策略(policy——何时触发,紫色)、读取模型(read model,绿色)。时间轴从左到右展开——业务专家和开发者共同描述整个业务流程(不区别角色)。EventStorming代替传统的需求文档讨论——加速共识形成。"},
            {"heading": "在实现中的体现", "content": "在实现中Domain Event转化为event-driven architecture的核心。Event是已发生的不可撤销的事实(通常使用过去式动词命名——'OrderPlaced'而非'PlaceOrder')。CQRS(Command Query Responsibility Segregation)配合事件：将写模型(聚合)和读模型(投影/projection)分离——写端发布事件,读端处理并更新查询优化模型。Event Sourcing将聚合的状态存储为事件序列而非当前状态快照(事件流回放重构当前状态——提供完整的审计日志和时间旅行调试)。"},
            {"heading": "关键结论", "content": "1. EventStorming的产出是一张可视化全景图(所有参会者理解一致) 2. Domain Events一经发布不可修改(append-only) 3. Event Sourcing解决了状态变化的审计问题但增加了系统复杂性(read/eventual consistency/replay性能) 4. Bounded Context边界的划分通常基于领域专家语言(统一语言UBiquitous Language)的一致性 5. EventStorming可以作为敏捷团队做需求发现的常规实践(Kick-off每sprint/feature)"},
            {"heading": "关联知识点", "content": "[[软件工程-微服务架构]] [[软件工程-契约式设计DbC]] [[分布式系统-事件驱动架构]]"}
        ]
    },
    {
        "dir_name": "软件工程",
        "file_stem": "软件度量与Halstead",
        "title": "软件度量与Halstead",
        "course": "软件工程",
        "chapter": "软件度量",
        "difficulty": "INTERMEDIATE",
        "tags": ["软件工程", "软件度量", "Halstead", "圈复杂度", "度量"],
        "aliases": ["Software Metrics", "Halstead Complexity", "Cyclomatic Complexity"],
        "source": "Halstead 1977 (Elements of Software Science); McCabe 1976 (Cyclomatic Complexity); Fenton & Bieman《Software Metrics》",
        "sections": [
            {"heading": "核心定义", "content": "软件度量(software metrics)量化软件质量、复杂度和可维护性。Halstead度量集包括：程序词汇量(η——η1=不同操作符数, η2=不同操作数数)、程序长度(N——N1=总操作符数, N2=总操作数数)、程序体积(V=N*log2(η1+η2)信息论bits)、难度(D=V/D'),工作量(E=D*V)和预测bug数(B=V/3000)。McCabe圈复杂度(Cyclomatic Complexity): C=E-N+2P(其中E=边,N=节点,P=连通分量+1)——计算程序control flow graph的独立路径数。"},
            {"heading": "实践应用", "content": "度量在code review和改进过程中的应用：1.)架设度量门(metric thresholds)——如圈复杂度>15触发审查(函数太复杂) 2.)追踪趋势(随时间看度量变化)而非单一数值 3.)度量不是绝对好坏判断——仅作为争议触发器(canary)。Line of Code(LOC)虽粗略但能指示模块相对规模。LCOM(Lack of COhesion of Methods)指示类的内聚性。Chidamber and Kemerer(CK)指标集衡量OO软件(DIT,depth of inheritance tree; CBO,coupling between objects)。现代工具SonarQube和radon/mccabe实现了这些度量。"},
            {"heading": "关键结论", "content": "1. One metric is no metric——单个度量不能作为决策依据(使用度量集) 2. 度量只度量某一方面——不能替代human judgement(度量提供信息,非决策) 3. 高复杂度可能导致低coverage测试不充分(识别需要重构的候选人) 4. LOC成为bug估计的基础(~5-50/千行代码取决于组织成熟度) 5. 度量基准(benchmark)因语言和领域而异(比较不能跨语言——比较要在相同域)"},
            {"heading": "关联知识点", "content": "[[软件工程-代码审查与质量保证]] [[软件工程-软件测试策略]] [[软件工程-持续集成与持续部署]]"}
        ]
    },

    # ═══════════════════════════════════════════════════════════════
    # 信息安全 — 5 supplemental topics
    # ═══════════════════════════════════════════════════════════════
    {
        "dir_name": "信息安全",
        "file_stem": "侧信道攻击防御",
        "title": "侧信道攻击防御",
        "course": "信息安全",
        "chapter": "硬件安全",
        "difficulty": "ADVANCED",
        "tags": ["信息安全", "侧信道", "Spectre", "Meltdown", "防御"],
        "aliases": ["Side-Channel Attacks", "Spectre/Meltdown", "Timing Analysis"],
        "source": "Kocher 1996 (Timing attacks); Lipp et al. 2018 (Meltdown); Spectre/Meltdown site; Intel/AMD mitigation guides",
        "sections": [
            {"heading": "核心定义", "content": "侧信道攻击(side-channel attack)通过观测程序的物理/时序侧信道(执行时间、power consumption、电磁辐射、cache)而非逻辑缺陷来提取秘密信息。Spectre和Meltdown(2018)是最著名的微架构侧信道——利用CPU的推测执行(speculative execution)加载缓存秘密数据(secret-laden cache line)，然后通过flush+reload等cache timing测量判断是否被加载。Spectre v1(bounds check bypass)利用条件分支i预测; v2(branch target injection)毒化BTB; Meltdown绕过硬件的特权检查(乱序执行中解除引用内核内存)。"},
            {"heading": "防御体系", "content": "防御层次：1.)软件防御——lfence/retpoline切换间接分支预测/return trampoline(防止返回猜测)；IBRS/IBPB(Indirect Branch Restricted Speculation——限制共享线程的分支预测) 2.)Compiler-level——禁能分支预测(-mretpoline) 3.)Kernel-level——KPTI(内核页表隔离——in-kernel在用户态仅映射必需的kernel内存) 4.)Hardware——speculation restrictions(新的微架构减轻推测攻击)。另一类常数时间编程(constant-time programming)——加密算法路径和内存访问模式不被秘密影响(EDDSA/X25519等使用固定window size / Montgomery ladder)。"},
            {"heading": "关键结论", "content": "1. 侧信道安全首要责任在CPU vendor——微架构漏洞从硬件架构方面难以完全消除 2. 常数时间编码消除timing channel——但无法消除cache channel(需要额外策略) 3. 针对Meltdown/Spectre的防御带来1-30%性能损失(较为集中的IO密集型系统调用) 4. 云环境中的侧信道影响尤为严重(共享硬件资源——需要重视隔离) 5. 密码库(libsodium/BoringSSL)在2018后全部实现Spectre-safe的加密——规避微架构预测影响秘密"},
            {"heading": "关联知识点", "content": "[[信息安全-密码学基础]] [[信息安全-硬件安全模块HSM]] [[计算机组成原理-分支预测器深度]]"}
        ]
    },
    {
        "dir_name": "信息安全",
        "file_stem": "安全多方计算SMPC",
        "title": "安全多方计算SMPC",
        "course": "信息安全",
        "chapter": "密码协议",
        "difficulty": "ADVANCED",
        "tags": ["信息安全", "SMPC", "安全多方计算", "隐私", "零知识"],
        "aliases": ["Secure Multi-Party Computation", "SMPC", "Garbled Circuits"],
        "source": "Yao 1982 (Millionaires' Problem); Yao 1986 (Garbled circuits); Cramer, Damgard & Nielsen《Secure Multiparty Computation》",
        "sections": [
            {"heading": "核心定义", "content": "安全多方计算(SMPC)使n个参与方在私有输入上联合计算函数f(x1,...,xn)而互不泄露自己的输入。通用SMPC基础——Yao的混淆电路(Garbled Circuit, Yao 86)：一个参与方为布尔电路中的每个门创建混淆后真值表并发送给另一方；另一方通过不经意传输(OT/Oblivious Transfer)获取自己的输入电路线对应的混淆值；执行混淆门(不需要电路结构信息尽可得最终输出)。GMW协议(1987)使用秘密共享(secret-sharing)实现多方参与(multi-party)的SMPC。"},
            {"heading": "应用与效率", "content": "SMPC在以下几个方面有应用：1.)隐私保护的机器学习(训练和推理——模型中各方数据不外泄) 2.)安全拍卖(不需要公开出价就能确定获胜方) 3.)密钥管理(多方签名——将完整私钥的切片分散持有,联合签名无需拼接重建私钥/ECDSA threshold signing) 4.)隐私保护的集合交集PSI(Private Set Intersection——两个组织了解共同客户而不暴露各自的完整客户列表)。当前对SMPC的性能优化：混淆电路的硬件加速、OT extension(扩展少量OT实现大量OT——IKNP 2003)。"},
            {"heading": "关键结论", "content": "1. SMPC的信息论安全需要大多数参与方诚实(semi-honest/malicious model) 2. 混淆电路的主要成本在AES-based混淆(+网络传输)——但pre-computing可大幅节省在线协商时间 3. 同态加密(HE/FHE)与SMPC互为补充——在不同情境各自优势 4. 恶意模型下的SMPC需额外验证步骤(效度校验) 5. 近年来SMPC已从理论走向实用(在医疗/金融领域出现真实的私有cross-org协作)"},
            {"heading": "关联知识点", "content": "[[信息安全-密码学基础]] [[信息安全-同态加密与隐私计算]] [[离散数学-安全协议形式化分析]]"}
        ]
    },
    {
        "dir_name": "信息安全",
        "file_stem": "硬件安全模块HSM",
        "title": "硬件安全模块HSM",
        "course": "信息安全",
        "chapter": "硬件安全",
        "difficulty": "INTERMEDIATE",
        "tags": ["信息安全", "HSM", "硬件安全", "密钥管理", "SGX"],
        "aliases": ["Hardware Security Module", "HSM", "TEE", "SGX"],
        "source": "FIPS 140-3 (Security Requirements for Cryptographic Modules); Intel SGX developer guide; AWS CloudHSM/Nitro Enclaves",
        "sections": [
            {"heading": "核心定义", "content": "硬件安全模块(HSM)是专门保护密钥和密码运算的物理硬件设备。HSM提供：1.)密钥生成(在硬件中的真随机数发生器——TRNG) 2.)密钥存储(私钥永不离硬件——永不暴露在明文中) 3.)加密/签名运算(在硬件内执行)。FIPS 140-3 Level 3认证要求硬件对篡改的检测和响应(钥匙删除)。TEE(Trusted Execution Environment)是CPU中的安全飞地(enclave)——Intel SGX/AMD SEV/ARM TrustZone在不可信OS中提供可信执行环境(加密的内存区域)。Nitro Enclaves(AWS)在EC2实例中提供无外部连接的虚拟机。"},
            {"heading": "PKI与HSM", "content": "证书机构(CA)使用HSM保护根私钥——这是PKI信任链的物理基础。HSM支持PKCS#11(Cryptoki)标准——C库API的统一操作接口(C_GenerateKey/C_Sign/C_Encrypt)。Cloud HSM(如AWS CloudHSM/GCP Cloud KMS with HSM)通过多租户架构(分区)提供FIPS 140-3认证的HSM服务而不需物理硬件。KMS(Key Management Service)在HSM前增加一层——通过数据密钥(data key)与主密钥(master key)分离，定期轮换(master key rotation自动——数据密钥使用envelope encryption)。"},
            {"heading": "关键结论", "content": "1. HSM保护的最核心资源是根私钥(RCA的private key) 2. SGX enclave受内存加密保护——即使系统管理员/dump内存也无法读明文 3. BIP32/HSM硬件钱包安全实现比特币(cryptocurrency)的密钥管理(冷存储——永不暴露/联网) 4. TPM可被视为计算机内置的轻量HSM(提供密钥密封和平台证明——seal/bind/unseal) 5. 密钥安全的原则——密钥永不离开安全模块(签名在模块内完成)"},
            {"heading": "关联知识点", "content": "[[信息安全-密码学基础]] [[操作系统-安全启动与TPM]] [[信息安全-安全多方计算SMPC]]"}
        ]
    },
    {
        "dir_name": "信息安全",
        "file_stem": "网络协议Fuzzing",
        "title": "网络协议fuzzing",
        "course": "信息安全",
        "chapter": "安全测试",
        "difficulty": "INTERMEDIATE",
        "tags": ["信息安全", "fuzzing", "协议安全", "漏洞发现"],
        "aliases": ["Protocol Fuzzing", "AFL", "Coverage-Guided Fuzzing"],
        "source": "Zalewski (American Fuzzy Lop); Fioraldi et al. 2020 (AFL++); Sutton et al.《Fuzzing: Brute Force Vulnerability Discovery》",
        "sections": [
            {"heading": "核心定义", "content": "Fuzzing(模糊测试)为被测程序提供大量随机或半编译生成的输入以触发异常或崩溃。协议fuzzing(protocol fuzzing)聚焦网络协议的健壮性——构造格式正确但语义异常的协议消息。三种方法：生成式fuzzing(generation-based——根据协议语法描述生成输入——需要格式定义如protobuf)、变异式fuzzing(mutation-based——劫持有效的协议数据流进行比特变异)、灰盒fuzzing(coverage-guided——AFL/AFL++用代码覆盖率引导进化式变异以达到更深程序路径)。LibFuzzer对库API的in-process fuzzing。"},
            {"heading": "AFL工作原理", "content": "AFL(American Fuzzy Lop)是最具影响力的覆盖率导向fuzzer。编译时插桩(basic block transitions——记录每个输入触发的边的集合)将input文件转为高熵->低熵。Fuzzer维护queue(有趣输入)和当前变异输入——每发现触发新边的输入即加入queue用作下一轮变异的种子(进化选择)。AFL利用fork server避免每个输入都经历完整的execve开销。Sanitizers(ASAN/UBSAN)增加内存错误检出率。Fuzzer常需一天到几周连续运行——发现罕见race condition。"},
            {"heading": "关键结论", "content": "1. Fuzzing是最有效地发现真实世界安全漏洞的方法之一 2. Protocol fuzzing需要理解协议状态——stateless fuzz只有浅层bug,stateful fuzz更深入但更复杂 3. Dumb fuzzer(纯随机)通常无法通过输入格式解析(覆盖率极低) 4. 结合fuzzing与符号执行(如Driller/QSYM)可跨越magic byte/checksum等障碍 5. Google的OSS-Fuzz项目持续fuzz数百个开源项目——已经发现了数十万个安全漏洞"},
            {"heading": "关联知识点", "content": "[[信息安全-代码安全审计]] [[软件工程-软件测试策略]] [[编译原理-静态分析工具链]]"}
        ]
    },
    {
        "dir_name": "信息安全",
        "file_stem": "证书透明度Certificate-Transparency",
        "title": "证书透明度Certificate Transparency",
        "course": "信息安全",
        "chapter": "PKI安全",
        "difficulty": "INTERMEDIATE",
        "tags": ["信息安全", "Certificate Transparency", "CT", "PKI"],
        "aliases": ["Certificate Transparency", "CT Logs", "SCT"],
        "source": "RFC 6962 (Certificate Transparency); Google CT project; SSLMate CT monitoring",
        "sections": [
            {"heading": "核心定义", "content": "Certificate Transparency(CT)是公开可审计的证书签发日志框架，旨在检测错误签发或恶意签发的TLS证书。原理：CA将每个签发的证书提交到CT Log服务器(分布式、仅追加、密码学保证的Merkle tree日志)。日志返回SCT(Signed Certificate Timestamp)嵌入到证书扩展中——浏览器只接受包含有效SCT的证书。Merkle树保证日志行为的一致性——定期发布的Signed Tree Head(STH)锚定当前日志内容(cryptographic commitment)。监视器(Monitors)持续扫描日志寻找可疑证书(如未经授权的domains)。"},
            {"heading": "运作与影响", "content": "审计者(Auditors)验证CT Logs的合规性(一致性证明consistency proof——新旧STH间的唯一追加路径)和包含证明(inclusion proof——某个证书在Merkle树中)。如果CA私下签发证书(未记录在CT)，则audit时被检测出(因为浏览器需要SCT)。Chrome自2018年对所有TLS证书强制CT(Apple自2021年)。全球有约20个CT Log运行(Couldflare Nimbus/Google Argon)。crt.sh是对公众的可查询CT日志搜索界面(查询一个域的所有签发证书)。"},
            {"heading": "关键结论", "content": "1. CT不能阻止CA错误签发证书——但能让此类行为公开可见(make it public) 2. CT+HPKP(证书钉扎)/Expect-CT组合增强防御 3. 私有的证书(内部CA)可以通过域验证的CT去验证公共签发的证书 4. SCT的签名确保日志无法在证书提交后篡改 5. 日志的bloom filter/查询认证(Merkle proof)支持高效不信任验证(browser完全不需要信任日志)"},
            {"heading": "关联知识点", "content": "[[计算机网络-TLS与HTTPS]] [[信息安全-PKI与信任模型]] [[信息安全-硬件安全模块HSM]]"}
        ]
    },

    # ═══════════════════════════════════════════════════════════════
    # 分布式系统 — 5 supplemental topics
    # ═══════════════════════════════════════════════════════════════
    {
        "dir_name": "分布式系统",
        "file_stem": "分布式共识深度Paxos-Raft对比",
        "title": "分布式共识深度(Paxos/Raft对比)",
        "course": "分布式系统",
        "chapter": "共识协议",
        "difficulty": "ADVANCED",
        "tags": ["分布式系统", "Paxos", "Raft", "共识", "一致性"],
        "aliases": ["Distributed Consensus", "Paxos vs Raft", "Multi-Paxos"],
        "source": "Lamport 1998 (Paxos Made Simple); Ongaro & Ousterhout 2014 (Raft); Howard 2019 (Paxos vs Raft survey)",
        "sections": [
            {"heading": "核心定义", "content": "分布式共识(distributed consensus)要求多个节点在某个提案上达成一致。Paxos(Lamport)是共识协议的理论基础——分两阶段：Phase 1(Prepare——Proposer发起proposal number→获得多数Acceptor的promise不处理更低编号)和Phase 2(Accept——Proposer发送value→多数Acceptor accept)。Raft(Ongaro)以可理解性为设计目标——通过强领导(strong leader)和受限行为减少状态空间。核心子问题：领导人选举(Leader Election——获得多数vote)、日志复制(Log Replication——Leader强制follower复制日志)、安全性(arg)。"},
            {"heading": "Paxos vs Raft对比", "content": """根本结构差异：Raft的领导人时刻保证独自接收写(leader-centric——任何日志entry都必须通过leader转述)， Paxos的提案可来自任何节点(every node can propose——但实际多用stable leader即Multi-Paxos)。Raft的日志不空洞(entry必须索引连续——index+term唯一标识)，Multi-Paxos允许日志空洞(需要单独填补——view stamping优化)。成员变更：Raft使用joint consensus(两个配置重叠——新配置和老配置交换)保证安全性(中间无需多个阶段)，Paxos需要考虑更多。Raft的"可理解"设计已成为工业界分布式系统的首选入门。"""},
            {"heading": "关键结论", "content": "1. Paxos难以实现正确(历史中很多系统打着Paxos旗号实际有bug——e.g. Google Chubby) 2. Raft的可理解性大大缩短了开发人员从阅读论文到正确实现的时间(~1-2个月 vs ~>4个月) 3. 两个协议都在leader failure时产生短暂不可用(~选举时间) 4. 两者都是crash fault tolerant(CFT——非拜占庭) 5. 大多数生产级raft实现(etcd/hashicorp raft/TiKV)在基本raft上扩展了pipelining和batch + witness/snapshot"},
            {"heading": "关联知识点", "content": "[[分布式系统-拜占庭容错实践(PBFT/HotStuff)]] [[分布式系统-CAP定理与一致性模型]] [[分布式系统-分布式快照Chandy-Lamport]]"}
        ]
    },
    {
        "dir_name": "分布式系统",
        "file_stem": "MapReduce与Spark计算模型",
        "title": "MapReduce与Spark计算模型",
        "course": "分布式系统",
        "chapter": "大数据计算",
        "difficulty": "INTERMEDIATE",
        "tags": ["分布式系统", "MapReduce", "Spark", "RDD", "计算模型"],
        "aliases": ["MapReduce", "Apache Spark", "RDD"],
        "source": "Dean & Ghemawat 2004 (MapReduce); Zaharia et al. 2010 (Spark); Spark官方文档",
        "sections": [
            {"heading": "核心定义", "content": "MapReduce(Google, 2004)是大规模分布式数据处理的开创性模型。Map阶段：读入原始数据(k1,v1)→产生中间键值对(k2,v2)→shuffle(按k2分区,合并排序)→Reduce阶段：处理每组(k2,list<v2>)→输出最终结果。Hadoop MapReduce通过HDFS实现数据局部性(data locality)——任务调度到数据所在的节点(colocation)。Spark通过RDD(Resilient Distributed Dataset, 弹性分布式数据集)实现更高效的数据处理——RDD是可容错、可并行操作的只读分区记录集合。"},
            {"heading": "Spark vs Hadoop", "content": "Spark相比Hadoop MapReduce的三大优势：1.)内存计算(in-memory)——中间结果保存在内存中(而非反复写入HDFS)，迭代算法(ML/图算法)性能提升10x-100x 2.)丰富的操作(Transformations: map/filter/join..., Actions: reduce/collect/count——惰性执行) 3.)DAG执行引擎——将整个作业编译为目的图(directed acyclic graph)优化,管道化shuffle-less阶段。DataFrame/Dataset API(SQL-like操作, Catalyst优化器)是RDD的更高层抽象。Shuffle是性能的主要瓶颈(涉及跨节点数据交换——通常也是网络带宽和磁盘IO瓶颈)。"},
            {"heading": "关键结论", "content": "1. MapReduce的shuffle是性能瓶颈(需要排序)——Spark优化shuffle(不一定排序,通过hash partition) 2. RDD的lineage(沿DAG恢复丢失分区的方案)保证容错——不需要checkpoint(尽管长时间迭代可以checkpoint) 3. Spark的Catalyst优化器使用树形转换规则(类似数据库优化器) 4. shuffle partitions数量是Spark的关键性能参数(默认200 partitions可能不当——随数据规模调整) 5. 数据倾斜(skewed data)是真实世界Spark作业中最常见的性能杀手(热点partition)"},
            {"heading": "关联知识点", "content": "[[分布式系统-GFS/HDFS分布式文件系统]] [[分布式系统-分布式共识深度(Paxos/Raft对比)]] [[数据库原理-查询优化器深度]]"}
        ]
    },
    {
        "dir_name": "分布式系统",
        "file_stem": "CRDT与最终一致性",
        "title": "CRDT与最终一致性",
        "course": "分布式系统",
        "chapter": "一致性模型",
        "difficulty": "ADVANCED",
        "tags": ["分布式系统", "CRDT", "最终一致性", "无冲突复制"],
        "aliases": ["Conflict-free Replicated Data Types", "CRDT", "Eventual Consistency"],
        "source": "Shapiro et al. 2011 (CRDTs); Brewer 2000 (CAP); Terry et al. 1995 (Eventual Consistency); Dynamo paper",
        "sections": [
            {"heading": "核心定义", "content": "CRDT(Conflict-free Replicated Data Types,无冲突复制数据类型)是在分布式系统中无需协调(synchronization)即可并发的可复制数据结构——合并操作commutative、associative且idempotent保证最终一致性无冲突。两大类型：基于操作的CRDT(op-based——操作在发出端应用然后重传到其他replica)和基于状态的CRDT(state-based——定期merge state,要求merge是set的least-upper-bound在预定义的semilattice上)。经典CRDT：G-Counter(增长计数器——各自维护vector,sum合局值), PN-Counter(正负计数器), G-Set(只增集合), OR-Set(观察消除集合——tombstone追踪删除)。"},
            {"heading": "实际应用", "content": "CRDT在协同编辑(Google Docs style——YATA/Logoot/RGA算法处理文本插入序列)和分布数据库(AntidoteDB/Riak)中找到应用。Delta state CRDT缩减合并了的state大小(只传输变化部分而非整个state)。ORMap(Observed-Remove Map)追踪因果关系以删除不再引用的tombstones。本地优先软件(local-first software)使用CRDT在所有设备上无服务器协同。数据库中的最终一致性(KV stores——Dynamo/Cassandra)通过CRDT或LWW(Last-Writer-Wins)解决并发更新冲突。"},
            {"heading": "关键结论", "content": "1. CRDT消除分布式系统中'协商解决冲突'的需要(自动merging——无需交互协议) 2. 操作CRDT要求可靠的因果广播(causal broadcast)——底层更多假设 3. CRDT的元数据(tombstones/clocks)随时间增长(需要压缩garbage collection) 4. CRDT不能保留某些invariant——全局唯一值/order invariant需要额外机制 5. CRDT+Actor模型(如Elixir)给出无锁分布的近乎理想方案"},
            {"heading": "关联知识点", "content": "[[分布式系统-CAP定理与一致性模型]] [[分布式系统-分布式共识深度(Paxos/Raft对比)]] [[数据库原理-事务与并发控制]]"}
        ]
    },
    {
        "dir_name": "分布式系统",
        "file_stem": "分布式快照Chandy-Lamport",
        "title": "分布式快照Chandy-Lamport",
        "course": "分布式系统",
        "chapter": "分布式协议",
        "difficulty": "ADVANCED",
        "tags": ["分布式系统", "快照", "Chandy-Lamport", "一致性快照"],
        "aliases": ["Distributed Snapshot", "Chandy-Lamport Algorithm", "Consistent Cut"],
        "source": "Chandy & Lamport 1985 (Distributed Snapshots); Verissimo & Rodrigues《Distributed Systems for System Architects》; Kshemkalyani & Singhal",
        "sections": [
            {"heading": "核心定义", "content": "Chandy-Lamport算法(1985)在分布式系统中捕获一致全局快照(consistent global snapshot)而不中断系统——即记录在某个时刻各节点的状态和所有在途传输中的消息。核心假设：1.)信道是故障免费的FIFO(unidirectional,exactly-once) 2.)信道图连通。算法：快照发起者记录自己的状态后发送marker消息到所有传出信道；当节点首次接收到marker(在某个传入信道上)时，记录自己的状态、调用marker发送规则(发送marker到所有传出信道)并从该传入信道直到接收下一个channels的marker间记录所有消息(channel recording)。所有节点完成记录后快照完成。"},
            {"heading": "一致切与意义", "content": "一致切(consistent cut)指快照中的事件集满足因果闭包——若事件e在快照中且f happens-before e则f也在快照中。Chandy-Lamport算法仅在实践中获取可检测为'垃圾'的空窗期(节点记录后的前置消息被遗漏——但因协议设定后置消息在稍后恢复)。Fidge/Mattern向量时钟(vector clocks)检测快照的因果一致性。分布式快照的应用：1.)死锁检测 2.)全局状态检测(debug) 3.)checkpoint/故障恢复(RRB/DFS的checkpoints) 4.)日志抽取(merge point in consistent snapshot) 5.)分布式垃圾回收。"},
            {"heading": "关键结论", "content": "1. 一致快照不反映系统任何时刻的实际状态——它是组合多个时刻的近似(因果一致) 2. 非FIFO信道需要序列号包装成FIFO 3. 不需要停止系统——快照获取是偷窃式(stealthy) 4. 快照的开销主要是marker发送(O(diameter)时间)和channel recording存储(消息频次) 5. Chandy-Lamport是理解一致性、因果和分布式监控的理论基石(许多后续工作基础)"},
            {"heading": "关联知识点", "content": "[[分布式系统-逻辑时钟与向量时钟]] [[分布式系统-分布式共识深度(Paxos/Raft对比)]] [[操作系统-虚拟内存与TLB]]"}
        ]
    },
    {
        "dir_name": "分布式系统",
        "file_stem": "拜占庭容错实践PBFT-HotStuff",
        "title": "拜占庭容错实践(PBFT/HotStuff)",
        "course": "分布式系统",
        "chapter": "共识协议",
        "difficulty": "ADVANCED",
        "tags": ["分布式系统", "拜占庭容错", "PBFT", "HotStuff", "BFT"],
        "aliases": ["Byzantine Fault Tolerance", "PBFT", "HotStuff", "BFT"],
        "source": "Castro & Liskov 1999 (PBFT); Yin et al. 2019 (HotStuff); Buchman 2016 (Tendermint); LibraBFT",
        "sections": [
            {"heading": "核心定义", "content": "拜占庭容错(BFT)处理节点可能恶意行为(不仅仅是崩溃)的共识——以拜占庭将军问题命名(Lamport 1982)。经典的PBFT(Practical Byzantine Fault Tolerance, 1999)是第一个实用的BFT协议，容错f个恶意节点需n>=3f+1个总节点。PBFT三阶段：pre-prepare(leader分发proposal)→prepare(节点广播prepare确认,收集到2f matching prepare消息→进入committed)→commit(广播commit,收集到2f+1 commit→本地执行)。View change在leader故障时更换leader。HotStuff(2019,Libra Diem采用的协议)线性化了leader-based流程——允许只有一个leader消息触发共识。"},
            {"heading": "HotStuff与区块链共识", "content": "HotStuff的核心创新：1.)三次消息交换(准备prepare→预提交pre-commit→提交commit)——leader收集回应后发给followers{ack, nack, or timeout} 2.)Pipelining——每个块同时处于各不同阶段(一个块的commit阶段=下一块的pre-commit,第三个块的prepare)——提升吞吐量 3.)线性视图切换(所有节点在super-majority下就leader更换达成一致)。Tendermint(基于PBFT共识引擎+app interface ABCI)在Cosmos network中使用。"},
            {"heading": "关键结论", "content": "1. PBFT的O(n^2)消息复杂度限制了网络规模(通常<=20-100节点) 2. HotStuff降低消息复杂度到O(n)——使得BFT在数百节点规模可行 3. BFT共识需要同时考虑活性(liveness——最终达成共识)和安全性(safety——一旦共识不过期) 4. 对于crash-only系统——Paxos/Raft(CFT)已足够(降低复杂性) 5. 证明BFT在面对非确定性恶意行为时的正确性很有挑战——需模型检测和形式化证明"},
            {"heading": "关联知识点", "content": "[[分布式系统-分布式共识深度(Paxos/Raft对比)]] [[分布式系统-CAP定理与一致性模型]] [[信息安全-密码学基础]]"}
        ]
    },

    # ═══════════════════════════════════════════════════════════════
    # 计算机图形学 — 5 supplemental topics
    # ═══════════════════════════════════════════════════════════════
    {
        "dir_name": "计算机图形学",
        "file_stem": "PBR材质系统",
        "title": "PBR材质系统",
        "course": "计算机图形学",
        "chapter": "渲染",
        "difficulty": "ADVANCED",
        "tags": ["图形学", "PBR", "材质", "BSDF", "渲染"],
        "aliases": ["Physically Based Rendering", "PBR", "BSDF"],
        "source": "Pharr, Jakob & Humphreys《Physically Based Rendering》(PBRT); Disney Principled BRDF 2012; Burley 2015 (PBR in practice)",
        "sections": [
            {"heading": "核心定义", "content": "PBR(Physically Based Rendering,基于物理的渲染)遵循物理光学原则模拟光线与材质的交互。核心BRDF(Bidirectional Reflectance Distribution Function)满足三大性质：能量守恒(反射的能量<=入射)、对称性(互换入射出射方向不变)和遵循微面元理论(microfacet theory)。Cook-Torrance microfacets model将表面建模为微小完美镜面的集合(D=法线分布,遮蔽函数G=几何衰减项,F=菲涅尔)。金属与非金属BRDF的区别——金属无diffuse分量(所有反射都是镜面)。"},
            {"heading": "Disney Principled BSDF", "content": "Disney的Principled BRDF(2012)将复杂的物理参数简化为艺术友好的参数集：baseColor(基础色)、metallic(金属度0-1)、roughness(粗糙度)、specular/specularTint、sheen、clearcoat(清漆层)、transmission。此模型不是物理完美的但它为艺术创作提供直觉控制同时保持物理合理的外观。GGX(Trowbridge-Reitz)是当今最常用的microfacet法线分布——比旧的Beckmann分布有更长的尾部(soft highlights + long tail——更自然)。Image-based lighting(IBL——用环境贴图hdr cubemap做光照)通过预计算辐照度和预过滤环境贴图加速。"},
            {"heading": "关键结论", "content": "1. PBR的diffuse+specular归一化保证能量守恒——材质不生成额外的光 2. 菲涅尔效应的直观表现—— grazing angle (glancing) 下几乎所有表面变镜面 3. Standard metallic workflow(多数的game engine采用)使用roughness/metallic贴图 4. ASTC/BC压缩贴图在运行时解压——多个贴图打包进不同channel(Packed textures/optimize usage) 5. RTX and ReSTIR enable real-time PBR path-tracing(光子路径采样——降噪器denoiser提供低样本count)"},
            {"heading": "关联知识点", "content": "[[计算机图形学-光线追踪与光栅化]] [[计算机图形学-全局光照与辐射度]] [[计算机组成原理-GPU渲染管线与GPGPU]]"}
        ]
    },
    {
        "dir_name": "计算机图形学",
        "file_stem": "全局光照与辐射度",
        "title": "全局光照与辐射度",
        "course": "计算机图形学",
        "chapter": "渲染",
        "difficulty": "ADVANCED",
        "tags": ["图形学", "全局光照", "radiosity", "Monte Carlo", "光照"],
        "aliases": ["Global Illumination", "Radiosity", "Monte Carlo Path Tracing"],
        "source": "Kajiya 1986 (Rendering Equation); Goral et al. 1984 (Radiosity); Veach 1997 (Multiple Importance Sampling)",
        "sections": [
            {"heading": "核心定义", "content": "全局光照(Global Illumination/GI)计算场景中所有光路的交互——直接光照(光源→物体→眼睛)和间接光照(多次反射)。渲染方程(Rendering Equation, Kajiya 1986)统一描述：出射辐射L_o(p,ω_o)=自发光L_e + 积分(BRDF*入射辐射*cosθ) dω_i。这是Fredholm第二类积分方程,一般需迭代求解。monte carlo path tracing通过随机采样入射方向反复应用渲染方程得到无偏估计。Radiosity(辐射度)基于能量守恒将场景分为surface patches并求解线性系统(geometry form factors)。"},
            {"heading": "Path Tracing与降噪", "content": "Monte Carlo path tracing通过模拟光子路径采样光积分：每次交互随机发射一条ray(bounce, 要么击中光源得到radiance,要么不击中→0返回)。Multiple Importance Sampling(MIS)结合BRDF采样和灯光采样权重降低方差(每策略的结果通过heuristical balance heuristic加权——降低估计方差)。现代real-time GI使用探针(probe-based——DDGI/Dynamic Diffuse GI)预计算场景辐照度储存在空间光探针中,着色时插值光探针。Screen space GI(屏幕空间追踪/SSGI采集相邻样本)成本低但不捕获屏幕外的二次光。"},
            {"heading": "关键结论", "content": "1. 蒙特卡洛积分的error速率为O(1/sqrt(N))——需要大量采样收敛 2. Shadow denoising和折射都很难(光线分布的复杂多模态——推荐用RTOF/Shader执行库优化) 3. 路径追踪是UE5/Lumen/Unity Progressive Lightmapper的主力(支持产品的GI计算) 4. 辐射度线求解O(n^2) matrix过大多用于预烘培(light baking) 5. NVIDIA的RTX GI即时路径追踪加速使得video games首次全面采用光线追踪GI"},
            {"heading": "关联知识点", "content": "[[计算机图形学-PBR材质系统]] [[计算机图形学-光线追踪与光栅化]] [[算法设计与分析-线性规划与单纯形法]]"}
        ]
    },
    {
        "dir_name": "计算机图形学",
        "file_stem": "GPU架构与CUDA编程",
        "title": "GPU架构与CUDA编程",
        "course": "计算机图形学",
        "chapter": "并行计算",
        "difficulty": "ADVANCED",
        "tags": ["图形学", "GPU", "CUDA", "并行", "图形"],
        "aliases": ["GPU Architecture", "CUDA Programming", "Graphics Compute"],
        "source": "NVIDIA CUDA Programming Guide; Akeley & Hanrahan real-time graphics; GPU Gems series (NVIDIA)",
        "sections": [
            {"heading": "核心定义", "content": "现代GPU是高度并行化的many-core处理器。NVIDIA GPU的SM(Streaming Multiprocessor)：多个CUDA核心、专用Function Units(Tensor Core/RT Core)、L1 cache/shared memory和warp scheduler。warp(32线程)以SIMT模式执行——所有lane执行相同指令但在不同数据上(vergen)。Tensor Core(Volta+)提供4x4矩阵乘加(D=A*B+C)在单时钟周期内——对深度学习推理和光线追踪BVH的重要加速。Ray Tracing Core提供硬件加速的BVH遍历和ray-triangle intersection(帧内硬件加速)。"},
            {"heading": "CUDA编程模型", "content": "CUDA程序组织为grid→block→thread层级。Kernel函数(__global__)在GPU上以<<<gridDim,blockDim>>>启动——每个线程根据threadIdx和blockIdx计算全局数据索引。Memory hierarchy：register(每线程最快但有限——256 registers/thread最多影响活跃warp数)→shared memory(__shared__ — block可见,程序员管理,L1-like)→global memory(所有线程可见,最大但最慢——靠coalesced access保持带宽)。__syncthreads()在block内同步。Streams实现overlap传输+计算(异步kernel启动——concurrent copy and execute)。"},
            {"heading": "关键结论", "content": "1. Warp divergence(同一warp内不同分支路径活跃)是GPU性能杀手(所有分支路径都执行但无效数据被屏蔽masked off) 2. 全局内存访问模式必须合并(coalesced)保证高带宽(block的相邻线程访问相邻地址——128B对齐) 3. Shared memory bank conflicts可能多线程访问同一bank的偏移(32-way bank stride padding解决) 4. Occupancy(活跃warp/SM的理论上限)是隐藏global memory latency的关键因素(延迟被另一个warp隐藏) 5. Unified Memory简化CPU-GPU数据迁移(自动页面迁移但可能有页错误延迟)"},
            {"heading": "关联知识点", "content": "[[计算机组成原理-GPU渲染管线与GPGPU]] [[计算机图形学-PBR材质系统]] [[算法设计与分析-并行算法]]"}
        ]
    },
    {
        "dir_name": "计算机图形学",
        "file_stem": "贝塞尔曲线与B样条",
        "title": "贝塞尔曲线与B样条",
        "course": "计算机图形学",
        "chapter": "曲线与曲面",
        "difficulty": "INTERMEDIATE",
        "tags": ["图形学", "贝塞尔", "B样条", "NURBS", "曲线"],
        "aliases": ["Bezier Curves", "B-Splines", "NURBS"],
        "source": "Bezier 1966 (UNISURF); de Casteljau 1959; Piegl & Tiller《The NURBS Book》; Farin《Curves and Surfaces for CAGD》",
        "sections": [
            {"heading": "核心定义", "content": "贝塞尔曲线(Bézier curves)由控制点P_0,...,P_n定义(通过Bernstein多项式基函数加权)：C(t)=Σ B_i^n(t)*P_i，其中B_i^n(t)=C(n,i)*t^i*(1-t)^(n-i)是Bernstein多项式。de Casteljau算法(几何评估——通过递归线性插值：P_i^(k)= (1-t)*P_i^(k-1) + t*P_(i+1)^(k-1))避免直接计算Bernstein多项式。贝塞尔曲线在一个控制点的小变动影响整条曲线(无局部控制)。凸包性质：曲线完全位于控制多边形的凸包内(用于碰撞检测的快速粗检)。"},
            {"heading": "B样条与NURBS", "content": "B样条(B-spline)通过节点向量(knot vector)定义基函数的支持范围——每个控制点的影响局限在少量区间内(局部控制)。基函数由Cox-de Boor递推定义。NURBS(Non-Uniform Rational B-Spline)添加权重将B样条投影到rational空间(用齐次坐标——每个控制点带权w_i)。NURBS可精确表示圆锥曲线(圆/椭圆/双曲线)——贝塞尔只能近似。NURBS用于CAD/CAM和影视制作(尤其在工业设计Rhino和汽车设计CATIA)。T样条(T-splines)允许无限顶点分辨率(非矩形控制grid——局部精化而无需引入冗余控制点)。"},
            {"heading": "关键结论", "content": "1. 贝塞尔是B样条的特例(knot vector无内部节点) 2. B样条次数=order-1(与控制点数无关) 3. Clamped knots endpoint interpolation B样条通过首末控制点(重复节点) 4. NURBS的权重大于1时拉伸曲线更靠近控制点,权重小于1时推离 5. 有理形式存在权重可能导致设计困难——通常保持单位权重(用控制点/次数控制形状)"},
            {"heading": "关联知识点", "content": "[[计算机图形学-骨骼动画与蒙皮]] [[计算机图形学-PBR材质系统]] [[数据结构-数值计算与逼近理论]]"}
        ]
    },
    {
        "dir_name": "计算机图形学",
        "file_stem": "骨骼动画与蒙皮",
        "title": "骨骼动画与蒙皮",
        "course": "计算机图形学",
        "chapter": "动画",
        "difficulty": "INTERMEDIATE",
        "tags": ["图形学", "骨骼动画", "蒙皮", "LBS", "rigging"],
        "aliases": ["Skeletal Animation", "Skinning", "LBS", "Dual Quaternion"],
        "source": "Magnenat-Thalmann et al. 1988 (Joint-dependent deformations); Kavan et al. 2007 (Dual Quaternion Skinning); Game Engine Architecture (Gregory)",
        "sections": [
            {"heading": "核心定义", "content": """骨骼动画(Skeletal Animation)是最常用的角色(character)动画方式。骨骼(skeleton)是由关节(joint)层级连接成树/有向图的结构——每个关节在模型空间绑定姿态(bind pose)下的transform。蒙皮(skinning)将网格的每个顶点绑定到一个或多个骨骼：通过加权平均多个骨骼变换后的顶点位置。LBS(Linear Blend Skinning)标准公式：v' = Σ w_i * M_i * v, w_i是第i个骨骼对该顶点的权重,M_i是骨骼的变换矩阵。LBS简单但存在"糖果包装"(candy wrapper)问题——旋转导致体积塌陷(肘部/肩部位置网格内陷)。"""},
            {"heading": "高级蒙皮技术", "content": "Dual Quaternion Skinning(DQS,双四元数蒙皮)使用单位对偶四元数(unit dual quaternion)替代矩阵线性混合——保持刚体变换性质(消除linear blend的旋转时的体积损失),代价是可能旋转中心漂移(较严重——在拉伸/长肢体中更明显)。Sparse Skinning通过稀疏局部锚点+Laplacian变形提供质量最高的可控解(可用于解剖精确的肌肉变形)。Blend Shapes(Morph Targets——对面部表情特别有用)基向量线性组合表示顶点的偏移(在nominal neutral姿势周围)。PBS(Physical-Based Simulation——肌肉/脂肪作为弹性体模拟)与骨骼动画混合叠加。"},
            {"heading": "关键结论", "content": "1. LBS计算量小(GPU-friendly)但质量有限 2. DQS是最佳默认选择(质量~good + 低overhead) 3. 通常每顶点4骨权重(多余4可以drop)为工业标准——packed到ubyte4 4. 骨骼绑定(Rigging——建立骨骼-蒙皮关系)至今以手动为主(自动工具improving) 5. 动画压缩(ACL——动画压缩库)在运行时解压减少内存(通常10x压缩比+可忽略的解压开销)"},
            {"heading": "关联知识点", "content": "[[计算机图形学-贝塞尔曲线与B样条]] [[计算机图形学-PBR材质系统]] [[数学-线性代数与矩阵变换]]"}
        ]
    },

    # ═══════════════════════════════════════════════════════════════
    # 程序设计 — 5 supplemental topics
    # ═══════════════════════════════════════════════════════════════
    {
        "dir_name": "程序设计",
        "file_stem": "声明式vs命令式深度对比",
        "title": "声明式vs命令式深度对比",
        "course": "程序设计",
        "chapter": "编程范式",
        "difficulty": "INTERMEDIATE",
        "tags": ["程序设计", "声明式", "命令式", "范式", "编程"],
        "aliases": ["Declarative vs Imperative", "Programming Paradigms"],
        "source": "Backus 1977 (FP Turing Award lecture); Van Roy & Haridi《Concepts, Techniques, and Models of Computer Programming》",
        "sections": [
            {"heading": "核心定义", "content": "命令式编程(imperative)通过指导计算机'如何做'来求解——序列化的状态改变(赋值、循环、条件)。声明式编程(declarative)描述'要什么'而非如何获得——回避显式状态管理。Backus(1997)批判冯诺依曼语言的'逐词执行'瓶颈。SQL是声明式的终极范例(SELECT result而非如何遍历——查询优化器决定怎样)。函数式(Haskell/elaborate map+reduce)、逻辑式(Prolog/描述事实和规则)和反应式(声明数据流)都是声明式的子类型。现实语言通常是多范式(Tuple: C=imperative+small declarations, Rust=imperative+functional borrowing)。"},
            {"heading": "范式融合", "content": "声明式的优势：1.)更接近领域语言——简洁且易于推理(transform expression) 2.)优化器自由——声明允许查询计划自动优化(SQL优化器) 3.)并行容易——纯函数无副作用(无数据竞争)。命令式的优势：1.)细粒度控制(硬件接近) 2.)可预测性能(no abstraction overhead) 3.)直接在模型上操作(不完全抽象——处理困难/未抽象边缘)。现代UI框架(React/声明式UI)采用declarative component model(UI = f(state))，数据库(ORM)将声明式和命令式混合。"},
            {"heading": "关键结论", "content": "1. 声明式——编写程式=描述结果(最佳在特定域) 2. 命令式在需要具体步骤/优化的场景中无可替代(system programming) 3. 多范式实际项目中混合使用——命令式在底层性能关键,声明式在高层逻辑 4. DSL(Domain Specific Language)实现声明式的domain abstraction(如Terraform=infrastructure as declaration) 5. 编程演进方向——整体趋势向更声明式(更安全+更多compiler optimization leverage)"},
            {"heading": "关联知识点", "content": "[[程序设计语言原理-类型系统总览]] [[程序设计语言原理-求值策略与副作用控制]] [[软件工程-软件架构设计]]"}
        ]
    },
    {
        "dir_name": "程序设计",
        "file_stem": "设计模式批判与替代",
        "title": "设计模式批判与替代",
        "course": "程序设计",
        "chapter": "软件设计",
        "difficulty": "INTERMEDIATE",
        "tags": ["程序设计", "设计模式批判", "函数式", "替代方案"],
        "aliases": ["Design Patterns Critique", "Functional Alternatives", "Pattern Obsolescence"],
        "source": "Norvig 1998 (Design patterns in dynamic languages); Hickey (Simple Made Easy talk); Gabriel《Patterns of Software》",
        "sections": [
            {"heading": "核心定义", "content": "GoF设计模式是否仍然相关的辩论持续。批评核心论点：许多GoF模式是对当时语言特性不足的补偿(Design patterns = language smells, Norvig)——Strategy/Cmd在lisp中就是lambda函数传递(无需类包装)；Observer通过函数/响应式流替代；Decorator用函数组合/annotations解决；Factory/Builder对Java冗长的构造器是必要的但在Rust/Kotlin有更简洁的解决方案。Peter Norvig在1998演讲中发现GoF的23个模式在Lisp中16个变得不可见或极简化(暗示这些模式补偿了语言缺陷)。"},
            {"heading": "现代替代", "content": "现代语言对经典模式的补偿：1.)Function types消除Strategy/Command模式——直接传函数 2.)闭包消除状态Memento(捕获外部变量) 3.)ADT(Algebraic Data Types/case class/sealed class)消除Interpreter/部分Visitor(模式匹配) 4.)Traits/Rust traits替代Bridge/Adapter(通过编译器保证适配) 5.)Iterator pattern内置在大多数语言的foreach中。模式'过时'有争议——架构级模式(如MVC, PubSub, Repository)仍有价值，实现级模式(micro-patterns)可能被语言机制消解。Rich Hickey强调简单性胜于模式复用——'Simplicity'而非'patterns'是设计决策第一指导。"},
            {"heading": "关键结论", "content": "1. 模式不是教条——根据实际情况选择实现策略 2. 语言特性丰富度的增加降低了实现模式的复杂度(消除boilerplate) 3. 设计原则(SOLID/Law of Demeter/composition over inheritance)比具体模式更持久 4. 代码模式和语言相关性很高——语言不可知的设计模式保留交流价值 5. 学习模式有助(提取共性问题)但不要过度produce pattern-oriented thinking(不要先画模式后用)——先设计再识别是否巧合匹配现有模式"},
            {"heading": "关联知识点", "content": "[[Java深入-设计模式实战]] [[软件工程-契约式设计DbC]] [[程序设计-声明式vs命令式深度对比]]"}
        ]
    },
    {
        "dir_name": "程序设计",
        "file_stem": "GIT内部原理",
        "title": "GIT内部原理",
        "course": "程序设计",
        "chapter": "版本控制",
        "difficulty": "INTERMEDIATE",
        "tags": ["程序设计", "Git", "版本控制", "内部原理"],
        "aliases": ["Git Internals", "Git Objects", "Content-Addressable"],
        "source": "Pro Git (Chacon & Straub) Ch 10; Scott Chacon《Git Internals》; Git源代码",
        "sections": [
            {"heading": "核心定义", "content": "Git是内容寻址文件系统(content-addressable filesystem)上的版本控制系统。核心三类对象(存储在.git/objects/)：blob(存储文件内容的压缩二进制——文件名等不保存于blob)，tree(目录的'内容清单'——指针指向blob和其他tree+名称+mode)，commit(快照——指向一个tree(根目录)+parent commit(s)+author/committer/date/message)。每个对象通过SHA-1(已迁移SHA-256)哈希内容命名，前两位作目录名，剩余作为文件名(如.git/objects/ab/cdef123...)。浅层对象结构和四类ref(branch/tag/HEAD/remote refs)形成Git的完整数据模型。"},
            {"heading": "Pack与垃圾回收", "content": "Git自动将松散对象打包成packfiles(git gc——.git/objects/pack/)——每个pack包含一个pack索引文件(.idx，object hash→offset映射)和数据文件(.pack)。Pack存储完整的基准对象和基于其的delta压缩差异(减量存储——增量使得历史版本空间开销小)。Git gc使用启发式(保留最近的对象松散存储——push/pull频繁的数据仍快,较旧的打包存档)。Commit graph(git commit-graph write)通过预计算文件加速log和merge-base操作。"},
            {"heading": "关键结论", "content": "1. Branch仅是指向commit的40字节文件——廉价创建/销毁 2. Detached HEAD状态：HEAD指向直接commit(而非branch)——检查或实验用 3. rebase重写commit历史(产生新commit,旧commit orphaned——在reflog中保留30天) 4. Git的DAG(Directed Acyclic Graph)保证parent指向唯一(合并commit有两个parents)。5. 'git cat-file -p'可内部查看任意类型commit"},
            {"heading": "关联知识点", "content": "[[软件工程-版本控制与Git]] [[数据结构-有向无环图DAG]] [[声明式vs命令式深度对比]]"}
        ]
    },
    {
        "dir_name": "程序设计",
        "file_stem": "Unicode与编码深度",
        "title": "Unicode与编码深度",
        "course": "程序设计",
        "chapter": "数据表示",
        "difficulty": "INTERMEDIATE",
        "tags": ["程序设计", "Unicode", "编码", "UTF-8", "字符集"],
        "aliases": ["Unicode", "UTF-8", "Character Encoding", "Code Points"],
        "source": "Unicode标准 v15; Davis et al. (UTS/Unicode Technical Standards); Spolsky《The Absolute Minimum Every Software Developer Must Know About Unicode》",
        "sections": [
            {"heading": "核心定义", "content": "Unicode为每一个字符分配唯一的码点(code point, U+XXXX)。当前v15定义149,186个字符(涵盖所有现代和古代文字)。编码形式(encoding form)将码点映射为字节序列——UTF-8(变长1-4字节,ASCII兼容:0xxxxxxx→1字节, 110xxxxx 10xxxxxx→2字节, 1110xxxx 10xxxxxx 10xxxxxx→3字节, 11110xxx → 4字节,单字节最高到U+007F)，UTF-16(变长2-4字节, surrogate pair编码BMP外的码点,U+D800-DBFF高代理+U+DC00-U+DFFF低代理: code point = (H-0xD800)*0x400 + (L-0xDC00) + 0x10000)。UTF-32(固定4字节)。"},
            {"heading": "表示与陷阱", "content": "Unicode规范化形式(normalization:NFC/NFD/NFKC/NFKD)解决多表示等价(如'é'可以precomposed U+00E9或decomposed e+combining acute U+0065 U+0301)。NFC将分解后的字符合成简并;NFD分解到基本字符+组合标记。排序(collation)通过CLDR的地区化排序权重(不匹配的码点二进制序)。emoji序列——多个码点组合为一个可见字形(ZWJ连字er+ZWJ+连字ee=？？？；skin tone modifier是组合修饰符)。编程：locale-sensitive vs locale-insensitive编码区分——字符流/byte流的'Unicode sandwich'最佳实践(仅在系统边界转换，内部始终使用codepoint)。"},
            {"heading": "关键结论", "content": "1. 英文text中最多的是1字节UTF-8序列(ASCII)。 2. 永远不要假设1 byte=1 char或1 code unit=1 code point(使用正确的string lib/API/codepoint iterator) 3. Unicode中的emoji操作复杂(检查字符串长度/grapheme cluster boundaries——word/line break算法) 4. 大小写映射(uppercase/lowercase)是locale-dependent(如突厥语I/dotted-i)。5. BOM(Byte Order Mark U+FEFF)在UTF-8中不推荐但常见(仅Windows式工具)在UTF-16中必须分辨LE/BE"},
            {"heading": "关联知识点", "content": "[[程序设计-正则表达式引擎实现]] [[Go语言-String与[]byte转换]] [[数据库原理-字符集与排序规则]]"}
        ]
    },
    {
        "dir_name": "程序设计",
        "file_stem": "正则表达式引擎实现",
        "title": "正则表达式引擎实现",
        "course": "程序设计",
        "chapter": "字符串处理",
        "difficulty": "ADVANCED",
        "tags": ["程序设计", "正则", "引擎", "NFA", "回溯"],
        "aliases": ["Regex Engine Implementation", "NFA vs DFA", "Backtracking"],
        "source": "Thompson 1968 (NFA regex); Cox 2007 (Regular Expression Matching可以快); Friedl《Mastering Regular Expressions》",
        "sections": [
            {"heading": "核心定义", "content": "正则表达式引擎分两大类：NFA引擎(回溯——Perl/PCRE/JavaScript/V8/Java/Python)保留反向引用和捕获组(功能丰富)。算法是递归回溯匹配，最坏O(2^n)——恶意模式可导致ReDoS(Regular expression Denial of Service)通过病态输入和回溯爆炸。DFA引擎(Thompson NFA模拟——GNU grep/AWK)基于多状态simulation的线性性能(无回溯)但无捕获组和反向引用(太限制其实用性)。现代混合引擎(RE2/Go/rust-regex)采用Thompson NFA模拟(cached states——lazy DFA)提供线性性能保证。"},
            {"heading": "RE2与性能", "content": "RE2(Google, Rust Regex engine)通过禁用反向引用和后向断言(keep forward-only semantics)获得线性复杂度。核心技术：Thompson NFA为每个输入字符生成活跃状态集(step指令/下一个活跃状态)。记忆化/缓存——新近的状态保存以复用验证。Regex literal解析在编译期——编译为状态机(非解释模式在运行时匹配)。SIMD加速的边界检查(SSE/AVX memchr和流——向量化byte扫描)。rust regex的模式分析——在编译期选择最佳引擎(fast子串搜索+DFA/Teddy SIMD算法——检测literal前缀)。"},
            {"heading": "关键结论", "content": "1. 不要使用不信任的正则——不可信pattern可能含有ReDoS 2. 使用线性引擎(RE2/Rust regex)处理外源regex(网络请求主体、用户配置等) 3. 编译regex overhead(解析→状态机)在重用中分摊 4. 善用Index和prefix加速(多数匹配在搜索literal前缀后执行完整匹配——限定搜索空间) 5. Capture groups增加回溯开销(但可控——限制在实用模式中)"},
            {"heading": "关联知识点", "content": "[[程序设计-Unicode与编码深度]] [[离散数学-有限状态机与正则语言]] [[编译原理-词法分析与语法分析]]"}
        ]
    },
]

# ── Write back to wiki_topics.json ──
json_path = Path(__file__).with_name("wiki_topics.json")
with open(json_path, "r", encoding="utf-8") as f:
    existing = json.load(f)
existing.extend(NEW_TOPICS)
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)
print(f"Added {len(NEW_TOPICS)} topics, total now {len(existing)}")
