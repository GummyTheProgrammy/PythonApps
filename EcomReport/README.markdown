# EcomReport

EcomReport is a Python-based desktop application designed to generate detailed sales reports from e-commerce CSV data. Part of the [PythonApps](https://github.com/GummyTheProgrammy/PythonApps) repository, it processes sales data, performs statistical analysis, and creates professional visualizations (bar, line, and donut charts) with PDF export capabilities. The app features a modular architecture for scalability and maintainability.

---

### Key Features

* **Robust Data Processing**: Cleans and validates raw CSV sales data, handling issues like missing values, incorrect data types, and malformed entries.
* **Statistical Analysis**: Calculates key metrics such as total revenue, total orders, average order value, top-selling products, sales by period, and sales by category.
* **Visual Reporting**: Generates visualizations including bar charts (top products), line charts (revenue over time), and donut charts (sales distribution by product and category), with the option to save as PDF.
* **User-Friendly Interface**: A Tkinter-based GUI with a split layout (30% for CSV preview, 70% for report display) for intuitive interaction.

---

### Technologies & Libraries

* **Python**: Core language for the application.
* **Tkinter**: Powers the graphical user interface for file selection, data preview, and report display.
* **Pandas**: Handles data manipulation and analysis for processing and aggregating sales data.
* **Matplotlib**: Creates high-quality visualizations (bar, line, and donut charts).
* **Pillow**: Combines charts and text into a single report image and supports PDF export.

---

### Installation

1. Ensure you have cloned the `PythonApps` repository:
   ```bash
   git clone https://github.com/<your-username>/PythonApps.git
   cd PythonApps/EcomReport
   ```

2. Install dependencies from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

3. Verify that Python 3.8+ is installed on your system.

---

### Usage

1. Navigate to the `EcomReport` directory:
   ```bash
   cd PythonApps/EcomReport
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. In the GUI:
   - Click **"1. Select CSV File"** to upload a sales CSV.
   - Click **"2. Generate Report"** to process the data and display the report (charts and statistics).
   - Click **"3. Save as PDF"** to export the report as a PDF file.

The interface displays a CSV preview on the left (30% width) and the generated report on the right (70% width).

---

### CSV File Format

The application expects CSV files with the following columns:
- `id_pedido`: Unique order ID (e.g., `1001`).
- `data_do_pedido`: Order date in `YYYY-MM-DD` format (e.g., `2025-01-15`).
- `valor_total`: Total order value (numeric, e.g., `150.50`).
- `id_produto`: Product ID (e.g., `PROD001`).
- `categoria`: Product category (optional, e.g., `Eletrônicos`).

The app handles CSVs with or without headers and ignores irrelevant columns (e.g., `cor`, `tamanho`, `sabor`). Example CSV (`test1.csv`):
```csv
cor,tamanho,id_produto,sabor,valor_total,categoria,data_do_pedido,id_pedido
vermelho,M,PROD001,doce,150.50,Eletrônicos,2025-01-15,1001
azul,G,PROD002,salgado,89.90,Roupas,2025-02-10,1002
```

Sample CSV files (`test1.csv`, `test2.csv`, `test3.csv`) are included in the `EcomReport` directory for testing.

---

### Example Output

The generated report includes:
- **Summary Statistics**: Total revenue, total orders, and average order value.
- **Bar Chart**: Top 5 best-selling products by total sales.
- **Line Chart**: Revenue over time (by month).
- **Donut Charts**: Sales distribution by product and category (if `categoria` is present in the CSV).

The report is displayed in the GUI and can be saved as a PDF file.

---

### Project Structure

* **`app.py`**: Main application file, orchestrates data flow and manages the Tkinter GUI.
* **`processor.py`**: Handles CSV data ingestion, validation, and cleaning.
* **`analyzer.py`**: Performs statistical analysis and data aggregation.
* **`reporter.py`**: Generates visualizations and compiles the report image.
* **`test1.csv`, `test2.csv`, `test3.csv`**: Sample CSV files for testing.

---

### Contributing

Contributions to EcomReport are welcome! You can:
- Add new features (e.g., additional chart types, data filters).
- Improve data processing or UI/UX.
- Submit issues or pull requests via GitHub.

Please follow the guidelines in the main `PythonApps` repository (`../README.md`) for contributing.

---

### License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file in the main repository for details.