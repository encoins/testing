import sys
import shutil
import os
import yaml

def main():
	
	if len(sys.argv) != 2:
		print("Missing argument: ", len(sys.argv), " found, 2 needed")
		exit(1)
		
	# Read the architecture file
	
	with open(sys.argv[1], "r") as archi_file:
	
		lines = archi_file.read()
		archi_file.close()

	archi = yaml.load(lines, Loader=yaml.FullLoader)

	# Other implicit hyperparameters

	port_init = 12345

	# Write net_config file in current dir
	
	with open("server/encoins-config/net_config.yml", "w") as f:
		
		f.write("parameters:\n")
		f.write(" nb_servers: "+str(archi["S"])+"\n")
		
		for i in range(archi["S"] + archi["B"]):
			f.write("server"+str(i)+":\n")
			if archi["Interactive"]: f.write(" address: localhost\n")
			else: f.write(" address: server"+str(i)+"\n")
			f.write(" port_server: "+str(port_init+(2*i))+"\n")
			f.write(" port_client: "+str(port_init+(2*i+1))+"\n\n")
		
		f.close()
	
	# Copy it in the server and client dir

	shutil.copy("server/encoins-config/net_config.yml", "client/")

if __name__ == '__main__':
    main()