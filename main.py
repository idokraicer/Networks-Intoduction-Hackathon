import subprocess
import time

# Path to the client script
CLIENT_SCRIPT = "C:\\Users\\kidox\\Documents\\GitHub\\Networks-Intoduction_Hackathon\\client\\client.py"

# Test configurations
TEST_CONFIGS = [
    {"file_size": 1024, "tcp_connections": 1, "udp_connections": 1},
    {"file_size": 2048, "tcp_connections": 2, "udp_connections": 2},
    {"file_size": 8192, "tcp_connections": 4, "udp_connections": 4},
    {"file_size": 16 * 1024 * 1024, "tcp_connections": 8, "udp_connections": 8},  # 16 MB
    {"file_size": 400 * 1024 * 1024, "tcp_connections": 1, "udp_connections": 1}  # 400 MB
]


def run_client(file_size, tcp_connections, udp_connections):
    """
    Run the client script for a given test configuration and measure its duration.
    """
    start_time = time.time()
    timeout = 300 if file_size < 100 * 1024 * 1024 else 600  # Adjust timeout for large files
    try:
        result = subprocess.run(
            ["python", CLIENT_SCRIPT, str(file_size), str(tcp_connections), str(udp_connections)],
            text=True,
            capture_output=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        print(result.stdout)
        print(result.stderr)
    except subprocess.TimeoutExpired:
        print(f"Client timed out for file_size={file_size}, tcp_connections={tcp_connections}, udp_connections={udp_connections}")
    except Exception as e:
        print(f"Error running client: {e}")
    finally:
        elapsed_time = time.time() - start_time
        print(f"Test completed in {elapsed_time:.2f} seconds.")


def main():
    """
    Run tests for multiple configurations.
    """
    print("Starting client tests...")
    
    for config in TEST_CONFIGS:
        run_client(config["file_size"], config["tcp_connections"], config["udp_connections"])
        print(f"Completed test for config: {config}")
        time.sleep(2)  # Pause between tests to allow server reset

    print("All tests completed.")

if __name__ == "__main__":
    main()
