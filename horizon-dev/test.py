#!/usr/bin/env python3
import os
import logging
import argparse
from paramiko_wrapper import ParamikoWrapper
from CMDB import CMDB

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jboss_cleanup")
logger.addHandler(logging.StreamHandler())

def get_machine_ip(cmdb, machine_name):
    """
    Get machine IP using CMDB query
    """
    try:
        query = """
            SELECT prop_value 
            FROM new_machine_prop_value 
            WHERE machine_name = %s 
            AND prop_name = 'SERVER.IP'
        """
        # Pass parameters as a list
        args = [machine_name]  # Changed from tuple to list
        result = cmdb.execute_query_safe(query, args)[0][0]
        return result
    except Exception as e:
        logger.error(f"Error getting IP for machine {machine_name}: {str(e)}")
        return None

def remove_jboss_directories_and_files_in_one_command(ip, private_key):
    """
    Removes the /opt/jboss directory, /home/jboss directory, and specific script files
    on the target server in a single SSH command.
    """
    logger.info(f"Starting cleanup for machine on server with IP: {ip}")
    
    combined_command = "rm -rf /opt/jboss /home/jboss && rm -f /opt/jboss/stop_jboss.sh /opt/jboss/start_jboss.sh"
    logger.info("Executing combined cleanup command...")
    
    cmd_results = ParamikoWrapper.ssh_cmd(ip, combined_command, private_key, 
                                        print_stdout=False, logger_name=logger.name)
    
    if cmd_results.get('stderr_raw'):
        logger.warning(f"Error during cleanup: {cmd_results['stderr_raw'].decode()}")
    else:
        logger.info("Cleanup command executed successfully")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Remove JBoss directories and specific script files on target servers."
    )
    parser.add_argument("-m", "--machines", required=True, 
                       help="Comma-separated list of machine names")
    args = parser.parse_args()
    
    # Initialize CMDB instance
    cmdb = CMDB()
    
    # Path to the private key for SSH
    private_key = os.path.expanduser("~/.ssh/id_rsa")
    
    # Split the machine names and process each
    machine_list = args.machines.split(",")
    
    for machine in machine_list:
        logger.info(f"Processing machine: {machine}")
        
        # Get IP using CMDB query
        machine_ip = get_machine_ip(cmdb, machine)
        
        if not machine_ip:
            logger.error(f"IP address for machine {machine} not found. Skipping...")
            continue
            
        # Run the combined cleanup function
        remove_jboss_directories_and_files_in_one_command(machine_ip, private_key)
