import socket

def send_message(ip_address, port, message):
    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Send the message
        s.settimeout(10)
        s.sendto(message.encode(), (ip_address, port))
    except ConnectionRefusedError:
        print("Connection refused to neighboor", ip_address)
    except TimeoutError:
        print("Connection timed out to neighboor", ip_address)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
    finally:
        # Close the socket
        s.close()

# Example usage
ip_address = "10.132.241.200"  # Replace with the desired IP address
port = 5000  # Replace with the desired port number
message = "*192.168.88.124;1*192.168.50.123;2"  # Replace with your message

send_message(ip_address, port, message)
