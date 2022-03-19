import os.path
import shutil
import subprocess
from os import listdir
from os.path import join, isfile

cliencoins_path = "client"
server_path = "server"
byzantine_path = "byzantine"
encoins_config_path = server_path + "/encoins-config/"
test_results_path = "tests"
wallets_dir = test_results_path + "/wallets"
current_servers = list()


def gen_network_cfg(correct_servers_nb, byzantine_servers_nb):
    total_nb_servers = correct_servers_nb + byzantine_servers_nb
    net_config_path = encoins_config_path + "net_config.yml"
    start_port = 12345
    with open(net_config_path, "w") as f:
        f.write("parameters:\n")
        f.write(" nb_servers: " + str(total_nb_servers) + "\n")

        for i in range(total_nb_servers):
            f.write("server" + str(i) + ":\n")
            f.write(" address: localhost\n")
            f.write(" port_server: " + str(start_port + (2 * i)) + "\n")
            f.write(" port_client: " + str(start_port + (2 * i + 1)) + "\n\n")

        f.close()

    # Copy it in the server and client dir

    shutil.copy(net_config_path, "client/")


def gen_dirs(correct_servers_nb, byzantine_servers_nb, max_transactions_nb, variable_servers,
             variable_transactions):
    if not os.path.exists(test_results_path):
        os.mkdir(test_results_path)

    if not os.path.exists(wallets_dir):
        os.mkdir(wallets_dir)

    partial_dir_path = test_results_path + "/" + str(correct_servers_nb)

    if variable_servers:
        partial_dir_path += "var"

    partial_dir_path += "cor_" + str(byzantine_servers_nb) + "byz_" + str(max_transactions_nb)

    if variable_transactions:
        partial_dir_path += "var"

    partial_dir_path += "tr"
    nb_tested = 0
    dir_path = partial_dir_path
    while os.path.exists(dir_path):
        nb_tested += 1
        dir_path = partial_dir_path + "_" + str(nb_tested)

    os.mkdir(dir_path)
    return dir_path


def gen_and_load_wallets(nb_wallets):
    # First check number of existing wallets
    current_nb_wallets = 0
    partial_wallet_path = "wallet_"
    wallet_path = partial_wallet_path + str(current_nb_wallets)
    while os.path.exists(wallet_path):
        current_nb_wallets += 1
        wallet_path = partial_wallet_path + str(current_nb_wallets)

    # Create new wallets if necessary
    if current_nb_wallets < nb_wallets:
        wallet_to_gen = nb_wallets - current_nb_wallets
        gen_path = wallets_dir + "/wallet_gen.txt"
        if os.path.exists(gen_path):
            f = open(gen_path, 'w')
        else:
            f = open(gen_path, 'x')

        for i in range(wallet_to_gen):
            f.write("genwallet " + wallets_dir + "/wallet_" + str(current_nb_wallets + i) + "\n")
        f.write("quit\n")
        f.close()

        log_path = wallets_dir + "/wallets_gen_logs.txt"
        command = cliencoins_path + "/./cliencoins false < " + gen_path + ">" + log_path
        os.system(command)

    # Load all wallets into an array of public keys
    pk_array = []
    for i in range(nb_wallets):
        wallet_path = wallets_dir + "/" + partial_wallet_path + str(i) + ".wallet"
        f_wal = open(wallet_path, 'r')
        pk = f_wal.readline().replace("\n", "")
        pk_array.append(pk)
        f_wal.close()

    return pk_array


def launch_servers(correct_servers_nb, byzantine_servers_nb):
    gen_network_cfg(correct_servers_nb, byzantine_servers_nb)

    for i in range(correct_servers_nb):
        command = [server_path + "/./encoins", str(i)]
        print(command)
        current_servers.append(subprocess.Popen(command, stdout=subprocess.DEVNULL))

    for i in range(byzantine_servers_nb):
        command = "NUM_NODE=" + str(i + correct_servers_nb), server_path, "/./encoins"
        print(command)
        current_servers.append(subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL))


def scrap_logs(test_dir_path):
    server_logs_path = test_dir_path + "/servers_logs"
    os.mkdir(server_logs_path)
    partial_server_files_path = server_path + "/files"
    current_serv = 0
    s_f_p = partial_server_files_path + str(current_serv) + "/logs"
    while os.path.exists(s_f_p):
        logfiles = [f for f in listdir(s_f_p) if isfile(join(s_f_p, f))]
        logfile = s_f_p + "/"+logfiles[0]
        new_path = server_logs_path + '/server_' + str(current_serv) + ".txt"
        command = "mv " + logfile + " " + new_path
        os.system(command)
        current_serv += 1
        s_f_p = partial_server_files_path + str(current_serv) + "/logs"


def delete_servers():
    for serv in current_servers:
        serv.kill()
        current_servers.remove(serv)

    partial_server_files_path = server_path+"/files"
    current_file = 0
    s_f_p = partial_server_files_path+str(current_file)
    while os.path.exists(s_f_p):
        command = "rm -r "+s_f_p
        os.system(command)
        current_file+=1
        s_f_p = partial_server_files_path + str(current_file)


def make_test(correct_servers_nb, byzantine_servers_nb, transactions_nb, pk_array, test_folder_path):
    testfile_path = test_folder_path + "/" + str(correct_servers_nb) + "cor_" + \
                    str(byzantine_servers_nb) + "byz_" + str(transactions_nb) + "tr.txt"

    launch_servers(correct_servers_nb, byzantine_servers_nb)

    f = open(testfile_path, 'x')
    for i in range(transactions_nb):
        wallet_path = wallets_dir + "/wallet_" + str(i) + ".wallet"
        f.write("ldwallet " + wallet_path + "\n")
        f.write("transfer " + pk_array[i] + " 0\n")

    f.write("quit\n")
    f.close()

    logs_path = test_folder_path + "/client_logs.txt"

    command = cliencoins_path + "/./cliencoins false < " + testfile_path + " > " + logs_path
    os.system(command)

    scrap_logs(test_folder_path)
    delete_servers()


def make_tests(correct_servers_nb, byzantine_servers_nb, transactions_nb, variable_servers,
               variable_transactions):
    # Generate test_folder
    test_folder_path = gen_dirs(correct_servers_nb, byzantine_servers_nb, transactions_nb, variable_servers,
                                variable_transactions)

    # Generate and load pk array for the tests
    pk_array = gen_and_load_wallets(transactions_nb)

    if variable_transactions:
        start_transaction = 0
    else:
        start_transaction = transactions_nb

    if variable_servers:
        start_server = max(3, byzantine_servers_nb)
    else:
        start_server = correct_servers_nb

    for correct_servers in range(start_server, correct_servers_nb + 1):

        total_nb_servers = correct_servers + byzantine_servers_nb
        current_test_folder_path = test_folder_path + "/" + str(correct_servers) + "_" + str(byzantine_servers_nb)
        os.mkdir(current_test_folder_path)

        for tr_nb in range(start_transaction, transactions_nb + 1):
            tr_test_folder_path = current_test_folder_path + "/" + str(tr_nb) + "tr"
            os.mkdir(tr_test_folder_path)

            # generate the testfile
            make_test(correct_servers_nb, byzantine_servers_nb, transactions_nb, pk_array, tr_test_folder_path)


make_tests(10, 0, 1, False, False)

