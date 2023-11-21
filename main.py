import ftplib
import os
from dotenv import load_dotenv

load_dotenv()
# FTP server details for the source (from_server) and destination (to_server)
from_server_ip = os.environ.get("from_server_ip")
from_server_user = os.environ.get("from_server_user")
from_server_pass = os.environ.get("from_server_pass")

to_server_ip = os.environ.get("to_server_ip")
to_server_user = os.environ.get("to_server_user")
to_server_pass = os.environ.get("to_server_pass")

# print(f"first ftp server ip is {from_server_ip}")
# Function to check FTP server reachability using Telnet
def test_ftp_server_connection(server, port=21):
    try:
        ftp = ftplib.FTP()
        ftp.connect(server, port)
        ftp.quit()
        return True
    except Exception as e:
        print(f"Failed to connect to FTP server {server}. Error: {e}")
        return False

# Function to list files in an FTP directory
def get_ftp_directory_listing(server, username, password, directory):
    file_list = []
    try:
        with ftplib.FTP(server) as ftp:
            ftp.login(username, password)
            ftp.cwd(directory)
            ftp.retrlines('LIST', file_list.append)
    except Exception as e:
        print(f"Failed to list directory on FTP server {server}. Error: {e}")
    return file_list

# Function to upload a file to an FTP server
def upload_ftp_file(server, username, password, local_file, remote_file):
    try:
        with ftplib.FTP(server) as ftp:
            ftp.login(username, password)
            with open(local_file, 'rb') as file:
                ftp.storbinary(f'STOR {remote_file}', file)
    except Exception as e:
        print(f"Failed to upload file to FTP server {server}. Error: {e}")

# Check FTP server reachability for both source and destination servers
from_server_reachable = test_ftp_server_connection(from_server_ip)
to_server_reachable = test_ftp_server_connection(to_server_ip)

if from_server_reachable and to_server_reachable:
    try:
        # List files in the source directory
        source_directory_path = "/"
        source_file_list = get_ftp_directory_listing(from_server_ip, from_server_user, from_server_pass, source_directory_path)

        if source_file_list:
            # Specify the destination directory path
            destination_directory_path = "/In"

            # Download and upload each file from the source to destination
            with ftplib.FTP(from_server_ip) as from_ftp, ftplib.FTP(to_server_ip) as to_ftp:
                from_ftp.login(from_server_user, from_server_pass)
                to_ftp.login(to_server_user, to_server_pass)

                for file_info in source_file_list:
                    file_name = file_info.split()[-1]
                    source_file_path = f"{source_directory_path}/{file_name}"
                    destination_file_path = f"{destination_directory_path}/{file_name}"

                    # Download the file from the source server
                    with open(file_name, 'wb') as local_file:
                        from_ftp.retrbinary(f"RETR {source_file_path}", local_file.write)

                    # Upload the file to the destination server
                    with open(file_name, 'rb') as local_file:
                        to_ftp.storbinary(f"STOR {destination_file_path}", local_file)

                    # Clean up the downloaded file
                    os.remove(file_name)
                    # delete Source file
                    from_ftp.delete(source_file_path)

            print("File transfer completed successfully.")
        else:
            print(f"No files found in the source directory on FTP server {from_server_ip}.")

    except Exception as e:
        print(f"Error: {e}")

else:
    if not from_server_reachable:
        print(f"FTP server {from_server_ip} is not reachable. Check your network connectivity or FTP server configurations.")
    if not to_server_reachable:
        print(f"FTP server {to_server_ip} is not reachable. Check your network connectivity or FTP server configurations.")
