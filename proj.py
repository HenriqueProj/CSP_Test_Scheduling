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
    resources = [[0 for _ in range(num_tests)] for _ in range(num_resources)]

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

            if len(test_resources) != 0:
                for i in test_resources:
                    resources[i-1][cont - 3] = 1

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
    instance["teste_Number"] = num_tests
    instance["machine_Number"] = num_machines
    instance["resource_Number"] = num_resources
    
    instance["teste"] = test_durations
    instance["m"] = machines
    instance["resources"] = resources
    
    # Solve the model
    result = instance.solve()
    
    # Output all variable assignments
    return result, resources


def format_machines_output(machines, resources):
    output = ""
    num_lines = len(machines)
    num_columns = len(machines[0])
    num_resources = len(resources)

    for line in range(num_lines):
        # Count the number of tests (i.e., number of non-(0, 0) tuples in this line)
        n_tests = sum(1 for time, count in machines[line] if count > 0)
        
        # Start forming the machine output for the current line
        line_output = f"machine( 'm{line+1}', {n_tests}"
        
        # Collect the test information for this machine (line)
        tests = []
        for col in range(num_columns):
            time, count = machines[line][col]
            if count > 0:
                # Collect resources for the current test
                rec = [f"'r{r+1}'" for r in range(num_resources) if resources[r][col] == 1]
                
                # Format the resource string without brackets, just commas between resources
                rec_str = f"{','.join(rec)}" if rec else ""
                
                # Add the tuple (test) with time and optional resource
                tests.append(f"('t{col+1}',{time-1}{',' + rec_str if rec_str else ''})")
        
        # If there are tests, format them as an array and append to line output
        if tests:
            line_output += ", [" + ",".join(tests) + "]"

        # Close the line output
        line_output += ")\n"  # Add a newline character at the end of each machine output
        output += line_output

    return output


# Main entry point for the script
if __name__ == "__main__":
    # Argument parser setup
    parser = argparse.ArgumentParser(description="Run MiniZinc model with input from a custom file.")
    parser.add_argument('input_file', help="Path to the input data file")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Run the solver with the provided arguments
    result, resources = solve_mzn_with_parsed_input(args.input_file)

    print("% Makespan: ", result["objective"])
    print(format_machines_output(result["machines"], resources))