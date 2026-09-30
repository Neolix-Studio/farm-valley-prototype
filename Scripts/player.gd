extends CharacterBody2D
signal tool_used(target_position: Vector2)
signal seed_used(target_position: Vector2)
## Top-down farm hand.  The Tiny Wonder sheet only has left/right facings,
## so vertical movement keeps whichever side the player last faced.

@export var speed: float = 78.0

@onready var _sprite: AnimatedSprite2D = $Sprite

var _facing: String = "right"
var facing_direction: Vector2 = Vector2.DOWN



func _physics_process(_delta: float) -> void:
	var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	var use_tool := Input.is_action_just_pressed("use_tool")
	var plant_seed_pressed := Input.is_action_just_pressed("plant_seed")
	velocity = direction * speed
	move_and_slide()

	if direction.x > 0.1:
		_facing = "right"
		facing_direction = Vector2.RIGHT
	elif direction.x < -0.1:
		_facing = "left"
		facing_direction = Vector2.LEFT
	elif direction.y > 0.1:
		facing_direction = Vector2.DOWN
	elif direction.y < -0.1:
		facing_direction = Vector2.UP
		
	if use_tool:
		var player_position := global_position + facing_direction * 16
		tool_used.emit(player_position)
	if plant_seed_pressed:
		var player_position := global_position + facing_direction * 16
		seed_used.emit(player_position)
		print("seed planted")

	var wanted := ("walk_" if direction != Vector2.ZERO else "idle_") + _facing
	if _sprite.animation != wanted:
		_sprite.play(wanted)
