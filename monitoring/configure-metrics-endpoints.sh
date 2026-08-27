#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="/root/opsboard-monitoring-backups"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

echo "==> Creating backup directory: ${BACKUP_DIR}"
sudo mkdir -p "${BACKUP_DIR}"

echo "==> Backing up control-plane manifests"
sudo cp /etc/kubernetes/manifests/kube-controller-manager.yaml \
  "${BACKUP_DIR}/kube-controller-manager.yaml.${TIMESTAMP}"

sudo cp /etc/kubernetes/manifests/kube-scheduler.yaml \
  "${BACKUP_DIR}/kube-scheduler.yaml.${TIMESTAMP}"

sudo cp /etc/kubernetes/manifests/etcd.yaml \
  "${BACKUP_DIR}/etcd.yaml.${TIMESTAMP}"

echo "==> Exposing kube-controller-manager metrics on port 10257"
sudo sed -i \
  's/--bind-address=127\.0\.0\.1/--bind-address=0.0.0.0/' \
  /etc/kubernetes/manifests/kube-controller-manager.yaml

echo "==> Exposing kube-scheduler metrics on port 10259"
sudo sed -i \
  's/--bind-address=127\.0\.0\.1/--bind-address=0.0.0.0/' \
  /etc/kubernetes/manifests/kube-scheduler.yaml

echo "==> Exposing etcd metrics on port 2381"
sudo sed -i \
  's#--listen-metrics-urls=http://127\.0\.0\.1:2381#--listen-metrics-urls=http://0.0.0.0:2381#' \
  /etc/kubernetes/manifests/etcd.yaml

echo "==> Backing up kube-proxy ConfigMap"
kubectl -n kube-system get configmap kube-proxy -o yaml \
  > "${BACKUP_DIR}/kube-proxy-configmap.${TIMESTAMP}.yaml"

echo "==> Configuring kube-proxy metrics on port 10249"
kubectl -n kube-system get configmap kube-proxy -o yaml \
  | sed 's/metricsBindAddress: ""/metricsBindAddress: "0.0.0.0:10249"/' \
  | kubectl apply -f -

echo "==> Restarting kube-proxy DaemonSet"
kubectl -n kube-system rollout restart daemonset kube-proxy
kubectl -n kube-system rollout status daemonset kube-proxy --timeout=2m

echo
echo "Metrics endpoints configured."
echo "Backups stored in: ${BACKUP_DIR}"
