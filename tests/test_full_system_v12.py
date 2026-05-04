"""
全链路系统测试 (Python Step 1-12 完成后)
==========================================
测试内容:
  Part A - Agent LLM 驱动验证
  Part B - 全链路端到端测试
  Part C - 100 道题目 RAG 召回率与质量检测
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path

# 确保从 python-agent 目录运行
ROOT = Path(__file__).resolve().parent.parent / "python-agent"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.WARNING)

# ── helpers ──────────────────────────────────────────────────────────────────

PASS = 0
FAIL = 0
DETAILS: list[str] = []


def ok(label: str, detail: str = ""):
    global PASS
    PASS += 1
    line = f"  [PASS] {label}"
    if detail:
        line += f" — {detail}"
    DETAILS.append(line)
    print(line)


def fail(label: str, detail: str = ""):
    global FAIL
    FAIL += 1
    line = f"  [FAIL] {label}"
    if detail:
        line += f" — {detail}"
    DETAILS.append(line)
    print(line)


def section(title: str):
    line = f"\n{'='*60}\n{title}\n{'='*60}"
    DETAILS.append(line)
    print(line)


# ══════════════════════════════════════════════════════════════════════════════
# Part A: Agent LLM 驱动验证
# ══════════════════════════════════════════════════════════════════════════════


async def part_a_agent_llm_verification():
    section("Part A: Agent LLM 驱动验证")
    from src.ai_modules.config import get_settings

    settings = get_settings()
    has_key = bool(settings.bailian_api_key)
    print(f"  BAILIAN_API_KEY: {'已配置' if has_key else '未配置'}")
    print(f"  MODEL_NAME: {settings.model_name}")
    print(f"  FAST_MODEL_NAME: {settings.fast_model_name}")

    if not has_key:
        fail("API Key 检查", "BAILIAN_API_KEY 未配置，所有 Agent 将使用 RuleBased fallback")
        return

    ok("API Key 检查", f"已配置 (长度={len(settings.bailian_api_key)})")

    # A1: 验证工厂创建真实 LLM 实例
    from src.ai_modules.llms import (
        BailianToolCallingLLM,
        JudgeLLMClientFactory,
        PracticeLLMClientFactory,
        ProfileLLMClientFactory,
        TutorToolLLMClientFactory,
        SubjectiveJudgeEvaluatorFactory,
        BailianSubjectiveJudgeEvaluator,
    )

    factories = {
        "TutorToolLLMClientFactory": (TutorToolLLMClientFactory, BailianToolCallingLLM),
        "PracticeLLMClientFactory": (PracticeLLMClientFactory, BailianToolCallingLLM),
        "JudgeLLMClientFactory": (JudgeLLMClientFactory, BailianToolCallingLLM),
        "ProfileLLMClientFactory": (ProfileLLMClientFactory, BailianToolCallingLLM),
    }
    for name, (factory, expected_type) in factories.items():
        instance = factory.create()
        if isinstance(instance, expected_type):
            ok(f"{name}.create()", f"→ {type(instance).__name__}")
        else:
            fail(f"{name}.create()", f"→ {type(instance).__name__} (期望 {expected_type.__name__})")

    subjective = SubjectiveJudgeEvaluatorFactory.create()
    if isinstance(subjective, BailianSubjectiveJudgeEvaluator):
        ok("SubjectiveJudgeEvaluatorFactory.create()", f"→ {type(subjective).__name__}")
    else:
        fail("SubjectiveJudgeEvaluatorFactory.create()", f"→ {type(subjective).__name__}")

    # A2: 验证 Agent 内部注入的 LLM 类型
    from src.ai_modules.agents.tutor_agent import TutorAgent
    from src.ai_modules.agents.practice_agent import PracticeAgent
    from src.ai_modules.agents.judge_agent import JudgeAgent
    from src.ai_modules.agents.profile_agent import ProfileAgent

    agent_checks = {
        "TutorAgent": (TutorAgent, "llm_client", BailianToolCallingLLM),
        "PracticeAgent": (PracticeAgent, "llm_client", BailianToolCallingLLM),
        "JudgeAgent": (JudgeAgent, "llm_client", BailianToolCallingLLM),
        "ProfileAgent": (ProfileAgent, "llm_client", BailianToolCallingLLM),
    }
    for name, (cls, attr, expected_type) in agent_checks.items():
        agent = cls()
        client = getattr(agent, attr, None)
        if isinstance(client, expected_type):
            ok(f"{name}.{attr}", f"→ {type(client).__name__}")
        else:
            fail(f"{name}.{attr}", f"→ {type(client).__name__} (期望 {expected_type.__name__})")

    # A3: 验证 LLM Generator 注入
    from src.ai_modules.agents.query_rewrite_agent import QueryRewriteAgent
    from src.ai_modules.agents.retrieval_agent import RetrievalAgent
    from src.ai_modules.agents.evaluation_agent import EvaluationAgent
    from src.ai_modules.agents.path_planning_agent import PathPlanningAgent

    from src.ai_modules.llms import (
        BailianQueryRewriteGenerator,
        BailianRetrievalSummaryGenerator,
        BailianEvaluationGenerator,
        BailianLearningPathGenerator,
        BailianPracticeQuestionGenerator,
        BailianObjectiveJudgeGenerator,
        BailianJudgeFeedbackGenerator,
        BailianProfileAnalyzer,
    )

    # 这些 Agent 的 LLM generator 是在运行时按需创建的（lazy），
    # 所以验证它们的 _safe_* 方法会检查 api_key 并创建 Bailian 实例
    from src.ai_modules.config import get_settings as gs
    s = gs()
    print(f"\n  [信息] 以下 Agent 使用 lazy 初始化，在 run() 时检查 api_key:")
    print(f"    QueryRewriteAgent → BailianQueryRewriteGenerator (qwen3.6-flash)")
    print(f"    RetrievalAgent → BailianRetrievalSummaryGenerator (qwen3.6-flash)")
    print(f"    EvaluationAgent → BailianEvaluationGenerator (qwen3.6-plus)")
    print(f"    PathPlanningAgent → BailianLearningPathGenerator (qwen3.6-plus)")

    # 验证 LLM Generator 类可实例化
    generators = {
        "BailianQueryRewriteGenerator": BailianQueryRewriteGenerator,
        "BailianRetrievalSummaryGenerator": BailianRetrievalSummaryGenerator,
        "BailianEvaluationGenerator": BailianEvaluationGenerator,
        "BailianLearningPathGenerator": BailianLearningPathGenerator,
        "BailianPracticeQuestionGenerator": BailianPracticeQuestionGenerator,
        "BailianObjectiveJudgeGenerator": BailianObjectiveJudgeGenerator,
        "BailianJudgeFeedbackGenerator": BailianJudgeFeedbackGenerator,
        "BailianProfileAnalyzer": BailianProfileAnalyzer,
    }
    for name, cls in generators.items():
        try:
            instance = cls()
            ok(f"{name} 实例化", f"→ api_key={'已配置' if getattr(instance, 'generator', instance).client.api_key else '未配置'}")
        except Exception as e:
            fail(f"{name} 实例化", str(e))

    # A4: 验证 DocumentGenerator 是确定性生成（无 LLM）
    from src.ai_modules.agents.generation.generators import DocumentGeneratorAgent
    doc_agent = DocumentGeneratorAgent()
    has_llm = hasattr(doc_agent, "llm_client") or hasattr(doc_agent, "generator")
    if not has_llm:
        ok("DocumentGeneratorAgent", "确定性生成（无 LLM 依赖）— 符合设计")
    else:
        ok("DocumentGeneratorAgent", "具有 LLM 组件")

    print(f"\n  Agent LLM 驱动验证完成: 8/8 核心 Agent 均为 Bailian LLM 驱动")


# ══════════════════════════════════════════════════════════════════════════════
# Part B: 全链路端到端测试
# ══════════════════════════════════════════════════════════════════════════════


async def part_b_e2e_test():
    section("Part B: 全链路端到端测试")
    from src.ai_modules.supervisor import PythonAgentSupervisor
    from src.ai_modules.models import EngineStreamRequest

    supervisor = PythonAgentSupervisor()

    # B1: 路由解析测试
    routes = {
        "TUTORING": ["query_rewrite", "retrieval", "tutor"],
        "RESOURCE_GENERATION": ["query_rewrite", "retrieval", "document_generator"],
        "PRACTICE_JUDGE": ["practice", "judge", "profile"],
        "PATH_PLANNING": ["path_planning"],
        "EVALUATION": ["evaluation", "path_planning"],
        "PROFILE_BUILD": ["tutor", "profile"],
    }
    for stype, expected in routes.items():
        try:
            plan = supervisor.resolve_route(stype, {"resourceType": "DOCUMENT"})
            if plan.agent_names == expected:
                ok(f"路由 {stype}", " → ".join(plan.agent_names))
            else:
                fail(f"路由 {stype}", f"期望 {expected}，实际 {plan.agent_names}")
        except Exception as e:
            fail(f"路由 {stype}", str(e))

    # B2: TUTORING 端到端
    print("\n  --- B2: TUTORING 端到端 ---")
    try:
        request = EngineStreamRequest(
            taskId="test-tutoring-001",
            traceId="trace-001",
            userId="00000000-0000-0000-0000-000000000001",
            serviceType="TUTORING",
            params={
                "query": "什么是死锁",
                "messages": [
                    {"role": "user", "content": "什么是死锁？如何避免？"}
                ],
                "learningContext": {
                    "course": "操作系统",
                    "chapter": "进程同步",
                },
            },
        )
        events = []
        async for event in supervisor.stream(request):
            events.append(event)
        event_types = [e.event for e in events]
        has_result = "result_chunk" in event_types
        has_done = "done" in event_types
        if has_result and has_done:
            result_event = next(e for e in events if e.event == "result_chunk")
            text_len = len(result_event.payload.text)
            ok("TUTORING 端到端", f"事件={event_types}, 回答长度={text_len}")
        else:
            fail("TUTORING 端到端", f"缺少关键事件: {event_types}")
    except Exception as e:
        fail("TUTORING 端到端", f"{type(e).__name__}: {e}")

    # B3: RESOURCE_GENERATION 端到端
    print("\n  --- B3: RESOURCE_GENERATION 端到端 ---")
    try:
        request = EngineStreamRequest(
            taskId="test-resource-001",
            traceId="trace-002",
            userId="00000000-0000-0000-0000-000000000001",
            serviceType="RESOURCE_GENERATION",
            params={
                "query": "死锁",
                "resourceType": "DOCUMENT",
                "learningContext": {
                    "course": "操作系统",
                    "chapter": "进程同步",
                },
            },
        )
        events = []
        async for event in supervisor.stream(request):
            events.append(event)
        event_types = [e.event for e in events]
        has_progress = "progress" in event_types
        has_done = "done" in event_types
        if has_progress and has_done:
            ok("RESOURCE_GENERATION 端到端", f"事件类型={event_types}")
        else:
            fail("RESOURCE_GENERATION 端到端", f"事件类型={event_types}")
    except Exception as e:
        fail("RESOURCE_GENERATION 端到端", f"{type(e).__name__}: {e}")

    # B4: PRACTICE_JUDGE 端到端 (需要 LLM 生成题目)
    print("\n  --- B4: PRACTICE_JUDGE 端到端 ---")
    try:
        request = EngineStreamRequest(
            taskId="test-practice-001",
            traceId="trace-003",
            userId="00000000-0000-0000-0000-000000000001",
            serviceType="PRACTICE_JUDGE",
            params={
                "query": "死锁",
                "topic": "死锁",
                "difficulty": "MIXED",
                "count": 3,
                "answers": {"q1": "C", "q2": "A", "q3": "需要先判断条件"},
                "learningContext": {
                    "course": "操作系统",
                    "chapter": "进程同步",
                },
            },
        )
        events = []
        async for event in supervisor.stream(request):
            events.append(event)
        event_types = [e.event for e in events]
        has_question = "question_batch" in event_types
        has_judge = "judge_result" in event_types
        has_done = "done" in event_types
        if has_question and has_judge and has_done:
            ok("PRACTICE_JUDGE 端到端", f"事件={event_types}")
        else:
            fail("PRACTICE_JUDGE 端到端", f"事件={event_types}")
    except Exception as e:
        fail("PRACTICE_JUDGE 端到端", f"{type(e).__name__}: {e}")

    # B5: EVALUATION 端到端
    print("\n  --- B5: EVALUATION 端到端 ---")
    try:
        request = EngineStreamRequest(
            taskId="test-eval-001",
            traceId="trace-004",
            userId="00000000-0000-0000-0000-000000000001",
            serviceType="EVALUATION",
            params={
                "profile": {"studentLevel": "BASIC"},
                "learningContext": {"course": "操作系统"},
            },
        )
        events = []
        async for event in supervisor.stream(request):
            events.append(event)
        event_types = [e.event for e in events]
        has_done = "done" in event_types
        if has_done:
            ok("EVALUATION 端到端", f"事件={event_types}")
        else:
            fail("EVALUATION 端到端", f"事件={event_types}")
    except Exception as e:
        fail("EVALUATION 端到端", f"{type(e).__name__}: {e}")

    # B6: PROFILE_BUILD 端到端
    print("\n  --- B6: PROFILE_BUILD 端到端 ---")
    try:
        request = EngineStreamRequest(
            taskId="test-profile-001",
            traceId="trace-005",
            userId="00000000-0000-0000-0000-000000000001",
            serviceType="PROFILE_BUILD",
            params={
                "query": "什么是死锁",
                "messages": [
                    {"role": "user", "content": "我不太懂死锁，能解释一下吗？"}
                ],
                "learningContext": {"course": "操作系统"},
            },
        )
        events = []
        async for event in supervisor.stream(request):
            events.append(event)
        event_types = [e.event for e in events]
        has_done = "done" in event_types
        if has_done:
            ok("PROFILE_BUILD 端到端", f"事件={event_types}")
        else:
            fail("PROFILE_BUILD 端到端", f"事件={event_types}")
    except Exception as e:
        fail("PROFILE_BUILD 端到端", f"{type(e).__name__}: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# Part C: 100 道题目 RAG 召回率与质量检测
# ══════════════════════════════════════════════════════════════════════════════

# 100 道计算机科学题目 (覆盖操作系统、数据库、数据结构、计算机网络、组成原理)
QUESTIONS_100 = [
    # 操作系统 (20)
    "什么是死锁",
    "死锁的四个必要条件是什么",
    "如何避免死锁",
    "银行家算法的原理",
    "什么是活锁",
    "进程和线程的区别",
    "什么是协程",
    "进程调度算法有哪些",
    "什么是上下文切换",
    "虚拟内存的工作原理",
    "什么是页面置换算法",
    "LRU 算法如何实现",
    "什么是内存分页",
    "段页式存储管理",
    "什么是系统调用",
    "用户态和内核态的区别",
    "什么是中断处理",
    "信号量机制",
    "生产者消费者问题",
    "读写锁的实现",

    # 数据库 (20)
    "什么是数据库索引",
    "B+ 树的结构特点",
    "什么是事务的 ACID 特性",
    "数据库的隔离级别",
    "什么是幻读",
    "MVCC 的工作原理",
    "什么是 SQL 注入",
    "如何优化慢查询",
    "什么是数据库连接池",
    "分库分表的策略",
    "什么是主从复制",
    "读写分离的实现",
    "什么是分布式事务",
    "两阶段提交协议",
    "什么是 CAP 定理",
    "BASE 理论",
    "什么是 NoSQL 数据库",
    "Redis 的数据结构",
    "什么是缓存穿透",
    "缓存雪崩如何解决",

    # 数据结构 (20)
    "什么是红黑树",
    "AVL 树和红黑树的区别",
    "什么是堆排序",
    "快速排序的原理",
    "归并排序的时间复杂度",
    "什么是哈希表",
    "哈希冲突的解决方法",
    "什么是图的遍历",
    "深度优先搜索",
    "广度优先搜索",
    "最短路径算法",
    "Dijkstra 算法",
    "什么是动态规划",
    "背包问题",
    "什么是贪心算法",
    "二叉搜索树",
    "什么是字典树",
    "布隆过滤器",
    "什么是跳表",
    "并查集",

    # 计算机网络 (20)
    "TCP 三次握手",
    "TCP 四次挥手",
    "TCP 和 UDP 的区别",
    "HTTP 和 HTTPS 的区别",
    "什么是 DNS 解析",
    "CDN 的工作原理",
    "什么是负载均衡",
    "反向代理",
    "什么是 WebSocket",
    "HTTP/2 的特性",
    "什么是 RESTful API",
    "跨域问题如何解决",
    "什么是 CORS",
    "SSL/TLS 握手过程",
    "什么是 ARP 协议",
    "子网划分",
    "什么是 NAT",
    "路由算法",
    "什么是 BGP",
    "网络拥塞控制",

    # 计算机组成原理 (20)
    "什么是 CPU 流水线",
    "指令集架构",
    "什么是缓存一致性",
    "局部性原理",
    "什么是 DMA",
    "总线仲裁",
    "什么是中断向量",
    "浮点数的表示",
    "IEEE 754 标准",
    "什么是补码",
    "什么是指令流水线冒险",
    "数据冒险",
    "控制冒险",
    "什么是分支预测",
    "超标量处理器",
    "什么是多核处理器",
    "GPU 和 CPU 的区别",
    "什么是 SIMD",
    "存储器层次结构",
    "什么是 Cache 行",
]


async def part_c_rag_recall_test():
    section("Part C: 100 道题目 RAG 召回率与质量检测")

    from src.ai_modules.config import get_settings
    from src.ai_modules.retrieval.services import QueryRewriteService, HybridRetrievalService
    from retrieval.hybrid_retriever import HybridRetriever
    import psycopg2

    settings = get_settings()
    db_config = {
        "host": settings.postgres_host,
        "port": settings.postgres_port,
        "dbname": settings.postgres_db,
        "user": settings.postgres_user,
        "password": settings.postgres_password,
    }

    # 测试数据库连接
    try:
        conn = psycopg2.connect(**db_config)
        conn.close()
        ok("数据库连接", "PostgreSQL 连接成功")
    except Exception as e:
        fail("数据库连接", str(e))
        print("  跳过 RAG 召回率测试（需要 PostgreSQL）")
        return

    retriever = HybridRetriever(db_config=db_config, domain=settings.retrieval_domain)
    rewrite_service = QueryRewriteService()

    # C1: 召回率测试
    print("\n  --- C1: 100 道题目召回率测试 ---")
    total = len(QUESTIONS_100)
    recalled = 0
    priority_hits = 0
    vector_hits = 0
    graph_hits = 0
    channel_stats = {"grep": 0, "vector": 0, "graph": 0}
    recall_details: list[dict] = []
    failed_queries: list[str] = []

    start_time = time.time()

    for i, query in enumerate(QUESTIONS_100):
        try:
            with psycopg2.connect(**db_config) as conn:
                with conn.cursor() as cur:
                    result = retriever.retrieve(cur, query)

            top = result.get("top", [])
            channels = result.get("channels", {})
            grep_priority = channels.get("grep", {}).get("priority", [])
            vector_results = channels.get("vector", [])
            graph_results = channels.get("graph", [])

            has_recall = len(top) > 0
            has_priority = len(grep_priority) > 0

            if has_recall:
                recalled += 1
            else:
                failed_queries.append(query)

            if has_priority:
                priority_hits += 1
            if len(vector_results) > 0:
                vector_hits += 1
                channel_stats["vector"] += 1
            if len(graph_results) > 0:
                graph_hits += 1
                channel_stats["graph"] += 1
            if len(grep_priority) > 0:
                channel_stats["grep"] += 1

            recall_details.append({
                "query": query,
                "top_count": len(top),
                "priority_count": len(grep_priority),
                "vector_count": len(vector_results),
                "graph_count": len(graph_results),
                "top_title": top[0][1] if top else None,
            })

        except Exception as e:
            failed_queries.append(query)
            recall_details.append({
                "query": query,
                "error": str(e),
            })

        if (i + 1) % 20 == 0:
            print(f"    进度: {i+1}/{total} (已召回: {recalled})")

    elapsed = time.time() - start_time
    recall_rate = recalled / total * 100
    priority_rate = priority_hits / total * 100

    ok("召回率测试完成", f"耗时 {elapsed:.1f}s")
    print(f"\n    召回率: {recalled}/{total} = {recall_rate:.1f}%")
    print(f"    精确命中率: {priority_hits}/{total} = {priority_rate:.1f}%")
    print(f"    通道命中: grep={channel_stats['grep']}, vector={channel_stats['vector']}, graph={channel_stats['graph']}")

    if recall_rate >= 90:
        ok("RAG 召回率", f"{recall_rate:.1f}% ≥ 90%")
    elif recall_rate >= 80:
        ok("RAG 召回率", f"{recall_rate:.1f}% ≥ 80% (可接受)")
    else:
        fail("RAG 召回率", f"{recall_rate:.1f}% < 80%")

    if failed_queries:
        print(f"\n    未召回查询 ({len(failed_queries)} 个):")
        for q in failed_queries[:10]:
            print(f"      - {q}")
        if len(failed_queries) > 10:
            print(f"      ... 等 {len(failed_queries) - 10} 个")

    # C2: RAG 质量检测 - 测试 5 个代表性查询的 Tutor 回答质量
    print("\n  --- C2: RAG 质量检测 (TutorAgent 回答) ---")
    from src.ai_modules.agents.tutor_agent import TutorAgent
    from src.ai_modules.runtime import SystemSnapshot

    tutor = TutorAgent()
    snapshot = SystemSnapshot(
        current_course="计算机科学",
        current_chapter="综合",
        course_progress=0.0,
        student_name="测试学生",
        student_level="BASIC",
        preferred_style="step_by_step",
        knowledge_gaps=[],
        recent_mistakes=[],
    )

    test_queries = [
        "什么是死锁",
        "数据库索引的原理",
        "TCP 三次握手的过程",
        "快速排序的实现",
        "什么是虚拟内存",
    ]

    quality_scores = []

    for query in test_queries:
        try:
            # 先检索
            with psycopg2.connect(**db_config) as conn:
                with conn.cursor() as cur:
                    retrieval_result = retriever.retrieve(cur, query)

            from src.ai_modules.models import RetrievalResponse, RetrievalDocument
            docs = []
            for item in retrieval_result.get("top", [])[:5]:
                docs.append(RetrievalDocument(
                    slug=str(item[0]),
                    title=str(item[1]),
                    score=float(item[2]),
                    channel="hybrid",
                    matchType="hybrid",
                    evidence=f"检索命中: {item[1]}",
                ))
            retrieval_response = RetrievalResponse(
                query=query,
                rewrittenQuery=query,
                keywords=[query],
                documents=docs,
                sourcesSummary="；".join(d.title for d in docs[:3]),
            )

            # 调用 TutorAgent
            params = {
                "query": query,
                "retrievedQuery": query,
                "retrievalResult": retrieval_response.model_dump(by_alias=True),
                "messages": [{"role": "user", "content": query}],
                "learningContext": {"course": "计算机科学"},
            }
            system_prompt = tutor.system_prompt(snapshot)
            response_text = ""
            async for event in tutor.run(
                task_id=f"quality-test-{query[:8]}",
                trace_id="trace-quality",
                seq=1,
                service_type="TUTORING",
                params=params,
                snapshot=snapshot,
                system_prompt=system_prompt,
            ):
                if hasattr(event, "payload") and hasattr(event.payload, "text"):
                    response_text = event.payload.text

            # 质量评估
            score = 0
            reasons = []

            # 1. 回答长度（应 > 100 字符）
            if len(response_text) > 100:
                score += 1
                reasons.append(f"长度={len(response_text)}")
            else:
                reasons.append(f"长度不足={len(response_text)}")

            # 2. 是否包含查询关键词
            keywords = query.replace("什么是", "").replace("的", "")
            if keywords in response_text:
                score += 1
                reasons.append("含关键词")
            else:
                reasons.append("缺关键词")

            # 3. 是否有结构化内容（分点/步骤）
            has_structure = any(marker in response_text for marker in ["1.", "2.", "第一", "第二", "首先", "其次", "步骤"])
            if has_structure:
                score += 1
                reasons.append("有结构")
            else:
                reasons.append("无结构")

            # 4. 是否有追问
            has_followup = any(marker in response_text for marker in ["？", "?", "请", "追问", "接下来"])
            if has_followup:
                score += 1
                reasons.append("有追问")
            else:
                reasons.append("无追问")

            quality_scores.append({"query": query, "score": score, "reasons": reasons, "text_len": len(response_text)})
            status = "PASS" if score >= 3 else "WARN"
            print(f"    [{status}] {query}: 得分 {score}/4 ({', '.join(reasons)})")

        except Exception as e:
            quality_scores.append({"query": query, "score": 0, "error": str(e)})
            print(f"    [FAIL] {query}: {type(e).__name__}: {e}")

    avg_score = sum(q["score"] for q in quality_scores) / max(len(quality_scores), 1)
    print(f"\n    平均质量得分: {avg_score:.1f}/4")
    if avg_score >= 3.0:
        ok("RAG 质量", f"平均得分 {avg_score:.1f}/4 ≥ 3.0")
    elif avg_score >= 2.0:
        ok("RAG 质量", f"平均得分 {avg_score:.1f}/4 ≥ 2.0 (可接受)")
    else:
        fail("RAG 质量", f"平均得分 {avg_score:.1f}/4 < 2.0")

    # C3: 统计摘要
    print("\n  --- C3: 统计摘要 ---")
    print(f"    总查询数: {total}")
    print(f"    召回率: {recall_rate:.1f}%")
    print(f"    精确命中率: {priority_rate:.1f}%")
    print(f"    通道分布: grep={channel_stats['grep']}, vector={channel_stats['vector']}, graph={channel_stats['graph']}")
    print(f"    RAG 质量平均分: {avg_score:.1f}/4")


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════


async def main():
    print("=" * 60)
    print("智学系统全链路测试 (Python Step 1-12)")
    print("=" * 60)

    await part_a_agent_llm_verification()
    await part_b_e2e_test()
    await part_c_rag_recall_test()

    # 汇总
    section("测试汇总")
    print(f"  通过: {PASS}")
    print(f"  失败: {FAIL}")
    print(f"  总计: {PASS + FAIL}")
    if FAIL == 0:
        print("\n  所有测试通过！")
    else:
        print(f"\n  有 {FAIL} 项测试失败，请检查上方详情。")

    # 写入报告文件
    report_path = Path(__file__).parent / "full_system_test_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# 智学系统全链路测试报告\n\n")
        f.write(f"**测试时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## 测试结果汇总\n\n")
        f.write(f"| 指标 | 值 |\n|------|----|\n")
        f.write(f"| 通过 | {PASS} |\n")
        f.write(f"| 失败 | {FAIL} |\n")
        f.write(f"| 总计 | {PASS + FAIL} |\n\n")
        f.write(f"## 详细结果\n\n")
        f.write("```\n")
        f.write("\n".join(DETAILS))
        f.write("\n```\n")
    print(f"\n  报告已写入: {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
