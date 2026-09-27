$ErrorActionPreference = "Stop"

$Root = (Get-Location).Path

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " SAR Cargo UAV - Obsidian Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Projeto: $Root"
Write-Host ""

$Folders = @(
    "docs",
    "docs\inbox",
    "docs\attachments",
    "docs\master",
    "docs\requirements",
    "docs\decisions",
    "docs\lessons",
    "docs\experiments",
    "docs\issues",
    "docs\geometries",
    "docs\meshes",
    "docs\openfoam",
    "docs\numerical-tank",
    "docs\propulsion",
    "docs\avionics",
    "docs\aerodynamics",
    "docs\structures",
    "docs\architecture",
    "docs\templates"
)

foreach ($Folder in $Folders) {

    $Path = Join-Path $Root $Folder

    if (-not (Test-Path $Path)) {

        New-Item `
            -ItemType Directory `
            -Path $Path `
            -Force | Out-Null

        Write-Host "[CRIADO]  $Folder" -ForegroundColor Green
    }
    else {
        Write-Host "[EXISTE]  $Folder" -ForegroundColor DarkGray
    }
}

# Arquivos placeholder para o Git manter pastas vazias
$KeepFolders = @(
    "docs\inbox",
    "docs\attachments",
    "docs\master",
    "docs\geometries",
    "docs\meshes",
    "docs\propulsion",
    "docs\avionics",
    "docs\aerodynamics",
    "docs\structures",
    "docs\architecture"
)

foreach ($Folder in $KeepFolders) {

    $KeepFile = Join-Path $Root "$Folder\.gitkeep"

    if (-not (Test-Path $KeepFile)) {
        New-Item `
            -ItemType File `
            -Path $KeepFile `
            -Force | Out-Null
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Estrutura criada com sucesso" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Base de conhecimento:"
Write-Host "  $Root\docs"
Write-Host ""
Write-Host "Novas notas:"
Write-Host "  docs\inbox"
Write-Host ""
Write-Host "Anexos:"
Write-Host "  docs\attachments"
Write-Host ""