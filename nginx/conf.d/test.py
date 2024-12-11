#!/usr/bin/env python3
import hvac
import logging
import os
import time
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
    """Manages connections to multiple Vault servers with TTL caching."""

    def __init__(self):
        self.connections = {}  # {vault_addr: {"client": client_instance, "ttl": expiry_time}}
        self.lock = Lock()  # To ensure thread-safe operations on connections

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

    def init(self, environment=None, vault_addr=None, ttl_seconds=300):
        """Initialize the VaultHelper."""
        self.environment = environment
        self.vault_addr = vault_addr or self.get_vault_host()
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
        """Retrieve the Vault host based on the environment."""
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
            vault_host = results[0][0]
            LOG.info(f"Retrieved Vault host: {vault_host}")
            return f"https://{vault_host}:8200"
        else:
            raise ValueError(f"No Vault host found for environment: {self.environment}")

    def get_smtp_creds(self, environment: str) -> tuple:
        """Retrieve SMTP credentials from Vault."""
        keys_to_retrieve = ['smtp.secure.username', 'smtp.secure.password']
        mount_point = f'nodalsuite/{environment}/kv'
        secrets = self.read_secrets(mount_point, 'smtp', keys_to_retrieve)

        smtp_username = secrets.get('smtp.secure.username')
        smtp_password = secrets.get('smtp.secure.password')

        if not smtp_password or not smtp_username:
            LOG.error(f"Unable to acquire SMTP password from Vault for environment: {environment}")
            raise ValueError('SMTP password not found.')

        return smtp_username, smtp_password

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

    def close_connection(self):
        """Closes the Vault client connection."""
        LOG.info("Closing Vault client connection.")
        self.vault_client = None
