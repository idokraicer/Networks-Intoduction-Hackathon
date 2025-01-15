# **Network Speed Test - Client and Server Application**

## **Introduction**

This project implements a network speed test application designed for a hackathon. It compares the performance of TCP and UDP file transfers between a client and a server. The application supports multi-threaded file transfers and dynamically adjusts resources based on file size.

---

## **Features**

- **Server**:

  - Sends broadcast offers over UDP for clients to detect.
  - Handles TCP and UDP requests for file transfers.
  - Supports multi-threaded file transfers for efficient processing of large files.

- **Client**:

  - Listens for server offers and connects to a chosen server.
  - Allows user-configurable parameters for file size, TCP connections, and UDP connections.
  - Measures and logs transfer speeds, transfer times, and packet loss (UDP).
  - Automatically retries in case of errors.

- **Testing Script**:
  - Automates client tests with various configurations.
  - Measures performance for different file sizes and connection counts.

---

## **Usage**

### **Prerequisites**

- Python 3.x installed on the system.
- The `server.py`, `client.py`, and `main.py` files in the same directory.

### **Steps to Run**

1. **Start the Server**:
   Run the server script:

   ```bash
   python server.py
   ```

   The server will begin broadcasting offers and listening for incoming connections.

2. **Run the Client**:
   Run the client script interactively or with command-line arguments:

   - **Interactive Mode**:
     ```bash
     python client.py
     ```
     Enter the requested parameters (file size, TCP connections, UDP connections) when prompted.
   - **Command-Line Arguments**:
     ```bash
     python client.py <file_size> <tcp_connections> <udp_connections>
     ```
     Example:
     ```bash
     python client.py 1048576 4 4  # 1 MB file, 4 TCP connections, 4 UDP connections
     ```

3. **Run Automated Tests**:
   Use the `main.py` script to test multiple configurations automatically:
   ```bash
   python main.py
   ```

---

## **File Descriptions**

1. **server.py**:

   - Implements the server logic, including:
     - Broadcasting UDP offers.
     - Handling TCP and UDP file transfers.
     - Multi-threaded processing for efficient data transfer.
   - Dynamically calculates threads for large file transfers.

2. **client.py**:

   - Implements the client logic, including:
     - Listening for server offers.
     - Configurable TCP and UDP connections for speed tests.
     - Logging performance metrics such as transfer speed and packet loss.

3. **main.py**:
   - Automates client tests with predefined configurations.
   - Measures and logs performance for each test configuration.

---

## **Packet Formats**

### **Offer Packet (UDP)**

- **Magic Cookie** (4 bytes): `0xabcddcba`
- **Message Type** (1 byte): `0x2` (offer)
- **Server UDP Port** (2 bytes): Port for UDP requests.
- **Server TCP Port** (2 bytes): Port for TCP requests.

### **Request Packet (UDP)**

- **Magic Cookie** (4 bytes): `0xabcddcba`
- **Message Type** (1 byte): `0x3` (request)
- **File Size** (8 bytes): Size of the requested file.

### **Payload Packet (UDP)**

- **Magic Cookie** (4 bytes): `0xabcddcba`
- **Message Type** (1 byte): `0x4` (payload)
- **Total Segment Count** (8 bytes): Total number of segments in the data stream.
- **Current Segment Count** (8 bytes): Current segment number.
- **Payload**: Actual data.

---

## **Test Configurations**

Here are the default configurations used in `main.py`:

```python
TEST_CONFIGS = [
    {"file_size": 1024, "tcp_connections": 1, "udp_connections": 1},
    {"file_size": 2048, "tcp_connections": 2, "udp_connections": 2},
    {"file_size": 8192, "tcp_connections": 4, "udp_connections": 4},
    {"file_size": 16 * 1024 * 1024, "tcp_connections": 8, "udp_connections": 8},  # 16 MB
    {"file_size": 400 * 1024 * 1024, "tcp_connections": 1, "udp_connections": 1},  # 400 MB
]
```

---

## **Performance Metrics**

- **TCP Transfers**:
  - Logs transfer speed and duration.
- **UDP Transfers**:
  - Logs transfer speed, duration, and packet loss percentage.

---

## **Error Handling**

- Ensures compatibility with unexpected packet loss or corruption.
- Handles connection timeouts gracefully.
- Implements retries for UDP transfers.

---

## **Code Quality**

- Properly commented and modular.
- Uses dynamic threading for large file transfers.
- Follows Python coding standards for readability and maintainability.

---

## **Future Enhancements**

- Improve error recovery for extreme packet loss.
- Add support for secure data transfers (e.g., encryption).
- Optimize for high-latency networks.

---

## **Acknowledgments**

This project was developed for the "Intro to Computer Networks 2024 Hackathon." It adheres to the assignment guidelines and ensures full compatibility with other teams' implementations.
