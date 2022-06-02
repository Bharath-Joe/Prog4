from asyncore import write
import os
from datetime import datetime
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
fd_to_time = {} # {fileDescriptor Number : [creation time, modification time, access time]}


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
        fd_to_time[fileDescriptor] = [-1, -1, -1]
    # find free block in free_blocks and set that value
    for block in free_blocks.keys():
        if free_blocks[block] == 1:
            free_blocks[block] = 0
            inodeBlocks_to_dataBlocks[block] = []
            fileDescriptor_to_Inode[fileDescriptor] = block
            # create Inode number for file
            # write to Disk with "I" as first Byte
            val, read_block = readBlock(1,1,"")
            buffer = ""
            for byte in read_block:
                if chr(byte) != "#":
                    buffer += chr(byte)
                else:
                    break
            buffer += name + " "
            writeBlock(1, block, b"I")
            now = datetime.now()
            dt_string = now.strftime(" %m/%d/%Y %H:%M:%S")
            fd_to_time[fileDescriptor][0] =  dt_string
            val2, read_block2 = readBlock(1,block,"")
            buffer2 = ""
            for byte in read_block2:
                if chr(byte) != "#":
                    buffer2 += chr(byte)
                else:
                    break
            buffer2 += dt_string
            writeBlock(1, block, buffer2.encode('utf-8'))
            writeBlock(1, 1, buffer.encode('utf-8'))
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
    inode = fileDescriptor_to_Inode[fileDescriptor]
    now = datetime.now()
    dt_string = now.strftime(" %m/%d/%Y %H:%M:%S")
    fd_to_time[fileDescriptor][1] = dt_string
    val, read_block = readBlock(1,inode,"")
    buffer2 = ""
    for byte in read_block:
        if chr(byte) != "#":
            buffer2 += chr(byte)
        else:
            break
    buffer2 += dt_string
    writeBlock(1, inode, buffer2.encode('utf-8'))
    
    print("\n--- Written '%s' to file %s successfully ---"%(buffer, file_table[fileDescriptor]))
    return 0

def tfs_delete(fileDescriptor):
    if fileDescriptor not in file_table.keys() and fileDescriptor not in closed_file_table.values():
        print("ERROR: File descriptor not found")
        return -1
    val, read_block = readBlock(1,1,"")
    deleted_file = ""
    if fileDescriptor in file_table.keys():
        deleted_file = file_table[fileDescriptor]
    elif fileDescriptor in closed_file_table.values():
        for filename in closed_file_table.keys():
            if closed_file_table[filename] == fileDescriptor:
                deleted_file = filename
                break
    str_read_block = ""
    for byte in read_block:
        str_read_block += chr(byte)
    str_read_block = str_read_block.replace(deleted_file + " ", len(deleted_file) * "#")
    writeBlock(1, 1, str_read_block.encode('utf-8'))
    myFileName = ""
    for name in closed_file_table.keys():
        if closed_file_table[name] == fileDescriptor:
            myFileName = name
    inode = fileDescriptor_to_Inode[fileDescriptor]
    writeBlock(1, inode, b"#" * 256)
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

    inode = fileDescriptor_to_Inode[fileDescriptor]
    now = datetime.now()
    dt_string = now.strftime(" %m/%d/%Y %H:%M:%S")
    val2, read_block2 = readBlock(1,inode,"")
    buffer2 = ""
    for byte in read_block2:
        if chr(byte) != "#":
            buffer2 += chr(byte)
        else:
            break
    buffer2 += dt_string
    writeBlock(1, inode, buffer2.encode('utf-8'))
    fd_to_time[fileDescriptor][2] = dt_string

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

# Optional Functionality B: ---------------------

#   tfs_rename -> renames a file
def tfs_rename(old_filename, new_filename):
    if old_filename in file_table.values(): # if old_filename is a current open file
        for fd in file_table.keys():
            if file_table[fd] == old_filename:
                file_table[fd] = new_filename # replace old filename with new filename at corresponding fd
                break
    elif old_filename in closed_file_table.keys(): # if old_filename is a closed file
        fd = closed_file_table[old_filename]
        del closed_file_table[old_filename] # delete old filename
        closed_file_table[new_filename] = fd # insert new filename with same fd as before
    else: # if old_filename does not exist on disk
        print("ERROR: file to rename does not exist")
        return -1

    val, read_block = readBlock(1,1,"")
    str_read_block = ""
    for byte in read_block:
        str_read_block += chr(byte)
    str_read_block = str_read_block.replace(old_filename, new_filename)
    writeBlock(1, 1, str_read_block.encode('utf-8'))
    return 0 # return 0 on success

#   tfs_readdir -> lists all files and directories on disk
def tfs_readdir():
    if len(file_table) == 0 and len(closed_file_table) == 0:
        print("No files or directories currently on disk")
    else:
        print("Directories on disk: root directory")
        print("Files on disk:")
        for filename in file_table.values(): # print all open files
            print(filename)
        for filename in closed_file_table.keys(): # print all closed files
            print(filename)

# End of Optional Functionality B: -----------------


# Optional Functionality E: ---------------------

#   tfs_stat(fileDescriptor) -> returns file creation time
def tfs_stat(fileDescriptor):
    print()
    print("Timestamps for fileDescriptor: ", fileDescriptor)
    print("Creation time:", fd_to_time[fileDescriptor][0])
    print("Modification time:", fd_to_time[fileDescriptor][1])
    print("Access time:", fd_to_time[fileDescriptor][2])

# End of Optional Functionality E: -----------------