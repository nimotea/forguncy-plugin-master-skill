<#
.SYNOPSIS
    配置已创建的活字格插件项目（Logo、依赖）。

.DESCRIPTION
    此脚本用于在项目创建完成后，交互式地配置项目：
    1. 生成专业 Logo (SVG + PNG)。
    2. 添加常用 NuGet 依赖 (如 Newtonsoft.Json)。

.PARAMETER ProjectName
    项目名称。如果不提供，默认为 "MyForguncyPlugin"。

.EXAMPLE
    .\setup_project.ps1 -ProjectName "MyNewPlugin"
#>

param(
    [string]$ProjectName = "MyForguncyPlugin"
)

try {
    $TargetPath = Join-Path (Get-Location) $ProjectName
    
    if (-not (Test-Path $TargetPath)) {
        Write-Warning "Project folder '$ProjectName' not found in current directory."
        Write-Warning "Please make sure you have created the project and are running this script from the parent directory."
        return
    }

    # Logo Generation Prompt
    Write-Host "`n=== Plugin Configuration ===" -ForegroundColor Cyan
    Write-Host "Do you want to generate a professional plugin logo? (Y/N)" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq 'Y' -or $response -eq 'y') {
        Write-Host "Select logo icon type:"
        Write-Host "1. Text only (Default)"
        Write-Host "2. Gantt (Industrial/APS)"
        Write-Host "3. Chart (Analytics/Reports)"
        Write-Host "4. Database (Storage/Data)"
        Write-Host "5. Gear (Tools/Processing)"
        $typeIdx = Read-Host "Choice [1-5]"
        $LogoType = switch ($typeIdx) {
            "2" { "gantt" }
            "3" { "chart" }
            "4" { "db" }
            "5" { "gear" }
            Default { "text" }
        }

        $LogoText = Read-Host "Enter 2-3 characters for the logo (e.g. APS)"
        if ([string]::IsNullOrWhiteSpace($LogoText)) { $LogoText = "FP" }
        
        $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
        $GenerateLogoScript = Join-Path $ScriptDir "generate_logo.py"
        
        if (Test-Path $GenerateLogoScript) {
            # Use --sync to automatically overwrite existing logos
            python $GenerateLogoScript $TargetPath --text $LogoText --type $LogoType --sync
            Write-Host "Logos generated and synchronized in $ProjectName\Resources\" -ForegroundColor Green
            
            Write-Host "`n[Important] For PluginConfig.json (Main Icon), use:" -ForegroundColor Yellow
            Write-Host "Resources/PluginLogo.png (or your custom name)" -ForegroundColor White
            Write-Host "`n[Tip] For Command/CellType class [Icon] attribute, use:" -ForegroundColor Cyan
            Write-Host "[Icon(""pack://application:,,,/$ProjectName;component/Resources/PluginLogo.png"")]" -ForegroundColor White
        } else {
            Write-Warning "Logo generation script not found at $GenerateLogoScript"
        }
    }

    Write-Host "`nDo you want to add common dependencies (Newtonsoft.Json)? (Y/N)" -ForegroundColor Yellow
    $addJson = Read-Host
    if ($addJson -eq 'Y' -or $addJson -eq 'y') {
        Push-Location $TargetPath
        dotnet add package Newtonsoft.Json
        Pop-Location
        Write-Host "Added Newtonsoft.Json to $ProjectName" -ForegroundColor Green
    }
    
    Write-Host "`nConfiguration complete!" -ForegroundColor Green
}
catch {
    Write-Error "An error occurred during setup: $_"
}
