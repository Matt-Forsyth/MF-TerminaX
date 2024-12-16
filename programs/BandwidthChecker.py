import iperf3
import time

def get_user_input(prompt, default=None):
    """Get user input with an optional default value."""
    user_input = input(f"{prompt} [{default}]: " if default else f"{prompt}: ")
    return user_input.strip() or default

def check_bandwidth(server_ip, port, duration, reverse):
    """Check bandwidth using iperf3."""
    client = iperf3.Client()
    client.server_hostname = server_ip
    client.port = port
    client.duration = duration
    client.reverse = reverse

    print(f"\nConnecting to {server_ip} on port {port}...\n")
    try:
        result = client.run()
        if result.error:
            print(f"Error: {result.error}")
        else:
            print(f"Test Completed:\n"
                  f"  Protocol: {result.protocol}\n"
                  f"  Sent Bandwidth: {result.sent_Mbps:.2f} Mbps\n"
                  f"  Received Bandwidth: {result.received_Mbps:.2f} Mbps\n"
                  f"  Test Duration: {result.duration} seconds")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    print("=== Bandwidth Checker ===")
    server_ip = get_user_input("Enter the server IP address")
    port = int(get_user_input("Enter the port number"))
    duration = int(get_user_input("Enter the test duration"))
    reverse = get_user_input("Run in reverse mode? (Y/N)", "N").lower() == "Y"

    check_bandwidth(server_ip, port, duration, reverse)

if __name__ == "__main__":
    main()
