### Grupo: SO-TI-12
### Aluno 1: Renato Pereira (fc52599)
### Aluno 2: Duarte Fernandes (fc55327)
### Aluno 3: Duarte Miranda (fc58631)


##############################################################################################################################
########################################################## Imports ###########################################################
##############################################################################################################################

import queue
import sys, os, signal, time, math
from multiprocessing import Process, Value, Lock, active_children, Queue, Manager, Array
from threading import Timer

##############################################################################################################################
###################################################### GLOBAL VARIABLES ######################################################
##############################################################################################################################

start = time.perf_counter()     # stores the moment where the program was started
programName = sys.argv[0]       # stores the program's name
arguments = sys.argv[1:]        # stores the arguments passed onto the program

c = 0						    # controls whether -c option was called
l = 0						    # controls whether -l option was called
n = 0						    # stores the value associated with -p option
k = None					    # controls whether -e option was called and stores the value associated with it
wordToFind = None			    # stores the word the program must search for
filesToSearch = []              # stores the names of the files in which the program must search
filesToSearchE = []
filesToSearchSize = []	        # stores the names of the files in which the program must search and their respective byte size
filesByProcess = []             # stores lists that contain the files that each process must search in
sumOptionC = Value('i', 0)	    # stores the total number of occurrences of the word
sumOptionL = Value('i', 0)	    # stores the total number of lines in which the word was found
processes = []				    # stores all processes created by the program
workBlocks = Queue()            # stores all the work blocks in which the processes will search
finishedFiles = Value('i', 0)
ongoingFiles = Value('i', 0)
lock = Lock()                   # controlls process execution in critical sections
finished = 1

sharedLines = sharedLines = Manager().list()

arrayFiles = None
arrayFilesInfo = None
fileBlocks = Queue()
filesDic = dict()
ended = Value('i',1)

##############################################################################################################################
##################################################### ARGUMENT HANDLING ######################################################
##############################################################################################################################

"""
processArgs takes a list with all arguments passed onto 
pgrepwc command on the command line and updates the value 
of the global variables that represent the different 
options of that command accordingly.

Arguments:
    > args- List with all the arguments passed onto 
			pgrepwc command on the command line.
"""
def processArgs(args):
    global c, l, n, k, filesToSearchSize, wordToFind, filesToSearchE

    i = 0
    while i < len(args):
        if args[i] == "-c":
            c = 1
        elif args[i] == "-l":
            l = 1
        elif args[i] == "-p":
            try:
                i += 1
                n = int(args[i])
                if n < 0:
                    n = 0
            except:
                n = 0
        elif args[i] == "-e":
            try:
                i += 1
                k = int(args[i])
                if k < 0:
                    k = 0
            except:
                k = 0
        elif "." in args[i]:
            try:
                filesToSearchE.append(args[i])
                filesToSearchSize.append((args[i], os.path.getsize(args[i])))
            except:
                pass
        else:
            wordToFind = args[i]
        i += 1

##############################################################################################################################
################################################# PROCESS HANDLING ###########################################################
##############################################################################################################################

"""
createprocesses handles process creation when '-e' option is 
not specified. It creates at most as many processes as there 
are files, then it distributes the files as evenly as 
possible among all processes.

Arguments:
    > nrprocesses- Number of processes to be created.
	> nrFiles- Number of files to search in.
	> word- Word to be searched for.
"""
def createProcesses(nrProcesses, nrFiles, word):
    global filesToSearchSize, filesByProcess
    if nrProcesses > nrFiles:
        nrProcesses = nrFiles
    sortFiles(filesToSearchSize)
    distributeFiles(nrProcesses)

    for i in range(nrProcesses):
        filesToProcess = []
        for tuplo in filesByProcess[i]:
            filesToProcess.append(tuplo[0])
        processes.append(Process(target=searchInFile, args=(word, filesToProcess,)))


