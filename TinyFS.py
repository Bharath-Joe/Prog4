from libDisk import openDisk, writeBlock

BLOCKSIZE = 256
DEFAULT_DISK_SIZE = 10240
DEFAULT_DISK_NAME = "tinyFSDisk"
currentDisks = {}    # mounted means it is 1 at index 1
fileDescriptor = 0
file_table = {}     # {fileDescriptor Number : fileName} 
free_blocks = {}    # {block # : 0 or 1} where 0 = not free / 1 free  
                    # ---- BitMap in the form of a dictionary
inode_blocks = {}   # {block # : [info], data block #}
data_blocks = {}    # {block # : info} 



def main():
    tfs_mkfs(DEFAULT_DISK_NAME, DEFAULT_DISK_SIZE)
    tfs_mount(DEFAULT_DISK_NAME)
    tfs_unmount()


def writeSB(diskNum):
    block = b"S"
    if writeBlock(diskNum, 0, block) != -1:
        print("- Setting magic numbers")
        print("- Creating special Inode to track name-inode pairs")
        print("- Creating mechanism to manage free blocks")
        return 0
    else:
        print("Error")
        return -1

def FBSetUp(diskNum, nBytes):
    block = b"F"
    numberOfBlocks = int(nBytes / 256)
    for i in range(256, nBytes, 256):
        free_blocks[i//256] = 1
    # starts at 1 because at 0 it is superblock
    for i in range(1, numberOfBlocks):
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
    # find free block in free_blocks and set that value
    # create Inode number for file
    # write to Disk with "I" as first Byte
    # find next available free block in free_block
    # write to Disk with "D" as first Byte
    # associate both the data and Inode
    # adds name of file to file_table and gives it a file descriptor
    # returns file descriptor
    return 0

def tfs_close(fileDescriptor):
    return 0

def tfs_write(fileDescriptor, buffer, size):
    return 0

def tfs_delete(fileDescriptor):
    return 0

def tfs_readByte(fileDescriptor, buffer):
    return 0

def tfs_seek(fileDescriptor, offset):
    return 0


if __name__ == '__main__':
    main()
    