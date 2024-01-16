#!/bin/bash
# use following command to make this file executable:
# Run chmod +x TPC_macos_setup.sh to make the script executable.

## Set your repository details
VERSION_TAG="v1.0.0"    # Replace with the repository name
OWNER="boiseskibum"  # Replace with the GitHub username or organization
REPO="TPC_Analytics"    # Replace with the repository name

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Python could not be found. Please install Python."
    exit
fi

# Create TPC directory in the Documents directory
mkdir -p ~/Documents/TPC/application

# Create a virtual environment
python3 -m venv ~/Documents/TPC/application/venv

# Activate the virtual environment
source ~/Documents/TPC/application/venv/bin/activate

# Download the code from GitHub
curl -L "https://github.com/$OWNER/$REPO/archive/refs/tags/$VERSION_TAG.zip" -o ~/Documents/TPC/application/code.zip
#curl -L https://github.com/boiseskibum/JT_Analytics_for_Athletes/archive/refs/tags/Beta_Release_2023_12_22_1.zip -o ~/Documents/TPC/application/code.zip

##########################
# to do the latest release run the following code, uncomment down below
##########################
# code to get the most current version of a file

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
unzip ~/Documents/TPC/application/code.zip -d ~/Documents/TPC/application/
# rename directory with title and version to be "code"
mv ~/Documents/TPC/application/$REPO-$VERSION_TAG ~/Documents/TPC/application/code
# delete the zip file
rm ~/Documents/TPC/application/code.zip
# create dummy file to contain the version information
echo "$Github Repository: REPO Version: $VERSION_TAG" > ~/Documents/TPC/TPC_version_info

# Install required modules
pip install -r ~/Documents/TPC/application/code/requirements.txt

# Create TPC_run command file
echo "#!/bin/bash" > ~/TPC_run
echo "source ~/Documents/TPC/application/venv/bin/activate" >> ~/TPC_run
echo "python ~/Documents/TPC/application/code/TPC_main.py" >> ~/TPC_run
chmod +x ~/TPC_run
echo " "
echo "Setup completed. Run your application with './TPC_run'"
echo " "
