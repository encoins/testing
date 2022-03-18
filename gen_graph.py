import os
import subprocess
import time
import numpy as np
import matplotlib.pyplot as plt

def main():

    #Hyperparameters
    obj_min = 1 #min 1
    obj_max = 100
    servers_min = 10 #min 3
    servers_max = 11
    transactions_per_client = 1

    time_reload = 0.5
    time_end = 1

    DIR_FIG = "figures/"
    formatting = 'r-'
    resolution_fig = 500
    x_label_step = 10

    #Initializing graph arrays
    if obj_max-obj_min <= 1:
        if servers_max-servers_min <= 1:
            print("Error : bad hyperparameters")
            exit(1)
        else:
            graph_type = 1
    else :
        if servers_max-servers_min > 1:
            print("Error : bad hyperparameters")
            exit(1)
        graph_type = 0
    
    if graph_type == 0:
        X = np.arange(obj_min, obj_max)
        Y = [np.empty(obj_max-obj_min) for i in range(servers_min)]
    if graph_type == 1:
        X = np.arange(servers_min, servers_max)
        Y = np.empty(servers_max-servers_min)

    #Main loop
    os.system("docker kill $(docker ps -q)")
    
    for servers in range(servers_min, servers_max):
        for obj in range(obj_min, obj_max):
            simulation(servers, obj, transactions_per_client, servers_min, servers_max, obj_min, obj_max, Y, graph_type, time_reload, time_end)

    os.system("clear")
    print("TEST over !")

    #Building graph

    if graph_type == 0:
        plt.xticks(np.arange(0, obj_max, x_label_step))
        plt.xlabel("Simultaneous transactions validated (number)")
        for proc in range(servers_min):
            plt.plot(X, Y[proc])

    if graph_type == 1:
        plt.xticks(np.arange(0, servers_max, x_label_step))
        plt.xlabel("Servers used (number)")
        plt.plot(X, Y, formatting)

    plt.ylabel("Time taken (seconds)")

    print("Saving figure...")

    #Saving the figure
    if not os.path.exists(DIR_FIG):
        os.makedirs(DIR_FIG)
    fig_name = "serv["+str(servers_min)+"-"+str(servers_max-1)+"]_obj["+str(obj_min)+"-"+str(obj_max-1)+"].png"
    plt.savefig(DIR_FIG+fig_name, dpi=resolution_fig)



def simulation(servers, obj, transactions_per_client, servers_min, servers_max, obj_min, obj_max, Y, graph_type, time_reload, time_end):

    cmd1 = "docker exec -ti server0 cat validated.txt"

    #Writing archi.yml
    with open("archi.yml", "w") as f:
    
        f.write("# Number of correct servers in your test\nS: ")
        f.write(str(servers))
        f.write("\n\n# Number of byzantine servers in your test\nB: ")
        f.write("0")
        f.write("\n\n# Number of clients in your test\nC: ")
        f.write(str(obj))
        f.write("\n\n# Interactive mode allows to communicate yourself with the servers, it should be a bit slower\nInteractive: ")
        f.write("true")
        f.write("\n\n# Number of validated transactions to reach before simulation ends (0 means no end)\nObj_transactions: ")
        f.write(str(obj*transactions_per_client))
        
        f.close()
    
    #Running simulation
    os.system("make")

    #Running checker
    validated = 0
    
    while validated < obj:
        time.sleep(time_reload)
        p = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)    
        while True:
            line = p.stdout.readline()
            try:
                validated = int(line)
            except:
                break
        os.system("clear")
        print("TEST: objective of transactions ["+str(obj)+"/"+str(obj_max-1)+"] "+str(int(100*validated/obj))+"%")
        print("                        servers ["+str(servers)+"/"+str(servers_max-1)+"]")
    
    #Saving results
    
    time.sleep(time_end)

    if graph_type == 0:
        for proc in range(servers):
            cmd2 = "docker exec -ti server"+str(proc)+" cat result.txt"
            p = subprocess.Popen(cmd2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            try :
            	Y[proc][obj-obj_min] = float(p.stdout.readline())/1000
            except:
            	Y[proc][obj-obj_min] = 0

    if graph_type == 1:
        cmd2 = "docker exec -ti server0 cat result.txt"
        p = subprocess.Popen(cmd2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        Y[servers-servers_min] = float(p.stdout.readline())/1000
    
    #Stopping simulation
    os.system("docker kill $(docker ps -q)")



if __name__ == '__main__':
    main()
