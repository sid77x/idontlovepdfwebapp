# PowerShell script to stop all microservices
Write-Host "Stopping all microservices..." -ForegroundColor Cyan
Write-Host ""

# Define service ports
$ports = @(8000, 8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8009, 8010, 8011, 8012, 8013, 8014, 8015, 8016, 8017, 8018, 8019, 8020)

$stoppedCount = 0

foreach ($port in $ports) {
    Write-Host "Checking port $port..." -NoNewline
    
    $connection = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    
    if ($connection) {
        $processId = $connection.OwningProcess
        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
        
        if ($process) {
            $processName = $process.ProcessName
            Stop-Process -Id $processId -Force -ErrorAction Stop
            Write-Host " Stopped $processName (PID: $processId)" -ForegroundColor Green
            $stoppedCount++
        }
    } else {
        Write-Host " Not running" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Stopped $stoppedCount service(s)" -ForegroundColor Cyan
Write-Host "All services stopped!" -ForegroundColor Green
