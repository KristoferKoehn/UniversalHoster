extends Node2D

var connector
var uuid:String
var timer
# Called when the node enters the scene tree for the first time.
func _ready():
	connector = preload("res://Scripts/UniversalConnector.gd").new("127.0.0.1", 9999)
	timer = Timer.new()
	self.add_child(timer)
	timer.timeout.connect(timer_timeout_handler)
	timer.start(4)
	$Control/Panel/Tree.clear()
	$Control/Panel/Tree.create_item()
	$Control/Panel/Tree.hide_root = true


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(_delta):
	pass


func _on_host_pressed():
	uuid = connector.host($Control/Panel/ServerName.text)


func _on_join_pressed():
	$Control/Panel/IpLabel.text = connector.join($Control/Panel/Tree.get_selected().get_text(0))
	
func timer_timeout_handler():
	$Control/Panel/Tree.clear()
	$Control/Panel/Tree.create_item()
	$Control/Panel/Tree.hide_root = true
	var browse_list:Array = await connector.browse()
	if browse_list[0] == "":
		return
	
	for item in browse_list:
		var info:Array = item.split(" ", true, 1)
		var temp:TreeItem = $Control/Panel/Tree.create_item()
		temp.set_text(0, info[0])
		temp.set_text(1, info[1])
		
