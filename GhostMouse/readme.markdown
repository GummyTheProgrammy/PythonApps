# Mouse Recording and Playback Robot with Python

This document explains how the `RecordMouse.py` and `ReproduceMouse.py` scripts work, tools designed to automate repetitive tasks by capturing mouse movements and clicks and playing them back in a continuous loop.

---

### How to Use

To run the scripts, you need to have **Python** and the **`pynput`** and **`pyautogui`** libraries installed. Install them via terminal:

```bash
pip install pynput pyautogui

```

**Step 1: Recording**
Run the recording script to capture your movements:

```bash
python RecordMouse.py

```

Follow the instructions in the console: type 's' to start, perform the actions and press **ENTER** to finish and save the `mouse_events.json` file.

**Step 2: Reproduction**
Run the replay script to replay the recorded actions:

```bash
python ReproduceMouse.py

```

You will have 5 seconds to switch to the desired window before execution begins.

---

### How It Works

The system is divided into two modules that use specific libraries to interact with the hardware:

1. **`pynput`**: Used in `RecordMouse.py` to monitor the mouse in real time. It allows the script to listen for movement and click events without blocking the main program from running.
2. **`pyautogui`**: Used in `ReproduceMouse.py` to control the mouse cursor and simulate physical clicks based on coordinates and times extracted from the JSON file.

The workflow is as follows:

1. **Event Capture**: The recording script records the action (move, press or release), the `(x, y)` coordinates and, most importantly, the **delay** (time elapsed between one event and another) to ensure that playback is natural.
2. **Storage**: The data is structured in a Python dictionary and exported to a `mouse_events.json` file. This allows you to record once and play back as many times as you want, even on different days.
3. **Accurate Playback**: The playback script reads the JSON and uses `time.sleep()` to respect the original intervals, ensuring that the automation speed is identical to the original recording.
4. **Security (Fail-Safe)**: The reproduction script has a security lock. If you lose control, simply move the mouse sharply to the **top left corner (0,0)** of the screen to stop the execution immediately.

---

### Benefits

* **Loop Automation**: Unlike simple macros, this robot runs in an infinite loop until it is stopped manually.
* **Fidelity**: Captures the exact time between movements, allowing you to interact with interfaces that have specific loading times.
* **Integrated Security**: PyAutoGUI's *Fail-Safe* feature prevents the computer from being "stuck" in an automation if something goes wrong.

---

### Contributions

Contributions to this project are welcome! You can:

* Add support for recording keyboard keys.
* Implement a graphical interface (GUI) to manage recordings.
* Create a function to adjust the playback speed (ex: 2x faster).

Follow the guidelines in the main repository to submit your improvements via Pull Request.

---

### License

This project is licensed. See the [LICENSE](https://www.google.com/search?q=../LICENSE) file in the main repository for details.