## Before you run the code, you need to:

1. Download libraries via the VS Code console:
```python
pip install pillow
```
```python
pip install psycopg2
```
```python
pip install bcrypt
```

2. Create 'postgres' database in SQL server:
```SQL
CREATE DATABASE postgres;
```

3: Specify your server password:
```python
def connect_to_db():
    try:
        connection = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="123",
            host="localhost",
            port="5432"
        )
        return connection
    except Exception as e:
        messagebox.showerror("Ошибка подключения", f"Не удалось подключиться к базе данных: {e}")
        return None
```
