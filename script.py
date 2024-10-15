import os
import subprocess
import time

# Folder paths
folder_path = './tsp-instances'
proj_script = 'proj.py'
checker_script = 'checker/checker.py'

success_count = 0
failure_count = 0
checker_pass_count = 0
checker_fail_count = 0
timeout_duration = 30  # timeout (5 mins in seconds)

# List all files in the specified folder
files = os.listdir(folder_path)

output_base_path = './outputs'
os.makedirs(output_base_path, exist_ok=True)

# Step 1: Execute proj.py script for each file
for file in files:
    file_path = os.path.join(folder_path, file)
    output_file_path = os.path.join(output_base_path, file)  # Use this for the output files

    # Ensure it's a file and not a directory
    if os.path.isfile(file_path):
        try:
            # Run the command: python3 proj.py ../x/file with a timeout
            start_time = time.time()
            with open(output_file_path + ".out", 'w') as f_out:
                result = subprocess.run(['python3', proj_script, file_path],
                                        timeout=timeout_duration, stdout=f_out, stderr=subprocess.STDOUT, text=True)
            elapsed_time = time.time() - start_time

            # Check if the process finished within the timeout
            if elapsed_time <= timeout_duration:
                success_count += 1
                print(f"Success: {file} ({elapsed_time:.2f} seconds)")
            else:
                failure_count += 1
                print(f"Failure: {file}")

        except subprocess.TimeoutExpired:
            failure_count += 1
            print(f"Failure: {file}")


# Step 2: Run checker.py for each .out file in the outputs directory and accumulate results
output_files = os.listdir(output_base_path)

validity_results = []  # List to store the validity results for each file
for output_file in output_files:
    if output_file.endswith('.out'):
        # Extract filename without the .out extension
        base_filename = os.path.splitext(output_file)[0]
        
        # Paths for the checker script arguments
        tsp_instance_file = os.path.join('./tsp-instances', base_filename)
        output_file_path = os.path.join(output_base_path, output_file)
        
        # Run the checker script
        try:
            result = subprocess.run(['python3', checker_script, tsp_instance_file, output_file_path],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Check if the last line of result.stdout ends with 'valid'
            output_lines = result.stdout.strip().split('\n')
            last_line = output_lines[-1] if output_lines else ""

            if last_line.endswith('valid.'):
                checker_pass_count += 1
                validity_results.append(f"{output_file}: valid")
            else:
                checker_fail_count += 1
                validity_results.append(f"{output_file}: invalid")

        except Exception as e:
            checker_fail_count += 1
            validity_results.append(f"{output_file}: invalid")

# Step 3: Print all the results together at the end
print("\nChecker Results:")
for result in validity_results:
    print(result)

# Print the total number of successes and failures for proj.py
print(f"\nNumber of successes (proj.py): {success_count}")
print(f"Number of failures (proj.py): {failure_count}")

# Print the total number of valid and invalid results for checker.py
print(f"\nNumber of valid outputs: {checker_pass_count}")
print(f"Number of invalid outputs: {checker_fail_count}")
