import socket


def is_connected(hostname: str):
    try:
        # See if we can resolve the host name - tells us if there is
        # a DNS listening
        host = socket.gethostbyname(hostname)
        # Connect to the host - tells us if the host is actually reachable
        s = socket.create_connection((host, 80), 2)
        s.close()

        return True
    except Exception:
        pass # We ignore any errors, returning False

    return False