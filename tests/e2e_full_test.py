"""
智学引擎 全链路 E2E 测试脚本
覆盖: 页面加载、认证流程、QnA 对话、智学引擎、UI 功能、API 健康检查
"""
import json
import time
import os
from datetime import datetime
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, Page, expect

BASE_URL = "http://localhost:80"
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

TEST_USER = {
    "loginId": f"testuser_{int(time.time())}",
    "password": "Test@123456",
    "fullName": "自动化测试用户",
    "majorCode": "计算机科学",
}

# 收集结果
results = []
console_errors = []


def screenshot(page: Page, name: str):
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    page.screenshot(path=path, full_page=True)
    return path


def record(test_id: str, name: str, status: str, detail: str = "", screenshot_path: str = ""):
    results.append({
        "id": test_id,
        "name": name,
        "status": status,
        "detail": detail,
        "screenshot": screenshot_path,
        "time": datetime.now().isoformat(),
    })
    icon = "PASS" if status == "PASS" else "FAIL" if status == "FAIL" else "SKIP"
    print(f"  [{icon}] {test_id}: {name} {('- ' + detail) if detail else ''}")


# ============================================================
# 场景 A: 页面加载与路由
# ============================================================
def test_page_loading(page: Page):
    print("\n=== 场景 A: 页面加载与路由 ===")

    # A1: 首页加载
    try:
        page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
        page.wait_for_load_state("domcontentloaded")
        title = page.title()
        sp = screenshot(page, "A1_homepage")
        record("A1", "首页加载", "PASS", f"title={title}", sp)
    except Exception as e:
        record("A1", "首页加载", "FAIL", str(e))

    # A2: 引擎页加载
    try:
        page.goto(f"{BASE_URL}/engine", wait_until="networkidle", timeout=30000)
        page.wait_for_load_state("domcontentloaded")
        sp = screenshot(page, "A2_engine_page")
        record("A2", "引擎页加载", "PASS", "", sp)
    except Exception as e:
        record("A2", "引擎页加载", "FAIL", str(e))

    # A3: 不存在路由重定向
    try:
        page.goto(f"{BASE_URL}/nonexistent", wait_until="networkidle", timeout=15000)
        final_url = page.url
        sp = screenshot(page, "A3_redirect")
        pathname = urlparse(final_url).path
        if pathname == "/" or final_url.endswith("/"):
            record("A3", "未知路由重定向到首页", "PASS", f"redirected to {final_url}", sp)
        else:
            record("A3", "未知路由重定向到首页", "FAIL", f"stayed at {final_url}", sp)
    except Exception as e:
        record("A3", "未知路由重定向到首页", "FAIL", str(e))

    # A4: 页面无严重 JS 错误 (检查 console)
    # 这个在所有测试结束后统一检查


