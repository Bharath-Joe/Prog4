from time import sleep
from libTinyFS import tfs_mkfs, tfs_delete, tfs_close, tfs_mount, tfs_open, tfs_readByte, tfs_seek, tfs_unmount, tfs_write, tfs_readdir, tfs_rename, tfs_stat
from libTinyFS import file_table , closed_file_table, filePointer_table, free_blocks, inodeBlocks_to_dataBlocks, fileDescriptor_to_Inode, dataBlockSize
BLOCKSIZE = 256
DEFAULT_DISK_SIZE = 10240
DEFAULT_DISK_NAME = "tinyFSDisk"

# For video:

# Demo 1: mkfs, mount, open, write, seek, read (Overall), close, delete
# Talk about how blocks are organized
# Inodes are being accessed through direct indexing, the inodes include a mechanism to index the datablock
# Free Blocks are being managed through a Bit Map in the form of a dict 
# def main():
#     tfs_mkfs(DEFAULT_DISK_NAME, DEFAULT_DISK_SIZE)
#     tfs_mount(DEFAULT_DISK_NAME)
#     print("-----------------------------------Info to Demo-----------------------------------")
#     print("Free Blocks:", free_blocks)
#     print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
#     print("File Table", file_table)
#     print("FD to Inode", fileDescriptor_to_Inode)
#     print("Data Block Sizes", dataBlockSize)
#     print("File Pointer Table:", filePointer_table)
#     print("Closed File Table:", closed_file_table)
#     print("----------------------------------------------------------------------------------")
#     fd = tfs_open("random.txt")
#     print("-----------------------------------Info to Demo-----------------------------------")
#     print("Free Blocks:", free_blocks)
#     print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
#     print("File Table", file_table)
#     print("FD to Inode", fileDescriptor_to_Inode)
#     print("Data Block Sizes", dataBlockSize)
#     print("File Pointer Table:", filePointer_table)
#     print("Closed File Table:", closed_file_table)
#     print("----------------------------------------------------------------------------------")
#     fd2 = tfs_open("random2.txt")
#     fd3 = tfs_open("random3.txt")
#     print("-----------------------------------Info to Demo-----------------------------------")
#     print("Free Blocks:", free_blocks)
#     print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
#     print("File Table", file_table)
#     print("FD to Inode", fileDescriptor_to_Inode)
#     print("Data Block Sizes", dataBlockSize)
#     print("File Pointer Table:", filePointer_table)
#     print("Closed File Table:", closed_file_table)
#     print("----------------------------------------------------------------------------------")
#     randomBuffer = "If you are working alone or with a partner, add TWO additional areas of functionality from the list below (30%). If you are working in a group of three, add THREE additional features. You are free to implement the features in your own way, so be creative, but feel free to do a little research, and base your design decisions on existing solutions. Fragmentation info and defragmentation"
#     tfs_write(fd, randomBuffer, 387)
#     print("-----------------------------------Info to Demo-----------------------------------")
#     print("Free Blocks:", free_blocks)
#     print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
#     print("File Table", file_table)
#     print("FD to Inode", fileDescriptor_to_Inode)
#     print("Data Block Sizes", dataBlockSize)
#     print("File Pointer Table:", filePointer_table)
#     print("Closed File Table:", closed_file_table)
#     print("----------------------------------------------------------------------------------")
#     tfs_seek(fd, 300)
#     print("-----------------------------------Info to Demo-----------------------------------")
#     print("Free Blocks:", free_blocks)
#     print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
#     print("File Table", file_table)
#     print("FD to Inode", fileDescriptor_to_Inode)
#     print("Data Block Sizes", dataBlockSize)
#     print("File Pointer Table:", filePointer_table)
#     print("Closed File Table:", closed_file_table)
#     print("----------------------------------------------------------------------------------")
#     tfs_readByte(fd, "")
#     tfs_readByte(fd, "")
#     print("-----------------------------------Info to Demo-----------------------------------")
#     print("Free Blocks:", free_blocks)
#     print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
#     print("File Table", file_table)
#     print("FD to Inode", fileDescriptor_to_Inode)
#     print("Data Block Sizes", dataBlockSize)
#     print("File Pointer Table:", filePointer_table)
#     print("Closed File Table:", closed_file_table)
#     print("----------------------------------------------------------------------------------")
#     tfs_close(fd3)
#     print("-----------------------------------Info to Demo-----------------------------------")
#     print("Free Blocks:", free_blocks)
#     print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
#     print("File Table", file_table)
#     print("FD to Inode", fileDescriptor_to_Inode)
#     print("Data Block Sizes", dataBlockSize)
#     print("File Pointer Table:", filePointer_table)
#     print("Closed File Table:", closed_file_table)
#     print("----------------------------------------------------------------------------------")
#     tfs_delete(fd3)
#     print("-----------------------------------Info to Demo-----------------------------------")
#     print("Free Blocks:", free_blocks)
#     print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
#     print("File Table", file_table)
#     print("FD to Inode", fileDescriptor_to_Inode)
#     print("Data Block Sizes", dataBlockSize)
#     print("File Pointer Table:", filePointer_table)
#     print("Closed File Table:", closed_file_table)
#     print("----------------------------------------------------------------------------------")
    
