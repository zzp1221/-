"""
Generate resources for new wiki topics in 信息安全, 分布式系统, 计算机图形学.
Also supplements existing courses with resources for newly added wiki topics.
96 total resources (24 per course × 3 new courses + 24 supplements).
"""
import sys, os, json, uuid, time
from pathlib import Path
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from knowledge.import_pipeline import run_import


def make_content(rtype, title, course, chapter, topics):
    if rtype == "READING":
        sections = "\n\n".join([f"## {t}\n\n{t}是{course}中{chapter}的重要概念，需要结合理论和实践来深入理解。" for t in topics])
        return f"# {title}\n\n## 概述\n\n本文档详细讲解{course}中{chapter}的核心知识点。\n\n{sections}\n\n## 总结\n\n以上内容涵盖了{chapter}的核心要点。"
    elif rtype == "QUIZ":
        questions = "\n\n".join([f"## 题{i+1}. 简述{t}的核心概念和应用场景。\n\n**答案要点**:\n- {t}的定义与特性\n- 关键技术原理\n- 实际应用场景" for i, t in enumerate(topics)])
        return f"# {title}\n\n{questions}"
    elif rtype == "CODE":
        code_blocks = "\n\n".join([f"## {t}\n\n```python\n# {t}实现\ndef demo_{i}():\n    pass  # TODO\n```" for i, t in enumerate(topics)])
        return f"# {title}\n\n## 实验目标\n\n掌握{chapter}的代码实现。\n\n{code_blocks}"
    elif rtype == "PRACTICE":
        steps = "\n\n".join([f"### 步骤{i+1}: {t}\n\n1. 理解{t}原理\n2. 动手实践\n3. 验证结果" for i, t in enumerate(topics)])
        return f"# {title}\n\n## 实验目标\n\n通过实践掌握{chapter}。\n\n{steps}"
    elif rtype == "SLIDES":
        slides = "\n\n".join([f"## 第{i+1}部分: {t}\n\n- 核心概念\n- 关键技术\n- 应用案例" for i, t in enumerate(topics)])
        return f"# {title}\n\n{slides}"
    elif rtype == "MINDMAP":
        return f"# {title}\n\n## 知识图谱\n\n中心节点: {chapter}\n\n" + "\n\n".join([f"### {t}\n\n- 核心概念\n- 关联知识" for t in topics])
    return f"# {title}\n\n{chapter}"


