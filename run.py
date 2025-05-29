import os
import paramiko
import time

HOSTNAME='172.20.10.11'
USERNAME='ft'
PASSWORD='fischertechnik'

def main():
    ssh = paramiko.SSHClient() 
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)

    stdin, stdout, stderr = ssh.exec_command("sudo -S python3 /opt/ft/workspaces/ft_example/main.py")
    stdin.write(PASSWORD + '\n')
    stdin.flush()

    while True:
        line = stdout.readline()
        if not line:
            break
        print(line, end='')
        time.sleep(0.5)


    ssh.close()

if __name__ == '__main__':
    main()