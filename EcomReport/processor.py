import pandas as pd
from datetime import datetime

class DataProcessor:
    """
    Flexible class to process and clean sales data, capable of handling
    different header formats and missing data.
    """
    COLUMN_ALIASES = {
        'data_do_pedido': ['data', 'date', 'order_date', 'data do pedido', 'Data do Pedido'],
        'id_pedido': ['id', 'order_id', 'pedido', 'número do pedido', 'ID do Pedido'],
        'id_produto': ['produto', 'product', 'id_produto', 'id-produto', 'ID do Produto'],
        'valor_total': ['valor', 'value', 'total_value', 'valor_total', 'total', 'Valor Total']
    }

    def __init__(self, filepath):
        self.filepath = filepath
        self.df = None

    def _clean_column_name(self, name):
        """Standardizes a column name for easier comparison."""
        return str(name).lower().strip().replace(' ', '_').replace('-', '_')

    def _detect_and_map_columns(self, header_row):
        """
        Maps the file's column names to our standardized names.
        """
        mapped_columns = {}
        cleaned_header = [self._clean_column_name(col) for col in header_row]
        
        ordered_aliases = {key: self.COLUMN_ALIASES[key] for key in sorted(self.COLUMN_ALIASES)}
        for standard_name, aliases in ordered_aliases.items():
            for alias in aliases:
                alias_clean = self._clean_column_name(alias)
                if alias_clean in cleaned_header:
                    original_index = cleaned_header.index(alias_clean)
                    original_name = header_row[original_index]
                    if original_name not in mapped_columns:
                        mapped_columns[original_name] = standard_name
                        break
        return mapped_columns

    def _is_date_column(self, series):
        """Validates if a column contains dates in expected formats (DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD)."""
        try:
            # Try parsing with specific formats
            sample = series.iloc[0:10].dropna().astype(str)
            for date_format in ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']:
                parsed = pd.to_datetime(sample, format=date_format, errors='coerce')
                if parsed.notna().all():
                    return True
            return False
        except (ValueError, TypeError):
            return False

    def _is_numeric_column(self, series):
        """Checks if a column contains numeric values."""
        try:
            pd.to_numeric(series.iloc[0:10].dropna(), errors='coerce')
            return True
        except (ValueError, TypeError):
            return False
    
    def _is_id_column(self, series):
        """Identifies an ID column (integers or unique strings)."""
        try:
            numeric_series = pd.to_numeric(series.iloc[0:10].dropna(), errors='coerce')
            if numeric_series.notna().all():
                return all(x == int(x) for x in numeric_series)  # Check for integer values
            return series.iloc[0:10].nunique() == len(series.iloc[0:10].dropna())
        except (ValueError, TypeError):
            return False

    def _infer_column_map_from_data(self, df):
        """
        Infers which column corresponds to each data type.
        Prioritizes: id_pedido -> data_do_pedido -> valor_total -> id_produto.
        """
        inferred_map = {}
        remaining_cols = list(df.columns)
        print(f"Available columns for inference: {remaining_cols}")
        
        # 1. Find the id_pedido (integer IDs or unique strings)
        for col in remaining_cols:
            if self._is_id_column(df[col]):
                inferred_map[col] = 'id_pedido'
                remaining_cols.remove(col)
                print(f"Mapped {col} as id_pedido")
                break
        
        # 2. Find the date column
        for col in remaining_cols:
            if self._is_date_column(df[col]):
                inferred_map[col] = 'data_do_pedido'
                remaining_cols.remove(col)
                print(f"Mapped {col} as data_do_pedido")
                break
        
        # 3. Find the total value column (numeric with decimals)
        for col in remaining_cols:
            if self._is_numeric_column(df[col]):
                sample = df[col].iloc[0:10].dropna()
                if any('.' in str(x) for x in sample):
                    inferred_map[col] = 'valor_total'
                    remaining_cols.remove(col)
                    print(f"Mapped {col} as valor_total")
                    break
        
        # 4. Assign id_produto to the remaining column
        if remaining_cols:
            inferred_map[remaining_cols[0]] = 'id_produto'
            print(f"Mapped {remaining_cols[0]} as id_produto")

        return inferred_map
    
    def process_data(self):
        """
        Processes the sales data with logic for header detection and inference.

        Returns:
            pd.DataFrame: The cleaned and processed DataFrame.
            None: If a fatal error occurs during processing.
        """
        try:
            # Try to read the file assuming it has a header
            temp_df = pd.read_csv(self.filepath, nrows=10, skip_blank_lines=True)
            mapped_columns = self._detect_and_map_columns(temp_df.columns)
            print(f"Columns found from header: {list(mapped_columns.values())}")

            if len(mapped_columns) >= 2:
                self.df = pd.read_csv(self.filepath, skip_blank_lines=True)
                self.df = self.df.rename(columns=mapped_columns)
            else:
                # Read without header, ensuring all columns are included
                self.df = pd.read_csv(self.filepath, header=None, skip_blank_lines=True, index_col=False)
                print(f"Raw DataFrame columns: {list(self.df.columns)}")
                mapped_columns_from_data = self._infer_column_map_from_data(self.df)
                print(f"Columns inferred from data: {list(mapped_columns_from_data.values())}")
                
                # Rename columns using their indices
                self.df.columns = [mapped_columns_from_data.get(i, f'col_{i}') for i in range(len(self.df.columns))]

        except FileNotFoundError:
            print(f"Error: File not found at {self.filepath}")
            return None
        except Exception as e:
            print(f"An error occurred while loading the file: {e}")
            return None

        try:
            # Validate if all essential columns exist
            required_columns = ['data_do_pedido', 'id_produto', 'id_pedido', 'valor_total']
            found_in_df = [col for col in required_columns if col in self.df.columns]
            print(f"Columns found in the final DataFrame: {found_in_df}")
            print(f"Required columns: {required_columns}")

            if not all(col in self.df.columns for col in required_columns):
                missing_cols = set(required_columns) - set(self.df.columns)
                raise ValueError(f"Could not identify all necessary columns. Missing: {missing_cols}")

            # Drop rows with missing values
            self.df.dropna(subset=required_columns, inplace=True)
            if self.df.empty:
                raise ValueError("After cleaning, the DataFrame is empty.")

            # Convert data types
            self.df['data_do_pedido'] = pd.to_datetime(self.df['data_do_pedido'], format='%Y-%m-%d', errors='coerce')
            self.df['valor_total'] = pd.to_numeric(self.df['valor_total'], errors='coerce')
            self.df['id_pedido'] = self.df['id_pedido'].astype(str)
            self.df['id_produto'] = self.df['id_produto'].astype(str)

            # Drop rows with conversion errors (NaT or NaN)
            self.df.dropna(subset=['data_do_pedido', 'valor_total'], inplace=True)

        except (KeyError, ValueError) as e:
            print(f"Data type conversion error. Check the file format: {e}")
            return None

        # Filter out invalid values
        self.df = self.df[self.df['valor_total'] >= 0]
        
        return self.df