<#
    Port housekeeping for run.cmd.

    This lives in its own file rather than inline in the batch script because escaping a
    PowerShell one-liner inside cmd is a trap: a caret continuation plus a quoted string
    containing a pipe silently produces a command that does nothing, reports success, and
    leaves the port held. That is exactly how "Clearing ports..." printed happily while
    clearing nothing.

    Usage:
        ports.ps1 -Action free   -Ports 8020,4300
        ports.ps1 -Action check  -Ports 8020,4300      # exit 1 if any are still held
        ports.ps1 -Action wait   -Ports 8020 -Url http://127.0.0.1:8020/api/health
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][ValidateSet('free', 'check', 'wait')][string]$Action,
    # Taken as a string and split here rather than declared [int[]]. When this script is
    # invoked with `powershell -File`, every argument arrives as a single string: "8020,4300"
    # binds to an int array as the number 80204300, which Get-NetTCPConnection then rejects
    # as too large for a port. The batch file has to use -File, so the split belongs here.
    [string]$Ports = '',
    [string]$Url = '',
    [int]$TimeoutSeconds = 90
)

$PortList = @(
    $Ports -split ',' |
        ForEach-Object { $_.Trim() } |
        Where-Object { $_ -match '^\d+$' } |
        ForEach-Object { [int]$_ }
)

function Get-Holders {
    param([int]$Port)
    # Get-NetTCPConnection rather than parsing netstat: the netstat columns shift with the
    # address family, so a text pattern that matches a port bound on 0.0.0.0 misses the
    # same port bound on [::] and reports the port as free while a process still holds it.
    Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
}

switch ($Action) {

    'free' {
        foreach ($port in $PortList) {
            $holders = Get-Holders -Port $port
            if (-not $holders) {
                Write-Host "  port $port already free"
                continue
            }
            foreach ($holder in $holders) {
                $proc = Get-Process -Id $holder.OwningProcess -ErrorAction SilentlyContinue
                $name = if ($proc) { $proc.ProcessName } else { 'unknown' }
                try {
                    Stop-Process -Id $holder.OwningProcess -Force -ErrorAction Stop
                    Write-Host "  freed port $port (was $name, PID $($holder.OwningProcess))"
                } catch {
                    Write-Host "  could not free port $port - $name (PID $($holder.OwningProcess)) is not ours to stop" -ForegroundColor Yellow
                }
            }
        }
        # Sockets linger briefly in TIME_WAIT after the process dies.
        Start-Sleep -Seconds 2
        exit 0
    }

    'check' {
        $busy = @()
        foreach ($port in $PortList) {
            if (Get-Holders -Port $port) { $busy += $port }
        }
        if (-not $busy) { exit 0 }

        Write-Host ''
        Write-Host "  STILL IN USE: $($busy -join ', ')" -ForegroundColor Red
        foreach ($port in $busy) {
            foreach ($holder in Get-Holders -Port $port) {
                $proc = Get-Process -Id $holder.OwningProcess -ErrorAction SilentlyContinue
                Write-Host "    port $port -> PID $($holder.OwningProcess) $(if ($proc) { "($($proc.ProcessName))" })"
            }
        }
        Write-Host ''
        Write-Host '  Something outside this project is holding it. Either stop that process,'
        Write-Host '  or pick different ports in frontend\vite.config.js and at the top of run.cmd.'
        # vite.config.js sets strictPort, so a squatted web port is a hard error with a
        # stack trace. Refusing here, with the offending PID named, beats that.
        exit 1
    }

    'wait' {
        # The API warms its caches on startup - the audit plan, the rota, the duplicate
        # filter and the language probe - so no page load pays a cold cost. Wait for it to
        # actually answer rather than guessing a fixed delay: on a cold disk the warm-up
        # outlasts any timeout worth hard-coding, and starting the web app early just means
        # the first page load races the warm-up and loses.
        for ($i = 0; $i -lt $TimeoutSeconds; $i++) {
            try {
                $res = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
                if ($res.StatusCode -eq 200) {
                    Write-Host "  API is up (after ${i}s)."
                    exit 0
                }
            } catch { }
            Start-Sleep -Seconds 1
        }
        Write-Host "  API did not answer within ${TimeoutSeconds}s - check the MPLADS API window." -ForegroundColor Yellow
        exit 0
    }
}
