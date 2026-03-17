import docker
import os
import json
import tempfile
import tarfile
import io
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = docker.from_env()

SANDBOX_IMAGE = "python:3.11-slim"
TIMEOUT_SECONDS = 30
MEMORY_LIMIT = "128m"
CPU_LIMIT = 0.5

def pull_sandbox_image():
    print(f"Pulling sandbox image: {SANDBOX_IMAGE}")
    print("This may take a minute on first run...")
    try:
        client.images.pull(SANDBOX_IMAGE)
        print("Image ready.")
        return True
    except Exception as e:
        print(f"Error pulling image: {e}")
        return False

def run_code_in_sandbox(code: str, language: str = "python"):
    print(f"Running {language} code in sandbox...")

    try:
        if language == "python":
            result = client.containers.run(
    SANDBOX_IMAGE,
    command=["python", "-c", code],
    mem_limit=MEMORY_LIMIT,
    nano_cpus=int(CPU_LIMIT * 1e9),
    network_disabled=True,
    read_only=False,
    remove=True,
    stdout=True,
    stderr=True
)

            output = result.decode("utf-8")
            return {
                "success": True,
                "output": output,
                "error": None,
                "language": language,
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

    except docker.errors.ContainerError as e:
        return {
            "success": False,
            "output": None,
            "error": e.stderr.decode("utf-8") if e.stderr else str(e),
            "language": language,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {
            "success": False,
            "output": None,
            "error": str(e),
            "language": language,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def run_file_in_sandbox(file_path: str, language: str = "python"):
    print(f"Running file in sandbox: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        filename = os.path.basename(file_path)

        container = client.containers.create(
            SANDBOX_IMAGE,
            command=["python", f"/code/{filename}"],
            mem_limit=MEMORY_LIMIT,
            nano_cpus=int(CPU_LIMIT * 1e9),
            network_disabled=True,
            remove=False,
            stdout=True,
            stderr=True
        )

        tar_buffer = io.BytesIO()
        with tarfile.open(fileobj=tar_buffer, mode='w') as tar:
            code_bytes = code.encode('utf-8')
            info = tarfile.TarInfo(name=filename)
            info.size = len(code_bytes)
            tar.addfile(info, io.BytesIO(code_bytes))
        tar_buffer.seek(0)

        container.put_archive('/code', tar_buffer)
        container.start()

        result = container.wait(timeout=TIMEOUT_SECONDS)
        stdout = container.logs(stdout=True, stderr=False).decode('utf-8')
        stderr = container.logs(stdout=False, stderr=True).decode('utf-8')
        container.remove()

        success = result['StatusCode'] == 0
        return {
            "success": success,
            "output": stdout,
            "error": stderr if not success else None,
            "exit_code": result['StatusCode'],
            "language": language,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    except Exception as e:
        return {
            "success": False,
            "output": None,
            "error": str(e),
            "language": language,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def run_with_rollback(code: str, original_code: str, language: str = "python"):
    print("Running with rollback protection...")

    result = run_code_in_sandbox(code, language)

    if result["success"]:
        print("Code passed in sandbox.")
        return {
            "success": True,
            "output": result["output"],
            "rolled_back": False,
            "final_code": code
        }
    else:
        print("Code failed — rolling back to original.")
        original_result = run_code_in_sandbox(original_code, language)
        return {
            "success": False,
            "output": result["output"],
            "error": result["error"],
            "rolled_back": True,
            "final_code": original_code,
            "original_works": original_result["success"]
        }

def test_sandbox():
    print("=" * 40)
    print("  Sandbox Execution Test")
    print("=" * 40)
    print()

    print("Test 1 — Simple Python code:")
    result = run_code_in_sandbox('print("Hello from sandbox!")', "python")
    if result["success"]:
        print(f"  Output: {result['output'].strip()}")
    else:
        print(f"  Error: {result['error']}")

    print("\nTest 2 — Math calculation:")
    result = run_code_in_sandbox("""
numbers = [10, 20, 30, 40, 50]
average = sum(numbers) / len(numbers)
print(f"Average: {average}")
""", "python")
    if result["success"]:
        print(f"  Output: {result['output'].strip()}")
    else:
        print(f"  Error: {result['error']}")

    print("\nTest 3 — Error handling:")
    result = run_code_in_sandbox("""
x = 10
y = 0
print(x / y)
""", "python")
    if result["success"]:
        print(f"  Output: {result['output'].strip()}")
    else:
        print(f"  Error caught safely: {result['error'].strip()[:80]}")

    print("\nTest 4 — Rollback protection:")
    fixed_code = "print(10 / 0)"
    original_code = "print(10 / 2)"
    result = run_with_rollback(fixed_code, original_code, "python")
    if result["rolled_back"]:
        print(f"  Rolled back successfully — original code works: {result['original_works']}")
    else:
        print(f"  Fix worked: {result['output']}")

    print("\nAll sandbox tests complete.")

if __name__ == "__main__":
    print("Checking Docker connection...")
    try:
        client.ping()
        print("Docker is running.")
        print()
        pull_sandbox_image()
        print()
        test_sandbox()
    except Exception as e:
        print(f"Docker error: {e}")
        print("Make sure Docker Desktop is running.")
