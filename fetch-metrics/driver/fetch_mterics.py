#!/usr/bin/env python

# Import necessary libraries
import sys
import csv
import time
from sdcclient import IbmAuthHelper, SdMonitorClient
import json


# Constants

# Add the monitoring instance information that is required for authentication
URL = "https://ca-tor.monitoring.cloud.ibm.com"
APIKEY = "0ly9p7sGhp6-R4yPo2IEFsiZgFricb8cRpSCKuzt6OLS"
GUID = "b92c514a-ca21-4548-b3f0-4d6391bab407"
ibm_headers = IbmAuthHelper.get_headers(URL, APIKEY, GUID)

# Instantiate the Python client
sdclient = SdMonitorClient(sdc_url=URL, custom_headers=ibm_headers)

# Define the Kubernetes namespace you want to monitor
kube_namespace = "acmeair-g4"
kube_cluster_name = "ece750cluster"



# Function to fetch and save metrics
def fetch_and_save_metrics(metrics, coulumn_names, service_names, hours):

    # Iterate over each item in kube_pods_list
    for service_name in service_names:
        #
        # Prepare the filter
        #

        filter = "kubernetes.cluster.name='%s' and kubernetes.namespace.name='%s' and kubernetes.workload.name='%s' and kubernetes.pod.name='%s'" % (kube_cluster_name, kube_namespace, service_name, service_name_pod_name)

        all_data = []

        ok, res = sdclient.get_data(metrics=metrics,  # List of metrics to query
                                        start_ts= -300,
                                        end_ts= 0,
                                        sampling_s=10,  # 1 data point per 10 seconds
                                        filter=filter,  # The filter specifying the target host
                                        datasource_type='container')  # The source for our metrics is the container


        if not ok:
                print("Error")
                print(res)
                sys.exit(1)

        # Specify the name of the CSV file
        csv_file = service_name + "_output.csv"
        csv_file_location = "output/" + csv_file
        to_write_column = True
        is_file_not_exists = False
        if not os.path.exists(csv_file_location):
            is_file_not_exists = True

        # Write data to CSV
        with open(csv_file_location, mode='a', newline='') as file:
            writer = csv.writer(file)
            
            # Write the header row
            if to_write_column and is_file_not_exists:
                writer.writerow(coulumn_names)
                to_write_column = False
            
            # Write the data rows
            for data in res:
                data_rows = data['data']
                for entry in data_rows:
                    timestamp = entry['t']
                    values = entry['d']
                    row = values + [timestamp]  # Combine values and timestamp in one row
                    writer.writerow(row)
      
        print(f"Data has been saved to {csv_file}")


def main():

    if len(sys.argv) != 2:
        print("Usage: python script_name.py <number_of_hours>. Where <number_of_hours> is the desired time span, counting backward from the present, for retrieving metrics.")
        sys.exit(1)

    try:
        # Get the number of hours from the command-line argument
        hours = float(sys.argv[1])


        service_names = [ "acmeair-authservice",  "acmeair-bookingservice", "acmeair-customerservice", "acmeair-flightservice", "acmeair-mainservice"]
        db_service_names = [ "acmeair-booking-db", "acmeair-customer-db", "acmeair-flight-db"]


        # Initialize an empty dictionary
        data_dict = {}

        # Read the JSON file and store its contents in the dictionary
        with open("metrics/metrics.json", "r") as json_file:
            data_dict = json.load(json_file)


        # Initialize an empty dictionary
        db_data_dict = {}

        # Read the JSON file and store its contents in the dictionary
        with open("metrics/db_metrics.json", "r") as json_file:
            db_data_dict = json.load(json_file)

        
        # Fetch and save metrics for Kubernetes pods
        fetch_and_save_metrics(data_dict["metrics"], data_dict["column_display_name"], service_names, hours)

        # Fetch and save metrics for Kubernetes DB pods
        fetch_and_save_metrics(db_data_dict["metrics"], db_data_dict["column_display_name"], db_service_names, hours)

    except ValueError:
        print("Invalid input. Please enter a valid number of hours.")
        sys.exit(1)

if __name__ == "__main__":
    main()