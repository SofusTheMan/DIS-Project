./createdotenv.sh

pip install -r requirements.txt

psql < setup.sql

psql < dummy_data.sql