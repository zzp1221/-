---
title: "Python深入-CPython对象模型"
course: Python深入
chapter: 解释器内部
difficulty: ADVANCED
tags: [Python, CPython, 对象模型, PyObject, PyTypeObject, slot]
aliases: [CPython Object Model, PyObject Internals]
source: "CPython source: Include/object.h, Objects/typeobject.c; Python docs: C API Reference; 《CPython Internals》(Shaw 2020)"
updated_at: 2026-05-02
---

## 核心定义

CPython中一切数据都是PyObject指针。基础结构PyObject包含ob_refcnt(引用计数)和ob_type(指向PyTypeObject的指针)。变长对象(PyVarObject)额外包含ob_size(元素数)。PyTypeObject是类型的元类在C层的体现——定义tp_new/tp_init/tp_dealloc/tp_getattro/tp_setattro/tp_call/tp_iter/tp_hash等函数指针(slot)。调用obj.method()的实际路径：type(obj).__dict__['method']返回未绑定方法→__get__通过实例绑定→执行。属性访问obj.attr最终走向tp_getattro→_PyObject_GenericGetAttrWithDict→依次检查：数据描述符→实例__dict__→非数据描述符。type是PyTypeObject的元类在C层的实例。

## 关键结论

1.小整数池：CPython预分配-5~256的PyLongObject对象(tp_dealloc时放入free_list而非释放) 2.字符串intern：符合标识符命名规则或长度≤1的字符串自动放入interned字典，全局共享 3.列表的over-allocation：appending时obj_size按公式new_allocated = (newsize>>3)+(newsize<9?3:6)预留容量 4.Python 3.6+字典使用紧凑表：indices稀疏数组(每个条目占1字节)和entries密集数组(preserve insertion order) 5.tp_slot重载可改变类型的底层行为——例如__getattribute__的tp_slot重载影响所有属性访问 6.ob_type的修改体现对象的动态性——实例方法可以通过设置__class__改变类型(Python 3.11+已限制)

## 关联知识点

[[Python深入-GIL与并发编程]] [[Python深入-内存管理与GC]] [[Python深入-元类编程]] [[Python深入-描述符协议]]
