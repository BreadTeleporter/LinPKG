#!/usr/bin/python3
# Simple package manager written in python
# LinPKG is licensed under GPL3
# ----------------------------------------

# Imports
import tarfile
import os
import urllib.request
import shutil
from distutils.dir_util import copy_tree
import argparse

# Global variables

# Remember to change sysroot to / when finished
SYSROOT = "sysrootTemp/"

# TODO: Config file for repos
REPO = "https://raw.githubusercontent.com/BreadTeleporter/linpkg-repo/main/"

# Decompress package archive to temp
# Takes file path and returns nothing
def decompressToTemp(fname):
  checkIfTempPathExists()
  # tar = tarfile.open(f"{SYSROOT}/tmp/linpkg/{fname}.tar.gz", "r:gz")
  # tar.extractall(f"{SYSROOT}tmp")
  # tar.close()
  if os.path.exists(f"{SYSROOT}tmp/linpkg/{fname}"):
    shutil.rmtree(f"{SYSROOT}tmp/linpkg/{fname}")
  os.makedirs(f"{SYSROOT}tmp/linpkg/{fname}")
  # os.system(f"tar xf {SYSROOT}tmp/linpkg/{fname}.tar.gz -C {SYSROOT}tmp/linpkg/{fname}/")
  tar = tarfile.open(f"{SYSROOT}/tmp/linpkg/{fname}.tar.gz")
  # tar.getnames()
  # print(contents)
  tar.extractall(f"{SYSROOT}tmp/linpkg/{fname}/")
  tar.close()

# Creates temp path if it does not exist
# Takes nothing and returns nothing
def checkIfTempPathExists():
  if not os.path.exists(f"{SYSROOT}tmp/linpkg"):
    os.makedirs(f"{SYSROOT}tmp/linpkg")

# Get archive from repo defined in 'REPO'
# Takes package name and returns nothing
def getArchiveFromRepo(aname):
  checkIfTempPathExists()
  try:
    urllib.request.urlretrieve(f'{REPO}/{aname}/package.tar.gz', f'{SYSROOT}tmp/linpkg/{aname}.tar.gz')
    return True
  except:
    return False

# Runs getArchiveFromRepo and decompressToTemp in one function
# Takes Package name and returns nothing
def getAndDecompress(aname):
  print(f"Downloading '{aname}'")
  if aname == "":
    return
  if getArchiveFromRepo(aname):
    decompressToTemp(aname)
    return True
  else:
    return False
  
# Copies extracted package from tmp to sysroot
# Takes Package name and returns nothing
def installFromTemp(aname):
  # TODO: Error checking... Kinda important :)
  copy_tree(f"{SYSROOT}/tmp/linpkg/{aname}/", f"{SYSROOT}")

# Clean temp folder when we are done installing
def cleanTemp():
  shutil.rmtree(f"{SYSROOT}tmp/linpkg")

def getDeps(aname):
  # TODO: This is bad code, very bad code.
  try:
    response = urllib.request.urlopen(f'{REPO}/{aname}/deps').read().decode('utf-8').split("\n)")
    if response[0] == "":
      return None
    else:
      return response
  except:
    return None
    
# DEPRECATED
# Add package to installed list
# Takes package name and returns True on success
def addToInstalled(pname):
  with open(f"{SYSROOT}etc/installedPackages", "a") as f:
    f.write(f"{pname}\n")
    f.close()
    return True


def get_files_in_directory(path):
    file_list = []
    
    # Iterate over all items in the directory
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        
        # Check if the item is a file
        if os.path.isfile(item_path):
            file_list.append(item_path)
        # If the item is a directory, recursively call the function
        elif os.path.isdir(item_path):
            file_list.extend(get_files_in_directory(item_path))
    
    return file_list


def addPathsToInstalled(tarfilePath):
  # tar = tarfile.open(f"{SYSROOT}/tmp/linpkg/{tarfilePath}.tar.gz")
  names = [""]
  directory_path = f"{SYSROOT}tmp/linpkg/{tarfilePath}"
  file_list = get_files_in_directory(directory_path)
  
  # Print the list of files
  for file in file_list:
    # print(file)
    names += file
  if not os.path.exists(f"{SYSROOT}etc/linpkg"):
    os.mkdir(f"{SYSROOT}etc/linpkg")
  with open(f"{SYSROOT}etc/linpkg/{tarfilePath}.txt", "w") as f:
    for file in file_list:
      f.write(f"{file.replace(f'sysrootTemp/tmp/linpkg/{tarfilePath}/', '')}\n")
    f.close()
  return True
  # tar.close()


# Performs all the functions required to download and install a package

# !!WARNING!! DO NOT USE THIS FUNCTION ON ITS OWN
# This does not install any deps required, so any package
# that has deps will break!! PLEASE USE installPackageAndDeps

# Takes Package name and returns True on success
def installPackage(pname):
  if pname == "":
    return
  #try:
  if getAndDecompress(pname):
    installFromTemp(pname)
    #except Exception as e:
    #print(f"Failed to install package. {e}")
    # addToInstalled(pname)
    addPathsToInstalled(pname)
    print(f"Installed {pname}")
    return True
  else:
    return False

# Uses installPackage to install a package and its deps
def installPackageAndDeps(pname):
  deps = getDeps(pname)

  # try:
  #   with open(f"{SYSROOT}etc/installedPackages", "r") as f:
  #     packages = f.readlines()
  #     f.close()
  # except FileNotFoundError:
  #   # System has not used LinPKG before, assume no installed packages
  #   print("No valid installedPackages list, assuming none.")
  #   packages = [""]

  packages = os.listdir(f"{SYSROOT}etc/linpkg")
  
  for i in range(len(packages)):
    packages[i] = packages[i].replace("\n", "")
  if deps is not None:
    for i in range(len(deps)):
      # print(packages)
      if not deps[i] + ".txt" in packages:
        installPackage(deps[i].replace("\n", ""))
      else:
        continue
  if not pname + ".txt" in packages:
    installPackage(pname)
    # cleanTemp()
  else:
    print(f"{pname} is already installed.")

  
def removePackage(pname):
  if not os.path.exists(f"{SYSROOT}etc/linpkg/{pname}.txt"):
    print("Package not installed.")
    return
  with open(f"{SYSROOT}etc/linpkg/{pname}.txt", "r") as f:
    lines = f.readlines()
  for i in range(len(lines)):
    noNewline = lines[i].replace('\n', '')
    os.remove(f"{SYSROOT}{noNewline}")
  # Read the file and store its lines in a list

  file_path = f"{SYSROOT}etc/linpkg/installedPackages"
  os.remove(f"{SYSROOT}etc/linpkg/{pname}.txt")
  
# installPackageAndDeps("neofetch")


# Command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--install", type=ascii,
                    help="install a package")
parser.add_argument("-r", "--remove", type=ascii,
                    help="remove a package")
args = parser.parse_args()

if args.install:
  installPackageAndDeps(args.install.replace("'", ""))
if args.remove:
  removePackage(args.remove.replace("'", ""))
if args.remove and args.install:
  print("Cannot install and remove at the same time, this isnt pacman :)")