$base = "http://127.0.0.1:8000"
$h = Invoke-RestMethod "$base/health"
if ($h.status -ne "ok") { throw "health failed" }
Write-Host "health OK"
$img = Invoke-RestMethod -Method POST -Uri "$base/image/generate" -ContentType "application/json" -Body '{"prompt":"smoke test boat"}'
Write-Host "v1 image job:" $img.job_id
Start-Sleep -Seconds 1
$j = Invoke-RestMethod "$base/jobs/$($img.job_id)"
Write-Host "v1 status:" $j.status
$v2 = Invoke-RestMethod -Method POST -Uri "$base/media/image/generate" -ContentType "application/json" -Body '{"prompt":"smoke v2 boat"}'
Write-Host "v2 job:" $v2.job_id
Write-Host "SMOKE OK (revisa status failed si faltan HF/ComfyUI)"
