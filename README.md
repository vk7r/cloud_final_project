# Advanced Concepts in Cloud Computing - Final Poject

This project demonstrates the implementation of **Cloud Design Patterns** using a MySQL cluster on AWS EC2 instances. The solution integrates the **Proxy Pattern** and **Gatekeeper Pattern** to create a scalable, secure, and efficient database architecture.

The Proxy Pattern is employed to handle read and write operations efficiently across a distributed MySQL cluster. Three distinct implementations are provided: 
1. **Direct Hit**: Requests are directly routed to the manager node without distribution logic.
2. **Random**: Read requests are routed to a randomly selected worker node.
3. **Customized**: Requests are routed based on the response time of worker nodes for optimal performance.

The Gatekeeper Pattern adds an additional security layer by introducing an **internet-facing gatekeeper** and a **trusted host** to validate and route requests securely to the MySQL cluster.

The project also includes benchmarking with **sysbench** to measure the performance of the cluster and automation scripts for end-to-end deployment using AWS SDKs. This ensures the architecture is robust, secure, and easy to replicate.

## System Design:
![General System Design](final_proj_systemdesign.png "System Design")


## Instructions to Run the Code

1. **Configure AWS Credentials**  
   - Set up your AWS credentials on your local machine using the AWS CLI or environment variables.

2. **Edit the `globals.py` File**  
   - Open the `globals.py` file and fill in the constants with the appropriate relative paths required by your project.

3. **Insert AWS Credentials in the `elb_userdata.sh` File**  
   - Open the `elb_userdata.sh` script and insert your AWS credentials in the following format:

     ```bash
     aws_access_key_id=[INSERT]
     aws_secret_access_key=[INSERT]
     aws_session_token=[INSERT]
     ```

4. **Make the `run_all.sh` Script Executable**  
   - In the terminal, run the following command to give execution permissions to the `run_all.sh` script:

     ```bash
     chmod +x run_all.sh
     ```

5. **Run the Bash Script**  
   - After making the script executable, run it using the following command:

     ```bash
     ./run_all.sh
     ```

6. **Check the Benchmarking Results**  
   - Once the script has completed running, the results from sysbench and the benchmarking can be found in the folder `test_results/`. You can open this folder to review the performance data.
