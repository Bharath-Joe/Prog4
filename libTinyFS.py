import os
from libDisk import openDisk, readBlock, writeBlock
# The very first Inode block (from super block) needs to have an associated data block.

BLOCKSIZE = 256
DEFAULT_DISK_SIZE = 10240
DEFAULT_DISK_NAME = "tinyFSDisk"
currentDisks = {}    # mounted means it is 1 at index 1
fileDescriptor = 0
file_table = {}     # {fileDescriptor Number : fileName} 
closed_file_table = {} # {fileName : fileDescriptor Number}
filePointer_table = {} # {fileDescriptor Number: pointer in file}
free_blocks = {}    # {block # in disk : 0 or 1} where 0 = not free / 1 free  
                    # ---- BitMap in the form of a dictionary
inodeBlocks_to_dataBlocks = {}   # {block # : list of data block #s}
fileDescriptor_to_Inode = {}    # {fd : associated inode}
dataBlockSize = {}          #{block # : size}


def main():
    tfs_mkfs(DEFAULT_DISK_NAME, DEFAULT_DISK_SIZE)
    tfs_mount(DEFAULT_DISK_NAME)
    # print("Free Blocks:", free_blocks)
    # print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
    # print("File Table", file_table)
    # print("FD to Inode", fileDescriptor_to_Inode)
    # print("Data Block Sizes", dataBlockSize)
    # print("File Pointer Table:", filePointer_table)
    fd = tfs_open("random.txt")
    fd2 = tfs_open("random2.txt")
    fd3 = tfs_open("random3.txt")
    tfs_close(fd2)
    tfs_close(fd)
    fd = tfs_open("random.txt")
    tfs_write(fd, "YOLO", 4)
    print(tfs_readByte(fd, ""))
    tfs_delete(fd)
    # buff = "If you are working alone or with a partner, add TWO additional areas of functionality from the list below (30%). If you are working in a group of three, add THREE additional features. You are free to implement the features in your own way, so be creative, but feel free to do a little research, and base your design decisions on existing solutions. Fragmentation info and defragmentation"
    # tfs_write(fd, buff, 290)
    # tfs_write(fd2, "YOLO", 4)
    # tfs_readByte(fd2, "")
    # fd2 = tfs_open("random2.txt")
    # tfs_write(fd2, "YOLO", 4)
    # print(tfs_readByte(fd2, ""))
    # print("Free Blocks:", free_blocks)
    # print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
    # print("File Table", file_table)
    # print("FD to Inode", fileDescriptor_to_Inode)
    # print("Data Block Sizes", dataBlockSize)
    # print("File Pointer Table:", filePointer_table)
    # print("Closed File Table:", closed_file_table)



def writeSB(diskNum):
    block = b"S"
    if writeBlock(diskNum, 0, block) != -1:
        print("- Setting magic numbers")
        print("- Creating special Inode to track name-inode pairs")
        writeBlock(diskNum, 1, b"I")
        writeBlock(diskNum, 2, b"D")
        print("- Creating mechanism to manage free blocks")
        return 0
    else:
        print("Error")
        return -1