# Demo 2: Cannot do anything after unmount or closing a file
# def main():
#     tfs_mkfs(DEFAULT_DISK_NAME, DEFAULT_DISK_SIZE)
#     tfs_mount(DEFAULT_DISK_NAME)
#     print("-----------------------------------Info to Demo-----------------------------------")
#     print("Free Blocks:", free_blocks)
#     print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
#     print("File Table", file_table)
#     print("FD to Inode", fileDescriptor_to_Inode)
#     print("Data Block Sizes", dataBlockSize)
#     print("File Pointer Table:", filePointer_table)
#     print("Closed File Table:", closed_file_table)
#     fd = tfs_open("random.txt")
#     print("-----------------------------------Info to Demo-----------------------------------")
#     print("Free Blocks:", free_blocks)
#     print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
#     print("File Table", file_table)
#     print("FD to Inode", fileDescriptor_to_Inode)
#     print("Data Block Sizes", dataBlockSize)
#     print("File Pointer Table:", filePointer_table)
#     print("Closed File Table:", closed_file_table)
#     tfs_close(fd)
#     print("-----------------------------------Info to Demo-----------------------------------")
#     print("Free Blocks:", free_blocks)
#     print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
#     print("File Table", file_table)
#     print("FD to Inode", fileDescriptor_to_Inode)
#     print("Data Block Sizes", dataBlockSize)
#     print("File Pointer Table:", filePointer_table)
#     print("Closed File Table:", closed_file_table)
#     print("----------------------------------------------------------------------------------")
#     tfs_write(fd, "hello", 5) # should give an error
#     tfs_unmount()
#     print("-----------------------------------Info to Demo-----------------------------------")
#     print("Free Blocks:", free_blocks)
#     print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
#     print("File Table", file_table)
#     print("FD to Inode", fileDescriptor_to_Inode)
#     print("Data Block Sizes", dataBlockSize)
#     print("File Pointer Table:", filePointer_table)
#     print("Closed File Table:", closed_file_table)
#     print("----------------------------------------------------------------------------------")
#     fd = tfs_open("random.txt")
#     randomBuffer = "If you are working alone or with a partner, add TWO additional areas of functionality from the list below (30%). If you are working in a group of three, add THREE additional features. You are free to implement the features in your own way, so be creative, but feel free to do a little research, and base your design decisions on existing solutions. Fragmentation info and defragmentation"
#     tfs_write(fd, randomBuffer, 387)
#     print("-----------------------------------Info to Demo-----------------------------------")
#     print("Free Blocks:", free_blocks)
#     print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
#     print("File Table", file_table)
#     print("FD to Inode", fileDescriptor_to_Inode)
#     print("Data Block Sizes", dataBlockSize)
#     print("File Pointer Table:", filePointer_table)
#     print("Closed File Table:", closed_file_table)
#     print("----------------------------------------------------------------------------------")

# Demo 3: Deleting a file after a write, removes Inode and Data blocks from disk
# and sets them as free (Show tinyFSDisk)
# def main():
#     tfs_mkfs(DEFAULT_DISK_NAME, DEFAULT_DISK_SIZE)
#     tfs_mount(DEFAULT_DISK_NAME)
#     print("-----------------------------------Info to Demo-----------------------------------")
#     print("Free Blocks:", free_blocks)
#     print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
#     print("File Table", file_table)
#     print("FD to Inode", fileDescriptor_to_Inode)
#     print("Data Block Sizes", dataBlockSize)
#     print("File Pointer Table:", filePointer_table)
#     print("Closed File Table:", closed_file_table)
#     print("----------------------------------------------------------------------------------")
#     fd = tfs_open("random.txt")
#     print("-----------------------------------Info to Demo-----------------------------------")
#     print("Free Blocks:", free_blocks)
#     print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
#     print("File Table", file_table)
#     print("FD to Inode", fileDescriptor_to_Inode)
#     print("Data Block Sizes", dataBlockSize)
#     print("File Pointer Table:", filePointer_table)
#     print("Closed File Table:", closed_file_table)
#     print("----------------------------------------------------------------------------------")
#     fd2 = tfs_open("random2.txt")
#     fd3 = tfs_open("random3.txt")
#     print("-----------------------------------Info to Demo-----------------------------------")
#     print("Free Blocks:", free_blocks)
#     print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
#     print("File Table", file_table)
#     print("FD to Inode", fileDescriptor_to_Inode)
#     print("Data Block Sizes", dataBlockSize)
#     print("File Pointer Table:", filePointer_table)
#     print("Closed File Table:", closed_file_table)
#     print("----------------------------------------------------------------------------------")
#     randomBuffer = "If you are working alone or with a partner, add TWO additional areas of functionality from the list below (30%). If you are working in a group of three, add THREE additional features. You are free to implement the features in your own way, so be creative, but feel free to do a little research, and base your design decisions on existing solutions. Fragmentation info and defragmentation"
#     tfs_write(fd3, randomBuffer, 387)
#     print("-----------------------------------Info to Demo-----------------------------------")
#     print("Free Blocks:", free_blocks)
#     print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
#     print("File Table", file_table)
#     print("FD to Inode", fileDescriptor_to_Inode)
#     print("Data Block Sizes", dataBlockSize)
#     print("File Pointer Table:", filePointer_table)
#     print("Closed File Table:", closed_file_table)
#     print("----------------------------------------------------------------------------------")
#     tfs_delete(fd3)
#     print("-----------------------------------Info to Demo-----------------------------------")
#     print("Free Blocks:", free_blocks)
#     print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
#     print("File Table", file_table)
#     print("FD to Inode", fileDescriptor_to_Inode)
#     print("Data Block Sizes", dataBlockSize)
#     print("File Pointer Table:", filePointer_table)
#     print("Closed File Table:", closed_file_table)
#     print("----------------------------------------------------------------------------------")

