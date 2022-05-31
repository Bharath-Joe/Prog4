import os
from libDisk import openDisk, writeBlock
# The very first Inode block (from super block) needs to have an associated data block.
BLOCKSIZE = 256
DEFAULT_DISK_SIZE = 10240
DEFAULT_DISK_NAME = "tinyFSDisk"
currentDisks = {}    # mounted means it is 1 at index 1
fileDescriptor = 1
file_table = {}     # {fileDescriptor Number : fileName} 
filePointer_table = {} # {fileDescriptor Number: pointer in file}
free_blocks = {}    # {block # : 0 or 1} where 0 = not free / 1 free  
                    # ---- BitMap in the form of a dictionary
inode_blocks = {}   # {block # : data block #}
data_blocks = {}    # {block # : info} 


def main():
    tfs_mkfs(DEFAULT_DISK_NAME, DEFAULT_DISK_SIZE)
    tfs_mount(DEFAULT_DISK_NAME)
    fD = tfs_open("test1.txt")
    # fD2 = tfs_open("test2.txt")
    print(free_blocks)
    print(file_table)
    # print("Inode Block Number: Data Block Number")
    # print(inode_blocks)
    tfs_write(fD, "Hello World!", 12)
    # print(free_blocks)
    # print("Inode Block Number: Data Block Number")
    # print(inode_blocks)
    # tfs_delete(fD)
    # print("After deleting\n", free_blocks)
    # print(inode_blocks)
    # print(file_table)
    tfs_readByte(fD, "")
    tfs_readByte(fD, "")
    tfs_seek(fD, 11)
    print(tfs_readByte(fD, ""))
    tfs_unmount()


def writeSB(diskNum):
    block = b"S"
    if writeBlock(diskNum, 0, block) != -1:
        print("- Setting magic numbers")
        print("- Creating special Inode to track name-inode pairs")
        inodeBlock = b"I"
        writeBlock(diskNum, 1, inodeBlock)
        print("- Creating mechanism to manage free blocks")
        return 0
    else:
        print("Error")
        return -1

def FBSetUp(diskNum, nBytes):
    block = b"F"
    numberOfBlocks = int(nBytes / 256)
    free_blocks[1] = 0
    for i in range(512, nBytes, 256):
        free_blocks[i//256] = 1
    # starts at 2 because at 0 = superblock & 1 = special Inode Block
    for i in range(2, numberOfBlocks):
        writeBlock(diskNum, i, block)
    return 0

def tfs_mkfs(filename, nBytes):
    print("--- Creating empty TinyFS file system ---\n")
    diskNum = openDisk(filename, nBytes)
    if diskNum < 0:
        print("Error")
        return -1
    else:
        currentDisks[filename] = 0
        f = open(filename, "rb+")
        f.seek(0)
        print("- Initializing all data to 0x00")
        for i in range(nBytes):
            f.write(b"#")
        f.close()
        writeSB(diskNum)
        FBSetUp(diskNum, nBytes)
        return 0

def tfs_mount(filename):
    for item in currentDisks:
        if item == filename:
            currentDisks[item] = 1
        else:
            currentDisks[item] = 0
    print("\n--- Mounted TinyFS file system ---")
    return 0

def tfs_unmount():
    for item in currentDisks:
        if currentDisks[item] == 1:
             currentDisks[item] = 0
    file_table.clear()
    free_blocks.clear()
    inode_blocks.clear() 
    data_blocks.clear() 
    print("\n--- Unmounted TinyFS file system ---")
    return 0

def tfs_open(name):
    free = False
    global fileDescriptor
    fileDescriptor += 1
    # find free block in free_blocks and set that value
    file_table[fileDescriptor] = name
    f = open(name, "w+")
    for block in free_blocks.keys():
        if free_blocks[block] == 1:
            free_blocks[block] = 0
            inode_blocks[block] = None
            # create Inode number for file
            # write to Disk with "I" as first Byte
            writeBlock(1, block, b"I")
            filePointer_table[fileDescriptor] = 0
            free = True
            break
    if free == False:
        print("- Not enough blocks available to open file")
        return(-1)
    print("--- File successfully opened ---")
    return fileDescriptor

def tfs_close(fileDescriptor):
    return 0

def tfs_write(fileDescriptor, buffer, size):
    # CHANGE HERE!!! WHEN YOU WRITE A FILE WITH MORE THAN 256 BYTES, IT NEEDS A NEW DATA BLOCK
    if size == 0:
        print("- Size is 0, no data written to file")
        return 0
    elif size > 0:
        fileName = file_table[fileDescriptor]
        f = open(fileName, "r+")
        f.write(buffer)
        f.seek(0)
        for block in free_blocks.keys():
            if free_blocks[block] == 1:
                free_blocks[block] = 0
                inode_blocks[fileDescriptor] = block
                # create Inode number for file
                # write to Disk with "D" as first Byte
                # link InodeBlock to DataBlock
                writeBlock(1, block, b"D")
                filePointer_table[fileDescriptor] = 0
                free = True
                break
        if free == False:
            print("- Not enough blocks available to write to file")
            return(-1)
    print("--- Written to file successfully ---")
    return 0

def tfs_delete(fileDescriptor):
    fileName = file_table[fileDescriptor]
    # remove from our file_table
    # remove from our directory
    os.remove(fileName)
    # set the iNode Block to Free Block
    free_blocks[fileDescriptor] = 1
    writeBlock(1, fileDescriptor, b"F")
    dataBlockNumber = inode_blocks[fileDescriptor]
    writeBlock(1, dataBlockNumber, b"F")
    if dataBlockNumber is not None:
        free_blocks[dataBlockNumber] = 1

    # set the associated Data Block to Free Block
    del file_table[fileDescriptor]
    del inode_blocks[fileDescriptor]
    print("--- Deleted file successfuly ---")
    return 0

def tfs_readByte(fileDescriptor, buffer):
    fileName = file_table[fileDescriptor]
    f = open(fileName, "r")
    if filePointer_table[fileDescriptor] >= os.path.getsize(fileName):
        print("- File pointer is at the end of the file")
        return -1
    else:
        f.seek(filePointer_table[fileDescriptor])
        buffer = f.read(1)
        filePointer_table[fileDescriptor] += 1
    return buffer

def tfs_seek(fileDescriptor, offset):
    fileName = file_table[fileDescriptor]
    if offset > os.path.getsize(fileName):
        print("- Offset larger than file size")
        return -1
    filePointer_table[fileDescriptor] = offset
    print("--- Successfully seeked to offest in file ---")
    return 0

if __name__ == '__main__':
    main()
    