#!/usr/bin/env node
/**
 * 在 Sourcegraph 平台搜索使用了指定 API 的所有项目（仓库）
 * 通用 skill 脚本，可单独运行。
 *
 * 用法:
 *   node searchApi.js <api字符串> [--json|--md|--regex|--limit N]
 *
 * 默认使用内置的 Sourcegraph 地址，无需设置环境变量。
 * 仅当使用自建/私有等特殊 URL 时，通过 SOURCEGRAPH_URL 覆盖。
 * 访问令牌：优先环境变量 SOURCEGRAPH_ACCESS_TOKEN；未设置时在终端交互粘贴，
 * 留空取消；非 TTY 环境须预先 export。
 */

const readline = require('readline');

const SOURCEGRAPH_URL = (process.env.SOURCEGRAPH_URL || "https://sourcegraph.yc345.tv").replace(/\/$/, '');

/**
 * 若未通过环境变量指定 token，则交互式提示用户输入；无 token 时返回空字符串。
 * 非交互环境（如无 TTY）不阻塞，直接返回空并已在 stderr 打印说明。
 */
function promptForToken(baseUrl) {
  if (!process.stdin.isTTY || !process.stdout.isTTY) {
    console.error(`
当前无法交互输入令牌（未检测到终端）。
请在本机执行其一：
  export SOURCEGRAPH_ACCESS_TOKEN='你的令牌'
  node scripts/searchApi.js "<搜索词>" ...

或一次性：
  SOURCEGRAPH_ACCESS_TOKEN='你的令牌' node scripts/searchApi.js "<搜索词>"
`.trim());
    return Promise.resolve('');
  }

  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  console.log(`
┌─ Sourcegraph 访问令牌 ─────────────────────────────────────────
│ 即将搜索实例：${baseUrl}
│ 需要 Access token 才能调用搜索 API（与用户设置中的令牌一致）。
│
│ • 粘贴令牌后按 Enter 继续
│ • 直接按 Enter（留空）可取消，不会发起任何请求
└────────────────────────────────────────────────────────────────
`.trim());

  return new Promise((resolve) => {
    rl.question('请粘贴 SOURCEGRAPH_ACCESS_TOKEN: ', (answer) => {
      rl.close();
      resolve((answer || '').trim());
    });
  });
}

function buildSearchQuery(apiString, patternType) {
  const term = apiString.includes(' ') || apiString.includes('"')
    ? `"${apiString.replace(/"/g, '\\"')}"`
    : apiString;
  return `patternType:${patternType} ${term} count:all`;
}

