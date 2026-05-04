"""
全链路系统测试 V2
==================
Part 1: Java 认证链路 (注册 → 登录 → /me → 登出)
Part 2: Python Agent 功能测试 (6 种 serviceType × 5 维度)
Part 3: Java 全链路 (submit → SSE stream)
Part 4: 测试报告生成

5 个测试维度:
  D1 - 响应时间 (Response Time)
  D2 - 正确性 (Correctness / Output Structure)
  D3 - SSE 事件序列 (Event Sequence)
  D4 - 错误处理 (Error Handling)
  D5 - 输出质量 (Output Quality)
"""

from __future__ import annotations

import asyncio
import json
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

# ── 配置 ─────────────────────────────────────────────────────────────────────

JAVA_BASE = "http://localhost:8081"
PYTHON_BASE = "http://localhost:8000"

TIMEOUT = httpx.Timeout(300.0, connect=10.0)

TEST_USER = {
    "loginId": f"test_chain_{uuid.uuid4().hex[:8]}",
    "password": "Test@123456",
    "fullName": "全链路测试用户",
    "majorCode": "CS",
}

# ── 结果收集 ──────────────────────────────────────────────────────────────────


@dataclass
class TestResult:
    name: str
    passed: bool
    dimension: str  # D1-D5
    detail: str = ""
    duration_ms: float = 0.0


@dataclass
class AgentTestSuite:
    service_type: str
    results: list[TestResult] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.passed)


ALL_SUITES: list[AgentTestSuite] = []
AUTH_RESULTS: list[TestResult] = []
CHAIN_RESULTS: list[TestResult] = []


def record(suite: AgentTestSuite | None, result: TestResult):
    if suite:
        suite.results.append(result)
    tag = "PASS" if result.passed else "FAIL"
    ms = f" ({result.duration_ms:.0f}ms)" if result.duration_ms else ""
    print(f"    [{tag}] [{result.dimension}] {result.name}{ms} — {result.detail}")


# ── Part 1: Java 认证链路 ────────────────────────────────────────────────────


