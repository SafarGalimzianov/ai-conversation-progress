#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QPointF, QEvent
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QCheckBox, QInputDialog, QMessageBox, QDialog, QLineEdit, QPushButton,
    QTextEdit
)
from PyQt5.QtWidgets import QSizePolicy

# Define colors
COLOR_GREEN = QColor("#8ec07c")
COLOR_GRAY = QColor("#bdbdbd")
COLOR_LIGHT_GRAY = QColor("#eeeeee") # Background for progress bar circles
COLOR_DARK_GRAY = QColor("#616161") # Text color

class ProgressBar(QWidget):
    """Custom progress bar with circles and lines."""
    def __init__(self, total_steps=1, parent=None):
        super().__init__(parent)
        self._total_steps = max(1, total_steps)
        self._completed_steps = set()  # Track which specific steps are completed
        self.setMinimumHeight(30)

    def set_total_steps(self, steps):
        self._total_steps = max(1, steps)
        self._completed_steps = set(s for s in self._completed_steps if s < self._total_steps)
        self.update()  # Trigger repaint

    def set_step_completed(self, step_index, completed):
        if 0 <= step_index < self._total_steps:
            if completed:
                self._completed_steps.add(step_index)
            else:
                self._completed_steps.discard(step_index)
            self.update()  # Trigger repaint

    # Keep the original set_current_step for compatibility
    def set_current_step(self, step):
        self._completed_steps = set(range(step))
        self.update()  # Trigger repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        padding = 10
        diameter = min(height - 2 * padding, (width - 2 * padding) / (self._total_steps + (self._total_steps - 1) * 0.5))
        if self._total_steps == 1:
            step_width = 0
        else:
            step_width = (width - 2 * padding - diameter) / (self._total_steps - 1)

        y_center = height / 2

        pen_gray = QPen(COLOR_GRAY, 2)
        pen_green = QPen(COLOR_GREEN, 2)
        brush_green = QBrush(COLOR_GREEN)
        brush_light_gray = QBrush(COLOR_LIGHT_GRAY)
        
        # Draw lines first
        painter.setPen(pen_gray)
        for i in range(self._total_steps - 1):
            x1 = padding + diameter / 2 + i * step_width
            x2 = padding + diameter / 2 + (i + 1) * step_width
            painter.drawLine(QPointF(x1, y_center), QPointF(x2, y_center))

        # Draw green lines between completed steps that are adjacent
        painter.setPen(pen_green)
        for i in range(self._total_steps - 1):
            if i in self._completed_steps and i + 1 in self._completed_steps:
                x1 = padding + diameter / 2 + i * step_width
                x2 = padding + diameter / 2 + (i + 1) * step_width
                painter.drawLine(QPointF(x1, y_center), QPointF(x2, y_center))

        # Draw circles
        for i in range(self._total_steps):
            x = padding + i * step_width
            rect = QRectF(x, y_center - diameter / 2, diameter, diameter)

            if i in self._completed_steps:
                # Completed step: Green fill, green border
                painter.setPen(pen_green)
                painter.setBrush(brush_green)
                painter.drawEllipse(rect)
                # Draw checkmark
                pen_white = QPen(Qt.white, 2)
                painter.setPen(pen_white)
                painter.drawLine(QPointF(rect.center().x() - diameter * 0.2, rect.center().y()),
                                 QPointF(rect.center().x() - diameter * 0.05, rect.center().y() + diameter * 0.2))
                painter.drawLine(QPointF(rect.center().x() - diameter * 0.05, rect.center().y() + diameter * 0.2),
                                 QPointF(rect.center().x() + diameter * 0.2, rect.center().y() - diameter * 0.2))
            else:
                # Future step: Gray border, light gray fill
                painter.setPen(pen_gray)
                painter.setBrush(brush_light_gray)
                painter.drawEllipse(rect)


