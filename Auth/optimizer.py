from pulp import LpMaximize, LpProblem, LpVariable, lpSum

def optimize_parcel_placement(parcels, container):
    # Define the problem
    problem = LpProblem("Parcel Optimization", LpMaximize)

    # Binary decision variables: 1 if parcel is included, 0 otherwise
    x = {i: LpVariable(f"x_{i}", cat="Binary") for i in range(len(parcels))}

    # Constraint: Total volume of selected parcels should not exceed container volume
    problem += lpSum(x[i] * parcels[i].volume for i in range(len(parcels))) <= container.volume

    # Constraint: Total weight should not exceed container's max weight
    problem += lpSum(x[i] * parcels[i].weight for i in range(len(parcels))) <= container.max_weight

    # Objective: Maximize total utilized volume
    problem += lpSum(x[i] * parcels[i].volume for i in range(len(parcels)))

    # Solve the problem
    problem.solve()

    # Return selected parcels
    return [parcels[i] for i in range(len(parcels)) if x[i].value() == 1]
