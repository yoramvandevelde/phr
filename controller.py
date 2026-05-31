import kopf
import httpx
import os
from kubernetes import client, config


PIHOLE = os.environ.get("PIHOLE_URL", "http://10.10.20.53")
PASSWORD = os.environ.get("PIHOLE_PASSWORD", "")

@kopf.on.login()
def login_fn(**kwargs):
    return kopf.login_via_service_account(**kwargs)

@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, **kwargs):
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()


def pihole_auth() -> str:
    r = httpx.post(f"{PIHOLE}/api/auth", json={"password": PASSWORD})
    return r.json()["session"]["sid"]


@kopf.on.create('dns.sifft.io', 'v1alpha1', 'piholerecords')
def create_record(spec, name, logger, **kwargs):
    ip = spec['ip']
    hostname = spec['hostname']
    logger.info(f"Creating DNS record: {ip} -> {hostname}")
    sid = pihole_auth()
    r = httpx.put(
        f"{PIHOLE}/api/config/dns/hosts/{ip}%20{hostname}",
        headers={"sid": sid}
    )
    logger.info(f"Pi-hole response: {r.status_code}")
    return {"synced": True}


@kopf.on.delete('dns.sifft.io', 'v1alpha1', 'piholerecords')
def delete_record(spec, name, logger, **kwargs):
    ip = spec['ip']
    hostname = spec['hostname']
    logger.info(f"Deleting DNS record: {ip} -> {hostname}")
    sid = pihole_auth()
    r = httpx.delete(
        f"{PIHOLE}/api/config/dns/hosts/{ip}%20{hostname}",
        headers={"sid": sid}
    )
    logger.info(f"Pi-hole response: {r.status_code}")
