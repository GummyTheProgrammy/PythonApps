# Simple Counter Widget

Not much to say, just a counter really, you can add 1, decrease 1, copy the current value and close the application. 
Features: if you click anywhere else then the buttons, you can freely drag it around. If you open another windows it will remain on top, super useful for when keeping track between tabs.

---

### How to Use

To run the script, you need to have **Python** and the **`pandas`** and **`tqdm`** libraries installed. If you don't already have them, install them via the terminal:

To run the script, you need to have **Python** and the **`PySide6`** library installed. If you don't already have them, install them via the terminal:

```bash
pip install PySide6

````

Then, run the script from the terminal:

```bash
python Counter.py

```

**Note**: Ensure you have an image named **`circle.png`** in the same directory as the script. If the image is not found, the program will automatically generate a temporary blue circular background for you.

-----

### How it Works

The `Counter.py` script creates a customized, frameless desktop widget using the **PySide6** framework:

1. **`PySide6 (Qt)`**: The core library used to create the Graphical User Interface (GUI). It handles the window transparency, custom shapes (masks), and the rendering of the digital counter.
2. **Custom Window Masking**: The script uses `QBitmap` and `setMask` to create a perfectly circular window, even though the underlying window is technically a square.
3. **Transparent Interaction Layer**: It implements invisible clickable areas (`QLabel`) positioned strategically over the background image to function as buttons without visual clutter.

The script workflow is as follows:

1. **Initialization**: The widget is set to be "Always on Top" and "Frameless." It loads the `circle.png` background and scales it to 200x200 pixels.
2. **Event Handling**: Since the window is frameless, a custom `mouseMoveEvent` and `mousePressEvent` logic is implemented to allow you to drag the gadget anywhere on your screen.
3. **Counter Logic**: It maintains an internal integer state. Clicking the "Plus" or "Minus" areas updates this state, which is then formatted as a 4-digit string (e.g., `0001`) and displayed using a digital-style font.
4. **Clipboard Integration**: The "Copy" area uses `QApplication.clipboard()` to instantly send the current counter value to your system's clipboard for use in other applications.

---

### Benefits

* **Minimalist Design**: A clean, circular UI that stays on top of other windows without the bulk of standard title bars or borders.
* **Customizable Interaction**: Easily adjust button positions, sizes, and transparency levels directly in the code to match any background image.
* **Low Resource Usage**: Built on Qt, ensuring smooth performance and quick response times for counter increments and dragging.
* **Ready-to-Use**: Includes a fallback mechanism that generates its own assets if the background image is missing.

---

### Contributions

Contributions are welcome! You can:

* Add new features (like sound effects on click, or visual confirmation when the content is copied).
* Improve the UI/UX or add support for multiple themes.
* Submit issues or pull requests via GitHub.

Follow the guidelines in the main repository to contribute.

---

### License

This project is licensed. See the [LICENSE] file in the main repository for details.

---