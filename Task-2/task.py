import sqlite3
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Database file path
db_path = 'inventory.db'

# Delete the old database file if it exists
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Database '{db_path}' deleted successfully.")
else:
    print(f"Database '{db_path}' not found.")

# Create a new database and table
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# Create the Products table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL
);
''')

# Create a table for storing user credentials (username and password)
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);
''')

# Insert a new username and password (you can change these)
new_username = 'admin'
new_password = 'password123'  # Please change this to a stronger password

# Insert the new username and password into the Users table
cursor.execute('''
INSERT OR REPLACE INTO Users (username, password)
VALUES (?, ?)
''', (new_username, new_password))

# Commit the changes
connection.commit()

# Close the connection
connection.close()

print("New database created and user 'admin' with password 'password123' added.")

# tkinter setup for the GUI
class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("800x600")
        
        # Database connection
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # GUI components
        self.create_widgets()
        self.show_products()

    def create_widgets(self):
        # Frame for input fields
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(pady=10)

        # Name, category, quantity, and price labels and entries in grid layout
        self.name_label = tk.Label(self.input_frame, text="Name")
        self.name_label.grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(self.input_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        self.category_label = tk.Label(self.input_frame, text="Category")
        self.category_label.grid(row=0, column=2, padx=5, pady=5)
        self.category_entry = tk.Entry(self.input_frame)
        self.category_entry.grid(row=0, column=3, padx=5, pady=5)

        self.quantity_label = tk.Label(self.input_frame, text="Quantity")
        self.quantity_label.grid(row=1, column=0, padx=5, pady=5)
        self.quantity_entry = tk.Entry(self.input_frame)
        self.quantity_entry.grid(row=1, column=1, padx=5, pady=5)

        self.price_label = tk.Label(self.input_frame, text="Price")
        self.price_label.grid(row=1, column=2, padx=5, pady=5)
        self.price_entry = tk.Entry(self.input_frame)
        self.price_entry.grid(row=1, column=3, padx=5, pady=5)

        # Frame for buttons (to display them side by side)
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)

        # Buttons for actions (side by side)
        self.add_button = tk.Button(self.button_frame, text="Add Product", command=self.add_product)
        self.add_button.grid(row=0, column=0, padx=5, pady=5)

        self.edit_button = tk.Button(self.button_frame, text="Edit Product", command=self.edit_product)
        self.edit_button.grid(row=0, column=1, padx=5, pady=5)

        self.delete_button = tk.Button(self.button_frame, text="Delete Product", command=self.delete_product)
        self.delete_button.grid(row=0, column=2, padx=5, pady=5)

        self.low_stock_button = tk.Button(self.button_frame, text="Low Stock Alert", command=self.low_stock_report)
        self.low_stock_button.grid(row=0, column=3, padx=5, pady=5)

        # Treeview for displaying products
        self.tree_frame = tk.Frame(self.root)
        self.tree_frame.pack(fill="both", expand=True)

        self.products_tree = ttk.Treeview(self.tree_frame, columns=("ID", "Name", "Category", "Quantity", "Price"), show="headings")
        self.products_tree.heading("ID", text="ID")
        self.products_tree.heading("Name", text="Name")
        self.products_tree.heading("Category", text="Category")
        self.products_tree.heading("Quantity", text="Quantity")
        self.products_tree.heading("Price", text="Price")
        self.products_tree.pack(fill="both", expand=True)

    def add_product(self):
        name = self.name_entry.get()
        category = self.category_entry.get()
        quantity = self.quantity_entry.get()
        price = self.price_entry.get()

        # Check if all fields are filled
        if not name or not category or not quantity or not price:
            messagebox.showerror("Input Error", "Please fill in all fields")
            return

        # Insert into database
        try:
            self.cursor.execute("INSERT INTO Products (name, category, quantity, price) VALUES (?, ?, ?, ?)",
                                (name, category, int(quantity), float(price)))
            self.conn.commit()
            messagebox.showinfo("Success", "Product added successfully!")
            self.show_products()
        except Exception as e:
            messagebox.showerror("Error", f"Error adding product: {e}")

    def edit_product(self):
        selected_item = self.products_tree.selection()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select a product to edit")
            return

        product_id = self.products_tree.item(selected_item, "values")[0]
        name = self.name_entry.get()
        category = self.category_entry.get()
        quantity = self.quantity_entry.get()
        price = self.price_entry.get()

        # Update product in the database
        try:
            self.cursor.execute('''UPDATE Products 
                                   SET name = ?, category = ?, quantity = ?, price = ? 
                                   WHERE product_id = ?''',
                                (name, category, int(quantity), float(price), product_id))
            self.conn.commit()
            messagebox.showinfo("Success", "Product updated successfully!")
            self.show_products()
        except Exception as e:
            messagebox.showerror("Error", f"Error updating product: {e}")

    def delete_product(self):
        selected_item = self.products_tree.selection()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select a product to delete")
            return

        product_id = self.products_tree.item(selected_item, "values")[0]

        try:
            self.cursor.execute("DELETE FROM Products WHERE product_id=?", (product_id,))
            self.conn.commit()
            messagebox.showinfo("Success", "Product deleted successfully!")
            self.show_products()
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting product: {e}")

    def show_products(self):
        # Clear the existing treeview
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)

        # Fetch all products
        self.cursor.execute("SELECT * FROM Products")
        products = self.cursor.fetchall()

        # Insert fetched products into the treeview
        for product in products:
            self.products_tree.insert("", "end", values=product)

    def low_stock_report(self):
        # Threshold for low stock
        threshold = 10

        # Fetch products with quantity below threshold
        self.cursor.execute("SELECT * FROM Products WHERE quantity < ?", (threshold,))
        low_stock_products = self.cursor.fetchall()

        # Show the low-stock products
        if low_stock_products:
            report = "Low Stock Products:\n"
            for product in low_stock_products:
                report += f"ID: {product[0]}, Name: {product[1]}, Category: {product[2]}, Quantity: {product[3]}, Price: {product[4]}\n"
            messagebox.showinfo("Low Stock Alert", report)
        else:
            messagebox.showinfo("Low Stock Alert", "No products are below the low stock threshold.")

    def close(self):
        self.conn.close()

# Start the tkinter application
if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close)  # Handle closing the app
    root.mainloop()
