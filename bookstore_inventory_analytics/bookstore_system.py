"""
Bookstore Inventory and Analytics System
Requirements: pandas, numpy, matplotlib, seaborn

Install dependencies:
    pip install pandas numpy matplotlib seaborn

Run:
    python bookstore_system.py

Files expected in the same folder:
    inventory.csv
    sales.csv
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = Path(__file__).resolve().parent
INVENTORY_FILE = BASE_DIR / "inventory.csv"
SALES_FILE = BASE_DIR / "sales.csv"

INVENTORY_COLUMNS = ["Title", "Author", "Genre", "Price", "Quantity"]
SALES_COLUMNS = ["Date", "Title", "Quantity Sold", "Total Revenue"]


class Bookstore:
    """Manage book inventory, record sales, and analyze bookstore data."""

    def __init__(self, inventory_file=INVENTORY_FILE, sales_file=SALES_FILE):
        self.inventory_file = Path(inventory_file)
        self.sales_file = Path(sales_file)
        self.inventory = self._load_inventory()
        self.sales = self._load_sales()

    def _load_inventory(self):
        """Load and validate the inventory CSV; create it if it does not exist."""
        if not self.inventory_file.exists():
            pd.DataFrame(columns=INVENTORY_COLUMNS).to_csv(self.inventory_file, index=False)

        df = pd.read_csv(self.inventory_file)
        for column in INVENTORY_COLUMNS:
            if column not in df.columns:
                df[column] = np.nan
        df = df[INVENTORY_COLUMNS]

        df["Title"] = df["Title"].fillna("").astype(str).str.strip()
        df["Author"] = df["Author"].fillna("").astype(str).str.strip()
        df["Genre"] = df["Genre"].fillna("Unknown").astype(str).str.strip()
        df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
        df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
        df = df.dropna(subset=["Price", "Quantity"])
        df = df[(df["Title"] != "") & (df["Price"] >= 0) & (df["Quantity"] >= 0)]
        df["Quantity"] = df["Quantity"].astype(int)
        return df.reset_index(drop=True)

    def _load_sales(self):
        """Load and validate sales records; create the CSV if missing."""
        if not self.sales_file.exists():
            pd.DataFrame(columns=SALES_COLUMNS).to_csv(self.sales_file, index=False)

        df = pd.read_csv(self.sales_file)
        for column in SALES_COLUMNS:
            if column not in df.columns:
                df[column] = np.nan
        df = df[SALES_COLUMNS]

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Title"] = df["Title"].fillna("").astype(str).str.strip()
        df["Quantity Sold"] = pd.to_numeric(df["Quantity Sold"], errors="coerce")
        df["Total Revenue"] = pd.to_numeric(df["Total Revenue"], errors="coerce")
        df = df.dropna(subset=["Date", "Quantity Sold", "Total Revenue"])
        df = df[(df["Title"] != "") & (df["Quantity Sold"] > 0) & (df["Total Revenue"] >= 0)]
        df["Quantity Sold"] = df["Quantity Sold"].astype(int)
        return df.reset_index(drop=True)

    def _save_inventory(self):
        self.inventory.to_csv(self.inventory_file, index=False)

    def _save_sales(self):
        sales_to_save = self.sales.copy()
        sales_to_save["Date"] = pd.to_datetime(sales_to_save["Date"]).dt.strftime("%Y-%m-%d")
        sales_to_save.to_csv(self.sales_file, index=False)

    def add_book(self, title, author, price, quantity, genre="Unknown"):
        """Add a new book or update the existing book's stock."""
        title, author, genre = title.strip(), author.strip(), genre.strip() or "Unknown"
        if not title or not author:
            print("Title and author cannot be empty.")
            return
        try:
            price, quantity = float(price), int(quantity)
        except (ValueError, TypeError):
            print("Price must be numeric and quantity must be a whole number.")
            return
        if price < 0 or quantity < 0:
            print("Price and quantity cannot be negative.")
            return

        matches = self.inventory["Title"].str.casefold() == title.casefold()
        if matches.any():
            print("This title already exists. Use Update Stock to change its quantity.")
            return

        new_row = pd.DataFrame([{
            "Title": title, "Author": author, "Genre": genre,
            "Price": price, "Quantity": quantity
        }])
        self.inventory = pd.concat([self.inventory, new_row], ignore_index=True)
        self._save_inventory()
        print(f"Added '{title}' to inventory.")

    def update_inventory(self, title, quantity):
        """Set the stock quantity for a book."""
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            print("Quantity must be a whole number.")
            return
        if quantity < 0:
            print("Quantity cannot be negative.")
            return

        matches = self.inventory["Title"].str.casefold() == title.strip().casefold()
        if not matches.any():
            print("Book not found.")
            return
        self.inventory.loc[matches, "Quantity"] = quantity
        self._save_inventory()
        print(f"Stock updated for '{title}'.")

    def remove_book(self, title):
        """Remove a book from the inventory."""
        matches = self.inventory["Title"].str.casefold() == title.strip().casefold()
        if not matches.any():
            print("Book not found.")
            return
        self.inventory = self.inventory.loc[~matches].reset_index(drop=True)
        self._save_inventory()
        print(f"Removed '{title}' from inventory.")

    def record_sale(self, title, quantity):
        """Record a sale, reduce stock, and calculate revenue."""
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            print("Quantity sold must be a whole number.")
            return
        if quantity <= 0:
            print("Quantity sold must be greater than zero.")
            return

        matches = self.inventory["Title"].str.casefold() == title.strip().casefold()
        if not matches.any():
            print("Book not found in inventory.")
            return

        index = self.inventory.index[matches][0]
        available = int(self.inventory.at[index, "Quantity"])
        if quantity > available:
            print(f"Not enough stock. Available quantity: {available}")
            return

        price = float(self.inventory.at[index, "Price"])
        revenue = round(price * quantity, 2)
        self.inventory.at[index, "Quantity"] = available - quantity
        sale = pd.DataFrame([{
            "Date": pd.Timestamp.today().normalize(),
            "Title": self.inventory.at[index, "Title"],
            "Quantity Sold": quantity,
            "Total Revenue": revenue
        }])
        self.sales = pd.concat([self.sales, sale], ignore_index=True)
        self._save_inventory()
        self._save_sales()
        print(f"Sale recorded: {quantity} copy/copies of '{title}', revenue ₹{revenue:.2f}.")

    def show_inventory(self):
        if self.inventory.empty:
            print("Inventory is empty.")
        else:
            print("\nBOOK INVENTORY")
            print(self.inventory.to_string(index=False))

    def show_sales(self):
        if self.sales.empty:
            print("No sales records available.")
        else:
            print("\nSALES RECORDS")
            print(self.sales.to_string(index=False))

    def generate_report(self):
        """Print useful inventory and sales metrics."""
        print("\n========== BOOKSTORE REPORT ==========")
        print(f"Different book titles: {len(self.inventory)}")
        print(f"Total copies in stock: {int(self.inventory['Quantity'].sum()) if not self.inventory.empty else 0}")
        stock_value = (self.inventory["Price"] * self.inventory["Quantity"]).sum()
        print(f"Current inventory value: ₹{stock_value:.2f}")
        total_revenue = float(self.sales["Total Revenue"].sum()) if not self.sales.empty else 0.0
        total_sold = int(self.sales["Quantity Sold"].sum()) if not self.sales.empty else 0
        print(f"Total copies sold: {total_sold}")
        print(f"Total revenue: ₹{total_revenue:.2f}")

        if not self.sales.empty:
            top_books = (self.sales.groupby("Title")["Quantity Sold"]
                         .sum().sort_values(ascending=False))
            print("\nTop-selling books:")
            print(top_books.head(5).to_string())
        else:
            print("Top-selling books: no sales data yet.")

    def analyze_sales(self):
        """Use NumPy and Pandas to calculate sales summaries."""
        if self.sales.empty:
            print("No sales data to analyze.")
            return

        quantities = self.sales["Quantity Sold"].to_numpy(dtype=float)
        revenues = self.sales["Total Revenue"].to_numpy(dtype=float)
        print("\n========== SALES ANALYSIS ==========")
        print(f"Total revenue: ₹{np.sum(revenues):.2f}")
        print(f"Average revenue per sales record: ₹{np.mean(revenues):.2f}")
        print(f"Average quantity per sales record: {np.mean(quantities):.2f}")

        top = (self.sales.groupby("Title")["Quantity Sold"].sum()
               .sort_values(ascending=False))
        print("\nTop-selling books:")
        print(top.head(5).to_string())

        inventory_details = self.inventory[["Title", "Author", "Genre"]]
        enriched = self.sales.merge(inventory_details, on="Title", how="left")
        enriched["Genre"] = enriched["Genre"].fillna("Unknown")
        print("\nRevenue by genre:")
        print(enriched.groupby("Genre")["Total Revenue"].sum()
              .sort_values(ascending=False).to_string())

        monthly = self.sales.assign(Month=self.sales["Date"].dt.to_period("M").astype(str))
        print("\nMonthly revenue:")
        print(monthly.groupby("Month")["Total Revenue"].sum().to_string())

    def visualize_data(self):
        """Create bar, line, pie, and heatmap visualizations."""
        if self.inventory.empty and self.sales.empty:
            print("There is no data to visualize.")
            return

        sns.set_theme(style="whitegrid")
        inventory_details = self.inventory[["Title", "Author", "Genre"]]
        sales = self.sales.merge(inventory_details, on="Title", how="left")
        sales["Genre"] = sales["Genre"].fillna("Unknown")

        # 1. Bar chart: copies sold by genre
        if not sales.empty:
            genre_sales = sales.groupby("Genre")["Quantity Sold"].sum().sort_values(ascending=False)
            plt.figure(figsize=(9, 5))
            sns.barplot(x=genre_sales.index, y=genre_sales.values)
            plt.title("Total Copies Sold by Genre")
            plt.xlabel("Genre")
            plt.ylabel("Copies Sold")
            plt.xticks(rotation=30, ha="right")
            plt.tight_layout()
            plt.show()

            # 2. Line chart: monthly revenue
            monthly = sales.assign(Month=sales["Date"].dt.to_period("M").dt.to_timestamp())
            monthly_revenue = monthly.groupby("Month")["Total Revenue"].sum().sort_index()
            plt.figure(figsize=(9, 5))
            plt.plot(monthly_revenue.index, monthly_revenue.values, marker="o")
            plt.title("Monthly Sales Revenue")
            plt.xlabel("Month")
            plt.ylabel("Revenue (₹)")
            plt.xticks(rotation=30, ha="right")
            plt.tight_layout()
            plt.show()

            # 3. Pie chart: revenue share by genre
            genre_revenue = sales.groupby("Genre")["Total Revenue"].sum()
            genre_revenue = genre_revenue[genre_revenue > 0]
            if not genre_revenue.empty:
                plt.figure(figsize=(7, 7))
                plt.pie(genre_revenue.values, labels=genre_revenue.index,
                        autopct="%1.1f%%", startangle=90)
                plt.title("Revenue Share by Genre")
                plt.tight_layout()
                plt.show()

        # 4. Heatmap: correlation between price and sales volume
        if not self.inventory.empty:
            book_sales = self.sales.groupby("Title")["Quantity Sold"].sum().rename("Total Sold")
            comparison = self.inventory[["Title", "Price"]].merge(
                book_sales, on="Title", how="left"
            )
            comparison["Total Sold"] = comparison["Total Sold"].fillna(0)
            if len(comparison) >= 2:
                corr = comparison[["Price", "Total Sold"]].corr(numeric_only=True)
                plt.figure(figsize=(6, 4))
                sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1)
                plt.title("Correlation: Book Price and Sales Volume")
                plt.tight_layout()
                plt.show()
            else:
                print("Heatmap needs at least two book titles.")

    def menu(self):
        """Interactive command-line menu."""
        while True:
            print("""
========== BOOKSTORE INVENTORY & ANALYTICS ==========
1. Show inventory
2. Add a book
3. Update stock quantity
4. Remove a book
5. Record a sale
6. Show sales records
7. Generate report
8. Analyze sales
9. Show visualizations
0. Exit
""")
            choice = input("Enter your choice: ").strip()

            if choice == "1":
                self.show_inventory()
            elif choice == "2":
                title = input("Book title: ").strip()
                author = input("Author: ").strip()
                genre = input("Genre: ").strip() or "Unknown"
                price = input("Price (₹): ").strip()
                quantity = input("Quantity: ").strip()
                self.add_book(title, author, price, quantity, genre)
            elif choice == "3":
                title = input("Book title: ").strip()
                quantity = input("New stock quantity: ").strip()
                self.update_inventory(title, quantity)
            elif choice == "4":
                self.remove_book(input("Book title to remove: ").strip())
            elif choice == "5":
                title = input("Book title sold: ").strip()
                quantity = input("Quantity sold: ").strip()
                self.record_sale(title, quantity)
            elif choice == "6":
                self.show_sales()
            elif choice == "7":
                self.generate_report()
            elif choice == "8":
                self.analyze_sales()
            elif choice == "9":
                self.visualize_data()
            elif choice == "0":
                print("Thank you for using the Bookstore System!")
                break
            else:
                print("Invalid choice. Please enter a number from 0 to 9.")


if __name__ == "__main__":
    Bookstore().menu()
