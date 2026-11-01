# Computer Networks — Semester V Academic Notes
Author: Dept of Computer Engineering & IT
Course Code: CS-501

## Chapter 1: Network Models & The OSI 7-Layer Architecture
The OSI (Open Systems Interconnection) reference model divides network communication into seven distinct layers:
1. **Physical Layer:** Responsible for the transmission of raw unstructured bitstreams over a physical medium (cables, radio waves, optical fibers). Deals with voltages, pinouts, and bit timing.
2. **Data Link Layer:** Provides error-free transmission of data frames between two directly connected nodes on the same network. Implements MAC addressing, framing, flow control, and error detection (CRC).
3. **Network Layer:** Handles logical addressing (IPv4/IPv6) and packet routing across intermediate routers to establish end-to-end communication across disparate networks. Protocols: IP, ICMP, OSPF, BGP.
4. **Transport Layer:** Provides end-to-end communication control, reliability, connection multiplexing, and segmentation. Key protocols: TCP and UDP.
5. **Session Layer:** Establishes, manages, and terminates conversational sessions between presentation-layer entities. Controls duplex/half-duplex synchronization points.
6. **Presentation Layer:** Ensures data is readable by the receiving application layer. Handles data translation, character encoding (ASCII, UTF-8), compression, and cryptographic encryption (TLS/SSL).
7. **Application Layer:** Interacts directly with software applications to provide network services. Examples include HTTP/HTTPS, DNS, FTP, SMTP, and SSH.

## Chapter 2: Transport Layer — TCP vs UDP
### Transmission Control Protocol (TCP)
TCP is a connection-oriented, highly reliable transport protocol. Key features:
- **Three-Way Handshake:** Connection established using SYN, SYN-ACK, ACK sequence before data exchange.
- **Reliability:** Guarantees in-order delivery of data packets via sequence numbers and cumulative acknowledgments. Lost packets are automatically retransmitted.
- **Congestion Control & Flow Control:** Uses sliding window protocols (Go-Back-N, Selective Repeat) and algorithms such as Slow Start, Congestion Avoidance, Fast Retransmit, and Fast Recovery.
- **Use Cases:** Web browsing (HTTP/HTTPS), file transfer (FTP, SFTP), email (SMTP/IMAP).

### User Datagram Protocol (UDP)
UDP is a connectionless, lightweight, and unreliable transport protocol. Key features:
- **No Handshake:** Transmits datagrams immediately without initial connection setup delay.
- **No Retransmission:** Packets can arrive out of order, get duplicated, or be dropped silently without acknowledgment.
- **Low Overhead:** Header size is only 8 bytes compared to TCP's 20-60 bytes.
- **Use Cases:** Real-time video conferencing (WebRTC), online gaming, DNS lookups, voice over IP (VoIP), live video streaming.

## Chapter 3: IP Addressing & Routing Protocols
- **IPv4 Address Space:** 32-bit addresses divided into Class A, B, C, D (multicast), and E (reserved). Subnetting uses CIDR (Classless Inter-Domain Routing) notation (e.g., /24 represents a 255.255.255.0 subnet mask).
- **Distance Vector Routing:** Uses the Bellman-Ford algorithm where each router shares its full routing table only with immediate neighbors periodically (e.g., RIP). Subject to count-to-infinity problem.
- **Link-State Routing:** Uses Dijkstra’s shortest path first (SPF) algorithm. Every router constructs a complete topological map of the entire network using Link State Advertisements (e.g., OSPF).
