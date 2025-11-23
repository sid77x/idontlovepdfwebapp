# Check microservices status
Write-Host "Checking microservices status..." -ForegroundColor Cyan
Write-Host ""

$ports = @(8000, 8001, 8002, 8003, 8004, 8005, 8006, 8010, 8011, 8012)
$names = @("Orchestrator", "Merge", "Rotate", "Split", "Protect", "Compress", "Watermark", "OCR", "PDF to Image", "Image to PDF")

$runningCount = 0

for ($i = 0; $i -lt $ports.Length; $i++) {
    $port = $ports[$i]
    $serviceName = $names[$i]
    
    Write-Host "$port - $serviceName " -NoNewline -ForegroundColor Yellow
    
    $connection = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    
    if ($connection) {
        $processId = $connection.OwningProcess
        Write-Host "RUNNING" -ForegroundColor Green -NoNewline
        Write-Host " (PID: $processId)" -ForegroundColor Gray
        $runningCount++
    } else {
        Write-Host "STOPPED" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "$runningCount of $($ports.Length) services running" -ForegroundColor Cyan
