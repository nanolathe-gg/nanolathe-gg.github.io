# No network, Go compiler, game, or real Start Menu changes. Windows opens
# real production-generated .lnk files; elsewhere only the child loader runs.
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
. (Join-Path (Split-Path $PSScriptRoot -Parent) 'static/install.ps1')
# Compile the interop even on portable hosts; COM execution remains Windows-only.
Initialize-NanolatheShortcutInterop

function Assert-ShortcutEqual($Actual, $Expected, [string]$Message) {
    if ($Actual -cne $Expected) { throw "$Message (actual: $Actual; expected: $Expected)" }
}

function Assert-ShortcutLaunch([string]$Path, [string]$Base, [string]$Release) {
    $sentinel = Join-Path $Base 'sentinel.txt'
    if ([IO.File]::Exists($sentinel)) { [IO.File]::Delete($sentinel) }
    $start = New-Object Diagnostics.ProcessStartInfo
    if ($nativeWindows) {
        # Ask Windows to open the saved link, not its decoded command. Start
        # elsewhere so only the link can supply the correct working directory.
        $start.FileName = $Path
        $start.UseShellExecute = $true
        $start.WorkingDirectory = $work
    } else {
        $start.FileName = (Get-Process -Id $PID).Path
        # STA and WindowStyle are Windows-only; the payload is unchanged.
        $start.Arguments = (Get-NanolatheLaunchCommand).Replace(' -STA', '').Replace(' -WindowStyle Normal', '')
        $start.UseShellExecute = $false
        $start.WorkingDirectory = $Base
    }
    $process = [Diagnostics.Process]::Start($start)
    try {
        # Hosted ARM64 machines can take longer to cold-start Windows PowerShell.
        if (!$process -or !$process.WaitForExit(60000)) {
            if ($process) { $process.Kill(); $process.WaitForExit() }
            throw "Shortcut did not finish within 60 seconds (sentinel exists: $([IO.File]::Exists($sentinel))): $Path"
        }
        Assert-ShortcutEqual $process.ExitCode 0 'Shortcut child exit code'
        if (![IO.File]::Exists($sentinel)) { throw "Shortcut did not write a sentinel: $Path" }
        Assert-ShortcutEqual ([IO.File]::ReadAllText($sentinel)) ($Base + "`n" + $Release) 'Shortcut selected Base and release'
        $hostVersion = [IO.File]::ReadAllText((Join-Path $Base 'host-version.txt'))
        if ($nativeWindows -and $hostVersion -notlike '5.1.*') { throw "Expected Windows PowerShell 5.1 child, got $hostVersion" }
        Write-Host "Sentinel child PowerShell $hostVersion selected $Release"
    } finally { if ($process) { $process.Dispose() } }
}

function Assert-SavedShortcut([string]$Path, [string]$Base, [string]$Release) {
    $wsh = New-Object -ComObject WScript.Shell
    $shell = New-Object -ComObject Shell.Application
    $link = $null
    $folder = $null
    $item = $null
    try {
        $link = $wsh.CreateShortcut($Path)
        $folder = $shell.Namespace([IO.Path]::GetDirectoryName($Path))
        $item = $folder.ParseName([IO.Path]::GetFileName($Path))
        $wide = [Nanolathe.WindowsShortcut]::Read($Path)
        # GetArguments readers can truncate silently. Inspect the property store
        # as well as WSH, and still require an actual launch below (issue #117).
        $fullArguments = $item.ExtendedProperty('System.Link.Arguments')
        $expected = Get-NanolatheLaunchCommand
        Write-Host "Saved shortcut arguments: expected=$($expected.Length), WSH=$($link.Arguments.Length), property store=$($fullArguments.Length)"
        Assert-ShortcutEqual $fullArguments $expected 'Full stored shortcut arguments'
        Assert-ShortcutEqual $link.Arguments $expected 'Short arguments survive WSH readback'
        # WSH path getters can return a lossy ANSI spelling. Read through the
        # Unicode interface, then prove the path through actual execution.
        Write-Host "Working directory readback: WSH=$($link.WorkingDirectory); Unicode=$($wide.WorkingDirectory)"
        Assert-ShortcutEqual $wide.WorkingDirectory $Base 'Saved shortcut working directory'
        Assert-ShortcutEqual $wide.TargetPath (Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe') 'Saved shortcut target'
        Assert-ShortcutEqual $wide.WindowStyle 1 'Saved shortcut has a visible console for folder selection'
        $iconPath = Join-Path (Join-Path (Join-Path $Base 'releases') $Release) 'Nanolathe.ico'
        Assert-ShortcutEqual $wide.IconLocation ($iconPath + ',0') 'Saved shortcut release icon'
        Add-Type -AssemblyName System.Drawing
        $icon = New-Object Drawing.Icon($iconPath)
        try { if ($icon.Width -le 0) { throw 'Windows could not load the icon.' } }
        finally { $icon.Dispose() }
    } finally {
        foreach ($com in @($item, $folder, $link, $shell, $wsh)) {
            if ($com) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($com) }
        }
    }
}