async function searchApiUsage(apiString, options = {}) {
  const { patternType = 'literal', maxRepos = 10000 } = options;

  const query = buildSearchQuery(apiString, patternType);
  const params = new URLSearchParams({
    q: query,
    v: 'V3',
    display: String(options.displayLimit ?? 3000),
  });

  const url = `${SOURCEGRAPH_URL}/.api/search/stream?${params.toString()}`;
  const headers = { Accept: 'text/event-stream' };
  const accessToken = options.accessToken || '';
  if (accessToken) headers['Authorization'] = `token ${accessToken}`;

  const res = await fetch(url, { headers });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Sourcegraph 请求失败: ${res.status} ${res.statusText}\n${text}`);
  }

  const repos = new Set();
  const details = [];
  const text = await res.text();

  function pushDetail(repository, path, lineNumber, line, commit, contextSnippet) {
    details.push({
      repository,
      path,
      lineNumber,
      line,
      contextSnippet: contextSnippet ?? line,
      ...(commit ? { commit } : {}),
    });
  }

  const eventBlocks = text.split(/\n\n+/).filter(Boolean);
  for (const block of eventBlocks) {
    const lines = block.split('\n');
    const eventLine = lines.find((l) => l.startsWith('event:'));
    const dataLine = lines.find((l) => l.startsWith('data:'));
    const eventType = eventLine ? eventLine.replace(/^event:\s*/, '').trim() : '';
    if (eventType === 'matches' && dataLine) {
      try {
        const data = JSON.parse(dataLine.replace(/^data:\s*/, ''));
        if (Array.isArray(data)) {
          for (const match of data) {
            if (!match.repository) continue;
            const path = match.path || '';
            if (path.endsWith('.pb.go') || path.endsWith('.swagger.json') || path.endsWith('openapi.yaml') || path.endsWith('.md')) continue;
            repos.add(match.repository);
            const commit = match.commit;
            const lineMatches = match.lineMatches || [];
            if (lineMatches.length > 0) {
              for (const lm of lineMatches) {
                const line = (lm.line || '').trim();
                pushDetail(match.repository, path, lm.lineNumber ?? 0, line, commit, line);
              }
            } else {
              const line = match.type === 'path' ? `(路径匹配) ${path}` : '(无行内容)';
              pushDetail(match.repository, path, 0, line, commit, line);
            }
            if (repos.size >= maxRepos) break;
          }
        }
      } catch (_) {}
    }
    if (repos.size >= maxRepos) break;
  }

  return { repos: Array.from(repos), details };
}

/**
 * 从仓库名解析服务名与所属团队
 * 例：gitlab.yc345.tv/backend/go-revenue → { serviceName: 'go-revenue', team: 'backend(后端)' }
 *     gitlab.yc345.tv/frontend/activity-page → { serviceName: 'activity-page', team: 'frontend(前端)' }
 */
const TEAM_DISPLAY = {
  backend: 'backend(后端)',
  frontend: 'frontend(前端)',
  "security-and-payment": 'security-and-payment(安全与支付)',
  ops: 'ops(运维)',
  wuhan: 'wuhan(武汉)',
  android: 'android(安卓)',
  ios: 'ios(苹果)',
  teacher: 'teacher(教师端)',
  "7to12app-test": '7to12app-test(7-12测试)',
};
function parseRepoServiceAndTeam(repository) {
  const parts = (repository || '').split('/').filter(Boolean);
  const serviceName = parts.length >= 2 ? parts[parts.length - 1] : repository || '-';
  const teamRaw = parts.length >= 2 ? parts[parts.length - 2] : '-';
  const team = TEAM_DISPLAY[teamRaw.toLowerCase()] ?? '其他';
  return { serviceName, team };
}

function printUsage() {
  console.log(`
在 Sourcegraph 上搜索使用了指定 API 的所有项目

用法:
  node searchApi.js <API字符串> [选项]

选项:
  --json    输出 JSON
  --regex   正则匹配
  --limit N 最多 N 条（默认 3000）
  --md      输出 Markdown 表格

访问令牌: 未设置 SOURCEGRAPH_ACCESS_TOKEN 时，在终端中会先说明再提示粘贴；
  留空回车可取消。非终端环境请预先 export 该变量。
环境变量（可选）: SOURCEGRAPH_URL 仅在使用自建/私有地址时覆盖。
`);
}

function formatAsMarkdown(apiString, details) {
  const escapePipe = (s) => String(s).replace(/\|/g, '\\|');
  const escapeHtml = (s) =>
    String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  const codeToTableCell = (code) => {
    const escaped = escapeHtml(code || '');
    return `<pre><code>${escaped.replace(/\n/g, '<br>')}</code></pre>`;
  };
  const lines = [];
  lines.push(`# API 使用情况：\`${apiString.replace(/`/g, '\\`')}\``);
  lines.push('');
  lines.push('| **项目名称** | **服务名** | **所属团队** | **文件路径** | **定位行** | **相关代码上下文** |');
  lines.push('| --- | --- | --- | --- | --- | --- |');
  for (const d of details) {
    const { serviceName, team } = parseRepoServiceAndTeam(d.repository);
    const codeCell = codeToTableCell(d.contextSnippet || d.line);
    lines.push(`| **${escapePipe(d.repository)}** | ${escapePipe(serviceName)} | ${escapePipe(team)} | ${escapePipe(d.path)} | ${d.lineNumber} | ${codeCell} |`);
  }
  return lines.join('\n');
}

async function main() {
  const args = process.argv.slice(2);
  const jsonOut = args.includes('--json');
  const mdOut = args.includes('--md');
  const useRegex = args.includes('--regex');
  const apiArg = args.filter((a) => !a.startsWith('--'))[0];

  if (!apiArg || args.includes('--help') || args.includes('-h')) {
    printUsage();
    process.exit(apiArg ? 0 : 1);
  }

  let accessToken = (process.env.SOURCEGRAPH_ACCESS_TOKEN || '').trim();
  if (!accessToken) {
    accessToken = await promptForToken(SOURCEGRAPH_URL);
  }
  if (!accessToken) {
    console.error(`
未提供访问令牌，已取消执行（未向 Sourcegraph 发送请求）。
可选操作：
  • 在终端设置：export SOURCEGRAPH_ACCESS_TOKEN='你的令牌'
  • 或重新运行脚本，在提示处粘贴令牌
`.trim());
    process.exit(1);
  }

  try {
    const limitIdx = args.indexOf('--limit');
    const displayLimit = limitIdx >= 0 && args[limitIdx + 1] ? parseInt(args[limitIdx + 1], 10) : 3000;

    const { repos, details } = await searchApiUsage(apiArg, {
      accessToken,
      patternType: useRegex ? 'regexp' : 'literal',
      displayLimit: Number.isFinite(displayLimit) ? displayLimit : 3000,
    });
    if (mdOut) {
      console.log(formatAsMarkdown(apiArg, details));
    } else if (jsonOut) {
      console.log(JSON.stringify({ repos, details }, null, 2));
    } else {
      console.log(`找到 ${repos.length} 个仓库，共 ${details.length} 处调用\n`);
      console.log('--- 仓库列表 ---');
      repos.forEach((r) => console.log(r));
      console.log('\n--- 调用详情 ---');
      for (const d of details) {
        console.log(`\n[${d.repository}] ${d.path}:${d.lineNumber}`);
        console.log(`  ${d.line}`);
      }
    }
  } catch (err) {
    console.error('错误:', err.message);
    process.exit(1);
  }
}

main();
