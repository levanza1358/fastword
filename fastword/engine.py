import ctypes
import os
import subprocess
import threading
import time
from ctypes import wintypes

if not hasattr(wintypes, "ULONG_PTR"):
    wintypes.ULONG_PTR = wintypes.WPARAM
if not hasattr(wintypes, "LRESULT"):
    wintypes.LRESULT = wintypes.LPARAM


user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104
WM_QUIT = 0x0012

VK_BACK = 0x08
VK_RETURN = 0x0D
VK_TAB = 0x09
VK_SPACE = 0x20
VK_CONTROL = 0x11
VK_MENU = 0x12
VK_SHIFT = 0x10

KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", wintypes.ULONG_PTR),
    ]


class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", POINT),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", wintypes.ULONG_PTR),
    ]

# Correct 64-bit alignment for INPUT structure
class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("ki", KEYBDINPUT),
        ("mi", ctypes.c_byte * 32), # Ensure union is large enough for MOUSEINPUT
        ("hi", ctypes.c_byte * 32)  # Ensure union is large enough for HARDWAREINPUT
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("padding", ctypes.c_byte * 4), # Explicit padding for 64-bit alignment if needed?
                                        # Actually, ctypes handles alignment usually, but 
                                        # Windows INPUT struct is tricky.
                                        # type is 4 bytes.
                                        # on 64-bit, the union starts at offset 8.
                                        # So there is a 4-byte padding after type.
        ("union", INPUT_UNION)
    ]

# Redefine to be safer
class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("union", INPUT_UNION)]

LPKBDLLHOOKSTRUCT = ctypes.POINTER(KBDLLHOOKSTRUCT)
LowLevelKeyboardProc = ctypes.WINFUNCTYPE(wintypes.LRESULT, wintypes.INT, wintypes.WPARAM, wintypes.LPARAM)

