# Paper2Code 运行脚本 (PowerShell 版本)
# 用法: .\run.ps1

# 获取脚本所在目录
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScript = Join-Path $scriptDir "run.py"

# 检查 Python 是否可用
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "错误: 找不到 Python，请确保 Python 已安装并添加到 PATH" -ForegroundColor Red
    exit 1
}

# 运行 Python 脚本
Write-Host "启动 Paper2Code 流程..." -ForegroundColor Green
python $pythonScript

# 检查退出码
if ($LASTEXITCODE -ne 0) {
    Write-Host "执行失败，退出码: $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "执行完成！" -ForegroundColor Green
