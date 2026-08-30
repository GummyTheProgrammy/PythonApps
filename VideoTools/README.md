# Video Processing Automation Suite

This document details the operation of the scripts contained in the `VideoTools` folder. It is a set of Python tools designed to automate the manipulation, analysis and processing of videos in batch, optimizing editing and media management workflows.

The included scripts are:
* `SmartVideoCutter.py`
* `TimelineTotalizer.py`
* `MultiVideoInspector.py`
* `MultiVideoToFrames.py`

---

### How to Use

To run any of the scripts, you need to have **Python** installed, along with the **`moviepy`**, **`tqdm`**, **`keyboard`**, **`pillow`** and **`numpy`** libraries. Install them all via terminal with the command:

```bash
pip install moviepy tqdm keyboard pillow numpy

```

#### 1. SmartVideoCutter.py

An interactive tool to join videos together and cut them into smaller segments automatically.

```bash
python SmartVideoCutter.py

```

* **Functionality:** The script will ask for the folder path. Use the **arrow keys (↑/↓)** to adjust the cutting duration dynamically. Choose the resolution (Horizontal, Vertical or Custom) and naming pattern.

#### 2. TimelineTotalizer.py

Calculates the total length of all videos in a folder structure (including subfolders).

```bash
python TimelineTotalizer.py

```

* **Output:** Displays the formatted total time (HH:MM:SS), as well as totals in minutes and seconds, depending on the accumulated duration.

#### 3. MultiVideoInspector.py

Quickly scan a folder and list the resolution (Width x Height) of each video file.

```bash
python MultiVideoInspector.py

```

* **Utility:** Perfect for identifying non-standard files (e.g. mixing 1080p with 4K) before starting an edit.

#### 4. MultiVideoToFrames.py

Extracts all frames from all videos in a folder and saves them as PNG images.

```bash
python MultiVideoToFrames.py

```

* **Note:** The script uses a visual progress bar to track the extraction, which can be intensive.

---

### How It Works

These scripts demonstrate advanced use of the **`moviepy`** library combined with file system manipulation (`os`, `shutil`) and user interaction.

1. **Interactivity and UX (`SmartVideoCutter.py`)**: Unlike static command-line scripts, this file uses the **`keyboard`** library to capture key events in real time, allowing fine-tuning of parameters (such as cut duration) without the need to repeatedly enter numbers. It also implements *input* validation logic to ensure that resolutions and paths are valid.
2. **Recursive Processing (`TimelineTotalizer.py`)**: Uses `os.walk()` to navigate deep into directory trees. This demonstrates the ability to handle complex file structures, summing metadata from hundreds of files without running out of memory.
3. **Memory Management (`MultiVideoToFrames.py`)**: When dealing with extracting thousands of images, the script does not load the entire video into RAM. It uses **iterators** (`clip.iter_frames()`) to process and save one frame at a time, ensuring efficiency even in long videos.
4. **Smart Concatenation**: `SmartVideoCutter` normalizes videos to a target resolution before concatenating, avoiding common *codec* compatibility errors or varying dimensions during the `concatenate_videoclips` process.

---

### Benefits

* **Productivity**: Automates tasks that would take hours manually, such as cutting dozens of videos into equal parts or adding up the length of hundreds of clips.
* **Visual Feedback**: All scripts (especially long-running ones) implement progress bars (`tqdm` or native to `moviepy`) and bilingual status messages (PT-BR / EN-US), improving the user experience.
* **Flexibility**: The code supports several video formats (`.mp4`, `.avi`, `.mkv`, etc.) and allows customized resolution and naming settings.

---

### Contributions

Contributions to the PythonApps repository are welcome! Ideas for improvements to the VideoTools folder:

* Add GPU acceleration support (NVENC/CUDA) for faster rendering.
* Create a graphical interface (GUI) with `tkinter` or `PyQt` to select files via "drag and drop".
* Implement image filters (e.g. black and white, contrast) in the frame extractor.

Follow the guidelines in the main repository (`../README.md`) to contribute.

---

### License

This project is licensed. See the [LICENSE](https://www.google.com/search?q=../LICENSE) file in the main repository for details.