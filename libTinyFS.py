import os
from libDisk import closeDisk, openDisk, readBlock, writeBlock, diskToFile
# The very first Inode block (from super block) needs to have an associated data block.

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
        print("ERROR: Cannot create initialize superblock")
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
        print("ERROR: Cannot create TinyFS file system")
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
             for diskNum in diskToFile.keys():
                 if diskToFile[diskNum][0] == item:
                    closeDisk(diskNum)
    file_table.clear()
    free_blocks.clear()
    inodeBlocks_to_dataBlocks.clear() 
    fileDescriptor_to_Inode.clear()
    closed_file_table.clear()
    dataBlockSize.clear()
    filePointer_table.clear()  
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
        print("ERROR: Not enough blocks available to open file")
        return(-1)
    file_table[fileDescriptor] = name
    print("\n--- File %s successfully opened ---"%(file_table[fileDescriptor]))
    return fileDescriptor

def tfs_close(fileDescriptor):
    if fileDescriptor not in file_table.keys():
        print("ERROR: File descriptor not found")
        return -1
    fileName = file_table[fileDescriptor]
    closed_file_table[fileName] = fileDescriptor
    print("\n--- File %s successfully closed ---"%(file_table[fileDescriptor]))
    del file_table[fileDescriptor]
    return 0

def tfs_write(fileDescriptor, buffer, size):
    for fd in closed_file_table.values():
        if fd == fileDescriptor:
            print("ERROR: Cannot write to a closed file")
            return -1
    if fileDescriptor not in file_table.keys():
        print("ERROR: File descriptor not found")
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
            print("ERROR: Not enough blocks available to write to file")
            return(-1)
    print("\n--- Written '%s' to file %s successfully ---"%(buffer, file_table[fileDescriptor]))
    return 0

def tfs_delete(fileDescriptor):
    if fileDescriptor not in file_table.keys() and fileDescriptor not in closed_file_table.values():
        print("ERROR: File descriptor not found")
        return -1
    myFileName = ""
    for name in closed_file_table.keys():
        if closed_file_table[name] == fileDescriptor:
            myFileName = name
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
        print("\n--- Deleted %s file successfuly ---"%(file_table[fileDescriptor]))
        del file_table[fileDescriptor]
    elif fileDescriptor in closed_file_table.values():
        print("\n--- Deleted %s file successfuly ---"%(myFileName))
        del closed_file_table[myFileName]
    return 0

def tfs_readByte(fileDescriptor, buffer):
    for fd in closed_file_table.values():
        if fd == fileDescriptor:
            print("ERROR: Cannot read to a closed file.")
            return -1
    location = filePointer_table[fileDescriptor] % 256
    indexInDataBlock = filePointer_table[fileDescriptor] // 256
    dataBlockNum = inodeBlocks_to_dataBlocks[fileDescriptor_to_Inode[fileDescriptor]][indexInDataBlock]
    if location >= dataBlockSize[dataBlockNum]:
        print("ERROR: Nothing else to read")
        return -1
    val, myBuffer = readBlock(1, dataBlockNum, buffer)
    filePointer_table[fileDescriptor] += 1
    print("\n--- Successfully read byte from %s file ---"%(file_table[fileDescriptor]))
    print("- Byte read:", chr(myBuffer[location]))
    return chr(myBuffer[location])

def tfs_seek(fileDescriptor, offset):
    size = 0
    for dataBlock in inodeBlocks_to_dataBlocks[fileDescriptor_to_Inode[fileDescriptor]]:
        size += dataBlockSize[dataBlock]
    filePointer_table[fileDescriptor] = offset
    if offset > size:
        print("ERROR: Offset larger than file size")
        return -1
    filePointer_table[fileDescriptor] = offset
    print("\n--- Successfully seeked to offest in %s file ---"%(file_table[fileDescriptor]))
    return 0
