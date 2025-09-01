import pandas as pd

class DataAnalyzer:
    """
    Performs statistical and business analysis on a sales DataFrame.
    This class is independent of input or output formats, focusing solely on extracting insights from data.
    """
    def __init__(self, df: pd.DataFrame):
        # Validate that the input is a pandas DataFrame
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input to DataAnalyzer must be a pandas DataFrame.")
        self.df = df

        # Validate required columns
        required_columns = ['valor_total', 'id_pedido', 'data_do_pedido']
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        if missing_columns:
            raise ValueError(f"DataFrame is missing required columns: {', '.join(missing_columns)}")

        # Convert 'data_do_pedido' to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(self.df['data_do_pedido']):
            self.df['data_do_pedido'] = pd.to_datetime(self.df['data_do_pedido'])

    def get_summary_stats(self):
        """
        Calculates high-level metrics about sales.

        Returns:
            dict: A dictionary containing total revenue, total orders, and average order value.
        """
        # Handle empty DataFrame to prevent errors
        if self.df.empty:
            return {'total_revenue': 0, 'total_orders': 0, 'average_order_value': 0}

        # Calculate total revenue and number of unique orders
        total_revenue = self.df['valor_total'].sum()
        total_orders = self.df['id_pedido'].nunique()
        
        # Compute average order value, handling division by zero
        average_order_value = total_revenue / total_orders if total_orders > 0 else 0

        return {
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'average_order_value': average_order_value
        }

    def get_sales_by_product(self, n_top: int = 5) -> pd.DataFrame:
        """
        Identifies the top N best-selling products based on total sales value.

        Args:
            n_top (int): Number of top products to return. Defaults to 5.

        Returns:
            pd.DataFrame: A DataFrame with the top products and their total sales values.
        """
        # Validate n_top parameter
        if not isinstance(n_top, int) or n_top <= 0:
            raise ValueError("n_top must be a positive integer.")

        # Group by product ID and sum total sales, then select top N
        sales_by_product = self.df.groupby('id_produto')['valor_total'].sum().nlargest(n_top)
        return sales_by_product.reset_index()

    def get_sales_by_period(self, period: str = 'M') -> pd.DataFrame:
        """
        Calculates total sales by time period (e.g., 'D' for day, 'W' for week, 'M' for month).

        Args:
            period (str): Time period for grouping sales. Valid options are 'D', 'W', 'M', 'Q', 'Y'.

        Returns:
            pd.DataFrame: A DataFrame with total revenue by period.
        """
        # Validate period parameter
        valid_periods = ['D', 'W', 'M', 'Q', 'Y']
        if period not in valid_periods:
            raise ValueError(f"Invalid period '{period}'. Choose from: {', '.join(valid_periods)}")

        # Set 'data_do_pedido' as index for time-based resampling
        df_indexed = self.df.set_index('data_do_pedido')
        
        # Aggregate sales by period efficiently
        sales_by_period = df_indexed['valor_total'].resample(period).sum()
        return sales_by_period.reset_index()

    def get_sales_by_category(self) -> pd.DataFrame:
        """
        Calculates total sales by product category, if category information is available.

        Returns:
            pd.DataFrame: A DataFrame with total sales by category, or empty if 'categoria' column is missing.
        """
        # Check if 'categoria' column exists
        if 'categoria' not in self.df.columns:
            return pd.DataFrame(columns=['categoria', 'valor_total'])

        # Group by category and sum total sales
        sales_by_category = self.df.groupby('categoria')['valor_total'].sum()
        return sales_by_category.reset_index()