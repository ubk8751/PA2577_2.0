#!/bin/bash
# Deletes all the K8 resources
deleteKubernetesResources() {
    read -p "This will attempt deleting ALL K8 resources [Y/N]: " mainmenuinput

    case $mainmenuinput in
        "y" | "Y")
            printf "Deleting all Kubernetes resources\n"
            objsToDrop=("services" "deployments" "configmaps")

            for obj in ${objsToDrop[@]}
            do
                printf "Deleting $obj \n"
                kubectl delete $obj --all 1> /dev/null
            done

            printf "Deleting PersistentVolumeClaims...\n"
            kubectl patch pvc postgres-pv-claim -p '{"metadata":{"finalizers":null}}' 1> /dev/null
            kubectl delete pvc postgres-pv-claim --grace-period=0 --force 1> /dev/null

            printf "Deleting PersistentVolumes...\n"
            kubectl patch pv postgres-pv-volume -p '{"metadata":{"finalizers":null}}' 1> /dev/null
            kubectl delete pv postgres-pv-volume --grace-period=0 --force 1> /dev/null

            printf "Done\n"
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
    printf "Deploying postgres...\n"
    kubectl apply -f kubernetes/postgres-deployment.yaml
    kubectl apply -f kubernetes/postgres-pvc-pv.yaml
    
    # Apply configmaps
    printf "Deploying configmaps...\n"
    kubectl apply -f kubernetes/configmaps.yaml

    # Read the database ip
    POSTGRES_IP=$(kubectl get service/postgres-service -o jsonpath='{.spec.clusterIP}')
    printf "Postgres deployed. Binding postgres ip ($POSTGRES_IP) to flask-api and flask-user-management ConfigMap\n"

    # Apply the database ip to the flask-api and flask-user-management configmaps
    kubectl get configmap flask-api-config -o yaml \
        | sed -r "s/NOTSET/$POSTGRES_IP/" | kubectl apply -f -
        
    kubectl get configmap flask-user-management-config -o yaml \
        | sed -r "s/NOTSET/$POSTGRES_IP/" | kubectl apply -f -


    # Deploy flask-api and load balancer
    printf "Deploying flask-api...\n"
    kubectl apply -f kubernetes/flask-api-deployment.yaml

    # Deploy flask-user-management and load balancer
    printf "Deploying flask-user-management...\n"
    kubectl apply -f kubernetes/flask-user-management-deployment.yaml

    # Read the api ip
    FLASK_API_IP=$(kubectl get service/flask-api-service -o jsonpath='{.spec.clusterIP}')
    FLASK_UM_IP=$(kubectl get service/flask-user-management-service -o jsonpath='{.spec.clusterIP}')
    printf "flask-api and flask-user-management deployed. Binding API ip ($FLASK_API_IP) and UM ip ($FLASK_UM_IP) to flask-ui ConfigMap\n"
    kubectl get configmaps/flask-ui-config -o yaml \
        | sed -r "s/APIHOST/$FLASK_API_IP/" \
        | sed -r "s/UMHOST/$FLASK_UM_IP/" | kubectl apply -f -

    # Deploy flask-api and flask-user-management
    printf "Deploying flask-ui...\n"
    kubectl apply -f kubernetes/flask-ui-deployment.yaml 
}

case $1 in
    "delete")
        deleteKubernetesResources
        ;;
    "deploy")
        deployKubernetesResources
        ;;
esac
