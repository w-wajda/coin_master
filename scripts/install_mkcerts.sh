#!/bin/bash

# check if mkcert is installed
check_mkcert() {
    if command -v mkcert &> /dev/null; then
        exit 0;
    else
        echo "mkcert is not installed. Proceeding with installation..."
        install_mkcert
    fi
}

# Function to install mkcert on macOS
install_mkcert_mac() {
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "Error: Homebrew is not installed."
        echo "Please install Homebrew manually using the following command:"
        echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        exit 1;
    fi
    # Install mkcert using Homebrew
    echo "Installing mkcert using Homebrew..."
    brew install mkcert
    # Set up mkcert for local certificate authority
    mkcert -install
}

# Function to install mkcert on Ubuntu
install_mkcert_ubuntu() {
    # Update package lists and install mkcert along with necessary tools
    echo "Updating package lists and installing mkcert..."
    sudo apt-get update
    sudo apt-get install -y mkcert libnss3-tools
    # Set up mkcert for local certificate authority
    mkcert -install
}

# Function to detect the operating system and proceed with mkcert installation
install_mkcert() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS detected
        install_mkcert_mac
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Ubuntu detected
        install_mkcert_ubuntu
    else
        # Unsupported operating system
        echo "Unsupported operating system."
        exit 1
    fi
}

# Main function call to check and install mkcert if needed
check_mkcert
