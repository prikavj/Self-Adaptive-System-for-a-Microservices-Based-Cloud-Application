#!/bin/bash

# Parse arguments
CPU_REQUEST=$1
CPU_LIMIT=$2
MEMORY_REQUEST=$3
MEMORY_LIMIT=$4
DEPLOYMENT=$5
NAMESPACE=$6
NUM_PODS=$7

oc login --token=sha256~D0GVQacKjvtWhQdAv3ze3x_JmqCEAR9TaX992acMYn8 --server=https://c104-e.ca-tor.containers.cloud.ibm.com:31635
oc project $NAMESPACE
echo "Updating resources for deployment: $DEPLOYMENT"

# Update CPU and memory requests and limits
oc set resources deployment $DEPLOYMENT --requests=cpu=$CPU_REQUEST,memory=$MEMORY_REQUEST --limits=cpu=$CPU_LIMIT,memory=$MEMORY_LIMIT

# Scale the deployment to the desired number of pods
oc scale --replicas=$NUM_PODS deployment/$DEPLOYMENT

echo "Resource update complete for deployment: $DEPLOYMENT"

