---
title: "GIT内部原理"
course: 程序设计
chapter: 版本控制
difficulty: INTERMEDIATE
tags: [程序设计, Git, 版本控制, 内部原理]
aliases: [Git Internals, Git Objects, Content-Addressable]
source: "Pro Git (Chacon & Straub) Ch 10; Scott Chacon《Git Internals》; Git源代码"
updated_at: 2026-05-02
---

## 核心定义

Git是内容寻址文件系统(content-addressable filesystem)上的版本控制系统。核心三类对象(存储在.git/objects/)：blob(存储文件内容的压缩二进制——文件名等不保存于blob)，tree(目录的'内容清单'——指针指向blob和其他tree+名称+mode)，commit(快照——指向一个tree(根目录)+parent commit(s)+author/committer/date/message)。每个对象通过SHA-1(已迁移SHA-256)哈希内容命名，前两位作目录名，剩余作为文件名(如.git/objects/ab/cdef123...)。浅层对象结构和四类ref(branch/tag/HEAD/remote refs)形成Git的完整数据模型。

## Pack与垃圾回收

Git自动将松散对象打包成packfiles(git gc——.git/objects/pack/)——每个pack包含一个pack索引文件(.idx，object hash→offset映射)和数据文件(.pack)。Pack存储完整的基准对象和基于其的delta压缩差异(减量存储——增量使得历史版本空间开销小)。Git gc使用启发式(保留最近的对象松散存储——push/pull频繁的数据仍快,较旧的打包存档)。Commit graph(git commit-graph write)通过预计算文件加速log和merge-base操作。

## 关键结论

1. Branch仅是指向commit的40字节文件——廉价创建/销毁 2. Detached HEAD状态：HEAD指向直接commit(而非branch)——检查或实验用 3. rebase重写commit历史(产生新commit,旧commit orphaned——在reflog中保留30天) 4. Git的DAG(Directed Acyclic Graph)保证parent指向唯一(合并commit有两个parents)。5. 'git cat-file -p'可内部查看任意类型commit

## 关联知识点

[[软件工程-版本控制与Git]] [[数据结构-有向无环图DAG]] [[声明式vs命令式深度对比]]
