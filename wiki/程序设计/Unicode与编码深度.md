---
title: "Unicode与编码深度"
course: 程序设计
chapter: 数据表示
difficulty: INTERMEDIATE
tags: [程序设计, Unicode, 编码, UTF-8, 字符集]
aliases: [Unicode, UTF-8, Character Encoding, Code Points]
source: "Unicode标准 v15; Davis et al. (UTS/Unicode Technical Standards); Spolsky《The Absolute Minimum Every Software Developer Must Know About Unicode》"
updated_at: 2026-05-02
---

## 核心定义

Unicode为每一个字符分配唯一的码点(code point, U+XXXX)。当前v15定义149,186个字符(涵盖所有现代和古代文字)。编码形式(encoding form)将码点映射为字节序列——UTF-8(变长1-4字节,ASCII兼容:0xxxxxxx→1字节, 110xxxxx 10xxxxxx→2字节, 1110xxxx 10xxxxxx 10xxxxxx→3字节, 11110xxx → 4字节,单字节最高到U+007F)，UTF-16(变长2-4字节, surrogate pair编码BMP外的码点,U+D800-DBFF高代理+U+DC00-U+DFFF低代理: code point = (H-0xD800)*0x400 + (L-0xDC00) + 0x10000)。UTF-32(固定4字节)。

## 表示与陷阱

Unicode规范化形式(normalization:NFC/NFD/NFKC/NFKD)解决多表示等价(如'é'可以precomposed U+00E9或decomposed e+combining acute U+0065 U+0301)。NFC将分解后的字符合成简并;NFD分解到基本字符+组合标记。排序(collation)通过CLDR的地区化排序权重(不匹配的码点二进制序)。emoji序列——多个码点组合为一个可见字形(ZWJ连字er+ZWJ+连字ee=？？？；skin tone modifier是组合修饰符)。编程：locale-sensitive vs locale-insensitive编码区分——字符流/byte流的'Unicode sandwich'最佳实践(仅在系统边界转换，内部始终使用codepoint)。

## 关键结论

1. 英文text中最多的是1字节UTF-8序列(ASCII)。 2. 永远不要假设1 byte=1 char或1 code unit=1 code point(使用正确的string lib/API/codepoint iterator) 3. Unicode中的emoji操作复杂(检查字符串长度/grapheme cluster boundaries——word/line break算法) 4. 大小写映射(uppercase/lowercase)是locale-dependent(如突厥语I/dotted-i)。5. BOM(Byte Order Mark U+FEFF)在UTF-8中不推荐但常见(仅Windows式工具)在UTF-16中必须分辨LE/BE

## 关联知识点

[[程序设计-正则表达式引擎实现]] [[Go语言-String与[]byte转换]] [[数据库原理-字符集与排序规则]]
