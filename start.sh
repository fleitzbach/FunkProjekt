

#!/bin/bash

# Start the backend
cd backend
uvicorn main:app --reload &

# Start the frontend
cd ../frontend
npm run dev
