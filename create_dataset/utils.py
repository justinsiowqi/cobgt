import os
import glob

# Function to get the GCP Credentials File Path 
def get_gcp_credentials_path(config_folder="config"):
    """
    Automatically find the neo4j credentials file in the given config folder.
    
    Returns:
        The path to the credentials file.
    """
    # Get the Path to the Config Folder
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    config_folder = os.path.join(parent_dir, "config")
    
    pattern = os.path.join(config_folder, "*.json")
    files = glob.glob(pattern)
    
    if not files:
        raise FileNotFoundError(
            f"No gcp credentials file found in '{config_folder}'."
        )
    
    # Choose the Most Recent File
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]