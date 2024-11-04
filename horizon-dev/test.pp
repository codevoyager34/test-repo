
node 'your_node_name' {
    # Ensure the firewall services for Wildfly and Wildfly debugging are removed
    firewalld_service { 'wildfly':
        ensure => 'absent',
        zone   => 'public',
    }

    firewalld_service { 'wildflydebugging':
        ensure => 'absent',
        zone   => 'public',
    }

    # Reload firewalld to apply the changes only if services are modified
    exec { 'firewalld-reload':
        command     => '/bin/firewall-cmd --reload',
        path        => '/bin:/usr/bin',
        refreshonly => true,
        subscribe   => [ Firewalld_service['wildfly'], Firewalld_service['wildflydebugging'] ],
    }

    # Remove the /opt/jboss directory and its contents
    file { '/opt/jboss':
        ensure  => absent,
        recurse => true,
        force   => true,
        owner   => 'jboss',  # Adjust ownership if needed
        group   => 'jboss',
    }

    # Remove the /home/jboss directory and its contents
    file { '/home/jboss':
        ensure  => absent,
        recurse => true,
        force   => true,
        owner   => 'jboss',  # Adjust ownership if needed
        group   => 'jboss',
    }

    # Remove the jboss user and its home directory
    user { 'jboss':
        ensure     => absent,
        managehome => true,  # This will remove the home directory if it hasn't been deleted already
    }
}

