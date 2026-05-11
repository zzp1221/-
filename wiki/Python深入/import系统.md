---
title: "Python深入-import系统与模块加载"
course: Python深入
chapter: 模块系统
difficulty: INTERMEDIATE
tags: [Python, import, 模块, importlib, sys.modules, 命名空间包]
aliases: [Python Import System, Module Loading, sys.meta_path]
source: "Python docs: importlib; PEP 302 (New Import Hooks); PEP 420 (Namespace Packages); PEP 451 (ModuleSpec)"
updated_at: 2026-05-02
---

## 核心定义

import语句的执行路径：importlib.__import__ → importlib._bootstrap._find_and_load。sys.modules(dict)缓存所有已加载模块(模块名→模块对象)，导入前先查此缓存。模块查找分为两级：元路径查找器(sys.meta_path，包含BuiltinImporter、FrozenImporter、PathFinder)和路径查找器(sys.path_hooks，用于处理文件路径)。PathFinder扫描sys.path列表，对每个路径尝试所有path_hook，为匹配的后缀(.py/.pyc/.so/.pyd)创建Loader。PEP 451引入ModuleSpec，将查找和加载解耦——spec定义了模块的origin、loader、子模块查找方式等完整信息。PEP 420定义了命名空间包：无__init__.py的目录仍可在不同路径下分布。

## 关键结论

1.importlib.reload重新执行模块代码，更新sys.modules中的条目，但不更新已有from导入的变量(仅刷新模块全局变量) 2.相对导入(.foo/..bar)仅在包内模块中使用——__main__模块不支持相对导入 3.__pycache__中的.pyc字节码加速后续导入，基于源文件的时间戳和magic number决定是否重新编译 4.zip文件可通过sys.path直接导入(zipimport内部处理器)——这是pyinstaller打包的基础 5.import hook可用于从数据库/网络/加密归档加载代码——实现importlib.abc.Loader即可 6.循环导入(A导B，B导A)：解释器会返回已部分执行的模块对象(用过的名字可用，未执行到的raise AttributeError)

## 关联知识点

[[Python深入-CPython对象模型]] [[JavaScript-ES模块vs CommonJS]] [[Go语言-接口与类型系统]]
