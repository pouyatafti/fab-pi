import os

from getpass import getpass
from fabric.api import env, local, run, sudo, put, reboot, lcd

def write_disk(disk, boot_partition=None):
	if boot_partition is None:
		boot_partition = disk + "1"

	local('rm -rf ./work')
	local('mkdir -p ./work/mnt')
	with lcd('./work'):
		local('wget https://downloads.raspberrypi.org/raspbian_latest')
		local('unzip raspbian_latest')
		local('sudo dd if=$(find . -name "*.img") of=%s bs=2M' % disk)

		# enable remote ssh on first boot
		local('sudo mount %s ./mnt' % boot_partition)
		local('sudo touch ./mnt/ssh')
		local('sudo umount ./mnt')

def remote_uname():
	run('uname -a')

def create_user(pubkey, username, passwd=None):
	if username == 'pi':
		raise ValueError('default user pi is not allowed')

	# get passwd
	if passwd is None:
            passwd = getpass('new password for user %s: ' % username)
		
	# add new user
	sudo('useradd %s -s /bin/sh -m -G adm,sudo' % username)
	sudo('echo -e "%s\\\\n%s" | passwd %s' % (passwd, passwd, username))
	sudo('sed -i "s/sudo\s.*ALL=(ALL:ALL) ALL/sudo	ALL=(ALL) NOPASSWD: ALL/g" /etc/sudoers')

	# deploy public key
	sudo('mkdir -p /home/%s/.ssh' % username, user=username)
	sudo('chmod 700 /home/%s/.ssh' % username, user=username)
	put(pubkey, '/home/%s/.ssh/authorized_keys' % username, use_sudo=True)
	sudo('chown -R %s:%s /home/%s/.ssh' % (username, username, username))
	sudo('chmod 600 /home/%s/.ssh/authorized_keys' % username)

def remove_x11():
    sudo('apt-get remove -y --purge oracle-java8-jdk openjdk-7-jre oracle-java7-jdk openjdk-8-jre')
    sudo('apt-get -y --purge remove ca-certificates-java') 
    sudo('apt-get -y --purge remove cups*')
    sudo('apt-get -y --purge remove gnome*')
    sudo('apt-get -y --purge remove x11-common*')
    sudo('apt-get -y --purge autoremove')

def upgrade():
	sudo('apt-get update -y')
	sudo('apt-get dist-upgrade -y')
	sudo('apt-get autoremove -y')

def setup_wifi():
	put('./files/wpa_supplicant.conf', '/etc/wpa_supplicant/wpa_supplicant.conf', mode='0600', use_sudo=True)

def setup_unattended_upgrades():
	sudo('apt-get install unattended-upgrades apt-listchanges -y')
	put('./files/50unattended-upgrades', '/etc/apt/apt.conf.d/50unattended-upgrades', use_sudo=True)
	put('./files/20auto-upgrades', '/etc/apt/apt.conf.d/20auto-upgrades', use_sudo=True)

def harden(hostname, pubkey, username, passwd=None, first_run='True'):
        runone = (first_run.lower() == 'true')

	# create new user and delete the default one
        if runone:
            create_user(pubkey, username, passwd)

            env.user = username
            env.key_filename = pubkey[:-4]

            sudo('sudo service lightdm stop')
            sudo('sudo systemctl disable autologin@tty1')
            sudo('sudo systemctl stop autologin@tty1')
            sudo('for p in $(ps -o pid -u pi | tail -n +2); do kill -9 $p; done')
            sudo('userdel pi')
            sudo('rm -rf /home/pi')

	# change hostname
	sudo('hostname %s && sed -i "s/raspberrypi/%s/g" /etc/hosts && sed -i "s/raspberrypi/%s/g" /etc/hostname' % (hostname, hostname, hostname))

	# update ssh and sshd configuration
	put(os.path.join(os.getcwd(), 'files/ssh_config'), '/etc/ssh/ssh_config', use_sudo=True)
	put(os.path.join(os.getcwd(), 'files/sshd_config'), '/etc/ssh/sshd_config', use_sudo=True)
        sudo('systemctl restart ssh')

        # configure firewall
        sudo('DEBIAN_FRONTEND=noninteractive apt-get install iptables iptables-persistent -yq')
	put(os.path.join(os.getcwd(), 'files/rules.v4'), '/etc/iptables/rules.v4', use_sudo=True)
	put(os.path.join(os.getcwd(), 'files/rules.v6'), '/etc/iptables/rules.v6', use_sudo=True)

def deploy(hostname, pubkey, username, passwd=None, first_run='True'):
        runone = (first_run.lower() == 'true')

        if runone:
            env.user = 'pi'
        else:
            env.user = username
            env.key_filename = pubkey[:-4]

	setup_wifi()
        remove_x11()
	upgrade()
	setup_unattended_upgrades()
	harden(hostname, pubkey, username, passwd, first_run)
	reboot()
