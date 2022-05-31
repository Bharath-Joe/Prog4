from os.path import exists

BLOCKSIZE = 256
diskToFile = {} # disk number: [filename, status]
initialDiskNum = 0
nBytesArray = {}
    
def openDisk(filename, nBytes):
    global initialDiskNum
    if nBytes % BLOCKSIZE != 0 or nBytes < 0:
        print("Error")
        return -1
    if nBytes > 0 and exists(filename) == True:
        f = open(filename, "a")
        f.truncate(nBytes)
        for disk in diskToFile.keys():
            if diskToFile[disk][0] == filename:
                diskToFile[disk] = [filename, "opened"]
                nBytesArray[disk] = int(nBytes)
            return disk
    elif nBytes > 0 and exists(filename) == False:
        open(filename, "w")
        initialDiskNum += 1
        diskToFile[initialDiskNum] = [filename, "opened"]
        nBytesArray[initialDiskNum] = int(nBytes)
        return initialDiskNum
    elif nBytes == 0 and exists(filename) == False:
        print("Error")
        return -1
    elif nBytes == 0:
        open(filename, "r+")
        for disk in diskToFile.keys():
            if diskToFile[disk][0] == filename:
                return disk

def readBlock(disk, bNum, block):
    filename = diskToFile[disk][0]
    status = diskToFile[disk][1]
    numBytes = nBytesArray[disk]
    if disk in diskToFile.keys():
        if numBytes <= bNum * BLOCKSIZE:
            print("Error")
            return -1
        elif status == "opened":
            f = open(filename, "rb")
            f.seek(bNum * BLOCKSIZE)
            block = f.read(BLOCKSIZE)
            return 0, block
    print("Error in readBlock")
    return -1

def writeBlock(disk, bNum, block):
    filename = diskToFile[disk][0]
    status = diskToFile[disk][1]
    numBytes = nBytesArray[disk]
    if disk in diskToFile.keys():
        if numBytes <= bNum * BLOCKSIZE:
            print("Error")
            return -1
        if status == "opened":
            f = open(filename, "rb+")
            f.seek(bNum * BLOCKSIZE)
            f.write(block)
            f.close()
            return 0
    print("Error")
    return -1


def closeDisk(disk):
    diskToFile[disk][1] = "closed"
    return 0
