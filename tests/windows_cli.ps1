# Source/behavior checks only. All Docker commands are mocked; no Docker engine is used.
[CmdletBinding()]
param([string]$OutputPath)

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'
if (-not [string]::IsNullOrWhiteSpace($OutputPath)) { $OutputPath = [System.IO.Path]::GetFullPath($OutputPath) }
$root = Split-Path -Parent $PSScriptRoot
$wrapper = Join-Path $root 'scripts\docker.ps1'
$tokens = $null
$parseErrors = $null
$null = [System.Management.Automation.Language.Parser]::ParseFile($wrapper, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count -ne 0) { throw ($parseErrors | Out-String) }

. $wrapper
$script:Checks = New-Object 'System.Collections.Generic.List[string]'
function Assert-Check {
    param([bool]$Condition, [string]$Name)
    if (-not $Condition) { throw ('FAIL: ' + $Name) }
    $script:Checks.Add($Name)
}

$originalLocation = Get-Location
$originalEnvironment = @{}
foreach ($name in @('WEB_PORT', 'LAB_NO_BROWSER', 'COMPOSE_PROJECT_NAME', 'LOCAL_UID', 'LOCAL_GID')) {
    $originalEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
}
$fixture = Join-Path ([System.IO.Path]::GetTempPath()) ('securedb-windows-cli-' + [Guid]::NewGuid().ToString('N'))
$null = New-Item -ItemType Directory -Path $fixture
$script:ProjectRoot = $fixture
$script:ProjectName = 'securedb-lab'
$env:WEB_PORT = $null
$env:LAB_NO_BROWSER = '1'
$env:COMPOSE_PROJECT_NAME = 'securedb-lab'

