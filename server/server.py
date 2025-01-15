import socket
import threading
import struct
import time

MAGIC_COOKIE = 0xabcddcba
MESSAGE_TYPE_OFFER = 0x2
MESSAGE_TYPE_REQUEST = 0x3
MESSAGE_TYPE_PAYLOAD = 0x4

THREAD_THRESHOLD = 4 * 4 * 1024 * 1024  # 16 MB threshold for multi-threading to allow at least 4 threads
MAX_THREADS = 8  # Cap on the number of threads
BASE_CHUNK_SIZE = 4 * 1024 * 1024  # 1 MB per thread

SEGMENT_SIZE = 4 * 1024  # 4 KB segment size



def broadcast_offers(udp_port, tcp_port, interval=1):
    """
    Broadcasts offer messages over UDP.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        try:
            message = struct.pack("!IBHH", MAGIC_COOKIE, MESSAGE_TYPE_OFFER, udp_port, tcp_port)
            sock.sendto(message, ('<broadcast>', udp_port))
            time.sleep(interval)
        except Exception as e:
            print(f"Error broadcasting offers: {e}")


def calculate_threads(file_size, max_threads=MAX_THREADS, base_chunk_size=BASE_CHUNK_SIZE):
    """
    Dynamically calculate the number of threads based on file size.
    """
    if file_size <= THREAD_THRESHOLD:
        return 1
    return min(max_threads, max(1, file_size // base_chunk_size))


def send_file_chunk(client_socket, chunk_index, chunk_size):
    """
    Send a specific file chunk over TCP.
    """
    try:
        data = b"A" * chunk_size
        client_socket.sendall(data)
        print(f"Sent chunk {chunk_index} ({chunk_size} bytes) to client.")
    except Exception as e:
        print(f"Error sending chunk {chunk_index}: {e}")


def handle_tcp_request(client_socket, address):
    """
    Handle a TCP request, splitting the file into chunks if necessary.
    """
    try:
        request = client_socket.recv(1024).decode().strip()
        file_size = int(request)
        print(f"Handling TCP request from {address}. File size: {file_size} bytes.")

        num_threads = calculate_threads(file_size)
        print(f"Using {num_threads} thread(s) for file size {file_size} bytes.")

        if num_threads == 1:
            # Single-threaded transfer
            data = b"A" * file_size
            client_socket.sendall(data)
            print(f"Sent {file_size} bytes to {address} over TCP.")
        else:
            # Multi-threaded transfer
            chunk_size = file_size // num_threads
            threads = []

            for i in range(num_threads):
                current_chunk_size = chunk_size if i < num_threads - 1 else file_size - i * chunk_size
                t = threading.Thread(target=send_file_chunk, args=(client_socket, i, current_chunk_size))
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

            print(f"Multi-threaded transfer to {address} complete.")
    except Exception as e:
        print(f"Error in TCP transfer with {address}: {e}")
    finally:
        client_socket.close()


def handle_udp_request(client_address, file_size):
    """
    Handle a UDP request by sending payload packets.
    """
    try:
        print(f"Handling UDP request from {client_address}. File size: {file_size} bytes.")
        total_segments = (file_size + SEGMENT_SIZE - 1) // SEGMENT_SIZE

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as temp_socket:
            for segment in range(total_segments):
                # Construct payload
                payload = struct.pack("!IBQQ", MAGIC_COOKIE, MESSAGE_TYPE_PAYLOAD, total_segments, segment)
                payload += b"A" * (SEGMENT_SIZE - len(payload))
                temp_socket.sendto(payload, client_address)
                print(f"Sending segment {segment + 1}/{total_segments} to {client_address}")
                time.sleep(0.001)  # Optional: simulate delay

        print(f"Completed UDP transfer to {client_address}. Sent {total_segments} segments.")

    except Exception as e:
        print(f"Error in UDP transfer: {e}")



def server_listener(tcp_port, udp_port):
    """
    Set up the server to listen for TCP and UDP requests.
    """
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind(("127.0.0.1", tcp_port))
    tcp_socket.listen(5)

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("127.0.0.1", udp_port))

    print(f"Server listening on TCP port {tcp_port} and UDP port {udp_port}.")

    while True:
        # Accept TCP connections
        client_socket, client_address = tcp_socket.accept()
        threading.Thread(target=handle_tcp_request, args=(client_socket, client_address)).start()

        # Handle UDP requests
        data, udp_address = udp_socket.recvfrom(4096)
        magic_cookie, message_type, file_size = struct.unpack("!IBQ", data[:13])
        if magic_cookie == MAGIC_COOKIE and message_type == MESSAGE_TYPE_REQUEST:
            threading.Thread(target=handle_udp_request, args=(udp_address, file_size)).start()


if __name__ == "__main__":
    UDP_PORT = 13117
    TCP_PORT = 12345

    threading.Thread(target=broadcast_offers, args=(UDP_PORT, TCP_PORT), daemon=True).start()
    server_listener(TCP_PORT, UDP_PORT)
