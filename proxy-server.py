#!/usr/bin/env python3
"""
Simple HTTP/HTTPS proxy server that runs in VM to bypass Netskope.
The proxy handles TLS connections, so Mac's Netskope certs aren't used.
"""

import socket
import select
import sys
import ssl
import threading
from urllib.parse import urlparse

LISTEN_PORT = 8888
BUFFER_SIZE = 8192

def handle_client(client_socket, client_addr):
    """Handle a single client connection."""
    try:
        # Read the first request
        request = client_socket.recv(BUFFER_SIZE)
        if not request:
            return

        # Parse the request to get the target
        first_line = request.split(b'\r\n')[0].decode('utf-8', errors='ignore')
        method, url, _ = first_line.split(' ')

        if method == 'CONNECT':
            # HTTPS CONNECT tunnel
            host, port = url.split(':')
            port = int(port)

            # Connect to target
            target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target.connect((host, port))

            # Send 200 Connection Established
            client_socket.send(b'HTTP/1.1 200 Connection Established\r\n\r\n')

            # Tunnel data bidirectionally
            tunnel(client_socket, target)
        else:
            # Regular HTTP request
            parsed = urlparse(url if url.startswith('http') else 'http://' + url)
            host = parsed.hostname
            port = parsed.port or 80

            # Connect to target
            target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target.connect((host, port))
            target.send(request)

            # Tunnel data bidirectionally
            tunnel(client_socket, target)

    except Exception as e:
        print(f"Error handling client {client_addr}: {e}", file=sys.stderr)
    finally:
        client_socket.close()


def tunnel(client, target):
    """Bidirectionally tunnel data between client and target."""
    sockets = [client, target]
    try:
        while True:
            readable, _, _ = select.select(sockets, [], [], 1)

            if client in readable:
                data = client.recv(BUFFER_SIZE)
                if not data:
                    break
                target.sendall(data)

            if target in readable:
                data = target.recv(BUFFER_SIZE)
                if not data:
                    break
                client.sendall(data)
    except Exception as e:
        print(f"Tunnel error: {e}", file=sys.stderr)
    finally:
        target.close()
        client.close()


def main():
    """Start the proxy server."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', LISTEN_PORT))
    server.listen(100)

    print(f"✓ Proxy server listening on 0.0.0.0:{LISTEN_PORT}")
    print("  Ready to accept connections from Mac")
    print("  Press Ctrl+C to stop")

    try:
        while True:
            client_socket, client_addr = server.accept()
            print(f"→ Connection from {client_addr[0]}:{client_addr[1]}")

            # Handle each client in a separate thread
            thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_addr),
                daemon=True
            )
            thread.start()
    except KeyboardInterrupt:
        print("\n✓ Proxy server stopped")
    finally:
        server.close()


if __name__ == '__main__':
    main()
