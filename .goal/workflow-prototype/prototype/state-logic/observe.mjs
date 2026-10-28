// A small observation script: real Chrome inputs, rendered DOM output, no dependencies.
import { spawn } from 'node:child_process';
import { mkdtemp, readFile, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const firstSeatOnly = process.argv.includes('--first-seat-only');
const capturePrefix = process.argv.find(arg => arg.startsWith('--capture-prefix='))?.split('=')[1] || new Date().toISOString().replaceAll(/[^0-9A-Za-z]/g, '-');
const profile = await mkdtemp('/private/tmp/workflow-prototype-state-logic-');
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [
  '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  '--remote-debugging-port=0', `--user-data-dir=${profile}`, 'about:blank',
], { stdio: ['ignore', 'ignore', 'pipe'] });
let chromeError = '';
chrome.stderr.on('data', chunk => { chromeError += chunk.toString(); });
let socket;
let requestId = 0;
const waiting = new Map();
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const output = (label, data) => console.log(`${label} ${JSON.stringify(data)}`);

try {
  const activePortPath = path.join(profile, 'DevToolsActivePort');
  for (let tries = 0; !existsSync(activePortPath); tries++) {
    if (tries > 150 || chrome.exitCode !== null) throw new Error(`Chrome did not start: ${chromeError}`);
    await sleep(100);
  }
  const port = (await readFile(activePortPath, 'utf8')).split('\n')[0];
  const target = await (await fetch(`http://127.0.0.1:${port}/json/new?${encodeURIComponent(pathToFileURL(path.join(here, 'index.html')).href)}`, { method: 'PUT' })).json();
  socket = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => { socket.addEventListener('open', resolve, { once: true }); socket.addEventListener('error', reject, { once: true }); });
  socket.addEventListener('message', event => {
    const message = JSON.parse(event.data);
    if (!message.id) return;
    const pending = waiting.get(message.id);
    if (!pending) return;
    waiting.delete(message.id);
    clearTimeout(pending.timeout);
    message.error ? pending.reject(new Error(JSON.stringify(message.error))) : pending.resolve(message.result);
  });
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++requestId;
    const timeout = setTimeout(() => { waiting.delete(id); reject(new Error(`CDP timeout: ${method}`)); }, 10000);
    waiting.set(id, { resolve, reject, timeout });
    socket.send(JSON.stringify({ id, method, params }));
  });
  const evaluate = async expression => {
    const response = await send('Runtime.evaluate', { expression, returnByValue: true });
    if (response.exceptionDetails) throw new Error(JSON.stringify(response.exceptionDetails));
    return response.result.value;
  };
  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 1024, deviceScaleFactor: 1, mobile: false });
  for (let tries = 0; await evaluate('document.readyState') !== 'complete'; tries++) {
    if (tries > 100) throw new Error('Document did not load');
    await sleep(50);
  }
  output('BROWSER', await send('Browser.getVersion'));
  output('SOURCE', { url: target.url, profile, interface: 'Mouse input on visible participant radios and buttons; rendered list/status observations.' });

  const click = async selector => {
    const rect = await evaluate(`(() => { const r = document.querySelector(${JSON.stringify(selector)}).getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + r.height / 2 }; })()`);
    await send('Input.dispatchMouseEvent', { type: 'mousePressed', ...rect, button: 'left', clickCount: 1 });
    await send('Input.dispatchMouseEvent', { type: 'mouseReleased', ...rect, button: 'left', clickCount: 1 });
  };
  const select = async person => {
    await click(`label[for="person-${person}"]`);
    const actual = await evaluate('document.querySelector("input[name=participant]:checked").value');
    if (actual !== person) throw new Error(`Input selection missed: expected ${person}, got ${actual}`);
  };
  const state = () => evaluate(`({
    confirmed: [...document.querySelectorAll('#confirmed li:not(.empty)')].map(item => item.textContent),
    waitlist: [...document.querySelectorAll('#waitlist li:not(.empty)')].map(item => item.textContent),
    confirmedCount: document.querySelector('#confirmed-count').textContent,
    waitlistCount: document.querySelector('#waitlist-count').textContent,
    notice: document.querySelector('#notice').textContent,
    history: [...document.querySelectorAll('#history li')].map(item => item.textContent)
  })`);
  let step = 0;
  const check = async (action, confirmed, waitlist, notice) => {
    const observed = await state();
    output(`STEP ${step++}`, { action, ...observed });
    if (JSON.stringify(observed.confirmed) !== JSON.stringify(confirmed) || JSON.stringify(observed.waitlist) !== JSON.stringify(waitlist)) {
      throw new Error(`STATE MISMATCH after ${action}. Expected confirmed ${JSON.stringify(confirmed)}, waitlist ${JSON.stringify(waitlist)}.`);
    }
    if (observed.confirmedCount !== `${confirmed.length} / 2 seats` || observed.waitlistCount !== `${waitlist.length} people`) throw new Error(`COUNT MISMATCH after ${action}`);
    if (notice && observed.notice !== notice) throw new Error(`NOTICE MISMATCH after ${action}: expected ${notice}`);
  };
  const reserve = async person => { await select(person); await click('#reserve'); };
  const cancel = async person => { await select(person); await click('#cancel'); };
  const screenshot = async filename => {
    const capture = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
    await writeFile(path.join(here, 'evidence', `${capturePrefix}-${filename}`), Buffer.from(capture.data, 'base64'));
    output('SCREENSHOT', { filename: `${capturePrefix}-${filename}` });
  };

  await check('Initial screen', [], []);
  await reserve('Ada');
  await check('Reserve Ada', ['Ada'], [], 'Ada has a confirmed seat.');
  if (!firstSeatOnly) {
    await reserve('Bo');
    await check('Reserve Bo', ['Ada', 'Bo'], []);
    await reserve('Cy');
    await check('Reserve Cy at capacity', ['Ada', 'Bo'], ['Cy']);
    await reserve('Dana');
    await check('Reserve Dana at capacity', ['Ada', 'Bo'], ['Cy', 'Dana']);
    await screenshot('01-full-with-waitlist.png');
    await reserve('Cy');
    await check('Reserve Cy again', ['Ada', 'Bo'], ['Cy', 'Dana'], 'Cy is already on the waitlist.');
    await cancel('Cy');
    await check('Cancel waiting Cy', ['Ada', 'Bo'], ['Dana'], 'Cy left the waitlist.');
    await reserve('Cy');
    await check('Cy rejoins at the end', ['Ada', 'Bo'], ['Dana', 'Cy']);
    await cancel('Ada');
    await check('Cancel confirmed Ada', ['Bo', 'Dana'], ['Cy'], 'Ada cancelled. Dana was promoted from the waitlist.');
    await screenshot('02-first-promotion.png');
    await cancel('Bo');
    await check('Cancel confirmed Bo', ['Dana', 'Cy'], [], 'Bo cancelled. Cy was promoted from the waitlist.');
    await cancel('Ada');
    await check('Cancel absent Ada', ['Dana', 'Cy'], [], 'Ada has no participation to cancel.');
    await screenshot('03-second-promotion-and-noop.png');
    await click('#reset');
    await check('Reset experiment', [], [], 'Ready. No reservations yet.');
    await screenshot('04-reset.png');
  }
  output('PASS', { observations: step, mode: firstSeatOnly ? 'first-seat-only' : 'full public-control scenario' });
} catch (error) {
  console.error(`FAIL ${error.message}`);
  process.exitCode = 1;
} finally {
  socket?.close();
  chrome.kill('SIGTERM');
}
