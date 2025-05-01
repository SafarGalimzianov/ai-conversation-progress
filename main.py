#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QCheckBox, QInputDialog, QMessageBox
)


class CircleProgressBar(QWidget):
    def __init__(self, count, statuses, parent=None):
        super().__init__(parent)
        self.count = count
        self.statuses = statuses  # список булев
        self.margin = 20
        self.radius = 10
        self.line_width = 4
        self.color_done = QColor("#8ec07c")
        self.color_pending = QColor("#cccccc")

    def set_statuses(self, statuses):
        self.statuses = statuses
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width() - 2 * self.margin
        n = self.count
        if n < 2:
            return
        # расстояние между центрами
        span = w / (n - 1)
        # найти первый непоставленный
        try:
            k = self.statuses.index(False)
        except ValueError:
            k = n  # все выполнены

        # рисуем линии
        for i in range(n - 1):
            x1 = self.margin + i * span
            x2 = self.margin + (i + 1) * span
            y = self.height() / 2
            pen = QPen(self.color_done if i < k else self.color_pending, self.line_width)
            painter.setPen(pen)
            painter.drawLine(x1, y, x2, y)

        # рисуем кружки
        for i in range(n):
            x = self.margin + i * span
            y = self.height() / 2
            rect = QRectF(x - self.radius, y - self.radius,
                          2 * self.radius, 2 * self.radius)

            if i < k:
                # заполненный
                painter.setBrush(QBrush(self.color_done))
                painter.setPen(Qt.NoPen)
            elif i == k:
                # текущий: контур зеленый, без заливки
                painter.setBrush(Qt.NoBrush)
                painter.setPen(QPen(self.color_done, 2))
            else:
                # далее: серый контур
                painter.setBrush(Qt.NoBrush)
                painter.setPen(QPen(self.color_pending, 2))

            painter.drawEllipse(rect)


class TaskProgressApp(QWidget):
    def __init__(self, title, subtasks):
        super().__init__()
        self.setWindowTitle("Task Progress")
        self.setStyleSheet("background-color: #f0f0f0;")
        self.subtasks = subtasks
        self.statuses = [False] * len(subtasks)

        # layout
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(15, 15, 15, 15)
        vbox.setSpacing(10)

        # Main Task label
        label = QLabel(title)
        label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        vbox.addWidget(label, alignment=Qt.AlignLeft)

        # progress bar widget
        self.pb = CircleProgressBar(len(subtasks), self.statuses)
        self.pb.setFixedHeight(50)
        vbox.addWidget(self.pb)

        # list of checkboxes
        for idx, name in enumerate(subtasks):
            h = QHBoxLayout()
            cb = QCheckBox(name)
            cb.setStyleSheet("font-size: 12pt;")
            cb.stateChanged.connect(self.make_toggle(idx))
            h.addWidget(cb)
            h.addStretch()
            vbox.addLayout(h)

    def make_toggle(self, idx):
        def toggle(state):
            self.statuses[idx] = (state == Qt.Checked)
            self.pb.set_statuses(self.statuses)
        return toggle


def ask_user():
    # ввод заголовка
    title, ok = QInputDialog.getText(
        None, "Main Task", "Enter main task title:")
    if not ok or not title.strip():
        QMessageBox.warning(None, "Ошибка", "Заголовок не может быть пустым")
        sys.exit(0)

    # ввод подзадач
    text, ok = QInputDialog.getMultiLineText(
        None, "Subtasks", "Enter subtasks (one per line):")
    if not ok or not text.strip():
        QMessageBox.warning(None, "Ошибка", "Нужно ввести хотя бы одну подзадачу")
        sys.exit(0)

    subtasks = [line.strip() for line in text.splitlines() if line.strip()]
    if not subtasks:
        QMessageBox.warning(None, "Ошибка", "Нужно ввести хотя бы одну подзадачу")
        sys.exit(0)

    return title, subtasks


def main():
    app = QApplication(sys.argv)
    # шрифт системный по умолчанию (Noto Sans, если установлен)
    title, subtasks = ask_user()
    win = TaskProgressApp(title, subtasks)
    win.resize(400, 300)
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
