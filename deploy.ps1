# ============================================
#  Dinol Briefing Deploy Script (deploy.ps1) — HARDENED
#  Usage:  ./deploy.ps1  ["commit message"]
#  (No arg = commit message "briefing YYYY-MM-DD")
#
#  안전장치: 아래 중 하나라도 걸리면 배포를 '즉시 중단'한다.
#   - 원격이 로컬보다 앞서 있음(뒤처짐) 또는 히스토리가 갈라짐  → git pull 먼저
#   - 스테이징된 파일에 충돌 마커(<<<<<<< ======= >>>>>>>) 존재  → 정리 먼저
#   - push 실패                                                  → git pull 후 재시도
#  ⚠️ 이 스크립트는 스스로 merge/pull 하지 않는다. 동기화는 사람이
#     '작업 시작 전' git pull 로 먼저 맞춘다(clean 상태에서). 여기서는 확인·푸시만.
# ============================================

# UTF-8 (한글 커밋 메시지/콘솔 깨짐 방지)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# 0) 스크립트가 있는 폴더 = 레포 루트로 이동 (PC 독립)
Set-Location $PSScriptRoot

# 레포인지 확인
git rev-parse --is-inside-work-tree *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[중단] 여기는 git 레포가 아닙니다: $PSScriptRoot" -ForegroundColor Red
    exit 1
}

# 1) 원격 상태 확인 (fetch만 — merge/pull은 하지 않음)
Write-Host "`n[1/5] 원격 확인 (git fetch)..." -ForegroundColor Cyan
git fetch origin
if ($LASTEXITCODE -ne 0) {
    Write-Host "[중단] fetch 실패(네트워크/인증 확인)." -ForegroundColor Red
    exit 1
}

$local  = (git rev-parse HEAD).Trim()
$remote = (git rev-parse origin/main).Trim()
$base   = (git merge-base HEAD origin/main).Trim()

if ($local -ne $remote) {
    if ($local -eq $base) {
        Write-Host "[중단] 원격에 새 커밋이 있습니다(로컬이 뒤처짐)." -ForegroundColor Red
        Write-Host "  → 배포하지 말고 먼저:  git pull" -ForegroundColor Yellow
        Write-Host "     그 다음 브리핑 파일을 '다시' 배치하고 배포하세요." -ForegroundColor Yellow
        exit 1
    }
    elseif ($remote -eq $base) {
        Write-Host "  로컬이 원격보다 앞섬(미푸시 커밋 있음) — 진행 가능." -ForegroundColor DarkGray
    }
    else {
        Write-Host "[중단] 로컬과 원격이 갈라졌습니다(양쪽에 서로 다른 커밋)." -ForegroundColor Red
        Write-Host "  → git pull 로 통합/충돌 해결 후 다시 배포하세요." -ForegroundColor Yellow
        exit 1
    }
}
else {
    Write-Host "  원격과 동기화 상태 OK." -ForegroundColor DarkGray
}

# 2) 스테이징
Write-Host "`n[2/5] 변경 스테이징 (git add -A)..." -ForegroundColor Cyan
git add -A

# 3) 충돌 마커 검사 (스테이징된 내용 기준) — 있으면 중단
Write-Host "`n[3/5] 충돌 마커 검사..." -ForegroundColor Cyan
$conflict = git grep -l -E "^<<<<<<<|^>>>>>>>" --cached 2>$null
if ($conflict) {
    Write-Host "[중단] 충돌 마커가 남은 파일이 있습니다:" -ForegroundColor Red
    $conflict | ForEach-Object { Write-Host "   - $_" -ForegroundColor Red }
    Write-Host "  → 해당 파일의 <<<<<<< ======= >>>>>>> 를 정리한 뒤 다시 배포하세요." -ForegroundColor Yellow
    Write-Host "     (index.json/published_urls.json 이면: index는 올바른 목록으로 재작성," -ForegroundColor Yellow
    Write-Host "      published_urls.json 은 python scripts/build_published_urls.py 로 재생성)" -ForegroundColor Yellow
    exit 1
}
Write-Host "  마커 없음 — 통과." -ForegroundColor DarkGray

# 4) 커밋 (메시지: 인자 or 오늘 날짜)
$msg = if ($args.Count -gt 0) { $args -join " " } else { "briefing " + (Get-Date -Format "yyyy-MM-dd") }
Write-Host "`n[4/5] 커밋: $msg" -ForegroundColor Cyan
git commit -m "$msg"
if ($LASTEXITCODE -ne 0) {
    Write-Host "  커밋할 변경이 없습니다(working tree clean). 푸시만 시도합니다." -ForegroundColor DarkGray
}

# 5) 푸시 (fast-forward). 실패하면 중단.
Write-Host "`n[5/5] 푸시 (git push)..." -ForegroundColor Cyan
git push
if ($LASTEXITCODE -ne 0) {
    Write-Host "[중단] push 실패. 그 사이 원격이 바뀌었을 수 있습니다." -ForegroundColor Red
    Write-Host "  → git pull 로 맞춘 뒤 다시 배포하세요." -ForegroundColor Yellow
    exit 1
}

# 결과
Write-Host "`n=== 배포 상태 ===" -ForegroundColor Green
git status
Write-Host "`n완료! GitHub Actions가 ~20-30초 내 반영합니다." -ForegroundColor Green
Write-Host "Actions:  https://github.com/kei-insu/dinol-news/actions" -ForegroundColor Green
Write-Host "사이트:   https://kei-insu.github.io/dinol-news/  (Ctrl+Shift+R)`n" -ForegroundColor Green
