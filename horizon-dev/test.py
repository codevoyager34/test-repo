import os
import logging
import argparse
from paramiko_wrapper import ParamikoWrapper
from CMDB import CMDB  # Importing the CMDB class

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jboss_cleanup")
logger.addHandler(logging.StreamHandler())

def remove_jboss_directories_and_files(ip, private_key):
    """
    Removes the /opt/jboss directory, /home/jboss directory, and specific script files on the target server.
    """
    logger.info(f"Starting cleanup on server with IP: {ip}")

    # Command to remove /opt/jboss directory
    jboss_dir_command = "rm -rf /opt/jboss"
    logger.info("Removing /opt/jboss directory...")
    cmd_results = ParamikoWrapper.ssh_cmd(ip, jboss_dir_command, private_key, print_stdout=False, logger_name=logger.name)
    if cmd_results.get('stderr_raw'):
        logger.warning(f"Error removing /opt/jboss: {cmd_results['stderr_raw'].decode()}")
    else:
        logger.info("/opt/jboss directory removed successfully")

    # Command to remove /home/jboss directory
    jboss_home_command = "rm -rf /home/jboss"
    logger.info("Removing /home/jboss directory...")
    cmd_results = ParamikoWrapper.ssh_cmd(ip, jboss_home_command, private_key, print_stdout=False, logger_name=logger.name)
    if cmd_results.get('stderr_raw'):
        logger.warning(f"Error removing /home/jboss: {cmd_results['stderr_raw'].decode()}")
    else:
        logger.info("/home/jboss directory removed successfully")

    # Commands to remove specific script files in /opt/jboss
    script_files = ["/opt/jboss/stop_jboss.sh", "/opt/jboss/start_jboss.sh"]
    for script in script_files:
        logger.info(f"Removing {script}...")
        script_command = f"rm -f {script}"
        cmd_results = ParamikoWrapper.ssh_cmd(ip, script_command, private_key, print_stdout=False, logger_name=logger.name)
        if cmd_results.get('stderr_raw'):
            logger.warning(f"Error removing {script}: {cmd_results['stderr_raw'].decode()}")
        else:
            logger.info(f"{script} removed successfully")

if __name__ == "__main__":
    # Set up argument parser to take machine names as a comma-separated list
    parser = argparse.ArgumentParser(description="Remove JBoss directories and specific script files on target servers.")
    parser.add_argument("-m", "--machines", required=True, help="Comma-separated list of machine names")
    args = parser.parse_args()

    # Initialize CMDB instance
    cmdb = CMDB()

    # Path to the private key for SSH
    private_key = os.path.expanduser("~/.ssh/id_rsa")

    # Split the machine names and process each
    machine_list = args.machines.split(",")
    for machine in machine_list:
        logger.info(f"Processing machine: {machine}")
        machine_cmdb_properties = cmdb.get_property_values(machine, [])
        machine_ip = machine_cmdb_properties.get('SERVER.IP')

        if not machine_ip:
            logger.error(f"IP address for machine {machine} not found. Skipping...")
            continue

        # Run the cleanup function
        remove_jboss_directories_and_files(machine_ip, private_key)

