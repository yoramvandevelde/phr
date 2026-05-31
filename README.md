# phr — Pi-hole DNS Operator for Kubernetes

A Kubernetes operator that manages Pi-hole local DNS records via custom resources.
Built with [kopf](https://kopf.readthedocs.io/) (Kubernetes Operator Pythonic Framework).

## How it works

The operator watches for `PiholeRecord` custom resources in your cluster. On create/delete
it calls the Pi-hole v6 REST API to add or remove local DNS entries.

```
kubectl apply PiholeRecord
       ↓
  K8s API server
       ↓ (watch event)
  phr-controller (Pod)
       ↓ (HTTP)
  Pi-hole API
```

## Requirements

- Kubernetes 1.24+
- Pi-hole v6 (REST API)
- `kubectl` access to your cluster

## Installation

### 1. Deploy the CRD

```bash
kubectl apply -f https://raw.githubusercontent.com/yoramvandevelde/phr/main/k8s/crd.yaml
```

### 2. Create the Pi-hole password secret

```bash
kubectl create secret generic phr-pihole \
  --from-literal=password=<your-pihole-password>
```

### 3. Deploy RBAC and controller

Edit `k8s/deployment.yaml` and set `PIHOLE_URL` to your Pi-hole address, then:

```bash
kubectl apply -f k8s/rbac.yaml
kubectl apply -f k8s/deployment.yaml
```

### 4. Verify

```bash
kubectl get pods -l app=phr-controller
kubectl logs -f deployment/phr-controller
```

## Usage

### Create a DNS record

```yaml
apiVersion: dns.sifft.io/v1alpha1
kind: PiholeRecord
metadata:
  name: myhost
  namespace: default
spec:
  hostname: myhost.lan
  ip: 10.10.10.50
```

```bash
kubectl apply -f record.yaml
kubectl get phr
```

### Delete a DNS record

```bash
kubectl delete phr myhost
```

The operator removes the record from Pi-hole before the object is deleted from k8s
(enforced via finalizer).

### List all records

```bash
kubectl get phr -A
```

## Development

### Local run (outside cluster)

```bash
uv sync
PIHOLE_URL=http://10.10.20.53 PIHOLE_PASSWORD=secret uv run kopf run controller.py --verbose
```

### Build and push image

```bash
git tag v0.1.x
git push origin v0.1.x
```

GitHub Actions builds and pushes to `ghcr.io/yoramvandevelde/phr:<tag>`.
