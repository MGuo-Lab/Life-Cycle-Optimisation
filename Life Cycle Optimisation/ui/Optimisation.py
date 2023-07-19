import time
from collections import defaultdict

import pyomo.environ as pe
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QDialog, QGroupBox, QLineEdit, QComboBox, QGridLayout, QLabel, QPushButton
from geopy.distance import geodesic

from database.Data import Data
from objects.Process import Process
from objects.Product import Product
from optimisation.ThreeObjs import ThreeObjs
from optimisation.TwoObjs import TwoObjs
from ui.Message import Message
from ui.Result import Result


class Optimisation(QDialog):
    def __init__(self, nodes):
        super().__init__()
        dw = QGuiApplication.primaryScreen().size()
        self.resize(int(dw.width() * 0.9), int(dw.height()))
        self.nodes = nodes
        layout = QGridLayout(self)
        self.setLayout(layout)
        self.impactCategories = Data.get_impact_categories(Data.get_impact_methods())
        # groupbox for single-objective optimisation
        single_group = QGroupBox('Two Objectives (Weighted Sum)')
        single_layout = QGridLayout()
        single_group.setLayout(single_layout)
        self.price = QLineEdit()
        single_layout.addWidget(QLabel('Emissions Allowances: '), 0, 2)
        single_layout.addWidget(self.price, 0, 3)
        self.impact_combobox = QComboBox()
        for _, category in self.impactCategories:
            self.impact_combobox.addItem(category)
        single_layout.addWidget(QLabel('Impact Category: '), 0, 0)
        single_layout.addWidget(self.impact_combobox, 0, 1)
        single_layout.addWidget(QPushButton('Start Optimisation', clicked=self.optimise1), 1, 3)
        # groupbox for two-objective optimisation
        two_group = QGroupBox('Two Objectives (Pareto Front)')
        two_layout = QGridLayout()
        two_group.setLayout(two_layout)
        self.impact_combobox1 = QComboBox()
        for _, category in self.impactCategories:
            self.impact_combobox1.addItem(category)
        two_layout.addWidget(QLabel('Impact Category: '), 0, 0)
        two_layout.addWidget(self.impact_combobox1, 0, 1)
        two_layout.addWidget(QLabel('Impact Category Limit: '), 0, 2)
        self.limit1 = QLineEdit()
        two_layout.addWidget(self.limit1, 0, 3)
        two_layout.addWidget(QPushButton('Start Optimisation', clicked=self.optimise2), 1, 3)
        # groupbox for three-objective optimisation
        three_group = QGroupBox('Three Objectives (Pareto Front)')
        three_layout = QGridLayout()
        three_group.setLayout(three_layout)
        self.impact_combobox2 = QComboBox()
        for _, category in self.impactCategories:
            self.impact_combobox2.addItem(category)
        three_layout.addWidget(QLabel('Impact Category: '), 0, 0)
        three_layout.addWidget(self.impact_combobox2, 0, 1)
        three_layout.addWidget(QLabel('Impact Category Limit: '), 0, 2)
        self.limit2 = QLineEdit()
        three_layout.addWidget(self.limit2, 0, 3)
        self.impact_combobox3 = QComboBox()
        for _, category in self.impactCategories:
            self.impact_combobox3.addItem(category)
        three_layout.addWidget(QLabel('Impact Category: '), 1, 0)
        three_layout.addWidget(self.impact_combobox3, 1, 1)
        three_layout.addWidget(QLabel('Impact Category Limit: '), 1, 2)
        self.limit3 = QLineEdit()
        three_layout.addWidget(self.limit3, 1, 3)
        three_layout.addWidget(QPushButton('Start Optimisation', clicked=self.optimise3), 2, 3)
        layout.addWidget(single_group, 0, 0)
        layout.addWidget(two_group, 1, 0)
        layout.addWidget(three_group, 2, 0)
        self.flows = set()
        self.processes = []
        self.processFlow = defaultdict(int)
        self.nodeDict = {}
        self.get_info()
        self.processes = sorted(self.processes)

    def get_info(self):
        for node in self.nodes.values():
            self.nodeDict[node.id] = node
            if isinstance(node, Process):
                self.processes.append(node.id)
                df = Data.get_flow_for_process(node.id)
                for index, row in df.iterrows():
                    self.flows.add(row['Flow'])
                    self.processFlow[(node.id, row['Flow'])] = float(row['Amount'])

    def build_model(self):
        all_nodes = []
        product = {}
        transform = []
        profit = {}
        weight = {}
        loss = {}
        all_processes = []
        self.transport_cost = {}
        for node in self.nodes.values():
            all_nodes.append(node.id)
            # get the relationship between nodes, 1 means there is a connection
            for i in node.next_nodes:
                weight[(node.id, i)] = 1
                location1 = (node.latitude, node.longitude)
                location2 = (self.nodeDict[i].latitude, self.nodeDict[i].longitude)
                self.transport_cost[node.id] = geodesic(location1, location2).km * node.fee
            # get the amount for the product
            if isinstance(node, Product):
                product[node.id] = float(node.amount)
            # get info of each process
            else:
                all_processes.append(node.id)
                if node.loss != 1:
                    transform.append(node.id)
                    loss[node.id] = node.loss
                profit[node.id] = node.revenue + node.subsidy
        flows = list(self.flows)
        # build the model
        model = pe.ConcreteModel()
        # sets
        model.flows = pe.Set(initialize=flows)
        model.allProcesses = pe.Set(initialize=all_processes)
        model.product = pe.Set(initialize=product.keys())
        model.allNodes = pe.Set(initialize=all_nodes)
        model.transform = pe.Set(initialize=transform)
        model.process = pe.Set(initialize=self.processes)
        # parameters
        model.loss = pe.Param(model.transform, initialize=loss)
        model.profit = pe.Param(model.allProcesses, initialize=profit)
        model.amount = pe.Param(model.product, initialize=product)
        model.relation = pe.Param(model.allNodes, model.allNodes, initialize=weight, default=0.0)
        model.transportation_cost = pe.Param(model.allNodes, initialize=self.transport_cost, default=0.0)
        model.inventory = pe.Param(model.allProcesses, model.flows, initialize=self.processFlow, default=0.0)
        # variables
        model.x = pe.Var(model.allProcesses, domain=pe.NonNegativeReals)
        model.y = pe.Var(model.allNodes, model.allNodes, domain=pe.NonNegativeReals)

        # constraints
        # the product produced by the process should all be transported to the next node
        def produce_rule(m, k):
            return m.x[k] == sum(m.y[k, i] * m.relation[k, i] for i in m.allNodes)

        model.produce_rule = pe.Constraint(model.process, rule=produce_rule)

        # the input of a transform process times loss rate equals the output
        def transform_rule(m, k):
            return sum(m.y[i, k] * m.relation[i, k] for i in m.allNodes) * m.loss[k] == sum(
                m.y[k, i] * m.relation[k, i] for i in m.allNodes)

        model.transform_rule = pe.Constraint(model.transform, rule=transform_rule)
        return model

    def optimise1(self):
        if not self.price.text():
            Message('Please enter the price of emission allowance.').exec()
        else:
            impact_category_id = self.impactCategories[self.impact_combobox.currentIndex()][0]
            factors = defaultdict(int)
            impact_flows = Data.get_impact_flows(impact_category_id)
            for flowID in impact_flows:
                if flowID in self.flows:
                    factors[flowID] = float(Data.get_impact_factor(impact_category_id, flowID))
            # build the model
            model = self.build_model()
            model.factors = pe.Param(model.flows, initialize=factors, default=0.0)

            # the input of a product node minus the demand of the product equals the output
            def demand_rule(m, k):
                return sum(m.y[i, k] * m.relation[i, k] for i in m.allNodes) - m.amount[k] == sum(
                    m.y[k, i] * m.relation[k, i] for i in m.allNodes)

            model.demand_rule = pe.Constraint(model.product, rule=demand_rule)

            # objective
            def objective(m):

                return sum(m.profit[i] * m.x[i] for i in m.allProcesses) - float(self.price.text()) * sum(
                    m.factors[f] * sum(m.x[t] * m.inventory[t, f] for t in m.allProcesses) for f in m.flows) - sum(
                    m.transportation_cost[i] * m.x[i] for i in m.allProcesses)

            model.obj = pe.Objective(rule=objective, sense=pe.maximize)
            solver = pe.SolverFactory('glpk')
            t1 = time.time()
            solver.solve(model)
            t2 = time.time()
            print('time: ' + str(t2 - t1))
            label = 'Objective 1:\nMinimise ' + self.impact_combobox.currentText() + \
                    '\nObjective 2:\nMaximise Profit\n\n' \
                    + 'Profit:\n' + str(
                pe.value(model.obj))
            Result(1, self.nodes, [], [], [], label).exec()

    def optimise2(self):
        # get the environmental impact
        impact_category_id = self.impactCategories[self.impact_combobox1.currentIndex()][0]
        factors = defaultdict(int)
        impact_flows = Data.get_impact_flows(impact_category_id)
        for flowID in impact_flows:
            if flowID in self.flows:
                factors[flowID] = float(Data.get_impact_factor(impact_category_id, flowID))
        # get objectives and constraints
        objectives = defaultdict(lambda: [0, 0])
        constraints = defaultdict(lambda: 1)
        amount, scale, var_range = 0, 0, 0
        for node in self.nodes.values():
            # get info of all processes
            if isinstance(node, Process):
                # loss=1 means it's a production process
                if node.loss == 1:
                    # get the environmental impacts and profit for each production process
                    objectives[node.id][0] = sum(factors[f] * self.processFlow[node.id, f] for f in self.flows)
                    objectives[node.id][1] = node.revenue + node.subsidy - self.transport_cost[node.id]
                    # all downstream processes' environmental impacts and profits should be considered
                    i = node
                    while i.next_nodes:
                        if isinstance(self.nodeDict[i.next_nodes[0]], Process):
                            constraints[node.id] *= self.nodeDict[i.next_nodes[0]].loss
                            objectives[node.id][0] += constraints[node.id] * sum(
                                factors[f] * self.processFlow[i.next_nodes[0], f] for f in self.flows)
                            objectives[node.id][1] += constraints[node.id] * (
                                    self.nodeDict[i.next_nodes[0]].revenue + self.nodeDict[i.next_nodes[0]].subsidy -
                                    self.transport_cost[i.next_nodes[0]])
                        i = self.nodeDict[i.next_nodes[0]]
            # get info of the final commodity
            else:
                # no next nodes mean it's the final product
                if not node.next_nodes:
                    amount = float(node.amount)
                    # scale down the search space to less than 100 cuz large search space means large population size
                    # not enough computational power
                    # scale back up after genetic algorithm
                    scale = 1
                    while amount > 100:
                        amount /= 10
                        scale *= 10
                    var_range = amount
        num_of_var = len(self.processes)
        obj = [[0 for _ in range(2)] for _ in range(num_of_var + 1)]
        con = [0 for _ in range(num_of_var + 1)]
        # set limits for environmental impacts
        con[num_of_var] = amount
        obj[num_of_var][0] = float(self.limit1.text()) if self.limit1.text() else float('inf')
        obj[num_of_var][1] = float('inf')
        # convert dictionary to array
        for i in range(num_of_var):
            obj[i][0] = objectives[self.processes[i]][0]
            obj[i][1] = objectives[self.processes[i]][1]
            con[i] = constraints[self.processes[i]]
        name = self.impact_combobox1.currentText()
        TwoObjs(obj, con, var_range, scale, name, self.nodes)

    def optimise3(self):
        # get the two environmental impacts
        impact_id = self.impactCategories[self.impact_combobox2.currentIndex()][0]
        impact_id1 = self.impactCategories[self.impact_combobox3.currentIndex()][0]
        factors = defaultdict(int)
        impact_flows = Data.get_impact_flows(impact_id)
        for flowID in impact_flows:
            if flowID in self.flows:
                factors[flowID] = float(Data.get_impact_factor(impact_id, flowID))
        factors1 = defaultdict(int)
        impact_flows = Data.get_impact_flows(impact_id1)
        for flowID in impact_flows:
            if flowID in self.flows:
                factors1[flowID] = float(Data.get_impact_factor(impact_id1, flowID))
        # get objectives and constraints
        objectives = defaultdict(lambda: [0, 0, 0])
        constraints = defaultdict(lambda: 1)
        amount, scale, var_range = 0, 0, 0
        for node in self.nodes.values():
            # get info of all processes
            if isinstance(node, Process):
                # loss=1 means it's a production process
                if node.loss == 1:
                    # get the environmental impacts and profit for each production process
                    objectives[node.id][0] = sum(factors[f] * self.processFlow[node.id, f] for f in self.flows)
                    objectives[node.id][1] = sum(factors1[f] * self.processFlow[node.id, f] for f in self.flows)
                    objectives[node.id][2] = node.revenue + node.subsidy - self.transport_cost[node.id]
                    # all downstream processes' environmental impacts and profits should be considered
                    i = node
                    while i.next_nodes:
                        if isinstance(self.nodeDict[i.next_nodes[0]], Process):
                            constraints[node.id] *= self.nodeDict[i.next_nodes[0]].loss
                            objectives[node.id][0] += constraints[node.id] * sum(
                                factors[f] * self.processFlow[i.next_nodes[0], f] for f in self.flows)
                            objectives[node.id][1] += constraints[node.id] * sum(
                                factors1[f] * self.processFlow[i.next_nodes[0], f] for f in self.flows)
                            objectives[node.id][2] += constraints[node.id] * (
                                    self.nodeDict[i.next_nodes[0]].revenue + self.nodeDict[i.next_nodes[0]].subsidy -
                                    self.transport_cost[i.next_nodes[0]])
                        i = self.nodeDict[i.next_nodes[0]]
            # get info of the final commodity
            else:
                # no next nodes mean it's the final product
                if not node.next_nodes:
                    amount = float(node.amount)
                    # scale down the search space to less than 100 cuz large search space means large population size
                    # not enough computational power
                    # scale back up after genetic algorithm
                    scale = 1
                    while amount > 100:
                        amount /= 10
                        scale *= 10
                    var_range = amount
        num_of_var = len(self.processes)
        obj = [[0 for _ in range(3)] for _ in range(num_of_var + 1)]
        con = [0 for _ in range(num_of_var + 1)]
        # set limits for environmental impacts
        con[num_of_var] = amount
        obj[num_of_var][0] = float(self.limit2.text()) if self.limit2.text() else float('inf')
        obj[num_of_var][1] = float(self.limit3.text()) if self.limit3.text() else float('inf')
        obj[num_of_var][2] = float('inf')
        # convert dictionary to array
        for i in range(num_of_var):
            obj[i][0] = objectives[self.processes[i]][0]
            obj[i][1] = objectives[self.processes[i]][1]
            obj[i][2] = objectives[self.processes[i]][2]
            con[i] = constraints[self.processes[i]]
        name1 = self.impact_combobox2.currentText()
        name2 = self.impact_combobox3.currentText()
        ThreeObjs(obj, con, var_range, scale, name1, name2, self.nodes)
