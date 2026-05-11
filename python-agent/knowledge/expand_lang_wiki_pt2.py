"""
Generate Python深入 and JavaScript/TypeScript wiki topics and append to wiki_topics.json.
Each topic has real CS content with official sources.
"""
import json
from pathlib import Path

NEW_TOPICS = [
    # ═══════════════════════════════════════════════════════════════════════════
    # Python深入 (12 topics)
    # ═══════════════════════════════════════════════════════════════════════════

    {
        "dir_name": "Python深入",
        "file_stem": "GIL与并发编程",
        "title": "Python深入-GIL与并发编程",
        "course": "Python深入",
        "chapter": "并发与GIL",
        "difficulty": "ADVANCED",
        "tags": ["Python", "GIL", "多线程", "asyncio", "subinterpreter"],
        "aliases": ["Python GIL", "Global Interpreter Lock"],
        "source": "Python docs: Global Interpreter Lock; PEP 703 (No-GIL); Grothe《Inside the Python GIL》(2013)",
        "sections": [
            {
                "heading": "核心定义",
                "content": "GIL(Global Interpreter Lock)是CPython解释器中保护内部状态(引用计数、内存分配器、类型对象)的互斥锁。任何线程执行Python字节码前必须获取GIL——这意味着Python多线程在CPU密集型任务中实际上是串行的。GIL每隔sys.getswitchinterval()秒(默认5ms)或每执行约100条字节码后被强制释放，由等待线程争抢。等待I/O时线程主动释放GIL(Py_BEGIN_ALLOW_THREADS)，因此I/O密集型多线程仍然有效。PEP 703提出用偏向引用计数替代GIL，计划Python 3.13+实验性支持。Python 3.12引入的子解释器(PEP 684)每个拥有独立GIL，可并行执行。GIL是CPython的实现细节，并非Python语言规范——Jython和IronPython没有GIL。"
            },
            {
                "heading": "关键结论",
                "content": "1.CPU密集型任务用multiprocessing(每个进程独立GIL)或C扩展中释放GIL 2.I/O密集型任务(网络请求、文件读写)多线程有效——等待I/O时GIL被释放 3.multiprocessing的进程间通信(Queue/Pipe)有序列化开销，适合粗粒度任务划分 4.concurrent.futures.ThreadPoolExecutor适合I/O密集型，ProcessPoolExecutor适合CPU密集型 5.GIL内部的切换机制：ceval.c中的_PyEval_EvalFrameDefault循环，每执行完一条字节码检查是否需要释放GIL 6.开发时可用cpu_count()来自动决定线程池vs进程池 7.GIL导致某个线程的无限循环阻塞所有线程——即使调用time.sleep(0)也会短暂释放GIL给其他线程"
            },
            {
                "heading": "关联知识点",
                "content": "[[Python深入-CPython对象模型]] [[Python深入-asyncio事件循环]] [[Python深入-内存管理与GC]] [[Python深入-生成器与协程]]"
            }
        ]
    },
    {
        "dir_name": "Python深入",
        "file_stem": "描述符协议",
        "title": "Python深入-描述符协议与属性查找",
        "course": "Python深入",
        "chapter": "面向对象进阶",
        "difficulty": "ADVANCED",
        "tags": ["Python", "描述符", "Descriptor", "属性查找", "property", "__get__"],
        "aliases": ["Python Descriptor", "Descriptor Protocol"],
        "source": "Python docs: Descriptor HowTo Guide; Python Language Reference §3.3.2 Customizing attribute access",
        "sections": [
            {
                "heading": "核心定义",
                "content": "描述符(Descriptor)是实现__get__(self,instance,owner)、__set__(self,instance,value)或__delete__(self,instance)中任意方法的对象。数据描述符(Data Descriptor)定义了__set__或__delete__，在属性查找链中优先级最高，覆盖实例__dict__中的同名键。非数据描述符(Non-data Descriptor)仅定义__get__，优先级低于实例__dict__。属性查找的完整MRO链：类type(obj).__mro__上的数据描述符→实例obj.__dict__→类及其基类的非数据描述符→__getattr__作为最终回退。type.__getattribute__实现了以上查找逻辑，所有自定义类默认继承。"
            },
            {
                "heading": "关键结论",
                "content": "1.@property将方法转为数据描述符——通过__set__判断只读(reade-only)属性 2.@classmethod和@staticmethod都是非数据描述符 3.Django ORM字段、SQLAlchemy Column都是数据描述符，拦截属性读写转换为SQL操作 4.__slots__通过为每个槽生成描述符替代__dict__，减少内存开销30-50% 5.描述符的应用模式：懒加载(首次访问时计算并缓存)、类型验证、访问日志 6.orm应用：字段描述符在__set__中校验类型，在__get__中从存储引擎获取值 7.自定义__getattribute__会覆盖整个查找链——极度谨慎使用，可能引入无限递归"
            },
            {
                "heading": "关联知识点",
                "content": "[[Python深入-元类编程]] [[Python深入-CPython对象模型]] [[Python深入-装饰器进阶]] [[Python深入-dataclass与attrs]]"
            }
        ]
    },
    {
        "dir_name": "Python深入",
        "file_stem": "元类编程",
        "title": "Python深入-元类编程与类创建",
        "course": "Python深入",
        "chapter": "面向对象进阶",
        "difficulty": "ADVANCED",
        "tags": ["Python", "元类", "metaclass", "type", "__new__", "类创建"],
        "aliases": ["Python Metaclass", "Class Factory"],
        "source": "Python docs: __new__/metaclass; PEP 3115 (Metaclasses in Python 3000); PEP 487 (Simpler customisation)",
        "sections": [
            {
                "heading": "核心定义",
                "content": "元类(metaclass)是创建类的类——type是所有类的默认元类。class Foo(Base): x=1 在内部等价于 Foo = type('Foo', (Base,), {'x':1})。类创建过程分为三阶段：1.调用元类的__prepare__(name,bases)准备命名空间(默认返回空dict，可用OrderedDict保留属性顺序) 2.执行类体代码填充命名空间 3.调用元类的__new__(mcs,name,bases,namespace)创建类对象→调用__init__(cls,name,bases,namespace)初始化。PEP 487引入__init_subclass__钩子，在普通基类中拦截子类创建，大多数元类需求可由此替代。PEP 3115允许__prepare__返回自定义映射类型。"
            },
            {
                "heading": "关键结论",
                "content": "1.元类主要用例：ORM模型注册(Django ModelBase/SQLAlchemy DeclarativeMeta)、ABC接口强制、插件自动注册、单例模式 2.多继承时的元类一致性：type(cls)必须是所有基类元类的子类——Python要求最具体的元类满足MRO 3.自定义type.__call__可拦截类实例化流程(例如将obj.__init__调用包装在事务中) 4.__init_subclass__比元类更简单：class PluginBase: def __init_subclass__(cls,**kwargs): register(cls) 5.元类可控制__slots__、__module__、__qualname__等类级属性的生成 6.避免不必要的元类——能用类装饰器或__init_subclass__解决的就不要上元类 7.元类编程容易写出难以调试的代码——确认没有更简单的方案再使用元类"
            },
            {
                "heading": "关联知识点",
                "content": "[[Python深入-描述符协议]] [[Python深入-CPython对象模型]] [[Python深入-装饰器进阶]] [[Python深入-类型注解与mypy]]"
            }
        ]
    },
    {
        "dir_name": "Python深入",
        "file_stem": "生成器与协程",
        "title": "Python深入-生成器与协程底层",
        "course": "Python深入",
        "chapter": "迭代与生成",
        "difficulty": "INTERMEDIATE",
        "tags": ["Python", "生成器", "yield", "协程", "yield from", "iterator"],
        "aliases": ["Python Generator", "Coroutine Protocol"],
        "source": "PEP 342 (Coroutines via Enhanced Generators); PEP 380 (yield from); PEP 492 (async/await); Python docs: Generator Types",
        "sections": [
            {
                "heading": "核心定义",
                "content": "包含yield关键字的函数返回生成器对象(Generator)，同时实现迭代器协议(__iter__和__next__)。每次yield暂停函数执行，将执行状态保存在gi_frame(帧对象)中，值返回给调用者。PEP 342扩展了生成器接口——g.send(value)在yield点恢复执行并将value作为yield表达式的返回值；g.throw(exc)在yield点引发异常；g.close()引发GeneratorExit。PEP 380引入yield from子句，将迭代委托给子生成器，建立双向通道：调用者的send/throw/close透明传播到子生成器，子生成器的yield/return值返回到委托生成器。"
            },
            {
                "heading": "关键结论",
                "content": "1.生成器的栈帧在yield时被保存到堆上(gi_frame)，此时生成器不在调用栈上——本质是'可暂停的计算语境' 2.send(None)等价于next()；首次调用必须是send(None)或next()（预激生成器） 3.yield from自动处理子生成器的结束：子生成器raise StopIteration(value)→value作为yield from表达式的值 4.生成器表达式(genexpr)创建匿名生成器：(x*2 for x in range(10))，性能略高于生成器函数 5.close()在yield点引发GeneratorExit异常——生成器内部可捕获做清理，但必须re-raise或return 6.PEP 525引入异步生成器(async def+ yield)，由asyncio调度，不基于传统的yield协程"
            },
            {
                "heading": "关联知识点",
                "content": "[[Python深入-asyncio事件循环]] [[JavaScript-async/await与生成器]] [[JavaScript-Iterator与Generator]] [[Go语言-GMP调度器与goroutine]]"
            }
        ]
    },
    {
        "dir_name": "Python深入",
        "file_stem": "内存管理与GC",
        "title": "Python深入-内存管理与GC机制",
        "course": "Python深入",
        "chapter": "内存管理",
        "difficulty": "INTERMEDIATE",
        "tags": ["Python", "内存管理", "GC", "引用计数", "循环引用", "弱引用"],
        "aliases": ["Python GC", "Python Memory Management", "Reference Counting"],
        "source": "Python docs: gc module; Python docs: Garbage Collector Interface; CPython Modules/gcmodule.c",
        "sections": [
            {
                "heading": "核心定义",
                "content": "CPython采用引用计数(reference counting)与分代垃圾回收(Generational GC)的混合方案。每个PyObject包含ob_refcnt字段(通过Py_INCREF/Py_DECREF增减)，引用计数归零时立即通过tp_dealloc回收内存。引用计数无法处理循环引用(PyList包含自身)，分代GC专门解决此问题：仅追踪可包含其他对象的'容器'类型(list/dict/set/自定义类实例等)，按generation 0/1/2分层。新对象进入gen0；每次GC中存活的对象晋升到下一代；gen0收集最频繁(阈值默认700个obj分配)，gen2最不频繁。Python 3.11+引入快速GC避免在gen0为空时仍触发。"
            },
            {
                "heading": "关键结论",
                "content": "1.gc.get_threshold()查看阈值(默认(700,10,10))；gc.collect(generation=0)手动触发 2.weakref.WeakValueDictionary/WeakKeyDictionary可用于缓存而不阻止对象回收 3.__del__和GC交互复杂：有__del__的不可达循环对象在Python 3.4以下放到gc.garbage；3.4+简化为直接调用__del__ 4.上下文管理器(with)优于__del__——__del__调用时机不确定，解释器退出时可能不调用 5.对象池优化：小整数(-5~256)预分配；短字符串(单字符/标识符)自动intern到全局dict 6.objgraph和tracemalloc可用于诊断内存泄漏——tracemalloc显示内存分配的Python回溯"
            },
            {
                "heading": "关联知识点",
                "content": "[[Python深入-CPython对象模型]] [[Python深入-上下文管理器]] [[JavaScript-内存管理与内存泄漏]] [[Go语言-内存管理与GC]]"
            }
        ]
    },
    {
        "dir_name": "Python深入",
        "file_stem": "import系统",
        "title": "Python深入-import系统与模块加载",
        "course": "Python深入",
        "chapter": "模块系统",
        "difficulty": "INTERMEDIATE",
        "tags": ["Python", "import", "模块", "importlib", "sys.modules", "命名空间包"],
        "aliases": ["Python Import System", "Module Loading", "sys.meta_path"],
        "source": "Python docs: importlib; PEP 302 (New Import Hooks); PEP 420 (Namespace Packages); PEP 451 (ModuleSpec)",
        "sections": [
            {
                "heading": "核心定义",
                "content": "import语句的执行路径：importlib.__import__ → importlib._bootstrap._find_and_load。sys.modules(dict)缓存所有已加载模块(模块名→模块对象)，导入前先查此缓存。模块查找分为两级：元路径查找器(sys.meta_path，包含BuiltinImporter、FrozenImporter、PathFinder)和路径查找器(sys.path_hooks，用于处理文件路径)。PathFinder扫描sys.path列表，对每个路径尝试所有path_hook，为匹配的后缀(.py/.pyc/.so/.pyd)创建Loader。PEP 451引入ModuleSpec，将查找和加载解耦——spec定义了模块的origin、loader、子模块查找方式等完整信息。PEP 420定义了命名空间包：无__init__.py的目录仍可在不同路径下分布。"
            },
            {
                "heading": "关键结论",
                "content": "1.importlib.reload重新执行模块代码，更新sys.modules中的条目，但不更新已有from导入的变量(仅刷新模块全局变量) 2.相对导入(.foo/..bar)仅在包内模块中使用——__main__模块不支持相对导入 3.__pycache__中的.pyc字节码加速后续导入，基于源文件的时间戳和magic number决定是否重新编译 4.zip文件可通过sys.path直接导入(zipimport内部处理器)——这是pyinstaller打包的基础 5.import hook可用于从数据库/网络/加密归档加载代码——实现importlib.abc.Loader即可 6.循环导入(A导B，B导A)：解释器会返回已部分执行的模块对象(用过的名字可用，未执行到的raise AttributeError)"
            },
            {
                "heading": "关联知识点",
                "content": "[[Python深入-CPython对象模型]] [[JavaScript-ES模块vs CommonJS]] [[Go语言-接口与类型系统]]"
            }
        ]
    },
    {
        "dir_name": "Python深入",
        "file_stem": "类型注解与mypy",
        "title": "Python深入-类型注解与静态检查",
        "course": "Python深入",
        "chapter": "类型系统",
        "difficulty": "INTERMEDIATE",
        "tags": ["Python", "类型注解", "mypy", "static checking", "PEP 484", "Protocol"],
        "aliases": ["Python Type Hints", "mypy", "Static Type Checking"],
        "source": "PEP 484 (Type Hints); PEP 526 (Variable Annotations); PEP 604 (X|Y Union); PEP 544 (Protocols); mypy docs",
        "sections": [
            {
                "heading": "核心定义",
                "content": "PEP 484引入类型提示(Type Hints): def greet(name: str, times: int = 1) -> str: ...。运行时类型提示存储在__annotations__字典中(可通过typing.get_type_hints解析字符串前向引用)。Python本身不做类型检查——mypy/pyright/pytype等静态检查工具在编译期验证类型一致性。PEP 526引入变量注解x: int = 5。PEP 604引入X|Y联合类型(Python 3.10+)，语法更简洁。PEP 544定义Protocol(结构化子类型)：类不需要显式继承协议，只要实现所需方法即视为满足协议(类似Go interface的duck typing)。typing模块提供: List[T], Dict[K,V], Optional[T], Callable[...], TypeVar用于泛型。"
            },
            {
                "heading": "关键结论",
                "content": "1.类型提示不提升运行时性能——mypy完全是离线检查工具 2.Literal['small','medium','large']可限制字符串枚举(PEP 586, Python 3.8+) 3.TypedDict用于表示固定键名的字典(类似JSON schema) 4.overload装饰器让mypy理解同一函数的不同类型签名组合 5.Protocol的主要场景：函数参数要求'类文件对象'(有read/write方法)，不强制继承特定基类 6.Final装饰器标记不可重写的类/方法/变量；@final标记不可继承的类 7.pydantic/dataclasses-json利用运行时注解做数据验证和序列化 8.mypy支持增量类型检查(.mypy_cache/)使大型项目检查保持在秒级"
            },
            {
                "heading": "关联知识点",
                "content": "[[Python深入-dataclass与attrs]] [[TypeScript-类型系统]] [[Go语言-接口与类型系统]]"
            }
        ]
    },
    {
        "dir_name": "Python深入",
        "file_stem": "上下文管理器",
        "title": "Python深入-上下文管理器协议",
        "course": "Python深入",
        "chapter": "协议与接口",
        "difficulty": "BASIC",
        "tags": ["Python", "上下文管理器", "with", "__enter__", "__exit__", "contextlib"],
        "aliases": ["Python Context Manager", "with statement", "__enter__/__exit__"],
        "source": "PEP 343 (The 'with' Statement); Python docs: __enter__/__exit__; contextlib documentation",
        "sections": [
            {
                "heading": "核心定义",
                "content": "上下文管理器是实现__enter__(self)和__exit__(self,exc_type,exc_val,exc_tb)的对象。__enter__在with块进入时调用，其返回值绑定到as子句的变量；__exit__在块退出时调用(即使发生异常)。__exit__的三个异常参数在无异常时为None；返回True抑制异常(相当于静默捕获)，返回None或False让异常继续传播。with语句等价于try/finally——确保资源在作用域结束时释放。PEP 343不仅引入了with语法，还定义了contextlib模块：@contextmanager将生成器函数转为上下文管理器(yield前=__enter__，yield后=__exit__)。"
            },
            {
                "heading": "关键结论",
                "content": "1.contextlib.ExitStack管理动态数量的上下文管理器——适合运行时确定的资源列表 2.嵌套上下文：with A() as a, B() as b同时管理多个资源，__exit__按FILO顺序调用(后进先出) 3.contextlib.closing(thing)为仅有close()方法的对象创建上下文管理器 4.contextlib.suppress(*exceptions)优雅忽略指定异常(比try/except pass更易读) 5.contextlib.redirect_stdout/redirect_stderr临时重定向标准输出 6.AsyncExitStack(Python 3.7+)管理异步上下文管理器，async with asyncio.timeout(5)设置超时 7.自定义上下文管理器应确保__exit__是幂等的——多次调用不会误解状态"
            },
            {
                "heading": "关联知识点",
                "content": "[[Python深入-内存管理与GC]] [[Python深入-asyncio事件循环]] [[Python深入-CPython对象模型]]"
            }
        ]
    },
    {
        "dir_name": "Python深入",
        "file_stem": "CPython对象模型",
        "title": "Python深入-CPython对象模型",
        "course": "Python深入",
        "chapter": "解释器内部",
        "difficulty": "ADVANCED",
        "tags": ["Python", "CPython", "对象模型", "PyObject", "PyTypeObject", "slot"],
        "aliases": ["CPython Object Model", "PyObject Internals"],
        "source": "CPython source: Include/object.h, Objects/typeobject.c; Python docs: C API Reference; 《CPython Internals》(Shaw 2020)",
        "sections": [
            {
                "heading": "核心定义",
                "content": "CPython中一切数据都是PyObject指针。基础结构PyObject包含ob_refcnt(引用计数)和ob_type(指向PyTypeObject的指针)。变长对象(PyVarObject)额外包含ob_size(元素数)。PyTypeObject是类型的元类在C层的体现——定义tp_new/tp_init/tp_dealloc/tp_getattro/tp_setattro/tp_call/tp_iter/tp_hash等函数指针(slot)。调用obj.method()的实际路径：type(obj).__dict__['method']返回未绑定方法→__get__通过实例绑定→执行。属性访问obj.attr最终走向tp_getattro→_PyObject_GenericGetAttrWithDict→依次检查：数据描述符→实例__dict__→非数据描述符。type是PyTypeObject的元类在C层的实例。"
            },
            {
                "heading": "关键结论",
                "content": "1.小整数池：CPython预分配-5~256的PyLongObject对象(tp_dealloc时放入free_list而非释放) 2.字符串intern：符合标识符命名规则或长度≤1的字符串自动放入interned字典，全局共享 3.列表的over-allocation：appending时obj_size按公式new_allocated = (newsize>>3)+(newsize<9?3:6)预留容量 4.Python 3.6+字典使用紧凑表：indices稀疏数组(每个条目占1字节)和entries密集数组(preserve insertion order) 5.tp_slot重载可改变类型的底层行为——例如__getattribute__的tp_slot重载影响所有属性访问 6.ob_type的修改体现对象的动态性——实例方法可以通过设置__class__改变类型(Python 3.11+已限制)"
            },
            {
                "heading": "关联知识点",
                "content": "[[Python深入-GIL与并发编程]] [[Python深入-内存管理与GC]] [[Python深入-元类编程]] [[Python深入-描述符协议]]"
            }
        ]
    },
    {
        "dir_name": "Python深入",
        "file_stem": "asyncio事件循环",
        "title": "Python深入-异步编程asyncio事件循环",
        "course": "Python深入",
        "chapter": "异步编程",
        "difficulty": "INTERMEDIATE",
        "tags": ["Python", "asyncio", "事件循环", "async/await", "协程", "Task"],
        "aliases": ["Python asyncio", "Event Loop", "AsyncIO"],
        "source": "Python docs: asyncio module; PEP 3156 (Asynchronous IO Support); PEP 492 (async/await); uvloop project",
        "sections": [
            {
                "heading": "核心定义",
                "content": "asyncio提供基于事件循环(Event Loop)的单线程协作式并发模型。事件循环是核心调度器——管理就绪的Task队列、注册I/O回调(基于epoll/kqueue/IOCP)、调度定时任务。async def创建协程对象(Coroutine)，await将控制权交还给事件循环(让其他Task运行)。可等待对象(Awaitable)有三种：协程、Task(包装协程的运行单元，由loop.create_task创建)、Future(低级结果容器)。事件循环每轮迭代：处理就绪I/O→执行已到期的定时回调→执行就绪的协程步骤。asyncio.run()是Python 3.7+的推荐入口——创建新的事件循环、运行协程、清理。uvloop(基于libuv)是Dropbox开源的更快事件循环实现。"
            },
            {
                "heading": "关键结论",
                "content": "1.await释放控制权——不用await的阻塞调用(time.sleep/requests.get)阻塞整个线程和其他协程 2.asyncio.gather(*aws)并发执行多个协程，返回结果列表；任一抛出异常默认传播(return_exceptions=True可抑制) 3.asyncio.create_task()调度协程为后台任务(需保持强引用，否则任务可能被GC) 4.同步代码在线程中运行：await asyncio.to_thread(func)(Python 3.9+) 5.asyncio.Semaphore限制并发数量：async with semaphore控制同时运行的协程数 6.TaskGroup(Python 3.11+)提供结构化并发：异步上下文管理器中所有子任务完成才退出 7.调试：PYTHONASYNCIODEBUG=1启用慢回调检测(超过100ms的协程步骤)"
            },
            {
                "heading": "关联知识点",
                "content": "[[Python深入-生成器与协程]] [[Python深入-GIL与并发编程]] [[Python深入-上下文管理器]] [[JavaScript-事件循环与Job Queue]]"
            }
        ]
    },
    {
        "dir_name": "Python深入",
        "file_stem": "装饰器进阶",
        "title": "Python深入-装饰器进阶",
        "course": "Python深入",
        "chapter": "函数式编程",
        "difficulty": "INTERMEDIATE",
        "tags": ["Python", "装饰器", "decorator", "functools", "wraps", "lru_cache"],
        "aliases": ["Python Decorator", "@decorator", "functools"],
        "source": "PEP 318 (Decorators for Functions); PEP 3129 (Class Decorators); PEP 614 (Relaxing Grammar Restrictions); Python docs: @functools",
        "sections": [
            {
                "heading": "核心定义",
                "content": "装饰器语法@decorator等价于: func = decorator(func)。装饰器是在函数/类创建之后、绑定到名字之前执行的高阶函数。PEP 318于Python 2.4引入函数装饰器，PEP 3129于Python 2.6引入类装饰器(@)。@functools.wraps(被装饰函数)保留原函数的__name__、__doc__、__module__、__dict__等元信息——本质是将原函数的__wrapped__属性链保存到包装函数上。带参数装饰器需要三层嵌套：def deco(arg1, arg2): return partial(real_deco, ...) 或 在nonlocal中捕获参数。PEP 614(Python 3.9+)放松装饰器语法限制——允许任意表达式跟在@后面(如@buttons[id].on_click)。"
            },
            {
                "heading": "关键结论",
                "content": "1.多个装饰器的应用顺序从下往上：@d1 @d2 def f => f = d1(d2(f)) 2.@functools.lru_cache(maxsize=128)实现LRU缓存——基于Python dict(OrderedDict)+双向链表，O(1)访问 3.@functools.singledispatch根据第一个参数类型分发——实现泛型函数(类Julia的多分派) 4.类装饰器比函数装饰器更灵活：__init__捕获参数，__call__实现包装逻辑，可维护状态 5.__call__使类实例成为可调用装饰器：class Retry: def __init__(self,times): ... def __call__(self,func): ... 6.装饰器在类方法上使用时：需用@classmethod与@deco的顺序小心——外层应用在类创建之后 7.__wrapped__属性链允许inspect.unwrap()逐层展开装饰器获取原始函数"
            },
            {
                "heading": "关联知识点",
                "content": "[[Python深入-描述符协议]] [[Python深入-元类编程]] [[TypeScript-装饰器与Reflect Metadata]]"
            }
        ]
    },
    {
        "dir_name": "Python深入",
        "file_stem": "dataclass与attrs",
        "title": "Python深入-数据类与attrs对比",
        "course": "Python深入",
        "chapter": "数据建模",
        "difficulty": "BASIC",
        "tags": ["Python", "dataclass", "attrs", "数据建模", "PEP 557"],
        "aliases": ["Python dataclass", "attrs library", "Data Class"],
        "source": "PEP 557 (Data Classes); Python docs: dataclasses; attrs documentation (https://www.attrs.org); PEP 681 (dataclass_transform)",
        "sections": [
            {
                "heading": "核心定义",
                "content": "@dataclass装饰器(Python 3.7+)自动生成__init__/__repr__/__eq__/__hash__等方法，减少样板代码。字段通过类型注解声明：@dataclass class Point: x: int; y: int = 0。field()函数定制字段：default/default_factory(默认值)、init/repr/compare/hash(参与哪些方法)、metadata(元信息字典)。attrs是第三方库(2015年至今)，提供attr.s()/attr.ib()等价功能，但附加更丰富的验证器、转换器、冻结(frozen)等特性。两者都支持__slots__优化(Python 3.10+的dataclass slotted=True)。PEP 681引入dataclass_transform，允许attrs/Pydantic等库声明自身模仿dataclass行为，让mypy能理解。"
            },
            {
                "heading": "关键结论",
                "content": "1.dataclass的__post_init__进行后处理验证(字段就绪后执行) 2.frozen=True使用__setattr__重载阻止修改(不可变实例) 3.attrs的validator支持多种内建校验(instance_of/lt/gt/in_)和自定义可调用对象；支持converter管道(输入值自动转换) 4.Pydantic BaseModel提供运行时类型验证+JSON序列化，区别在于Pydantic验证输入数据而dataclass信任源码 5.field(init=False)创建非初始化字段(如从其他字段计算) 6.Inheritance: dataclass子类继承父类字段(子类字段在__init__中放在父类字段之后) 7.Ordering: 设置order=True自动生成__lt__/__le__/__gt__/__ge__比较方法(按字段定义顺序)"
            },
            {
                "heading": "关联知识点",
                "content": "[[Python深入-类型注解与mypy]] [[Python深入-描述符协议]] [[Python深入-CPython对象模型]]"
            }
        ]
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # JavaScript/TypeScript (15 topics)
    # ═══════════════════════════════════════════════════════════════════════════

    {
        "dir_name": "JavaScript/TypeScript",
        "file_stem": "V8引擎执行模型",
        "title": "JavaScript-V8引擎执行模型",
        "course": "JavaScript/TypeScript",
        "chapter": "引擎与运行时",
        "difficulty": "ADVANCED",
        "tags": ["JavaScript", "V8", "Ignition", "TurboFan", "隐藏类", "JIT"],
        "aliases": ["V8 Engine", "JavaScript Engine", "JIT Compilation"],
        "source": "V8 blog (v8.dev/blog); Google V8 documentation; 《JavaScript Engines》by Mathias Bynens",
        "sections": [
            {
                "heading": "核心定义",
                "content": "V8是Google开发的JavaScript/WebAssembly引擎(Chrome/Node.js/Deno/Electron)。运行时流水线：源码→解析器(parser)生成AST→Ignition解释器将AST编译为字节码并执行→热门函数(HotSpot)由TurboFan/WarpDrive编译为优化机器码。Ignition执行时收集类型反馈(type feedback)：函数的调用次数(call count)、参数类型、属性访问对象的隐藏类(Shape)。TurboFan基于'推测优化'(speculative optimization)假设运行时类型保持稳定，插入非优化回退检查点(bailout)。推测失败时进行去优化(deoptimization)——丢弃优化代码，回退到解释执行并重新收集反馈。V8 11+(Chromium 128+)推出Maglev中间层编译器(Speed + 低成本编译)，形成Ignition→Maglev→TurboFan的三层编译流水线。"
            },
            {
                "heading": "关键结论",
                "content": "1.隐藏类/Map: V8为结构相同(属性名和顺序一致)的对象分配共享Shape，属性访问用Cache Index大量减少查找时间 2.内联缓存(Inline Cache): 多态调用点缓存最近的类型反馈；单态(1 Shape)最快，超过4种Shape转为megamorphic(慢) 3.动态添加属性或delete属性导致隐藏类分裂——初始化为相同顺序避免 4.数组应保持元素类型一致: SMI(小整数)>DOUBLE(浮点)>PACKED(杂类型)，性能递减 5.try-catch快(throw-away)的捕获块和with语句阻止作用域内所有TurboFan优化 6.使用--trace-opt/--trace-deopt(V8 flags)分析函数优化和去优化事件"
            },
            {
                "heading": "关联知识点",
                "content": "[[JavaScript-内存管理与内存泄漏]] [[JavaScript-事件循环与Job Queue]] [[Python深入-CPython对象模型]]"
            }
        ]
    },
    {
        "dir_name": "JavaScript/TypeScript",
        "file_stem": "事件循环与任务队列",
        "title": "JavaScript-事件循环与Job Queue",
        "course": "JavaScript/TypeScript",
        "chapter": "异步编程",
        "difficulty": "INTERMEDIATE",
        "tags": ["JavaScript", "事件循环", "Event Loop", "macrotask", "microtask", "渲染"],
        "aliases": ["JavaScript Event Loop", "Job Queue", "Microtask"],
        "source": "HTML Spec §8.1.4 Event loops; Jake Archibald《Tasks, microtasks, queues and schedules》(2015); ECMA-262 §8.4 Jobs and Host Operations",
        "sections": [
            {
                "heading": "核心定义",
                "content": "事件循环(Event Loop)是JavaScript运行时的核心协调机制。有两级队列：任务队列(macrotask/task queue: 来自setTimeout/setInterval/I/O事件/postMessage/MessageChannel)和微任务队列(microtask queue: 来自Promise.then/catch/finally、MutationObserver、queueMicrotask)。每次事件循环迭代(tick)顺序：1.从macrotask队列取出一个任务执行 2.清空microtask队列中的所有微任务(包括执行中新增的) 3.可能的UI渲染更新(浏览器特有，每16.6ms一帧)。Node.js额外有nextTick队列(process.nextTick)，优先级高于microtask——在进入下个tick之前清空。HTML Spec §8.1.4规范了此行为确保跨浏览器一致。"
            },
            {
                "heading": "关键结论",
                "content": "1.Promise.resolve().then(fn)进入microtask——这就是为何即使是立即resolve的Promise也比setTimeout(fn,0)先执行 2.async函数中await后的代码→转换为Promise.then，进入microtask队列 3.requestAnimationFrame在下一帧渲染前执行——与macrotask/microtask在不同的调度阶段 4.microtask无限循环：microtask中添加新的microtask会无限排队——浏览器设置递归限制(一般1000次) 5.Node.js的setImmediate在I/O回调之后、close回调之前——与setTimeout(fn,0)的执行顺序依赖调用上下文 6.长时间同步任务阻断事件循环(阻塞渲染)——用requestIdleCallback或Web Worker拆分"
            },
            {
                "heading": "关联知识点",
                "content": "[[JavaScript-Promise与微任务]] [[JavaScript-async/await与生成器]] [[Python深入-asyncio事件循环]]"
            }
        ]
    },
    {
        "dir_name": "JavaScript/TypeScript",
        "file_stem": "原型链与继承",
        "title": "JavaScript-原型链与继承",
        "course": "JavaScript/TypeScript",
        "chapter": "面向对象",
        "difficulty": "INTERMEDIATE",
        "tags": ["JavaScript", "原型链", "prototype", "__proto__", "继承", "ES6 class"],
        "aliases": ["JavaScript Prototype Chain", "JavaScript Inheritance"],
        "source": "ECMA-262 §Objects; MDN Inheritance and the prototype chain; Dr. Axel Rauschmayer《JavaScript for impatient programmers》§Prototypes",
        "sections": [
            {
                "heading": "核心定义",
                "content": "ECMA-262定义JavaScript的继承基于原型链(prototype chain)。每个对象拥有[[Prototype]]内部槽(通过__proto__访问者属性或Object.getPrototypeOf()访问)——属性查找沿着原型链向上遍历，直至找到属性或到达null(Object.prototype.__proto__)。构造函数拥有prototype属性，其实例的[[Prototype]]指向该prototype对象(constructor.prototype的constructor反向指向构造函数)。方法固定在prototype上实现多实例共享——避免每实例复制函数。ES6 class语法本质是原型继承的语法糖：class Child extends Parent {...} 设置Child.prototype.__proto__ = Parent.prototype和Child.__proto__ = Parent(静态方法继承)。"
            },
            {
                "heading": "关键结论",
                "content": "1.Object.create(proto, descriptors)创建以proto为[[Prototype]]的新对象——最纯粹的继承方式 2.instanceof操作符检查Constructor.prototype是否出现在对象的原型链上 3.super()内部调用Parent.call(this)，super.method()在原型链上查找method 4.原型污染(prototype pollution): 修改Object.prototype影响所有对象——JSON.parse、_.merge等是攻击面 5.Object.create(null)创建无原型对象——适合用作纯净字典(无toString/valueOf等继承属性) 6.私有字段#privateField不通过原型链访问(lexical scope内的slot) 7.原型链查找性能：长链影响属性访问速度(V8通过隐藏类的快捷路径优化)"
            },
            {
                "heading": "关联知识点",
                "content": "[[JavaScript-闭包与作用域链]] [[JavaScript-Symbol与元编程]] [[Java-JVM架构与字节码]]"
            }
        ]
    },
    {
        "dir_name": "JavaScript/TypeScript",
        "file_stem": "闭包与作用域链",
        "title": "JavaScript-闭包与作用域链",
        "course": "JavaScript/TypeScript",
        "chapter": "作用域与闭包",
        "difficulty": "INTERMEDIATE",
        "tags": ["JavaScript", "闭包", "作用域链", "Lexical Environment", "let", "var"],
        "aliases": ["JavaScript Closure", "Lexical Environment", "Scope Chain"],
        "source": "ECMA-262 §Lexical Environments; MDN Closures; Kyle Simpson《You Don't Know JS: Scope & Closures》",
        "sections": [
            {
                "heading": "核心定义",
                "content": "ECMA-262定义词法环境(Lexical Environment)为规范类型，由环境记录(Environment Record: 存储标识符绑定)和外层词法环境引用([[OuterEnv]])组成。每个函数创建时拥有[[Environment]]内部槽，指向定义处的词法环境——而非调用处的环境(词法作用域)。函数执行时创建新的函数环境记录，其[[OuterEnv]]指向[[Environment]]，形成作用域链。闭包是函数与[[Environment]]的组合——即使外部函数执行完毕且从其调用栈弹出，内部函数仍能访问外部变量(因为这些变量仍被[[Environment]]引用，无法被GC回收)。引擎(V8)通过按需捕获(Context-allocated)和逃逸分析优化闭包内存——只捕获实际使用的变量。"
            },
            {
                "heading": "关键结论",
                "content": "1.var是函数作用域(没有块级作用域)；let/const在每次循环迭代创建独立的词法环境 2.经典闭包陷阱：for(var i=0;i<3;i++){setTimeout(()=>console.log(i))}打印3,3,3——改用let或IIFE 3.模块模式(揭示模块模式)利用闭包实现私有状态和公共API的封装 4.闭包导致内存泄漏：DOM元素持有闭包→闭包持有DOM元素的引用→循环引用(IE旧版；现代浏览器标记清除可处理) 5.setTimeout/setInterval的回调、事件监听器都是闭包——取消时需要清理引用 6.闭包的性能开销：每次创建闭包都要分配[[Environment]]引用——热路径中应减少闭包"
            },
            {
                "heading": "关联知识点",
                "content": "[[JavaScript-原型链与继承]] [[JavaScript-内存管理与内存泄漏]] [[JavaScript-V8引擎执行模型]]"
            }
        ]
    },
    {
        "dir_name": "JavaScript/TypeScript",
        "file_stem": "Promise与微任务",
        "title": "JavaScript-Promise与微任务队列",
        "course": "JavaScript/TypeScript",
        "chapter": "异步编程",
        "difficulty": "INTERMEDIATE",
        "tags": ["JavaScript", "Promise", "microtask", "then", "catch", "allSettled"],
        "aliases": ["JavaScript Promise", "Microtask Queue", "Promise Combinators"],
        "source": "ECMA-262 §Promise; Promises/A+ specification; MDN Using Promises",
        "sections": [
            {
                "heading": "核心定义",
                "content": "ECMA-262定义Promise为表示异步操作最终完成或失败的对象——内部[[PromiseState]]为pending/fulfilled/rejected。new Promise((resolve,reject)=>{...})中executor同步执行。.then(onFulfilled,onRejected)返回新Promise(链式调用——实现方法链)。.then回调被放入PromiseJobs队列(即microtask队列)而非调用栈——保证总是在当前execution context完成后异步执行。Promise.resolve(值)/Promise.reject(原因)创建已决议Promise。底层算法：NewPromiseCapability(executor)→CreateResolvingFunctions(promise)→resolve/reject闭包持有promise引用。Promise的thenable识别(Promise.resolve检查[Symbol.species]或.then方法)——用于coerce非Promise值。"
            },
            {
                "heading": "关键结论",
                "content": "1.Promise.all等待所有resolve(任一reject即整体reject短路)；Promise.allSettled等待全部settled(含失败原因) 2.Promise.race: 任一settled立即返回——适合超时模式；Promise.any: 任一fulfilled即成功(全部rejected才reject) 3.Promise.prototype.finally()无论成功失败都执行(不改变返回值)，后跟.then链继续处理 4.unhandledRejection: 未加.catch的Promise rejection在microtask清空后触发unhandledrejection事件(Node.js process: warning) 5.executor中的同步throw等价于reject——Promise自动捕获异常 6.Promise.resolve(promise)直接返回该promise(不创建新包装)——这是resolve不同于new Promise的关键区别"
            },
            {
                "heading": "关联知识点",
                "content": "[[JavaScript-事件循环与Job Queue]] [[JavaScript-async/await与生成器]] [[Python深入-asyncio事件循环]]"
            }
        ]
    },
    {
        "dir_name": "JavaScript/TypeScript",
        "file_stem": "async-await原理",
        "title": "JavaScript-async/await与生成器",
        "course": "JavaScript/TypeScript",
        "chapter": "异步编程",
        "difficulty": "INTERMEDIATE",
        "tags": ["JavaScript", "async", "await", "Generator", "异步", "微任务"],
        "aliases": ["JavaScript async/await", "Async Functions"],
        "source": "ECMA-262 §Async Functions; MDN async function; Jake Archibald《Async functions》blog series",
        "sections": [
            {
                "heading": "核心定义",
                "content": "async function返回AsyncFunction类型——调用时创建AsyncGenerator对象(底层用Promise包装)。await expression等价于Promise.resolve(expression).then(回调)，暂停async函数执行，将await之后的代码作为microtask入队(PromiseJobs)。引擎实现上，async函数被转换为生成器+自动执行器的组合：Babel/TypeScript的__awaiter辅助函数将async转为switch case状态机+Promise.then链。ES2017原生async优化为直接在字节码层面(而非生成器转换)实现性能改进。async函数的返回值自动包装为Promise.resolve。顶级await(ES2022)允许在ESM模块作用域顶层使用await——模块图加载暂停等待该Promise处理完毕再继续依赖模块。"
            },
            {
                "heading": "关键结论",
                "content": "1.await暂停async函数但不阻塞线程——其他macrotask/microtask正常调度 2.for await...of消费AsyncIterable(实现[Symbol.asyncIterator]的对象)，常用于流式读取 3.async generator: async function* gen(){yield await data}——返回AsyncGenerator，由for await消费 4.错误处理：await后的rejection可被try/catch捕获——等价.catch 5.性能：过度串行await()应改为await Promise.all([a(),b()])并行执行 6.误解：'await使代码执行变快'——await不提升速度，只是表达异步流程的语法糖 7.注意：async函数中的return value自动包装——与普通函数的return不同 8.意外await非Promise值无性能损失(Promise.resolve同步值直接返回)"
            },
            {
                "heading": "关联知识点",
                "content": "[[JavaScript-Promise与微任务]] [[JavaScript-事件循环与Job Queue]] [[JavaScript-Iterator与Generator]]"
            }
        ]
    },
    {
        "dir_name": "JavaScript/TypeScript",
        "file_stem": "TypeScript类型系统",
        "title": "TypeScript-类型系统",
        "course": "JavaScript/TypeScript",
        "chapter": "类型系统",
        "difficulty": "INTERMEDIATE",
        "tags": ["TypeScript", "类型系统", "Structural Typing", "Conditional Types", "infer"],
        "aliases": ["TypeScript Type System", "Structural Subtyping", "TS Types"],
        "source": "TypeScript Handbook; TypeScript Compiler docs (microsoft/TypeScript); TypeScript Deep Dive (Basarat)",
        "sections": [
            {
                "heading": "核心定义",
                "content": "TypeScript是JavaScript的超集，提供渐进式(opt-in)结构化类型系统。核心构造：联合类型(A|B, 值具有任意一方的形状); 交叉类型(A&B, 值同时满足两方); 字面量类型('a'|2, 精确值类型); 条件类型(T extends U?X:Y, 类型级别的if/else); 映射类型({[K in keyof T]: Transformed}, 对T的每个属性做变换); 模板字面量类型(`prefix-${string}`, 字符串级别的联合类型)。结构化子类型：是否兼容不依赖继承声明，只比较结构——{x:number,y:number}可替代{x:number}。类型推导系统基于Hindley-Milner思想的变体，支持：变量类型推导、返回类型推导、泛型约束推导。编译后所有类型注解被完全擦除(对运行时无影响)。"
            },
            {
                "heading": "关键结论",
                "content": "1.any禁用类型检查(危险——不应从any派生)；unknown安全——使用前必须类型收窄(typeof/instanceof/in) 2.never表示不可能值——用于穷尽性检查(default: const _exhaustive:never=x) 3.infer在条件类型内提取类型信息：type Returned<T>= T extends ((...args:any[])=>infer R)?R: never 4.keyof T返回T的所有键的联合类型；typeof获取值的类型——typeof window→Window类型 5.tsconfig strict模式包含：noImplicitAny/strictNullChecks/strictFunctionTypes等严格检查 6.声明合并：同名interface自动合并；namespace与class可合并以扩展功能 7.const assertion(as const)使类型收窄到最具体——对象转为readonly nested literal"
            },
            {
                "heading": "关联知识点",
                "content": "[[TypeScript-装饰器与Reflect Metadata]] [[Python深入-类型注解与mypy]] [[JavaScript-ES模块vs CommonJS]]"
            }
        ]
    },
    {
        "dir_name": "JavaScript/TypeScript",
        "file_stem": "Proxy与Reflect",
        "title": "JavaScript-Proxy与Reflect API",
        "course": "JavaScript/TypeScript",
        "chapter": "元编程",
        "difficulty": "ADVANCED",
        "tags": ["JavaScript", "Proxy", "Reflect", "元编程", "拦截", "Vue3"],
        "aliases": ["JavaScript Proxy", "Reflect API", "Meta-programming"],
        "source": "ECMA-262 §Proxy; MDN Proxy and Reflect; Vue 3 Reactivity in Depth Guide",
        "sections": [
            {
                "heading": "核心定义",
                "content": "ECMA-262 §28定义Proxy对象: new Proxy(target, handler)创建目标对象的虚拟包装。handler可拦截13种内部方法(internal methods / 规范操作): [[Get]](get)/[[Set]](set)/[[HasProperty]](has)/[[Delete]](deleteProperty)/[[OwnPropertyKeys]](ownKeys)/[[GetPrototypeOf]]/[[SetPrototypeOf]]/[[IsExtensible]]/[[PreventExtensions]]/[[GetOwnProperty]](getOwnPropertyDescriptor)/[[DefineOwnProperty]](defineProperty)/[[Call]](apply, 针对函数)/[[Construct]](construct, new操作符)。Reflect API提供与proxy handler trap一一对应的默认行为方法——在每个trap中可调用Reflect方法转发到原始行为(如Reflect.get(target,prop,receiver))。Proxy可透明拦截——对使用者不可见(除非使用===与target比较)。"
            },
            {
                "heading": "关键结论",
                "content": "1.Vue 3的响应式系统核心基于Proxy(替代Vue 2的Object.defineProperty)——可检测属性添加/删除/数组index赋值/Map/Set 2.Reflect的作用：确保[[Get]]/[[Set]]等操作的receiver参数正确传递，维持原型链上this的指向 3.可撤销Proxy(Proxy.revocable): 为临时敏感对象创建代理，在需要时调用revoke()永久关闭所有访问 4.trap的get/set需对invariant检查——如set的返回值必须为truthy且不可报告添加属性的假操作 5.Proxy限制：不适用于内建类型(Set/Map/Date)内部方法需要this绑定到原始对象——用receiver解决 6.Proxy的性能开销：每次操作经过trap(slow path)——热路径不适合大量Proxy 7.Proxy+Reflect可用于：负索引数组、默认属性值(不存在时返回自定义值)、属性访问日志"
            },
            {
                "heading": "关联知识点",
                "content": "[[JavaScript-Symbol与元编程]] [[JavaScript-Iterator与Generator]] [[Python深入-描述符协议]]"
            }
        ]
    },
    {
        "dir_name": "JavaScript/TypeScript",
        "file_stem": "Iterator与Generator",
        "title": "JavaScript-Iterator与Generator协议",
        "course": "JavaScript/TypeScript",
        "chapter": "迭代协议",
        "difficulty": "INTERMEDIATE",
        "tags": ["JavaScript", "Iterator", "Generator", "Symbol.iterator", "yield*"],
        "aliases": ["JavaScript Iterator", "Generator Protocol", "Iterable"],
        "source": "ECMA-262 §Iteration; MDN Iterators and generators; ExploringJS by Dr. Axel Rauschmayer",
        "sections": [
            {
                "heading": "核心定义",
                "content": "ECMA-262定义两个独立协议：可迭代协议(Iterable)——对象实现[Symbol.iterator]方法返回迭代器；迭代器协议(Iterator)——对象实现next()方法返回{value, done}结果对象。所有内建可迭代类型：Array、String、Map、Set、TypedArray、arguments对象、NodeList、generator对象。function*声明生成器函数——调用返回Generator对象(同时实现Iterable和Iterator协议)，每次yield暂停并产出{value, done:false}，return时产出{value, done:true}。yield*委托另一个可迭代对象的所有值——等价于for(const val of iterable) yield val但带有双向通信通道(send/throw/return传播到委托的迭代器)。"
            },
            {
                "heading": "关键结论",
                "content": "1.for...of循环内部调用iterator[Symbol.iterator]()获取迭代器然后消费 2.展开运算符(...)、解构([a,b]=arr)、Array.from()、new Map(iterable)均基于迭代器协议 3.生成器的.throw(err)和.return(value)方法: throw在yield点引发异常；return提前终止生成器(设置done:true) 4.可迭代的范围表达式(fx*): function* range(start,end) { for(let i=start;i<end;i++) yield i } 5.异步迭代器[Symbol.asyncIterator]返回{value,done}包装在Promise中——for await...of消费 6.惰性求值：生成器实现管道模式(fx* pipeline)——每个步骤仅当消费时才计算，内存友好 7.无限迭代器：自然数序列、斐波那契——生成器完美表达"
            },
            {
                "heading": "关联知识点",
                "content": "[[JavaScript-async/await与生成器]] [[Python深入-生成器与协程]] [[JavaScript-Map/Set/WeakMap/WeakSet]]"
            }
        ]
    },
    {
        "dir_name": "JavaScript/TypeScript",
        "file_stem": "ES模块vsCommonJS",
        "title": "JavaScript-ES模块vs CommonJS",
        "course": "JavaScript/TypeScript",
        "chapter": "模块系统",
        "difficulty": "INTERMEDIATE",
        "tags": ["JavaScript", "ESM", "CommonJS", "import", "require", "Tree Shaking"],
        "aliases": ["ES Modules", "CommonJS vs ESM", "JavaScript Modules"],
        "source": "ECMA-262 §Modules; Node.js docs: ECMAScript Modules; TC39 modules proposals",
        "sections": [
            {
                "heading": "核心定义",
                "content": "ES模块(ECMA-262 §Modules)使用import/export声明式语法。导入：import defaultExport from 'mod'(默认导入)、import {named} from 'mod'(命名导入)、import * as ns from 'mod'(命名空间导入)。导出：export default expr(每个模块一个默认导出)、export const x=1(命名导出)、export {a as b}(重新导出)。ES模块是静态结构——import/export声明必须在模块最顶层(不能在if/函数中)，模块指定符必须是字符串字面量。这使编译器可静态分析模块依赖图，实现tree-shaking(消除未使用代码)。动态导入import(specifier)返回Promise，返回模块命名空间对象，在运行时异步加载。CommonJS用require()/module.exports——同步加载，运行时解析，值是导出对象的拷贝。"
            },
            {
                "heading": "关键结论",
                "content": "1.ESM绑定是live binding(实时绑定)：导入方看到导出方的当前值(如果导出变量改变，导入方可见)；CJS是值的快照拷贝 2.循环依赖：CJS中未完成的模块导出可能不完整(部分属性undefined)；ESM通过live binding优雅处理 3.Node.js双模块系统：.mjs=总是ESM，.cjs=总是CJS；package.json设置 type:module 默认ESM 4.ESM自动启用strict mode；CJS不是严格的——这是常见的行为差异来源 5.WASI/Deno原生ESM；Node.js在ESM中不可用__dirname/__filename——用import.meta.url+fileURLToPath 6.ESM的import.meta提供模块元信息(.url=文件路径，.resolve=resolve指定符)"
            },
            {
                "heading": "关联知识点",
                "content": "[[JavaScript-V8引擎执行模型]] [[TypeScript-类型系统]] [[Python深入-import系统]]"
            }
        ]
    },
    {
        "dir_name": "JavaScript/TypeScript",
        "file_stem": "内存管理与泄漏",
        "title": "JavaScript-内存管理与内存泄漏",
        "course": "JavaScript/TypeScript",
        "chapter": "内存管理",
        "difficulty": "INTERMEDIATE",
        "tags": ["JavaScript", "内存管理", "GC", "Mark-and-Sweep", "内存泄漏", "WeakRef"],
        "aliases": ["JavaScript Memory Leak", "Garbage Collection", "Mark-Sweep"],
        "source": "MDN Memory Management; V8 Blog: Orinoco (Concurrent GC); Chrome DevTools Memory Profiling docs",
        "sections": [
            {
                "heading": "核心定义",
                "content": "JavaScript使用标记清除(Mark-and-Sweep)垃圾回收——非确定性(不可预知何时发生)。可达性(reachability)原则：从根对象(全局对象、当前执行上下文的局部变量和作用域链、闭包捕获的变量)出发，所有可达对象保留，不可达的回收。现代引擎(V8 Orinoco项目)分层实现：新生代(Scavenge算法：Cheney's copying collector——存活对象晋升到老生代)+老生代(并发Mark-Sweep+Mark-Compact)。并发标记：工作线程标记可达对象的同时主线程继续执行——写屏障(write barrier)截获指针修改以保持并发标记的正确性(三色抽象：白→灰→黑)。标记阶段完全并发(SW-free)，压缩阶段有短Stop-The-World窗口。大对象直接分配到老生代避免复制开销。"
            },
            {
                "heading": "关键结论",
                "content": "1.常见内存泄漏模式：未清理的全局变量、遗忘的定时器/事件监听器、分离的DOM节点(JS引用但不在DOM树)、闭包中意外持有的大对象引用 2.WeakMap/WeakSet: 键(对象)是弱引用——键被GC时条目自动删除，适合缓存和DOM元数据 3.WeakRef+FinalizationRegistry(ES2021): 允许观察GC但行为不确定——不应作为应用逻辑依赖 4.Chrome DevTools Memory面板：堆快照(查找delta)、分配时间轴(看到分配模式)、分配采样 5.内存增长三阶段模式：初始增长→趋于平稳(正常)→持续增长(泄漏) 6.大数组/字符串的转移(Transferable): 零拷贝传递(如从Worker到主线程)节省内存"
            },
            {
                "heading": "关联知识点",
                "content": "[[JavaScript-WeakMap/WeakSet]] [[JavaScript-闭包与作用域链]] [[JavaScript-V8引擎执行模型]]"
            }
        ]
    },
    {
        "dir_name": "JavaScript/TypeScript",
        "file_stem": "WebWorkers",
        "title": "JavaScript-Web Workers与并行",
        "course": "JavaScript/TypeScript",
        "chapter": "并行与并发",
        "difficulty": "BASIC",
        "tags": ["JavaScript", "Web Worker", "并行", "postMessage", "SharedArrayBuffer"],
        "aliases": ["Web Workers", "Dedicated Worker", "Service Worker"],
        "source": "HTML Spec §Workers; MDN Web Workers API; Surma《The State of Web Workers》2023",
        "sections": [
            {
                "heading": "核心定义",
                "content": "HTML Spec定义的Web Workers提供独立于主线程的JavaScript执行环境。const worker = new Worker('worker.js')创建专用Worker——有独立的全局对象(DedicatedWorkerGlobalScope，无window/document)、独立的事件循环、独立的内存堆。与主线程通过结构化克隆(structured clone)传递消息——postMessage(data, [transferList])。Transferable对象(ArrayBuffer/MessagePort/ImageBitmap)在转移后不可在发送端访问(zero-copy transfer)。SharedWorker让多个浏览上下文共享单一worker实例(通过port通信)。Service Worker是特殊的Worker——作为浏览器和网络之间的可编程代理(支持PWA的离线缓存、后台同步、推送通知)。Node.js的worker_threads提供类似能力。"
            },
            {
                "heading": "关键结论",
                "content": "1.结构化克隆有性能成本——大数组应用Transferable(所有权转移)或SharedArrayBuffer+Atomics(共享内存) 2.Web Worker适用于：CPU密集型计算(图像处理/数据压缩/加解密)、后台数据预取、用户交互干扰隔离 3.Worker内部可用importScripts()同步加载脚本——现在推荐import声明(ES模块Worker: new Worker('w.js',{type:'module'})) 4.错误处理：Worker内部onerror事件+主线程worker.onerror/worker.onmessageerror 5.限制：不能访问DOM/localStorage(用IndexedDB替代)/cookie(可通过CookieStore API) 6.OffscreenCanvas+Worker：允许在Worker线程渲染Canvas——游戏/数据可视化场景 7.Comlink库(Google Chrome Labs): 将postMessage抽象为RPC调用——Comlink.wrap(worker)"
            },
            {
                "heading": "关联知识点",
                "content": "[[JavaScript-事件循环与Job Queue]] [[JavaScript-内存管理与内存泄漏]] [[Python深入-GIL与并发编程]]"
            }
        ]
    },
    {
        "dir_name": "JavaScript/TypeScript",
        "file_stem": "Symbol与元编程",
        "title": "JavaScript-Symbol与元编程",
        "course": "JavaScript/TypeScript",
        "chapter": "元编程",
        "difficulty": "ADVANCED",
        "tags": ["JavaScript", "Symbol", "元编程", "Well-known Symbols", "Symbol.iterator"],
        "aliases": ["JavaScript Symbol", "Well-known Symbols", "JS Meta-programming"],
        "source": "ECMA-262 §Symbol; MDN Symbol; ExploringJS Ch. Symbols by Dr. Axel Rauschmayer",
        "sections": [
            {
                "heading": "核心定义",
                "content": "ECMA-262定义Symbol为第七种原始类型(undefined/null/boolean/number/bigint/string/symbol)。Symbol('desc')每次调用返回全局唯一的symbol值(描述仅用于调试toString)。Symbol.for('key')在全局Symbol注册表中查找或创建共享symbol(跨realm/module)。Well-known Symbols(@@xxx)是JavaScript元编程的接口：@@iterator(Symbol.iterator)定义可迭代协议；@@toPrimitive控制对象→原始值转换；@@hasInstance自定义instanceof行为；@@species控制派生对象构造器(Array.map返回的默认用原类型)；@@toStringTag定义Object.prototype.toString的标签；@@isConcatSpreadable控制Array.prototype.concat是否展开对象；@@asyncIterator定义异步迭代协议。这些symbol是语言级的钩子——引擎根据对象是否定义这些symbol触发定制行为。"
            },
            {
                "heading": "关键结论",
                "content": "1.Symbol作为对象键不会出现在Object.keys/for...in中——可用Object.getOwnPropertySymbols获取(非私有,仅是隐藏) 2.自定义@@toPrimitive: 覆盖默认的valueOf→toString的优先级，接收hint('number'/'string'/'default') 3.为库添加@@iterator可使自定义集合支持for...of和展开运算符 4.Symbol.unscopables让with语句忽略某些属性(但with本身已不推荐) 5.为自定义类定义@@species: static get[Symbol.species](){return this}控制map返回的构造器类型 6.@@match/@@replace/@@search/@@split允许对象参与String.prototype对应方法(如正则替代方案)"
            },
            {
                "heading": "关联知识点",
                "content": "[[JavaScript-Proxy与Reflect]] [[JavaScript-Iterator与Generator]] [[Python深入-元类编程]]"
            }
        ]
    },
    {
        "dir_name": "JavaScript/TypeScript",
        "file_stem": "Map-Set-WeakMap",
        "title": "JavaScript-Map/Set/WeakMap/WeakSet",
        "course": "JavaScript/TypeScript",
        "chapter": "集合类型",
        "difficulty": "BASIC",
        "tags": ["JavaScript", "Map", "Set", "WeakMap", "WeakSet", "ES6"],
        "aliases": ["JavaScript Map", "WeakMap", "ES6 Collections"],
        "source": "ECMA-262 §Map/Set/WeakMap/WeakSet; MDN Keyed Collections; V8 blog: ES6 Collections",
        "sections": [
            {
                "heading": "核心定义",
                "content": "ES6引入四类集合Map/Set/WeakMap/WeakSet，解决Object仅支持字符串/Symbol键的限制。Map: 键值对集合，任意值(包括对象/NaN/-0)作为键，插入顺序迭代(entries/keys/values)。Set: 唯一值集合，SameValueZero算法比较(===但NaN等于自身，-0等于+0)。底层实现：V8中Map/Set基于确定性哈希表(OrderedHashTable)，平均O(1)插入/删除/查找，N个条目内存约N×(8+8+16)字节。WeakMap: 键必须是对象(不允许原始类型)，键为弱引用——键对象被GC时对应条目自动移除，不可迭代、无size属性(因为GC行为不确定)。WeakSet: 对象弱引用集合——add只接受对象。WeakRef和FinalizationRegistry(ES2021)是更基础层弱引用机制。"
            },
            {
                "heading": "关键结论",
                "content": "1.Map vs Object: Map保留插入顺序、任意类型键、优化频繁增删(size属性O(1) vs Object.keys O(n)) 2.WeakMap的核心用例：关联私有数据到DOM元素(HTML/SVG/DOM节点)→节点移除时自动清理 3.WeakMap实现私有属性: const privates=new WeakMap(); class Foo{constructor(){privates.set(this,{...})}} 4.Set的操作: 去重/交集/并集/差集——ES2025+将提供原生Set方法(.intersection/.union/.difference/.symmetricDifference) 5.WeakRef允许观察对象何时被GC(deref()返回undefined)——FinalizationRegistry注册GC后回调——但行为不确定不建议业务依赖 6.Map的迭代顺序与插入顺序一致(区别Object的无序/插入顺序) 7.WeakMap不能用于遍历/计数(count)——GC的不可预测性意味着内容会随时改变"
            },
            {
                "heading": "关联知识点",
                "content": "[[JavaScript-内存管理与内存泄漏]] [[JavaScript-Iterator与Generator]] [[JavaScript-Symbol与元编程]]"
            }
        ]
    },
    {
        "dir_name": "JavaScript/TypeScript",
        "file_stem": "装饰器与ReflectMetadata",
        "title": "TypeScript-装饰器与Reflect Metadata",
        "course": "JavaScript/TypeScript",
        "chapter": "装饰器",
        "difficulty": "INTERMEDIATE",
        "tags": ["TypeScript", "装饰器", "Decorator", "Reflect Metadata", "TC39", "NestJS"],
        "aliases": ["TypeScript Decorators", "Reflect Metadata", "TC39 Decorators Proposal"],
        "source": "TC39 Decorators Proposal (Stage 3, 2024); TypeScript Handbook: Decorators; reflect-metadata package (Polyfill)",
        "sections": [
            {
                "heading": "核心定义",
                "content": "TC39装饰器提案(Stage 3, 2024)定义装饰器为：type Decorator = (target, context) => { ... init, extra }。五种装饰器：Class/ClassMethod/ClassGetter/ClassSetter/ClassAutoAccessor/ClassField。context参数提供：kind(装饰类型)、name(成员名)、isStatic、isPrivate、addInitializer(注册init回调)→在类实例化或类定义完成时调用initializer链。装饰器在类定义时执行一次，不是在实例化时——实现了编译期横切关注点。TypeScript的experimentalDecorators使用旧版TC39提案(Stage 2)语法，与新版不完全兼容。reflect-metadata是ES7提议的polyfill——提供Reflect.defineMetadata(k,v,target)/Reflect.getMetadata(k,target)，在编译期通过emitDecoratorMetadata自动注入design:type/design:paramtypes/design:returntype元数据键。"
            },
            {
                "heading": "关键结论",
                "content": "1.装饰器vs高阶函数：装饰器在类定义时执行可访问类上下文(可修改原型/静态成员)，高阶函数在调用时执行 2.context.addInitializer(cb)支持异步初始化——若回调返回Promise，实例化等待完成 3.design:开头的元数据由TypeScript compiler自动注入(emitDecoratorMetadata:true) 4.装饰器在框架中的应用：Angular(@Component/@NgModule)、NestJS(@Controller/@Module)、InversifyJS(IoC容器绑定) 5.参数装饰器(@Param/@Body)是TypeScript特有，未进入TC39标准 6.装饰器组合顺序：多个装饰器从下向上执行(与Python相同)；各装饰器初始化的addInitializer也是FILO 7.与Python装饰器对比：Python装饰器可以直接替换函数/类，JS装饰器通过init/finisher方法修改目标"
            },
            {
                "heading": "关联知识点",
                "content": "[[TypeScript-类型系统]] [[Python深入-装饰器进阶]] [[JavaScript-Proxy与Reflect]]"
            }
        ]
    },
]


def main():
    json_path = Path(__file__).with_name("wiki_topics.json")

    if not json_path.exists():
        print(f"Error: {json_path} not found")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        existing = json.load(f)

    before = len(existing)
    print(f"Existing topics: {before}")

    existing.extend(NEW_TOPICS)

    after = len(existing)
    print(f"New topics added: {after - before}")
    print(f"Total topics: {after}")

    # Validate all topics have required keys
    required_keys = {"dir_name", "file_stem", "title", "course", "chapter", "difficulty",
                     "tags", "aliases", "source", "sections"}
    for i, topic in enumerate(NEW_TOPICS):
        missing = required_keys - set(topic.keys())
        if missing:
            print(f"WARNING: topic {i} ({topic.get('title', '?')}) missing keys: {missing}")
        # Check sections content length
        for j, section in enumerate(topic.get("sections", [])):
            content_len = len(section.get("content", ""))
            if content_len < 50 or content_len > 600:
                print(f"WARNING: topic {i} section {j} content length={content_len} "
                      f"(title={topic.get('title')}, heading={section.get('heading')})")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print("Written to wiki_topics.json")
    print(f"Added {len(NEW_TOPICS)} topics ({len([t for t in NEW_TOPICS if 'Python' in t['dir_name']])} Python, "
          f"{len([t for t in NEW_TOPICS if 'JavaScript' in t['dir_name']])} JS/TS)")


if __name__ == "__main__":
    main()
