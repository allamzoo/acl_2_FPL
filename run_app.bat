@echo off
echo ============================================================
echo FPL Knowledge Graph Assistant
echo ============================================================
echo.

cd /d "d:\Acl Proj MS3\acl_2_FPL"

echo Starting application...
echo.
echo The application will open in your browser at http://localhost:8501
echo Press Ctrl+C to stop the application
echo ============================================================
echo.

"C:\Users\omarb\AppData\Local\Programs\Python\Python313\python.exe" -m streamlit run src/ui/app.py --server.port 8501 --server.headless false

pause
