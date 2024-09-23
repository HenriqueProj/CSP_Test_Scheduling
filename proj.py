from minizinc import Instance, Model, Solver

# Create a MiniZinc model
model = Model()
model.add_file("Test_Scheduling.mzn")  # Load the MiniZinc model

# Create a MiniZinc instance
gecode = Solver.lookup("gecode")  # Select the solver
instance = Instance(gecode, model)

# Solve the model
result = instance.solve()

"""
    TODO: Processar o output
"""

print(instance.solve())
