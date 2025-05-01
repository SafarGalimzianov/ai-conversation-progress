# Task Progress App

A simple, elegant application for tracking progress on tasks and subtasks with visual feedback.

![Task Progress App Screenshot](icon.png)

## Features

- **Visual Progress Tracking**: See your progress with an intuitive circle-based progress bar
- **Task Management**: Create, edit, and complete main tasks and subtasks
- **Persistence**: App automatically saves your tasks between sessions
- **User-Friendly Interface**: Clean, minimal design focused on productivity
- **Keyboard Shortcuts**: Efficient task editing with keyboard support

## Installation

### Prerequisites

- Python 3.12 or higher
- PyQt5

### Method 1: From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/SafarGalimzianov/ai-conversation-progress.git
   cd ai-conversation-progress
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .
   ```

3. Run the application:
   ```bash
   python main.py
   ```

### Method 2: Desktop Integration (Linux)

1. Make the wrapper script executable:

   ```bash
   chmod +x run.sh
   ```

2. Create a desktop entry file:
   bash
   mkdir -p ~/.local/share/applications/
   cp task-progress.desktop ~/.local/share/applications/
   update-desktop-database ~/.local/share/applications/
   

## Usage

### Managing Tasks

- **Main Task**: Click on the main task title to edit it
- **Add Subtask**: Click the "+ Add Subtask" button
- **Edit Subtask**: Left-click on any subtask text
- **Delete Subtask**: Middle-click on any subtask text
- **Complete Subtask**: Check the circular checkbox next to a subtask

### Keyboard Shortcuts

- **Enter**: Finish editing and save changes
- **Escape**: Finish editing and save changes
- **Ctrl+Enter**: Insert a new line while editing a subtask

## Data Storage

The application automatically saves your tasks to `~/.task_progress_app.json` when you close it and loads them when you start it again.

## Technical Details

- Built with PyQt5
- Uses JSON for data persistence
- Custom-drawn progress indicators

## License

MIT License - See the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.