// Standalone Chrome CDP driver; native Node WebSocket/fetch, no packages.
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';

const root = dirname(fileURLToPath(import.meta.url));
const [profile, url, phase = 'green', outputDirectory = 'evidence'] = process.argv.slice(2);
if (!profile || !url || !['red', 'green'].includes(phase)) {
  throw new Error('Usage: node browser-check.mjs <fresh-Chrome-profile> <local-demo-URL> [red|green] [output-directory]');
}
const port = (await readFile(join(profile, 'DevToolsActivePort'), 'utf8')).split('\n')[0];
const targets = await fetch(`http://127.0.0.1:${port}/json/list`).then(response => response.json());
const target = targets.find(item => item.type === 'page');
if (!target) throw new Error('No page in the explicitly provided standalone Chrome profile');
const socket = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {
  socket.addEventListener('open', resolve, { once: true });
  socket.addEventListener('error', reject, { once: true });
});
let sequence = 0;
const pending = new Map();
const browserErrors = [];
socket.addEventListener('message', event => {
  const message = JSON.parse(event.data);
  if (message.method === 'Runtime.exceptionThrown') browserErrors.push(message.params.exceptionDetails.text);
  const waiter = pending.get(message.id);
  if (!waiter) return;
  pending.delete(message.id);
  message.error ? waiter.reject(new Error(JSON.stringify(message.error))) : waiter.resolve(message.result);
});
function call(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++sequence;
    const timeout = setTimeout(() => { pending.delete(id); reject(new Error(`CDP timeout: ${method}`)); }, 10000);
    pending.set(id, { resolve: value => { clearTimeout(timeout); resolve(value); }, reject: error => { clearTimeout(timeout); reject(error); } });
    socket.send(JSON.stringify({ id, method, params }));
  });
}
async function evaluate(expression) {
  const result = await call('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
  return result.result.value;
}
async function clickByName(name) {
  const point = await evaluate(`(() => {
    const button = [...document.querySelectorAll('button')].find(element => (element.getAttribute('aria-label') || element.textContent.trim()) === ${JSON.stringify(name)});
    if (!button) throw new Error('Visible button not found: ' + ${JSON.stringify(name)});
    const rectangle = button.getBoundingClientRect();
    return { x: rectangle.x + rectangle.width / 2, y: rectangle.y + rectangle.height / 2 };
  })()`);
  await call('Input.dispatchMouseEvent', { type: 'mousePressed', button: 'left', clickCount: 1, ...point });
  await call('Input.dispatchMouseEvent', { type: 'mouseReleased', button: 'left', clickCount: 1, ...point });
  await evaluate('new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))');
}
async function visibleState() {
  return evaluate(`({
    title: document.querySelector('h2').textContent,
    count: document.querySelector('[role="status"]').textContent,
    tasks: [...document.querySelectorAll('button[aria-label$="상세 보기"]')].filter(button => button.getClientRects().length).map(button => button.getAttribute('aria-label')),
    selectedView: document.querySelector('[role="tab"][aria-selected="true"]').textContent.trim(),
    selectedFilter: document.querySelector('[aria-pressed="true"]').textContent.trim(),
    dialogVisible: document.querySelector('dialog').open,
    dialogTitle: document.querySelector('dialog h2').textContent
  })`);
}
const evidence = join(root, outputDirectory);
const observations = [];
let browserVersion;
let failure;
async function record(step, screenshot = false) {
  const state = await visibleState();
  observations.push({ step, ...state });
  console.log(JSON.stringify({ step, ...state }));
  if (screenshot) {
    const result = await call('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
    await writeFile(join(evidence, `${step}.png`), Buffer.from(result.data, 'base64'));
    const accessibility = await call('Accessibility.getFullAXTree');
    await writeFile(join(evidence, `${step}.ax.json`), JSON.stringify(accessibility, null, 2) + '\n');
  }
  return state;
}
try {
  await mkdir(evidence, { recursive: true });
  browserVersion = await call('Browser.getVersion');
  await call('Page.enable');
  await call('Runtime.enable');
  await call('Network.enable');
  await call('Network.setCacheDisabled', { cacheDisabled: true });
  await call('Emulation.setDeviceMetricsOverride', { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
  await call('Page.navigate', { url });
  for (let attempt = 0; attempt < 40; attempt++) {
    if (await evaluate('document.readyState === "complete" && !!document.querySelector("[role=status]")')) break;
    await new Promise(resolve => setTimeout(resolve, 50));
  }
  await evaluate('document.fonts.ready.then(() => new Promise(resolve => requestAnimationFrame(resolve)))');
  if (phase === 'red') {
    await record('red-before-filter');
    await clickByName('검토 필요 2');
    const state = await record('red-after-filter');
    assert.equal(state.count, '2개 작업 표시', 'Review filter must show two matching tasks');
  } else {
    const expectedReviewTasks = ['랜딩 페이지 문구 검토 상세 보기', '주간 리포트 확인 상세 보기'];
    const variants = [
      ['a-list', 'A · 목록한 줄에서 나란히'],
      ['b-cards', 'B · 카드하나씩 둘러보기'],
      ['c-board', 'C · 상태 보드상태별로 모아 보기']
    ];
    for (const [prefix, tabName] of variants) {
      await clickByName(tabName);
      await clickByName('전체 5');
      const all = await record(`${prefix}-all`, true);
      assert.equal(all.count, '5개 작업 표시');
      assert.equal(all.tasks.length, 5);
      await clickByName('검토 필요 2');
      const filtered = await record(`${prefix}-review`, true);
      assert.equal(filtered.count, '2개 작업 표시');
      assert.deepEqual(filtered.tasks, expectedReviewTasks);
      await clickByName('랜딩 페이지 문구 검토 상세 보기');
      const detail = await record(`${prefix}-detail`, true);
      assert.equal(detail.dialogVisible, true);
      assert.equal(detail.dialogTitle, '랜딩 페이지 문구 검토');
      await clickByName('닫기');
      const closed = await record(`${prefix}-closed`);
      assert.equal(closed.dialogVisible, false);
      assert.equal(closed.count, '2개 작업 표시');
    }
    assert.deepEqual(browserErrors, [], 'No JavaScript runtime exceptions during exercised behavior');
    console.log('PASS: 3 views, 5→2 task filtering, correct detail open/close; no observed JS exceptions.');
  }
} catch (error) {
  failure = error.stack;
  console.error(`${phase.toUpperCase()} RESULT: ${error.stack}`);
  process.exitCode = 1;
} finally {
  await writeFile(join(evidence, `${phase}-observations.json`), JSON.stringify({ browser: 'standalone Google Chrome via native Node CDP', viewport: { width: 1280, height: 900, deviceScaleFactor: 1 }, phase, url, browserVersion, observations, browserErrors, failure }, null, 2) + '\n');
  socket.close();
}
