import socket
import struct
import time
import threading
import sys

MAGIC_COOKIE = 0xabcddcba
MESSAGE_TYPE_REQUEST = 0x3
MESSAGE_TYPE_PAYLOAD = 0x4

BASE_CHUNK_SIZE = 4 * 1024 * 1024  # 4 MB per thread

SEGMENT_SIZE = 4 * 1024  # 4 KB segment size



def send_tcp_request(server_ip, tcp_port, file_size):
    """
    Send a TCP request and measure transfer speed.
    """
    start_time = time.time()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((server_ip, tcp_port))
            sock.sendall(f"{file_size}\n".encode())
            data = sock.recv(min(BASE_CHUNK_SIZE, 8 * 1024 * 1024))  # Receive in 8 MB chunks
        elapsed_time = time.time() - start_time
        speed = file_size / elapsed_time
        print(f"\033[92mTCP transfer complete: {speed:.2f} bytes/second\033[0m")
    except Exception as e:
        print(f"\033[91mError in TCP transfer: {e}\033[0m")


def send_udp_request(server_ip, udp_port, file_size):
    """
    Send a UDP request, process responses, and calculate transfer metrics.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(2)  # Timeout for responses
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Bind to a unique local port
            local_port = 13118 + threading.get_ident() % 1000
            sock.bind(("127.0.0.1", local_port))
            print(f"Client UDP socket bound to {sock.getsockname()} on thread {threading.get_ident()}")

            # Send the request packet
            request_packet = struct.pack("!IBQ", MAGIC_COOKIE, MESSAGE_TYPE_REQUEST, file_size)
            sock.sendto(request_packet, (server_ip, udp_port))
            print(f"UDP request sent to {server_ip}:{udp_port} for {file_size} bytes.")

            # Receive packets
            start_time = time.time()
            received_packets = set()
            total_segments = (file_size + SEGMENT_SIZE - 1) // SEGMENT_SIZE

            try:
                while True:
                    # Ensure buffer size is sufficient
                    data, addr = sock.recvfrom(SEGMENT_SIZE + 128)
                    if len(data) < 21:  # Ignore incomplete packets
                        continue

                    # Extract packet details
                    _, message_type, total, segment = struct.unpack("!IBQQ", data[:21])
                    if message_type == MESSAGE_TYPE_PAYLOAD and 0 <= segment < total_segments:
                        received_packets.add(segment)
                        print(f"Received packet: Segment {segment + 1}/{total_segments} from {addr}")
            except socket.timeout:
                pass  # No more packets received

            elapsed_time = time.time() - start_time
            packet_loss = 100 * (1 - len(received_packets) / total_segments) if total_segments > 0 else 100
            speed = (len(received_packets) * SEGMENT_SIZE) / elapsed_time if elapsed_time > 0 else 0

            print(f"\033[92mUDP transfer complete: {speed:.2f} bytes/second, Packet loss: {packet_loss:.2f}%\033[0m")

    except Exception as e:
        print(f"\033[91mError in UDP transfer: {e}\033[0m")



def get_user_input():
    """
    Get user input for test parameters.
    Supports both command-line arguments and interactive input.
    """
    try:
        if len(sys.argv) > 1:
            # Read from command-line arguments
            file_size = int(sys.argv[1])
            tcp_connections = int(sys.argv[2])
            udp_connections = int(sys.argv[3])
        else:
            # Interactive input
            file_size = int(input("Enter file size (bytes): "))
            tcp_connections = int(input("Enter the number of TCP connections: "))
            udp_connections = int(input("Enter the number of UDP connections: "))
        return file_size, tcp_connections, udp_connections
    except (ValueError, IndexError):
        print("\033[91mInvalid input! Please enter numeric values.\033[0m")
        sys.exit(1)


if __name__ == "__main__":
    SERVER_IP = "127.0.0.1"
    UDP_PORT = 13117
    TCP_PORT = 12345

    # Get user input for test parameters
    FILE_SIZE, TCP_CONNECTIONS, UDP_CONNECTIONS = get_user_input()

    # Start specified number of TCP and UDP transfers in separate threads
    threads = []
    for _ in range(TCP_CONNECTIONS):
        t = threading.Thread(target=send_tcp_request, args=(SERVER_IP, TCP_PORT, FILE_SIZE))
        t.start()
        threads.append(t)

    for _ in range(UDP_CONNECTIONS):
        t = threading.Thread(target=send_udp_request, args=(SERVER_IP, UDP_PORT, FILE_SIZE))
        t.start()
        threads.append(t)

    # Wait for all threads to complete
    for t in threads:
        t.join()

    print("\033[92mClient execution completed.\033[0m")
    sys.exit(0)

