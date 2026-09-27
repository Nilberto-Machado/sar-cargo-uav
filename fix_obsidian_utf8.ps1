$ErrorActionPreference = "Stop"

$Root = Join-Path (Get-Location).Path "docs"

if (-not (Test-Path $Root)) {
    throw "docs folder not found: $Root"
}

$Cp1252 = [System.Text.Encoding]::GetEncoding(1252)
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

# Typical mojibake marker characters:
# U+00C3 = Latin Capital A with tilde
# U+00C2 = Latin Capital A with circumflex
# U+00E2 = Latin small a with circumflex
# U+00F0 = Latin small eth
$Marker1 = [char]0x00C3
$Marker2 = [char]0x00C2
$Marker3 = [char]0x00E2
$Marker4 = [char]0x00F0

$Files = Get-ChildItem -Path $Root -Recurse -File -Filter "*.md"

$FixedCount = 0
$SkippedCount = 0

Write-Host ""
Write-Host "========================================"
Write-Host " SAR Cargo UAV - UTF8 Repair"
Write-Host "========================================"
Write-Host ""

foreach ($File in $Files) {

    $Text = [System.IO.File]::ReadAllText($File.FullName)

    $HasMojibake =
        $Text.Contains($Marker1) -or
        $Text.Contains($Marker2) -or
        $Text.Contains($Marker3) -or
        $Text.Contains($Marker4)

    if (-not $HasMojibake) {
        Write-Host "[OK]      $($File.FullName)"
        $SkippedCount++
        continue
    }

    $Backup = $File.FullName + ".utf8-backup"

    if (-not (Test-Path $Backup)) {
        Copy-Item -LiteralPath $File.FullName -Destination $Backup
    }

    try {
        $Bytes = $Cp1252.GetBytes($Text)
        $Fixed = [System.Text.Encoding]::UTF8.GetString($Bytes)

        [System.IO.File]::WriteAllText(
            $File.FullName,
            $Fixed,
            $Utf8NoBom
        )

        Write-Host "[FIXED]   $($File.FullName)"
        $FixedCount++
    }
    catch {
        Write-Host "[ERROR]   $($File.FullName)"
        Write-Host $_.Exception.Message
    }
}

Write-Host ""
Write-Host "========================================"
Write-Host " Finished"
Write-Host "========================================"
Write-Host ""
Write-Host "Fixed:   $FixedCount"
Write-Host "Skipped: $SkippedCount"
Write-Host ""
Write-Host "Backup extension: .utf8-backup"
Write-Host ""