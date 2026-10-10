// Start tests/browser_demo_server.py, then run this file with Playwright MCP's
// browser_run_code tool (filename). Uses synthetic responses, not live APIs.
async (page) => {
  const check = (value, message) => { if (!value) throw new Error(message); };
  await page.setViewportSize({width: 1440, height: 900});
  await page.goto("http://127.0.0.1:8765");
  await page.waitForFunction(() => document.getElementById("connection").textContent.includes("연결됨"));
  check(await page.locator(".scenario-button").count() === 6, "Recommended list must show six scenarios");
  check(await page.locator("#scenario-count").innerText() === "6 / 16", "Catalog count is wrong");
  for (const [category, id, title] of [
    ["analysis", 3, "저장소 구조 개선"],
    ["operations", 15, "운영 배포와 권한 변경"],
    ["recommended", 6, "회의록에서 할 일 추출"],
  ]) {
    await page.selectOption("#scenario-category", category);
    await page.locator(`[data-scenario-id="${id}"]`).click();
    const active = page.locator('.scenario-button[aria-pressed="true"]');
    check(await active.count() === 1, "Exactly one visible scenario must be selected");
    check(await active.getAttribute("data-scenario-id") === String(id), "Selection used filtered position instead of original ID");
    check(await page.locator("#scenario-title").innerText() === title, "Request and list selection disagree");
  }
  await page.selectOption("#scenario-category", "all");
  check(await page.locator(".scenario-button").count() === 16, "All scenarios must be reachable");
  await page.locator("#scenario-search").fill("고객");
  check(await page.locator(".scenario-button").count() === 1, "Search must narrow the list");
  await page.locator('[data-scenario-id="7"]').click();
  check(await page.locator(".scenario-button.selected").getAttribute("data-scenario-id") === "7", "Search selection marker is wrong");
  const original = await page.evaluate(() => new Promise((resolve, reject) => {
    const socket = new WebSocket(`ws://${location.host}/ws`);
    socket.onmessage = event => { const initial = JSON.parse(event.data); socket.close(); resolve(initial.scenarios[7].request); };
    socket.onerror = () => { socket.close(); reject(new Error("Unable to read fixture catalog")); };
  }));
  await page.locator(".request-details summary").click();
  check(await page.locator("#request-preview").textContent() === original, "Long request was abbreviated or changed");
  await page.locator(".request-details summary").click();
  await page.locator("#scenario-search").fill("notfound-scenario");
  check(await page.locator("#scenario-empty").isVisible(), "Empty search must be explained");
  check(await page.locator("#scenario-title").innerText() === "고객 안내 메일 초안", "Filtering must not replace the active request");
  await page.locator("#scenario-search").fill("");
  for (const width of [1000, 800, 560, 390, 320]) {
    await page.setViewportSize({width, height: 850});
    if (width <= 800) {
      await page.locator("#scenario-browser").waitFor({state: "hidden"});
      await page.locator("#scenario-toggle").click();
      await page.locator('[data-scenario-id="6"]').click();
      await page.locator("#scenario-browser").waitFor({state: "hidden"});
    }
    check(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `Horizontal overflow at ${width}px`);
  }
  return {recommended: 6, total: 16, originalIdSelection: true, search: true, fullRequest: true, mobileCollapse: true};
}
