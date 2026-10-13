# Offline tests; no Windows, network, Go compiler, or retail assets required.
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$installer = Join-Path (Split-Path $PSScriptRoot -Parent) 'static/install.ps1'
$tokens = $null
$errors = $null
[void][Management.Automation.Language.Parser]::ParseFile($installer, [ref]$tokens, [ref]$errors)
if ($errors.Count) { throw ($errors | Out-String) }
. $installer

function Assert-Throws([scriptblock]$Action, [string]$Message) {
    $threw = $false
    try { & $Action | Out-Null } catch { $threw = $true }
    if (!$threw) { throw "Expected rejection: $Message" }
}
function Assert-Equal($Actual, $Expected, [string]$Message) {
    if ($Actual -cne $Expected) { throw "$Message (actual: $Actual; expected: $Expected)" }
}

Assert-Equal (Resolve-NanolatheWindowsArchitecture @(9) $true) 'amd64' 'Native x64 selection'
Assert-Equal (Resolve-NanolatheWindowsArchitecture @(12) $true) 'arm64' 'Native ARM64 selection, including emulated shells'
Assert-Equal (Resolve-NanolatheWindowsArchitecture @(12, 12) $true) 'arm64' 'Multiple ARM64 processors'
Assert-Throws { Resolve-NanolatheWindowsArchitecture @(9) $false } '32-bit PowerShell'
Assert-Throws { Resolve-NanolatheWindowsArchitecture @() $true } 'missing CPU information'
Assert-Throws { Resolve-NanolatheWindowsArchitecture @(0) $true } 'unsupported CPU'
Assert-Throws { Resolve-NanolatheWindowsArchitecture @(9, 12) $true } 'inconsistent CPU information'

$hash = 'a' * 64
$manifest = @"
version=alpha-1
source_revision=$('b' * 40)
source_tar_sha256=$hash
source_zip_sha256=$hash
go_version=1.25.0
go_darwin_arm64_sha256=$hash
go_darwin_amd64_sha256=$hash
go_linux_amd64_sha256=$hash
go_linux_arm64_sha256=$hash
go_windows_amd64_sha256=$hash
go_windows_arm64_sha256=$hash
"@
Assert-Equal (Read-NanolatheManifest $manifest).version 'alpha-1' 'Valid manifest'
Assert-Equal (Read-NanolatheManifest ($manifest.Replace("`n", "`r`n"))).go_version '1.25.0' 'CRLF manifest'
Assert-Equal (Read-NanolatheManifest ($manifest + "`nfuture_key=`$(throw 'must stay inert')")).future_key "`$(throw 'must stay inert')" 'Unknown keys remain data'
Assert-Throws { Read-NanolatheManifest ($manifest + "`nversion=evil") } 'duplicate key'
Assert-Throws { Read-NanolatheManifest ($manifest + "`nthrow 'execute'") } 'code instead of key=value'
Assert-Throws { Read-NanolatheManifest ($manifest.Replace('alpha-1', '../other')) } 'path traversal'
Assert-Throws { Read-NanolatheManifest ($manifest.Replace('alpha-1', "`$(throw 'execute')")) } 'code in version'
Assert-Throws { Read-NanolatheManifest ($manifest.Replace(('b' * 40), ('B' * 40))) } 'uppercase revision'
Assert-Throws { Read-NanolatheManifest ($manifest.Replace('go_version=1.25.0', 'go_version=latest')) } 'unpinned toolchain'
Assert-Throws { Read-NanolatheManifest ($manifest.Replace("source_zip_sha256=$hash", 'source_zip_sha256=abc')) } 'bad digest'
Assert-Throws { Read-NanolatheManifest ($manifest.Replace("source_tar_sha256=$hash", '')) } 'missing digest'

