import matplotlib.pyplot as plt
import numpy as np
from nsga2.evolution import Evolution
from nsga2.problem import Problem

from ui.Result import Result


class TwoObjs:
    def __init__(self, objective, constraint, var_range, scale, impact_name, nodes):
        num_of_var = len(objective) - 1
        # get the most sustainable solution (scenario a) and the most profitable solution (scenario b)
        small = [float('inf'), []]
        large = [0, []]

        # objective function for environmental impact
        def f1(x):
            s = sum(objective[i][0] * x[i] for i in range(num_of_var))
            if sum(constraint[i] * x[i] for i in range(num_of_var)) < constraint[-1]:
                s = float('inf')
            if s != float('inf'):
                if s < small[0]:
                    small[0] = s
                    small[1] = [i * scale for i in x]
                if s > large[0] and s * scale <= objective[-1][0]:
                    large[0] = s
                    large[1] = [i * scale for i in x]
            return s

        # objective function for profit
        def f2(x):
            s = -sum(objective[i][1] * x[i] for i in range(num_of_var))
            if sum(constraint[i] * x[i] for i in range(num_of_var)) < constraint[-1]:
                s = float('inf')
            return s

        # apply genetic algorithm
        problem = Problem(num_of_variables=num_of_var, objectives=[f1, f2], variables_range=[(0, var_range)],
                          same_range=True, expand=False)
        evo = Evolution(problem, num_of_individuals=500, num_of_generations=300)
        func = [i.objectives for i in evo.evolve()]
        function1 = []
        function2 = []
        # choose solutions satisfying environmental constraints
        for i in func:
            if i[0] * scale <= objective[-1][0]:
                function1.append(i[0] * scale)
                function2.append(-i[1] * scale)
        x = np.array(function1)
        y = np.array(function2)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel(impact_name)
        ax.set_ylabel('Profit')
        ax.set_title('Pareto Front')
        ax.scatter(x, y)
        label = 'Objective 1:\nMinimise ' + impact_name + \
                '\nObjective 2:\nMaximise Profit\n\n' \
                'Scenario a - Sustainability Prioritised:\n' + \
                impact_name + ':\n' + str(min(function1)) + '\n' + 'Profit:\n' + str(
            min(function2)) + '\n\nScenario b - Profitability Prioritised:\n' + \
                impact_name + ':\n' + str(max(function1)) + '\n' + 'Profit:\n' + str(max(function2))
        Result(2, nodes, small, large, fig, label).exec()
