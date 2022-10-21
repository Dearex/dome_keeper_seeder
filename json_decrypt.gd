extends SceneTree

const SAVE_FILE_PASSWORD = "yaph!o0keu5iTei&"

# modify this variable to point to directories containing .scn files to convert
var directories = ["res://"]

var recursive = true # search through subdirectories for .scn files
var keep_originals = true # keep the original .scn files

func _init():
	for arg in OS.get_cmdline_args():
		if (arg == "-rm"):
			keep_originals = false
	
	for dir_path in directories:
		var dir = Directory.new()
		if (dir.open(dir_path) == OK):
			dir.list_dir_begin()
			var filename = dir.get_next()
			while (filename != ""):
				if (!dir.current_is_dir() && filename.split(".")[-1] == "json"):

					var metastate: = {}
					var save = File.new()
					var err = save.open_encrypted_with_pass(dir.get_current_dir() + "/" + filename, File.READ, SAVE_FILE_PASSWORD)
					if err == OK:
						var i = save.get_as_text()
						var parsed = JSON.parse(i)
						if parsed.result:
							metastate = parsed.result
					save.close()
					var file = File.new()
					file.open(dir.get_current_dir() + "/" + filename.left(filename.length() - 5) + "_decrypted.json", File.WRITE)
					file.store_line(to_json(metastate))
					file.close()
					print("saved " + dir.get_current_dir() + "/" + filename.left(filename.length() - 5) + "_decrypted.json")
					if (!keep_originals):
						dir.remove(dir.get_current_dir() + "/" + filename)
						print("Deleted: " + dir.get_current_dir() + "/" + filename)
				elif (dir.current_is_dir() && recursive && !(filename == "." || filename == "..")):
					directories.append(dir.get_current_dir() + "/" +filename)
				filename = dir.get_next()
	
	quit()


	

	
	print("Done Decrypting")