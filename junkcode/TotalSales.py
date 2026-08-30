import pandas as pd

# Load the dataset with a different encoding
try:
    df = pd.read_csv('Superstore.csv', encoding='latin-1')
except UnicodeDecodeError:
    df = pd.read_csv('Superstore.csv', encoding='iso-8859-1')

# Calculate total sales
total_sales = df['Sales'].sum()
print(f"Total Sales: {total_sales}")

# Calculate sales by category
sales_by_category = df.groupby('Category')['Sales'].sum().reset_index()
sales_by_category['Percentage'] = (sales_by_category['Sales'] / total_sales) * 100
print("\nSales by Category:")
print(sales_by_category)