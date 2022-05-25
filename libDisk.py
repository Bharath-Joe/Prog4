from os.path import exists

from numpy import nbytes

BLOCKSIZE = 256
diskToFile = {} # disk number: [filename, status]
initialDiskNum = 0
nBytesArray = {}

def openDisk(filename, nBytes):
    if BLOCKSIZE % nBytes != 0 or nBytes < 0:
        print("Error")
        return -1
    if nBytes > 0:
        open(filename, "w")
        initialDiskNum += 1
        diskToFile[initialDiskNum] = [filename, "opened"]
        nBytesArray[initialDiskNum] = nBytes
        return 0
    elif nBytes == 0 and exists(filename) == False:
        print("Error")
        return -1
    elif nBytes == 0:
        open(filename, "w")
        return 0

def readBlock(disk, bNum, block):
    filename = diskToFile[disk][0]
    status = diskToFile[disk][0]
    nybtes = nBytesArray[disk]
    if disk in diskToFile.keys():
        if nybtes <= bNum * BLOCKSIZE:
            print("Error")
            return -1
        elif status == "opened":
            f = open(filename, "rb")
            f.seek(bNum * BLOCKSIZE)
            block = f.read(BLOCKSIZE) # when would the size of block be anything less than 256
            return 0, block
    print("Error")
    return -1

def writeBlock(disk, bNum, block):
    filename = diskToFile[disk][0]
    status = diskToFile[disk][0]
    nybtes = nBytesArray[disk]
    if disk in diskToFile.keys():
        if nybtes <= bNum * BLOCKSIZE:
            print("Error")
            return -1
        if status == "opened":
            f = open(filename, "wb")
            f.seek(bNum * BLOCKSIZE)
            f.write(block) # must write 256 bytes no matter the size of block ???
            return 0
    print("Error")
    return -1


def closeDisk(disk):
    diskToFile[disk][1] = "closed"
    return 0
