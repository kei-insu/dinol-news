// assets/ 를 dist/assets/ 로 통째 복사하고,
// 완결형 루트 페이지들(index.html 등)을 dist/ 최상위로 복사한다.
import { cp, stat, readdir, access } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const src = path.join(root, 'assets');
const distDir = path.join(root, 'dist');
const dest = path.join(distDir, 'assets');

// dist/ 가 없으면 오류
try {
  const s = await stat(distDir);
  if (!s.isDirectory()) throw new Error('not a directory');
} catch {
  console.error(`[copy-assets] 오류: dist/ 가 없습니다 (${distDir}). 먼저 astro build 를 실행하세요.`);
  process.exit(1);
}

await cp(src, dest, { recursive: true });

// 복사한 파일 개수 세기 (재귀)
async function countFiles(dir) {
  let n = 0;
  const entries = await readdir(dir, { withFileTypes: true });
  for (const e of entries) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) n += await countFiles(p);
    else n += 1;
  }
  return n;
}

const count = await countFiles(dest);
console.log(`[copy-assets] assets/ → dist/assets/ 복사 완료: ${count}개 파일`);

// ── 루트 완결형 페이지/데이터 파일을 dist/ 최상위로 복사 ──
// index.html 은 astro build 산출물을 이번 복사가 덮어써야 한다(build 뒤 실행이라 순서 OK).
// fortune.html 은 있으면 복사, 없으면 건너뛴다.
const rootFiles = [
  'index.html',
  'archive.html',
  'privacy.html',
  'index.json',
  '.nojekyll',
  'fortune.html', // optional
];

console.log('[copy-assets] 루트 → dist/ 복사:');
for (const name of rootFiles) {
  const from = path.join(root, name);
  const to = path.join(distDir, name);
  try {
    await access(from);
  } catch {
    console.log(`  - ${name}: 원본 없음 → 건너뜀`);
    continue;
  }
  await cp(from, to);
  console.log(`  · ${name}: 복사됨`);
}
