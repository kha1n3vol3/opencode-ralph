import subprocess
import sys
import json
import os


def main():
    if len(sys.argv) != 3:
        print("Usage: python ralph_loop.py <max_iterations> <prompt>")
        print(
            'Example: python ralph_loop.py 20 "Implement features from prd.json one by one."'
        )
        sys.exit(1)

    max_iter = int(sys.argv[1])
    prompt = sys.argv[2]
    completion_promise = "<promise>COMPLETE</promise>"

    # Required files
    prd_file = "prd.json"
    progress_file = "progress.txt"
    if not os.path.exists(prd_file):
        print(f"Error: {prd_file} not found. Create it with your task list.")
        sys.exit(1)
    if not os.path.exists(progress_file):
        open(progress_file, "w").close()  # Create empty if missing

    # Optional: Customize model/flags (e.g., add --file for more attachments)
    opencode_opts = f"--model claude/sonnet --file {prd_file} --file {progress_file}"

    # Function to run opencode and capture output
    def run_opencode(extra_args=""):
        cmd = (
            ["opencode", "run"] + opencode_opts.split() + [extra_args, prompt]
            if extra_args
            else ["opencode", "run"] + opencode_opts.split() + [prompt]
        )
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running opencode: {result.stderr}")
            sys.exit(1)
        return result.stdout.strip()

    # Function to commit changes (mimic transcript's git commit)
    def git_commit(message="Ralph iteration commit"):
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", message], check=True)
        print("Git commit made.")

    # Start initial iteration
    print("Starting initial iteration...")
    result = run_opencode()
    print(result)

    # Post-iteration: Commit if no error
    git_commit("Initial Ralph commit")

    if completion_promise in result:
        print("Task complete on first iteration.")
        sys.exit(0)

    # Loop for subsequent iterations
    for i in range(1, max_iter):
        print(f"Iteration {i} of {max_iter}...")
        result = run_opencode("--continue")
        print(result)

        # Commit after each iteration
        git_commit(f"Ralph commit after iteration {i}")

        if completion_promise in result:
            print("Task complete.")
            sys.exit(0)

        # Optional: Check if PRD is manually complete (safety net)
        with open(prd_file, "r") as f:
            prd = json.load(f)
        if all(item.get("passes", False) for item in prd):
            print("PRD fully passed manually. Exiting.")
            sys.exit(0)

    print(
        "Max iterations reached. Check prd.json, progress.txt, and git log for progress."
    )


if __name__ == "__main__":
    main()
