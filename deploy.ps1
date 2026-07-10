# ============================================
#  디놀 브리핑 배포 스크립트 (deploy.ps1)
#  사용법: PowerShell에서  ./deploy.ps1
#  (인수 없이 실행하면 "브리핑 YYYY-MM-DD" 메시지로 커밋)
# ============================================

# 0) 프로젝트 폴더로 이동 (경로가 다르면 이 줄만 수정)
Set-Location "C:\Users\jrdo\Desktop\dinol-news\dinol-news"

# 1) 원격 최신부터 받기 (다른 PC/루틴 반영분 충돌 방지)
Write-Host "`n[1/4] 원격 최신 받기 (git pull)..." -ForegroundColor Cyan
git pull

# 2) 변경 파일 스테이징 (브리핑·index·에셋·문서 모두 포함)
Write-Host "`n[2/4] 변경 파일 추가 (git add -A)..." -ForegroundColor Cyan
git add -A

# 3) 커밋 (메시지: 인수로 받거나, 없으면 오늘 날짜)
$msg = if ($args.Count -gt 0) { $args -join " " } else { "브리핑 " + (Get-Date -Format "yyyy-MM-dd") }
Write-Host "`n[3/4] 커밋: $msg" -ForegroundColor Cyan
git commit -m "$msg"

# 4) 푸시
Write-Host "`n[4/4] 푸시 (git push)..." -ForegroundColor Cyan
git push

# 결과
Write-Host "`n=== 배포 상태 ===" -ForegroundColor Green
git status
Write-Host "`n완료! GitHub Actions에서 배포가 진행됩니다 (20~30초)." -ForegroundColor Green
Write-Host "확인: https://github.com/kei-insu/dinol-news/actions`n" -ForegroundColor Green
