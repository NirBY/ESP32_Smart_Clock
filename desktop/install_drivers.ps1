# Uses Windows' built-in update service to obtain applicable signed USB drivers.
$ErrorActionPreference = 'Stop'
$report = Join-Path $env:LOCALAPPDATA 'SmartClock\driver-result.txt'
try {
    $devices = @(Get-CimInstance Win32_PnPEntity | Where-Object {
        $_.PNPDeviceID -match 'USB\\VID_(10C4|1A86|0403|303A)' })
    if ($devices.Count -eq 0) { throw 'No supported USB bridge detected. Check the USB data cable and reconnect the clock.' }
    $hardwareIds = @($devices | ForEach-Object { $_.HardwareID })
    $session = New-Object -ComObject Microsoft.Update.Session
    $search = $session.CreateUpdateSearcher().Search("IsInstalled=0 and Type='Driver'")
    $selected = New-Object -ComObject Microsoft.Update.UpdateColl
    foreach ($update in $search.Updates) {
        $id = $update.DriverHardwareID
        if ($id -and ($hardwareIds -contains $id) -and $id -match 'VID_(10C4|1A86|0403|303A)') {
            if (-not $update.EulaAccepted) { $update.AcceptEula() }
            [void]$selected.Add($update)
        }
    }
    if ($selected.Count -eq 0) {
        'No applicable USB driver update offered by Windows Update. If no COM port appears, the vendor driver is still required.' | Set-Content -LiteralPath $report
        exit 0
    }
    $downloader = $session.CreateUpdateDownloader()
    $downloader.Updates = $selected
    $download = $downloader.Download()
    if ($download.ResultCode -ne 2) { throw "Driver download failed: $($download.ResultCode)" }
    $installer = $session.CreateUpdateInstaller()
    $installer.Updates = $selected
    $result = $installer.Install()
    if ($result.ResultCode -ne 2) { throw "Driver installation failed: $($result.ResultCode)" }
    "USB driver installation completed. Reconnect USB. Restart required: $($result.RebootRequired)" | Set-Content -LiteralPath $report
} catch {
    "Driver setup failed: $($_.Exception.Message)" | Set-Content -LiteralPath $report
    exit 1
}
