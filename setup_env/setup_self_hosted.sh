# This is a setup script for the self-hosted server
# used for CI/CD workflows.

# Install git
sudo apt update
sudo apt-get --yes --force-yes install git

# Create CICD dir
sudo mkdir /var/data/store-lidarhd/projet-LHD
sudo chmod -R 777 /var/data/store-lidarhd/projet-LHD
mkdir /var/data/store-lidarhd/projet-LHD/ProduitDeriveLidar
cd /var/data/store-lidarhd/projet-LHD

# Install anaconda (https://docs.anaconda.com/anaconda/install/linux/)
sudo apt-get --yes --allow install libgl1-mesa-glx libegl1-mesa libxrandr2 libxrandr2 libxss1 libxcursor1 libxcomposite1 libasound2 libxi6 libxtst6
wget https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh
bash Anaconda3-2021.11-Linux-x86_64.sh -b -p Anaconda3

# Add right of "/etc/fstab"
sudo chmod u+rwx
# Insert the command in the last file
//store.ign.fr/store-lidarhd/projet-LHD      /var/data/store-lidarhd/projet-LHD    cifs    credentials=/root/.smbcredentials,uid=24636,gid=10000,iocharset=utf8   0       0

# Create the file 'smbcredentials' in the folder 'root'
sudo mdkir /root/.smbcredentials
# Insert the informations in the file
'
username=MDupays
password=MotdePasseSession
domain=ign
'

# Mouting file assets for tests - you will need credentials fo both self-hosted server and mounted asset directory
sudo mount -v -t cifs -o user=mdupays,domain=IGN,uid=24636,gid=10000 //store.ign.fr/store-lidarhd/projet-LHD/Classification /var/data/store-lidarhd/projet-LHD/Classification/

# Install necessary libraries onces
sudo apt-get --yes --allow install nvidia-cuda-toolkit
sudo apt-get install postgis
