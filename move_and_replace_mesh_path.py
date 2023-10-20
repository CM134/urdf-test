import os
import shutil
import xml.etree.ElementTree as ET
import argparse
from ament_index_python.packages import get_package_share_directory

import xacro


# Define the paths to the URDF file and the meshes directory
WORK_DIR = os.path.dirname(os.path.realpath(__file__))
MESH_DIR = os.path.join(WORK_DIR, "meshes")


def get_urdf_from_xacro(
    package_name: str,
    application: str,
    serial_no: str,
    implement_serial_no: str,
    simulation: str,
):
    # only loads implement when simulation is true
    if implement_serial_no is not None:
        simulation = "true"

    description_mappings = {
        "application": application,
        "simulation": simulation,
        "serial_no": serial_no,
        "implement_serial_no": implement_serial_no,
    }

    urdf_name = package_name.replace("platform_", "") + ".urdf"
    xacro_file = os.path.join(
        get_package_share_directory(package_name),
        "urdf",
        (urdf_name + ".xacro"),
    )
    assert os.path.exists(xacro_file), f"The {xacro_file} doesn't exist"

    robot_desc = xacro.process_file(
        xacro_file, mappings=description_mappings
    ).toprettyxml(indent="  ")

    # add serial_no to the urdf_name
    urdf_name = urdf_name.replace(
        ".urdf", f"_{serial_no}_{application}_{implement_serial_no}.urdf"
    )

    return ET.fromstring(robot_desc), urdf_name


def get_urdf_file_path(urdf_path):
    os.path.join(urdf_path)
    assert os.path.exists(urdf_path), f"The {urdf_path} doesn't exist"

    urdf_name = os.path.basename(urdf_path)

    tree = ET.parse(urdf_path)
    return tree.getroot(), urdf_name


def create_remote_urdf(root, urdf_name):
    # Create a copy of the original urdf file
    urdf_path = os.path.join(WORK_DIR, "urdf", urdf_name)

    remote_urdf_path = urdf_path.replace(".urdf", "_remote.urdf")
    # shutil.copyfile(urdf_path, remote_urdf_path)

    # remote url
    remote_url = "https://raw.githubusercontent.com/CM134/urdf-test/main/"

    # Find all the mesh tags in the URDF file
    mesh_tags = root.findall(".//mesh")

    for mesh_tag in mesh_tags:
        # Extract the filename attribute from the mesh tag
        filename = mesh_tag.attrib["filename"]

        # Construct the full path to the mesh file
        mesh_path = filename.replace("file://", "")

        # Construct the new path for the mesh file in the meshes directory
        new_mesh_path = os.path.join(MESH_DIR, os.path.basename(mesh_path))

        # Check if file exists
        if not os.path.isfile(mesh_path):
            print("File does not exist: {}".format(mesh_path))
            continue

        # Copy the mesh file to the meshes directory
        shutil.copyfile(mesh_path, new_mesh_path)

        # Update the filename attribute of the mesh tag to point to the new location of the mesh file
        mesh_tag.attrib["filename"] = remote_url + os.path.relpath(
            new_mesh_path, WORK_DIR
        )

    # Write the updated URDF file to disk
    tree = ET.ElementTree(root)
    tree.write(remote_urdf_path)

    print("Remote URDF file created: {}".format(remote_urdf_path))


def main(args):
    package_name = args.package_name
    urdf_file_name = args.urdf_file_name
    application = args.application
    serial_no = args.serial_no
    implement_serial_no = args.implement_serial_no
    simulation = args.simulation

    if package_name is not None:
        assert (
            (application is not None)
            and (serial_no is not None)
            and (implement_serial_no is not None)
        ), "To parse XACRO it requires application, serial_no, implement_serial_no."
        root, urdf_name = get_urdf_from_xacro(
            package_name, application, serial_no, implement_serial_no, simulation
        )
    elif urdf_file_name is not None:
        root, urdf_name = get_urdf_file_path(urdf_file_name)
    else:
        raise ValueError("Either package_name or urdf_file_name must be provided.")

    create_remote_urdf(root, urdf_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "-p",
        "--package_name",
        type=str,
        help="Name of the package containing the XACRO file to make remote.\nRequires application, simulation, serial_no, implement_serial_no. \nPath to the XACRO file is assumed to be <package_name>/urdf/<robot_name>.urdf.xacro. Where robot_name is the name of the package without the 'platform_' prefix.",
    )

    parser.add_argument(
        "-a",
        "--application",
        type=str,
        help="Name of the application",
    )
    parser.add_argument(
        "-s",
        "--simulation",
        type=str,
        help="Name of the simulation",
    )
    parser.add_argument(
        "-sn",
        "--serial_no",
        type=str,
        help="Name of the serial number",
    )
    parser.add_argument(
        "-isn",
        "--implement_serial_no",
        type=str,
        help="Name of the implement serial number",
    )

    parser.add_argument(
        "-u",
        "--urdf_file_name",
        type=str,
        help="Name of the URDF file to make remote available",
    )

    args = parser.parse_args()
    main(args)
