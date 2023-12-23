#!/bin/bash
# use following command to make this file executable:
# Run chmod +x tcp_macos_setup.sh to make the script executable.

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Python could not be found. Please install Python."
    exit
fi

# Create TCP directory in the Documents directory
mkdir -p ~/Documents/TCP/application

# Create a virtual environment
python3 -m venv ~/Documents/TCP/application/venv

# Activate the virtual environment
source ~/Documents/TCP/application/venv/bin/activate

# Download the code from GitHub
Curl -L https://github.com/boiseskibum/JT_Analytics_for_Athletes/archive/refs/tags/Beta_Release_2023_12_22_1.zip ~/Documents/TCP/application/code.zip

##########################
to do the latest release run the following code, uncomment down below
##########################
# code to get the most current version of a file
# Set your repository details
OWNER="boiseskibum"  # Replace with the GitHub username or organization
REPO="JT_Analytics_for_Athletes"    # Replace with the repository name

# Get the latest release data from GitHub API
LATEST_RELEASE=$(curl -s "https://api.github.com/repos/$OWNER/$REPO/releases/latest")

# Extract the URL of the first asset
ASSET_URL=$(echo $LATEST_RELEASE | jq -r '.assets[0].browser_download_url')

# Check if the URL is valid
if [ -z "$ASSET_URL" ] || [ "$ASSET_URL" == "null" ]; then
  echo "No assets found in the latest release."
  exit 1
fi

# Output the URL
echo "Latest Release URL: $ASSET_URL"

# Uncomment the following line to download the asset
# curl -L -o filename.ext "$ASSET_URL"
######################

# unzip the file,
unzip ~/Documents/TCP/application/code.zip -d ~/Documents/TCP/application/
mv ~/Documents/TCP/application/repository-1.0.0 ~/Documents/TCP/application/code
rm ~/Documents/TCP/application/code.zip

# Install required modules
pip install -r ~/Documents/TCP/application/code/requirements.txt

# Create TCP_start command file
echo "#!/bin/bash" > ~/Documents/TCP/TCP_start
echo "source ~/Documents/TCP/application/venv/bin/activate" >> ~/Documents/TCP/TCP_start
echo "python ~/Documents/TCP/application/code/TCP_main.py" >> ~/Documents/TCP/TCP_start
chmod +x ~/Documents/TCP/TCP_start

echo "Setup completed. Run your application with '~/Documents/TCP/TCP_start'"
