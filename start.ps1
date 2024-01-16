# Start backend server
Start-Process -FilePath "bash" -ArgumentList "-c `"cd backend && uvicorn main:app --reload`""

# Start frontend development server
Start-Process -FilePath "bash" -ArgumentList "-c `"cd frontend && npm run dev`""

# Wait for backend server to start
Start-Sleep -Seconds 5

# Attach to the backend process
Get-Process | Where-Object {$_.ProcessName -eq "uvicorn"} | Select-Object -First 1 | ForEach-Object {Start-Process -FilePath "powershell" -ArgumentList "-Command `"AttachConsole $($_.Id);`""}

# Wait for frontend server to start
Start-Sleep -Seconds 5

# Attach to the frontend process
Get-Process | Where-Object {$_.ProcessName -eq "npm"} | Select-Object -First 1 | ForEach-Object {Start-Process -FilePath "powershell" -ArgumentList "-Command `"AttachConsole $($_.Id);`""}
