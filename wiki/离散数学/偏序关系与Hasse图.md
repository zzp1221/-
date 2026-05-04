---
title: 偏序关系与Hasse图
course: 离散数学
chapter: 关系
difficulty: INTERMEDIATE
tags: [偏序关系, Hasse图, 偏序集, 极大元, 极小元, 上下界, 格]
aliases: [Partial Order, Poset, Hasse Diagram]
source:
  - Kenneth H. Rosen《离散数学及其应用》
updated_at: 2026-05-02
---

## 核心定义

偏序关系（Partial Order / Partially Ordered Set, Poset）是集合 A 上满足**自反性、反对称性、传递性**的二元关系，通常记为 ≤ 或 ≼。记偏序集为 (A, ≼)。偏序的核心特征是并非任意两个元素都可比较：可能存在 a, b ∈ A 使得 a ≮ b 且 b ≮ a，这区别于全序（Total Order）——全序中任意两个元素都是可比较的。**Hasse图**是偏序集的图形化表示，其绘制规则为：(1) 每个元素用一个点表示；(2) 若 a ≺ b（即 a ≼ b 且 a ≠ b，且不存在 c 使 a ≺ c ≺ b——a 是 b 的**直接前驱/覆盖者**），则 b 点画在 a 点上方并用线段连接；(3) 省略自环（自反性隐含）和由传递性可导出的边。重要概念：**极小元** min-el（不存在比它更小的元素）、**极大元** max-el（不存在比它更大的元素）、**最小元**（小于等于所有元素）、**最大元**（大于等于所有元素）、上界/下界、上确界/下确界、**良序集**（每个非空子集都有最小元的全序集）。

## 关键结论

- 偏序 ≠ 全序：全序（如 ≤ 在实数上）要求任意两个元素可比较，偏序（如 ⊆ 在幂集上）允许不可比较的元素对
- 极小/极大元不一定唯一（一个偏序集可以有多个极小（大）元），但最小/最大元若存在则唯一
- Hasse 图中，若 a 从下往上连到 b，意味着 a 直接覆盖 b（a immediately precedes b），中间没有其他元素
- 有限偏序集至少有一个极小元和一个极大元
- 上确界（supremum）是最小上界，下确界（infimum）是最大下界——它们是格论的基础
- Hasse 图是判定偏序结构、验证格性质的直观工具

## 易错点

1. 将 Hasse 图中不相连的元素认为没有可比性——确是如此（直接相连表示覆盖关系，但可能通过传递性有间接可比性）
2. 混淆极小元与最小元：极小元满足"没有元素比它小"（可能多个），最小元满足"它比所有元素都小"（若存在则唯一）
3. 在 Hasse 图中误画传递闭包边：正确的 Hasse 图只画覆盖关系（直接边），依赖传递性推导的间接关系不画边

## 例题

**例题1**：设 A = {1, 2, 3, 4, 6, 12}，偏序关系为整除关系 |。画出 (A, |) 的 Hasse 图，指出极大元、极小元、最大元、最小元。

**解答**：
整除关系下，1 整除所有数，12 被所有数整除。

Hasse 图（从下到上）：
  12
 /  \
6    4
|  \/
|  /\
3    2
 \  /
  1

极小元（也是最小元）：1；极大元（也是最大元）：12。

**例题2**：判断偏序集 (P({a,b,c}), ⊆) 是否为全序。

**解答**：否。例如 {a} 和 {b} 不可比较（{a} ⊈ {b} 且 {b} ⊈ {a}）。幂集上的 ⊆ 是经典的偏序但非全序的例子。

## 代码示例

```python
def hasse_cover(relation, elements):
    """从偏序关系中提取Hasse图的覆盖关系(去除传递边)"""
    cover = set()
    for a in elements:
        for b in elements:
            if (a, b) in relation and a != b:
                # 检查是否有中间元素c使得 a<c<b
                has_intermediate = any((a, c) in relation and 
                                       (c, b) in relation and 
                                       a != c != b 
                                       for c in elements)
                if not has_intermediate:
                    cover.add((a, b))
    return cover

# 整除关系偏序集
A = [1, 2, 3, 4, 6, 12]
divides = {(a, b) for a in A for b in A if b % a == 0}
covers = hasse_cover(divides, A)
print(f"覆盖关系(Hasse边): {sorted(covers)}")
# [(1,2), (1,3), (2,4), (2,6), (3,6), (4,12), (6,12)]
```

## 关联页面

[[二元关系]] [[等价关系]] [[格-偏序格-代数格]] [[相容关系]] [[图论基础-有向图]]
