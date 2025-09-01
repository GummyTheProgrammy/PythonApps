import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import os

class SalesReporter:
    """
    Generates sales charts and compiles a visual report into a single image.
    Responsible for data presentation, not analysis.
    """
    def __init__(self, data_analyzer_results):
        """
        Initializes the SalesReporter with analysis results.

        Args:
            data_analyzer_results (dict): Dictionary containing analysis results from DataAnalyzer.
        """
        self.results = data_analyzer_results
        self.temp_charts = []

    def _create_chart(self, df, x_col, y_col, title, filename, kind='bar'):
        """
        Private method to generate and save a chart as a temporary image.

        Args:
            df (pd.DataFrame): DataFrame containing the data to plot.
            x_col (str): Column name for the x-axis.
            y_col (str): Column name for the y-axis.
            title (str): Chart title.
            filename (str): File path to save the chart.
            kind (str): Type of chart ('bar', 'line', or 'donut'). Defaults to 'bar'.

        Raises:
            ValueError: If required columns are missing or invalid chart kind is specified.
        """
        # Validate input columns
        if x_col not in df.columns or y_col not in df.columns:
            raise ValueError(f"Missing required columns: {x_col}, {y_col}")

        # Set plot style and figure size
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.figure(figsize=(8, 5))

        # Define a consistent color palette
        colors = ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f']
        
        if kind == 'bar':
            plt.bar(df[x_col], df[y_col], color=colors[0])
            plt.xticks(rotation=45, ha='right')
        elif kind == 'line':
            plt.plot(df[x_col], df[y_col], marker='o', linestyle='-', color=colors[1])
        elif kind == 'donut':
            plt.pie(df[y_col], labels=df[x_col], autopct='%1.1f%%', colors=colors, 
                    wedgeprops=dict(width=0.3), startangle=90)
            plt.axis('equal')  # Ensure circular shape
        else:
            raise ValueError(f"Invalid chart kind: {kind}. Choose from 'bar', 'line', 'donut'.")

        # Set chart title and labels
        plt.title(title, fontsize=16)
        if kind != 'donut':  # Donut chart labels are on the slices
            plt.xlabel(x_col.replace('_', ' ').title())
            plt.ylabel(y_col.replace('_', ' ').title())
        
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
        self.temp_charts.append(filename)

    def generate_charts(self):
        """
        Orchestrates the creation of different charts for the report.
        """
        # Chart 1: Sales by Product (Bar)
        sales_by_product_df = self.results.get('sales_by_product')
        if sales_by_product_df is not None and not sales_by_product_df.empty:
            self._create_chart(
                df=sales_by_product_df,
                x_col='id_produto',
                y_col='valor_total',
                title='Top 5 Best-Selling Products',
                filename='top_products_chart.png',
                kind='bar'
            )

        # Chart 2: Sales Over Time (Line)
        sales_by_period_df = self.results.get('sales_by_period')
        if sales_by_period_df is not None and not sales_by_period_df.empty:
            self._create_chart(
                df=sales_by_period_df,
                x_col='data_do_pedido',
                y_col='valor_total',
                title='Revenue by Period',
                filename='sales_over_time_chart.png',
                kind='line'
            )

        # Chart 3: Sales Distribution by Product (Donut)
        if sales_by_product_df is not None and not sales_by_product_df.empty:
            self._create_chart(
                df=sales_by_product_df,
                x_col='id_produto',
                y_col='valor_total',
                title='Sales Distribution by Product',
                filename='donut_chart.png',
                kind='donut'
            )

        # Chart 4: Sales Distribution by Category (Donut)
        sales_by_category_df = self.results.get('sales_by_category')
        if sales_by_category_df is not None and not sales_by_category_df.empty:
            self._create_chart(
                df=sales_by_category_df,
                x_col='categoria',
                y_col='valor_total',
                title='Sales Distribution by Category',
                filename='category_donut_chart.png',
                kind='donut'
            )

    def compile_report(self):
        """
        Compiles all charts and text data into a single report image.

        Returns:
            str: Path to the saved report image.
        """
        report_path = 'sales_report.png'
        
        # Calculate report dimensions to fit the right pane (70% of window width)
        report_width = 700  # Approximately 70% of 1000px, adjusted for margins
        chart_heights = [Image.open(path).height for path in self.temp_charts]
        total_chart_height = sum(chart_heights) + 50 * (len(self.temp_charts) - 1)  # Space between charts
        report_height = total_chart_height + 250  # Space for title and summary
        
        # Create a blank image for the final report
        report_image = Image.new('RGB', (report_width, report_height), 'white')
        draw = ImageDraw.Draw(report_image)

        try:
            # Try to use a common font; fall back to default if not found
            font_title = ImageFont.truetype("arial.ttf", 30)
            font_text = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()

        # Add report title
        draw.text((30, 30), "E-commerce Sales Report", font=font_title, fill='black')

        # Add summary statistics
        summary = self.results.get('summary_stats', {})
        text_summary = (f"Total Revenue: R$ {summary.get('total_revenue', 0):,.2f}\n"
                        f"Total Orders: {int(summary.get('total_orders', 0))}\n"
                        f"Average Order Value: R$ {summary.get('average_order_value', 0):,.2f}")
        draw.text((30, 100), text_summary, font=font_text, fill='black')

        # Add charts to the report
        y_offset = 200
        for img_path in self.temp_charts:
            chart = Image.open(img_path)
            # Resize chart to fit report width
            chart.thumbnail((report_width - 60, chart.height), Image.Resampling.LANCZOS)
            report_image.paste(chart, (30, y_offset))
            y_offset += chart.height + 50
            chart.close()
            os.remove(img_path)  # Remove temporary file

        report_image.save(report_path)
        return report_path