# Resource definitions: (type, title, course, chapter, topics)
RESOURCE_DEFS = [
    # ── 信息安全 (24) ──
    ("READING", "信息安全-密码学基础精讲", "信息安全", "密码学基础", ["对称加密与DES-AES", "非对称加密RSA", "哈希函数与SHA系列", "数字签名原理", "Diffie-Hellman密钥交换"]),
    ("READING", "信息安全-网络安全协议详解", "信息安全", "网络安全协议", ["SSL与TLS协议详解", "IPSec协议体系", "Kerberos认证协议", "OAuth2与OpenID Connect"]),
    ("READING", "信息安全-Web安全攻防实战", "信息安全", "Web应用安全", ["SQL注入攻击与防御", "跨站脚本攻击XSS", "跨站请求伪造CSRF", "OWASP Top 10"]),
    ("READING", "信息安全-零信任与云安全架构", "信息安全", "新兴安全技术", ["零信任安全架构", "云安全架构", "隐私计算与联邦学习", "AI安全与对抗攻击"]),
    ("QUIZ", "信息安全-密码学题库", "信息安全", "密码学基础", ["对称加密AES", "非对称加密RSA", "哈希函数SHA", "数字签名", "PKI证书体系"]),
    ("QUIZ", "信息安全-Web安全题库", "信息安全", "Web应用安全", ["SQL注入", "XSS攻击", "CSRF防护", "OWASP Top 10", "会话安全"]),
    ("QUIZ", "信息安全-网络安全协议题库", "信息安全", "网络安全协议", ["TLS握手过程", "IPSec模式", "Kerberos认证", "OAuth2流程", "防火墙技术"]),
    ("QUIZ", "信息安全-系统安全题库", "信息安全", "系统安全", ["访问控制RBAC", "缓冲区溢出", "恶意软件防护", "沙箱隔离", "安全审计"]),
    ("CODE", "信息安全-AES加密算法实现", "信息安全", "密码学基础", ["AES加解密", "ECB/CBC模式", "密钥扩展", "S盒变换"]),
    ("CODE", "信息安全-RSA数字签名实现", "信息安全", "密码学基础", ["RSA密钥生成", "签名与验签", "大数运算", "素数检测"]),
    ("CODE", "信息安全-SQL注入检测工具", "信息安全", "Web应用安全", ["SQL注入检测", "参数化查询", "WAF规则", "输入验证"]),
    ("CODE", "信息安全-网络端口扫描器", "信息安全", "网络安全", ["TCP连接扫描", "SYN半开扫描", "服务识别", "结果报告"]),
    ("PRACTICE", "信息安全-PKI证书签发实验", "信息安全", "密码学基础", ["CA根证书", "证书签发", "证书链验证", "CRL/OCSP"]),
    ("PRACTICE", "信息安全-TLS握手抓包分析", "信息安全", "网络安全协议", ["Wireshark抓包", "ClientHello", "ServerHello", "密钥交换"]),
    ("PRACTICE", "信息安全-XSS漏洞利用与防御", "信息安全", "Web应用安全", ["反射型XSS", "存储型XSS", "CSP策略", "输出编码"]),
    ("PRACTICE", "信息安全-渗透测试流程演练", "信息安全", "安全治理", ["信息收集", "漏洞扫描", "渗透利用", "报告撰写"]),
    ("SLIDES", "信息安全-密码学体系大纲", "信息安全", "密码学基础", ["对称加密", "非对称加密", "哈希函数", "数字签名", "PKI"]),
    ("SLIDES", "信息安全-网络安全攻防大纲", "信息安全", "网络安全", ["攻击分类", "防御体系", "检测响应", "安全管理"]),
    ("SLIDES", "信息安全-Web安全防护大纲", "信息安全", "Web应用安全", ["注入攻击", "XSS/CSRF", "认证安全", "OWASP指南"]),
    ("SLIDES", "信息安全-新兴技术安全大纲", "信息安全", "新兴安全技术", ["云安全", "IoT安全", "AI安全", "隐私计算"]),
    ("MINDMAP", "信息安全-密码学知识图谱", "信息安全", "密码学基础", ["对称加密体系", "非对称加密体系", "哈希与签名", "密钥管理", "PKI信任模型"]),
    ("MINDMAP", "信息安全-网络安全知识图谱", "信息安全", "网络安全", ["网络攻击类型", "防御技术栈", "安全协议", "监控响应"]),
    ("MINDMAP", "信息安全-应用安全知识图谱", "信息安全", "Web应用安全", ["注入攻击", "跨站攻击", "认证缺陷", "安全编码"]),
    ("MINDMAP", "信息安全-安全治理知识图谱", "信息安全", "安全治理", ["风险评估", "等保合规", "渗透测试", "应急响应", "安全运营"]),

    # ── 分布式系统 (24) ──
    ("READING", "分布式系统-CAP与一致性模型", "分布式系统", "基础理论", ["CAP定理详解", "一致性模型强/最终/因果", "FLP不可能定理", "分布式时间与向量时钟"]),
    ("READING", "分布式系统-Paxos与Raft详解", "分布式系统", "一致性协议", ["Paxos协议详解", "Raft协议详解", "Multi-Paxos与日志复制", "ZAB协议"]),
    ("READING", "分布式系统-存储引擎深度解析", "分布式系统", "分布式存储", ["GFS与HDFS架构", "Bigtable与HBase", "Spanner与TrueTime", "Cassandra与Dynamo"]),
    ("READING", "分布式系统-微服务治理实战", "分布式系统", "分布式服务", ["服务发现与注册", "熔断与降级", "分布式追踪", "Service Mesh"]),
    ("QUIZ", "分布式系统-一致性协议题库", "分布式系统", "一致性协议", ["Paxos选举", "Raft日志复制", "2PC提交", "3PC提交", "Saga补偿"]),
    ("QUIZ", "分布式系统-分布式存储题库", "分布式系统", "分布式存储", ["一致性哈希", "数据分片", "副本策略", "LSM-Tree"]),
    ("QUIZ", "分布式系统-消息与协调题库", "分布式系统", "消息系统与协调", ["Kafka架构", "ZooKeeper原理", "分布式锁", "分布式ID"]),
    ("QUIZ", "分布式系统-可靠性工程题库", "分布式系统", "可靠性工程", ["分布式事务", "幂等设计", "混沌工程", "故障注入"]),
    ("CODE", "分布式系统-Raft共识算法实现", "分布式系统", "一致性协议", ["Leader选举", "日志复制", "安全性保证", "成员变更"]),
    ("CODE", "分布式系统-一致性哈希实现", "分布式系统", "分布式存储", ["哈希环", "虚拟节点", "数据迁移", "负载均衡"]),
    ("CODE", "分布式系统-分布式ID生成器", "分布式系统", "可靠性工程", ["Snowflake算法", "时钟回拨处理", "序列号生成", "Worker ID分配"]),
    ("CODE", "分布式系统-简易RPC框架", "分布式系统", "分布式服务", ["动态代理", "序列化", "网络传输", "服务注册"]),
    ("PRACTICE", "分布式系统-Kafka消息队列实验", "分布式系统", "消息系统", ["Topic创建", "Producer发送", "Consumer消费", "消费者组"]),
    ("PRACTICE", "分布式系统-ZooKeeper分布式锁实验", "分布式系统", "协调服务", ["临时顺序节点", "锁获取", "锁释放", "惊群效应"]),
    ("PRACTICE", "分布式系统-Kubernetes部署实验", "分布式系统", "云原生架构", ["Deployment", "Service", "Ingress", "HPA自动扩缩"]),
    ("PRACTICE", "分布式系统-混沌工程实验", "分布式系统", "可靠性工程", ["故障注入", "稳态假设", "爆炸半径", "自动恢复"]),
    ("SLIDES", "分布式系统-理论基础大纲", "分布式系统", "基础理论", ["CAP定理", "一致性模型", "时钟同步", "容错理论"]),
    ("SLIDES", "分布式系统-共识算法大纲", "分布式系统", "一致性协议", ["Paxos", "Raft", "ZAB", "2PC/3PC"]),
    ("SLIDES", "分布式系统-存储与计算大纲", "分布式系统", "分布式存储", ["GFS/HDFS", "Bigtable/HBase", "MapReduce", "Spark/Flink"]),
    ("SLIDES", "分布式系统-微服务架构大纲", "分布式系统", "分布式服务", ["服务治理", "负载均衡", "熔断降级", "可观测性"]),
    ("MINDMAP", "分布式系统-理论体系图谱", "分布式系统", "基础理论", ["CAP/BASE", "一致性模型", "时钟与序", "容错理论"]),
    ("MINDMAP", "分布式系统-协议与算法图谱", "分布式系统", "一致性协议", ["Paxos族", "Raft族", "两阶段提交", "补偿事务"]),
    ("MINDMAP", "分布式系统-存储体系图谱", "分布式系统", "分布式存储", ["文件系统", "列存储", "KV存储", "图存储", "时序存储"]),
    ("MINDMAP", "分布式系统-工程实践图谱", "分布式系统", "可靠性工程", ["事务方案", "幂等设计", "混沌工程", "监控告警"]),

    # ── 计算机图形学 (24) ──
    ("READING", "计算机图形学-数学基础与变换", "计算机图形学", "数学基础", ["向量与矩阵变换", "齐次坐标与仿射变换", "四元数与旋转表示", "几何变换流水线"]),
    ("READING", "计算机图形学-渲染管线全解析", "计算机图形学", "渲染管线", ["图形渲染管线概述", "顶点着色与图元装配", "光栅化算法", "片元着色与深度测试"]),
    ("READING", "计算机图形学-光照与PBR渲染", "计算机图形学", "光照与着色", ["光照模型Lambert/Phong", "PBR物理渲染原理", "纹理映射与Mipmap", "环境光遮蔽AO"]),
    ("READING", "计算机图形学-光线追踪技术", "计算机图形学", "光线追踪", ["光线追踪原理", "加速结构BVH/KD-Tree", "全局光照与路径追踪", "实时光线追踪DXR/RTX"]),
    ("QUIZ", "计算机图形学-数学变换题库", "计算机图形学", "数学基础", ["矩阵变换", "齐次坐标", "四元数旋转", "插值方法"]),
    ("QUIZ", "计算机图形学-渲染管线题库", "计算机图形学", "渲染管线", ["光栅化", "深度测试", "模板缓冲", "OpenGL/Vulkan"]),
    ("QUIZ", "计算机图形学-光照着色题库", "计算机图形学", "光照与着色", ["Phong模型", "PBR原理", "纹理映射", "法线贴图"]),
    ("QUIZ", "计算机图形学-几何与动画题库", "计算机图形学", "几何与动画", ["网格表示", "曲面细分", "骨骼动画", "粒子系统"]),
    ("CODE", "计算机图形学-软光栅化器实现", "计算机图形学", "渲染管线", ["三角形光栅化", "深度缓冲", "透视校正插值", "Blinn-Phong着色"]),
    ("CODE", "计算机图形学-光线追踪渲染器", "计算机图形学", "光线追踪", ["光线生成", "求交计算", "反射折射", "阴影投射"]),
    ("CODE", "计算机图形学-Bresenham画线算法", "计算机图形学", "光栅化", ["整数运算", "增量计算", "误差累积", "八分对称"]),
    ("CODE", "计算机图形学-贝塞尔曲线绘制", "计算机图形学", "几何", ["de Casteljau算法", "控制点交互", "曲线细分", "曲面生成"]),
    ("PRACTICE", "计算机图形学-OpenGL入门实验", "计算机图形学", "渲染管线", ["窗口创建", "三角形绘制", "着色器编译", "纹理加载"]),
    ("PRACTICE", "计算机图形学-Shader编程实验", "计算机图形学", "着色", ["顶点着色器", "片段着色器", "光照计算", "后处理效果"]),
    ("PRACTICE", "计算机图形学-模型加载与渲染", "计算机图形学", "几何", ["OBJ格式解析", "法线计算", "材质加载", "场景渲染"]),
    ("PRACTICE", "计算机图形学-延迟渲染实现", "计算机图形学", "高级渲染", ["G-Buffer生成", "光照Pass", "屏幕空间效果", "HDR色调映射"]),
    ("SLIDES", "计算机图形学-渲染管线大纲", "计算机图形学", "渲染管线", ["顶点处理", "光栅化", "片元处理", "输出合并"]),
    ("SLIDES", "计算机图形学-光照模型大纲", "计算机图形学", "光照与着色", ["局部光照", "全局光照", "PBR理论", "实时渲染"]),
    ("SLIDES", "计算机图形学-几何表示大纲", "计算机图形学", "几何", ["网格", "曲面", "细分", "隐式表示"]),
    ("SLIDES", "计算机图形学-高级渲染大纲", "计算机图形学", "高级渲染", ["光线追踪", "阴影技术", "后处理", "GPU计算"]),
    ("MINDMAP", "计算机图形学-渲染体系图谱", "计算机图形学", "渲染管线", ["光栅化管线", "光线追踪管线", "混合渲染", "GPU架构"]),
    ("MINDMAP", "计算机图形学-光照与材质图谱", "计算机图形学", "光照与着色", ["经典光照", "PBR材质", "纹理技术", "全局光照"]),
    ("MINDMAP", "计算机图形学-几何处理图谱", "计算机图形学", "几何", ["网格操作", "曲面表示", "细分方法", "物理模拟"]),
    ("MINDMAP", "计算机图形学-技术全景图谱", "计算机图形学", "全景", ["实时渲染", "离线渲染", "GPU编程", "虚拟现实", "科学可视化"]),

    # ── 现有课程补充 (24) ──
    ("READING", "操作系统-容器技术原理详解", "操作系统", "虚拟化", ["容器与Docker", "Namespace隔离", "Cgroups资源限制", "OCI标准"]),
    ("CODE", "操作系统-系统调用追踪工具", "操作系统", "系统结构", ["strace原理", "系统调用表", "ptrace接口", "syscall拦截"]),
    ("QUIZ", "操作系统-RTOS与实时调度题库", "操作系统", "实时系统", ["RMS调度", "EDF调度", "优先级反转", "实时约束"]),
    ("PRACTICE", "操作系统-中断处理流程分析", "操作系统", "中断机制", ["IDT表", "中断上下文", "top/bottom half", "APIC路由"]),
    ("READING", "数据库-数据湖与湖仓一体", "数据库原理", "数据架构", ["数据仓库", "数据湖", "ETL/ELT", "Iceberg/Delta Lake"]),
    ("CODE", "数据库-图数据库Cypher查询", "数据库原理", "NoSQL", ["Neo4j安装", "Cypher语法", "路径查询", "图算法"]),
    ("QUIZ", "数据库-分库分表与Sharding题库", "数据库原理", "数据库架构", ["水平拆分", "分片策略", "跨分片查询", "分布式ID"]),
    ("PRACTICE", "数据库-时序数据库InfluxDB实验", "数据库原理", "NoSQL", ["数据写入", "连续查询", "降采样", "保留策略"]),
    ("READING", "计算机网络-QUIC与HTTP3详解", "计算机网络", "传输层", ["QUIC协议", "0-RTT握手", "流多路复用", "连接迁移"]),
    ("CODE", "计算机网络-SDN控制器实验", "计算机网络", "网络架构", ["OpenFlow协议", "流表下发", "拓扑发现", "流量工程"]),
    ("QUIZ", "计算机网络-IoT协议题库", "计算机网络", "应用层", ["MQTT QoS", "CoAP协议", "轻量级协议", "物联网架构"]),
    ("PRACTICE", "计算机网络-MQTT消息通信实验", "计算机网络", "应用层", ["Broker部署", "发布订阅", "主题通配符", "遗嘱消息"]),
    ("READING", "编译原理-WebAssembly与现代编译", "编译原理", "编译目标", ["Wasm指令集", "WASI接口", "Emscripten工具链", "LLVM到Wasm"]),
    ("CODE", "编译原理-LLVM Pass开发", "编译原理", "代码优化", ["Pass框架", "分析Pass", "变换Pass", "Pass管理器"]),
    ("QUIZ", "编译原理-GC算法题库", "编译原理", "运行时", ["标记清除", "分代回收", "并发GC", "G1/ZGC"]),
    ("PRACTICE", "编译原理-垃圾回收可视化", "编译原理", "运行时", ["GC Roots追踪", "标记过程", "回收过程", "内存碎片"]),
    ("READING", "计算机组成原理-RISC-V架构详解", "计算机组成原理", "指令系统", ["RV32I基础指令", "扩展模块", "特权级", "自定义扩展"]),
    ("CODE", "计算机组成原理-RISC-V汇编实践", "计算机组成原理", "指令系统", ["RV32I汇编", "指令编码", "伪指令", "系统调用"]),
    ("QUIZ", "计算机组成原理-异构计算题库", "计算机组成原理", "处理器架构", ["GPU架构", "FPGA加速", "TPU脉动阵列", "CUDA编程"]),
    ("PRACTICE", "计算机组成原理-NoC拓扑仿真", "计算机组成原理", "多核架构", ["Mesh拓扑", "XY路由", "虚通道", "性能分析"]),
    ("READING", "程序设计-Go并发编程实战", "程序设计", "并发编程", ["Goroutine", "Channel", "select多路复用", "GMP调度"]),
    ("CODE", "程序设计-Kotlin协程网络请求", "程序设计", "异步编程", ["suspend函数", "async/await", "协程作用域", "异常处理"]),
    ("QUIZ", "程序设计-Rust所有权题库", "程序设计", "内存安全", ["所有权规则", "借用检查", "生命周期标注", "智能指针"]),
    ("PRACTICE", "程序设计-Go并发爬虫实战", "程序设计", "并发编程", ["Worker Pool", "Channel通信", "Context取消", "错误处理"]),
    ("READING", "软件工程-云原生技术栈", "软件工程", "架构设计", ["容器化", "Kubernetes", "微服务", "GitOps"]),
    ("CODE", "软件工程-Istio流量管理", "软件工程", "微服务架构", ["金丝雀发布", "流量镜像", "故障注入", "熔断配置"]),
    ("QUIZ", "软件工程-混沌工程题库", "软件工程", "可靠性工程", ["稳态假设", "故障注入", "爆炸半径", "自动化实验"]),
    ("PRACTICE", "软件工程-Prometheus监控实验", "软件工程", "可观测性", ["指标采集", "PromQL查询", "Grafana面板", "告警规则"]),
    ("READING", "离散数学-模态逻辑与Kripke语义", "离散数学", "逻辑", ["模态算子", "可能世界", "可达关系", "S4/S5系统"]),
    ("CODE", "离散数学-信息熵计算器", "离散数学", "信息论", ["熵计算", "条件熵", "互信息", "KL散度"]),
    ("QUIZ", "离散数学-范畴论题库", "离散数学", "抽象代数", ["范畴定义", "函子", "自然变换", "伴随函子"]),
    ("PRACTICE", "离散数学-模态逻辑Tableau证明", "离散数学", "逻辑", ["Kripke模型", "可满足性", "Tableau规则", "自动证明"]),
]