async def part1_auth_chain(client: httpx.AsyncClient):
    print("\n" + "=" * 70)
    print("Part 1: Java 认证链路测试")
    print("=" * 70)

    token = None
    user_id = None

    # 1.1 注册
    print("\n  [1.1] 注册新用户")
    t0 = time.perf_counter()
    try:
        resp = await client.post(f"{JAVA_BASE}/api/auth/register", json=TEST_USER)
        elapsed = (time.perf_counter() - t0) * 1000
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("token")
            user = data.get("user", {})
            user_id = user.get("userId")
            record(None, TestResult(
                name="注册", passed=True, dimension="D2",
                detail=f"userId={user_id}, loginId={user.get('loginId')}",
                duration_ms=elapsed,
            ))
            AUTH_RESULTS.append(TestResult(
                name="注册", passed=True, dimension="D2",
                detail=f"status={resp.status_code}", duration_ms=elapsed,
            ))
        elif resp.status_code == 409:
            record(None, TestResult(
                name="注册", passed=True, dimension="D2",
                detail="用户已存在，跳过注册",
                duration_ms=elapsed,
            ))
            AUTH_RESULTS.append(TestResult(
                name="注册(已存在)", passed=True, dimension="D2",
                detail="LOGIN_ID_EXISTS", duration_ms=elapsed,
            ))
        else:
            record(None, TestResult(
                name="注册", passed=False, dimension="D2",
                detail=f"status={resp.status_code}, body={resp.text[:200]}",
                duration_ms=elapsed,
            ))
            AUTH_RESULTS.append(TestResult(
                name="注册", passed=False, dimension="D2",
                detail=f"unexpected status {resp.status_code}", duration_ms=elapsed,
            ))
    except Exception as e:
        elapsed = (time.perf_counter() - t0) * 1000
        record(None, TestResult(
            name="注册", passed=False, dimension="D4",
            detail=f"{type(e).__name__}: {e}", duration_ms=elapsed,
        ))
        AUTH_RESULTS.append(TestResult(
            name="注册", passed=False, dimension="D4",
            detail=str(e), duration_ms=elapsed,
        ))

    # 1.2 登录
    # 注意: AuthService.login() 标注了 @Transactional(readOnly = true),
    # 但 auditService.log() 执行 INSERT, 导致 PostgreSQL 报错
    # "cannot execute INSERT in a read-only transaction".
    # 这是 Java 后端的已知 bug, 测试中用 register 返回的 token 作为 fallback.
    print("\n  [1.2] 登录")
    t0 = time.perf_counter()
    try:
        resp = await client.post(f"{JAVA_BASE}/api/auth/login", json={
            "loginId": TEST_USER["loginId"],
            "password": TEST_USER["password"],
        })
        elapsed = (time.perf_counter() - t0) * 1000
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("token")
            user = data.get("user", {})
            user_id = user.get("userId")
            has_token = bool(token and len(token) > 20)
            record(None, TestResult(
                name="登录", passed=has_token, dimension="D2",
                detail=f"token长度={len(token) if token else 0}, userId={user_id}",
                duration_ms=elapsed,
            ))
            AUTH_RESULTS.append(TestResult(
                name="登录", passed=has_token, dimension="D2",
                detail=f"token={token[:20]}..." if token else "no token",
                duration_ms=elapsed,
            ))
            AUTH_RESULTS.append(TestResult(
                name="登录响应时间", passed=elapsed < 3000, dimension="D1",
                detail=f"{elapsed:.0f}ms (阈值<3000ms)", duration_ms=elapsed,
            ))
        elif resp.status_code == 500 or (resp.status_code == 401 and token):
            # 已知 bug: readOnly 事务 + audit INSERT 冲突
            record(None, TestResult(
                name="登录", passed=False, dimension="D2",
                detail=f"已知bug: @Transactional(readOnly=true) + audit INSERT 冲突, status={resp.status_code}",
                duration_ms=elapsed,
            ))
            AUTH_RESULTS.append(TestResult(
                name="登录(已知bug)", passed=False, dimension="D2",
                detail="readOnly事务+audit INSERT冲突, 使用register token fallback",
                duration_ms=elapsed,
            ))
        else:
            record(None, TestResult(
                name="登录", passed=False, dimension="D2",
                detail=f"status={resp.status_code}, body={resp.text[:200]}",
                duration_ms=elapsed,
            ))
            AUTH_RESULTS.append(TestResult(
                name="登录", passed=False, dimension="D2",
                detail=f"status={resp.status_code}", duration_ms=elapsed,
            ))
    except Exception as e:
        elapsed = (time.perf_counter() - t0) * 1000
        record(None, TestResult(
            name="登录", passed=False, dimension="D4",
            detail=f"{type(e).__name__}: {e}", duration_ms=elapsed,
        ))
        AUTH_RESULTS.append(TestResult(
            name="登录", passed=False, dimension="D4",
            detail=str(e), duration_ms=elapsed,
        ))

    if not token:
        print("\n  [SKIP] 无法获取 token，跳过后续认证测试")
        return None

    headers = {"Authorization": f"Bearer {token}"}

    # 1.3 获取当前用户
    print("\n  [1.3] GET /api/auth/me")
    t0 = time.perf_counter()
    try:
        resp = await client.get(f"{JAVA_BASE}/api/auth/me", headers=headers)
        elapsed = (time.perf_counter() - t0) * 1000
        if resp.status_code == 200:
            data = resp.json()
            record(None, TestResult(
                name="获取当前用户", passed=True, dimension="D2",
                detail=f"userId={data.get('userId')}, loginId={data.get('loginId')}",
                duration_ms=elapsed,
            ))
            AUTH_RESULTS.append(TestResult(
                name="GET /me", passed=True, dimension="D2",
                detail="返回用户信息正确", duration_ms=elapsed,
            ))
        else:
            record(None, TestResult(
                name="获取当前用户", passed=False, dimension="D2",
                detail=f"status={resp.status_code}", duration_ms=elapsed,
            ))
            AUTH_RESULTS.append(TestResult(
                name="GET /me", passed=False, dimension="D2",
                detail=f"status={resp.status_code}", duration_ms=elapsed,
            ))
    except Exception as e:
        elapsed = (time.perf_counter() - t0) * 1000
        AUTH_RESULTS.append(TestResult(
            name="GET /me", passed=False, dimension="D4",
            detail=str(e), duration_ms=elapsed,
        ))

    # 1.4 未认证访问 (应返回 401)
    print("\n  [1.4] 未认证访问 /api/auth/me (期望 401)")
    t0 = time.perf_counter()
    try:
        resp = await client.get(f"{JAVA_BASE}/api/auth/me")
        elapsed = (time.perf_counter() - t0) * 1000
        is_401 = resp.status_code == 401
        body = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
        record(None, TestResult(
            name="未认证访问", passed=is_401, dimension="D4",
            detail=f"status={resp.status_code}, code={body.get('code')}",
            duration_ms=elapsed,
        ))
        AUTH_RESULTS.append(TestResult(
            name="未认证401", passed=is_401, dimension="D4",
            detail=f"status={resp.status_code}", duration_ms=elapsed,
        ))
    except Exception as e:
        elapsed = (time.perf_counter() - t0) * 1000
        AUTH_RESULTS.append(TestResult(
            name="未认证401", passed=False, dimension="D4",
            detail=str(e), duration_ms=elapsed,
        ))

    # 1.5 错误密码登录 (应返回 401)
    print("\n  [1.5] 错误密码登录 (期望 401)")
    t0 = time.perf_counter()
    try:
        resp = await client.post(f"{JAVA_BASE}/api/auth/login", json={
            "loginId": TEST_USER["loginId"],
            "password": "wrong_password_123",
        })
        elapsed = (time.perf_counter() - t0) * 1000
        is_401 = resp.status_code == 401
        record(None, TestResult(
            name="错误密码", passed=is_401, dimension="D4",
            detail=f"status={resp.status_code}",
            duration_ms=elapsed,
        ))
        AUTH_RESULTS.append(TestResult(
            name="错误密码401", passed=is_401, dimension="D4",
            detail=f"status={resp.status_code}", duration_ms=elapsed,
        ))
    except Exception as e:
        elapsed = (time.perf_counter() - t0) * 1000
        AUTH_RESULTS.append(TestResult(
            name="错误密码401", passed=False, dimension="D4",
            detail=str(e), duration_ms=elapsed,
        ))

    # 1.6 登出
    print("\n  [1.6] 登出")
    t0 = time.perf_counter()
    try:
        resp = await client.post(f"{JAVA_BASE}/api/auth/logout", headers=headers)
        elapsed = (time.perf_counter() - t0) * 1000
        # 登出是审计操作，应返回 200
        record(None, TestResult(
            name="登出", passed=resp.status_code == 200, dimension="D2",
            detail=f"status={resp.status_code}",
            duration_ms=elapsed,
        ))
        AUTH_RESULTS.append(TestResult(
            name="登出", passed=resp.status_code == 200, dimension="D2",
            detail=f"status={resp.status_code}", duration_ms=elapsed,
        ))
    except Exception as e:
        elapsed = (time.perf_counter() - t0) * 1000
        AUTH_RESULTS.append(TestResult(
            name="登出", passed=False, dimension="D4",
            detail=str(e), duration_ms=elapsed,
        ))

    return token, user_id


