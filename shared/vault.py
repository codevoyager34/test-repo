import os
import logging
import hvac
from SingletonWithTTL import SingletonWithTTL  # Assuming SingletonWithTTL is in this file

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class VaultHelper(SingletonWithTTL):
    def on_initialize(self):
        """Initialization logic specific to VaultHelper."""
        self.vault_addr = None
        self.cert_pem = None
        self.key_pem = None
        self.vault_client = None

    def init(self, environment=None, vault_addr=None, ttl_seconds=300):
        """Initialize or reinitialize the VaultHelper with TTL."""
        self.environment = environment
        super().init_ttl(ttl_seconds=ttl_seconds)  # Use TTL logic

        if self.vault_client is None:  # Only setup Vault details if not already initialized
            self.vault_addr = f"https://{vault_addr}:8200" if vault_addr else self.get_vault_host()
            self.cert_pem = os.path.join(os.environ["HOME"], "cmdb_vault", "deployerpull.crt")
            self.key_pem = os.path.join(os.environ["HOME"], "cmdb_vault", "deployerpull.key")
            self.vault_client = self.create_vault_client()

    def get_vault_host(self):
        # Example implementation for getting the Vault host
        return "https://default-vault.example.com:8200"

    def create_vault_client(self):
        """Create an HVAC client."""
        try:
            LOG.info("Creating HVAC client with cert authentication...")
            client = hvac.Client(url=self.vault_addr)
            client.auth.cert.login(cert_pem=self.cert_pem, key_pem=self.key_pem)
            LOG.info("Vault client created successfully.")
            return client
        except Exception as ex:
            LOG.error(f"Failed to create Vault client: {ex}")
            raise

    # Additional Vault-specific methods here...
