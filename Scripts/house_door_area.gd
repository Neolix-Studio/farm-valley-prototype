extends Area2D

@export_file("*.tscn") var destination_scene_path: String

@onready var prompt: Label = $Prompt

var player_at_door: bool = false

func _process(_delta: float) -> void:
	if player_at_door and Input.is_action_just_pressed("interact"):
		print("Enter the house")
		get_tree().change_scene_to_file(destination_scene_path)
		

func _on_body_entered(_body: Node2D) -> void:
	player_at_door = true
	prompt.show()
	
func _on_body_exited(_body: Node2D) -> void:
	player_at_door = false
	prompt.hide()
	
