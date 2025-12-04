#!/usr/bin/env python3
"""
Local Proxy Forwarder
Runs on localhost and forwards to remote proxy with authentication.
No auth dialog needed in browser!
"""

import socket
import threading
import base64
import sys

# Proxy credentials (same for all proxies)
PROXY_USER = "ngbycljc"
PROXY_PASS = "uel9u1dnf6ph"

# Local port to listen on
LOCAL_PORT = 8888


def create_proxy_auth_header():
    """Create Base64 encoded Proxy-Authorization header."""
    credentials = f"{PROXY_USER}:{PROXY_PASS}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Proxy-Authorization: Basic {encoded}\r\n"


def handle_client(client_socket, remote_host, remote_port):
    """Handle a client connection and forward to remote proxy."""
    try:
        # Connect to remote proxy
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((remote_host, int(remote_port)))
        
        # Receive initial request from client
        request = client_socket.recv(65536)
        
        if not request:
            return
        
        # Inject Proxy-Authorization header
        request_str = request.decode('utf-8', errors='ignore')
        
        # Find the end of the first line and inject auth header
        first_line_end = request_str.find('\r\n')
        if first_line_end > 0:
            # Insert auth header after first line
            modified_request = (
                request_str[:first_line_end + 2] +
                create_proxy_auth_header() +
                request_str[first_line_end + 2:]
            )
            remote_socket.send(modified_request.encode())
        else:
            remote_socket.send(request)
        
        # Forward data in both directions
        def forward(src, dst):
            try:
                while True:
                    data = src.recv(65536)
                    if not data:
                        break
                    dst.send(data)
            except:
                pass
            finally:
                try:
                    src.close()
                    dst.close()
                except:
                    pass
        
        # Start bidirectional forwarding
        t1 = threading.Thread(target=forward, args=(client_socket, remote_socket), daemon=True)
        t2 = threading.Thread(target=forward, args=(remote_socket, client_socket), daemon=True)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        try:
            client_socket.close()
        except:
            pass


def start_forwarder(remote_host, remote_port):
    """Start the local proxy forwarder."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', LOCAL_PORT))
    server.listen(100)
    
    print(f"=" * 50)
    print(f"Local Proxy Forwarder Started")
    print(f"=" * 50)
    print(f"Local:  127.0.0.1:{LOCAL_PORT}")
    print(f"Remote: {remote_host}:{remote_port}")
    print(f"Auth:   {PROXY_USER}:***")
    print(f"=" * 50)
    print(f"Use this in Chrome: --proxy-server=http://127.0.0.1:{LOCAL_PORT}")
    print(f"=" * 50)
    
    while True:
        client_socket, addr = server.accept()
        thread = threading.Thread(
            target=handle_client,
            args=(client_socket, remote_host, remote_port),
            daemon=True
        )
        thread.start()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} <remote_host> <remote_port>")
        print(f"Example: python {sys.argv[0]} 82.23.57.8 7262")
        sys.exit(1)
    
    remote_host = sys.argv[1]
    remote_port = sys.argv[2]
    
    try:
        start_forwarder(remote_host, remote_port)
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")

