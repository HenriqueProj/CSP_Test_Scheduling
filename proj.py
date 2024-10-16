import minizinc
import re
import argparse
import copy

sorted_indices = []

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
    
    #print(test_durations)
    """
    # Sort test durations to record the swaps
    global sorted_indices 
    sorted_indices = sorted(range(num_tests), key=lambda i: test_durations[i], reverse=True)

    # Sort the arrays based on the sorted indices
    test_durations = [test_durations[i] for i in sorted_indices]
    machines = [[machines[j][i] for i in sorted_indices] for j in range(len(machines))]
    resources = [[resources[j][i] for i in sorted_indices] for j in range(len(resources))]
    """
            
    return num_tests, num_machines, num_resources, test_durations, machines, resources


# Function to solve the MiniZinc model with the parsed input data
def solve_mzn_with_parsed_input(input_file):
    # Parse the custom input file
    num_tests, num_machines, num_resources, test_durations, machines, resources = parse_input_file(input_file)
    
    # Step 1: Compute the number of available machines for each test
    machines_per_test = compute_machines_per_test(machines)
    
    # Sort the machines_per_test based on the number of machines available for each test
    sorted_indices = sorted(range(num_tests), key=lambda i: machines_per_test[i])
    
    # Reorder machines and resources according to sorted_indices
    #machines_sorted, resources_sorted = reorder(machines, resources, sorted_indices)
    
    # Check if there are any tests that can only run in a specific machine
    machines = modify_m_array(machines)

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
    #instance["m"] = machines_sorted
    #instance["resources"] = resources_sorted
    instance["m"] = machines
    instance["resources"] = resources

    # Step 7: Pass the sorted test order to MiniZinc for the int_search
    instance["machine_per_test"] = machines_per_test  # Pass original machines_per_test

    # Create and send the color_of_machines array
    #color_of_machines = create_color_of_machines(machines_sorted)
    #instance["color_of_machines"] = color_of_machines

    # Solve the model
    result = instance.solve()
    
    # Output all variable assignments
    return result, num_machines, resources


def reorder(machines, resources, test_durations, sorted_indices):
    """
    Reorder machines, resources, and test_durations based on the sorted_indices.
    This ensures all arrays are ordered according to the number of machines per test.
    """
    # Reorder the machines array
    machines_sorted = [[machines[j][i] for i in sorted_indices] for j in range(len(machines))]
    
    # Reorder the resources array
    resources_sorted = [[resources[j][i] for i in sorted_indices] for j in range(len(resources))]
    
    # Reorder the test_durations array
    test_durations_sorted = [test_durations[i] for i in sorted_indices]

    return machines_sorted, resources_sorted, test_durations_sorted



def format_machines_output(test_start, test_machine, num_machines, resources):
    """
    machines, resources = reorder(machines, resources)
    """

    output = ""
    
    num_tests= len(test_start)
    num_resources = len(resources)

    for line in range(1, num_machines+1):
        # Count the number of tests (i.e., number of non-(0, 0) tuples in this line)
        n_tests = sum(1 for machine in test_machine if machine == line)
        
        # Start forming the machine output for the current line
        line_output = f"machine( 'm{line}', {n_tests}"
        
        # Collect the test information for this machine (line)
        tests = []
        for col in range(num_tests):
            time = test_start[col]
            count = test_machine[col]

            if count == line:
                # Collect resources for the current test
                rec = [f"'r{r+1}'" for r in range(num_resources) if resources[r][col] == 1]
                
                # Format the resource string without brackets, just commas between resources
                rec_str = f"{','.join(rec)}" if rec else ""
                
                # Add the tuple (test) with time and optional resource
                tests.append(f"('t{col+1}',{time-1}{',' + rec_str if rec_str else ''})")
        
        # If there are tests, format them as an array and append to line output
        # sort tests by the second element
        tests = sorted(tests, key=lambda x: int(x.split(',')[1].split(')')[0]))

        if tests:
            line_output += ", [" + ",".join(tests) + "]"

        # Close the line output
        line_output += ")\n"  # Add a newline character at the end of each machine output
        output += line_output

    return output

# Function to modify the m array based on the condition that the sum of the subarray is 1
def modify_m_array(m):
    # Iterate over each test (i.e., each index i in the m array)
    for i in range(len(m[0])):  # Iterate through tests (columns)
        # For each test, check the sum of the corresponding subarray (machines)
        machine_sum = sum(m[j][i] for j in range(len(m)))
        # If sum is 1, mark that machine by setting the 1 to 2
        if machine_sum == 1:
            for j in range(len(m)):
                if m[j][i] == 1:
                    m[j][i] = 2  # Mark this machine with 2 since it is the only one that can execute this test
    return m

# Function to generate the color_of_machines array
def create_color_of_machines(machines):
    num_machines = len(machines)
    machine_groups = {}

    # Create a mapping of unique test capability combinations to a group number
    for machine_id, machine_tests in enumerate(machines):
        machine_tuple = tuple(machine_tests)
        if machine_tuple not in machine_groups:
            machine_groups[machine_tuple] = len(machine_groups) + 1

    # Create the color_of_machines array based on the group each machine belongs to
    color_of_machines = [machine_groups[tuple(machines[i])] for i in range(num_machines)]
    return color_of_machines

def compute_machines_per_test(machines):
    """
    Calculate how many machines each test can run on.
    """
    num_tests = len(machines[0])
    num_machines = len(machines)
    machines_per_test = [0] * num_tests

    for i in range(num_tests):
        machines_per_test[i] = sum(machines[j][i] == 1 for j in range(num_machines))

    return machines_per_test

# Main entry point for the script
if __name__ == "__main__":
    # Argument parser setup
    parser = argparse.ArgumentParser(description="Run MiniZinc model with input from a custom file.")
    parser.add_argument('input_file', help="Path to the input data file")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Run the solver with the provided arguments
    result, num_machines, resources = solve_mzn_with_parsed_input(args.input_file)

    #print(result)
    print("% Makespan: ", result["objective"])
    print(format_machines_output(result["test_start"], result["test_machine"], num_machines, resources))