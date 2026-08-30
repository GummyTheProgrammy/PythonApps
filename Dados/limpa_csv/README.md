````markdown

# CSV Cleaning Script with Python

This document explains how the `limpa_csv.py` script works, a Python tool designed to process CSV files, remove rows with null values, and save the result to a new file. The script has been enhanced to provide real-time feedback on its progress.

---

### How to Use

To run the script, you need to have **Python** and the **`pandas`** and **`tqdm`** libraries installed. If you don't already have them, install them via the terminal:

```bash
pip install pandas tqdm

````

Then, run the script from the terminal, passing the name of your CSV file as an argument:

```bash
python limpa_csv.py nome_do_seu_arquivo.csv

```

**Example:**

```bash
python limpa_csv.py customers.csv

```

-----

### How it Works

The `limpa_csv.py` script uses two main libraries for its functionality:

1. **`pandas`**: The standard Python library for data manipulation and analysis. It is used to read the CSV file into a **DataFrame** (a table-like data structure).

2. **`tqdm`**: This library is responsible for creating the progress bar. It involves the process of reading the file, displaying a progress bar that updates in real time, providing visual feedback.

The script workflow is as follows:

1. **File Reading**: Instead of loading the entire file at once (which could be inefficient for large files), the script reads it in chunks (`chunksize`). With each chunk read, the `tqdm` progress bar is updated.

2. **Data Processing**: After the reading is complete, all chunks are concatenated into a single DataFrame. The `pandas` method **`dropna()`** is then applied, which efficiently removes any row containing at least one null value (`null`, `NaN`, etc.) in any of its columns.

3. **New File Creation**: The script calculates the number of rows that were removed and creates a name for the new file. The suffix **`_null_removed`** is added to the original name (for example, `customers_null_removed.csv`).

4. **Export**: Finally, the cleaned DataFrame is exported to the new CSV file using the **`to_csv()`** method. The `index=False` option is used to ensure that the DataFrame's index column is not included in the final file.

-----

### Benefits

* **Efficiency**: Processes large files without overloading computer memory by reading them in blocks.

* **Visual Feedback**: The progress bar offers an interactive experience, allowing you to track the progress of the cleanup in real time.

* **Simplicity**: Automates the data cleanup process, which is a crucial step in any database project, without requiring manual intervention.

<!-- end list -->

---

### Contributions

Contributions are welcome! You can:

- Add new features

- Improve data processing or the user interface/user experience.

- Submit issues or pull requests via GitHub.

Follow the guidelines in the main `PythonApps` repository (`../README.md`) to contribute.

---

### License

This project is licensed. See the [LICENSE](../LICENSE) file in the main repository for details.

```
```