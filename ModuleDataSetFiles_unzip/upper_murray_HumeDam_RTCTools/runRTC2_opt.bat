call .\venv\Scripts\activate && python .\src\Reservoir_Optimization.py --reservoirs_csv_path .\model\reservoirs.csv --volume_level_csv_paths .\model\volumelevel.csv  > .\RTC23opt_stdout.txt 2>&1
exit /b "%errorlevel%"  