import os
import subprocess
import time

# Folder containing the files
folder_path = '../tsp-instances/'
proj_script = 'proj.py'

success_count = 0
failure_count = 0
timeout_duration = 90  # timeout (seconds)

# List all files in the specified folder
files = os.listdir(folder_path)

# Loop through each file and execute the proj.py script
for file in files:
    file_path = os.path.join(folder_path, file)
    
    # Ensure it's a file and not a directory
    if os.path.isfile(file_path):
        try:
            # Run the command: python3 proj.py ../x/file with a 10-second timeout
            start_time = time.time()
            result = subprocess.run(['python3', proj_script, file_path],
                                    timeout=timeout_duration, capture_output=True, text=True)
            elapsed_time = time.time() - start_time

            # Check if the process finished within the timeout
            if elapsed_time <= timeout_duration:
                print(f"Success: {file}")
                success_count += 1
            else:
                print(f"Time exceeded: {file}")
                failure_count += 1

        except subprocess.TimeoutExpired:
            print(f"Time exceeded: {file}")
            failure_count += 1

# Print the total number of successes and failures
print(f"\nNumber of successes: {success_count}")
print(f"Number of failures: {failure_count}")
