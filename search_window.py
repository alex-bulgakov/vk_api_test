from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout


class SearchWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Create search label and input field
        self.search_label = QLabel("Search:")
        self.search_input = QLineEdit()

        # Create search button
        self.search_button = QPushButton("Search")

        # Create table for displaying search results
        self.results_table = QTableWidget()

        # Add widgets to layout
        layout = QVBoxLayout()
        layout.addWidget(self.search_label)
        layout.addWidget(self.search_input)
        layout.addWidget(self.search_button)
        layout.addWidget(self.results_table)

        self.setLayout(layout)

    def display_results(self, results):
        # Clear existing table
        self.results_table.clear()
        self.results_table.setRowCount(0)
        self.results_table.setColumnCount(2)

        # Set table headers
        self.results_table.setHorizontalHeaderLabels(['Group', 'Result'])

        # Add search results to table
        for group, result in results:
            row_count = self.results_table.rowCount()
            self.results_table.insertRow(row_count)
            self.results_table.setItem(row_count, 0, QTableWidgetItem(group))
            self.results_table.setItem(row_count, 1, QTableWidgetItem(result))