try {
    Assert-Check ($PSVersionTable.PSVersion.Major -ge 5) 'PowerShell 5.1 parser accepts wrapper source'
    Assert-Check ((Get-LabWebPort) -eq 8080) 'Default port is 8080'
    [System.IO.File]::WriteAllText((Join-Path $fixture '.env'), "WEB_PORT=18081`n", (New-Object System.Text.UTF8Encoding($false)))
    Assert-Check ((Get-LabWebPort) -eq 18081) 'Preserved .env port is displayed'
    $env:WEB_PORT = '18082'
    Assert-Check ((Get-LabWebPort) -eq 18082) 'Host port has Compose precedence'
    $env:WEB_PORT = '80'
    $rejected = $false
    try { $null = Get-LabWebPort } catch { $rejected = $true }
    Assert-Check $rejected 'Invalid port is rejected'
    $env:WEB_PORT = $null

    $unicode = 'observa' + [char]0x00E7 + [char]0x00E3 + 'o'
    $jsonPath = Join-Path $fixture 'encoding.json'
    Write-LabJson -Path $jsonPath -Value @{ name = $unicode }
    $bytes = [System.IO.File]::ReadAllBytes($jsonPath)
    Assert-Check (-not ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)) 'Observation JSON has no UTF-8 BOM'
    $decoded = ConvertFrom-Json -InputObject ([System.IO.File]::ReadAllText($jsonPath, [System.Text.Encoding]::UTF8))
    Assert-Check ($decoded.name -eq $unicode) 'Observation JSON preserves UTF-8 text'

    # Exercise native exit handling with cmd.exe only, never Docker.
    $script:DockerExe = $env:ComSpec
    $probe = Invoke-LabDockerProbe -Arguments '/d /c echo linux' -TimeoutMilliseconds 5000
    Assert-Check ($probe.Succeeded -and $probe.Output -eq 'linux') 'Bounded native probe captures its output'
    $rejected = $false
    try { Invoke-LabDocker -ArgumentList @('/d', '/c', 'exit', '7') } catch { $rejected = $true }
    Assert-Check $rejected 'Native nonzero exit becomes a failure'
    Invoke-LabDocker -ArgumentList @('/d', '/c', 'exit', '0')
    $script:DockerExe = Join-Path $fixture 'missing-docker.exe'
    $rejected = $false
    try { Invoke-LabDocker -ArgumentList @('version') 2>$null } catch { $rejected = $true }
    Assert-Check $rejected 'Launch failure cannot inherit a previous successful exit code'

    # The remainder uses only fake Docker responses in memory.
    $script:DockerCalls = New-Object 'System.Collections.Generic.List[string]'
    $script:BootstrapCalls = New-Object 'System.Collections.Generic.List[string]'
    function Invoke-LabDocker {
        param([string[]]$ArgumentList)
        $script:DockerCalls.Add(($ArgumentList -join '|'))
        $isNetwork = $ArgumentList[0] -eq 'network'
        $offset = 0
        if ($isNetwork) { $offset = 1 }
        if ($ArgumentList[$offset] -ne 'inspect') { throw 'Unexpected fake Docker call.' }
        switch ($ArgumentList[$offset + 2]) {
            '{{json .State.Running}}' { 'true' }
            '{{json .Config.Image}}' { '"official:test"' }
            '{{json .HostConfig.PortBindings}}' { 'null' }
            '{{json .NetworkSettings.Networks}}' { '{"securedb-lab_data":{"IPAddress":"172.29.74.2"}}' }
            '{{json .Name}}' { '"securedb-lab_data"' }
            '{{json .Internal}}' { 'true' }
            default { throw 'Unexpected fake inspect field.' }
        }
    }
    function Invoke-LabCompose {
        param([string[]]$ArgumentList)
        if ($ArgumentList[0] -eq 'ps') { return ('fake-' + $ArgumentList[2]) }
        throw 'Unexpected fake Compose call.'
    }
    function Invoke-LabBootstrap {
        param([string[]]$ArgumentList)
        $script:BootstrapCalls.Add(($ArgumentList -join '|'))
    }
    Invoke-LabDiagnostics
    $pg = ConvertFrom-Json -InputObject ([System.IO.File]::ReadAllText((Join-Path $fixture '.local\inspection\postgres.json')))
    $mongo = ConvertFrom-Json -InputObject ([System.IO.File]::ReadAllText((Join-Path $fixture '.local\inspection\mongo.json')))
    $network = ConvertFrom-Json -InputObject ([System.IO.File]::ReadAllText((Join-Path $fixture '.local\inspection\network.json')))
    Assert-Check ($pg.service -eq 'postgres' -and $mongo.service -eq 'mongo' -and $pg.running -eq $true) 'Both database observations use expected fields'
    Assert-Check ($null -eq $pg.port_bindings -and $network.Internal -eq $true) 'Network and port observation types match bootstrap contract'
    Assert-Check ($script:DockerCalls.Count -eq 10 -and -not (($script:DockerCalls -join ' ') -match 'Config\.Env')) 'Diagnostics reads only ten scoped inspect fields'
    Assert-Check ($script:BootstrapCalls[0] -eq 'run|--rm|--no-deps|-T|bootstrap|diagnose') 'Diagnostics delegates validation to bootstrap'
    Assert-Check (-not (Test-Path -LiteralPath (Join-Path $fixture 'evidencias\environment.json'))) 'Fake diagnostics does not fabricate an environment PASS'

    $script:Plan = New-Object 'System.Collections.Generic.List[string]'
    function Assert-LabDockerReady { $script:Plan.Add('ready') }
    function Initialize-Lab { $script:Plan.Add('setup') }
    function Invoke-LabDiagnostics { $script:Plan.Add('diagnose') }
    function Invoke-LabCompose {
        param([string[]]$ArgumentList)
        $script:Plan.Add('compose|' + ($ArgumentList -join '|'))
    }
    Invoke-LabMain -RequestedAction up -SkipBrowser
    Assert-Check (($script:Plan -join ';') -eq 'ready;setup;compose|config|--quiet;compose|up|-d|--build|--wait|--wait-timeout|300;diagnose') 'Up orders setup, readiness and diagnosis correctly'
    $script:Plan.Clear()
    Invoke-LabMain -RequestedAction test
    Assert-Check (($script:Plan -join ';') -eq 'ready;diagnose;compose|--profile|tools|build|ops;compose|--profile|tools|run|--rm|--no-deps|-T|ops|pytest|tests|-q|-p|no:cacheprovider') 'Test builds and invokes only container dependencies'
    foreach ($case in @(@{ Action = 'backup'; Database = 'sql' }, @{ Action = 'restore'; Database = 'nosql' })) {
        $script:Plan.Clear()
        Invoke-LabMain -RequestedAction $case.Action -RequestedDatabase $case.Database
        Assert-Check (($script:Plan -join ';').EndsWith('ops|python|scripts/backup_restore.py|--database|' + $case.Database)) ($case.Action + ' forwards its database selection')
    }
    $script:Plan.Clear()
    Invoke-LabMain -RequestedAction report
    Assert-Check (($script:Plan -join ';').EndsWith('ops|python|scripts/report.py')) 'Report executes Python only inside ops'
    $script:Plan.Clear()
    Invoke-LabMain -RequestedAction down
    Assert-Check (($script:Plan -join ';') -eq 'ready;compose|down') 'Down preserves named volumes'
    $script:Plan.Clear()
    Invoke-LabMain -RequestedAction diagnose
    Assert-Check (($script:Plan -join ';') -eq 'ready;diagnose') 'Diagnose executes the scoped observation flow'
    [System.IO.File]::WriteAllText((Join-Path $fixture '.local\ACESSO_LOCAL.txt'), 'synthetic credentials fixture')
    $script:Plan.Clear()
    $access = Invoke-LabMain -RequestedAction credentials
    Assert-Check ($access -eq 'synthetic credentials fixture' -and $script:Plan.Count -eq 0) 'Credentials can be read with Docker stopped'

    foreach ($case in @(@{ File = 'iniciar.cmd'; Action = 'up' }, @{ File = 'parar.cmd'; Action = 'down' }, @{ File = 'testar.cmd'; Action = 'test' })) {
        $body = [System.IO.File]::ReadAllText((Join-Path $root $case.File))
        Assert-Check ($body.Contains('-Action ' + $case.Action) -and $body.Contains('exit /b %LAB_EXIT%') -and $body.Contains('pause')) ($case.File + ' selects its action, preserves errors and propagates exit status')
    }
    $body = [System.IO.File]::ReadAllText($wrapper)
    Assert-Check ($body.Contains('Programs\DockerDesktop\resources\bin\docker.exe') -and $body.Contains('Docker\Docker\resources\bin\docker.exe')) 'CLI discovery includes per-user and system Docker Desktop installations'
    Assert-Check ($body.Contains('Programs\DockerDesktop\Docker Desktop.exe') -and $body.Contains('Docker\Docker\Docker Desktop.exe')) 'Desktop discovery includes both official installation locations'
    Assert-Check ($body.Contains('-WindowStyle Hidden') -and $body.Contains('AddSeconds(120)')) 'Desktop startup uses a hidden launch and bounded wait'
    Assert-Check (-not ($body -match 'Set-ExecutionPolicy|netsh|Set-NetFirewall|wsl\.exe')) 'Wrapper contains no system policy, WSL or firewall mutation'

    $result = [ordered]@{
        check = 'windows-powershell-cli-source-and-mocked-behavior'
        result = 'PASS'
        powershell = $PSVersionTable.PSVersion.ToString()
        checks = $script:Checks.Count
        observations = @($script:Checks)
        scope = 'Windows PowerShell parser, JSON encoding, native exit handling and mocked command flow only. No Docker engine or real container execution.'
    }
    if (-not [string]::IsNullOrWhiteSpace($OutputPath)) {
        Write-LabJson -Path ([System.IO.Path]::GetFullPath($OutputPath)) -Value $result
    }
    ConvertTo-Json -InputObject $result -Depth 5
} finally {
    Set-Location -LiteralPath $originalLocation
    foreach ($name in $originalEnvironment.Keys) {
        [Environment]::SetEnvironmentVariable($name, $originalEnvironment[$name], 'Process')
    }
}
