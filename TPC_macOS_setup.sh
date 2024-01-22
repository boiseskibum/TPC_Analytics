#!/bin/bash
# use following command to make this file executable:
# Run chmod +x TPC_macos_setup.sh to make the script executable.

## Set your repository details
VERSION_TAG="v1.0.2"    # Replace with the repository name
OWNER="boiseskibum"  # Replace with the GitHub username or organization
REPO="TPC_Analytics"    # Replace with the repository name
VERSION_TAG_NO_V=${VERSION_TAG:1}  # Remove the 'v' prefix from version tag
APP_NAME="TPC Analytics"

echo " "
echo "************************************************************************************"
echo "****************** $APP_NAME: Installing $APP_NAME $VERSION_TAG ********************"
echo "************************************************************************************"
echo " "

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo ""
    echo "*****  Python could not be found. Please install Python and rerun this script *****"
    echo "*****  go to https://www.python.org/downloads/macos/ and install version 3.11.x *****"
    echo ""
    exit
fi

echo "$APP_NAME: Create $APP_NAME directory in the Documents directory"
echo ""
mkdir -p ~/Documents/$APP_NAME/application

# Create a virtual environment
python3 -m venv ~/Documents/$APP_NAME/application/venv

# Activate the virtual environment
source ~/Documents/$APP_NAME/application/venv/bin/activate

echo "$APP_NAME: downloading code from GitHub"
# Download the code from GitHub
curl -L "https://github.com/$OWNER/$REPO/archive/refs/tags/$VERSION_TAG.zip" -o ~/Documents/$APP_NAME/application/code.zip

echo "$APP_NAME: unzip, and put code where it belongs"
# unzip the file,
unzip ~/Documents/$APP_NAME/application/code.zip -d ~/Documents/$APP_NAME/application/
# rename directory with title and version to be "code"
mv ~/Documents/$APP_NAME/application/$REPO-$VERSION_TAG_NO_V ~/Documents/$APP_NAME/application/code
# delete the zip file
rm ~/Documents/$APP_NAME/application/code.zip
# create dummy file to contain the version information
echo "$Github Repository: REPO Version: $VERSION_TAG" > ~/Documents/$APP_NAME/TPC_Analytics_version_info
echo ""

echo "$APP_NAME: installing python code specified in requirements.txt"
echo ""
# Install required modules
pip install -r ~/Documents/$APP_NAME/application/code/requirements.txt

echo "$APP_NAME: creating TPC_Analytics_run command file"
echo ""

# Create TPC_Analytics_run command file
echo "#!/bin/bash" > ~/TPC_Analytics_run
echo "source ~/Documents/$APP_NAME/application/venv/bin/activate" >> ~/TPC_Analytics_run
echo "python ~/Documents/$APP_NAME/application/code/TPC_Analytics_main.py" >> ~/TPC_Analytics_run
chmod +x ~/TPC_Analytics_run
echo " "
echo " From the command line and your root directory you can run your application with './TPC_Analytics_run'"
echo " "

# Creates icon path

# Define paths
appPath="$HOME/Desktop/$APP_NAME.app"
iconPath="$HOME/Documents/$APP_NAME/application/code/resources/img/jt.icns"
scriptPath="$HOME/TPC_Analytics_run"

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
appPath="$HOME/Documents/$APP_NAME/$APP_NAME.app"

# Create an AppleScript command to run your bash script
appleScriptCommand="do shell script \"${scriptPath}\""

# Create an AppleScript application
echo "$appleScriptCommand" | osacompile -o "$appPath"

# Set the icon for the application
cp "$iconPath" "$appPath/Contents/Resources/applet.icns"
echo ""
echo "------------------------------------------------------------------------------------------------"
echo "--------  $APP_NAME:  Installed $APP_NAME.  Find it in Desktop or Documents/$APP_NAME/  ------"
echo "------------------------------------------------------------------------------------------------"