"""
startProcesses starts all processes stored in the global 
variable 'processes'.
"""
def startProcesses():
    for process in processes:
        process.start()


"""
joinProcesses joins all processes stored in the global 
variable 'processes'.
"""
def joinProcesses():
    for process in processes:
        process.join()

def interruptProcessing(sig, NULL):
    activeProcesses = active_children()
    if k != None:
        smallestPid = math.inf
        for process in activeProcesses:
            if process.pid < smallestPid:
                smallestPid = process.pid
            process.kill()
        smallestPid -= 1
        printResults(wordToFind, [file[0] for file in filesToSearchSize])
        os.kill(smallestPid, signal.SIGTERM)
    else:
        global finished
        finished = 0
        for process in activeProcesses:
            process.kill()
        print()

signal.signal(signal.SIGINT, interruptProcessing)

##############################################################################################################################
################################################# SEARCH FUNCTIONS ###########################################################
##############################################################################################################################

"""
searchInFile handles process search when '-e' option is not 
specified. It searches for the word in the given files.

Arguments:
    > word- Word to be searched for.
	> files- Files to search in
"""
def searchInFile(word, files):
    global sumOptionC, sumOptionL, finishedFiles, ongoingFiles, sharedLines

    for file in files:
        lineIndex = 0
        with open(file) as reader:
            lock.acquire()
            ongoingFiles.value += 1
            lock.release()
            for line in reader:
                increment = line.count(word)
                if increment:
                    lock.acquire()
                    sharedLines.append(f"{lineIndex}: {line}")
                    sumOptionC.value += increment
                    sumOptionL.value += 1
                    lock.release()
                lineIndex += 1
            lock.acquire()
            finishedFiles.value += 1
            ongoingFiles.value -= 1 
            lock.release()

##############################################################################################################################
################################################# SPECIAL process SEARCH ######################################################
##############################################################################################################################

"""
createprocessesSpecial handles process creation when '-e' 
option is specified. It creates at most as many processes as 
there are lines in the given file, then it distributes the 
lines as evenly as possible among all processes.

Arguments:
    > nrprocesses- Number of processes to be created.
	> file- File to search in.
	> word- Word to be searched for.
"""
def createprocessesSpecial(nrprocesses, word):

    global arrayFiles,arrayFilesInfo, filesToSearchE, processes

    arrayFiles = Array('i', len(filesToSearchE))
    for i in range(len(filesToSearchE)):
        arrayFiles[i] = i + 1
    arrayFilesInfo = Array('i', len(filesToSearchE)*2)

    for _ in range(nrprocesses):
        processes.append(Process(target=processesearchSpecial, 
        args=(word,)))


"""
processesearchSpecial handles process search when '-e' option 
is specified. It searches for the word in the lines 
between index 'start' and 'end' of certain file.

Arguments:
    > word- Word to be searched for.
	> lines- List containing all lines of the file.
	> start- Index of the first line to search in.
	> end- Index of the last line to search in.
"""

def processesearchSpecial(word):
    Terminate = False
    while not Terminate:
        try:

            nrOcorrences = 0
            idx = fileBlocks.get(False)

            if idx == None:
                Terminate = True
                os.system("kill -9 " + str(os.getpid()))
                break

            #---------------------------------------
            for i in idx:
                line = i[1]
                file = i[0]

                nrOcorrences = line.count(word)

                if nrOcorrences:
                    lock.acquire()
                    sharedLines.append(f"{filesDic[file]}: {line}")
                    arrayFilesInfo[file - 1] += nrOcorrences
                    arrayFilesInfo[file] += 1
                    lock.release()
            #---------------------------------------
        except queue.Empty:
            pass
        

##############################################################################################################################
################################################### OPTION E #################################################################
##############################################################################################################################

