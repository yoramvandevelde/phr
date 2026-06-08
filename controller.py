import kopf
import httpx
import os
from kubernetes import client, config


PIHOLE = os.environ.get("PIHOLE_URL", "http://10.10.20.53")
PASSWORD = os.environ.get("PIHOLE_PASSWORD", "")


@kopf.on.login()
def login_fn(**kwargs):
    return kopf.login_with_service_account(**kwargs)


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


@kopf.on.update('dns.sifft.io', 'v1alpha1', 'piholerecords')
def update_record(spec, old, new, logger, **kwargs):
    old_spec = old.get('spec', {})
    new_spec = new.get('spec', {})

    old_ip = old_spec.get('ip')
    old_hostname = old_spec.get('hostname')
    new_ip = new_spec.get('ip')
    new_hostname = new_spec.get('hostname')

    if old_ip == new_ip and old_hostname == new_hostname:
        return  

    sid = pihole_auth()

    if old_ip and old_hostname:
        logger.info(f"Removing old record: {old_ip} -> {old_hostname}")
        httpx.delete(
            f"{PIHOLE}/api/config/dns/hosts/{old_ip}%20{old_hostname}",
            headers={"sid": sid}
        )

    logger.info(f"Creating new record: {new_ip} -> {new_hostname}")
    httpx.put(
        f"{PIHOLE}/api/config/dns/hosts/{new_ip}%20{new_hostname}",
        headers={"sid": sid}
    )

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
