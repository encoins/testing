# Requirements
    - install docker
    - install pyyaml 'pip install pyyaml'
    - be in sudo mode
    - copy in 'server/' the binary of a working encoins-node code ('encoins-node/encoins/target/release/encoins')
    - copy in 'client/' the binary of a working cliENcoinS code ('cliENcoinS/target/release/CliENcoinS')
    These binaries are created when running 'cargo install --path .'

# Set up your test

## archi.yml
Here set up the architecture of your test: number and types of nodes, and an objective number of transactions to reach
Interactive mode if you want to play a client

## client/script
The script executed by each client,
The actual binary is made to do only one transfer by client (then he sleeps)

# Makefile commands
    
## To run a test
    - 'make (run)' runs your test
    - 'make attach' runs your test and print logfiles in shell
## During a test
    - 'make validated' to see the number of validated transfers in server0
    - 'make result' to see the time spent to validate the goal set, in ms
    - 'make sh' to enter server0
## When finished
    - 'make kill' if you feel there are too much containers running in background, after a test
    - 'make clean'
    - 'make prune' removes all build images/containers of your computer, radical, needs sometimes to reboot

# Create a performance graph

    - fill the hyperparameters of gen_graph.py
    - 'make figure'