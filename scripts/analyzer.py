#!/usr/bin/env python

import os
import datetime
import pandas as pd
import json
import subprocess

# Constants
SCRIPTS_FOLDER = "../scripts"
LOGS_FOLDER = "../logs"
UPDATE_DEPLOYMENT_SCRIPT = "../scripts/executer.sh"

# Path to the log file
log_file = "../logs/analyzer.log"

# Get the current date and time
current_time = datetime.datetime.now()

# Format the timestamp
timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")

# Open the log file in append mode and write the timestamp
with open(log_file, "a") as file:
    file.write(f"Script execution started at {timestamp}\n")


# Fetch values for parameters for different configurations from the JSON file
def get_configuration_values(config_key):
    # Define default values in case the configuration key is not found
    default_values = {
        "cpu_request": "",
        "cpu_limit": "",
        "memory_request": "",
        "memory_limit": "",
        "num_pods": 1
    }
    configuration_states_file = "../configurations/configration_states.json"
    # Load configuration data from the JSON file
    with open(configuration_states_file, "r") as file:
        configurations = json.load(file)

    # Get the configuration values for the specified key, or use default values
    config_data = configurations.get(config_key, default_values)

    cpu_request = config_data["cpu_request"]
    cpu_limit = config_data["cpu_limit"]
    memory_request = config_data["memory_request"]
    memory_limit = config_data["memory_limit"]
    num_pods = config_data["num_pods"]

    return cpu_request, cpu_limit, memory_request, memory_limit, num_pods


# Update the deployment
def update_deployment_resources(deployment, namespace, cpu_request, cpu_limit, memory_request, memory_limit, num_pods):
    # Call the shell script with arguments
    subprocess.call([UPDATE_DEPLOYMENT_SCRIPT, cpu_request, cpu_limit, memory_request, memory_limit, deployment, namespace, str(num_pods)])

# Using self-optimization
def calculate_utility(metric_values, utility_config):

    # Initialize utility variables for each criterion
    c1u = 0
    c2u = 0 
    c3u = 0 
    c4u = 0 
    c5u = 0 

    # Loop through each metric in the utility configuration
    for config in utility_config:
        metric_name = config["name"]
        weight = config["weight"]
        scaled_thresholds = config["scaled thresholds"]
        preferences = config["preferences"]
        metric_value = metric_values[metric_name]

        # Check where the metric value falls and update utility variables accordingly
        if metric_value > scaled_thresholds[2]:
            c1u = c1u + weight * preferences["very high"]["C1"]
            c2u = c2u + weight * preferences["very high"]["C2"]
            c3u = c3u + weight * preferences["very high"]["C3"]
            c4u = c4u + weight * preferences["very high"]["C4"]
            c5u = c5u + weight * preferences["very high"]["C5"]
        elif metric_value <= scaled_thresholds[2] and metric_value > scaled_thresholds[1]:
            c1u = c1u + weight * preferences["high"]["C1"]
            c2u = c2u + weight * preferences["high"]["C2"]
            c3u = c3u + weight * preferences["high"]["C3"]
            c4u = c4u + weight * preferences["high"]["C4"]
            c5u = c5u + weight * preferences["high"]["C5"]
        elif metric_value <= scaled_thresholds[1] and metric_value > scaled_thresholds[0]:
            c1u = c1u + weight * preferences["medium"]["C1"]
            c2u = c2u + weight * preferences["medium"]["C2"]
            c3u = c3u + weight * preferences["medium"]["C3"]
            c4u = c4u + weight * preferences["medium"]["C4"]
            c5u = c5u + weight * preferences["medium"]["C5"]
        else:
            c1u = c1u + weight * preferences["low"]["C1"]
            c2u = c2u + weight * preferences["low"]["C2"]
            c3u = c3u + weight * preferences["low"]["C3"]
            c4u = c4u + weight * preferences["low"]["C4"]
            c5u = c5u + weight * preferences["low"]["C5"]

    # Create a dictionary to store the calculated utilities for each criterion
    utility_dict = {
        "C1" : c1u,
        "C2" : c2u,
        "C3" : c3u,
        "C4" : c4u,
        "C5" : c5u
    }

    return utility_dict



def calculate_averages(dataframe, columns_to_average):
    averages = {}
    for column in columns_to_average:
        averages[column] = dataframe[column].mean()
    return averages