def FBSetUp(nBytes):
    free_blocks[1] = 0 # special Inode
    free_blocks[2] = 0 # datablock for special Inode
    inodeBlocks_to_dataBlocks[1] = 2
    for i in range(768, nBytes, 256):
        free_blocks[i//256] = 1
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
        FBSetUp(nBytes)
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
    inodeBlocks_to_dataBlocks.clear() 
    print("\n--- Unmounted TinyFS file system ---")
    return 0

def tfs_open(name):
    free = False
    global fileDescriptor
    if name in closed_file_table.keys():
        fD = closed_file_table[name]
        file_table[fD] = name
        del closed_file_table[name]
        return fD
    else:
        fileDescriptor += 1
    # find free block in free_blocks and set that value
    file_table[fileDescriptor] = name
    for block in free_blocks.keys():
        if free_blocks[block] == 1:
            free_blocks[block] = 0
            inodeBlocks_to_dataBlocks[block] = []
            fileDescriptor_to_Inode[fileDescriptor] = block
            # create Inode number for file
            # write to Disk with "I" as first Byte
            writeBlock(1, block, b"I")
            filePointer_table[fileDescriptor] = 0
            free = True
            break
    if free == False:
        print("- Not enough blocks available to open file")
        return(-1)
    print("\n--- File successfully opened ---")
    return fileDescriptor

def tfs_close(fileDescriptor):
    if fileDescriptor not in file_table.keys():
        print("Error, file descriptor not found.")
        return -1
    fileName = file_table[fileDescriptor]
    closed_file_table[fileName] = fileDescriptor
    del file_table[fileDescriptor]
    print("\n--- File successfully closed ---")
    return 0

def tfs_write(fileDescriptor, buffer, size):
    for fd in closed_file_table.values():
        if fd == fileDescriptor:
            print("Error, cannot write to a closed file.")
            return -1
    bufferItems = []
    if size == 0:
        print("- Size is 0, no data written to file")
        return 0
    else:
        myString = ""
        for i in range(len(buffer)):
            if i % 256 == 0 and i != 0:
                bufferItems.append(myString)
                myString = ""
            myString += buffer[i]
        bufferItems.append(myString)
        for item in bufferItems:
            for block in free_blocks.keys():
                if free_blocks[block] == 1:
                    free_blocks[block] = 0
                    inodeBlocks_to_dataBlocks[fileDescriptor_to_Inode[fileDescriptor]].append(block)
                    # create Inode number for file
                    # write to Disk with "D" as first Byte
                    # link InodeBlock to DataBlock
                    dataBlockSize[block] = len(item)
                    writeBlock(1, block, item.encode('utf-8'))
                    filePointer_table[fileDescriptor] = 0
                    free = True
                    break
        if free == False:
            print("- Not enough blocks available to write to file")
            return(-1)
    print("\n--- Written to file successfully ---")
    return 0

def tfs_delete(fileDescriptor):
    fileName = file_table[fileDescriptor]
    # remove from our file_table
    # set the iNode Block to Free Block
    free_blocks[fileDescriptor_to_Inode[fileDescriptor]] = 1
    for dataBlock in inodeBlocks_to_dataBlocks[fileDescriptor_to_Inode[fileDescriptor]]:
        writeBlock(1, dataBlock, b'#' * dataBlockSize[dataBlock])
        del dataBlockSize[dataBlock]
        free_blocks[dataBlock] = 1
    writeBlock(1, fileDescriptor_to_Inode[fileDescriptor], b"#")
    # delete data entry in disk HERE
    del inodeBlocks_to_dataBlocks[fileDescriptor_to_Inode[fileDescriptor]]
    del fileDescriptor_to_Inode[fileDescriptor]
    del filePointer_table[fileDescriptor]
    if fileDescriptor in file_table.keys():
        del file_table[fileDescriptor]
    else:
        del closed_file_table[fileName]
    print("\n--- Deleted file successfuly ---")
    return 0

def tfs_readByte(fileDescriptor, buffer):
    for fd in closed_file_table.values():
        if fd == fileDescriptor:
            print("Error, cannot read to a closed file.")
            return -1
    location = filePointer_table[fileDescriptor] % 256
    indexInDataBlock = filePointer_table[fileDescriptor] // 256
    dataBlockNum = inodeBlocks_to_dataBlocks[fileDescriptor_to_Inode[fileDescriptor]][indexInDataBlock]
    if location >= dataBlockSize[dataBlockNum]:
        print("Error, nothing else to read")
        return -1
    val, myBuffer = readBlock(1, dataBlockNum, buffer)
    filePointer_table[fileDescriptor] += 1
    print("\n--- Successfully read byte from file ---")
    return chr(myBuffer[location])

def tfs_seek(fileDescriptor, offset):
    size = 0
    for dataBlock in inodeBlocks_to_dataBlocks[fileDescriptor_to_Inode[fileDescriptor]]:
        size += dataBlockSize[dataBlock]
    print(size)
    filePointer_table[fileDescriptor] = offset
    if offset > size:
        print("Error, offset larger than file size")
        return -1
    filePointer_table[fileDescriptor] = offset
    print("\n--- Successfully seeked to offest in file ---")
    return 0

if __name__ == '__main__':
    main()
    