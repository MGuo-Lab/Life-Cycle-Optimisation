from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QPolygonF, QFont
from PyQt6.QtWidgets import QGraphicsTextItem, QGraphicsPolygonItem


class Process(QGraphicsPolygonItem):
    def __init__(self, process_id, name, revenue, subsidy, loss, longitude, latitude, fee, next_nodes):
        self.id = process_id
        self.name = name
        self.type = 'process'
        self.x, self.y = 0, 0
        self.next_nodes = next_nodes
        self.loss = loss
        self.revenue = revenue
        self.subsidy = subsidy
        self.longitude = longitude
        self.latitude = latitude
        self.fee = fee
        QGraphicsPolygonItem.__init__(self)
        self.myPolygon = QPolygonF(
            [QPointF(-50, -50), QPointF(-50, 50), QPointF(50, 50), QPointF(50, -50), QPointF(-50, -50)])
        self.textItem = QGraphicsTextItem(self)
        self.textItem.setTextWidth(100)
        self.textItem.setFont(QFont('Arial', 10))
        self.textItem.setHtml(self.id + ', ' + self.name)
        self.textItem.setPos(self.myPolygon.boundingRect().topLeft())
        self.setPolygon(self.myPolygon)

    def get_json_object(self):
        data = {'id': self.id, "name": self.name, "type": self.type, "revenue": self.revenue, "subsidy": self.subsidy,
                "loss": self.loss, 'longitude': self.longitude, 'latitude': self.latitude, 'fee': self.fee,
                "position": {"x": self.x, "y": self.y}, "next_nodes": self.next_nodes}
        return data

    @staticmethod
    def from_json(node):
        process = Process(node['id'], node['name'], node['revenue'], node['subsidy'], node['loss'], node['longitude'],
                          node['latitude'], node['fee'], node["next_nodes"])
        process.x = node["position"]["x"]
        process.y = node["position"]["y"]
        process.type = 'process'
        return process
