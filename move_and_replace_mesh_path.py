import os
import shutil
import xml.etree.ElementTree as ET

# Define the paths to the URDF file and the meshes directory
work_dir = os.path.dirname(os.path.realpath(__file__))

urdf_path = os.path.join(work_dir, "john_deere.urdf")
meshes_dir = os.path.join(work_dir, "meshes")


# Create a copy of the original urdf file
remote_urdf_path = urdf_path.replace(".urdf", "_remote.urdf")
shutil.copyfile(urdf_path, remote_urdf_path)

# remote url
remote_url = "https://raw.githubusercontent.com/CM134/urdf-test/main/"


# Parse the URDF file
tree = ET.parse(urdf_path)
root = tree.getroot()

# Find all the mesh tags in the URDF file
mesh_tags = root.findall(".//mesh")

for mesh_tag in mesh_tags:
    # Extract the filename attribute from the mesh tag
    filename = mesh_tag.attrib["filename"]

    # Construct the full path to the mesh file
    mesh_path = filename.replace("file://", "")

    # Construct the new path for the mesh file in the meshes directory
    new_mesh_path = os.path.join(meshes_dir, os.path.basename(mesh_path))

    # Check if file exists
    if not os.path.isfile(mesh_path):
        print("File does not exist: {}".format(mesh_path))
        continue

    # Copy the mesh file to the meshes directory
    shutil.copyfile(mesh_path, new_mesh_path)

    # Update the filename attribute of the mesh tag to point to the new location of the mesh file
    mesh_tag.attrib["filename"] = remote_url + os.path.relpath(new_mesh_path, work_dir)

# Write the updated URDF file to disk
tree.write(remote_urdf_path)
