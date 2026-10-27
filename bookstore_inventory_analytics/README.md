# Bookstore Inventory and Analytics System

A Python project for managing bookstore stock, recording sales, analyzing revenue, and visualizing trends.

## Features
- Add, update, and remove books
- Validate price, stock, and sales quantities
- Record sales and automatically reduce stock
- Read/write `inventory.csv` and `sales.csv` using Pandas
- Use NumPy for numerical sales calculations
- Report total revenue, stock value, and top-selling books
- Analyze monthly revenue and revenue by genre
- Create a genre bar chart, monthly revenue line chart, genre revenue pie chart, and price/sales correlation heatmap

## Requirements
Python 3.9 or newer is recommended.

Install packages:
```bash
pip install pandas numpy matplotlib seaborn
```

## Run
Keep `bookstore_system.py`, `inventory.csv`, and `sales.csv` in the same folder, then run:
```bash
python bookstore_system.py
```

Choose an option from the interactive menu. The CSV files are updated when books or sales are changed.

## Dataset columns
- `inventory.csv`: Title, Author, Genre, Price, Quantity
- `sales.csv`: Date, Title, Quantity Sold, Total Revenue

The included CSV files contain sample data for testing. Back them up before experimenting if you want to preserve the original examples.
