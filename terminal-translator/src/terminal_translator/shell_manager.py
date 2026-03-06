"""
Shell Manager - PTY-based shell subprocess management
Spawns a real shell and captures its output for translation
"""

import os
import sys
import asyncio
from typing import Callable, Optional
import pty
import select
import subprocess


class ShellManager:
    """Manages a PTY-spawned shell subprocess"""
    
    def __init__(self, output_callback: Callable[[str], None]):
        """
        Initialize the shell manager.
        
        Args:
            output_callback: Async function called with shell output
        """
        self.output_callback = output_callback
        self.master_fd: Optional[int] = None
        self.slave_fd: Optional[int] = None
        self.process: Optional[subprocess.Popen] = None
        self.running = False
        self._read_task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start the shell subprocess"""
        # Determine shell to use
        shell = os.environ.get("SHELL", "/bin/bash")
        if sys.platform == "win32":
            # Windows: use cmd or PowerShell
            shell = os.environ.get("COMSPEC", "cmd.exe")
        
        # Create PTY pair
        self.master_fd, self.slave_fd = pty.openpty()
        
        # Set non-blocking mode on master
        import fcntl
        flags = fcntl.fcntl(self.master_fd, fcntl.F_GETFL)
        fcntl.fcntl(self.master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        
        # Spawn shell process
        self.process = subprocess.Popen(
            [shell],
            stdin=self.slave_fd,
            stdout=self.slave_fd,
            stderr=self.slave_fd,
            preexec_fn=os.setsid,
            env={**os.environ, "TERM": "xterm-256color"}
        )
        
        self.running = True
        
        # Start reading output
        self._read_task = asyncio.create_task(self._read_output())
    
    async def _read_output(self) -> None:
        """Continuously read output from the shell"""
        loop = asyncio.get_event_loop()
        
        while self.running and self.master_fd is not None:
            try:
                # Wait for data with timeout
                ready, _, _ = select.select([self.master_fd], [], [], 0.1)
                
                if ready:
                    try:
                        data = os.read(self.master_fd, 4096)
                        if data:
                            output = data.decode("utf-8", errors="replace")
                            # Call the callback
                            if asyncio.iscoroutinefunction(self.output_callback):
                                await self.output_callback(output)
                            else:
                                self.output_callback(output)
                    except OSError:
                        # Handle read errors gracefully
                        pass
                
                # Small delay to prevent CPU spinning
                await asyncio.sleep(0.05)
                
            except Exception as e:
                if self.running:
                    print(f"Shell read error: {e}")
                break
    
    async def send_command(self, command: str) -> None:
        """Send a command to the shell"""
        if self.master_fd is not None:
            try:
                os.write(self.master_fd, (command + "\n").encode("utf-8"))
            except OSError as e:
                print(f"Failed to send command: {e}")
    
    async def send_input(self, text: str) -> None:
        """Send raw input to the shell (no newline)"""
        if self.master_fd is not None:
            try:
                os.write(self.master_fd, text.encode("utf-8"))
            except OSError as e:
                print(f"Failed to send input: {e}")
    
    async def send_signal(self, signal: int) -> None:
        """Send a signal to the shell process"""
        if self.process:
            self.process.send_signal(signal)
    
    async def stop(self) -> None:
        """Stop the shell subprocess"""
        self.running = False
        
        # Cancel read task
        if self._read_task:
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass
        
        # Terminate process
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except:
                self.process.kill()
        
        # Close file descriptors
        if self.master_fd is not None:
            try:
                os.close(self.master_fd)
            except:
                pass
        
        if self.slave_fd is not None:
            try:
                os.close(self.slave_fd)
            except:
                pass
    
    @property
    def is_running(self) -> bool:
        """Check if the shell is still running"""
        if self.process:
            return self.process.poll() is None
        return False


class WindowsShellManager:
    """Shell manager for Windows (uses subprocess with pipes)"""
    
    def __init__(self, output_callback: Callable[[str], None]):
        self.output_callback = output_callback
        self.process: Optional[subprocess.Popen] = None
        self.running = False
        self._read_task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start the shell subprocess"""
        # Use PowerShell on Windows
        shell = os.environ.get("COMSPEC", "cmd.exe")
        
        self.process = subprocess.Popen(
            [shell],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        )
        
        self.running = True
        self._read_task = asyncio.create_task(self._read_output())
    
    async def _read_output(self) -> None:
        """Read output from the shell"""
        while self.running and self.process:
            try:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, self.process.stdout.readline
                )
                if line:
                    if asyncio.iscoroutinefunction(self.output_callback):
                        await self.output_callback(line)
                    else:
                        self.output_callback(line)
                await asyncio.sleep(0.01)
            except Exception as e:
                if self.running:
                    print(f"Read error: {e}")
                break
    
    async def send_command(self, command: str) -> None:
        """Send a command to the shell"""
        if self.process and self.process.stdin:
            try:
                self.process.stdin.write(command + "\n")
                self.process.stdin.flush()
            except Exception as e:
                print(f"Failed to send command: {e}")
    
    async def stop(self) -> None:
        """Stop the shell"""
        self.running = False
        if self._read_task:
            self._read_task.cancel()
        if self.process:
            self.process.terminate()


def get_shell_manager(output_callback: Callable) -> ShellManager:
    """Get the appropriate shell manager for the current platform"""
    if sys.platform == "win32":
        return WindowsShellManager(output_callback)
    return ShellManager(output_callback)
