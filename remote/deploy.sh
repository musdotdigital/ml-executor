#!/bin/bash

# Deploy Redis
kubectl apply -f redis-deployment.yaml
kubectl apply -f redis-service.yaml

# Deploy Worker
kubectl apply -f worker-deployment.yaml
kubectl apply -f worker-service.yaml

# Deploy Web
kubectl apply -f web-deployment.yaml
kubectl apply -f web-service.yaml