def handle_state_change(config_state, latest_config, config_state_path):
    current_config = config_state["current_config"]
    previous_config = config_state["previous_config"]
    data = {}

    # We do not update when the latest config to update is same as current confg
    # Also Below case handles when we want to wait for 1 cycle (5 mins) to update when the configs have just changed so that cluster can stablise
    if current_config == latest_config or current_config != previous_config:
        previous_config = current_config

        # Change so that in the next cycle we do not wait
        data["current_config"] = current_config
        data["previous_config"] = previous_config

        # Write the updated JSON back to the file
        with open(config_state_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        return False

    
    # Return True only when we want to update the deployment
    # We want to update the deployment when the latest config is different from current config AND the current config and previous config are same.
    # This approach allows us to wait for a cycle when the configs have just been updated.
    # Previous config is now current config and the current config is now latest config.
   
    data["current_config"] = latest_config
    data["previous_config"] = current_config

    # Write the updated JSON back to the file
    with open(config_state_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    return True


        

def main():
    configurations = {
        'C1': '1 Pod with limits: CPU 400m, Memory 300Mi, and requests: CPU 200m, Memory 200Mi.',
        'C2': '1 Pod with limits: CPU 600m, Memory 500Mi, and requests: CPU 400m, Memory 300Mi.',
        'C3': '1 Pod with limits: CPU 900m, Memory 700Mi, and requests: CPU 600m, Memory 500Mi.',
        'C4': '1 Pod with limits: CPU 1000m, Memory 900Mi, and requests: CPU 800m, Memory 800Mi.',
        'C5': '2 Pods with limits: CPU 1000m (each), Memory 900Mi (each), and requests: CPU 900m (each), Memory 800Mi (each).'
    }

    services = ["acmeair-authservice", "acmeair-customerservice", "acmeair-bookingservice", "acmeair-flightservice"]

    for service in services:

        dataset = "../output/" + service + "_output.csv"
        utility_config_path = "../configurations/" + service + "/analyzer_utility.json"
        config_state_path = "../configurations/" + service + "/config_state.json"

        # Read the CSV
        df = pd.read_csv(dataset)
        # Keep only the last 30 entries in df
        df = df.tail(30)

        # Load the JSON file
        try:
            with open(utility_config_path, 'r') as json_file:
                utility_config = json.load(json_file)
        except FileNotFoundError:
            print(f"File '{utility_config_path}' not found.")
            utility_config = {}

        # Load the JSON file
        try:
            with open(config_state_path, 'r') as json_file:
                config_state = json.load(json_file)
        except FileNotFoundError:
            print(f"File '{config_state_path}' not found.")
            config_state = {}

        # Extract all the metric names to analyze
        metrics = [item["name"] for item in utility_config]
    
        averages = calculate_averages(df, metrics)

        utility_dict = calculate_utility(averages, utility_config)

        # Picking the lowest possible configuration with highest utility value
        # Find the highest value
        max_value = max(utility_dict.values())

        # Filter keys with the highest value
        highest_value_keys = [key for key, value in utility_dict.items() if value == max_value]

        # Sort the filtered keys and get the lowest one
        lowest_key = min(highest_value_keys)
        
        to_update = handle_state_change(config_state, lowest_key, config_state_path)

        if to_update:
            # fetch the deployment update parameters
            cpu_request, cpu_limit, memory_request, memory_limit, num_pods = get_configuration_values(lowest_key)
            deployment = service
            namespace = "acmeair-g4"

            # update the deployment parameters
            update_deployment_resources(deployment, namespace, cpu_request, cpu_limit, memory_request, memory_limit, num_pods)

            print("\n\nAnalysis for Service: ", service)
            print("Utility dictionary is:")
            print(utility_dict)
            print("Choosing configuration: ", lowest_key)
            print("Set: ", configurations[lowest_key])

            # Open the log file in append mode and write the timestamp
            with open(log_file, "a") as file:
                file.write("-------------------------------------------------------\n")
                file.write("Analysis for Service: {}\n".format(service))
                file.write("Utility dictionary is:\n")
                for key, value in utility_dict.items():
                    file.write(f"{key}: {value}\n")

                file.write(f"Choosing configuration: {lowest_key}\n")
                file.write(f"Set: {configurations[lowest_key]}\n")

        else:
            print("\n\nAnalysis for Service: ", service)
            print("No update needed in this cycle.")

            # Open the log file in append mode and write the timestamp
            with open(log_file, "a") as file:
                file.write("-------------------------------------------------------\n")
                file.write("Analysis for Service: {}\n".format(service))
                file.write("No update needed in this cycle.\n")

            

    # Open the log file in append mode and write the timestamp
    with open(log_file, "a") as file:
        # Get the current date and time
        current_time = datetime.datetime.now()

        # Format the timestamp
        timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")

        file.write(f"Script execution ended at {timestamp}\n")


if __name__ == "__main__":
    main()