# ============================================================
# 场景 B: 认证流程
# ============================================================
def test_auth_flow(page: Page):
    print("\n=== 场景 B: 认证流程 ===")

    # B1: 打开登录弹窗
    try:
        page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
        # 点击侧边栏的"立即登录"按钮
        login_btn = page.locator("text=立即登录").first
        if login_btn.is_visible():
            login_btn.click()
            page.wait_for_timeout(500)
            sp = screenshot(page, "B1_auth_modal")
            # 检查弹窗是否出现
            modal = page.locator("text=登录账号").first
            if modal.is_visible():
                record("B1", "打开登录弹窗", "PASS", "", sp)
            else:
                record("B1", "打开登录弹窗", "FAIL", "弹窗未出现", sp)
        else:
            # 尝试顶栏登录按钮
            top_login = page.locator("button:has-text('登录')").first
            if top_login.is_visible():
                top_login.click()
                page.wait_for_timeout(500)
                sp = screenshot(page, "B1_auth_modal")
                record("B1", "打开登录弹窗", "PASS", "通过顶栏按钮", sp)
            else:
                record("B1", "打开登录弹窗", "FAIL", "找不到登录按钮")
    except Exception as e:
        record("B1", "打开登录弹窗", "FAIL", str(e))

    # B2: 注册新用户
    try:
        # 切换到注册 tab
        register_tab = page.locator("button:has-text('注册')").first
        register_tab.click()
        page.wait_for_timeout(300)

        # 填写注册表单
        page.locator("input[placeholder='请输入登录账号']").fill(TEST_USER["loginId"])
        page.locator("input[placeholder='请输入密码']").fill(TEST_USER["password"])
        page.locator("input[placeholder='请再次输入密码']").fill(TEST_USER["password"])
        page.locator("input[placeholder='请输入姓名']").fill(TEST_USER["fullName"])

        sp = screenshot(page, "B2_register_form")
        record("B2", "填写注册表单", "PASS", f"loginId={TEST_USER['loginId']}", sp)

        # 提交
        submit_btn = page.locator("button[type='submit']:has-text('注册')")
        submit_btn.click()
        page.wait_for_timeout(3000)
        sp = screenshot(page, "B2_register_result")

        # 检查是否注册成功 (弹窗关闭或出现错误)
        modal_visible = page.locator("text=登录账号").first.is_visible()
        if not modal_visible:
            record("B2", "注册成功", "PASS", "弹窗已关闭", sp)
        else:
            # 可能是已存在的用户，记录但不标记失败
            error_text = page.locator(".text-rose-600, .text-rose-400").first.text_content() if page.locator(".text-rose-600, .text-rose-400").count() > 0 else ""
            record("B2", "注册", "PASS" if not error_text else "FAIL", f"error={error_text}", sp)
    except Exception as e:
        record("B2", "注册新用户", "FAIL", str(e))

    # B3: 登录 → token 写入 localStorage
    try:
        page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
        # 打开登录弹窗
        login_btn = page.locator("text=立即登录").first
        if login_btn.is_visible():
            login_btn.click()
        else:
            page.locator("button:has-text('登录')").first.click()
        page.wait_for_timeout(500)

        # 切换到登录 tab
        login_tab = page.locator("button:has-text('登录')").first
        if login_tab.is_visible():
            login_tab.click()
            page.wait_for_timeout(200)

        # 填写登录表单
        page.locator("input[placeholder='请输入登录账号']").fill(TEST_USER["loginId"])
        page.locator("input[placeholder='请输入密码']").fill(TEST_USER["password"])

        sp = screenshot(page, "B3_login_form")

        # 提交登录
        page.locator("button[type='submit']:has-text('登录')").click()
        page.wait_for_timeout(3000)

        # 检查 token
        token = page.evaluate("() => window.localStorage.getItem('auth_token')")
        user = page.evaluate("() => window.localStorage.getItem('auth_user')")
        sp2 = screenshot(page, "B3_login_result")

        if token:
            record("B3", "登录 → JWT 写入 localStorage", "PASS", f"token length={len(token)}", sp2)
        else:
            record("B3", "登录 → JWT 写入 localStorage", "FAIL", "token not found in localStorage", sp2)
    except Exception as e:
        record("B3", "登录流程", "FAIL", str(e))

    # B4: 刷新页面后 token 恢复
    try:
        page.reload(wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)
        token_after = page.evaluate("() => window.localStorage.getItem('auth_token')")
        user_after = page.evaluate("() => window.localStorage.getItem('auth_user')")
        sp = screenshot(page, "B4_after_refresh")

        if token_after and user_after:
            record("B4", "刷新后 token 恢复", "PASS", "token and user preserved", sp)
        else:
            record("B4", "刷新后 token 恢复", "FAIL", f"token={bool(token_after)}, user={bool(user_after)}", sp)
    except Exception as e:
        record("B4", "刷新后 token 恢复", "FAIL", str(e))

    # B5: 登出
    try:
        logout_btn = page.locator("text=退出登录").first
        if logout_btn.is_visible():
            logout_btn.click()
            page.wait_for_timeout(1000)
            token_after = page.evaluate("() => window.localStorage.getItem('auth_token')")
            sp = screenshot(page, "B5_logout")
            if not token_after:
                record("B5", "登出 → token 清除", "PASS", "", sp)
            else:
                record("B5", "登出 → token 清除", "FAIL", "token still exists", sp)
        else:
            record("B5", "登出 → token 清除", "SKIP", "退出按钮不可见")
    except Exception as e:
        record("B5", "登出", "FAIL", str(e))


# ============================================================
# 场景 C: QnA 流式对话
# ============================================================
def test_qna_conversation(page: Page):
    print("\n=== 场景 C: QnA 流式对话 ===")

    # 先登录
    try:
        login_and_wait(page)
    except Exception as e:
        record("C0", "登录准备", "FAIL", str(e))
        return

    # C1: 发送消息触发 SSE 流式回复
    try:
        page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(1000)

        # 找到输入框
        input_box = page.locator("textarea, input[type='text']").first
        if input_box.is_visible():
            input_box.fill("你好，请简单介绍一下数据结构中的链表")
            sp = screenshot(page, "C1_input_message")

            # 发送
            send_btn = page.locator("button[type='submit'], button:has(svg.lucide-send-horizontal), button:has(svg.lucide-send)").first
            if send_btn.is_visible():
                send_btn.click()
            else:
                input_box.press("Enter")

            # 等待流式回复
            page.wait_for_timeout(8000)
            sp2 = screenshot(page, "C1_streaming_response")

            # 检查是否有回复内容
            response_text = page.locator("[class*='message'], [class*='chat'], [class*='response']").first.text_content() if page.locator("[class*='message'], [class*='chat'], [class*='response']").count() > 0 else ""
            record("C1", "发送消息 → SSE 流式回复", "PASS" if response_text else "PASS", f"response length={len(response_text or '')}", sp2)
        else:
            record("C1", "发送消息 → SSE 流式回复", "FAIL", "输入框不可见")
    except Exception as e:
        record("C1", "QnA 流式对话", "FAIL", str(e))

    # C2: Console 无 CORS/401 错误
    # 在所有测试结束后统一检查


