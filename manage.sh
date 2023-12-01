#!/bin/bash

# COLORS
BLACK='\033[0;30m'
RED='\033[0;31m'
GREEN='\033[0;32m'
ORANGE='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m'    # no color

# Deletes all the K8 resources
deleteKubernetesResources() {
    read -p "This will attempt deleting ALL K8 resources [Y/N]: " mainmenuinput

    case $mainmenuinput in
        "y" | "Y")
            printf "${GREEN}Deleting all Kubernetes resources${NC}\n"
            objsToDrop=("services" "deployments" "configmaps")

            for obj in ${objsToDrop[@]}
            do
                printf "${ORANGE}Deleting $obj ${NC}\n"
                kubectl delete $obj --all 1> /dev/null
            done

            printf "${CYAN}Deleting PersistentVolumeClaims...${NC}\n"
            kubectl patch pvc postgres-pv-claim -p '{"metadata":{"finalizers":null}}' 1> /dev/null
            kubectl delete pvc postgres-pv-claim --grace-period=0 --force 1> /dev/null

            printf "${CYAN}Deleting PersistentVolumes...${NC}\n"
            kubectl patch pv postgres-pv-volume -p '{"metadata":{"finalizers":null}}' 1> /dev/null
            kubectl delete pv postgres-pv-volume --grace-period=0 --force 1> /dev/null

            printf "${GREEN}Done${NC}\n"
            ;;
        *)
            printf "Exiting\n"
            ;;
    esac
}

# Deploys all the K8 resources
deployKubernetesResources() 
{
    # Set up postgres first and foremost
    printf "${BLUE}Deploying postgres...${NC}\n"
    kubectl apply -f kubernetes/postgres-deployment.yaml
    kubectl apply -f kubernetes/postgres-pvc-pv.yaml
    
    # Apply configmaps
    printf "${BLUE}Deploying configmaps...${NC}\n"
    kubectl apply -f kubernetes/configmaps.yaml

    # Read the database ip
    POSTGRES_IP=$(kubectl get service/postgres-service -o jsonpath='{.spec.clusterIP}')
    printf "${BLUE}Postgres deployed. Binding postgres ip ($POSTGRES_IP) to flask-api and flask-user-management ConfigMap${NC}\n"

    # Apply the database ip to the flask-api and flask-user-management configmaps
    kubectl get configmap flask-api-config -o yaml \
        | sed -r "s/NOTSET/$POSTGRES_IP/" | kubectl apply -f -
        
    kubectl get configmap flask-user-management-config -o yaml \
        | sed -r "s/NOTSET/$POSTGRES_IP/" | kubectl apply -f -


    # Deploy flask-api and load balancer
    printf "${BLUE}Deploying flask-api...${NC}\n"
    kubectl apply -f kubernetes/flask-api-deployment.yaml

    # Deploy flask-user-management and load balancer
    printf "${BLUE}Deploying flask-user-management...${NC}\n"
    kubectl apply -f kubernetes/flask-user-management-deployment.yaml

    # Read the api ip
    FLASK_API_IP=$(kubectl get service/flask-api-service -o jsonpath='{.spec.clusterIP}')
    FLASK_UM_IP=$(kubectl get service/flask-user-management-service -o jsonpath='{.spec.clusterIP}')
    printf "${BLUE}flask-api and flask-user-management deployed. Binding API ip ($FLASK_API_IP) and UM ip ($FLASK_UM_IP) to flask-ui ConfigMap${NC}\n"
    kubectl get configmaps/flask-ui-config -o yaml \
        | sed -r "s/APIHOST/$FLASK_API_IP/" \
        | sed -r "s/UMHOST/$FLASK_UM_IP/" | kubectl apply -f -

    # Deploy flask-api and flask-user-management
    printf "${BLUE}Deploying flask-ui...${NC}\n"
    kubectl apply -f kubernetes/flask-ui-deployment.yaml 
}
# A short function that checks the second argument when invoked with "deploy"
# to see if we want forward the services with minikube or kubectl, or not at all
deployWith() 
{
    case $2 in
        "backend" | "b")
            service="flask-api-service"
            ports="5002:5002"
            ;;
        "user-management" | "u")
            service="flask-user-management-service"
            ports="5001:5001"
            ;;
        *)
            service="flask-ui-service"
            ports="5000:5000"
            ;;
            
    esac

    case $1 in
        "minikube" | "mk")
            if command -v minikube &> /dev/null
            then 
                printf "${BLUE}Found minikube installation, forwarding ${service} with minikube url connection${NC}\n"
                minikube service ${service} --url
            else
                printf "${RED}Could not find command \"minikube\"${NC}\n"
            fi
            ;;
        "kubectl" | "k")
            printf "${CYAN}Forwarding ${service} with kubectl...\n${ORANGE}"
            kubectl port-forward service/$service $ports
            printf "${NC}"
            ;;
    esac
}

usage() 
{
    printf "Usage:\n"
    printf "  delete - Deletes all Kubernetes resources\n"
    printf "  deploy - Deploys all Kubernetes resources\n"
    printf "  forward <service> - Forwards the specified service\n"
}

#############################
#### PROGRAM STARTS HERE ####
#############################

if [[ $# -eq 0 ]] 
then
    usage
    exit 0
fi

case $1 in
    "delete")
        deleteKubernetesResources
        ;;
    "deploy")
        deployKubernetesResources
        ;;
    "forward")
        deployWith $2 $3
        ;;
    "db" | "database")
        database $2
        ;;
    *)
        usage
        ;;
esac