class TaskProgressApp(QWidget):
    def __init__(self):
        super().__init__()
        self.subtasks = [] # List to hold tuples of (QCheckBox, QLabel)
        self._current_editor = None # To hold the active QLineEdit
        self._edited_label = None   # To hold the QLabel being edited
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Task Progress')
        # self.setStyleSheet("background-color: #f0f0f0;") # Optional: Set background

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # --- Main Task Label ---
        self.main_task_label = QLabel('Main Task')
        font = self.main_task_label.font()
        font.setPointSize(16)
        font.setBold(True)
        self.main_task_label.setFont(font)
        self.main_task_label.setStyleSheet(f"color: {COLOR_DARK_GRAY.name()};")
        self.main_task_label.mousePressEvent = self.start_editing_main_task
        main_layout.addWidget(self.main_task_label)

        # --- Progress Bar ---
        # Container for padding/border
        progress_container = QWidget()
        progress_container.setStyleSheet("border: 1px solid #dcdcdc; border-radius: 5px; background-color: white;")
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setContentsMargins(10, 10, 10, 10) # Inner padding

        self.progress_bar = ProgressBar(total_steps=1) # Start with 4 steps
        progress_layout.addWidget(self.progress_bar)
        main_layout.addWidget(progress_container)


        # --- Subtasks ---
        self.subtasks_layout = QVBoxLayout()
        self.subtasks_layout.setSpacing(10)

        # Add initial subtasks
        self.add_subtask("Subtask 1", checked=False)
        # Add the "Add Subtask" button
        self.add_button = QPushButton("+ Add Subtask")
        self.add_button.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                border: 1px solid {COLOR_GRAY.name()};
                border-radius: 4px;
                padding: 6px 12px;
                color: {COLOR_DARK_GRAY.name()};
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: #f5f5f5;
                border: 1px solid {COLOR_GREEN.name()};
            }}
        """)
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.clicked.connect(self.on_add_subtask_clicked)
        
        main_layout.addLayout(self.subtasks_layout)
        main_layout.addWidget(self.add_button)
        main_layout.addStretch(1) # Push everything up

        self.update_progress() # Initial progress update
        self.resize(400, 300) # Set initial size
        self.show()


    def on_add_subtask_clicked(self):
        # Create a new subtask with a default name
        subtask_num = len(self.subtasks) + 1
        self.add_subtask(f"Subtask {subtask_num}", checked=False)
        
        # Update the progress bar
        self.progress_bar.set_total_steps(len(self.subtasks))
        self.update_progress()


    def add_subtask(self, text="New Subtask", checked=False):
        subtask_container = QWidget()
        subtask_layout = QHBoxLayout(subtask_container)  # Set container as parent for layout
        subtask_layout.setContentsMargins(0, 0, 0, 0)

        checkbox = QCheckBox()
        checkbox.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 1px solid {COLOR_GRAY.name()};
                border-radius: 9px; /* Make it round */
                background-color: {COLOR_LIGHT_GRAY.name()};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLOR_GREEN.name()};
                border: 1px solid {COLOR_GREEN.name()};
            }}
            /* Removed unsupported :after selector (content/display) to silence warnings */
        """)
        checkbox.setChecked(checked)
        checkbox.stateChanged.connect(self.update_progress)

        label = QLabel(text)
        label.setStyleSheet(f"color: {COLOR_DARK_GRAY.name()};")
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        label.setWordWrap(True)  # Enable text wrapping for multi-line display
        
        # Make the label clickable by enabling mouse tracking and setting attributes
        label.setMouseTracking(True)
        label.setAttribute(Qt.WA_Hover)
        label.setCursor(Qt.PointingHandCursor)  # Show hand cursor on hover
        label.setToolTip("Left-click to edit, middle-click to delete")
        
        # Replace direct lambda with a call to a method that handles different mouse buttons
        label.mousePressEvent = lambda event, lbl=label, container=subtask_container: self.handle_subtask_mouse_event(event, lbl, container)

        subtask_layout.addWidget(checkbox)
        subtask_layout.addWidget(label)

        self.subtasks_layout.addWidget(subtask_container)
        self.subtasks.append((checkbox, label))

        self.progress_bar.set_total_steps(len(self.subtasks))
        self.update_progress()

    def handle_subtask_mouse_event(self, event, label, container):
        # Left button: edit the subtask
        if event.button() == Qt.LeftButton:
            self.start_editing_subtask(event, label)
        # Middle button: delete the subtask
        elif event.button() == Qt.MiddleButton:
            self.delete_subtask(label, container)

    def delete_subtask(self, label, container):
        # Find the subtask in our list
        for i, (checkbox, lbl) in enumerate(self.subtasks):
            if lbl == label:
                # Remove from our list
                del self.subtasks[i]
                
                # Remove from layout
                self.subtasks_layout.removeWidget(container)
                container.deleteLater()
                
                # Update the progress bar
                self.progress_bar.set_total_steps(len(self.subtasks))
                self.update_progress()
                break

    def edit_main_task_label(self, event):
        # Finish any inline subtask editing first
        if self._current_editor:
            self.finish_editing_subtask()
        text, ok = QInputDialog.getText(self, 'Edit Main Task', 'Enter new task name:', QLineEdit.Normal, self.main_task_label.text())
        if ok and text:
            self.main_task_label.setText(text)


    def update_progress(self):
        # Finish any inline editing before updating progress/styles
        if self._current_editor:
            # if editing main task, finish that, else finish subtask
            if self._edited_label == self.main_task_label:
                self.finish_editing_main_task()
            else:
                self.finish_editing_subtask()

        # Update each subtask in the progress bar
        for i, (checkbox, label) in enumerate(self.subtasks):
            is_checked = checkbox.isChecked()
            
            # Update progress bar for this specific subtask
            self.progress_bar.set_step_completed(i, is_checked)
            
            # Update subtask styling
            if is_checked:
                label.setStyleSheet(f"color: {COLOR_DARK_GRAY.name()}; text-decoration: line-through;")
            else:
                label.setStyleSheet(f"color: {COLOR_DARK_GRAY.name()}; text-decoration: none;")


    def start_editing_main_task(self, event):
        # Finish any other inline editing first
        if self._current_editor:
            # Decide if the current edit should be finished or cancelled
            # For simplicity, we finish it.
            if self._edited_label == self.main_task_label:
                 self.finish_editing_main_task()
            else:
                 self.finish_editing_subtask()
            # Check if finishing cleared the editor (it should have)
            if self._current_editor: return # Avoid starting a new edit if the old one failed to finish

        self._edited_label = self.main_task_label
        layout = self.layout() # Get the main QVBoxLayout
        if not layout: return

        index = layout.indexOf(self.main_task_label)
        if index == -1: return

        self._current_editor = QLineEdit(self.main_task_label.text())
        # Apply similar styling/font
        font = self.main_task_label.font()
        self._current_editor.setFont(font)
        self._current_editor.setStyleSheet(f"color: {COLOR_DARK_GRAY.name()}; border: 1px solid {COLOR_GRAY.name()}; padding: 1px;")
        # Main task editor doesn't need to expand like subtasks
        # self._current_editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout.removeWidget(self.main_task_label)
        self.main_task_label.hide()
        layout.insertWidget(index, self._current_editor)
        self._current_editor.setFocus()
        self._current_editor.selectAll()

        self._current_editor.editingFinished.connect(self.finish_editing_main_task)

    def finish_editing_main_task(self):
        if not self._current_editor or self._edited_label != self.main_task_label:
            return # Not editing the main task or editor already gone

        editor = self._current_editor
        label = self._edited_label
        layout = self.layout()
        if not layout: return

        new_text = editor.text().strip()
        if new_text:
            label.setText(new_text)

        index = layout.indexOf(editor)
        if index == -1: return

        try:
            editor.editingFinished.disconnect(self.finish_editing_main_task)
        except TypeError:
            pass

        layout.removeWidget(editor)
        editor.deleteLater()
        layout.insertWidget(index, label)
        label.show()

        self._current_editor = None
        self._edited_label = None



    def start_editing_subtask(self, event, label):
        # If already editing another label, finish that first (existing code)
        if self._current_editor:
            if self._edited_label == self.main_task_label:
                self.finish_editing_main_task()
            else:
                self.finish_editing_subtask()
            # Check if finishing cleared the editor before proceeding
            if self._current_editor: 
                return # Avoid starting if finish failed or is still active

        # Store the label we're about to edit
        self._edited_label = label
        
        # Ensure the label we are trying to edit actually exists in a layout
        parent_widget = label.parentWidget()
        if not parent_widget: 
            return
        layout = parent_widget.layout() # Get the QHBoxLayout containing the label
        if not layout: 
            return # Should not happen

        # Find the index of the label
        index = layout.indexOf(label)
        if index == -1: 
            return # Should not happen

        # Create and configure the QTextEdit for multi-line editing
        self._current_editor = QTextEdit()
        self._current_editor.setText(label.text())
        self._current_editor.setStyleSheet(f"""
            color: {COLOR_DARK_GRAY.name()};
            border: 1px solid {COLOR_GRAY.name()};
            padding: 2px;
        """)
        
        # Configure height based on content but allow expansion
        self._current_editor.setMinimumHeight(25)
        self._current_editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        # Install event filter to handle Ctrl+Enter
        self._current_editor.installEventFilter(self)
        
        # Replace label with editor in the layout
        layout.removeWidget(label)
        label.hide()
        layout.insertWidget(index, self._current_editor)
        self._current_editor.setFocus()
        self._current_editor.selectAll()

    def finish_editing_subtask(self):
        if not self._current_editor or not self._edited_label:
            return

        editor = self._current_editor
        label = self._edited_label
        layout = editor.parentWidget().layout()
        if not layout: return

        # Get text and update label if not empty
        new_text = editor.toPlainText().strip()
        if new_text:
            label.setText(new_text)
            # Configure label for multi-line text
            label.setWordWrap(True)

        # Find editor index
        index = layout.indexOf(editor)
        if index == -1: return

        # Remove event filter
        editor.removeEventFilter(self)

        # Replace editor with label
        layout.removeWidget(editor)
        editor.deleteLater() # Schedule for deletion
        layout.insertWidget(index, label)
        label.show()

        # Reset state
        self._current_editor = None
        self._edited_label = None
        self.update_progress() # Re-apply styling if needed (like strikethrough)

    def eventFilter(self, obj, event):
        # Handle key press events in the text editor
        if obj is self._current_editor and event.type() == QEvent.KeyPress:
            # Check if Ctrl+Enter was pressed
            if (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter) and \
               (event.modifiers() & Qt.ControlModifier):
                # Insert a newline
                cursor = self._current_editor.textCursor()
                cursor.insertText('\n')
                self._current_editor.setTextCursor(cursor)
                return True
            # Handle Enter key to finish editing
            elif (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter) and \
                 not (event.modifiers() & Qt.ControlModifier):
                self.finish_editing_subtask()
                return True
                
        # Let the event be handled by the default handler
        return super().eventFilter(obj, event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Set default font if desired
    # font = QFont("Noto Sans", 10)
    # app.setFont(font)
    ex = TaskProgressApp()
    sys.exit(app.exec_())
