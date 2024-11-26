import hvac
import logging
import os
from singleton_with_ttl import SingletonWithTTL  # Import the separated SingletonWithTTL class

# Configure logging
LOG = logging.getLogger("vault_helper")
LOG.setLevel(logging.INFO)

if not LOG.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    LOG.addHandler(handler)


class VaultHelper(SingletonWithTTL):
    """VaultHelper for managing HashiCorp Vault interactions."""

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

    def create_vault_client(self) -> hvac.Client:
        """Create an HVAC client."""
        try:
            LOG.info("Creating HVAC client with cert authentication...")
            client = hvac.Client(url=self.vault_addr)
            client.auth.cert.login(cert_pem=self.cert_pem, key_pem=self.key_pem)
            LOG.info("Vault client created successfully.")
            return client
        except Exception as ex:
            LOG.error(f"Failed to create Vault client: {ex}", exc_info=True)
            raise

    def get_smtp_creds(self, environment: str) -> tuple:
        """Retrieve SMTP credentials from Vault."""
        keys_to_retrieve = ['smtp.secure.username', 'smtp.secure.password']
        mount_point = f'nodalsuite/{environment}/kv'
        secrets = self.read_secrets(mount_point, 'smtp', keys_to_retrieve)

        smtp_username = secrets.get('smtp.secure.username')
        smtp_password = secrets.get('smtp.secure.password')

        if not smtp_password:
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
        if self.vault_client:
            LOG.info("Closing Vault client connection.")
            self.vault_client = None

