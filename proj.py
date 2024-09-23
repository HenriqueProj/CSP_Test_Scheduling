import minizinc
import re
import argparse

# Function to parse the input file
def parse_input_file(input_file):
    with open(input_file, 'r') as file:
        lines = file.readlines()

    num_tests = int(re.search(r'Number of tests\s*:\s*(\d+)', lines[0]).group(1))
    num_machines = int(re.search(r'Number of machines\s*:\s*(\d+)', lines[1]).group(1))
    num_resources = int(re.search(r'Number of resources\s*:\s*(\d+)', lines[2]).group(1))

    test_durations = []
    machines = [[0 for _ in range(num_tests)] for _ in range(num_machines)]
    resources = [[0 for _ in range(num_tests)] for _ in range(num_machines)]

    # Regular expression to match the 'test' lines in the input file
    test_pattern = re.compile(r"test\(\s*'[^']*',\s*(\d+),\s*\[(.*?)\],\s*\[(.*?)\]\s*\)")

    for cont in range(3, len(lines)):
        line = lines[cont]
        match = test_pattern.match(line.strip())
        if match:
            duration = int(match.group(1))
            test_durations.append(duration)

            # Extract and clean machine names, remove quotes, and strip 'm'
            test_machines = [int(m.strip().replace("'", "").strip()[1:]) for m in match.group(2).split(',')] if match.group(2).strip() else []
            if len(test_machines) != 0:
                for i in test_machines:
                    machines[i-1][cont - 3] = 1
            else:
                for i in range(num_machines):
                    machines[i][cont - 3] = 1

            # Extract and clean resource names, remove quotes, and strip 'r'
            test_resources = [int(r.strip().replace("'", "").strip()[1:]) for r in match.group(3).split(',')] if match.group(3).strip() else []
            print(test_resources)
            if len(test_resources) != 0:
                for i in test_resources:
                    resources[i-1][cont - 3] = 1


    print(f"Number of tests: {num_tests} \nNumber of machines: {num_machines} \nNumber of resources: {num_resources} \nTest Durations: {test_durations} \nMachines Needed: {machines} \nResources Needed: {resources}")
    return num_tests, num_machines, num_resources, test_durations, machines, resources


# Function to solve the MiniZinc model with the parsed input data
def solve_mzn_with_parsed_input( input_file):
    # Parse the custom input file
    num_tests, num_machines, num_resources, test_durations, machines, resources = parse_input_file(input_file)

    # Load the MiniZinc model
    model = minizinc.Model("Test_Scheduling.mzn")

    # Load the MiniZinc solver (gecode in this case)
    solver = minizinc.Solver.lookup("gecode")

    # Create an instance of the MiniZinc model
    instance = minizinc.Instance(solver, model)

    # Set the parsed input data
    instance["num_tests"] = num_tests
    instance["num_machines"] = num_machines
    instance["num_resources"] = num_resources
    instance["test_durations"] = test_durations
    instance["resources"] = resources

    # Solve the model
    result = instance.solve()

    # Output all variable assignments
    print(result)

# Main entry point for the script
if __name__ == "__main__":
    # Argument parser setup
    parser = argparse.ArgumentParser(description="Run MiniZinc model with input from a custom file.")
    parser.add_argument('input_file', help="Path to the input data file")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Run the solver with the provided arguments
    solve_mzn_with_parsed_input(args.input_file)
