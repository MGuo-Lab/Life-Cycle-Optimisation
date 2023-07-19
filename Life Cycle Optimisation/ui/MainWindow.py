import json

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QGuiApplication, QColor
from PyQt6.QtWidgets import QWidget, QGraphicsView, QMainWindow, QFileDialog, QGridLayout, QPushButton, QLineEdit, \
    QGraphicsScene, QGroupBox

from objects.Arrow import Arrow
from objects.Process import Process
from objects.Product import Product
from ui.Message import Message
from ui.Optimisation import Optimisation
from ui.ProcessEditor import ProcessEditor
from ui.ProductEditor import ProductEditor


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        dw = QGuiApplication.primaryScreen().size()
        self.resize(int(dw.width()), int(dw.height()))
        self.network = QGraphicsScene()
        self.nodes = {}
        self.network.setSceneRect(QRectF(0, 0, 800, 500))

        # groupbox for edit
        edit_group = QGroupBox('Edit')
        edit_layout = QGridLayout()
        edit_group.setLayout(edit_layout)
        self.edit = QLineEdit()
        self.edit.setPlaceholderText('Enter the name of the node')
        edit_layout.addWidget(self.edit, 0, 0, 1, 2)
        edit_layout.addWidget(QPushButton('View Info', clicked=self.view_info), 1, 0)
        edit_layout.addWidget(QPushButton('Delete Node', clicked=self.delete_clicked), 1, 1)

        # groupbox for connect
        connect_group = QGroupBox('Connect')
        connect_layout = QGridLayout()
        connect_group.setLayout(connect_layout)
        self.connect = QLineEdit()
        self.connect.setPlaceholderText('Enter the name of the two nodes')
        connect_layout.addWidget(self.connect, 0, 0, 1, 2)
        connect_layout.addWidget(QPushButton('Connect Node', clicked=self.connect_clicked), 1, 0)
        connect_layout.addWidget(QPushButton('Disconnect Node', clicked=self.disconnect_clicked), 1, 1)

        # groupbox for basic
        basic_group = QGroupBox('Basic')
        basic_layout = QGridLayout()
        basic_group.setLayout(basic_layout)
        basic_layout.addWidget(QPushButton('Open File', clicked=self.open_clicked), 0, 0)
        basic_layout.addWidget(QPushButton('Save File', clicked=self.save_clicked), 0, 1)
        basic_layout.addWidget(QPushButton('Add Product', clicked=self.add_product), 1, 0)
        basic_layout.addWidget(QPushButton('Add Process', clicked=self.add_process), 1, 1)

        grid = QGridLayout()
        grid.addWidget(QPushButton('Start Optimisation', clicked=self.show_clicked), 0, 5)
        grid.addWidget(basic_group, 0, 0, 2, 1)
        grid.addWidget(edit_group, 0, 1, 2, 1)
        grid.addWidget(connect_group, 0, 2, 2, 1)
        grid.addWidget(QGraphicsView(self.network), 2, 0, 1, 6)
        widget = QWidget()
        widget.setLayout(grid)
        self.setCentralWidget(widget)

    def view_info(self):
        node_id = self.edit.text()
        if node_id not in self.nodes:
            Message('Please enter a valid id as shown in the beginning of the name of an item, e.g., 123456').exec()
        else:
            if self.nodes[node_id].type == 'process':
                widget = ProcessEditor(str(self.nodes[node_id].x), str(self.nodes[node_id].y),
                                       str(self.nodes[node_id].revenue), str(self.nodes[node_id].subsidy),
                                       str(self.nodes[node_id].loss), str(self.nodes[node_id].longitude),
                                       str(self.nodes[node_id].latitude),
                                       str(self.nodes[node_id].fee))
                ok = widget.exec()
                if ok:
                    item = self.nodes[node_id]
                    item.revenue = float(widget.revenue.text())
                    item.subsidy = float(widget.subsidy.text())
                    item.loss = float(widget.loss.text())
                    item.latitude = float(widget.latitude.text())
                    item.longitude = float(widget.longitude.text())
                    item.fee = float(widget.fee.text())
            else:
                widget = ProductEditor(str(self.nodes[node_id].x), str(self.nodes[node_id].y),
                                       str(self.nodes[node_id].amount), str(self.nodes[node_id].longitude),
                                       str(self.nodes[node_id].latitude),
                                       str(self.nodes[node_id].fee))
                ok = widget.exec()
                if ok:
                    item = self.nodes[node_id]
                    item.amount = float(widget.amount.text())
                    item.latitude = float(widget.latitude.text())
                    item.longitude = float(widget.longitude.text())
                    item.fee = float(widget.fee.text())

    def show_clicked(self):
        if not self.nodes:
            Message('Please build a supply chain before optimisation.').exec()
        else:
            Optimisation(self.nodes).exec()

    def delete_clicked(self):
        node_id = self.edit.text()
        if node_id not in self.nodes:
            Message('Please enter a valid id as shown in the beginning of the name of an item, e.g., 123456').exec()
        else:
            for i in self.nodes:
                if node_id in self.nodes[i].next_nodes:
                    self.nodes[i].next_nodes.remove(node_id)
            for item in self.network.items():
                if isinstance(item, Arrow):
                    if item.start.id == node_id or item.end.id == node_id:
                        self.network.removeItem(item)
                elif isinstance(item, Process) or isinstance(item, Product):
                    if item.id == node_id:
                        self.network.removeItem(item)
            self.nodes.pop(node_id)

    def add_product(self):
        widget = ProductEditor()
        ok = widget.exec()
        if ok:
            idx = widget.lookupTable.selectedIndexes()
            rows = list(set([i.row() for i in idx]))[0]
            product_id = widget.lookupTable.item(rows, 0).text()
            name = widget.lookupTable.item(rows, 1).text()
            item = Product(product_id, name, float(widget.amount.text()), float(widget.longitude.text()),
                           float(widget.latitude.text()),
                           float(widget.fee.text()), [])
            item.x = int(widget.x.text())
            item.y = int(widget.y.text())
            self.network.addItem(item)
            item.setPos(item.x, item.y)
            item.setBrush(QColor(255, 255, 200))
            self.nodes[item.id] = item

    def connect_clicked(self):
        if ',' not in self.connect.text():
            Message('Please enter the ids of the two nodes and separate them by a comma, e.g., 123456,234567').exec()
        else:

            node1, node2 = self.connect.text()[:self.connect.text().find(',')], self.connect.text()[
                                                                                self.connect.text().find(',') + 1:]
            if node1 not in self.nodes or node2 not in self.nodes:
                Message(
                    'Please enter the ids of the two nodes and separate them by a comma, e.g., 123456,234567').exec()
            else:
                arrow = Arrow(self.nodes[node1], self.nodes[node2])
                if node2 not in self.nodes[node1].next_nodes:
                    self.nodes[node1].next_nodes.append(node2)
                self.network.addItem(arrow)
                arrow.update()

    def disconnect_clicked(self):

        if ',' not in self.connect.text():
            Message('Please enter the ids of the two nodes and separate them by a comma, e.g., 123456,234567').exec()
        else:

            node1, node2 = self.connect.text()[:self.connect.text().find(',')], self.connect.text()[
                                                                                self.connect.text().find(',') + 1:]
            if node1 not in self.nodes or node2 not in self.nodes:
                Message(
                    'Please enter the ids of the two nodes and separate them by a comma, e.g., 123456,234567').exec()
            else:
                for item in self.network.items():
                    if isinstance(item, Arrow):
                        if item.start.id == node1 and item.end.id == node2:
                            self.network.removeItem(item)
                            break

    def add_process(self):
        widget = ProcessEditor()
        ok = widget.exec()
        if ok:

            idx = widget.lookupTable.selectedIndexes()

            rows = list(set([i.row() for i in idx]))[0]
            process_id = widget.lookupTable.item(rows, 0).text()
            name = widget.lookupTable.item(rows, 1).text() + ', ' + widget.lookupTable.item(rows, 2).text()
            item = Process(process_id, name, float(widget.revenue.text()), float(widget.subsidy.text()),
                           float(widget.loss.text()), float(widget.longitude.text()), float(widget.latitude.text()),
                           float(widget.fee.text()), [])
            item.x = int(widget.x.text())
            item.y = int(widget.y.text())
            self.network.addItem(item)
            item.setPos(item.x, item.y)
            if item.loss < 1:
                item.setBrush(QColor(200, 200, 255))
            else:
                item.setBrush(QColor(255, 200, 200))
            self.nodes[item.id] = item

    def open_clicked(self):
        for item in self.network.items():
            self.network.removeItem(item)
        self.nodes.clear()
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "JSON Files (*.json)")
        if filename:
            with open(filename, 'rb') as f:
                data = json.load(f)
                for node in data["nodes"]:
                    if node["type"] == "process":
                        item = Process.from_json(node)
                        self.nodes[item.id] = item
                        item.setPos(item.x, item.y)
                        if item.loss < 1:
                            item.setBrush(QColor(200, 200, 255))
                        else:
                            item.setBrush(QColor(255, 200, 200))
                        self.network.addItem(item)
                    else:
                        item = Product.from_json(node)
                        self.nodes[item.id] = item
                        item.setPos(item.x, item.y)
                        item.setBrush(QColor(255, 255, 200))
                        self.network.addItem(item)
            for item in self.nodes.values():
                for node in item.next_nodes:
                    arrow = Arrow(item, self.nodes[node])
                    self.network.addItem(arrow)
                    arrow.update()

    def save_clicked(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", "JSON Files (*.json)")
        if filename:
            formatted_filename = filename
            json_file = {}
            nodes = []
            for node in self.nodes.values():
                nodes.append(node.get_json_object())
            json_file["nodes"] = nodes
            with open(formatted_filename, 'w') as f:
                json.dump(json_file, f, indent=4)
