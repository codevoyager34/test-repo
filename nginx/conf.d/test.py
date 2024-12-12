#!/usr/bin/env python3
import hvac
import logging
import os
import time
from urllib.parse import urlparse
from threading import Lock
import socket

# Configure logging
LOG = logging.getLogger("vault_helper")
LOG.setLevel(logging.INFO)

if not LOG.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    LOG.addHandler(handler)

class VaultManager:
    """Manages connections to Vault servers with TTL caching."""

    def __init__(self):
        self.connections = {}  # {vault_addr: {"client": client_instance, "ttl": expiry_time}}
        self.lock = Lock()  # To ensure thread-safe operations

    def get_connection(self, vault_addr, ttl_seconds=300, cert_pem=None, key_pem=None):
        """Retrieve or create a Vault client connection."""
        current_time = time.time()
        with self.lock:  # Ensure thread safety
            if vault_addr in self.connections:
                connection = self.connections[vault_addr]
                if current_time < connection["ttl"]:  # Check if TTL is valid
                    return connection["client"]

            # Create a new client connection
            client = self._initialize_vault_client(vault_addr, cert_pem, key_pem)
            self.connections[vault_addr] = {
                "client": client,
                "ttl": current_time + ttl_seconds
            }
            return client

    def _initialize_vault_client(self, vault_addr, cert_pem, key_pem):
        """Initialize a Vault client for the given address."""
        try:
            # Ensure the Vault address includes the scheme
            if not vault_addr.startswith("http://") and not vault_addr.startswith("https://"):
                vault_addr = f"https://{vault_addr}"

            # Ensure the port is included
            if ':' not in vault_addr.split('//')[-1]:  # Check if port is missing after the host
                vault_addr += ":8200"

            LOG.info(f"Connecting to Vault at {vault_addr}")
            client = hvac.Client(url=vault_addr)
            client.auth.cert.login(cert_pem=cert_pem, key_pem=key_pem)
            LOG.info("Vault client created successfully.")
            return client
        except Exception as ex:
            LOG.error(f"Failed to create Vault client: {ex}", exc_info=True)
            raise

class VaultHelper:
    """VaultHelper for managing interactions with Vault using VaultManager."""

    def __init__(self):
        self.vault_manager = VaultManager()
        self.environment = None
        self.vault_addr = None
        self.cert_pem = None
        self.key_pem = None
        self.vault_client = None

    def init(self, environment=None, vault_addr=None, ttl_seconds=300):
        """Initialize the VaultHelper."""
        self.environment = environment

        # Determine Vault address
        if vault_addr:
            self.vault_addr = self._ensure_valid_vault_addr(vault_addr)
        else:
            self.vault_addr = self.get_vault_host()

        hostname = socket.gethostname()

        # Set certificate paths based on hostname
        if hostname == "rosie2.ad.nodalx.net":
            self.cert_pem = os.path.join("/opt", "cmdb_vault", "deployerpull.crt")
            self.key_pem = os.path.join("/opt", "cmdb_vault", "deployerpull.key")
        else:
            self.cert_pem = os.path.join(os.environ["HOME"], "cmdb_vault", "deployerpull.crt")
            self.key_pem = os.path.join(os.environ["HOME"], "cmdb_vault", "deployerpull.key")

        # Get a Vault connection with the manager
        self.vault_client = self.vault_manager.get_connection(
            self.vault_addr, ttl_seconds, self.cert_pem, self.key_pem
        )

    def get_vault_host(self) -> str:
        """Retrieve the Vault host based on the environment and ensure it includes scheme and port."""
        from CMDB import CMDB
        from CMDB.exceptions import CMDBException

        cmdb = CMDB()
        query = '''
            SELECT property_value 
            FROM new_environment_property_value 
            WHERE property_name = 'VAULT.SERVER.HOST' 
              AND environment_name = '{env}';
        '''
        try:
            results = cmdb.execute_query(query.format(env=self.environment))
        except CMDBException as e:
            LOG.exception("Error occurred while obtaining Vault host:\n" + query)
            LOG.exception(str(e))
            raise

        if results:
            raw_vault_host = results[0][0]
            LOG.info(f"Retrieved Vault host: {raw_vault_host}")
            return self._ensure_valid_vault_addr(raw_vault_host)
        else:
            error_message = f"No Vault host found for environment: {self.environment}"
            LOG.error(error_message)
            raise ValueError(error_message)

    def _ensure_valid_vault_addr(self, vault_addr: str) -> str:
        """Ensure the Vault address includes scheme and port."""
        if not vault_addr.startswith("http://") and not vault_addr.startswith("https://"):
            vault_addr = f"https://{vault_addr}"

        if ':' not in vault_addr.split('//')[-1]:  # Check if port is missing after the host
            vault_addr += ":8200"

        return vault_addr

    def read_secrets(self, mount_point: str, secret_path: str, keys: list) -> dict:
        """Read secrets from Vault."""
        try:
            LOG.info(f"Reading secret from Vault at {mount_point}/{secret_path}")
            secret_data = self.vault_client.secrets.kv.v2.read_secret_version(
                mount_point=mount_point,
                path=secret_path
            )["data"]["data"]
            LOG.info("Secret read successfully.")
            return {key: secret_data.get(key) for key in keys}
        except hvac.exceptions.InvalidPath:
            LOG.error(f"Secret not found at {mount_point}/{secret_path}")
            return {}
        except Exception as ex:
            LOG.error(f"Failed to read secret: {ex}", exc_info=True)
            raise

    def get_cmdb_creds(self) -> tuple:
        """Retrieve CMDB credentials from Vault."""
        keys = ['database', 'password', 'host', 'username', 'port']
        mount_point = 'techops/secrets'
        secret_path = 'RTV/deployer_secrets/cmdb'

        try:
            LOG.info(f"Retrieving CMDB credentials from Vault at {mount_point}/{secret_path}")

            if not self.vault_client:
                raise ValueError("Vault client is not initialized.")

            secret_data = self.vault_client.secrets.kv.v2.read_secret_version(
                mount_point=mount_point,
                path=secret_path
            )["data"]["data"]

            ordered_values = [secret_data.get(key) for key in keys]
            if not all(ordered_values):
                missing_keys = [key for key, value in zip(keys, ordered_values) if value is None]
                LOG.error(f"Missing keys in CMDB credentials: {', '.join(missing_keys)}")
                raise ValueError(f"Missing CMDB credentials for keys: {missing_keys}")

            LOG.info("Successfully retrieved CMDB credentials.")
            return tuple(ordered_values)

        except hvac.exceptions.InvalidPath:
            LOG.error(f"Invalid path: Secrets not found at {mount_point}/{secret_path}")
            raise

        except Exception as ex:
            LOG.error(f"Failed to retrieve CMDB credentials: {ex}", exc_info=True)
            raise

    def close_connection(self):
        """Closes the Vault client connection."""
        LOG.info("Closing Vault client connection.")
        self.vault_client = None


def _initialize_vault_client(self, vault_addr, cert_pem, key_pem):
    """Initialize a Vault client for the given address."""
    try:
        LOG.info(f"Connecting to Vault at {vault_addr}")
        client = hvac.Client(url=vault_addr)
        client.auth.cert.login(cert_pem=cert_pem, key_pem=key_pem)
        LOG.info("Vault client created successfully.")
        return client
    except Exception as ex:
        LOG.error(f"Failed to create Vault client: {ex}", exc_info=True)
        raise
