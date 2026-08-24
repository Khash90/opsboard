#!/usr/bin/env bash
set -euo pipefail

ARGO_HELM_REPO_NAME="argo"
ARGO_HELM_REPO_URL="https://argoproj.github.io/argo-helm"
ARGO_HELM_CHART="argo/argo-cd"
ARGO_HELM_CHART_VERSION="10.4.0"
ARGO_NAMESPACE="argocd"
ARGO_RELEASE_NAME="argocd"

helm repo add "${ARGO_HELM_REPO_NAME}" "${ARGO_HELM_REPO_URL}" --force-update
helm repo update

kubectl create namespace "${ARGO_NAMESPACE}" \
  --dry-run=client \
  -o yaml | kubectl apply -f -

helm upgrade --install "${ARGO_RELEASE_NAME}" "${ARGO_HELM_CHART}" \
  --version "${ARGO_HELM_CHART_VERSION}" \
  --namespace "${ARGO_NAMESPACE}" \
  -f argocd/values.yaml \
  --wait \
  --timeout 10m
