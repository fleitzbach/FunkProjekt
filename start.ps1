# Start the backend server in a new PowerShell window
Start-Process "powershell" -ArgumentList "-NoExit", "-Command", "cd .\backend; uvicorn main:app --reload" -WindowStyle 'Minimized'

# Start the frontend server in another new PowerShell window
Start-Process "powershell" -ArgumentList "-NoExit", "-Command", "cd .\frontend; npm run dev" -WindowStyle 'Minimized'