def build_resource_list():
    all_resources = []
    for rtype, title, course, chapter, topics in RESOURCE_DEFS:
        all_resources.append({
            "title": title,
            "type": rtype,
            "content": make_content(rtype, title, course, chapter, topics),
            "course": course,
            "chapter": chapter,
            "difficulty": "INTERMEDIATE",
            "description": f"{title} - {course}课程{chapter}章节的学习资源，涵盖：{', '.join(topics[:3])}",
            "source_url": f"wiki://{course}/{chapter}",
            "tags": [course, chapter] + topics[:3],
        })
    return all_resources


def main():
    dry_run = "--dry-run" in sys.argv
    print("=" * 60)
    print("New Course & Supplement Resources Generator")
    print("=" * 60)

    resources = build_resource_list()
    print(f"\nTotal resources: {len(resources)}")

    type_counts = Counter(r["type"] for r in resources)
    for t, c in sorted(type_counts.items()):
        print(f"  {t}: {c}")

    course_counts = Counter(r["course"] for r in resources)
    for co, c in sorted(course_counts.items()):
        print(f"  {co}: {c}")

    if dry_run:
        print("\n[DRY RUN]")
        return

    run_import(resources, label="new_courses+supplement")
    print(f"\nDone. {len(resources)} resources imported.")


if __name__ == "__main__":
    main()
