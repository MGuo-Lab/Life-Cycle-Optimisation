import math

from PyQt6.QtCore import QLineF, QPointF
from PyQt6.QtGui import QPolygonF
from PyQt6.QtWidgets import QGraphicsLineItem


class Arrow(QGraphicsLineItem):
    def __init__(self, start, end):
        super().__init__()
        self.start = start
        self.end = end
        self.arrowHead = QPolygonF()

    @staticmethod
    def get_intersect(line, item):
        poly = item.polygon()
        p1 = poly.first() + item.pos()
        intersect_point = QPointF()
        for i in poly:
            p2 = i + item.pos()
            intersect_type, intersect_point = QLineF(p1, p2).intersects(line)
            if intersect_type == QLineF.IntersectionType.BoundedIntersection: break
            p1 = p2
        return intersect_point

    def paint(self, painter, option, widget=None):
        self.arrowHead.clear()
        painter.setPen(self.pen())
        line = QLineF(self.start.pos(), self.end.pos())
        intersect_start = self.get_intersect(line, self.start)
        intersect_end = self.get_intersect(line, self.end)
        self.setLine(QLineF(intersect_start, intersect_end))
        angle = math.acos(line.dx() / line.length())
        if line.dy() > 0:
            angle = (math.pi * 2.0) - angle
        arrow_1 = self.line().p2() - QPointF(math.sin(angle + math.pi / 3.0) * 12,
                                             math.cos(angle + math.pi / 3) * 12)
        arrow_2 = self.line().p2() - QPointF(math.sin(angle + math.pi - math.pi / 3.0) * 12,
                                             math.cos(angle + math.pi - math.pi / 3.0) * 12)

        for point in [self.line().p2(), arrow_1, arrow_2]:
            self.arrowHead.append(point)

        painter.drawPolygon(self.arrowHead)
        painter.drawLine(self.line())
