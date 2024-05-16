# DLT_Experiments
This goal of this project was to learn about different Distributed Ledger Technogolies through experimentation. Docker was used to simulate different computers locally, and the flask package was used to allow the nodes to interact with each other. 

The three different types of DLTs which were experimented on was:
- A blockchain with a proof of work consensus algorithm
- An interpretation of IOTA's Tangle implementation, using DAG principles as well as a modified proof of stake consensus algorithm.
- An interpretation of the Hashgraph implementation, using Byzantine fault tolerance consensus algorithm.

### Required software and packages
- Docker: Go to https://www.docker.com/get-started/ to learn about docker and how to download it
- Python Packages: You can install all the python packages required for this project with the command:
``` pip install -r requirements.txt ```

### Installation
1. Clone this repository to your local machine:
```git clone https://github.com/Turlagh/DLT_Experiments.git ```
2. Open up your bash shell and set the working directory to the github repo
``` cd "path/to/the/repo"```
3. Build the docker containers:
``` docker-compose build ```

Now you can start the docker containers at any time with ``` docker-compose up ``` and close them at anytime with ``` docker-compose down ```

Once running, you can navigate to the file DLT_Tutorial.ipynb to start experimenting with interacting with the DLT system.
