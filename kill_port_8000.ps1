$conn = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($conn) {
    $conn | ForEach-Object { 
        Write-Host "Killing process $($_.OwningProcess) on port 8000"
        Stop-Process -Id $_.OwningProcess -Force 
    }
} else {
    Write-Host "No process found on port 8000"
}
