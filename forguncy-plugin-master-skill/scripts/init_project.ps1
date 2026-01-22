<#
.SYNOPSIS
    调用活字格插件构建器来初始化新项目。

.DESCRIPTION
    此脚本用于自动检测并启动官方的“活字格插件构建器”工具。
    脚本会尝试在常见安装路径下查找构建器，如果找到则直接启动。
    支持传入项目名称参数。

.PARAMETER ProjectName
    要创建的项目名称。如果不提供，默认为 "MyForguncyPlugin"。

.EXAMPLE
    .\InitProject.ps1 -ProjectName "MyNewPlugin"
#>

param(
    [string]$ProjectName = "MyForguncyPlugin"
)

# Define common paths for the builder
$PossiblePaths = @(
    "D:\Code\ForguncyPluginBuilder\forguncyPluginBuilder_V11.1\bin\ForguncyPluginCreator.exe",
    "C:\Program Files\Forguncy Plugin Builder\ForguncyPluginCreator.exe",
    "C:\Program Files (x86)\Forguncy Plugin Builder\ForguncyPluginCreator.exe",
    "$env:LOCALAPPDATA\Forguncy Plugin Builder\ForguncyPluginCreator.exe",
    "E:\forguncyPluginBuilder_V11.1\bin\ForguncyPluginCreator.exe"
)

$BuilderPath = $null

# Check paths
foreach ($path in $PossiblePaths) {
    if (Test-Path $path) {
        $BuilderPath = $path
        break
    }
}

if ($null -eq $BuilderPath) {
    Write-Warning "Forguncy Plugin Builder not found in default paths."
    Write-Host "Checked paths:"
    $PossiblePaths | ForEach-Object { Write-Host " - $_" }
    Write-Host "`nPlease start the builder manually."
    return
}

Write-Host "Builder found: $BuilderPath"
Write-Host "Starting builder for project: $ProjectName ..."

try {
    # Get the directory of the builder executable to set as WorkingDirectory
    # This prevents issues where the builder fails to load resources from relative paths
    $BuilderDir = Split-Path -Parent $BuilderPath
    
    # Try to start the builder with WorkingDirectory set
    Start-Process -FilePath $BuilderPath -WorkingDirectory $BuilderDir -ArgumentList "/name `"$ProjectName`"" -ErrorAction Stop
    
    Write-Host "Builder started. Please complete the project creation in the GUI."
}
catch {
    Write-Error "Failed to start builder: $_"
}
