#!/bin/bash
# use following command to make this file executable:
# Run chmod +x TPC_macos_setup.sh to make the script executable.

## Set your repository details
VERSION_TAG="v1.0.1"    # Replace with the repository name
OWNER="boiseskibum"  # Replace with the GitHub username or organization
REPO="TPC_Analytics"    # Replace with the repository name
VERSION_TAG_NO_V=${VERSION_TAG:1}  # Remove the 'v' prefix from version tag

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

echo "TPC: downloading code from GitHub"
# Download the code from GitHub
curl -L "https://github.com/$OWNER/$REPO/archive/refs/tags/$VERSION_TAG.zip" -o ~/Documents/TPC/application/code.zip

echo "TPC: unzip, and put code where it belongs"
# unzip the file,
unzip ~/Documents/TPC/application/code.zip -d ~/Documents/TPC/application/
# rename directory with title and version to be "code"
mv ~/Documents/TPC/application/$REPO-$VERSION_TAG_NO_V ~/Documents/TPC/application/code
# delete the zip file
rm ~/Documents/TPC/application/code.zip
# create dummy file to contain the version information
echo "$Github Repository: REPO Version: $VERSION_TAG" > ~/Documents/TPC/TPC_version_info

echo "TPC: installing python code specified in requirements.txt"
# Install required modules
pip install -r ~/Documents/TPC/application/code/requirements.txt

echo "TPC: creating TPC_run command file"

# Create TPC_run command file
echo "#!/bin/bash" > ~/TPC_run
echo "source ~/Documents/TPC/application/venv/bin/activate" >> ~/TPC_run
echo "python ~/Documents/TPC/application/code/TPC_main.py" >> ~/TPC_run
chmod +x ~/TPC_run
echo " "
echo " From the command line and your root directory you can run your application with './TPC_run'"
echo " "

# Creates icon path

# Define paths
appPath="$HOME/Desktop/TPC Analytics.app"
iconPath="$HOME/Documents/TPC/application/code/resources/img/jt.icns"
scriptPath="$HOME/TPC_run"

rm -rf "$appPath"

# Create an AppleScript command to run your bash script
appleScriptCommand="do shell script \"${scriptPath}\""

# Create an AppleScript application
echo "$appleScriptCommand" | osacompile -o "$appPath"

# Set the icon for the application
cp "$iconPath" "$appPath/Contents/Resources/applet.icns"

# Open the Desktop to view the new icon
open "$HOME/Desktop"

#####
appPath="$HOME/Documents/TPC/TPC Analytics.app"

# Create an AppleScript command to run your bash script
appleScriptCommand="do shell script \"${scriptPath}\""

# Create an AppleScript application
echo "$appleScriptCommand" | osacompile -o "$appPath"

# Set the icon for the application
cp "$iconPath" "$appPath/Contents/Resources/applet.icns"

echo "--------------------------------------------------------------------------------------"
echo "--------  TPC:  Installed TPC Analytics.  Find it in Desktop or Documents/TCP/  ------"
echo "--------------------------------------------------------------------------------------"

