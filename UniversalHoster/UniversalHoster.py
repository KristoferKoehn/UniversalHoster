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

join_response = '''{
  "request_type": "join",
  "data": {
    "ip": ""
  }
}'''

browse_message = '''{
  "request_type": "browse",
  "data": {}
}
'''

browse_response = '''{
  "request_type": "browse_response",
  "data": {
    "servers": [
    ]
  }
}
'''


def print_dict_recursive(input_dict, indent=0):
    for key, value in input_dict.items():
        if isinstance(value, dict):
            print(f"{' ' * indent}{key}:")
            print_dict_recursive(value, indent + 2)
        else:
            print(f"{' ' * indent}{key}: {value}")


def json_string_to_dict(utf8_json_string):
    try:
        # Decode the UTF-8 encoded JSON string
        decoded_json = utf8_json_string

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
    print(result_dict["request_type"])

    if result_dict["request_type"] == "host":
        host_id = str(uuid.uuid4())
        unique_identifier = result_dict["data"]["server_name"]
        hosts[host_id] = {
            "ip": result_dict["data"]["ip_address"],
            "registration_time": datetime.now(),
            "unique_identifier": result_dict["data"]["server_name"],
        }
        print(f"Host ID {host_id} ({unique_identifier}) registered from {client_socket.getpeername()[0]}")
        host_response = {
            "request_type": "host_response",
            "uuid": f"{host_id}"
        }
        client_socket.send(dict_to_utf8_json_string(host_response))
    elif result_dict["request_type"] == "browse":
        b_dict = json_string_to_dict(browse_response)
        for host_id, info in hosts.items():
            b_dict["data"]["servers"].append({"uuid": host_id, "server_name": info["unique_identifier"]})
        message = dict_to_utf8_json_string(b_dict)
        client_socket.send(message)
    elif result_dict["request_type"] == "join":
        if result_dict["data"]["unique_identifier"] in hosts:
            host_ip = hosts[result_dict["data"]["unique_identifier"]]["ip"]
            message = f' {{"request_type\" : \"join\",\"data\": {{\"ip\": \"{host_ip}\"}}}}'
            print(message)
            client_socket.send(message.encode("utf-8"))
    elif result_dict["request_type"] == "host_refresh":
        if result_dict["uuid"] in hosts:
            hosts[result_dict["uuid"]]["registration_time"] = datetime.now()
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