# ── Part 2: Python Agent 功能测试 ────────────────────────────────────────────


def _parse_sse_events(raw: str) -> list[dict[str, Any]]:
    """解析 SSE 文本为事件列表。"""
    events = []
    current_event = {}
    for line in raw.split("\n"):
        line = line.strip()
        if line.startswith("event:"):
            current_event = {"event": line[len("event:"):].strip()}
        elif line.startswith("data:"):
            current_event["data"] = line[len("data:"):].strip()
        elif line == "" and current_event:
            if "event" in current_event:
                try:
                    current_event["payload"] = json.loads(current_event.get("data", "{}"))
                except json.JSONDecodeError:
                    current_event["payload"] = current_event.get("data", "")
                events.append(current_event)
            current_event = {}
    if current_event and "event" in current_event:
        try:
            current_event["payload"] = json.loads(current_event.get("data", "{}"))
        except json.JSONDecodeError:
            current_event["payload"] = current_event.get("data", "")
        events.append(current_event)
    return events


async def _test_agent(
    suite: AgentTestSuite,
    client: httpx.AsyncClient,
    service_type: str,
    params: dict[str, Any],
    expected_events: list[str],
    quality_checks: dict[str, Any],
    label: str,
):
    """对单个 agent 进行 5 维度测试。"""
    task_id = f"test-{service_type.lower()}-{uuid.uuid4().hex[:6]}"
    trace_id = f"trace-{uuid.uuid4().hex[:6]}"

    request_body = {
        "serviceType": service_type,
        "taskId": task_id,
        "traceId": trace_id,
        "userId": "00000000-0000-0000-0000-000000000001",
        "params": params,
    }

    # D1: 响应时间 + D3: SSE 事件序列
    t0 = time.perf_counter()
    try:
        resp = await client.post(
            f"{PYTHON_BASE}/internal/smart-engine/stream",
            json=request_body,
            headers={"Accept": "text/event-stream"},
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000

        if resp.status_code != 200:
            record(suite, TestResult(
                name=f"{label} HTTP状态", passed=False, dimension="D2",
                detail=f"status={resp.status_code}, body={resp.text[:300]}",
                duration_ms=elapsed_ms,
            ))
            return

        raw_text = resp.text
        events = _parse_sse_events(raw_text)
        event_types = [e["event"] for e in events]

        # D1: 响应时间
        time_threshold = quality_checks.get("time_threshold_ms", 60000)
        time_ok = elapsed_ms < time_threshold
        record(suite, TestResult(
            name=f"{label} 响应时间",
            passed=time_ok,
            dimension="D1",
            detail=f"{elapsed_ms:.0f}ms (阈值<{time_threshold}ms)",
            duration_ms=elapsed_ms,
        ))

        # D2: 正确性 - 输出结构
        has_done = "done" in event_types
        has_error = "error" in event_types
        structure_ok = has_done and not has_error
        record(suite, TestResult(
            name=f"{label} 输出结构",
            passed=structure_ok,
            dimension="D2",
            detail=f"done={has_done}, error={has_error}, 事件数={len(events)}",
        ))

        # D3: SSE 事件序列
        missing = [e for e in expected_events if e not in event_types]
        seq_ok = len(missing) == 0
        record(suite, TestResult(
            name=f"{label} SSE事件序列",
            passed=seq_ok,
            dimension="D3",
            detail=f"期望{expected_events}, 实际{event_types}" + (f", 缺少{missing}" if missing else ""),
        ))

        # D4: 错误处理 - 测试无效 serviceType
        t_err = time.perf_counter()
        try:
            err_resp = await client.post(
                f"{PYTHON_BASE}/internal/smart-engine/stream",
                json={**request_body, "serviceType": "INVALID_TYPE_XYZ"},
                headers={"Accept": "text/event-stream"},
            )
            err_elapsed = (time.perf_counter() - t_err) * 1000
            is_400 = err_resp.status_code == 400
            record(suite, TestResult(
                name=f"{label} 错误处理",
                passed=is_400,
                dimension="D4",
                detail=f"无效serviceType返回{err_resp.status_code}",
                duration_ms=err_elapsed,
            ))
        except Exception as e:
            err_elapsed = (time.perf_counter() - t_err) * 1000
            record(suite, TestResult(
                name=f"{label} 错误处理",
                passed=False,
                dimension="D4",
                detail=f"{type(e).__name__}: {e}",
                duration_ms=err_elapsed,
            ))

        # D5: 输出质量
        quality_passed = True
        quality_detail_parts = []

        # 检查是否有 progress 事件
        if quality_checks.get("need_progress"):
            has_progress = "progress" in event_types
            quality_detail_parts.append(f"progress={has_progress}")
            if not has_progress:
                quality_passed = False

        # 检查特定事件的 payload 内容
        for evt_type, checks in quality_checks.get("event_checks", {}).items():
            matching = [e for e in events if e["event"] == evt_type]
            if not matching:
                quality_detail_parts.append(f"{evt_type}=缺失")
                quality_passed = False
                continue
            payload = matching[-1].get("payload", {})
            for key, validator in checks.items():
                val = payload.get(key)
                if callable(validator):
                    ok = validator(val)
                else:
                    ok = val is not None
                quality_detail_parts.append(f"{evt_type}.{key}={'ok' if ok else 'fail'}")
                if not ok:
                    quality_passed = False

        # 检查回答文本长度
        min_text_len = quality_checks.get("min_text_len", 0)
        if min_text_len > 0:
            result_chunks = [e for e in events if e["event"] == "result_chunk"]
            if result_chunks:
                text = result_chunks[-1].get("payload", {}).get("text", "")
                text_ok = len(text) >= min_text_len
                quality_detail_parts.append(f"文本长度={len(text)}(>={min_text_len})")
                if not text_ok:
                    quality_passed = False
            else:
                quality_detail_parts.append("无result_chunk")
                quality_passed = False

        record(suite, TestResult(
            name=f"{label} 输出质量",
            passed=quality_passed,
            dimension="D5",
            detail=", ".join(quality_detail_parts) if quality_detail_parts else "通过",
        ))

    except Exception as e:
        elapsed_ms = (time.perf_counter() - t0) * 1000
        record(suite, TestResult(
            name=f"{label} 异常", passed=False, dimension="D4",
            detail=f"{type(e).__name__}: {e}",
            duration_ms=elapsed_ms,
        ))


async def part2_agent_tests(client: httpx.AsyncClient):
    print("\n" + "=" * 70)
    print("Part 2: Python Agent 功能测试 (6 种 serviceType × 5 维度)")
    print("=" * 70)

    # ── TUTORING ──
    suite = AgentTestSuite("TUTORING")
    ALL_SUITES.append(suite)
    print("\n  [2.1] TUTORING (辅导)")
    await _test_agent(
        suite, client,
        service_type="TUTORING",
        params={
            "query": "什么是死锁？如何避免？",
            "messages": [{"role": "user", "content": "什么是死锁？如何避免？"}],
            "learningContext": {"course": "操作系统", "chapter": "进程同步"},
        },
        expected_events=["result_chunk", "done"],
        quality_checks={
            "time_threshold_ms": 180000,
            "min_text_len": 50,
            "need_progress": True,
        },
        label="TUTORING",
    )

    # ── RESOURCE_GENERATION ──
    suite = AgentTestSuite("RESOURCE_GENERATION")
    ALL_SUITES.append(suite)
    print("\n  [2.2] RESOURCE_GENERATION (资源生成)")
    await _test_agent(
        suite, client,
        service_type="RESOURCE_GENERATION",
        params={
            "query": "数据库索引",
            "resourceType": "DOCUMENT",
            "learningContext": {"course": "数据库原理"},
        },
        expected_events=["progress", "done"],
        quality_checks={
            "time_threshold_ms": 180000,
            "need_progress": True,
            "event_checks": {
                "progress": {
                    "stage": lambda v: v is not None,
                    "percent": lambda v: v is not None,
                },
            },
        },
        label="RESOURCE_GENERATION",
    )

    # ── PRACTICE_JUDGE ──
    suite = AgentTestSuite("PRACTICE_JUDGE")
    ALL_SUITES.append(suite)
    print("\n  [2.3] PRACTICE_JUDGE (练习判题)")
    await _test_agent(
        suite, client,
        service_type="PRACTICE_JUDGE",
        params={
            "query": "死锁",
            "topic": "死锁",
            "difficulty": "MIXED",
            "count": 3,
            "answers": {"q1": "C", "q2": "A", "q3": "需要先判断条件是否满足"},
            "learningContext": {"course": "操作系统", "chapter": "进程同步"},
        },
        expected_events=["question_batch", "judge_result", "done"],
        quality_checks={
            "time_threshold_ms": 240000,
            "event_checks": {
                "question_batch": {
                    "questions": lambda v: isinstance(v, list) and len(v) > 0,
                },
                "judge_result": {
                    "items": lambda v: isinstance(v, list) and len(v) > 0,
                },
            },
        },
        label="PRACTICE_JUDGE",
    )

    # ── PATH_PLANNING ──
    suite = AgentTestSuite("PATH_PLANNING")
    ALL_SUITES.append(suite)
    print("\n  [2.4] PATH_PLANNING (路径规划)")
    await _test_agent(
        suite, client,
        service_type="PATH_PLANNING",
        params={
            "profile": {
                "studentLevel": "BASIC",
                "learningGoal": "掌握操作系统核心概念",
                "weakPoints": ["死锁", "进程同步"],
            },
            "learningContext": {"course": "操作系统"},
        },
        expected_events=["done"],
        quality_checks={
            "time_threshold_ms": 180000,
        },
        label="PATH_PLANNING",
    )

    # ── EVALUATION ──
    suite = AgentTestSuite("EVALUATION")
    ALL_SUITES.append(suite)
    print("\n  [2.5] EVALUATION (评估)")
    await _test_agent(
        suite, client,
        service_type="EVALUATION",
        params={
            "profile": {"studentLevel": "BASIC"},
            "learningContext": {"course": "操作系统"},
        },
        expected_events=["done"],
        quality_checks={
            "time_threshold_ms": 180000,
        },
        label="EVALUATION",
    )

    # ── PROFILE_BUILD ──
    suite = AgentTestSuite("PROFILE_BUILD")
    ALL_SUITES.append(suite)
    print("\n  [2.6] PROFILE_BUILD (画像构建)")
    await _test_agent(
        suite, client,
        service_type="PROFILE_BUILD",
        params={
            "query": "什么是死锁",
            "messages": [
                {"role": "user", "content": "我不太懂死锁，能解释一下吗？"},
            ],
            "learningContext": {"course": "操作系统"},
        },
        expected_events=["result_chunk", "done"],
        quality_checks={
            "time_threshold_ms": 180000,
        },
        label="PROFILE_BUILD",
    )


# ── Part 3: Java 全链路 (submit → SSE) ──────────────────────────────────────


async def part3_java_chain(client: httpx.AsyncClient, token: str, user_id: str):
    print("\n" + "=" * 70)
    print("Part 3: Java 全链路测试 (submit → SSE stream)")
    print("=" * 70)

    headers = {"Authorization": f"Bearer {token}"}

    # 3.1 提交任务
    print("\n  [3.1] POST /api/smart-engine/submit (TUTORING)")
    task_id = None
    trace_id = None
    t0 = time.perf_counter()
    try:
        resp = await client.post(
            f"{JAVA_BASE}/api/smart-engine/submit",
            json={
                "serviceType": "TUTORING",
                "params": {
                    "query": "什么是虚拟内存？",
                    "messages": [{"role": "user", "content": "什么是虚拟内存？"}],
                    "learningContext": {"course": "操作系统", "chapter": "内存管理"},
                },
            },
            headers=headers,
        )
        elapsed = (time.perf_counter() - t0) * 1000
        if resp.status_code == 200:
            data = resp.json()
            task_id = data.get("taskId")
            trace_id = data.get("traceId")
            record(None, TestResult(
                name="提交任务", passed=True, dimension="D2",
                detail=f"taskId={task_id}, status={data.get('status')}",
                duration_ms=elapsed,
            ))
            CHAIN_RESULTS.append(TestResult(
                name="submit TUTORING", passed=True, dimension="D2",
                detail=f"taskId={task_id}", duration_ms=elapsed,
            ))
            CHAIN_RESULTS.append(TestResult(
                name="submit 响应时间", passed=elapsed < 5000, dimension="D1",
                detail=f"{elapsed:.0f}ms", duration_ms=elapsed,
            ))
        else:
            record(None, TestResult(
                name="提交任务", passed=False, dimension="D2",
                detail=f"status={resp.status_code}, body={resp.text[:300]}",
                duration_ms=elapsed,
            ))
            CHAIN_RESULTS.append(TestResult(
                name="submit TUTORING", passed=False, dimension="D2",
                detail=f"status={resp.status_code}", duration_ms=elapsed,
            ))
            return
    except Exception as e:
        elapsed = (time.perf_counter() - t0) * 1000
        record(None, TestResult(
            name="提交任务", passed=False, dimension="D4",
            detail=f"{type(e).__name__}: {e}", duration_ms=elapsed,
        ))
        CHAIN_RESULTS.append(TestResult(
            name="submit TUTORING", passed=False, dimension="D4",
            detail=str(e), duration_ms=elapsed,
        ))
        return

    # 3.2 查询任务状态
    print("\n  [3.2] GET /api/smart-engine/tasks/{taskId}")
    await asyncio.sleep(1)  # 等待任务开始处理
    t0 = time.perf_counter()
    try:
        resp = await client.get(
            f"{JAVA_BASE}/api/smart-engine/tasks/{task_id}",
            headers=headers,
        )
        elapsed = (time.perf_counter() - t0) * 1000
        if resp.status_code == 200:
            data = resp.json()
            record(None, TestResult(
                name="查询任务状态", passed=True, dimension="D2",
                detail=f"status={data.get('status')}, stage={data.get('currentStage')}",
                duration_ms=elapsed,
            ))
            CHAIN_RESULTS.append(TestResult(
                name="task status", passed=True, dimension="D2",
                detail=f"status={data.get('status')}", duration_ms=elapsed,
            ))
        else:
            record(None, TestResult(
                name="查询任务状态", passed=False, dimension="D2",
                detail=f"status={resp.status_code}", duration_ms=elapsed,
            ))
            CHAIN_RESULTS.append(TestResult(
                name="task status", passed=False, dimension="D2",
                detail=f"status={resp.status_code}", duration_ms=elapsed,
            ))
    except Exception as e:
        elapsed = (time.perf_counter() - t0) * 1000
        CHAIN_RESULTS.append(TestResult(
            name="task status", passed=False, dimension="D4",
            detail=str(e), duration_ms=elapsed,
        ))

    # 3.3 订阅 SSE 流
    print("\n  [3.3] GET /api/smart-engine/tasks/{taskId}/stream (SSE)")
    t0 = time.perf_counter()
    try:
        async with client.stream(
            "GET",
            f"{JAVA_BASE}/api/smart-engine/tasks/{task_id}/stream",
            headers={**headers, "Accept": "text/event-stream"},
            timeout=TIMEOUT,
        ) as resp:
            elapsed = (time.perf_counter() - t0) * 1000
            if resp.status_code == 200:
                chunks = []
                async for chunk in resp.aiter_text():
                    chunks.append(chunk)
                    # 收到 done 事件后停止
                    if "event:done" in chunk or "event: error" in chunk:
                        break

                full_text = "".join(chunks)
                sse_events = _parse_sse_events(full_text)
                event_types = [e["event"] for e in sse_events]
                has_done = "done" in event_types
                has_error = "error" in event_types

                record(None, TestResult(
                    name="SSE流接收",
                    passed=has_done and not has_error,
                    dimension="D3",
                    detail=f"事件={event_types}",
                    duration_ms=elapsed,
                ))
                CHAIN_RESULTS.append(TestResult(
                    name="SSE stream", passed=has_done and not has_error, dimension="D3",
                    detail=f"事件数={len(sse_events)}", duration_ms=elapsed,
                ))
            else:
                record(None, TestResult(
                    name="SSE流接收", passed=False, dimension="D3",
                    detail=f"status={resp.status_code}",
                    duration_ms=elapsed,
                ))
                CHAIN_RESULTS.append(TestResult(
                    name="SSE stream", passed=False, dimension="D3",
                    detail=f"status={resp.status_code}", duration_ms=elapsed,
                ))
    except Exception as e:
        elapsed = (time.perf_counter() - t0) * 1000
        record(None, TestResult(
            name="SSE流接收", passed=False, dimension="D4",
            detail=f"{type(e).__name__}: {e}",
            duration_ms=elapsed,
        ))
        CHAIN_RESULTS.append(TestResult(
            name="SSE stream", passed=False, dimension="D4",
            detail=str(e), duration_ms=elapsed,
        ))

    # 3.4 未认证提交 (应返回 401)
    print("\n  [3.4] 未认证提交任务 (期望 401)")
    t0 = time.perf_counter()
    try:
        resp = await client.post(
            f"{JAVA_BASE}/api/smart-engine/submit",
            json={"serviceType": "TUTORING", "params": {}},
        )
        elapsed = (time.perf_counter() - t0) * 1000
        is_401 = resp.status_code == 401
        record(None, TestResult(
            name="未认证提交", passed=is_401, dimension="D4",
            detail=f"status={resp.status_code}",
            duration_ms=elapsed,
        ))
        CHAIN_RESULTS.append(TestResult(
            name="未认证submit", passed=is_401, dimension="D4",
            detail=f"status={resp.status_code}", duration_ms=elapsed,
        ))
    except Exception as e:
        elapsed = (time.perf_counter() - t0) * 1000
        CHAIN_RESULTS.append(TestResult(
            name="未认证submit", passed=False, dimension="D4",
            detail=str(e), duration_ms=elapsed,
        ))


# ── Part 4: 报告生成 ─────────────────────────────────────────────────────────


def generate_report():
    print("\n" + "=" * 70)
    print("Part 4: 生成测试报告")
    print("=" * 70)

    report_path = Path(__file__).parent / "full_chain_test_report.md"

    # 汇总统计
    all_results = AUTH_RESULTS + CHAIN_RESULTS
    for suite in ALL_SUITES:
        all_results.extend(suite.results)

    total = len(all_results)
    passed = sum(1 for r in all_results if r.passed)
    failed = total - passed

    # 按维度统计
    dim_stats: dict[str, dict[str, int]] = {}
    for r in all_results:
        if r.dimension not in dim_stats:
            dim_stats[r.dimension] = {"pass": 0, "fail": 0}
        if r.passed:
            dim_stats[r.dimension]["pass"] += 1
        else:
            dim_stats[r.dimension]["fail"] += 1

    dim_names = {
        "D1": "响应时间",
        "D2": "正确性",
        "D3": "SSE事件序列",
        "D4": "错误处理",
        "D5": "输出质量",
    }

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# 智学系统全链路测试报告 V2\n\n")
        f.write(f"**测试时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # 汇总表
        f.write("## 1. 测试结果汇总\n\n")
        f.write("| 指标 | 值 |\n|------|----|\n")
        f.write(f"| 总测试数 | {total} |\n")
        f.write(f"| 通过 | {passed} |\n")
        f.write(f"| 失败 | {failed} |\n")
        f.write(f"| 通过率 | {passed/total*100:.1f}% |\n\n")

        # 五维度统计
        f.write("## 2. 五维度测试统计\n\n")
        f.write("| 维度 | 通过 | 失败 | 通过率 |\n")
        f.write("|------|------|------|--------|\n")
        for dim, label in dim_names.items():
            stats = dim_stats.get(dim, {"pass": 0, "fail": 0})
            dim_total = stats["pass"] + stats["fail"]
            rate = stats["pass"] / dim_total * 100 if dim_total > 0 else 0
            f.write(f"| {dim} - {label} | {stats['pass']} | {stats['fail']} | {rate:.0f}% |\n")
        f.write("\n")

        # Part 1 详情
        f.write("## 3. Part 1: Java 认证链路测试\n\n")
        f.write("| 测试项 | 维度 | 结果 | 耗时 | 详情 |\n")
        f.write("|--------|------|------|------|------|\n")
        for r in AUTH_RESULTS:
            tag = "PASS" if r.passed else "FAIL"
            f.write(f"| {r.name} | {r.dimension} | {tag} | {r.duration_ms:.0f}ms | {r.detail} |\n")
        f.write("\n")

        # Part 2 详情
        f.write("## 4. Part 2: Python Agent 功能测试\n\n")
        for suite in ALL_SUITES:
            f.write(f"### {suite.service_type}\n\n")
            f.write(f"通过: {suite.passed}, 失败: {suite.failed}\n\n")
            f.write("| 测试项 | 维度 | 结果 | 耗时 | 详情 |\n")
            f.write("|--------|------|------|------|------|\n")
            for r in suite.results:
                tag = "PASS" if r.passed else "FAIL"
                f.write(f"| {r.name} | {r.dimension} | {tag} | {r.duration_ms:.0f}ms | {r.detail} |\n")
            f.write("\n")

        # Part 3 详情
        f.write("## 5. Part 3: Java 全链路测试\n\n")
        f.write("| 测试项 | 维度 | 结果 | 耗时 | 详情 |\n")
        f.write("|--------|------|------|------|------|\n")
        for r in CHAIN_RESULTS:
            tag = "PASS" if r.passed else "FAIL"
            f.write(f"| {r.name} | {r.dimension} | {tag} | {r.duration_ms:.0f}ms | {r.detail} |\n")
        f.write("\n")

        # 响应时间汇总
        f.write("## 6. 响应时间汇总\n\n")
        f.write("| 操作 | 耗时(ms) |\n|------|----------|\n")
        for r in all_results:
            if r.duration_ms > 0:
                f.write(f"| {r.name} | {r.duration_ms:.0f} |\n")
        f.write("\n")

    print(f"  报告已写入: {report_path}")
    return report_path


# ── Main ─────────────────────────────────────────────────────────────────────


async def main():
    print("=" * 70)
    print("智学系统全链路测试 V2")
    print(f"Java: {JAVA_BASE}  Python: {PYTHON_BASE}")
    print("=" * 70)

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # 检查服务可用性
        print("\n  检查服务可用性...")
        java_ok = False
        python_ok = False

        try:
            resp = await client.get(f"{JAVA_BASE}/actuator/health", timeout=5.0)
            java_ok = resp.status_code == 200
            print(f"    Java  ({JAVA_BASE}): {'OK' if java_ok else f'FAIL ({resp.status_code})'}")
        except Exception as e:
            print(f"    Java  ({JAVA_BASE}): FAIL ({type(e).__name__})")

        try:
            resp = await client.get(f"{PYTHON_BASE}/health", timeout=5.0)
            python_ok = resp.status_code == 200
            print(f"    Python ({PYTHON_BASE}): {'OK' if python_ok else f'FAIL ({resp.status_code})'}")
        except Exception as e:
            print(f"    Python ({PYTHON_BASE}): FAIL ({type(e).__name__})")

        if not java_ok and not python_ok:
            print("\n  两个服务均不可用，请先启动服务。")
            print("  Java:  cd project && ./mvnw spring-boot:run")
            print("  Python: cd python-agent && python -m uvicorn server:app --port 8000")
            return

        # Part 1
        auth_result = None
        if java_ok:
            auth_result = await part1_auth_chain(client)
        else:
            print("\n  [SKIP] Java 服务不可用，跳过 Part 1")

        # Part 2
        if python_ok:
            await part2_agent_tests(client)
        else:
            print("\n  [SKIP] Python 服务不可用，跳过 Part 2")

        # Part 3
        if java_ok and auth_result:
            token, user_id = auth_result
            await part3_java_chain(client, token, user_id)
        else:
            print("\n  [SKIP] Java 服务不可用或未登录，跳过 Part 3")

    # Part 4
    report_path = generate_report()

    # 打印汇总
    all_results = AUTH_RESULTS + CHAIN_RESULTS
    for suite in ALL_SUITES:
        all_results.extend(suite.results)
    total = len(all_results)
    passed = sum(1 for r in all_results if r.passed)

    print(f"\n{'='*70}")
    print(f"测试完成: {passed}/{total} 通过 ({passed/total*100:.1f}%)")
    print(f"报告: {report_path}")
    print(f"{'='*70}")


if __name__ == "__main__":
    asyncio.run(main())
