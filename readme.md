System Overview
This assignment constitutes a sophisticated and adaptable system for the management and adaptation of complex applications, following the principles of the Monitor Analyze Plan Execute-Knowledge (MAPE-K) adaptation loop. The system encompasses well-structured code, diligent organization, and essential components that collaborate to ensure system responsiveness and resilience. Below is an overview of the directory structure and instructions on how to run the driver effectively.

Directory Structure
The directory is organized as follows:

configurations: Contains subdirectories for different services like acmeair-authservice, acmeair-bookingservice, acmeair-customerservice, and acmeair-flightservice. Each service directory includes configuration-related files, such as analyzer_utility.json and config_state.json. A master configration_states.json file is present for configuration state management.

logs: Holds log files, including analyzer.log, driver.log, and monitor.log, which are instrumental in tracking system events and performance.

metrics: Includes db_metrics.json and metrics.json files that define the metrics used in monitoring and adaptation processes.

output: Contains output data of monitoring step stored in CSV files, categorized by service. Examples include acmeair-authservice_output.csv and acmeair-mainservice_output.csv.

scripts: This directory is the operational hub of the system, housing key scripts:

analyzer.py: The script responsible for the Analysis and Planning phases of the MAPE-K loop.
driver.py: The driver program that initiates the adaptation code, ensuring regular monitoring and adaptation at 5-minute intervals.
executor.sh: A Bash script that is the Execution part, is used for updating resource requests and limits and scaling deployments. Ensure you update the login command with a valid token before using it. 
monitor.py: The monitor script for collecting metrics.

Running the Driver
To run the driver effectively, follow these steps:

Navigate to the scripts directory: cd scripts

Execute the driver program using Python 3: python3 driver.py. The driver program is responsible for initiating the adaptation code and ensures that the system undergoes consistent monitoring and adaptation at 5-minute intervals.

Before using executor.sh, update the login command with a valid token for secure interactions with the Kubernetes cluster.

By following these steps, you'll have the system up and running, efficiently managing and adapting your complex applications based on real-time metrics and feedback.

This project is a testament to the principles of adaptability, meticulous planning, and systematic execution in software systems management. It aligns with industry best practices and demonstrates a commitment to enhancing system stability and performance.