user32.SetWindowsHookExW.argtypes = [wintypes.INT, LowLevelKeyboardProc, wintypes.HINSTANCE, wintypes.DWORD]
user32.SetWindowsHookExW.restype = wintypes.HHOOK
user32.CallNextHookEx.argtypes = [wintypes.HHOOK, wintypes.INT, wintypes.WPARAM, wintypes.LPARAM]
user32.CallNextHookEx.restype = wintypes.LRESULT
user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
user32.UnhookWindowsHookEx.restype = wintypes.BOOL
user32.GetMessageW.argtypes = [ctypes.POINTER(MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
user32.GetMessageW.restype = wintypes.BOOL
user32.TranslateMessage.argtypes = [ctypes.POINTER(MSG)]
user32.TranslateMessage.restype = wintypes.BOOL
user32.DispatchMessageW.argtypes = [ctypes.POINTER(MSG)]
user32.DispatchMessageW.restype = wintypes.LRESULT
user32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.PostThreadMessageW.restype = wintypes.BOOL
user32.GetKeyboardState.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
user32.GetKeyboardState.restype = wintypes.BOOL
user32.GetKeyboardLayout.argtypes = [wintypes.DWORD]
user32.GetKeyboardLayout.restype = wintypes.HKL
user32.ToUnicodeEx.argtypes = [
    wintypes.UINT,
    wintypes.UINT,
    ctypes.POINTER(ctypes.c_ubyte),
    wintypes.LPWSTR,
    ctypes.c_int,
    wintypes.UINT,
    wintypes.HKL,
]
user32.ToUnicodeEx.restype = ctypes.c_int
user32.MapVirtualKeyW.argtypes = [wintypes.UINT, wintypes.UINT]
user32.MapVirtualKeyW.restype = wintypes.UINT
user32.GetAsyncKeyState.argtypes = [wintypes.INT]
user32.GetAsyncKeyState.restype = wintypes.SHORT
user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
user32.SendInput.restype = wintypes.UINT
user32.GetForegroundWindow.argtypes = []
user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD

kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
kernel32.GetModuleHandleW.restype = wintypes.HMODULE
kernel32.GetCurrentThreadId.argtypes = []
kernel32.GetCurrentThreadId.restype = wintypes.DWORD
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.QueryFullProcessImageNameW.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.LPWSTR,
    ctypes.POINTER(wintypes.DWORD),
]
kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000


def _async_down(vk: int) -> bool:
    return bool(user32.GetAsyncKeyState(vk) & 0x8000)


def _vk_to_text(vk: int, scan: int) -> str:
    state = (ctypes.c_ubyte * 256)()
    if not user32.GetKeyboardState(state):
        return ""

    layout = user32.GetKeyboardLayout(0)
    buf = ctypes.create_unicode_buffer(8)
    sc = scan or user32.MapVirtualKeyW(vk, 0)
    n = user32.ToUnicodeEx(vk, sc, state, buf, len(buf), 0, layout)
    if n == 1:
        return buf.value
    return ""


def _send_vk(vk: int) -> int:
    inputs = (INPUT * 2)()
    inputs[0].type = 1 # INPUT_KEYBOARD
    inputs[0].union.ki.wVk = vk
    inputs[0].union.ki.dwFlags = 0
    inputs[0].union.ki.dwExtraInfo = 0
    
    inputs[1].type = 1
    inputs[1].union.ki.wVk = vk
    inputs[1].union.ki.dwFlags = KEYEVENTF_KEYUP
    inputs[1].union.ki.dwExtraInfo = 0
    
    return user32.SendInput(2, inputs, ctypes.sizeof(INPUT))


def _send_backspaces(count: int) -> None:
    for _ in range(max(0, count)):
        _send_vk(VK_BACK)


def _send_text(text: str) -> None:
    if not text:
        return

    inputs = (INPUT * (len(text) * 2))()
    idx = 0
    for ch in text:
        # Down
        inputs[idx].type = 1
        inputs[idx].union.ki.wVk = 0
        inputs[idx].union.ki.wScan = ord(ch)
        inputs[idx].union.ki.dwFlags = KEYEVENTF_UNICODE
        inputs[idx].union.ki.dwExtraInfo = 0
        idx += 1
        
        # Up
        inputs[idx].type = 1
        inputs[idx].union.ki.wVk = 0
        inputs[idx].union.ki.wScan = ord(ch)
        inputs[idx].union.ki.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP
        inputs[idx].union.ki.dwExtraInfo = 0
        idx += 1

    user32.SendInput(len(inputs), inputs, ctypes.sizeof(INPUT))


def _send_enter() -> None:
    _send_vk(VK_RETURN)


def _normalize_app_targets(rule: dict) -> list[str]:
    raw = rule.get("app_targets", [])
    if isinstance(raw, str):
        raw = [part.strip() for part in raw.split(",")]
    if not isinstance(raw, list):
        return []
    targets = []
    for item in raw:
        name = os.path.basename(str(item or "").strip()).lower()
        if name and name not in targets:
            targets.append(name)
    return targets


def _foreground_process_name() -> str:
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return ""

    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if not pid.value:
        return ""

    process = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
    if not process:
        return ""

    try:
        size = wintypes.DWORD(1024)
        buffer = ctypes.create_unicode_buffer(size.value)
        if kernel32.QueryFullProcessImageNameW(process, 0, buffer, ctypes.byref(size)):
            return os.path.basename(buffer.value).lower()
    finally:
        kernel32.CloseHandle(process)
    return ""


class FastWordEngine:
    def __init__(self):
        self._rules = []
        self._enabled_map = {}
        self._triggers_sorted = []
        self._max_trigger_len = 0
        self._auto_enter = True
        self._global_delay_ms = 120

        self._buffer = ""
        self._buffer_max = 96
        self._injecting = False

        self._hook = None
        self._hook_proc = None
        self._thread = None
        self._thread_id = None
        self._running = threading.Event()
        self._lock = threading.Lock()
        
        self.log_callback = None

    def _log(self, msg: str):
        if self.log_callback:
            try:
                self.log_callback(msg)
            except:
                pass
        else:
            print(f"[Engine] {msg}")

    @property
    def running(self) -> bool:
        return bool(self._thread and self._thread.is_alive() and self._running.is_set())

    def set_rules(self, rules: list[dict]) -> None:
        with self._lock:
            self._rules = list(rules or [])
            enabled = {}
            for r in self._rules:
                if not r.get("enabled", True):
                    continue
                trig = str(r.get("trigger", ""))
                if not trig:
                    continue
                enabled.setdefault(trig, []).append(r)

            self._enabled_map = enabled
            self._triggers_sorted = sorted(enabled.keys(), key=len, reverse=True)
            self._max_trigger_len = max((len(t) for t in self._triggers_sorted), default=0)
            self._buffer_max = max(96, self._max_trigger_len * 4)

    def configure(self, *, auto_enter: bool, global_delay_ms: int) -> None:
        with self._lock:
            self._auto_enter = bool(auto_enter)
            self._global_delay_ms = max(0, int(global_delay_ms))

    def start(self) -> None:
        if self.running:
            self._log("Already running")
            return
        self._log("Starting engine...")
        self._running.set()
        self._thread = threading.Thread(target=self._thread_main, name="FastWordHook", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if not self._running.is_set():
            return
        
        self._log("Stopping engine...")
        self._running.clear()
        
        # Post a dummy message to wake up the message loop so it can exit
        tid = self._thread_id
        if tid:
            user32.PostThreadMessageW(tid, WM_QUIT, 0, 0)
        
        t = self._thread
        if t and t.is_alive():
            t.join(timeout=1.0)
            
        self._thread = None
        self._thread_id = None

    def _thread_main(self) -> None:
        self._thread_id = kernel32.GetCurrentThreadId()
        self._buffer = ""
        self._log(f"Hook thread started. TID: {self._thread_id}")

        # Keep a reference to prevent garbage collection
        @LowLevelKeyboardProc
        def hook_proc(nCode, wParam, lParam):
            if nCode < 0:
                return user32.CallNextHookEx(self._hook, nCode, wParam, lParam)

            if wParam == WM_KEYDOWN:
                try:
                    kb = ctypes.cast(lParam, LPKBDLLHOOKSTRUCT).contents
                    vk = kb.vkCode
                    
                    # Debug print (remove later)
                    # print(f"Key: {vk}")
                    
                    if self._injecting:
                        return user32.CallNextHookEx(self._hook, nCode, wParam, lParam)

                    if _async_down(VK_CONTROL) or _async_down(VK_MENU):
                        return user32.CallNextHookEx(self._hook, nCode, wParam, lParam)

                    if vk in (VK_RETURN, VK_TAB, VK_SPACE):
                        self._buffer = ""
                    elif vk == VK_BACK:
                        self._buffer = self._buffer[:-1]
                    else:
                        ch = _vk_to_text(vk, kb.scanCode)
                        if ch and ch.isprintable():
                            self._buffer += ch
                            if len(self._buffer) > self._buffer_max:
                                self._buffer = self._buffer[-self._buffer_max:]
                            
                            # Check for replacement
                            current_app = _foreground_process_name()
                            rep = self._match_replacement(current_app)
                            if rep:
                                rule = rep
                                trig = rule["trigger"]
                                replacement = rule["replacement"]
                                image_path = rule.get("image_path", "")
                                app_targets = _normalize_app_targets(rule)
                                
                                log_msg = f"Match: '{trig}'"
                                if replacement:
                                    log_msg += f" -> '{replacement}'"
                                if image_path:
                                    log_msg += f" + [Image]"
                                if app_targets:
                                    log_msg += f" @ {', '.join(app_targets)}"
                                self._log(log_msg)
                                
                                self._buffer = ""
                                self._injecting = True
                                try:
                                    pass
                                finally:
                                    pass
                                
                                # Using a separate thread to inject to avoid blocking the hook
                                auto_enter = rule.get("auto_enter", self._auto_enter)
                                threading.Thread(
                                    target=self._do_inject,
                                    args=(len(trig), replacement, image_path, bool(auto_enter)),
                                ).start()
                                # We return 1 to block the last character of the trigger from appearing
                                return 1
                        else:
                            # Non-printable resets buffer usually
                            pass

                except Exception as e:
                    self._log(f"Error in hook: {e}")

            return user32.CallNextHookEx(self._hook, nCode, wParam, lParam)

        self._hook_proc = hook_proc
        
        hmod = kernel32.GetModuleHandleW(None)
        self._hook = user32.SetWindowsHookExW(WH_KEYBOARD_LL, self._hook_proc, hmod, 0)
        
        if not self._hook:
            self._log("Failed to install hook")
            self._running.clear()
            return
            
        self._log("Hook installed successfully")

        msg = MSG()
        # Message loop
        while self._running.is_set():
            res = user32.GetMessageW(ctypes.byref(msg), 0, 0, 0)
            if res == -1 or res == 0:
                break
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        if self._hook:
            user32.UnhookWindowsHookEx(self._hook)
            self._hook = None

    def _do_inject(self, backspace_count: int, text: str, image_path: str = "", auto_enter: bool = True):
        try:
            self._injecting = True
            sent_content = False
            with self._lock:
                global_delay_ms = self._global_delay_ms
            
            # Add a small delay to ensure the last key up event is processed
            # threading.Event().wait(0.01) 
            
            # We blocked the last char, so backspace count is len(trigger) - 1
            if backspace_count > 1:
                # self._log(f"Sending {backspace_count-1} backspaces")
                _send_backspaces(backspace_count - 1)
            
            if text:
                # self._log(f"Sending text: {text}")
                _send_text(text)
                sent_content = True
            
            if image_path:
                sent_image = self._handle_image_paste(image_path)
                sent_content = sent_content or sent_image

            if sent_content and auto_enter:
                # Give target apps a moment to process the injected payload before submit.
                delay_seconds = max(global_delay_ms / 1000.0, 0.0)
                if delay_seconds > 0:
                    time.sleep(delay_seconds)
                self._log("Sending Enter")
                _send_enter()

        except Exception as e:
            self._log(f"Injection error: {e}")
        finally:
            self._injecting = False

    def _handle_image_paste(self, image_path: str) -> bool:
        if not os.path.exists(image_path):
            self._log(f"Image not found: {image_path}")
            return False
            
        self._log(f"Copying image to clipboard: {image_path}")
        try:
            # Use PowerShell to set image to clipboard
            # Command: Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Clipboard]::SetImage([System.Drawing.Image]::FromFile('path'))
            
            cmd = [
                "powershell", 
                "-NoProfile", 
                "-Command", 
                f"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Clipboard]::SetImage([System.Drawing.Image]::FromFile('{image_path}'))"
            ]
            
            # Hide console window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            subprocess.run(cmd, startupinfo=startupinfo, check=True, timeout=5)
            
            # Send Ctrl+V
            self._log("Sending Ctrl+V")
            
            # Send Ctrl+V combination
            self._send_ctrl_v()
            return True
            
        except Exception as e:
            self._log(f"Failed to copy/paste image: {e}")
            return False

    def _send_ctrl_v(self):
        inputs = (INPUT * 4)()
        
        # Ctrl Down
        inputs[0].type = 1
        inputs[0].union.ki.wVk = VK_CONTROL
        inputs[0].union.ki.dwFlags = 0
        
        # V Down
        inputs[1].type = 1
        inputs[1].union.ki.wVk = ord('V')
        inputs[1].union.ki.dwFlags = 0
        
        # V Up
        inputs[2].type = 1
        inputs[2].union.ki.wVk = ord('V')
        inputs[2].union.ki.dwFlags = KEYEVENTF_KEYUP
        
        # Ctrl Up
        inputs[3].type = 1
        inputs[3].union.ki.wVk = VK_CONTROL
        inputs[3].union.ki.dwFlags = KEYEVENTF_KEYUP
        
        user32.SendInput(4, inputs, ctypes.sizeof(INPUT))

    def _match_replacement(self, current_app: str) -> dict | None:
        with self._lock:
            if not self._enabled_map:
                return None

            buf = self._buffer
            for trig in self._triggers_sorted:
                if buf.endswith(trig):
                    rules = self._enabled_map[trig]
                    for rule in rules:
                        targets = _normalize_app_targets(rule)
                        if not targets:
                            return rule
                        if current_app and current_app in targets:
                            return rule
        return None