$base = Join-Path ([IO.Path]::GetTempPath()) ("nanolathe-test O'Brien & `$x; [alpha] " + [guid]::NewGuid().ToString('N'))
try {
    [void][IO.Directory]::CreateDirectory((Join-Path $base 'releases'))
    Add-Type -AssemblyName System.IO.Compression
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = Join-Path $base 'authored.zip'
    $zip = [IO.Compression.ZipFile]::Open($archive, [IO.Compression.ZipArchiveMode]::Create)
    try {
        $entry = $zip.CreateEntry("nested O'Brien & [alpha]/sentinel.txt")
        $writer = New-Object IO.StreamWriter($entry.Open())
        try { $writer.Write('authored archive content') } finally { $writer.Dispose() }
    } finally { $zip.Dispose() }
    $unpack = Join-Path $base 'extracted [alpha]'
    Expand-NanolatheArchive $archive $unpack
    Assert-Equal ([IO.File]::ReadAllText((Join-Path $unpack "nested O'Brien & [alpha]/sentinel.txt"))) 'authored archive content' 'ZIP extraction round trip'
    $old = Join-Path (Join-Path $base 'releases') 'old-release'
    [void][IO.Directory]::CreateDirectory($old)
    [IO.File]::WriteAllText((Join-Path $old 'nanolathe.exe'), 'working binary')
    Write-NanolatheData (Join-Path $base 'current.txt') 'old-release'
    $stage = Join-Path $base 'staging'
    [void][IO.Directory]::CreateDirectory($stage)
    $binary = Join-Path $stage 'nanolathe.exe'
    [IO.File]::WriteAllText($binary, 'unverified binary')
    $digest = (Get-FileHash -LiteralPath $binary -Algorithm SHA256).Hash
    Test-NanolatheChecksum $binary $digest
    Assert-Throws { Test-NanolatheChecksum $binary ('0' * 64) } 'checksum mismatch'
    Assert-Throws { Publish-NanolatheRelease $base $stage 'new-release' { throw 'failed build or --help' } } 'failed verification'
    Assert-Equal ([IO.File]::ReadAllText((Join-Path $base 'current.txt'))) 'old-release' 'Failure preserves active release'
    Assert-Equal ([IO.File]::ReadAllText((Join-Path $old 'nanolathe.exe'))) 'working binary' 'Failure preserves old binary'
    Assert-Throws { Publish-NanolatheRelease $base $stage 'new-release' {} { throw 'shortcut creation failed' } } 'failed shortcut preparation'
    Assert-Equal ([IO.File]::ReadAllText((Join-Path $base 'current.txt'))) 'old-release' 'Shortcut failure preserves active release'
    Assert-Equal ([IO.File]::ReadAllText((Join-Path $old 'nanolathe.exe'))) 'working binary' 'Shortcut failure preserves old binary'
    $iconSource = Join-Path $PSScriptRoot 'installer-fixtures\windows\Nanolathe.ico'
    [IO.File]::Copy($iconSource, (Join-Path $stage 'Nanolathe.ico'))
    $shortcut = [pscustomobject]@{ TargetPath = ''; Arguments = ''; WorkingDirectory = ''; WindowStyle = 7; Description = ''; IconLocation = '' }
    $systemRootBefore = $env:SystemRoot
    if ([string]::IsNullOrEmpty($env:SystemRoot)) { $env:SystemRoot = Join-Path $base 'authored Windows' }
    try {
        $published = Publish-NanolatheRelease $base $stage 'new-release' {
            param($candidate)
            if ([IO.File]::ReadAllText($candidate) -cne 'unverified binary') { throw 'Wrong candidate' }
            Write-Output 'Authored --help output'
        } {
            param($destination)
            Set-NanolatheShortcutProperties $shortcut $base $destination
        }
    } finally { $env:SystemRoot = $systemRootBefore }
    Assert-Equal ([IO.File]::ReadAllText((Join-Path $base 'current.txt'))) 'new-release' 'Success switches active release'
    Assert-Equal ([IO.File]::ReadAllText((Join-Path $old 'nanolathe.exe'))) 'working binary' 'Success retains previous binary'
    Assert-Equal $published (Join-Path (Join-Path $base 'releases') 'new-release') 'Published directory'
    Assert-Equal $shortcut.WindowStyle 1 'Start Menu opens a normal window'
    Assert-Equal $shortcut.Arguments.Contains('-WindowStyle Normal') $true 'PowerShell opens a normal window'
    $iconPath = $shortcut.IconLocation.Substring(0, $shortcut.IconLocation.LastIndexOf(','))
    Assert-Equal ([IO.Path]::GetDirectoryName($iconPath)) $published 'Shortcut icon belongs to the published release'
    Assert-Equal $shortcut.IconLocation.Substring($shortcut.IconLocation.LastIndexOf(',')) ',0' 'Shortcut selects the ICO image'
    Assert-Equal (Test-Path -LiteralPath $stage) $false 'Temporary stage was removed by promotion'
    Test-NanolatheChecksum $iconPath (Get-FileHash -LiteralPath $iconSource -Algorithm SHA256).Hash
    # On native Windows, prove WSH persists the icon on the actual shortcut,
    # and that recreating it points to the updated release's surviving icon.
    if ([Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT) {
        Add-Type -AssemblyName System.Drawing
        $nativeIcon = New-Object Drawing.Icon($iconPath)
        try { if ($nativeIcon.Width -le 0) { throw 'Windows could not load the icon.' } }
        finally { $nativeIcon.Dispose() }
        $shell = New-Object -ComObject WScript.Shell
        try {
            $shortcutPath = Join-Path $base 'Nanolathe.lnk'
            $nativeShortcut = $shell.CreateShortcut($shortcutPath)
            Set-NanolatheShortcutProperties $nativeShortcut $base $published
            $nativeShortcut.Save()
            Assert-Equal ($shell.CreateShortcut($shortcutPath)).IconLocation $shortcut.IconLocation 'Saved Start Menu icon'
            Assert-Equal ($shell.CreateShortcut($shortcutPath)).WindowStyle 1 'Saved Start Menu shortcut requests a normal window'
            $next = Join-Path (Join-Path $base 'releases') 'next-release'
            [void][IO.Directory]::CreateDirectory($next)
            [IO.File]::Copy($iconSource, (Join-Path $next 'Nanolathe.ico'))
            $nativeShortcut.WindowStyle = 7
            Set-NanolatheShortcutProperties $nativeShortcut $base $next
            $nativeShortcut.Save()
            Assert-Equal ($shell.CreateShortcut($shortcutPath)).IconLocation ((Join-Path $next 'Nanolathe.ico') + ',0') 'Update refreshes the same shortcut icon'
            Assert-Equal ($shell.CreateShortcut($shortcutPath)).WindowStyle 1 'Update restores a normal shortcut window'
        } finally { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($shell) }
    }

    $launcher = Get-NanolatheLauncher
    [void][Management.Automation.Language.Parser]::ParseInput($launcher, [ref]$tokens, [ref]$errors)
    if ($errors.Count) { throw ($errors | Out-String) }
    # Run the encoded shortcut command against an authored launcher, proving the
    # base path survives spaces, apostrophes, brackets and shell metacharacters.
    [IO.File]::WriteAllText((Join-Path $published 'launch.ps1'), 'param($Base); $Base')
    $arguments = $shortcut.Arguments
    $encoded = ($arguments -split ' ')[-1]
    $command = [Text.Encoding]::Unicode.GetString([Convert]::FromBase64String($encoded))
    Assert-Equal (& ([scriptblock]::Create($command))) $base 'Shortcut literal path round trip'
    # A real child host with -NonInteractive must never display an update UI.
    $installerLiteral = "'" + $installer.Replace("'", "''") + "'"
    $noninteractiveCommand = ". $installerLiteral; if (Confirm-NanolatheUpdate 'alpha-1') { throw 'Noninteractive update accepted.' }"
    $noninteractiveEncoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($noninteractiveCommand))
    & (Get-Process -Id $PID).Path -NoProfile -NonInteractive -EncodedCommand $noninteractiveEncoded
    Assert-Equal $LASTEXITCODE 0 'Noninteractive host keeps current version without prompting'

    # Exercise the emitted launcher with authored downloads and a native-game
    # command seam. No network request, native game, or dialog runs in this test.
    $updateTest = @{
        Mode = 'unchanged'; Accept = $false; Downloads = @(); Offers = 0
        CurrentLaunches = 0; NewLaunches = 0; Installed = $false
        Root = (Join-Path $base 'game assets'); Base = $base
    }
    [void][IO.Directory]::CreateDirectory($updateTest.Root)
    [void][IO.Directory]::CreateDirectory((Join-Path $base 'logs'))
    $authoredInstaller = @'
param([switch]$NoRun)
if (!$NoRun) { throw 'Update must not launch from the installer.' }
if ($env:NANOLATHE_INSTALL_DIR -cne $updateTest.Base) { throw 'Wrong update installation base.' }
$updateTest.Installed = $true
$ErrorActionPreference = 'SilentlyContinue'
$ProgressPreference = 'Continue'
if ($updateTest.Mode -eq 'failed') { throw 'Authored build failed.' }
$destination = Join-Path (Join-Path $env:NANOLATHE_INSTALL_DIR 'releases') 'updated-release'
[void][IO.Directory]::CreateDirectory($destination)
[IO.File]::WriteAllText((Join-Path $destination 'nanolathe.exe'), 'authored new binary')
[IO.File]::WriteAllText((Join-Path $destination 'launch.ps1'), @"
param([string]`$Base, [string]`$Root)
if (`$env:NANOLATHE_SKIP_UPDATE_CHECK -ne '1') { throw 'Missing relaunch guard.' }
if (`$Base -cne `$updateTest.Base -or `$Root -cne `$updateTest.Root) { throw 'Relaunch lost original paths.' }
`$updateTest.NewLaunches++
if (`$updateTest.Mode -eq 'new-game-failed') { throw 'Authored new game failed.' }
"@)
[IO.File]::WriteAllText((Join-Path $env:NANOLATHE_INSTALL_DIR 'current.txt'), 'updated-release')
'@
    # BOM + CRLF detects hashing after decode/reencode instead of the raw file.
    $installerBytes = [byte[]](@(239, 187, 191) + [Text.Encoding]::UTF8.GetBytes($authoredInstaller.Replace("`n", "`r`n")))
    $authoredPath = Join-Path $base 'authored-installer.ps1'
    [IO.File]::WriteAllBytes($authoredPath, $installerBytes)
    $installerHash = (Get-FileHash -LiteralPath $authoredPath -Algorithm SHA256).Hash
    $updateTest.Manifest = $manifest + "`ninstaller_ps1_sha256=$installerHash"
    function Get-NanolatheUpdateDownload([string]$Url, [string]$Path, [int]$TimeoutSeconds, [string]$Accept = 'application/octet-stream') {
        Assert-Equal ($updateTest.Messages -contains 'Checking for Nanolathe updates...') $true 'Update feedback precedes network work'
        $updateTest.Downloads += $Url
        if ($Url -ceq 'https://nanolathe.gg/install/release.txt') {
            Assert-Equal $TimeoutSeconds 3 'Manifest wait is bounded'
            if ($updateTest.Mode -eq 'offline') { throw 'Authored network unavailable.' }
            $text = $updateTest.Manifest
            if ($updateTest.Mode -eq 'unchanged') { $text = $text.Replace(('c' * 40), ('b' * 40)) }
            if ($updateTest.Mode -eq 'malformed') { $text += "`nversion=duplicate" }
            if ($updateTest.Mode -eq 'missing-hash') { $text = $text.Replace("installer_ps1_sha256=$installerHash", 'future=1') }
            if ($updateTest.Mode -eq 'bad-hash') { $text = $text.Replace($installerHash, ('0' * 64)) }
            [IO.File]::WriteAllText($Path, $text)
        } elseif ($Url -ceq 'https://api.github.com/repos/nanolathe-gg/nanolathe/commits/main') {
            Assert-Equal $TimeoutSeconds 3 'Main lookup is bounded'
            Assert-Equal $Accept 'application/vnd.github.sha' 'Request the plain commit ID'
            if ($updateTest.Mode -eq 'main-offline') { throw 'GitHub unavailable.' }
            $revision = 'c' * 40
            if ($updateTest.Mode -eq 'unchanged') { $revision = 'd' * 40 }
            if ($updateTest.Mode -eq 'invalid-main') { $revision = 'not-a-commit' }
            [IO.File]::WriteAllText($Path, $revision)
        } elseif ($Url -ceq 'https://nanolathe.gg/install.ps1') {
            Assert-Equal $TimeoutSeconds 60 'Installer download is bounded'
            [IO.File]::WriteAllBytes($Path, $installerBytes)
        } else { throw "Unexpected update URL: $Url" }
    }
    function Confirm-NanolatheUpdate([string]$Version) {
        Assert-Equal $Version ('main-' + ('c' * 12)) 'Main change is offered with unchanged website manifest'
        $updateTest.Offers++
        return $updateTest.Accept
    }
    function Invoke-TestGame {
        if ($args[0] -eq '--check-install') {
            Assert-Equal $args[2] $updateTest.Root 'Game root validation keeps the original root'
        } elseif ($args[0] -eq '--root') {
            Assert-Equal $args[1] $updateTest.Root 'Current launch keeps original root'
            Assert-Equal $args[2] '--save-dir' 'Current launch keeps save directory option'
            Assert-Equal $args[3] (Join-Path $base 'saves') 'Current launch keeps save directory'
            Assert-Equal $env:NANOLATHE_SETTINGS (Join-Path $base 'settings.json') 'Current launch keeps settings'
            $updateTest.CurrentLaunches++
        } else { throw 'Unexpected game invocation.' }
        $global:LASTEXITCODE = 0
    }
    function Read-Host { return '' }
    function Write-Host([string]$Object) { $updateTest.Messages += $Object }
    $testLauncher = (Get-NanolatheLauncher).Replace('& $exe ', '& Invoke-TestGame ')
    $environmentBefore = @{}
    foreach ($key in @('NANOLATHE_INSTALL_DIR', 'NANOLATHE_SKIP_UPDATE_CHECK', 'NANOLATHE_SETTINGS')) {
        $environmentBefore[$key] = [Environment]::GetEnvironmentVariable($key, 'Process')
        [Environment]::SetEnvironmentVariable($key, 'authored-existing-value', 'Process')
    }
    try {
        foreach ($mode in @('unchanged', 'offline', 'main-offline', 'invalid-main', 'malformed', 'missing-hash', 'decline', 'bad-hash', 'failed', 'accepted', 'new-game-failed', 'skip')) {
            $updateTest.Mode = $mode
            $updateTest.Accept = $mode -notin @('unchanged', 'offline', 'malformed', 'missing-hash', 'decline')
            $updateTest.Downloads = @()
            $updateTest.Messages = @()
            $updateTest.Offers = 0
            $updateTest.Installed = $false
            $updateTest.CurrentLaunches = 0
            $updateTest.NewLaunches = 0
            [IO.File]::WriteAllText((Join-Path $old 'release.txt'), $manifest)
            [IO.File]::WriteAllText((Join-Path $old 'source-revision'), ('d' * 40))
            Write-NanolatheData (Join-Path $base 'current.txt') 'old-release'
            $skipValue = 'authored-existing-value'
            if ($mode -eq 'skip') { $skipValue = '1' }
            [Environment]::SetEnvironmentVariable('NANOLATHE_SKIP_UPDATE_CHECK', $skipValue, 'Process')
            $errorBefore = $ErrorActionPreference
            $progressBefore = $ProgressPreference
            if ($mode -eq 'new-game-failed') {
                Assert-Throws { & ([scriptblock]::Create($testLauncher)) -Base $base -Root $updateTest.Root } 'New-game failure must not fall back and launch twice'
            } else { & ([scriptblock]::Create($testLauncher)) -Base $base -Root $updateTest.Root }
            Assert-Equal $ErrorActionPreference $errorBefore "$mode restores error preference"
            Assert-Equal $ProgressPreference $progressBefore "$mode restores progress preference"
            Assert-Equal $env:NANOLATHE_INSTALL_DIR 'authored-existing-value' "$mode restores installation environment"
            Assert-Equal $env:NANOLATHE_SKIP_UPDATE_CHECK $skipValue "$mode restores skip environment"
            Assert-Equal $env:NANOLATHE_SETTINGS 'authored-existing-value' "$mode restores settings environment"
            $expectedOffers = [int]($mode -in @('decline', 'bad-hash', 'failed', 'accepted', 'new-game-failed'))
            Assert-Equal $updateTest.Offers $expectedOffers "$mode update offers"
            $expectedDownloads = [int]($mode -ne 'skip') + [int]($mode -notin @('skip', 'offline', 'malformed')) + [int]($mode -in @('bad-hash', 'failed', 'accepted', 'new-game-failed'))
            Assert-Equal $updateTest.Downloads.Count $expectedDownloads "$mode download count"
            Assert-Equal $updateTest.Installed ($mode -in @('failed', 'accepted', 'new-game-failed')) "$mode only executes a verified installer"
            $newLaunches = [int]($mode -in @('accepted', 'new-game-failed'))
            Assert-Equal $updateTest.NewLaunches $newLaunches "$mode new launch count"
            Assert-Equal $updateTest.CurrentLaunches (1 - $newLaunches) "$mode current launch count"
            if (!$newLaunches) {
                Assert-Equal ([IO.File]::ReadAllText((Join-Path $base 'current.txt'))) 'old-release' "$mode retains selected release"
            }
        }
    } finally {
        foreach ($key in $environmentBefore.Keys) { [Environment]::SetEnvironmentVariable($key, $environmentBefore[$key], 'Process') }
        Remove-Item function:Write-Host
    }

    # Issue #112: exercise the generated launcher's real selection loop, both
    # directly (post-install) and through the encoded Start Menu command. Only
    # native game calls and console input are authored; any dialog is a failure.
    & {
        $firstRoot = Join-Path $base 'retail game'
        $secondRoot = Join-Path $base "TA O'Brien & `$literal; [custom]"
        $unusableRoot = Join-Path $base 'incomplete game'
        foreach ($folder in @($firstRoot, $secondRoot, $unusableRoot)) { [void][IO.Directory]::CreateDirectory($folder) }
        $remembered = Join-Path $base 'root.txt'
        $selection = @{}
        function Add-Type { $selection.Dialogs++; throw 'Game-folder selection must not open a dialog.' }
        function Read-Host([string]$Prompt) {
            if ($Prompt -eq 'Press Enter to close') { return '' }
            $selection.Prompts += $Prompt
            if ($selection.Answers.Count -eq 0) { throw 'Unexpected selection prompt.' }
            return $selection.Answers.Dequeue()
        }
        function Write-Host([string]$Object) { $selection.Messages += $Object }
        function Invoke-SelectionGame {
            $global:LASTEXITCODE = 0
            if ($args[0] -eq '--list-installs') {
                Assert-Equal $selection.Messages[-1] 'Searching for Total Annihilation installations...' 'Discovery feedback precedes native scan'
                $selection.Discoveries++
                return $selection.Candidates
            }
            if ($args[0] -eq '--check-install') {
                Assert-Equal $selection.Messages[-1] "Checking Total Annihilation game data: $($args[2])" 'Validation feedback precedes native check'
                $selection.Checks += $args[2]
                if ($args[2] -eq $unusableRoot) { $global:LASTEXITCODE = 1; return 'Authored unusable game data.' }
                Assert-Equal ($args[2] -in @($firstRoot, $secondRoot)) $true 'Only the chosen folder is validated'
                return
            }
            Assert-Equal $args[0] '--root' 'Game starts with one selected root'
            Assert-Equal $args.Count 4 'Selection never overlays installations'
            $selection.Launches += $args[1]
        }
        $selectionLauncher = (Get-NanolatheLauncher).Replace('& $exe ', '& Invoke-SelectionGame ')
        [IO.File]::WriteAllText((Join-Path $old 'launch.ps1'), $selectionLauncher)
        Write-NanolatheData (Join-Path $base 'current.txt') 'old-release'
        $shortcutCommand = [Text.Encoding]::Unicode.GetString([Convert]::FromBase64String(((Get-NanolatheLaunchCommand $base) -split ' ')[-1]))
        $skipBefore = $env:NANOLATHE_SKIP_UPDATE_CHECK
        $settingsBefore = $env:NANOLATHE_SETTINGS
        $env:NANOLATHE_SKIP_UPDATE_CHECK = '1'
        $env:NANOLATHE_SETTINGS = 'authored-settings-before-selection'
        try {
            $cases = @(
                @{ Name = 'post-install number'; Candidates = @($firstRoot, $secondRoot); Answers = @('2'); Expected = $secondRoot },
                @{ Name = 'shortcut number'; Candidates = @($firstRoot, $secondRoot); Answers = @('1'); Expected = $firstRoot; Shortcut = $true },
                @{ Name = 'bad numbers retry'; Candidates = @($firstRoot, $secondRoot); Answers = @('0', '3', '999999999999999999999', '2'); Expected = $secondRoot },
                @{ Name = 'invalid folder retry'; Candidates = @($firstRoot, $unusableRoot); Answers = @('2', '1'); Expected = $firstRoot },
                @{ Name = 'pasted quoted path'; Candidates = @(); Answers = @('  "' + $secondRoot + '"  '); Expected = $secondRoot },
                @{ Name = 'pasted single-quoted path'; Candidates = @($firstRoot, $secondRoot); Answers = @("'" + $secondRoot + "'"); Expected = $secondRoot },
                @{ Name = 'single usable folder'; Candidates = @($secondRoot); Answers = @(); Expected = $secondRoot },
                @{ Name = 'single unusable folder'; Candidates = @($unusableRoot); Answers = @($firstRoot); Expected = $firstRoot },
                @{ Name = 'cancel'; Candidates = @($firstRoot, $secondRoot); Answers = @(''); Expected = '' },
                @{ Name = 'stale memory cancellation'; Candidates = @($firstRoot, $secondRoot); Answers = @(' '); Expected = ''; Remembered = $unusableRoot; Shortcut = $true },
                @{ Name = 'stale memory replacement'; Candidates = @($firstRoot, $secondRoot); Answers = @('2'); Expected = $secondRoot; Remembered = $unusableRoot },
                @{ Name = 'remembered choice'; Candidates = @(); Answers = @(); Expected = $secondRoot; Remembered = $secondRoot; Shortcut = $true }
            )
            foreach ($case in $cases) {
                if ([IO.File]::Exists($remembered)) { [IO.File]::Delete($remembered) }
                if ($case.ContainsKey('Remembered')) { Write-NanolatheData $remembered $case.Remembered }
                $selection = @{
                    Candidates = $case.Candidates; Answers = (New-Object Collections.Queue)
                    Prompts = @(); Messages = @(); Checks = @(); Launches = @(); Discoveries = 0; Dialogs = 0
                }
                foreach ($answer in $case.Answers) { $selection.Answers.Enqueue($answer) }
                if ($case.ContainsKey('Shortcut')) { & ([scriptblock]::Create($shortcutCommand)) }
                else { & ([scriptblock]::Create($selectionLauncher)) -Base $base }
                if ($case.ContainsKey('Shortcut')) { Assert-Equal $selection.Messages[0] 'Opening Nanolathe...' "$($case.Name): shortcut announces startup" }
                Assert-Equal $selection.Prompts.Count $case.Answers.Count "$($case.Name): consumes expected choices"
                Assert-Equal ($selection.Launches -join '') $case.Expected "$($case.Name): launches only selected data"
                Assert-Equal $selection.Launches.Count ([int]($case.Expected -ne '')) "$($case.Name): starts once or cancels"
                Assert-Equal $selection.Dialogs 0 "$($case.Name): never attempts a dialog"
                Assert-Equal $env:NANOLATHE_SETTINGS 'authored-settings-before-selection' "$($case.Name): restores settings"
                if ($case.Expected -ne '') {
                    Assert-Equal ([IO.File]::ReadAllText($remembered)) $case.Expected "$($case.Name): remembers validated choice"
                } elseif ($case.ContainsKey('Remembered')) {
                    Assert-Equal ([IO.File]::ReadAllText($remembered)) $case.Remembered "$($case.Name): cancellation preserves memory"
                } else { Assert-Equal ([IO.File]::Exists($remembered)) $false "$($case.Name): cancellation writes no memory" }
                if ($selection.Prompts.Count -gt 0) {
                    Assert-Equal $selection.Prompts[0].Contains('press Enter') $true "$($case.Name): explains how to submit"
                    for ($i = 0; $i -lt $case.Candidates.Count; $i++) {
                        Assert-Equal ($selection.Messages -contains ('  {0}) {1}' -f ($i + 1), $case.Candidates[$i])) $true "$($case.Name): numbers each installation"
                    }
                }
                if ($case.Name -eq 'remembered choice') { Assert-Equal $selection.Discoveries 0 'Valid memory bypasses discovery and prompting' }
            }
        } finally {
            $env:NANOLATHE_SKIP_UPDATE_CHECK = $skipBefore
            $env:NANOLATHE_SETTINGS = $settingsBefore
        }
    }
    Write-Host 'Windows installer offline tests: OK'
} finally {
    if ([IO.Directory]::Exists($base)) { Remove-Item -LiteralPath $base -Recurse -Force }
}
