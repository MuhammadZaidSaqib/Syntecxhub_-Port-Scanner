import socket
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

DEFAULT_TIMEOUT = 1
DEFAULT_THREADS = 100


# ==============================
# Logging Setup
# ==============================

def setup_logging():
    logging.basicConfig(
        filename="scan_results.txt",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


# ==============================
# Port Scanner Function
# ==============================

def scan_port(host, port, timeout):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))

            if result == 0:
                return port, "OPEN"
            else:
                return port, "CLOSED"

    except socket.timeout:
        return port, "TIMEOUT"
    except Exception as e:
        return port, f"ERROR"


# ==============================
# Validation
# ==============================

def validate_ports(start_port, end_port):
    if start_port < 1 or end_port > 65535:
        print("❌ Ports must be between 1 and 65535.")
        sys.exit(1)

    if start_port > end_port:
        print("❌ Start port cannot be greater than end port.")
        sys.exit(1)


# ==============================
# Main
# ==============================

def main():

    print("=" * 60)
    print("🚀 FalconStrix TCP Port Scanner")
    print("=" * 60)

    # Take user input
    host = input("Enter Target Host (IP or Domain): ").strip()

    try:
        start_port = int(input("Enter Start Port: "))
        end_port = int(input("Enter End Port: "))
    except ValueError:
        print("❌ Ports must be numbers.")
        sys.exit(1)

    threads_input = input(f"Enter Number of Threads (default {DEFAULT_THREADS}): ").strip()
    timeout_input = input(f"Enter Timeout in Seconds (default {DEFAULT_TIMEOUT}): ").strip()

    threads = int(threads_input) if threads_input else DEFAULT_THREADS
    timeout = float(timeout_input) if timeout_input else DEFAULT_TIMEOUT

    validate_ports(start_port, end_port)
    setup_logging()

    print("\nStarting scan...\n")
    print(f"Target      : {host}")
    print(f"Port Range  : {start_port} - {end_port}")
    print(f"Threads     : {threads}")
    print(f"Timeout     : {timeout}s")
    print("-" * 60)

    start_time = datetime.now()

    try:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {
                executor.submit(scan_port, host, port, timeout): port
                for port in range(start_port, end_port + 1)
            }

            for future in as_completed(futures):
                port, status = future.result()

                if status == "OPEN":
                    print(f"[+] Port {port:5} OPEN")
                elif status == "CLOSED":
                    print(f"[-] Port {port:5} CLOSED")
                elif status == "TIMEOUT":
                    print(f"[!] Port {port:5} TIMEOUT")
                else:
                    print(f"[x] Port {port:5} {status}")

                logging.info(f"{host}:{port} - {status}")

    except KeyboardInterrupt:
        print("\n⚠️ Scan interrupted by user.")
        sys.exit(0)

    end_time = datetime.now()

    print("-" * 60)
    print("✅ Scan Completed")
    print(f"Finished at : {end_time}")
    print(f"Duration    : {end_time - start_time}")
    print("=" * 60)


if __name__ == "__main__":
    main()
