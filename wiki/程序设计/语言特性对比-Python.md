---
title: 语言特性对比-Python
course: 程序设计
chapter: 编程语言对比
difficulty: BASIC
tags: [Python, 解释型, 动态类型, 多范式, 数据科学, 列表推导, GIL, PEP]
aliases: [Python Language, Dynamic Typing, GIL, Data Science, List Comprehension]
source:
  - Guido van Rossum《The Python Language Reference》
  - Luciano Ramalho《Fluent Python》
  - David Beazley《Python Cookbook》
updated_at: 2026-05-02

---

## 核心定义

Python 由 Guido van Rossum 于 1991 年创建，设计哲学强调代码可读性和简洁性。"Pythonic"概念——代码应当清晰、明确、有一种显而易见的正确写法（"There should be one-- and preferably only one --obvious way to do it"，《The Zen of Python》）。Python 是全球使用最广泛的语言之一——从 Web 开发到数据科学到系统自动化无处不在。

**核心特征**：
- **动态强类型**：类型是值的属性，变量可重新绑定到不同类型的值，但类型错误在运行时抛出（非隐式类型转换）
- **解释型 + 字节码**：CPython 将源码编译为 `.pyc` 字节码后再由虚拟机解释执行
- **显著空白**（Significant Whitespace）：缩进决定代码块结构——不用大括号或 begin/end
- **多范式**：过程式、面向对象（class 关键字）、函数式（lambda, map, mapcomps, `functools`）
- **GC：引用计数 + 循环检测**：引用计数为零立即回收（确定性），`gc` 模块处理循环引用
- **GIL**（Global Interpreter Lock）：CPython 的核心限制——无论多少核 CPU，同一时间只有一个 Python 线程可以执行 Python 字节码（保障引用计数安全但严重限制了 CPU 密集型多线程）

**Python 数据模型**（Data Model）是最核心的"魔术"——`__dunder__` 特殊方法控制对象行为的协议。如 `__init__`（构造）、`__str__`（打印）、`__iter__`（迭代）、`__getitem__`（索引）、`__call__`（可调用）、`__enter__`/`__exit__`（上下文管理器）。

**核心语言特性**：
- **列表推导**（List Comprehension）：`[x*x for x in range(10) if x%2==0]` —— Pythonic 的核心表述
- **生成器**（Generator）：惰性求值序列 `(x*x for x in range(10))` 或 `yield` 函数——内存友好处理大/无限序列
- **装饰器**（Decorator）：包装函数/类以扩展行为——`@functools.lru_cache`、`@staticmethod`、`@pytest.mark`
- **上下文管理器**（Context Manager）：`with open(f) as file:` —— 自动资源管理（PEP 343）
- **f-string**（Python 3.6+）：`f"Hello {name}, score: {score:.2f}"`——简洁的字符串插值
- **类型提示**（Type Hints, 3.5+）：可选的渐进类型——仅供静态检查工具（mypy、Pyright）和 IDE 使用，运行时忽略

**Python 生态**：Django/Flask/FastAPI（Web）、NumPy/Pandas/Matplotlib（科学计算/数据分析）、Jupyter（交互式数据科学 Notebook）、Scikit-learn/PyTorch/TensorFlow（机器学习/深度学习）、pytest（测试）、Requests/httpx/Scrapy（HTTP/爬虫）、Pydantic（数据校验）。

**版本要点**：Python 2.7 (已废弃 2020-01-01, EOL) → Python 3.x (当前标准, 3.11/3.12 在 CPython 加速方面有巨大提升——Faster CPython 项目使 Python 速度提升了 25-60%)。

**GIL 与并发**：CPython 的 GIL 使多线程无法利用多核用于 CPU 密集型任务。绕过方法：(a) 多进程（`multiprocessing` 每个进程独立 GIL）；(b) 使用 C 扩展（NumPy 在 C 层释放 GIL 实现并行）；(c) asyncio（单线程异步 I/O，对 I/O 密集应用极高并发——非 CPU 密集）；(d) 尝试 `nogil` Python（PEP 703 实验性无 GIL 版本，2024 年目标）。

## 关键结论

- Python 的成功源于可读性和生态——"可执行的伪代码" + 最丰富的科学计算和 AI 库
- "Python 太慢" 的刻板印象需区分：CPython 解释执行确实慢于 C/Java 但大多数 I/O 密集型应用不受影响；计算密集部分通常用 C/C++/Rust 扩展编写（科学计算库内部即这样）
- Pythonic 是一种代码审美——简洁优于冗长，清晰优于巧妙，扁平优于嵌套
- GIL 是 CPython 实现的选择而非 Python 语言的设计——Jython（JVM）、IronPython（.NET）无 GIL

## 易错点

1. 可变默认参数——`def f(lst=[])` 这会在多次调用间共享同一个列表（默认参数在函数定义时创建一次）
2. GIL 不保护多个操作组成的一致性——`+= 1` 不是原子操作，多线程累加需要锁或原子数据结构
3. `is` vs `==`——`is` 判断对象身份（同一内存地址），`==` 判断值相等。`[] == []` 是 True 但 `[] is []` 是 False
4. Python 的变量不是"盒子"——是"标签/指针"指向堆上的对象，赋值是重新绑定标签而非复制数据

## 例题

**例题1**：为以下功能编写 Pythonic 代码：(a) 从列表中获取所有偶数并平方；(b) 读取大文件逐行处理避免一次性加载全文件。

**解答**：
```python
# (a)
evens_squared = [x * x for x in numbers if x % 2 == 0]
# (b) 生成器惰性逐行处理
def process_large_file(path):
    with open(path) as f:
        for line in f:  # 逐行惰性读取，非全部加载
            yield line.strip()
```

**例题2**：解释 Python 中 `__new__` 和 `__init__` 的区别，给出代码示例。

**解答**：`__new__` 是类方法（构造对象——分配内存并返回实例），`__init__` 是实例方法（初始化——设置对象的初始状态）。`__new__` 先被调用返回 self 再传递给 `__init__(self, ...)`。
```python
class Singleton:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    def __init__(self, value):
        self.value = value  # __init__ 每次调用仍会执行
```
注意：即使 `__new__` 返回相同实例，`__init__` 每次都会重新执行——应添加标志位防止重复初始化。

## 关联页面

[[函数式编程]] [[异步编程]] [[类型系统]] [[动态规划]]
