extends Node

@export 
var universal_hoster_address:String
@export
var port:int

func _init(ip:String, _port:int):
	universal_hoster_address = ip
	self.port = _port
	
func initialize_host(ip:String, _port:int):
	universal_hoster_address = ip
	self.port = _port
	
func send_command(command:String) -> String:
	
	var client = StreamPeerTCP.new()
	
	if client.connect_to_host(universal_hoster_address, port) != OK:
		print(client.get_status())
	
	while client.get_status() == client.STATUS_CONNECTING:
		client.poll()
		
	client.set_no_delay(true)
	
	if client.put_data(command.to_ascii_buffer()) != OK:
		print("Send error!")

	var response:String = ""
	
	while client.get_available_bytes() < 1:
		client.poll()
	
	var bytes:int = client.get_available_bytes()
	
	print("we out this bitch: " + str(client.get_available_bytes()))
	
	client.poll()
	print("Status: " + str(client.get_status()))
	#response = client.get_utf8_string()
	#print(response)
	response = client.get_string(bytes)
	#print("error code: " + str(bytes[0]))
	#print("Data: " + str(bytes[1]))
	
	client.poll()
	if client.get_status() != OK:
		print("Receiving status: " + str(client.get_status()))
	client.disconnect_from_host()
	
	return response

func join(uuid:String) -> String:
	return send_command("join {0}".format({"0":uuid}))
	
func browse() -> Array:
	var response:String = send_command("browse")
	var splitted:Array = response.split("\n")
	return splitted

func host(server_name:String) -> String:
	return send_command("host {0}".format({"0":server_name}))
	
func EndHost(uuid:String):
	send_command("delete {0}".format({"0":uuid}))
