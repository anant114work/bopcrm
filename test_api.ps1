# PowerShell script to test United Network CRM API

$apiKey = "UNC-TEST123456789"
$baseUrl = "http://localhost:8000"

Write-Host "Testing United Network CRM API..." -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Test API Status
Write-Host "`n1. Testing API Status..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/external/status/" -Headers @{"X-API-Key" = $apiKey}
    Write-Host "Status: SUCCESS" -ForegroundColor Green
    Write-Host "Total Bookings: $($response.total_bookings)" -ForegroundColor Cyan
} catch {
    Write-Host "Status: FAILED - $($_.Exception.Message)" -ForegroundColor Red
}

# Test Get All Bookings
Write-Host "`n2. Testing Get All Bookings..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/external/bookings/?per_page=10" -Headers @{"X-API-Key" = $apiKey}
    Write-Host "Status: SUCCESS" -ForegroundColor Green
    Write-Host "Total Bookings: $($response.pagination.total_bookings)" -ForegroundColor Cyan
    Write-Host "Bookings in response: $($response.bookings.Count)" -ForegroundColor Cyan
    
    if ($response.bookings.Count -gt 0) {
        Write-Host "`nFirst booking:" -ForegroundColor Magenta
        $booking = $response.bookings[0]
        Write-Host "  ID: $($booking.booking_id)" -ForegroundColor White
        Write-Host "  Customer: $($booking.customer_name)" -ForegroundColor White
        Write-Host "  Project: $($booking.project_name)" -ForegroundColor White
        Write-Host "  Amount: $($booking.total_amount)" -ForegroundColor White
    }
} catch {
    Write-Host "Status: FAILED - $($_.Exception.Message)" -ForegroundColor Red
}

# Test Search
Write-Host "`n3. Testing Search..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/external/search/?status=confirmed" -Headers @{"X-API-Key" = $apiKey}
    Write-Host "Status: SUCCESS" -ForegroundColor Green
    Write-Host "Search Results: $($response.total_found)" -ForegroundColor Cyan
} catch {
    Write-Host "Status: FAILED - $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=================================" -ForegroundColor Green
Write-Host "API Testing Complete!" -ForegroundColor Green
Write-Host "Use API Key: $apiKey" -ForegroundColor Yellow
Write-Host "Base URL: $baseUrl" -ForegroundColor Yellow