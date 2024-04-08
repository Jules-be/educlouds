import subprocess

def run_bandit(file_or_directory):
    print("Running Bandit static analysis...")
    result = subprocess.run(["bandit", "-r", file_or_directory], capture_output=True, text=True)
    print(result.stdout)

def run_safety(requirements_file):
    print("Running Safety dependency check...")
    result = subprocess.run(["safety", "check", "-r", requirements_file], capture_output=True, text=True)
    print(result.stdout)

if __name__ == "__main__":
    python_code_path = "src/server.py"
    requirements_file_path = "../requirements.txt"

    run_bandit(python_code_path)
    run_safety(requirements_file_path)
