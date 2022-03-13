import yaml
import sys

def main():

	if len(sys.argv) != 2:
		print("Missing argument: ", len(sys.argv), " found, 2 needed")
		exit(1)
		
	# Read the architecture file
	
	with open(sys.argv[1], "r") as archi_file:
	
		lines = archi_file.read()
		archi_file.close()

	archi = yaml.load(lines, Loader=yaml.FullLoader)
	
	# Write the docker-compose file
	
	with open("docker-compose.yml", "w") as f:
	
		f.write("version: \"3.3\"\n\n")
		f.write("services:\n\n")
		
		for i in range(archi["S"]):
			f.write(" server"+str(i)+":\n")
			f.write("  build: server\n")
			f.write("  container_name: server"+str(i)+"\n")
			if archi["Interactive"]: f.write("  network_mode: host\n")
			f.write("  environment:\n   - NUM_NODE="+str(i)+"\n   - RUST_BACKTRACE=1\n")
			f.write("   - OBJ_TRANSACTIONS="+str(archi["Obj_transactions"])+"\n\n")
		
		for i in range(archi["S"], archi["S"]+archi["B"]):
			f.write(" server"+str(i)+":\n")
			f.write("  build: byzantine\n")
			f.write("  container_name: server"+str(i)+"\n")
			if archi["Interactive"]: f.write("  network_mode: host\n")
			f.write("  environment:\n   - NUM_NODE="+str(i)+"\n   - RUST_BACKTRACE=1\n\n")
			
		for i in range(archi["C"]):
			f.write(" client"+str(i)+":\n")
			f.write("  build: client\n")
			f.write("  container_name: client"+str(i)+"\n")
			if archi["Interactive"]: f.write("  network_mode: host\n")
			f.write("  depends_on:\n")
			for j in range(archi["S"]):
				f.write("   - server"+str(j)+"\n")
			f.write("\n")
			
		f.close()

if __name__ == '__main__':
    main()