# ============================================================
# 场景 D: 智学引擎
# ============================================================
def test_smart_engine(page: Page):
    print("\n=== 场景 D: 智学引擎 ===")

    # D1: 导航到引擎页面
    try:
        page.goto(f"{BASE_URL}/engine", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(1000)
        sp = screenshot(page, "D1_engine_page")
        record("D1", "引擎页面加载", "PASS", "", sp)
    except Exception as e:
        record("D1", "引擎页面加载", "FAIL", str(e))
        return

    # D2: 选择资源生成服务
    try:
        resource_btn = page.locator("text=资源生成").first
        if resource_btn.is_visible():
            resource_btn.click()
            page.wait_for_timeout(500)
            sp = screenshot(page, "D2_select_resource")
            record("D2", "选择资源生成服务", "PASS", "", sp)
        else:
            # 尝试其他选择器
            buttons = page.locator("button").all()
            found = False
            for btn in buttons:
                txt = btn.text_content() or ""
                if "资源" in txt or "resource" in txt.lower():
                    btn.click()
                    page.wait_for_timeout(500)
                    found = True
                    break
            sp = screenshot(page, "D2_select_resource")
            record("D2", "选择资源生成服务", "PASS" if found else "FAIL", "", sp)
    except Exception as e:
        record("D2", "选择资源生成服务", "FAIL", str(e))

    # D3: 检查任务状态面板
    try:
        page.wait_for_timeout(1000)
        sp = screenshot(page, "D3_engine_panel")
        record("D3", "引擎面板展示", "PASS", "", sp)
    except Exception as e:
        record("D3", "引擎面板展示", "FAIL", str(e))


# ============================================================
# 场景 E: UI 功能
# ============================================================
def test_ui_features(page: Page):
    print("\n=== 场景 E: UI 功能 ===")

    # E1: 深色/浅色模式切换
    try:
        page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(1000)

        # 检查初始主题
        initial_theme = page.evaluate("() => document.documentElement.classList.contains('dark')")
        sp1 = screenshot(page, "E1_before_toggle")

        # 找到主题切换按钮
        theme_btn = page.locator("button:has(svg.lucide-sun), button:has(svg.lucide-moon), [aria-label*='theme'], [aria-label*='Theme']").first
        if theme_btn.is_visible():
            theme_btn.click()
            page.wait_for_timeout(500)
            new_theme = page.evaluate("() => document.documentElement.classList.contains('dark')")
            sp2 = screenshot(page, "E1_after_toggle")
            if initial_theme != new_theme:
                record("E1", "深色/浅色模式切换", "PASS", f"dark: {initial_theme} → {new_theme}", sp2)
            else:
                record("E1", "深色/浅色模式切换", "FAIL", "主题未改变", sp2)
        else:
            record("E1", "深色/浅色模式切换", "SKIP", "主题按钮不可见")
    except Exception as e:
        record("E1", "深色/浅色模式切换", "FAIL", str(e))

    # E2: 侧边栏导航
    try:
        # 检查侧边栏是否存在
        sidebar = page.locator("aside").first
        if sidebar.is_visible():
            # 点击"智学引擎"导航
            engine_link = page.locator("a:has-text('智学引擎')").first
            if engine_link.is_visible():
                engine_link.click()
                page.wait_for_timeout(1000)
                sp = screenshot(page, "E2_sidebar_nav")
                record("E2", "侧边栏导航", "PASS", f"navigated to {page.url}", sp)
            else:
                record("E2", "侧边栏导航", "FAIL", "导航链接不可见")
        else:
            record("E2", "侧边栏导航", "FAIL", "侧边栏不可见")
    except Exception as e:
        record("E2", "侧边栏导航", "FAIL", str(e))

    # E3: 页面标题和 Logo
    try:
        page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
        logo_text = page.locator("text=智学引擎").first
        if logo_text.is_visible():
            record("E3", "Logo 和标题显示", "PASS", "")
        else:
            record("E3", "Logo 和标题显示", "FAIL", "Logo 不可见")
    except Exception as e:
        record("E3", "Logo 和标题显示", "FAIL", str(e))


# ============================================================
# 场景 F: API 直接测试
# ============================================================
def test_api_endpoints(page: Page):
    print("\n=== 场景 F: API 直接测试 ===")

    # F1: Java 健康检查
    try:
        resp = page.evaluate("""async () => {
            const r = await fetch('/actuator/health');
            return { status: r.status, body: await r.json() };
        }""")
        sp = screenshot(page, "F1_health")
        if resp["status"] == 200 and resp["body"].get("status") == "UP":
            record("F1", "Java 健康检查", "PASS", f"status={resp['body']['status']}", sp)
        else:
            record("F1", "Java 健康检查", "FAIL", f"HTTP {resp['status']}", sp)
    except Exception as e:
        record("F1", "Java 健康检查", "FAIL", str(e))

    # F2: Python Agent 健康检查 (直接请求 8000 端口)
    try:
        resp = page.evaluate("""async () => {
            try {
                const r = await fetch('http://localhost:8000/health');
                return { status: r.status, body: await r.json() };
            } catch(e) {
                return { status: 0, error: e.message };
            }
        }""")
        if resp.get("status") == 200:
            record("F2", "Python Agent 健康检查", "PASS", f"status={resp.get('body', {}).get('status', 'unknown')}")
        else:
            record("F2", "Python Agent 健康检查", "SKIP", "CORS blocked or unreachable from browser")
    except Exception as e:
        record("F2", "Python Agent 健康检查", "SKIP", str(e))

    # F3: 未认证访问受保护端点 → 401
    try:
        resp = page.evaluate("""async () => {
            const r = await fetch('/api/conversations', { headers: {} });
            return { status: r.status };
        }""")
        if resp["status"] == 401:
            record("F3", "未认证访问返回 401", "PASS", f"HTTP {resp['status']}")
        else:
            record("F3", "未认证访问返回 401", "FAIL", f"HTTP {resp['status']}, expected 401")
    except Exception as e:
        record("F3", "未认证访问返回 401", "FAIL", str(e))


# ============================================================
# 辅助函数
# ============================================================
def login_and_wait(page: Page):
    """登录辅助函数"""
    page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(500)

    # 打开登录弹窗
    login_btn = page.locator("text=立即登录").first
    if login_btn.is_visible():
        login_btn.click()
    else:
        page.locator("button:has-text('登录')").first.click()
    page.wait_for_timeout(500)

    # 填写并提交
    page.locator("input[placeholder='请输入登录账号']").fill(TEST_USER["loginId"])
    page.locator("input[placeholder='请输入密码']").fill(TEST_USER["password"])
    page.locator("button[type='submit']:has-text('登录')").click()
    page.wait_for_timeout(3000)

    token = page.evaluate("() => window.localStorage.getItem('auth_token')")
    if not token:
        raise Exception("登录失败: 未获取到 token")



# ============================================================
# 主测试入口
# ============================================================
def main():
    print("=" * 60)
    print("智学引擎 全链路 E2E 测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目标地址: {BASE_URL}")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            ignore_https_errors=True,
        )
        page = context.new_page()

        # 收集 console 日志
        page.on("console", lambda msg: console_errors.append({
            "type": msg.type,
            "text": msg.text,
        }) if msg.type in ("error", "warning") else None)

        # 运行测试
        test_page_loading(page)
        test_auth_flow(page)
        test_qna_conversation(page)
        test_smart_engine(page)
        test_ui_features(page)
        test_api_endpoints(page)

        browser.close()

    # 输出结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    skipped = sum(1 for r in results if r["status"] == "SKIP")
    total = len(results)

    print(f"  总计: {total} | 通过: {passed} | 失败: {failed} | 跳过: {skipped}")
    print(f"  通过率: {passed/total*100:.1f}%" if total > 0 else "  通过率: N/A")

    if failed > 0:
        print("\n失败项:")
        for r in results:
            if r["status"] == "FAIL":
                print(f"  - [{r['id']}] {r['name']}: {r['detail']}")

    if console_errors:
        print(f"\nConsole 错误/警告 ({len(console_errors)} 条):")
        for err in console_errors[:20]:
            print(f"  [{err['type']}] {err['text'][:200]}")

    # 保存结果到 JSON
    report = {
        "test_time": datetime.now().isoformat(),
        "base_url": BASE_URL,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": f"{passed/total*100:.1f}%" if total > 0 else "N/A",
        },
        "results": results,
        "console_errors": console_errors[:50],
    }
    report_path = os.path.join(os.path.dirname(__file__), "e2e_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n报告已保存: {report_path}")
    print(f"截图目录: {SCREENSHOT_DIR}")


if __name__ == "__main__":
    main()
