extends Node2D

@onready var ground_top: TileMapLayer = $GroundTop
@onready var tilled_soil: TileMapLayer = $TilledSoil
@onready var crops: TileMapLayer = $Crops
var crop_stages: Dictionary = {}

func _on_player_tool_used(target_position: Vector2) -> void:
	var local_position := tilled_soil.to_local(target_position)
	var map_position := tilled_soil.local_to_map(local_position)
	var ground_tile_data := ground_top.get_cell_tile_data(map_position)

	if ground_tile_data == null:
		return

	var is_farmable: bool = ground_tile_data.get_custom_data("farmable")
	if not is_farmable:
		return

	tilled_soil.set_cell(map_position, 0, Vector2i(6, 15))


func _on_player_seed_used(target_position: Vector2) -> void:
	var local_position := crops.to_local(target_position) #Convert the global target position into pixel coordinates local to the Crops layer.
	var map_position := crops.local_to_map(local_position) #Convert local pixel coordinates into a grid-cell coordinate.
	var has_tilled_soil := tilled_soil.get_cell_source_id(map_position) != -1 #Check whether TilledSoil contains any tile at this cell. -1 means empty; != -1 converts that result into a Boolean.
	var has_crop := crops.get_cell_source_id(map_position) != -1 #Check whether Crops already contains a tile at this cell.
	
	if not has_tilled_soil: #if no tilled soil found then stop
		return
	if has_crop: #if the tilled soil has a crop already then stop
		return
		
	crops.set_cell(map_position, 2, Vector2i(0, 1)) #Place the first carrot growth stage
	crop_stages[map_position] = 0
	print(crop_stages)

func _on_crop_growth_timer_timeout() -> void:
	for map_position in crop_stages:
		var current_stage: int = crop_stages[map_position]
		if current_stage >= 4:
			continue
		current_stage += 1
		crop_stages[map_position] = current_stage
		print(map_position, current_stage)
		crops.set_cell(map_position, 2, Vector2i(current_stage, 1))
