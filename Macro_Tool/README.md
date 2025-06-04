# Macro Tool

A simple text macro tool that enhances your productivity by providing quick access to frequently used text snippets. Save any text to function keys (F1-F12) and access them instantly with a single key. Perfect for repetitive tasks or quick text insertion.

## Features

- Text storage on keys (Default: F1-F12)
- Customizable keybindings
- Multilingual interface (English, German, Spanish)
- Customizable color scheme
- System tray integration
- Optional automatic enter key after text insertion

## Installation

1. Ensure Python 3.x is installed
2. Download the project files
3. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Launch the application:
   ```
   python macro_tool.py
   ```

## Usage

1. Enter your desired text in the input fields
2. Enable the enter key option if needed
3. Use the assigned function keys to insert your text

## Customization

- Modify colors through the settings interface
- Reassign function keys to your preference
- Select your preferred language

## Built With

- Python - Main programming language
- tkinter - For creating the user interface
- keyboard - For detecting key presses
- pyautogui - For automating text input
- pystray - For the system tray icon
