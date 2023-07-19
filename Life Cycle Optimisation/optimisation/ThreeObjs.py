import matplotlib.pyplot as plt
from nsga2.evolution import Evolution
from nsga2.problem import Problem

from ui.Result import Result


class ThreeObjs:
    def __init__(self, objective, constrain, var_range, scale, impact_name1, impact_name2, nodes):
        num_of_var = len(objective) - 1
        # get the most sustainable solution (scenario a) and the most profitable solution (scenario b)
        small = [float('inf'), []]
        large = [0, []]

        # objective function for environmental impact 1
        def f1(x):
            s = sum(objective[i][0] * x[i] for i in range(num_of_var))
            if sum(constrain[i] * x[i] for i in range(num_of_var)) < constrain[-1]:
                s = float('inf')
            if s != float('inf'):
                if s < small[0]:
                    small[1] = [i * scale for i in x]
                    small[0] = s
                if s > large[0] and s * scale <= objective[-1][0]:
                    large[1] = [i * scale for i in x]
                    large[0] = s
            return s

        # objective function for environmental impact 2
        def f2(x):
            s = sum(objective[i][1] * x[i] for i in range(num_of_var))
            if sum(constrain[i] * x[i] for i in range(num_of_var)) < constrain[-1]:
                s = float('inf')
            return s

        # objective function for profit
        def f3(x):
            s = -sum(objective[i][2] * x[i] for i in range(num_of_var))
            if sum(constrain[i] * x[i] for i in range(num_of_var)) < constrain[-1]:
                s = float('inf')
            return s

        # apply genetic algorithm
        problem = Problem(num_of_variables=num_of_var, objectives=[f1, f2, f3], variables_range=[(0, var_range)],
                          same_range=True, expand=False)
        evo = Evolution(problem, num_of_individuals=500, num_of_generations=300)
        func = [i.objectives for i in evo.evolve()]
        function1 = []
        function2 = []
        function3 = []
        # choose solutions satisfying environmental constraints
        for i in func:
            if i[0] * scale <= objective[-1][0] and i[1] * scale <= objective[-1][1]:
                function1.append(i[0] * scale)
                function2.append(i[1] * scale)
                function3.append(-i[2] * scale)
        fig = plt.figure()
        ax = plt.axes(projection="3d")
        ax.scatter3D(function1, function2, function3)
        ax.set_title('Pareto Front')
        ax.set_xlabel(impact_name1)
        ax.set_zlabel('Profit')
        ax.set_ylabel(impact_name2)
        label = 'Objective 1:\nMinimise ' + impact_name1 + \
                '\nObjective 2:\nMinimise ' + impact_name2 + '\nObjective 3:\nMaximise Profit\n\n' \
                                                             'Scenario a - Sustainability Prioritised:\n' + \
                impact_name1 + ':\n' + str(min(function1)) + '\n' + impact_name2 + ':\n' + str(
            min(function2)) + '\n' + 'Profit:\n' + str(
            min(function3)) + '\n\nScenario b - Profitability Prioritised:\n' + \
                impact_name1 + ':\n' + str(max(function1)) + '\n' + impact_name2 + ':\n' + str(
            max(function2)) + '\n' + 'Profit:\n' + str(max(function3))
        Result(3, nodes, small, large, fig, label).exec()
