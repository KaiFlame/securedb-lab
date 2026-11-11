# Windows PowerShell 5.1. Application dependencies run only in Linux containers.
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('up', 'test', 'down', 'diagnose', 'backup', 'restore', 'report', 'credentials')]
    [string]$Action = 'up',
    [ValidateSet('sql', 'nosql', 'both')]
    [string]$Database = 'both',
    [switch]$NoBrowser
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'
$script:ProjectRoot = Split-Path -Parent $PSScriptRoot
$script:DockerExe = $null
$script:ProjectName = 'securedb-lab'

function Get-LabDockerExecutable {
    $command = Get-Command docker.exe -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -ne $command) { return $command.Source }
    foreach ($base in @($env:ProgramFiles, $env:LOCALAPPDATA)) {
        if ([string]::IsNullOrWhiteSpace($base)) { continue }
        foreach ($relative in @('Docker\Docker\resources\bin\docker.exe', 'Programs\DockerDesktop\resources\bin\docker.exe')) {
            $candidate = Join-Path $base $relative
            if (Test-Path -LiteralPath $candidate -PathType Leaf) { return $candidate }
        }
    }
    throw 'Docker nao encontrado. Instale o Docker Desktop para Windows: https://docs.docker.com/desktop/setup/install/windows-install/ . Abra o programa e conclua a configuracao inicial.'
}

function Get-LabDockerDesktopExecutable {
    foreach ($base in @($env:ProgramFiles, $env:LOCALAPPDATA)) {
        if ([string]::IsNullOrWhiteSpace($base)) { continue }
        foreach ($relative in @('Docker\Docker\Docker Desktop.exe', 'Programs\DockerDesktop\Docker Desktop.exe')) {
            $candidate = Join-Path $base $relative
            if (Test-Path -LiteralPath $candidate -PathType Leaf) { return $candidate }
        }
    }
    return $null
}

function Invoke-LabDockerProbe {
    param([string]$Arguments, [int]$TimeoutMilliseconds = 5000)
    # Probe arguments are fixed strings, never command text supplied by users.
    $start = New-Object System.Diagnostics.ProcessStartInfo
    $start.FileName = $script:DockerExe
    $start.Arguments = $Arguments
    $start.UseShellExecute = $false
    $start.CreateNoWindow = $true
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $start
    try {
        $null = $process.Start()
        $stdout = $process.StandardOutput.ReadToEndAsync()
        $stderr = $process.StandardError.ReadToEndAsync()
        if (-not $process.WaitForExit($TimeoutMilliseconds)) {
            try { $process.Kill() } catch { }
            $null = $process.WaitForExit(1000)
            return [pscustomobject]@{ Succeeded = $false; Output = '' }
        }
        $output = $stdout.Result.Trim()
        $null = $stderr.Result
        return [pscustomobject]@{ Succeeded = ($process.ExitCode -eq 0); Output = $output }
    } finally {
        $process.Dispose()
    }
}

function Assert-LabDockerReady {
    $script:DockerExe = Get-LabDockerExecutable
    $compose = Invoke-LabDockerProbe -Arguments 'compose version --short' -TimeoutMilliseconds 10000
    if (-not $compose.Succeeded) { throw 'Docker Compose v2 ausente ou indisponivel. Atualize o Docker Desktop.' }
    $engine = Invoke-LabDockerProbe -Arguments 'info --format "{{.OSType}}"'
    if (-not $engine.Succeeded) {
        $desktop = Get-LabDockerDesktopExecutable
        if ($null -eq $desktop) { throw 'O motor Docker esta indisponivel. Abra o Docker Desktop e tente novamente.' }
        Write-Host 'Abrindo Docker Desktop; aguardando o motor por ate 120 segundos...'
        Start-Process -FilePath $desktop -WindowStyle Hidden | Out-Null
        $deadline = [DateTime]::UtcNow.AddSeconds(120)
        do {
            $remaining = [int][Math]::Max(0, ($deadline - [DateTime]::UtcNow).TotalMilliseconds)
            if ($remaining -le 0) { break }
            $engine = Invoke-LabDockerProbe -Arguments 'info --format "{{.OSType}}"' -TimeoutMilliseconds ([Math]::Min(5000, $remaining))
            if ($engine.Succeeded) { break }
            $remaining = [int][Math]::Max(0, ($deadline - [DateTime]::UtcNow).TotalMilliseconds)
            if ($remaining -gt 0) { Start-Sleep -Milliseconds ([Math]::Min(2000, $remaining)) }
        } while ([DateTime]::UtcNow -lt $deadline)
        if (-not $engine.Succeeded) { throw 'Docker nao ficou disponivel. Conclua a configuracao inicial no Docker Desktop e tente novamente.' }
    }
    if ($engine.Output -ne 'linux') { throw 'Selecione Linux containers no Docker Desktop e tente novamente.' }
}

