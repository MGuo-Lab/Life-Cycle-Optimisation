from PyQt6.QtGui import QGuiApplication, QFont
from PyQt6.QtWidgets import QDialog, QGridLayout, QLabel, QTableWidget, QTableWidgetItem
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from objects.Process import Process


class Result(QDialog):
    def __init__(self, model, nodes, small, large, fig, label):
        super().__init__()
        process = []
        for node in nodes.values():
            if isinstance(node, Process):
                process.append(node.id)
        process = sorted(process)
        dw = QGuiApplication.primaryScreen().size()
        self.resize(int(dw.width() * 0.8), int(dw.height()))
        grid = QGridLayout()
        self.setLayout(grid)
        if model != 1:
            table = QTableWidget()
            table.setRowCount(len(process))
            table.setColumnCount(3)
            for i in range(table.rowCount()):
                table.setItem(i, 0, QTableWidgetItem(nodes[process[i]].name))
                table.setItem(i, 1, QTableWidgetItem(str(small[1][i])))
                table.setItem(i, 2, QTableWidgetItem(str(large[1][i])))
            table.verticalHeader().setVisible(False)
            table.setHorizontalHeaderLabels(['Name', 'Scenario a', 'Scenario b'])
            table.resizeColumnsToContents()
            canvas = FigureCanvas(fig)
            grid.addWidget(table, 1, 0, 1, 2)
            grid.addWidget(canvas, 0, 1)
        l = QLabel(label)
        l.setFont(QFont('Arial', 23))
        grid.addWidget(l, 0, 0)
