# fab-pi

fabfile for configuring a headless raspberry pi, with some hardening and a small (but maybe growing) number of additional tasks

## usage

I probably forgot some steps, but here's a try.  you will need a key pair for logging into the pi later on.

1. `git clone https://github.com/pouyatafti/fab-pi.git`
2. `cd fab-pi`
3. insert SD card into deployment machine (e.g. laptop)
4. find out the name of the corresponding disk (e.g. on linux: `dmesg | tail -n 30`)
5. run `fab create_disk:disk=/dev/{disk_found_in_previous_step}` and wait (takes a while)
6. insert SD card into raspberry pi; connect to ethernet, and then to power
7. wait for the raspberry pi to boot
8. find its IP address (e.g. using sth like `nmap -sn 192.168.1.1/24` or by checking your router's web page)
9. run `fab -H {raspi_IP_address} deploy:hostname={my_host},pubkey=/path/to/local/public/key.pub,username={my_user}`
10. enter new password for user 'pi' followed, confusingly, by the previous password when prompted (default password is 'raspberry'; user 'pi' will be deleted later)
11. wait
12. at some point you will be prompted to enter a new password for the new user; enter one
13. at a later point you may be prompted again for the same password.  enter it again
14. generally wait a lot
15. if sth breaks, fix it and retry ;) (once the user has been created, future runs should use `first_run=False`)

you can also do a bunch of other things afterwards, e.g. install tensorflow: `fab -H {my_user}@{raspi_IP_address} deploy_tensorflow` (and hope)
