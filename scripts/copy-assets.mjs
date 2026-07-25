// assets/ 를 dist/assets/ 로 통째 복사한다.
import { cp, stat, readdir } from 'node:fs/promises';
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
