#!/usr/bin/env bash
set -euo pipefail

CHART_VERSION="88.5.4"
RELEASE_NAME="monitoring"
NAMESPACE="monitoring"
REPO_NAME="prometheus-community"
REPO_URL="https://prometheus-community.github.io/helm-charts"

echo "==> Adding/updating Prometheus Community Helm repository"
helm repo add "${REPO_NAME}" "${REPO_URL}" --force-update
helm repo update

echo "==> Installing/upgrading kube-prometheus-stack ${CHART_VERSION}"
helm upgrade --install "${RELEASE_NAME}" \
  "${REPO_NAME}/kube-prometheus-stack" \
  --version "${CHART_VERSION}" \
  --namespace "${NAMESPACE}" \
  --create-namespace \
  --values monitoring/values.yaml \
  --wait \
  --timeout 15m

echo
echo "==> Monitoring release status"
helm status "${RELEASE_NAME}" -n "${NAMESPACE}"

echo
echo "==> Monitoring pods"
kubectl get pods -n "${NAMESPACE}" -o wide
