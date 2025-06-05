# Macro_Tool

A simple text macro tool that lets you assign custom text to function keys (F1–F12) for quick and easy access. Ideal for automating repetitive typing.

## Features

- Text storage on keys (Default: F1-F12)
- Customizable keybindings
- Multilingual interface (English, German, Spanish)
- Customizable color scheme
- System tray integration
- Optional automatic enter key after text insertion

## Installation

1. Make sure Python 3.x is installed
2. Clone this repository
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Start the program:
   ```
   python macro_tool.py
   ```
2. Enter text in the input fields
3. Optional: Enable the Enter checkbox for automatic Enter key
4. Macros can be called using the assigned keys

## Customization

- Modify colors through the settings interface
- Reassign function keys to your preference
- Select your preferred language

## Technical Details

- Python - Main programming language
- tkinter - For creating the user interface
- keyboard - For detecting key presses
- pyautogui - For automating text input
- pystray - For the system tray icon

