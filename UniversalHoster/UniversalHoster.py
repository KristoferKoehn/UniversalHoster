import socket
import threading
import uuid
import time
import json
from datetime import datetime, timedelta

# Dictionary to store host IDs, their corresponding IP addresses, and registration times
hosts = {}

host_message = '''{
  "request_type": "host",
  "data": {
    "ip_address": "",
    "server_name": ""
  }
}'''

success_host_message = '''{
  "request_type": "host_success",
  "data": {
    "uuid": ""
  }
}'''

join_message = '''{
  "request_type": "join",
  "data": {
    "server_name": ""
  }
}'''

browse_message = '''{
  "request_type": "browse",
  "data": {}
}
'''

browse_response = '''{
  "response_type": "browse_response",
  "data": {
    "servers": [
      {
        "uuid": "",
        "server_name": ""
      }
    ]
  }
}
'''


def json_string_to_dict(utf8_json_string):
    try:
        # Decode the UTF-8 encoded JSON string
        decoded_json = utf8_json_string.decode('utf-8')

        # Parse the JSON string into a Python dictionary
        json_dict = json.loads(decoded_json)

        return json_dict

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None


def dict_to_utf8_json_string(data_dict):
    try:
        # Serialize the dictionary to a JSON-formatted string
        json_string = json.dumps(data_dict)

        # Encode the JSON string to UTF-8
        utf8_encoded_string = json_string.encode('utf-8')

        return utf8_encoded_string

    except Exception as e:
        print(f"Error converting dictionary to UTF-8 JSON string: {e}")
        return None


def handle_client(client_socket):
    try:
        request = client_socket.recv(1024)
        print("command:" + str(request))
        request = request.decode("utf-8").strip()

    except ConnectionResetError:
        print(f"Connection terminated abruptly with {client_socket.getpeername()[0]}")
        return

    result_dict = json_string_to_dict(request)

    if result_dict["request_type"] == "host":
        host_id = str(uuid.uuid4())
        unique_identifier = result_dict["server_name"]
        hosts[host_id] = {
            "ip": result_dict["data"]["ip_address"],
            "registration_time": datetime.now(),
            "unique_identifier": result_dict["server_name"],
        }
        print(f"Host ID {host_id} ({unique_identifier}) registered from {client_socket.getpeername()[0]}")
        client_socket.send(host_id.encode("utf-8"))
    elif result_dict["request_type"] == "browse":
        b_dict = json_string_to_dict(browse_response.decode("utf-8"))
        for host_id, info in hosts.items():
            b_dict["data"]["servers"].append({host_id: info["unique_identifier"]})
            message = dict_to_utf8_json_string(b_dict)
            client_socket.send(message)


    ## OLD STUFF, NO JSON
    if request.startswith("host "):
        _, _, unique_identifier = request.partition(' ')  # Extract the unique identifier
        # Generate a unique host ID
        host_id = str(uuid.uuid4())
        # Store the host's IP address, registration time, and unique identifier
        hosts[host_id] = {
            "ip": client_socket.getpeername()[0],
            "registration_time": datetime.now(),
            "unique_identifier": unique_identifier,
        }
        print(f"Host ID {host_id} ({unique_identifier}) registered from {client_socket.getpeername()[0]}")
        client_socket.send(host_id.encode("utf-8"))

    elif request == "browse":
        # Send a list of host IDs along with unique identifiers to the client
        if len(hosts) < 1:
            client_socket.send("123 456".encode("utf-8"))
        else:
            host_info_list = [f"{host_id} {info['unique_identifier']}" for host_id, info in hosts.items()]
            host_info_str = "\n".join(host_info_list)
            print("Sending: " + host_info_str + " end of message")
            client_socket.send(host_info_str.encode("utf-8"))

    elif request.startswith("join "):
        host_id = request.split()[1]
        if host_id in hosts:
            host_ip = hosts[host_id]["ip"]
            client_socket.send(host_ip.encode("utf-8"))
        else:
            client_socket.send("".encode("utf-8"))

    elif request.startswith("delete "):
        host_id = request.split()[1]
        if host_id in hosts:
            del hosts[host_id]
            client_socket.send("Host deleted.".encode("utf-8"))
        else:
            client_socket.send("".encode("utf-8"))

    else:
        print("invalid command: " + request)
        client_socket.send("0000".encode("utf-8"))

    client_socket.close()


# Function to clean up hosts that have been registered for more than 20 minutes
def cleanup_hosts():
    while True:
        current_time = datetime.now()
        for host_id, host_info in list(hosts.items()):
            registration_time = host_info["registration_time"]
            if current_time - registration_time > timedelta(minutes=20):
                del hosts[host_id]
                print(f"Host ID {host_id} removed due to timeout.")
        time.sleep(60)  # Sleep for 1 minute before checking again


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 9999))
    server.listen(5)
    print("Server listening on port 9999")

    # Start the host cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_hosts)
    cleanup_thread.daemon = True
    cleanup_thread.start()

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr[0]}:{addr[1]}")

        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()


if __name__ == "__main__":
    main()
