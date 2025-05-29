import os
import paramiko
import time

HOSTNAME='172.20.10.11'
USERNAME='ft'
PASSWORD='fischertechnik'

def copy_helper(sftp: paramiko.SFTPClient, src: str, dest: str):
    sftp.mkdir(dest)
    
    for item in os.listdir(src):
        local_item = src + '/' + item
        remote_item = dest + '/' + item

        if os.path.isdir(local_item):
            copy_helper(sftp, local_item, remote_item)
        else:
            sftp.put(local_item, remote_item)

def upload(sftp: paramiko.SFTPClient, project_name: str, dest: str):
    copy_helper(sftp, project_name, dest + '/' + project_name )

def main():
    ssh = paramiko.SSHClient() 
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)

    stdin, stdout, stderr = ssh.exec_command("sudo -S rm -r /opt/ft/workspaces/ft_example")
    stdin.write(PASSWORD + '\n')
    stdin.flush()

    print(stdout.readlines(), stderr.readlines())
    sftp = ssh.open_sftp()

    upload(sftp, 'ft_example', '/opt/ft/workspaces')
    
    sftp.close()

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