import minizinc
import re
import argparse
import copy
import datetime

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

    return num_tests, num_machines, num_resources, test_durations, machines, resources


# Function to solve the MiniZinc model with the parsed input data
def solve_mzn_with_parsed_input(num_tests, num_machines, num_resources, test_durations, machines, resources, pointer):
    
    # Compute the number of available machines for each test
    machines_per_test = compute_machines_per_test(machines)
    
    # Calculate resource priorities for the tests
    resource_priority = calculate_resource_priority(resources, num_tests, num_resources)
    
    # Calculate combined priority for each test
    combined_priority = [resource_priority[i] * 1000 + num_machines - machines_per_test[i] for i in range(num_tests)]
    # Sort indices based on combined_priority (highest to lowest)
    test_index_sorted = sorted(range(num_tests), key=lambda i: combined_priority[i], reverse=True)
    # Reorder the machines, resources, test durations, etc., based on sorted test_index_sorted
    machines_sorted, resources_sorted, test_durations_sorted = reorder(
        machines, resources, test_durations, test_index_sorted
    )
    
    
    # Check if there are any tests that can only run on specific machines
    machines_sorted = modify_m_array(machines_sorted)
    
    # Load the MiniZinc model
    model = minizinc.Model("Test_Scheduling.mzn")

    # Load the MiniZinc solver (gecode in this case)
    solver = minizinc.Solver.lookup("com.google.ortools.sat")

    # Create an instance of the MiniZinc model
    instance = minizinc.Instance(solver, model)

    # Pass the sorted and reordered input data to the MiniZinc model
    instance["teste_Number"] = num_tests
    instance["machine_Number"] = num_machines
    instance["resource_Number"] = num_resources
    instance["teste"] = test_durations_sorted
    instance["m"] = machines_sorted
    instance["resources"] = resources_sorted
    instance["pointer"] = pointer

    # Solve the model
    TIMELIMIT = datetime.timedelta(seconds=15)
    result = instance.solve(timeout=TIMELIMIT)
    if not result:
        return None, None, None, None, None, None

    # Revert the sorted results back to their original order
    original_test_start = revert_order(result["test_start"], test_index_sorted )
    original_test_machine = revert_order(result["test_machine"], test_index_sorted )
    original_test_durations = revert_order(test_durations_sorted, test_index_sorted )
    original_machines = revert_matrix_order(machines_sorted, test_index_sorted )
    original_resources = revert_matrix_order(resources_sorted, test_index_sorted )

    # Output all variable assignments
    return result, original_test_durations, original_machines, original_resources, original_test_start, original_test_machine

def binary_search(input_file):
    num_tests, num_machines, num_resources, test_durations, machines, resources = parse_input_file(input_file)
    
    # Binary search starts here
    lower = max(max(test_durations), max(sum(test_durations[i] for i in range(num_tests) if resources[r][i] == 1) for r in range(num_resources)))
    higher = sum(test_durations) - (num_machines - 1) * min(test_durations)

    pointer = lower + (higher - lower) // 2

    while lower < higher:
        #print(f"Lower: {lower}, Higher: {higher}, Pointer: {pointer}")
        temp_result, temp_original_test_durations, temp_original_machines, temp_original_resources, temp_original_test_start, temp_original_test_machine = solve_mzn_with_parsed_input(num_tests, num_machines, num_resources, test_durations, machines, resources, pointer)

        if temp_result is not None:
            result, original_test_durations, original_machines, original_resources, original_test_start, original_test_machine = temp_result, temp_original_test_durations, temp_original_machines, temp_original_resources, temp_original_test_start, temp_original_test_machine
            higher = min(pointer, result["time"])
        else:
            lower = pointer + 1

        pointer = lower + (higher - lower) // 2

    return result, original_test_durations, original_machines, original_resources, original_test_start, original_test_machine, lower


def calculate_resource_priority(resources, num_tests, num_resources):
    # Calculate resource priority: the number of resources used by each test
    resource_priority = [0] * num_tests
    for i in range(num_tests):
        resource_priority[i] = sum(resources[r][i] for r in range(num_resources))
    return resource_priority

# Function to reorder arrays
def reorder(machines, resources, test_durations, sorted_indices):
    """
    Reorder machines, resources, and test_durations based on the sorted_indices.
    This ensures all arrays are ordered according to the number of machines per test.
    """
    machines_sorted = [[machines[j][i] for i in sorted_indices] for j in range(len(machines))]
    resources_sorted = [[resources[j][i] for i in sorted_indices] for j in range(len(resources))]
    test_durations_sorted = [test_durations[i] for i in sorted_indices]

    return machines_sorted, resources_sorted, test_durations_sorted


# Function to revert sorted arrays back to the original order
def revert_order(sorted_list, sorted_indices):
    original_list = [0] * len(sorted_list)
    for i, sorted_index in enumerate(sorted_indices):
        original_list[sorted_index] = sorted_list[i]
    return original_list


# Function to revert sorted matrices back to their original order
def revert_matrix_order(sorted_matrix, sorted_indices):
    original_matrix = [[0 for _ in range(len(sorted_matrix[0]))] for _ in range(len(sorted_matrix))]
    for j in range(len(sorted_matrix)):
        for i, sorted_index in enumerate(sorted_indices):
            original_matrix[j][sorted_index] = sorted_matrix[j][i]
    return original_matrix


def format_machines_output(test_start, test_machine, num_machines, resources):
    output = ""
    
    num_tests = len(test_start)
    num_resources = len(resources)

    for line in range(1, num_machines+1):
        n_tests = sum(1 for machine in test_machine if machine == line)
        line_output = f"machine( 'm{line}', {n_tests}"
        
        tests = []
        for col in range(num_tests):
            time = test_start[col]
            count = test_machine[col]

            if count == line:
                rec = [f"'r{r+1}'" for r in range(num_resources) if resources[r][col] == 1]
                rec_str = f"{','.join(rec)}" if rec else ""
                tests.append(f"('t{col+1}',{time-1}{',' + rec_str if rec_str else ''})")
        
        tests = sorted(tests, key=lambda x: int(x.split(',')[1].split(')')[0]))

        if tests:
            line_output += ", [" + ",".join(tests) + "]"
        line_output += ")\n"
        output += line_output

    return output

# Function to change the machines array. 
# If a test can only run in a single machine its value in that machine becomes 2
def modify_m_array(m):
    for i in range(len(m[0])): 
        machine_sum = sum(m[j][i] for j in range(len(m)))
        if machine_sum == 1:
            for j in range(len(m)):
                if m[j][i] == 1:
                    m[j][i] = 2
    return m

# Function to calculate the amount of machines per test
def compute_machines_per_test(machines):
    num_tests = len(machines[0])
    num_machines = len(machines)
    machines_per_test = [0] * num_tests

    for i in range(num_tests):
        machines_per_test[i] = sum(machines[j][i] == 1 for j in range(num_machines))

    return machines_per_test


# Main entry point for the script
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MiniZinc model with input from a custom file.")
    parser.add_argument('input_file', help="Path to the input data file")
    parser.add_argument('output_file', help="Path to the output result file")
    args = parser.parse_args()

    # Run the solver with the provided arguments
    result, original_test_durations, original_machines, original_resources, original_test_start, original_test_machine, time = binary_search(args.input_file)
    # Open the output file and write the results to it
    with open(args.output_file, 'w') as f:
        f.write(f"% Makespan: {time}\n")
        f.write(format_machines_output(original_test_start, original_test_machine, len(original_machines), original_resources))
