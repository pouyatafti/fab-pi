# fab-pi

fabfile for configuring a headless raspberry pi

## usage

1. `git clone https://github.com/pouyatafti/fab-pi.git`
2. `cd fab-pi`
3. insert SD card into deployment machine (e.g. laptop)
4. find out the name of the corresponding disk (e.g. on linux: `dmesg | tail -n 30`)
5. run `fab write_image:disk=/dev/{disk_found_in_previous_step}` and wait (takes a while)
6. insert SD card into raspberry pi; connect to ethernet, and then to power
7. wait for the raspberry pi to boot
8. find its IP address (e.g. using sth like `nmap -sn 192.168.1.1/24` or by checking your router's web page)
9. run `fab -H pi@{raspi_IP_address} deploy:hostname={my_hosti},pubkey=/path/to/local/public/key.pub,username={my_user}
10. enter remote password for user 'pi' when prompted (default password is 'raspberry')
11. wait
12. at some point you will be prompted for the new password for the new user; enter one
13. at a later point you will be prompted again for the same password.  enter it again
