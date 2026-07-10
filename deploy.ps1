# ============================================
#  Dinol Briefing Deploy Script (deploy.ps1)
#  Usage:  ./deploy.ps1  ["commit message"]
#  (No arg = commit message "briefing YYYY-MM-DD")
# ============================================

# Force UTF-8 output so Korean commit messages are not garbled
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# 0) Move to repo folder (edit this line if the path differs)
Set-Location "C:\Users\jrdo\Desktop\dinol-news\dinol-news"

# 1) Pull latest first (avoid conflicts from routine / other PC)
Write-Host "`n[1/4] Pulling latest (git pull)..." -ForegroundColor Cyan
git pull

# 2) Stage all changes (briefing, index, assets, docs)
Write-Host "`n[2/4] Staging changes (git add -A)..." -ForegroundColor Cyan
git add -A

# 3) Commit (message from arg, or today's date)
$msg = if ($args.Count -gt 0) { $args -join " " } else { "briefing " + (Get-Date -Format "yyyy-MM-dd") }
Write-Host "`n[3/4] Commit: $msg" -ForegroundColor Cyan
git commit -m "$msg"

# 4) Push
Write-Host "`n[4/4] Pushing (git push)..." -ForegroundColor Cyan
git push

# Result
Write-Host "`n=== Deploy status ===" -ForegroundColor Green
git status
Write-Host "`nDone! GitHub Actions will deploy in ~20-30s." -ForegroundColor Green
Write-Host "Check: https://github.com/kei-insu/dinol-news/actions`n" -ForegroundColor Green
