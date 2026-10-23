<#
    deploy-blog.ps1 - 博客增量部署

    原理：
      1. hugo 构建到站点目录下的 public/
      2. 本地逐个文件算 MD5，同时 ssh 读取服务器上现有文件的 MD5
      3. 两边对比：只上传「新增 / 有变化」的文件，删除「服务器上多余」的文件
      4. 最后修权限、校验文件数

    用法（在 deploy-blog.bat 里传参，或手动 powershell -File 调用）：
      (无参数)      增量部署：只上传变化的部分
      -Full         忽略差异，全部重传（文件多但最保险）
      -NoDelete     只上传，不删除服务器上多余的文件
      -DryRun       只计算并显示将要做什么，不实际上传/删除

    注意：
      - 本文件必须保存为「UTF-8 带 BOM」，否则 Windows PowerShell 5.1 读中文会乱码
      - 删除操作会跳过 .well-known、.user.ini 等点开头的文件，避免误删宝塔/证书验证文件
#>
[CmdletBinding()]
param(
    [switch]$Full,
    [switch]$NoDelete,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

# 统一用 UTF-8 和远端交互，避免中文路径乱码
try {
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [Console]::OutputEncoding = $utf8NoBom
    $OutputEncoding = $utf8NoBom
} catch { }

$SshHost    = 'blog'
$RemotePath = '/www/wwwroot/huanhe.site'

# 本脚本位于站点根目录（my-blog）；Hugo 主程序在工作区上一级目录
$siteDir   = $PSScriptRoot
$workspace = Split-Path -Parent $PSScriptRoot
$publicDir = Join-Path $siteDir 'public'
$hugoExe   = Join-Path $workspace 'hugo_extended_0.149.0_windows-amd64\hugo.exe'

function Show-Head { param([string]$Text) Write-Host ''; Write-Host ("== " + $Text) -ForegroundColor Cyan }
function Show-Ok   { param([string]$Text) Write-Host ("  [OK] " + $Text) -ForegroundColor Green }
function Show-Info { param([string]$Text) Write-Host ("  " + $Text) }
function Show-Warn { param([string]$Text) Write-Host ("  [!] " + $Text) -ForegroundColor Yellow }

function Format-Size {
    param([double]$Bytes)
    if ($Bytes -ge 1MB) { return ('{0:N2} MB' -f ($Bytes / 1MB)) }
    if ($Bytes -ge 1KB) { return ('{0:N1} KB' -f ($Bytes / 1KB)) }
    return (('{0} B' -f [int]$Bytes))
}

# 这些文件不参与差异删除，避免误删服务器上手工放的东西
$ProtectedPatterns = @('(^|/)\.', '^robots\.txt$')
function Test-Protected {
    param([string]$RelPath)
    foreach ($pat in $ProtectedPatterns) {
        if ($RelPath -match $pat) { return $true }
    }
    return $false
}

# 把一批相对路径安全地交给远端执行
# （避开 Windows 管道 BOM、换行符、中文编码等坑）
# 路径列表 -> UTF-8 -> Base64 -> 远端 base64 -d 还原 -> xargs 逐行执行
function Invoke-RemoteListAction {
    param(
        [string[]]$Items,
        [string]$ShellAction
    )
    $clean = @($Items | Where-Object { $_ -and $_.Trim() })
    if ($clean.Count -eq 0) { return }

    $chunkSize = 40
    for ($i = 0; $i -lt $clean.Count; $i += $chunkSize) {
        $end   = [Math]::Min($i + $chunkSize - 1, $clean.Count - 1)
        $chunk = @($clean[$i..$end])
        $b64   = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes(($chunk -join "`n")))
        $remoteCmd = "cd '" + $RemotePath + "' && printf %s '" + $b64 + "' | base64 -d | xargs -d '\n' " + $ShellAction
        & ssh -o BatchMode=yes $SshHost $remoteCmd
        if ($LASTEXITCODE -ne 0) {
            throw ("远端操作失败（" + $ShellAction + "）；可加 -DryRun 先预览清单")
        }
    }
}

# 解析远端 md5sum 输出（每行：「32位哈希 + 空白 + ./路径」）
function Convert-Md5Output {
    param([object[]]$Lines)
    $map = @{}
    foreach ($item in @($Lines)) {
        $line = [string]$item
        if ($line -notmatch '^[0-9a-fA-F]{32}[ \t]') { continue }
        $hash = $line.Substring(0, 32).ToLower()
        $rel  = $line.Substring(32).TrimStart()
        if ($rel.StartsWith('*'))  { $rel = $rel.Substring(1) }
        if ($rel.StartsWith('./')) { $rel = $rel.Substring(2) }
        $rel  = $rel.TrimEnd()
        if ($rel) { $map[$rel] = $hash }
    }
    return $map
}

