[CmdletBinding()]
param(
    [Parameter()]
    [ValidateNotNullOrEmpty()]
    [string]$BaseDirectory = "E:\GitHub",

    [Parameter()]
    [ValidateNotNullOrEmpty()]
    [string]$RepositoryUrl = "https://github.com/Nilberto-Machado/sar-cargo-uav.git",

    [Parameter()]
    [switch]$InstallMissingTools,

    [Parameter()]
    [switch]$OpenVault,

    [Parameter()]
    [string]$LogPath
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"

$script:Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[Console]::InputEncoding = $script:Utf8NoBom
[Console]::OutputEncoding = $script:Utf8NoBom
$OutputEncoding = $script:Utf8NoBom

if ([string]::IsNullOrWhiteSpace($LogPath)) {
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $LogPath = Join-Path ([System.IO.Path]::GetTempPath()) "sar-cargo-uav-bootstrap-$timestamp.log"
}

$logDirectory = Split-Path -Parent $LogPath
if ($logDirectory -and -not (Test-Path -LiteralPath $logDirectory)) {
    New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
}
[System.IO.File]::WriteAllText($LogPath, "", $script:Utf8NoBom)

function Write-Log {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,

        [Parameter()]
        [ValidateSet("INFO", "OK", "WARN", "ERROR")]
        [string]$Level = "INFO"
    )

    $line = "[{0}] [{1}] {2}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Level, $Message
    $color = switch ($Level) {
        "OK" { "Green" }
        "WARN" { "Yellow" }
        "ERROR" { "Red" }
        default { "Cyan" }
    }

    Write-Host $line -ForegroundColor $color
    [System.IO.File]::AppendAllText($LogPath, "$line`r`n", $script:Utf8NoBom)
}

function Write-Section {
    param([Parameter(Mandatory = $true)][string]$Title)
    Write-Host ""
    Write-Log "=== $Title ==="
}

function Confirm-Action {
    param([Parameter(Mandatory = $true)][string]$Prompt)
    $answer = Read-Host "$Prompt [s/N]"
    return $answer -match "^(s|sim|y|yes)$"
}

function Resolve-Executable {
    param(
        [Parameter(Mandatory = $true)][string]$CommandName,
        [Parameter()][string[]]$CandidatePaths = @()
    )

    $command = Get-Command $CommandName -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    foreach ($candidate in $CandidatePaths) {
        if ($candidate -and (Test-Path -LiteralPath $candidate -PathType Leaf)) {
            return $candidate
        }
    }

    return $null
}

function Install-WithWinget {
    param(
        [Parameter(Mandatory = $true)][string]$DisplayName,
        [Parameter(Mandatory = $true)][string]$PackageId
    )

    $winget = Resolve-Executable -CommandName "winget.exe"
    if (-not $winget) {
        Write-Log "winget não foi encontrado. Instale $DisplayName manualmente e execute o script novamente." "WARN"
        return $false
    }

    if (-not (Confirm-Action "Instalar $DisplayName com winget agora?")) {
        Write-Log "Instalação de $DisplayName não autorizada; nenhuma alteração foi feita." "WARN"
        return $false
    }

    Write-Log "Iniciando instalação confirmada de $DisplayName via winget."
    & $winget install --id $PackageId --exact --source winget --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) {
        throw "winget não conseguiu instalar $DisplayName (código $LASTEXITCODE)."
    }

    Write-Log "$DisplayName instalado pelo winget." "OK"
    return $true
}

function Get-RepositoryIdentity {
    param([Parameter(Mandatory = $true)][string]$Url)

    $value = $Url.Trim().TrimEnd("/")
    if ($value -match "^[a-zA-Z][a-zA-Z0-9+.-]*://") {
        try {
            $uri = [Uri]$value
            if ($uri.UserInfo) {
                throw "A URL do repositório contém credenciais. Use uma URL limpa e deixe a autenticação para o Git Credential Manager ou SSH."
            }
            $value = "$($uri.Host)$($uri.AbsolutePath)"
        }
        catch [System.UriFormatException] {
            throw "URL de repositório inválida: $Url"
        }
    }
    elseif ($value -match "^[^@]+@([^:]+):(.+)$") {
        $value = "$($Matches[1])/$($Matches[2])"
    }

    $value = $value -replace "\\", "/"
    $value = $value -replace "^/+", ""
    $value = $value -replace "\.git$", ""
    return $value.ToLowerInvariant()
}

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)][string]$GitPath,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter()][switch]$AllowFailure
    )

    $output = & $GitPath @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    if (-not $AllowFailure -and $exitCode -ne 0) {
        throw "Git falhou: git $($Arguments -join ' ')`n$($output -join [Environment]::NewLine)"
    }

    return [PSCustomObject]@{
        ExitCode = $exitCode
        Output = @($output)
    }
}