function Invoke-LabDocker {
    param([string[]]$ArgumentList)
    # Native stderr is displayed normally; the explicit exit code determines failure.
    $ErrorActionPreference = 'Continue'
    & $script:DockerExe @ArgumentList
    $completed = $?
    $exitVariable = Get-Variable LASTEXITCODE -ErrorAction SilentlyContinue
    $code = $null
    if ($null -ne $exitVariable) { $code = $exitVariable.Value }
    if (-not $completed -and ($null -eq $code -or $code -eq 0)) {
        throw 'Nao foi possivel executar o Docker. Verifique sua instalacao e permissoes.'
    }
    if ($code -ne 0) { throw ('Docker falhou (codigo {0}). Consulte a mensagem acima.' -f $code) }
}

function Invoke-LabCompose {
    param([string[]]$ArgumentList)
    Invoke-LabDocker -ArgumentList (@('compose', '-p', $script:ProjectName, '-f', (Join-Path $script:ProjectRoot 'docker-compose.yml')) + $ArgumentList)
}

function Invoke-LabBootstrap {
    param([string[]]$ArgumentList)
    Invoke-LabDocker -ArgumentList (@('compose', '-p', ($script:ProjectName + '-bootstrap'), '-f', (Join-Path $script:ProjectRoot 'compose.bootstrap.yml')) + $ArgumentList)
}

function Get-LabWebPort {
    $value = $env:WEB_PORT
    if ([string]::IsNullOrWhiteSpace($value)) {
        $file = Join-Path $script:ProjectRoot '.env'
        if (Test-Path -LiteralPath $file -PathType Leaf) {
            foreach ($line in [System.IO.File]::ReadAllLines($file, [System.Text.Encoding]::UTF8)) {
                if ($line -match '^WEB_PORT=(.*)$') { $value = $Matches[1].Trim() }
            }
        }
    }
    if ([string]::IsNullOrWhiteSpace($value)) { $value = '8080' }
    $port = 0
    if (-not [int]::TryParse($value, [ref]$port) -or $port -lt 1024 -or $port -gt 65535) {
        throw 'WEB_PORT precisa ser um numero entre 1024 e 65535.'
    }
    return $port
}

function Write-LabJson {
    param([string]$Path, [object]$Value)
    $json = ConvertTo-Json -InputObject $Value -Depth 20
    $utf8WithoutBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $json + [Environment]::NewLine, $utf8WithoutBom)
}

function Get-LabInspectField {
    param([string]$Id, [string]$Field, [switch]$Network)
    $arguments = @('inspect', '--format', ('{{json ' + $Field + '}}'), $Id)
    if ($Network) { $arguments = @('network') + $arguments }
    $json = @(Invoke-LabDocker -ArgumentList $arguments) -join [Environment]::NewLine
    return ConvertFrom-Json -InputObject $json
}

function Invoke-LabDiagnostics {
    if (-not (Test-Path -LiteralPath (Join-Path $script:ProjectRoot '.env') -PathType Leaf)) {
        throw 'Configuracao ausente. Execute primeiro iniciar.cmd.'
    }
    $folder = Join-Path $script:ProjectRoot '.local\inspection'
    $null = New-Item -ItemType Directory -Path $folder -Force
    $receipt = Join-Path $script:ProjectRoot 'evidencias\environment.json'
    if (Test-Path -LiteralPath $receipt -PathType Leaf) { Remove-Item -LiteralPath $receipt -Force }
    foreach ($service in @('postgres', 'mongo')) {
        $id = (@(Invoke-LabCompose -ArgumentList @('ps', '-q', $service)) -join '').Trim()
        if ([string]::IsNullOrWhiteSpace($id)) { throw ('Conteiner ausente: ' + $service) }
        # Read only the requested observation fields, never Config.Env or full inspect.
        $record = [ordered]@{
            service = $service
            running = Get-LabInspectField -Id $id -Field '.State.Running'
            image = Get-LabInspectField -Id $id -Field '.Config.Image'
            port_bindings = Get-LabInspectField -Id $id -Field '.HostConfig.PortBindings'
            networks = Get-LabInspectField -Id $id -Field '.NetworkSettings.Networks'
        }
        Write-LabJson -Path (Join-Path $folder ($service + '.json')) -Value $record
    }
    $name = $script:ProjectName + '_data'
    $network = [ordered]@{
        Name = Get-LabInspectField -Id $name -Field '.Name' -Network
        Internal = Get-LabInspectField -Id $name -Field '.Internal' -Network
    }
    Write-LabJson -Path (Join-Path $folder 'network.json') -Value $network
    Invoke-LabBootstrap -ArgumentList @('run', '--rm', '--no-deps', '-T', 'bootstrap', 'diagnose')
}