def eDiv(files, k):
    global n
    lx = []
    lxBytesLeft = []
    index = 1
    idx = 0
    i = 0
    idxLine = 0
    found = False
    for file in files:
        with open(file) as f:
            for line in f:
                idxLine += 1
                found = False

                lineSize = len(line)
                firstLine = (index, line, lineSize)
                firstCheck = sizeCheck(lxBytesLeft, firstLine[2])

                if firstCheck[0]:
                    lx[firstCheck[1]].append(firstLine)
                    lxBytesLeft[firstCheck[1]] -= firstLine[2]

                else:
                    lx.append([firstLine])
                    lxBytesLeft.append(k - firstLine[2])


                tam = len(lxBytesLeft)
                x = tam//2
                middle = math.ceil((tam - 1)/2)

                for i in range(x):
                    if lxBytesLeft[i] <= 0:
                        idx = i
                        found = True
                        break

                    if lxBytesLeft[(tam-i) - 1] <= 0:
                        idx = (tam-i) -1
                        found = True
                        break

                if lxBytesLeft != []:
                    if lxBytesLeft[middle] <= 0:
                        idx = middle
                        found = True
                
                if found or x >= 200:
                    if x >= 200:
                        idx = 0
                    
                    fileBlocks.put(lx[idx],block=False)

                    del lx[idx]
                    del lxBytesLeft[idx]

    for i in lx:
        fileBlocks.put(i, block=False)

    for i in range(n):
        fileBlocks.put(None)

def sizeCheck(lx, size):

    indexSave = 0
    first = True


    lenLx = len(lx)
    lenLxDiv = lenLx//2
    if lenLxDiv == 0:
        lenLxDiv = lenLx
    idx = 0
    middle = math.ceil((lenLx - 1)/2)

    for i in range(lenLxDiv):
        if lx[i] - size > 0 and first:
            indexSave = i
            first = False

        elif lx[i] - size == 0:
            return (True, i, lenLx)

        if lx[(lenLx - i) -1] - size == 0:
            return (True, (lenLx-i)-1, lenLx)
        idx += 1

    if lx != []:
        if lx[middle] - size == 0:
            return (True, idx+1, lenLx)

    if not first:
        return(True, indexSave, lenLx)
    
    return (False, "",lenLx)

##############################################################################################################################
################################################# PRINT FUNCTIONS ############################################################
##############################################################################################################################

"""
printResults prints a table that informs the user about 
the word that was searched, the files in which it was 
searched and the results associated with the '-c' and/or 
'-l' options, if used.
"""
def printResults(word, files):
    if not(c or l):
        return
    if k != None:
        for i in arrayFiles:
            posInfo = []
            maxPosition = (i*2) - 1
            posInfo.append(maxPosition - 1)
            posInfo.append(maxPosition)
            print("############### Search Results ###############")
            print("Option e print")
            print(f"Word = {word}")
            print(f"Files = {filesDic[i]}")
            print("----------------------------------------------")
            if c:
                print(f"Number of occurences of the word: ", arrayFilesInfo[posInfo[0]])
            if l:
                print(f"Number of lines containing the word: ", arrayFilesInfo[posInfo[1]])
            elapsedTime = (time.perf_counter() - start) * 10**6
            print(f"Time elapsed: {elapsedTime:.03f} ms")
            print("##############################################\n")
    else:
        print("############### Search Results ###############")
        print(f"Word = {word}")
        print(f"Files = {files}")
        print("----------------------------------------------")
        if c:
            print(f"Number of occurences of the word: ", sumOptionC.value)
        if l:
            print(f"Number of lines containing the word: ", sumOptionL.value)
        elapsedTime = (time.perf_counter() - start) * 10**6
        print(f"Time elapsed: {elapsedTime:.03f} ms")
        print("##############################################")