function Add-LocalExcludePattern {
    param(
        [Parameter(Mandatory = $true)][string]$ExcludeFile,
        [Parameter(Mandatory = $true)][string]$Pattern
    )

    $existingLines = if (Test-Path -LiteralPath $ExcludeFile) {
        [System.IO.File]::ReadAllLines($ExcludeFile)
    }
    else {
        @()
    }

    if ($existingLines -contains $Pattern) {
        Write-Log "Exclusão local já configurada: $Pattern" "OK"
        return
    }

    $prefix = ""
    if ($existingLines.Count -gt 0 -and $existingLines[-1] -ne "") {
        $prefix = "`r`n"
    }
    [System.IO.File]::AppendAllText($ExcludeFile, "$prefix$Pattern`r`n", $script:Utf8NoBom)
    Write-Log "Exclusão local adicionada a .git/info/exclude: $Pattern" "OK"
}

try {
    Write-Section "SAR Cargo UAV - bootstrap da estação Windows"
    Write-Log "Log: $LogPath"
    Write-Log "Diretório base: $BaseDirectory"
    Write-Log "Repositório: $(Get-RepositoryIdentity -Url $RepositoryUrl)"

    Write-Section "Ferramentas"
    $gitCandidates = @(
        (Join-Path $env:ProgramFiles "Git\cmd\git.exe"),
        (Join-Path ${env:ProgramFiles(x86)} "Git\cmd\git.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Git\cmd\git.exe")
    )
    $git = Resolve-Executable -CommandName "git.exe" -CandidatePaths $gitCandidates
    if (-not $git) {
        Write-Log "Git não foi encontrado." "WARN"
        if ($InstallMissingTools) {
            [void](Install-WithWinget -DisplayName "Git" -PackageId "Git.Git")
            $git = Resolve-Executable -CommandName "git.exe" -CandidatePaths $gitCandidates
        }
    }
    if (-not $git) {
        Write-Log "Instale o Git em https://git-scm.com/ ou execute novamente com -InstallMissingTools." "ERROR"
        throw "Git é necessário para continuar."
    }
    $gitVersion = (& $git --version 2>&1) -join " "
    Write-Log "Git encontrado: $gitVersion" "OK"

    $obsidianCandidates = @(
        (Join-Path $env:LOCALAPPDATA "Obsidian\Obsidian.exe"),
        (Join-Path $env:ProgramFiles "Obsidian\Obsidian.exe"),
        (Join-Path ${env:ProgramFiles(x86)} "Obsidian\Obsidian.exe")
    )
    $obsidian = Resolve-Executable -CommandName "Obsidian.exe" -CandidatePaths $obsidianCandidates
    if (-not $obsidian) {
        Write-Log "Obsidian não foi encontrado." "WARN"
        if ($InstallMissingTools) {
            [void](Install-WithWinget -DisplayName "Obsidian" -PackageId "Obsidian.Obsidian")
            $obsidian = Resolve-Executable -CommandName "Obsidian.exe" -CandidatePaths $obsidianCandidates
        }
    }
    if ($obsidian) {
        Write-Log "Obsidian encontrado: $obsidian" "OK"
    }
    else {
        Write-Log "Instale o Obsidian em https://obsidian.md/ ou execute novamente com -InstallMissingTools." "WARN"
    }

    Write-Section "Repositório"
    $repositoryName = [System.IO.Path]::GetFileNameWithoutExtension(($RepositoryUrl.TrimEnd("/") -replace "^.*[/:]", ""))
    if ([string]::IsNullOrWhiteSpace($repositoryName)) {
        throw "Não foi possível determinar o nome do repositório a partir de $RepositoryUrl."
    }
    $baseFullPath = [System.IO.Path]::GetFullPath($BaseDirectory)
    $repositoryPath = Join-Path $baseFullPath $repositoryName

    if (-not (Test-Path -LiteralPath $baseFullPath)) {
        New-Item -ItemType Directory -Path $baseFullPath -Force | Out-Null
        Write-Log "Diretório base criado: $baseFullPath" "OK"
    }

    if (-not (Test-Path -LiteralPath $repositoryPath)) {
        Write-Log "Clone local não existe; clonando em $repositoryPath."
        $cloneResult = Invoke-Git -GitPath $git -Arguments @("clone", "--", $RepositoryUrl, $repositoryPath)
        $cloneResult.Output | ForEach-Object { Write-Log "git: $_" }
        Write-Log "Repositório clonado." "OK"
    }
    else {
        $insideResult = Invoke-Git -GitPath $git -Arguments @("-C", $repositoryPath, "rev-parse", "--is-inside-work-tree") -AllowFailure
        if ($insideResult.ExitCode -ne 0 -or ($insideResult.Output -join "").Trim() -ne "true") {
            throw "O destino já existe, mas não é um repositório Git: $repositoryPath. Nada foi alterado."
        }

        $topLevelResult = Invoke-Git -GitPath $git -Arguments @("-C", $repositoryPath, "rev-parse", "--show-toplevel")
        $topLevel = [System.IO.Path]::GetFullPath(($topLevelResult.Output -join "").Trim()).TrimEnd("\")
        if ($topLevel -ine ([System.IO.Path]::GetFullPath($repositoryPath).TrimEnd("\"))) {
            throw "O destino está dentro de outro repositório ($topLevel), não na raiz esperada. Nada foi alterado."
        }

        $originResult = Invoke-Git -GitPath $git -Arguments @("-C", $repositoryPath, "remote", "get-url", "origin") -AllowFailure
        if ($originResult.ExitCode -ne 0) {
            throw "O repositório existente não possui o remoto origin; não é possível validá-lo com segurança."
        }
        $actualOrigin = ($originResult.Output -join "").Trim()
        if ((Get-RepositoryIdentity -Url $actualOrigin) -ne (Get-RepositoryIdentity -Url $RepositoryUrl)) {
            throw "O destino aponta para outro repositório (origin: $(Get-RepositoryIdentity -Url $actualOrigin)). Nada foi alterado."
        }

        Write-Log "Repositório existente validado: $repositoryPath" "OK"
        Write-Log "Executando somente git fetch origin; mudanças locais não serão sobrescritas."
        $fetchResult = Invoke-Git -GitPath $git -Arguments @("-C", $repositoryPath, "fetch", "origin")
        $fetchResult.Output | ForEach-Object { Write-Log "git: $_" }
        Write-Log "Fetch concluído." "OK"
    }

    Write-Section "Exclusões locais"
    $gitDirectoryResult = Invoke-Git -GitPath $git -Arguments @("-C", $repositoryPath, "rev-parse", "--git-dir")
    $gitDirectoryValue = ($gitDirectoryResult.Output -join "").Trim()
    $gitDirectory = if ([System.IO.Path]::IsPathRooted($gitDirectoryValue)) {
        $gitDirectoryValue
    }
    else {
        Join-Path $repositoryPath $gitDirectoryValue
    }
    $infoDirectory = Join-Path $gitDirectory "info"
    if (-not (Test-Path -LiteralPath $infoDirectory)) {
        New-Item -ItemType Directory -Path $infoDirectory -Force | Out-Null
    }
    $excludeFile = Join-Path $infoDirectory "exclude"
    Add-LocalExcludePattern -ExcludeFile $excludeFile -Pattern "openfoam/cfd_v2_alpha_p4_diag_noSnap/"
    Add-LocalExcludePattern -ExcludeFile $excludeFile -Pattern "openfoam/fuselage_v2_educational/"
    Write-Log ".gitignore não foi modificado." "OK"

    Write-Section "Vault e arquivos essenciais"
    $requiredPaths = @(".obsidian", "docs", ".gitignore", ".gitattributes")
    $missingPaths = @()
    foreach ($relativePath in $requiredPaths) {
        $fullPath = Join-Path $repositoryPath $relativePath
        if (Test-Path -LiteralPath $fullPath) {
            Write-Log "Presente: $relativePath" "OK"
        }
        else {
            $missingPaths += $relativePath
            Write-Log "Ausente: $relativePath" "ERROR"
        }
    }
    if ($missingPaths.Count -gt 0) {
        throw "O clone não contém todos os componentes esperados do Vault."
    }
    Write-Log "A raiz do Vault é a raiz do repositório: $repositoryPath" "OK"

    Write-Section "Privacidade do estado local do Obsidian"
    $ignoreTests = @(
        ".obsidian/workspace.json",
        ".obsidian/workspace-mobile.json",
        ".obsidian/plugins/plugin-de-teste/data.json"
    )
    $ignoreFailure = $false
    foreach ($ignoreTest in $ignoreTests) {
        $ignoreResult = Invoke-Git -GitPath $git -Arguments @("-C", $repositoryPath, "check-ignore", "--no-index", "-q", "--", $ignoreTest) -AllowFailure
        if ($ignoreResult.ExitCode -eq 0) {
            Write-Log "Ignorado corretamente: $ignoreTest" "OK"
        }
        else {
            $ignoreFailure = $true
            Write-Log "NÃO está ignorado: $ignoreTest" "ERROR"
        }
    }
    $sharedPluginData = ".obsidian/plugins/obsidian-git/data.json"
    $sharedPluginIgnoreResult = Invoke-Git -GitPath $git -Arguments @("-C", $repositoryPath, "check-ignore", "--no-index", "-q", "--", $sharedPluginData) -AllowFailure
    if ($sharedPluginIgnoreResult.ExitCode -eq 0) {
        $ignoreFailure = $true
        Write-Log "A configuração compartilhada ainda está ignorada: $sharedPluginData" "ERROR"
    }
    else {
        Write-Log "Configuração compartilhada não está ignorada: $sharedPluginData" "OK"
    }
    $trackedPrivateFilesResult = Invoke-Git -GitPath $git -Arguments @(
        "-C", $repositoryPath, "ls-files", "--",
        ".obsidian/workspace.json",
        ".obsidian/workspace-mobile.json",
        ".obsidian/plugins/*/data.json"
    )
    $trackedPrivateFiles = @($trackedPrivateFilesResult.Output | Where-Object {
        -not [string]::IsNullOrWhiteSpace($_) -and $_ -ne $sharedPluginData
    })
    if ($trackedPrivateFiles.Count -gt 0) {
        $ignoreFailure = $true
        $trackedPrivateFiles | ForEach-Object { Write-Log "Arquivo local sensível já rastreado pelo Git: $_" "ERROR" }
    }
    else {
        Write-Log "Nenhum workspace ou data.json privado de plugin está rastreado pelo Git." "OK"
    }
    if ($ignoreFailure) {
        throw "A proteção de arquivos locais do Obsidian está incompleta. Revise .gitignore sem incluir credenciais."
    }

    Write-Section "Plugin Obsidian Git"
    $pluginDirectory = Join-Path $repositoryPath ".obsidian\plugins\obsidian-git"
    $pluginRequiredFiles = @("manifest.json", "main.js", "data.json")
    $pluginReady = Test-Path -LiteralPath $pluginDirectory -PathType Container
    foreach ($pluginFile in $pluginRequiredFiles) {
        $pluginFilePath = Join-Path $pluginDirectory $pluginFile
        if (Test-Path -LiteralPath $pluginFilePath -PathType Leaf) {
            Write-Log "Plugin contém: $pluginFile" "OK"
        }
        else {
            $pluginReady = $false
            Write-Log "Plugin não contém: $pluginFile" "ERROR"
        }
    }

    $communityPluginsPath = Join-Path $repositoryPath ".obsidian\community-plugins.json"
    try {
        $communityPlugins = @(Get-Content -LiteralPath $communityPluginsPath -Raw -Encoding UTF8 | ConvertFrom-Json)
    }
    catch {
        throw "community-plugins.json não é um JSON válido: $($_.Exception.Message)"
    }
    if ($communityPlugins -contains "obsidian-git") {
        Write-Log "community-plugins.json referencia obsidian-git." "OK"
    }
    else {
        $pluginReady = $false
        Write-Log "community-plugins.json não referencia obsidian-git." "ERROR"
    }
    if (-not $pluginReady) {
        throw "O plugin obsidian-git não está completo no clone."
    }

    $pluginDataPath = Join-Path $pluginDirectory "data.json"
    try {
        $pluginSettings = Get-Content -LiteralPath $pluginDataPath -Raw -Encoding UTF8 | ConvertFrom-Json
    }
    catch {
        throw "O data.json compartilhado do obsidian-git não é um JSON válido: $($_.Exception.Message)"
    }
    $expectedPluginSettings = [ordered]@{
        autoPullOnBoot = $true
        autoSaveInterval = 0
        autoPushInterval = 0
        autoPullInterval = 0
        disablePush = $false
        pullBeforePush = $true
        syncMethod = "rebase"
    }
    foreach ($settingName in $expectedPluginSettings.Keys) {
        $settingProperty = $pluginSettings.PSObject.Properties[$settingName]
        $expectedValue = $expectedPluginSettings[$settingName]
        if ($null -eq $settingProperty -or $settingProperty.Value -ne $expectedValue) {
            $pluginReady = $false
            Write-Log "Configuração compartilhada divergente: $settingName deveria ser '$expectedValue'." "ERROR"
        }
        else {
            Write-Log "Configuração compartilhada: $settingName = $expectedValue" "OK"
        }
    }
    if (-not $pluginReady) {
        throw "A configuração compartilhada do obsidian-git não corresponde à baseline esperada."
    }
    Write-Log "data.json do obsidian-git está presente, revisado e compartilhado pelo Git." "OK"

    Write-Section "Status Git"
    $statusResult = Invoke-Git -GitPath $git -Arguments @("-C", $repositoryPath, "-c", "core.quotepath=false", "status", "--short", "--branch", "--untracked-files=all")
    if ($statusResult.Output.Count -eq 0) {
        Write-Log "Git não retornou linhas de status." "OK"
    }
    else {
        $statusResult.Output | ForEach-Object { Write-Log "git status: $_" }
    }
    $unexpectedUntracked = @($statusResult.Output | Where-Object { $_ -match "^\?\? " })
    if ($unexpectedUntracked.Count -gt 0) {
        Write-Log "Há $($unexpectedUntracked.Count) arquivo(s) untracked não ignorado(s). Revise-os manualmente; nada foi removido." "WARN"
        $unexpectedUntracked | ForEach-Object { Write-Log "untracked: $($_.Substring(3))" "WARN" }
    }
    else {
        Write-Log "Nenhum arquivo untracked inesperado foi encontrado." "OK"
    }

    Write-Section "Configuração manual no Obsidian"
    Write-Log "Abra a pasta como Vault: $repositoryPath"
    Write-Log "1. Saia do Restricted Mode, se ele estiver ativo."
    Write-Log "2. Confirme/ative Community Plugins e o plugin Obsidian Git."
    Write-Log "3. As preferências do Obsidian Git já vêm da baseline compartilhada em data.json."
    Write-Log "4. Confirme na interface: pull ao iniciar ON; rotinas automáticas OFF; push habilitado; sync por rebase."

    if ($OpenVault) {
        if ($obsidian) {
            Write-Log "Abrindo o Vault no Obsidian."
            $vaultUri = "obsidian://open?path=$([Uri]::EscapeDataString($repositoryPath))"
            Start-Process -FilePath $obsidian -ArgumentList @($vaultUri)
        }
        else {
            Write-Log "-OpenVault foi solicitado, mas o executável do Obsidian não foi encontrado." "WARN"
        }
    }

    Write-Section "Concluído"
    Write-Log "Bootstrap finalizado sem pull, reset, clean, commit ou push." "OK"
    Write-Log "Vault: $repositoryPath" "OK"
    Write-Log "Log UTF-8: $LogPath" "OK"
}
catch {
    Write-Log $_.Exception.Message "ERROR"
    Write-Log "Bootstrap interrompido com segurança. Consulte o log: $LogPath" "ERROR"
    exit 1
}