$nativeWindows = [Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT
$work = Join-Path ([IO.Path]::GetTempPath()) ('nl-shortcut-' + [guid]::NewGuid().ToString('N'))
try {
    [void][IO.Directory]::CreateDirectory($work)
    # macOS temp paths may contain /var -> /private/var. Compare the physical
    # path the child OS working directory returns, rather than its symlink alias.
    $directoryBefore = [Environment]::CurrentDirectory
    try {
        [Environment]::CurrentDirectory = $work
        $work = [Environment]::CurrentDirectory
    } finally { [Environment]::CurrentDirectory = $directoryBefore }
    $special = "O'Brien & `$x; [alpha] " + [char]0x03A9 + [char]0x65E5
    # Keep fixture files within Windows PowerShell 5.1's ordinary MAX_PATH
    # support, but make Base long enough to catch path-expanded command growth.
    $longName = $special + ('x' * [Math]::Max(1, (190 - $work.Length - $special.Length - 1)))
    foreach ($name in @('plain', $special, $longName)) {
        $base = Join-Path $work $name
        foreach ($release in @('old-release', 'next-release')) {
            $directory = Join-Path (Join-Path $base 'releases') $release
            [void][IO.Directory]::CreateDirectory($directory)
            [IO.File]::Copy((Join-Path $PSScriptRoot 'installer-fixtures/windows/Nanolathe.ico'), (Join-Path $directory 'Nanolathe.ico'))
            $fixture = @'
param([string]$Base)
[IO.File]::WriteAllText((Join-Path $Base 'host-version.txt'), $PSVersionTable.PSVersion.ToString())
[IO.File]::WriteAllText((Join-Path $Base 'sentinel.txt'), ($Base + "`n" + 'RELEASE_NAME'))
'@
            [IO.File]::WriteAllText((Join-Path $directory 'launch.ps1'), $fixture.Replace('RELEASE_NAME', $release))
        }
        Write-NanolatheData (Join-Path $base 'current.txt') 'old-release'
        # The installer prepares its link under Base, so the link's own path
        # must also survive Unicode and long directory names before copying.
        $temporaryLink = Join-Path $base 'temporary.lnk'
        $savedLink = Join-Path $work 'Nanolathe.lnk'
        $arguments = Get-NanolatheLaunchCommand
        if ($arguments.Length -ge 1023) { throw 'Shortcut loader no longer fits a 1023-character argument reader.' }
        foreach ($iconRelease in @('old-release', 'next-release')) {
            if ($nativeWindows) {
                Write-NanolatheShortcut $temporaryLink $base (Join-Path (Join-Path $base 'releases') $iconRelease)
                # Installation copies the prepared link out of its workspace.
                [IO.File]::Copy($temporaryLink, $savedLink, $true)
                [IO.File]::Delete($temporaryLink)
                Assert-SavedShortcut $savedLink $base $iconRelease
            } else {
                Write-NanolatheData (Join-Path $base 'launch.ps1') (Get-NanolatheBootstrap)
            }
            # Refreshing the shortcut must still launch the old release until
            # publication changes the pointer, even when its icon is newer.
            Assert-ShortcutLaunch $savedLink $base 'old-release'
        }
        Write-NanolatheData (Join-Path $base 'current.txt') 'next-release'
        Assert-ShortcutLaunch $savedLink $base 'next-release'
        Write-Host "Shortcut launch and refresh passed (Base length $($base.Length)): $name"
    }
    if ($nativeWindows) { Write-Host 'Native Windows saved-shortcut launch tests: OK' }
    else { Write-Host 'Portable child-loader tests: OK; SKIP native Windows .lnk execution and property-store checks.' }
} finally {
    if ([IO.Directory]::Exists($work)) { Remove-Item -LiteralPath $work -Recurse -Force }
}
