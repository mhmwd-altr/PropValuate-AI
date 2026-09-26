import json
import os
import sys
import io
import contextlib
import traceback

def execute_notebook(nb_path):
    print(f"Executing notebook: {nb_path}")
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    # Global namespace for execution
    exec_globals = {}
    
    # Change working dir to notebooks directory while executing so relative paths work
    orig_cwd = os.getcwd()
    nb_dir = os.path.dirname(os.path.abspath(nb_path))
    os.chdir(nb_dir)

    try:
        for i, cell in enumerate(nb["cells"]):
            if cell["cell_type"] == "code":
                source = "".join(cell["source"])
                stdout_capture = io.StringIO()
                stderr_capture = io.StringIO()
                
                print(f"  Executing cell {i}...")
                try:
                    with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
                        exec(source, exec_globals)
                    
                    stdout_str = stdout_capture.getvalue()
                    stderr_str = stderr_capture.getvalue()
                    
                    outputs = []
                    if stdout_str:
                        outputs.append({
                            "name": "stdout",
                            "output_type": "stream",
                            "text": [line + "\n" for line in stdout_str.splitlines()]
                        })
                    if stderr_str:
                        outputs.append({
                            "name": "stderr",
                            "output_type": "stream",
                            "text": [line + "\n" for line in stderr_str.splitlines()]
                        })
                    cell["outputs"] = outputs
                    cell["execution_count"] = i
                except Exception as e:
                    print(f"ERROR in cell {i}: {e}")
                    traceback.print_exc()
                    cell["outputs"] = [{
                        "ename": type(e).__name__,
                        "evalue": str(e),
                        "output_type": "error",
                        "traceback": traceback.format_exc().splitlines()
                    }]
                    raise e
    finally:
        os.chdir(orig_cwd)

    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2)
    print(f"Successfully executed and saved outputs to {nb_path}")

if __name__ == "__main__":
    execute_notebook(os.path.join("notebooks", "data_audit.ipynb"))
