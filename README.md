kubectl apply -f crd.yaml
kubectl get crd piholerecords.dns.sifft.io

# Maak een testobject
cat <<EOF | kubectl apply -f -
apiVersion: dns.sifft.io/v1alpha1
kind: PiholeRecord
metadata:
  name: testhost
  namespace: default
spec:
  hostname: testhost.lan
  ip: 10.10.10.99
EOF

kubectl get phr
kubectl describe phr testhost