# 一次性取回远端所有文件的 MD5
# 整包 Base64 传回，彻底规避「控制台编码 / 中文路径」问题
function Get-RemoteFileHashes {
    param(
        [string]$Path,
        [string]$SshTarget
    )
    $raw = & ssh -o BatchMode=yes -o ConnectTimeout=20 $SshTarget ("cd '" + $Path + "' 2>/dev/null && find . -type f -print0 | xargs -0 md5sum 2>/dev/null | base64 | tr -d '\n'") 2>$null
    $ok = ($LASTEXITCODE -eq 0)
    $text = ''
    $b64 = (@($raw) -join '').Trim()
    if ($ok -and $b64) {
        try {
            $text = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($b64))
        } catch {
            $text = ''
        }
    }
    $map = Convert-Md5Output ($text -split "`n")
    return @{ Ok = $ok; Map = $map }
}

$startedAt = Get-Date

try {
    # ---------------------------------------------------------------- 0 环境检查
    Show-Head '0/5 环境检查'
    if (-not (Test-Path -LiteralPath $hugoExe))   { throw ("找不到 Hugo：" + $hugoExe) }
    if (-not (Test-Path -LiteralPath $siteDir))   { throw ("找不到站点目录：" + $siteDir) }

    $probe = & ssh -o BatchMode=yes -o ConnectTimeout=15 $SshHost "echo DEPLOY_PROBE_OK" 2>$null
    if (($LASTEXITCODE -ne 0) -or (($probe -join "`n") -notmatch 'DEPLOY_PROBE_OK')) {
        throw ("SSH 连接失败（" + $SshHost + "）。请先确认网络和密钥可用，例如手动执行：ssh " + $SshHost)
    }
    Show-Ok ("SSH 正常 -> " + $SshHost)
    Show-Ok ("远端目录 -> " + $RemotePath)

    # ---------------------------------------------------------------- 1 构建
    Show-Head '1/5 构建站点'
    Push-Location -LiteralPath $siteDir
    try {
        & $hugoExe --minify --cleanDestinationDir | Out-Host
        $buildExit = $LASTEXITCODE
    } finally {
        Pop-Location
    }
    if ($buildExit -ne 0) { throw 'Hugo 构建失败，已中止部署' }
    if (-not (Test-Path -LiteralPath (Join-Path $publicDir 'index.html'))) { throw '构建产物缺少 index.html，已中止部署' }
    Show-Ok '构建完成'

    # ---------------------------------------------------------------- 2 计算差异
    Show-Head '2/5 对比本地与服务器'

    $local = @{}
    $localSize = @{}
    Get-ChildItem -LiteralPath $publicDir -Recurse -File -Force | ForEach-Object {
        $rel = $_.FullName.Substring($publicDir.Length + 1).Replace('\', '/')
        $local[$rel] = (Get-FileHash -LiteralPath $_.FullName -Algorithm MD5).Hash.ToLower()
        $localSize[$rel] = $_.Length
    }
    Show-Info ("本地文件：" + $local.Count + " 个，" + (Format-Size (($localSize.Values | Measure-Object -Sum).Sum)))

    $scan = Get-RemoteFileHashes -Path $RemotePath -SshTarget $SshHost
    $remote = $scan.Map
    $remoteScanOk = $scan.Ok

    if (-not $remoteScanOk) {
        Show-Warn '服务器目录尚不存在或读取失败，按「首次部署」处理'
    } else {
        Show-Info ("服务器文件：" + $remote.Count + " 个")
    }

    $uploadList = @(
        $local.Keys | Where-Object {
            $Full -or (-not $remote.ContainsKey($_)) -or ($remote[$_] -ne $local[$_])
        }
    ) | Sort-Object

    $deleteList = @()
    if (-not $NoDelete) {
        $deleteList = @(
            $remote.Keys | Where-Object {
                (-not $local.ContainsKey($_)) -and (-not (Test-Protected $_))
            }
        ) | Sort-Object
    }

    $uploadBytes = 0.0
    foreach ($rel in $uploadList) { $uploadBytes += [double]$localSize[$rel] }
    $skipCount = $local.Count - $uploadList.Count

    Show-Info ("需要上传：" + $uploadList.Count + " 个文件（" + (Format-Size $uploadBytes) + "）")
    Show-Info ("需要删除：" + $deleteList.Count + " 个文件")
    Show-Info ("跳过未变化：" + $skipCount + " 个文件")

    if ($uploadList.Count -eq 0 -and $deleteList.Count -eq 0) {
        Show-Ok '服务器已经是最新，无需上传'
        Write-Host ''
        return
    }

    if ($uploadList.Count -gt 0) {
        $preview = @($uploadList | Select-Object -First 25)
        foreach ($rel in $preview) { Show-Info ("  + " + $rel) }
        if ($uploadList.Count -gt $preview.Count) { Show-Info ("  ... 另有 " + ($uploadList.Count - $preview.Count) + " 个") }
    }
    if ($deleteList.Count -gt 0) {
        foreach ($rel in @($deleteList | Select-Object -First 25)) { Show-Info ("  - " + $rel) }
        if ($deleteList.Count -gt 25) { Show-Info ("  ... 另有 " + ($deleteList.Count - 25) + " 个") }
    }

    if ($DryRun) {
        Show-Warn 'DryRun 模式：只显示计划，没有实际上传'
        return
    }

    # ---------------------------------------------------------------- 3 建目录
    Show-Head '3/5 准备服务器目录'
    if (-not $remoteScanOk) {
        & ssh -o BatchMode=yes $SshHost ("mkdir -p '" + $RemotePath + "'")
        if ($LASTEXITCODE -ne 0) { throw '创建远端目录失败' }
    }

    $dirSet = @{}
    foreach ($rel in $uploadList) {
        $idx = $rel.LastIndexOf('/')
        if ($idx -gt 0) {
            $dir = $rel.Substring(0, $idx)
            while ($dir) {
                $dirSet[$dir] = $true
                $dir = $dir.Substring(0, [Math]::Max(0, $dir.LastIndexOf('/')))
            }
        }
    }
    if ($dirSet.Count -gt 0) {
        $dirList = @($dirSet.Keys | Sort-Object)
        Invoke-RemoteListAction -Items $dirList -ShellAction 'mkdir -p'
    }
    Show-Ok '目录就绪'

    # ---------------------------------------------------------------- 4 上传 / 删除
    Show-Head '4/5 上传差异并清理多余文件'

    if ($uploadList.Count -gt 0) {
        $groups = $uploadList | Group-Object {
            $rel = [string]$_
            $idx = $rel.LastIndexOf('/')
            if ($idx -gt 0) { $rel.Substring(0, $idx) } else { '' }
        }
        $done = 0
        foreach ($group in $groups) {
            $dir = [string]$group.Name
            $sources = @($group.Group | ForEach-Object { Join-Path $publicDir (([string]$_).Replace('/', '\')) })
            if ($dir) {
                $dest = $SshHost + ':' + $RemotePath + '/' + $dir + '/'
            } else {
                $dest = $SshHost + ':' + $RemotePath + '/'
            }
            $scpArgs = @('-o', 'BatchMode=yes', '-q') + $sources + @($dest)
            & scp @scpArgs
            if ($LASTEXITCODE -ne 0) { throw ("上传失败（目录：" + $dir + "）") }
            $done += $sources.Count
        }
        Show-Ok ("已上传 " + $done + " 个文件")
    }

    if ($deleteList.Count -gt 0) {
        Invoke-RemoteListAction -Items $deleteList -ShellAction 'rm -f'
        & ssh -o BatchMode=yes $SshHost ("cd '" + $RemotePath + "' && find . -mindepth 1 -type d -empty -delete") | Out-Null
        Show-Ok ("已删除 " + $deleteList.Count + " 个文件")
    }

    # ---------------------------------------------------------------- 5 权限 / 校验
    Show-Head '5/5 修复权限并校验'
    # 宝塔会在站点根目录放 .user.ini（chattr +i 锁定），这类文件改不了权限，忽略报错
    $permOut = & ssh -o BatchMode=yes $SshHost ("chown -R www:www '" + $RemotePath + "' 2>/dev/null; chmod -R 755 '" + $RemotePath + "' 2>/dev/null; echo PERM_DONE")
    if (($permOut -join "`n") -match 'PERM_DONE') {
        Show-Ok '权限已修复（www:www / 755；被锁定的文件自动跳过）'
    } else {
        Show-Warn '权限修复失败，请手动检查'
    }

    $remoteCountRaw = & ssh -o BatchMode=yes $SshHost ("find '" + $RemotePath + "' -type f | wc -l")
    $remoteCount = 0
    if ($remoteCountRaw -match '(\d+)') { $remoteCount = [int]$Matches[1] }
    $protectedExtras = @($remote.Keys | Where-Object { (Test-Protected $_) -and (-not $local.ContainsKey($_)) }).Count
    $expected = $local.Count + $protectedExtras
    if ($remoteCount -eq $expected) {
        Show-Ok ("远端文件数校验通过：" + $remoteCount + " 个")
    } else {
        Show-Warn ("远端文件数 " + $remoteCount + "，预期 " + $expected + "，请留意是否有额外文件")
    }

    # 重新扫描远端哈希，确认内容与本地完全一致
    $verifyScan = Get-RemoteFileHashes -Path $RemotePath -SshTarget $SshHost
    $remoteAfter = $verifyScan.Map
    $stillDiff = 0
    foreach ($rel in $local.Keys) {
        if (-not $remoteAfter.ContainsKey($rel)) { $stillDiff++; continue }
        if ($remoteAfter[$rel] -ne $local[$rel]) { $stillDiff++ }
    }
    if ($stillDiff -eq 0) {
        Show-Ok '内容校验通过：远端与本地完全一致'
    } else {
        Show-Warn ("内容校验发现 " + $stillDiff + " 个文件仍不一致，可再跑一次或加 -Full")
    }

    $elapsed = (Get-Date) - $startedAt
    Write-Host ''
    Write-Host ("部署完成，用时 " + [math]::Round($elapsed.TotalSeconds, 1) + " 秒") -ForegroundColor Green
    Write-Host ("本次上传 " + $uploadList.Count + " 个文件（" + (Format-Size $uploadBytes) + "），删除 " + $deleteList.Count + " 个") -ForegroundColor Green
    Write-Host '访问: https://huanhe.site' -ForegroundColor Green
}
catch {
    Write-Host ''
    Write-Host ("部署中止：" + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
exit 0