function Initialize-Lab {
    Write-Host 'Preparando configuracao local, certificados e credenciais...'
    Invoke-LabBootstrap -ArgumentList @('build', 'bootstrap')
    Invoke-LabBootstrap -ArgumentList @('run', '--rm', '--no-deps', '-T', 'bootstrap', 'setup')
}

function Build-LabOps {
    Invoke-LabCompose -ArgumentList @('--profile', 'tools', 'build', 'ops')
}

function Invoke-LabOps {
    param([string[]]$ArgumentList)
    Invoke-LabCompose -ArgumentList (@('--profile', 'tools', 'run', '--rm', '--no-deps', '-T', 'ops') + $ArgumentList)
}

function Invoke-LabMain {
    param([string]$RequestedAction, [string]$RequestedDatabase = 'both', [switch]$SkipBrowser)
    Set-Location -LiteralPath $script:ProjectRoot
    if ([string]::IsNullOrWhiteSpace($env:COMPOSE_PROJECT_NAME)) { $env:COMPOSE_PROJECT_NAME = 'securedb-lab' }
    $script:ProjectName = $env:COMPOSE_PROJECT_NAME
    if ($script:ProjectName -notmatch '^[a-z0-9][a-z0-9_-]*$') { throw 'COMPOSE_PROJECT_NAME precisa conter letras minusculas, numeros, hifen ou sublinhado, com inicio alfanumerico.' }
    if ([string]::IsNullOrWhiteSpace($env:LOCAL_UID)) { $env:LOCAL_UID = '1000' }
    if ([string]::IsNullOrWhiteSpace($env:LOCAL_GID)) { $env:LOCAL_GID = '1000' }
    if ($RequestedAction -eq 'credentials') {
        $path = Join-Path $script:ProjectRoot '.local\ACESSO_LOCAL.txt'
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw 'Execute iniciar.cmd antes de consultar os acessos.' }
        Get-Content -LiteralPath $path -Encoding UTF8
        return
    }
    Assert-LabDockerReady
    if ($RequestedAction -ne 'up' -and -not (Test-Path -LiteralPath (Join-Path $script:ProjectRoot '.env') -PathType Leaf)) {
        throw 'Configuracao ausente. Execute primeiro iniciar.cmd.'
    }
    switch ($RequestedAction) {
        'up' {
            Initialize-Lab
            Invoke-LabCompose -ArgumentList @('config', '--quiet')
            Invoke-LabCompose -ArgumentList @('up', '-d', '--build', '--wait', '--wait-timeout', '300')
            Invoke-LabDiagnostics
            $url = 'http://localhost:' + (Get-LabWebPort)
            Write-Host ("`nAplicacao: {0}`nAcessos: .local\ACESSO_LOCAL.txt" -f $url)
            if (-not $SkipBrowser -and $env:LAB_NO_BROWSER -ne '1') { Start-Process $url | Out-Null }
        }
        'down' {
            Invoke-LabCompose -ArgumentList @('down')
            Write-Host 'Servicos parados. Dados e credenciais preservados.'
        }
        'diagnose' { Invoke-LabDiagnostics }
        'test' {
            Invoke-LabDiagnostics
            Build-LabOps
            Invoke-LabOps -ArgumentList @('pytest', 'tests', '-q', '-p', 'no:cacheprovider')
        }
        { $_ -in @('backup', 'restore') } {
            Build-LabOps
            Invoke-LabOps -ArgumentList @('python', 'scripts/backup_restore.py', '--database', $RequestedDatabase)
        }
        'report' {
            Build-LabOps
            Invoke-LabOps -ArgumentList @('python', 'scripts/report.py')
        }
        default { throw 'Acao invalida.' }
    }
}

# Dot-sourcing loads functions for source tests without starting Docker.
if ($MyInvocation.InvocationName -ne '.') {
    try {
        Invoke-LabMain -RequestedAction $Action -RequestedDatabase $Database -SkipBrowser:$NoBrowser
        exit 0
    } catch {
        Write-Host ("`nFalha: " + $_.Exception.Message) -ForegroundColor Red
        exit 1
    }
}
