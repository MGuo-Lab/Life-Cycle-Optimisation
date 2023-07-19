from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QGridLayout, QDialog, QTableWidget, QHeaderView, QTableWidgetItem, QLabel, \
    QAbstractItemView, QLineEdit, QGroupBox, QPushButton

from database.Data import Data
from ui.Message import Message


class ProductEditor(QDialog):
    def __init__(self, x='', y='', amount='', longitude='', latitude='', fee=''):
        super().__init__()
        dw = QGuiApplication.primaryScreen().size()
        self.resize(int(dw.width() * 0.9), int(dw.height() * 0.9))
        self.product_data = Data.get_flow()
        self.lookupTable = QTableWidget()
        self.lookupTable.setRowCount(len(self.product_data.index))
        self.lookupTable.setColumnCount(2)
        for i in range(self.lookupTable.rowCount()):
            for j in range(self.lookupTable.columnCount()):
                self.lookupTable.setItem(i, j, QTableWidgetItem('{0}'.format(self.product_data.iloc[i, j])))
        self.lookupTable.verticalHeader().setVisible(False)
        self.lookupTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.lookupTable.setHorizontalHeaderLabels(self.product_data.columns)
        self.lookupTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        grid = QGridLayout()
        self.setLayout(grid)
        # groupbox for product info
        info_group = QGroupBox('Product Info')
        info_layout = QGridLayout()
        info_group.setLayout(info_layout)
        self.x = QLineEdit(x)
        self.y = QLineEdit(y)
        self.amount = QLineEdit(amount)
        self.longitude = QLineEdit(longitude)
        self.latitude = QLineEdit(latitude)
        self.fee = QLineEdit(fee)
        info_layout.addWidget(QLabel('Position X:'), 0, 0)
        info_layout.addWidget(QLabel('Position Y:'), 1, 0)
        info_layout.addWidget(QLabel('Amount:'), 2, 0)
        info_layout.addWidget(QLabel('Longitude:'), 3, 0)
        info_layout.addWidget(QLabel('Latitude:'), 4, 0)
        info_layout.addWidget(QLabel('Transport cost:'), 5, 0)
        info_layout.addWidget(self.x, 0, 1)
        info_layout.addWidget(self.y, 1, 1)
        info_layout.addWidget(self.amount, 2, 1)
        info_layout.addWidget(self.longitude, 3, 1)
        info_layout.addWidget(self.latitude, 4, 1)
        info_layout.addWidget(self.fee, 5, 1)
        self.search = QLineEdit()
        self.search.textChanged.connect(self.text_changed)
        grid.addWidget(QLabel('Search:'), 1, 0)
        grid.addWidget(self.lookupTable, 2, 0, 1, 2)
        grid.addWidget(self.search, 1, 1)
        grid.addWidget(info_group, 0, 0, 1, 2)
        grid.addWidget(QPushButton('OK', clicked=self.ok_clicked), 3, 0)

    def text_changed(self):
        text = self.search.text()
        df = self.product_data.query("Flow.str.contains(\"" + text + "\", case=False)", engine='python')
        self.lookupTable.setRowCount(len(df.index))
        self.lookupTable.setColumnCount(len(df.columns))
        for i in range(self.lookupTable.rowCount()):
            for j in range(self.lookupTable.columnCount()):
                self.lookupTable.setItem(i, j, QTableWidgetItem('{0}'.format(df.iloc[i, j])))

    def ok_clicked(self):
        if not self.isfloat(self.x.text()):
            Message('Please enter a number in Position X').exec()
        elif not self.isfloat(self.y.text()):
            Message('Please enter a number in Position Y').exec()
        elif not self.isfloat(self.amount.text()):
            Message('Please enter a number in Amount').exec()
        elif not self.isfloat(self.longitude.text()):
            Message('Please enter a number in Longitude').exec()
        elif not self.isfloat(self.latitude.text()):
            Message('Please enter a number in Latitude').exec()
        elif not self.isfloat(self.fee.text()):
            Message('Please enter a number in Transport Cost').exec()
        elif not self.lookupTable.selectedIndexes():
            Message('Please select a process from the table').exec()
        else:
            self.accept()

    def isfloat(self, num):
        try:
            float(num)
            return True
        except ValueError:
            return False
