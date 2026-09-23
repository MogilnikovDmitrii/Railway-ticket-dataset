if [ -f "$russian_names.csv" ]; then
    rm russian_names.csv
fi
if [ -f "$russian_names.parquet" ]; then
    rm russian_names.parquet
fi
python main.py
python unparqueter.py
