from PyQt5.QtWidgets import QWidget, QCheckBox, QPushButton, QVBoxLayout


class GroupsWindow(QWidget):
    def __init__(self, groups):
        super().__init__()

        # Create checkboxes for each group
        self.group_checkboxes = {}
        for group in groups:
            checkbox = QCheckBox(group['name'])
            self.group_checkboxes[group['id']] = checkbox

        # Create search button
        self.search_button = QPushButton("Search")

        # Add widgets to layout
        layout = QVBoxLayout()
        for checkbox in self.group_checkboxes.values():
            layout.addWidget(checkbox)
        layout.addWidget(self.search_button)

        self.setLayout(layout)