def printPartialResults():
    global sumOptionC, sumOptionL, finishedFiles, sharedLines, arrayFiles, filesDic, arrayFilesInfo

    if k != None:
        print("############## Partial Results ###############")
        for i in arrayFiles:
            posInfo = []
            maxPosition = (i*2) - 1
            posInfo.append(maxPosition - 1)
            posInfo.append(maxPosition)
            print("File: ", filesDic[i])
            if c:
                print("nrOcurrences: ", arrayFilesInfo[posInfo[0]])
            if l:
                print("nrLines: ", arrayFilesInfo[posInfo[1]])
            elapsedTime = (time.perf_counter() - start) * 10**6
            print(f"Time elapsed: {elapsedTime:.03f} ms")
        print("##############################################\n")
    else:
        print("############## Partial Results ###############")
        if c:
            print("nrOcurrences: ", sumOptionC.value)
        if l:
            print("nrLines: ", sumOptionL.value)
        print("Finished files: ", finishedFiles.value)
        print("Ongoing files: ", ongoingFiles.value)
        elapsedTime = (time.perf_counter() - start) * 10**6
        print(f"Time elapsed: {elapsedTime:.03f} ms")
        print("##############################################\n")

class RepeatFunction(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

timer = RepeatFunction(3, printPartialResults)

##############################################################################################################################
################################################# OTHER FUNCTIONS ############################################################
##############################################################################################################################

"""
readFiles continously asks the user for file names and 
stores said names in the global variable 'filesToSearch'.
"""
def readFiles():
    while 1:
        file = input("Name of the file to search in: ")
        if file:
            if "." in file:
                try:
                    filesToSearchSize.append((file, os.path.getsize(file)))
                except:
                    print("File not found!")
            else:
                print("Invalid file!")
            continue
        break

def distributeFiles(n):
    global filesByProcess

    for i in range(len(filesToSearchSize)):
        if i < n:
            filesByProcess.append([filesToSearchSize[i]])
        else:
            lowestByteSublist = 0                   #   index of the sublist with the lowest sum of total file size
            lowestByteNbr = math.inf                #   lowest number of bytes found on a sublist yet
            for sublist in filesByProcess:          #   each sublist stores the files to be searched for a determined process
                byteNbr = 0                         #   number of bytes summed from the files found on this sublist
                for nameAndSize in sublist:         #   nameAndSize is a tuple that stores the name and size of the file
                    byteNbr += nameAndSize[1]       #   like so:    (filename.txt, 1000)
                if (byteNbr < lowestByteNbr):
                    lowestByteNbr = byteNbr
                    lowestByteSublist = filesByProcess.index(sublist)
            filesByProcess[lowestByteSublist].append(filesToSearchSize[i])

def sortFiles(fileList):
    fileList.sort(key=lambda x: x[1], reverse=True)

##############################################################################################################################
####################################################### MAIN METHOD ##########################################################
##############################################################################################################################

"""
main orquestrates the whole program, it first handles the 
arguments passed through the command line, then it creates 
the amount of processes specified, or not, then it runs and 
joins the processes and finnaly it prints the results.

Arguments:
    > args- List with all the arguments passed onto 
			pgrepwc command on the command line.
"""
def main(args):
    global start,filesToSearchE

    print('Programa: ', programName)
    print('Argumentos: ', args, '\n')
    
    processArgs(arguments)
    if wordToFind == None:
        print("A word must be given as an argument")
        return
    if not filesToSearchSize:
        readFiles()

    index = 1
    for i in filesToSearchE:
        filesDic[index] = i
        index+=1

    if n:
        if k != None:
            createprocessesSpecial(n,wordToFind)
        else:
            createProcesses(n, len(filesToSearchSize), wordToFind)
    else:
        createProcesses(1, len(filesToSearchSize), wordToFind)
    
    timer.start()
    startProcesses()

    if k != None:
        eDiv(filesToSearchE,k)

    joinProcesses()
    timer.cancel()
    if finished == 1:
        for line in sharedLines:
            print(line)
    printResults(wordToFind, [file[0] for file in filesToSearchSize])
    

##############################################################################################################################
####################################################### MAIN Call ############################################################
##############################################################################################################################

if __name__ == "__main__":
    main(arguments)