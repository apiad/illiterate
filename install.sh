set -e

# Fetch the latest release version tag (e.g., v0.1.0)
LATEST_RELEASE=$(curl -s "https://api.github.com/repos/apiad/illiterate/releases/latest" | grep '"tag_name":' | sed -E 's/.*"tag_name": "(.*)",/\1/')

echo "Downloading illiterate version ${LATEST_RELEASE}..."

# Construct the download URL for the Linux binary
DOWNLOAD_URL="https://github.com/apiad/illiterate/releases/download/${LATEST_RELEASE}/illiterate-${LATEST_RELEASE}-linux-x86_64.tar.gz"

# Download and extract the binary into /usr/local/bin
# This may require sudo if you don't have write permissions to the target directory.
wget "${DOWNLOAD_URL}" -O illiterate.tar.gz

echo "Done. Enter your password now to install."

sudo tar -xvzf illiterate.tar.gz -C /usr/local/bin illiterate
rm illiterate.tar.gz

echo "Installation complete. You can now run 'illiterate' from your terminal."