# Demo 4: Additional Features
def main():
    tfs_mkfs(DEFAULT_DISK_NAME, DEFAULT_DISK_SIZE)
    tfs_mount(DEFAULT_DISK_NAME)
    print("-----------------------------------Info to Demo-----------------------------------")
    print("Free Blocks:", free_blocks)
    print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
    print("File Table", file_table)
    print("FD to Inode", fileDescriptor_to_Inode)
    print("Data Block Sizes", dataBlockSize)
    print("File Pointer Table:", filePointer_table)
    print("Closed File Table:", closed_file_table)
    print("----------------------------------------------------------------------------------")
    fd = tfs_open("random.txt")
    print("-----------------------------------Info to Demo-----------------------------------")
    print("Free Blocks:", free_blocks)
    print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
    print("File Table", file_table)
    print("FD to Inode", fileDescriptor_to_Inode)
    print("Data Block Sizes", dataBlockSize)
    print("File Pointer Table:", filePointer_table)
    print("Closed File Table:", closed_file_table)
    print("----------------------------------------------------------------------------------")
    fd2 = tfs_open("random2.txt")
    fd3 = tfs_open("random3.txt")
    print("-----------------------------------Info to Demo-----------------------------------")
    print("Free Blocks:", free_blocks)
    print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
    print("File Table", file_table)
    print("FD to Inode", fileDescriptor_to_Inode)
    print("Data Block Sizes", dataBlockSize)
    print("File Pointer Table:", filePointer_table)
    print("Closed File Table:", closed_file_table)
    print("----------------------------------------------------------------------------------")
    randomBuffer = "If you are working alone or with a partner, add TWO additional areas of functionality from the list below (30%). If you are working in a group of three, add THREE additional features. You are free to implement the features in your own way, so be creative, but feel free to do a little research, and base your design decisions on existing solutions. Fragmentation info and defragmentation"
    sleep(1)
    tfs_write(fd, randomBuffer, 387)
    print("-----------------------------------Info to Demo-----------------------------------")
    print("Free Blocks:", free_blocks)
    print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
    print("File Table", file_table)
    print("FD to Inode", fileDescriptor_to_Inode)
    print("Data Block Sizes", dataBlockSize)
    print("File Pointer Table:", filePointer_table)
    print("Closed File Table:", closed_file_table)
    print("----------------------------------------------------------------------------------")
    sleep(1)
    tfs_readByte(fd, "")
    tfs_close(fd3)
    print("-----------------------------------Info to Demo-----------------------------------")
    print("Free Blocks:", free_blocks)
    print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
    print("File Table", file_table)
    print("FD to Inode", fileDescriptor_to_Inode)
    print("Data Block Sizes", dataBlockSize)
    print("File Pointer Table:", filePointer_table)
    print("Closed File Table:", closed_file_table)
    print("----------------------------------------------------------------------------------")
    tfs_readdir()
    tfs_delete(fd3)
    print("-----------------------------------Info to Demo-----------------------------------")
    print("Free Blocks:", free_blocks)
    print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
    print("File Table", file_table)
    print("FD to Inode", fileDescriptor_to_Inode)
    print("Data Block Sizes", dataBlockSize)
    print("File Pointer Table:", filePointer_table)
    print("Closed File Table:", closed_file_table)
    print("----------------------------------------------------------------------------------")
    tfs_readdir()
    tfs_rename("random2.txt", "renamed.txt")
    print("-----------------------------------Info to Demo-----------------------------------")
    print("Free Blocks:", free_blocks)
    print("Inodes to data blocks", inodeBlocks_to_dataBlocks)
    print("File Table", file_table)
    print("FD to Inode", fileDescriptor_to_Inode)
    print("Data Block Sizes", dataBlockSize)
    print("File Pointer Table:", filePointer_table)
    print("Closed File Table:", closed_file_table)
    print("----------------------------------------------------------------------------------")
    tfs_readdir()
    tfs_stat(fd)


if __name__ == '__main__':
    main()
    