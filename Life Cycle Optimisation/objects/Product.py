from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QPolygonF, QFont
from PyQt6.QtWidgets import QGraphicsTextItem, QGraphicsPolygonItem


class Product(QGraphicsPolygonItem):
    def __init__(self, product_id, name, amount, longitude, latitude, fee, next_nodes):
        self.id = product_id
        self.name = name
        self.type = 'product'
        self.x, self.y = 0, 0
        self.amount = amount
        self.longitude = longitude
        self.latitude = latitude
        self.fee = fee
        self.next_nodes = next_nodes
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
        data = {"id": self.id, 'name': self.name, 'type': self.type, "position": {"x": self.x, "y": self.y},
                "amount": self.amount, 'longitude': self.longitude, 'latitude': self.latitude, 'fee': self.fee,
                "next_nodes": self.next_nodes}
        return data

    @staticmethod
    def from_json(node):
        product = Product(node['id'], node['name'], node['amount'], node['longitude'], node['latitude'], node['fee'],
                          node['next_nodes'])
        product.x = node["position"]["x"]
        product.y = node["position"]["y"]
        product.type = 'demand'
        return product
