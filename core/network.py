# core/network.py
import os

def get_network_settings(use_proxy, use_tor):
    """Return proxy URL based on Tor or HTTP_PROXY environment settings."""

    if use_tor:
        if not os.environ.get("TOR_ENABLED"):
            raise RuntimeError("Tor requested but TOR_ENABLED not set.")
        return "socks5://127.0.0.1:9050"

    if use_proxy:
        proxy = os.environ.get("HTTP_PROXY")
        if not proxy:
            raise RuntimeError("Proxy requested but HTTP_PROXY not set.")
        return proxy

    return None
