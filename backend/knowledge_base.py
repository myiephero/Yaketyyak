"""
Local Knowledge Base for Terminal Translator
Fast pattern matching for common commands, errors, and patterns
"""

import re
from typing import Optional, Dict, List
import time

# Knowledge base with common terminal patterns
# Structure: { pattern: { beginner: str, familiar: str } }
KNOWLEDGE_BASE: Dict[str, Dict[str, str]] = {
    # Git Commands
    "git init": {
        "beginner": "This command creates a new Git repository in your current folder. Think of it like creating a new photo album - it sets up a special tracking system that will remember all the changes you make to your files. After running this, you'll see a hidden '.git' folder that stores all the version history.",
        "familiar": "Initializes a new Git repository in the current directory, creating the .git folder for version control."
    },
    "git clone": {
        "beginner": "This command downloads a complete copy of a project from the internet (like GitHub) to your computer. It's like downloading a whole folder with all its history and files. You'll get everything the original project has, including all past versions.",
        "familiar": "Clones a remote repository to your local machine, including all branches and commit history."
    },
    "git add": {
        "beginner": "This command tells Git 'I want to save these changes'. It's like putting items in a shopping cart before checkout - you're selecting which changes you want to include in your next save point (commit). Use 'git add .' to add everything, or 'git add filename' for specific files.",
        "familiar": "Stages changes for the next commit. Use 'git add .' for all changes or specify files individually."
    },
    "git commit": {
        "beginner": "This saves your staged changes with a message describing what you did. Think of it like saving a checkpoint in a video game with a note about what you accomplished. Always include a clear message with -m 'your message' so you remember what changes you made.",
        "familiar": "Records staged changes to the repository with a descriptive message. Use -m flag for inline messages."
    },
    "git push": {
        "beginner": "This uploads your saved changes (commits) to the internet (like GitHub). It's like syncing your local photo album to the cloud so others can see your photos. Your teammates will be able to see your changes after you push.",
        "familiar": "Uploads local commits to the remote repository. Use 'git push origin branch-name' for specific branches."
    },
    "git pull": {
        "beginner": "This downloads the latest changes from the internet and merges them with your local files. It's like refreshing your email inbox to get new messages. Run this regularly to stay up-to-date with your team's work.",
        "familiar": "Fetches and merges remote changes into your current branch. Equivalent to git fetch + git merge."
    },
    "git status": {
        "beginner": "This shows you what's happening in your project right now - which files have changed, which are ready to be saved, and which are new. It's like a dashboard showing you the current state of everything. Run this often to understand where you are.",
        "familiar": "Displays the state of working directory and staging area - shows tracked, untracked, and staged files."
    },
    "git branch": {
        "beginner": "Branches are like parallel universes for your code. This command lists all branches or creates new ones. The main branch is usually called 'main' or 'master'. Create new branches to work on features without affecting the main code.",
        "familiar": "Lists, creates, or deletes branches. Use -a to see all branches including remote ones."
    },
    "git checkout": {
        "beginner": "This command lets you switch between different branches or restore files. Think of it like traveling between parallel universes of your code. Use 'git checkout branch-name' to switch branches or 'git checkout -- filename' to undo changes to a file.",
        "familiar": "Switches branches or restores files. Use -b flag to create and switch to a new branch simultaneously."
    },
    "git merge": {
        "beginner": "This combines changes from one branch into another. It's like taking two different versions of a document and combining them into one. Sometimes this causes 'conflicts' if the same lines were changed differently - you'll need to manually decide which version to keep.",
        "familiar": "Integrates changes from one branch into another. May require conflict resolution if changes overlap."
    },
    "git log": {
        "beginner": "This shows the history of all changes (commits) made to your project. It's like a diary or timeline showing who changed what and when. Use arrow keys to scroll, and press 'q' to exit.",
        "familiar": "Shows commit history. Use --oneline for compact view, --graph for branch visualization."
    },
    "git diff": {
        "beginner": "This shows exactly what has changed in your files compared to the last saved version. Lines starting with + are additions (in green), and lines with - are deletions (in red). Great for reviewing your changes before committing.",
        "familiar": "Shows differences between commits, branches, or working directory. Use --staged for staged changes."
    },
    "git stash": {
        "beginner": "This temporarily saves your uncommitted changes and gives you a clean slate. It's like putting your half-finished work in a drawer so you can work on something else. Use 'git stash pop' to bring your changes back.",
        "familiar": "Temporarily stores uncommitted changes. Use 'git stash pop' to restore, 'git stash list' to view stashed changes."
    },
    "git reset": {
        "beginner": "This command undoes changes. It can be gentle (keeping your files) or destructive (deleting changes). Be careful with 'git reset --hard' as it permanently deletes uncommitted changes! Use --soft to only unstage commits.",
        "familiar": "Resets HEAD to specified state. --soft keeps changes staged, --mixed unstages, --hard discards all changes."
    },
    "git rebase": {
        "beginner": "This reorganizes your commit history by moving your commits on top of another branch. It's like rewriting history to make it cleaner. Use with caution - never rebase commits that others have already pulled!",
        "familiar": "Reapplies commits on top of another base tip. Creates linear history. Use -i for interactive rebasing."
    },
    
    # npm/yarn Commands
    "npm install": {
        "beginner": "This downloads and installs all the packages (code libraries) your project needs. It reads a file called 'package.json' to know what to install. Think of it like installing apps on your phone - these packages give your project extra features.",
        "familiar": "Installs all dependencies listed in package.json. Use --save-dev for dev dependencies, -g for global install."
    },
    "npm start": {
        "beginner": "This starts your application, usually a development server. After running it, you'll typically see a message telling you to open a web browser to view your app. Press Ctrl+C to stop it.",
        "familiar": "Runs the 'start' script from package.json, typically launching a dev server."
    },
    "npm run build": {
        "beginner": "This creates an optimized, production-ready version of your application. The output is usually placed in a 'build' or 'dist' folder. This version is what you'd upload to a real website.",
        "familiar": "Executes the build script, typically creating optimized production bundles in /build or /dist."
    },
    "npm test": {
        "beginner": "This runs tests to check if your code is working correctly. Tests are like automated quality checks that verify your app does what it's supposed to. Green results mean passing, red means something is broken.",
        "familiar": "Runs the test suite defined in package.json, typically using Jest or similar test runners."
    },
    "yarn add": {
        "beginner": "This installs a new package (code library) and adds it to your project. For example, 'yarn add react' installs the React library. The package becomes available for you to use in your code.",
        "familiar": "Installs a package and adds it to dependencies. Use --dev for devDependencies."
    },
    
    # Python Commands
    "pip install": {
        "beginner": "This installs Python packages (code libraries) from the internet. For example, 'pip install requests' installs a popular library for making web requests. Add -r requirements.txt to install everything listed in that file.",
        "familiar": "Installs Python packages from PyPI. Use -r for requirements file, --upgrade to update existing packages."
    },
    "python -m venv": {
        "beginner": "This creates a virtual environment - an isolated space for your project's packages. It prevents different projects from conflicting with each other. After creating it, you need to 'activate' it before installing packages.",
        "familiar": "Creates a virtual environment. Activate with 'source venv/bin/activate' (Unix) or 'venv\\Scripts\\activate' (Windows)."
    },
    "python manage.py": {
        "beginner": "This is Django's management command. You'll use it for things like starting the server (runserver), creating database tables (migrate), or creating admin users. It's the main way to interact with Django projects.",
        "familiar": "Django management command. Common subcommands: runserver, migrate, makemigrations, createsuperuser."
    },
    "pytest": {
        "beginner": "This runs your Python tests. It automatically finds files starting with 'test_' and runs the test functions inside them. Green dots mean passing tests, red F's mean failures. The summary at the end shows what went wrong.",
        "familiar": "Python test runner. Use -v for verbose, -x to stop on first failure, -k for keyword filtering."
    },
    
    # Docker Commands
    "docker build": {
        "beginner": "This creates a Docker image from a Dockerfile - like baking a cake from a recipe. The image contains everything your app needs to run. Use -t to give it a name (tag). The image can then be run anywhere Docker is installed.",
        "familiar": "Builds an image from Dockerfile. Use -t for tagging, -f for custom Dockerfile path, --no-cache to rebuild."
    },
    "docker run": {
        "beginner": "This starts a container from an image - like turning on a virtual computer. Use -p to expose ports (e.g., -p 3000:3000), -d to run in background, and -v to share folders with your computer.",
        "familiar": "Creates and starts a container. Key flags: -d (detached), -p (ports), -v (volumes), -e (env vars), --rm (auto-remove)."
    },
    "docker-compose up": {
        "beginner": "This starts all the services defined in your docker-compose.yml file. It's like turning on multiple connected machines at once. Use -d to run in background, and docker-compose down to stop everything.",
        "familiar": "Starts services from docker-compose.yml. Use -d for detached mode, --build to rebuild images, --force-recreate to recreate containers."
    },
    "docker ps": {
        "beginner": "This lists all running containers - like a task manager for Docker. You'll see container IDs, names, and what ports they're using. Add -a to also see stopped containers.",
        "familiar": "Lists running containers. Use -a for all containers, -q for IDs only, --format for custom output."
    },
    
    # Linux/Unix Commands
    "ls": {
        "beginner": "This lists files and folders in your current location. It's like opening a folder on your computer. Add -l for detailed info (size, date, permissions), -a to show hidden files (starting with .).",
        "familiar": "Lists directory contents. Common flags: -l (long format), -a (all including hidden), -h (human-readable sizes)."
    },
    "cd": {
        "beginner": "This changes your current folder (directory). 'cd folder-name' goes into a folder, 'cd ..' goes back up one level, 'cd ~' goes to your home folder, and 'cd /' goes to the root of the system.",
        "familiar": "Changes directory. Use .. for parent, ~ for home, - for previous directory, / for root."
    },
    "mkdir": {
        "beginner": "This creates a new folder. For example, 'mkdir my-project' creates a folder called 'my-project'. Use -p to create nested folders at once (like 'mkdir -p parent/child/grandchild').",
        "familiar": "Creates directories. Use -p for nested directories, -m to set permissions."
    },
    "rm": {
        "beginner": "This deletes files permanently (no recycle bin!). Use 'rm filename' for files and 'rm -r foldername' for folders. BE CAREFUL - there's no undo! The -f flag forces deletion without confirmation.",
        "familiar": "Removes files/directories. Flags: -r (recursive), -f (force), -i (interactive confirm). Use with caution!"
    },
    "cp": {
        "beginner": "This copies files or folders. 'cp original.txt copy.txt' makes a copy. For folders, use -r flag: 'cp -r folder1 folder2'. The original stays intact.",
        "familiar": "Copies files/directories. Use -r for directories, -v for verbose, -i for interactive overwrite prompt."
    },
    "mv": {
        "beginner": "This moves or renames files/folders. 'mv old.txt new.txt' renames a file. 'mv file.txt folder/' moves the file into the folder. Unlike cp, this removes the original.",
        "familiar": "Moves or renames files/directories. Use -i for interactive, -v for verbose."
    },
    "cat": {
        "beginner": "This displays the entire contents of a file in your terminal. Great for small files. For larger files, use 'less' or 'head' instead so you can scroll through them.",
        "familiar": "Concatenates and displays file contents. Use with pipes for combining files."
    },
    "grep": {
        "beginner": "This searches for text patterns in files. 'grep \"hello\" file.txt' finds all lines containing 'hello'. Add -i for case-insensitive, -r to search in all files in a folder.",
        "familiar": "Searches for patterns. Flags: -i (ignore case), -r (recursive), -n (line numbers), -v (invert match)."
    },
    "chmod": {
        "beginner": "This changes file permissions - who can read, write, or execute a file. 'chmod +x script.sh' makes a script executable. Numbers like 755 or 644 set specific permission combinations.",
        "familiar": "Changes file permissions. Common modes: 755 (rwxr-xr-x), 644 (rw-r--r--). Use +x to add execute permission."
    },
    "sudo": {
        "beginner": "This runs a command with administrator (superuser) privileges. Some operations need special permissions. You'll be asked for your password. Be careful - sudo can change important system files!",
        "familiar": "Executes command as superuser. Use -i for interactive shell, -u to specify user."
    },
    "curl": {
        "beginner": "This downloads content from the internet or makes web requests. 'curl https://example.com' shows a website's HTML. Add -O to save to a file, or use it to test APIs with -X POST and -d for data.",
        "familiar": "Transfers data via URLs. Common: -X (method), -H (headers), -d (data), -o (output file), -v (verbose)."
    },
    "ssh": {
        "beginner": "This securely connects to another computer over the network. 'ssh user@hostname' logs you into that machine. You can then run commands as if you were sitting at that computer. Type 'exit' to disconnect.",
        "familiar": "Secure shell connection. Use -i for key file, -p for port, -L for port forwarding."
    },
    "tar": {
        "beginner": "This creates or extracts archive files (like .tar.gz or .tgz). To extract: 'tar -xvf file.tar.gz'. To create: 'tar -cvzf archive.tar.gz folder/'. The letters stand for extract/create, verbose, file, and gzip compression.",
        "familiar": "Archive utility. Extract: -xvf. Create: -cvzf. Common extensions: .tar, .tar.gz, .tgz."
    },
    
    # Common Errors
    "command not found": {
        "beginner": "The terminal doesn't recognize this command. This usually means: 1) The program isn't installed, 2) There's a typo, or 3) The program is installed but not in your PATH (the list of places the terminal looks for programs). Try installing the program or checking your spelling.",
        "familiar": "Command not in PATH. Either not installed, misspelled, or PATH not configured. Try 'which command' or install the package."
    },
    "permission denied": {
        "beginner": "You don't have permission to do this operation. This usually means you need administrator access. Try adding 'sudo' before your command (you'll need to enter your password). Or the file might need different permissions (use chmod).",
        "familiar": "Insufficient permissions. Try sudo for admin ops, or chmod to change file permissions."
    },
    "no such file or directory": {
        "beginner": "The file or folder you're trying to access doesn't exist at that location. Check: 1) Is the name spelled correctly? 2) Are you in the right folder? Use 'ls' to see what files are here, and 'pwd' to see where you are.",
        "familiar": "Path doesn't exist. Verify filename, current directory (pwd), and use ls to list available files."
    },
    "ENOENT": {
        "beginner": "This is Node.js saying 'Error NO ENTry' - the file or folder wasn't found. Usually means a path is wrong or a dependency wasn't installed. Try running 'npm install' or check if the file path is correct.",
        "familiar": "Node.js 'No Entry' error - file/directory not found. Check paths and run npm install."
    },
    "EACCES": {
        "beginner": "This Node.js error means 'Error ACCESs' - you don't have permission. When installing packages globally, try: 'sudo npm install -g' or fix npm permissions. Sometimes caused by permission issues with node_modules.",
        "familiar": "Node.js access error. For global installs use sudo or fix npm permissions. May need to delete node_modules and reinstall."
    },
    "ModuleNotFoundError": {
        "beginner": "Python can't find a module (library) you're trying to import. This means: 1) You haven't installed it yet (run 'pip install package-name'), 2) You're not in the right virtual environment, or 3) There's a typo in the import name.",
        "familiar": "Python module not installed. Run 'pip install module-name' or check virtual environment is activated."
    },
    "SyntaxError": {
        "beginner": "There's a grammar mistake in your code - like a missing comma, quotation mark, or bracket. The error message shows which line has the problem. Look carefully at that line and the one before it for missing or extra characters.",
        "familiar": "Code syntax issue. Check the indicated line for missing brackets, quotes, colons, or incorrect indentation."
    },
    "TypeError": {
        "beginner": "You're trying to do something with the wrong type of data - like adding a number to text, or calling a function on something that isn't a function. Check what type of data you have and what operation you're trying to do.",
        "familiar": "Type mismatch. Check data types and ensure operations are valid for those types. Use type() to debug."
    },
    "KeyError": {
        "beginner": "You're trying to access a dictionary key that doesn't exist. For example, if your dictionary has 'name' but you ask for 'Name' (Python is case-sensitive!). Use .get('key') for safer access that returns None instead of crashing.",
        "familiar": "Dictionary key doesn't exist. Use .get() for safe access or check key existence with 'in' operator."
    },
    "IndentationError": {
        "beginner": "Python uses spaces/tabs to understand code structure, and yours aren't consistent. Make sure you're using the same number of spaces (usually 4) for each indent level. Don't mix tabs and spaces! Your editor should have a setting to show whitespace characters.",
        "familiar": "Inconsistent indentation. Use consistent spacing (4 spaces recommended). Enable 'show whitespace' in editor."
    },
    "ConnectionRefusedError": {
        "beginner": "Your program tried to connect to something (like a server or database) but couldn't reach it. Make sure: 1) The service is running, 2) You're using the right address and port, 3) No firewall is blocking the connection.",
        "familiar": "Connection failed. Verify service is running, correct host:port, and check firewall rules."
    },
    "CORS error": {
        "beginner": "Cross-Origin Resource Sharing error - your web browser is blocking a request for security reasons. This happens when your frontend tries to access a different domain's API. The server needs to send special headers to allow this. This is a backend configuration issue.",
        "familiar": "Cross-Origin blocked. Server must send Access-Control-Allow-Origin header. Configure CORS middleware in backend."
    },
    "404 Not Found": {
        "beginner": "The web address (URL) you're trying to access doesn't exist. Check: 1) Is the URL spelled correctly? 2) Does the page/API endpoint actually exist? 3) Is the server running? This is one of the most common web errors.",
        "familiar": "Resource not found at URL. Verify endpoint path, check server routes, ensure server is running."
    },
    "500 Internal Server Error": {
        "beginner": "Something went wrong on the server side. This usually means there's a bug in the backend code. Check the server logs (terminal where the server is running) for detailed error messages. The problem isn't with your request - it's with how the server handles it.",
        "familiar": "Server-side error. Check server logs for stack trace. Debug backend code handling this request."
    },
    "SIGKILL": {
        "beginner": "Your process was forcefully terminated by the system, usually because it used too much memory (RAM). This often happens with large data processing or memory leaks. Try processing smaller chunks of data or fixing memory issues in your code.",
        "familiar": "Process killed (often OOM). Check memory usage, process smaller data chunks, or increase available memory."
    },
    "ECONNRESET": {
        "beginner": "The connection was unexpectedly closed by the other side. This can happen with unstable networks, server restarts, or timeouts. Try the request again. If it keeps happening, check if the server is stable or if there's a network issue.",
        "familiar": "Connection reset by peer. Retry request, check server health, verify network stability."
    },
}

# Pattern-based matching for more complex cases
PATTERN_MATCHERS = [
    {
        "pattern": r"fatal: not a git repository",
        "beginner": "Git doesn't see a repository in this folder. You need to either: 1) Run 'git init' to create a new repository here, or 2) Navigate to a folder that already has a '.git' folder (an existing repository).",
        "familiar": "Not in a git repo. Run 'git init' or cd to a directory with .git folder."
    },
    {
        "pattern": r"error: failed to push some refs",
        "beginner": "Your push was rejected because the remote repository has changes you don't have locally. First run 'git pull' to download and merge those changes, then try pushing again. If there are conflicts, you'll need to resolve them manually.",
        "familiar": "Remote has newer commits. Pull and merge first: 'git pull origin branch', then push again."
    },
    {
        "pattern": r"CONFLICT.*Merge conflict",
        "beginner": "Git found conflicting changes in the same lines of code. Open the file(s) listed and look for <<<<<<< and >>>>>>> markers. Between them, you'll see both versions. Edit the file to keep what you want, remove the markers, then 'git add' and 'git commit' to finish the merge.",
        "familiar": "Merge conflict. Edit files to resolve conflicts (look for <<<<<<< markers), then git add and commit."
    },
    {
        "pattern": r"npm ERR!.*ERESOLVE",
        "beginner": "npm found conflicting package requirements - different packages need different versions of the same dependency. Try: 1) 'npm install --legacy-peer-deps' to ignore conflicts, 2) Update your packages, or 3) Check which packages have conflicts in the error message.",
        "familiar": "Dependency resolution conflict. Use --legacy-peer-deps or --force. Consider updating packages or checking peer deps."
    },
    {
        "pattern": r"npm ERR!.*ENOTEMPTY",
        "beginner": "npm couldn't delete a folder because it's not empty. This usually happens with corrupted node_modules. Solution: Delete the node_modules folder manually ('rm -rf node_modules' on Mac/Linux or delete in file explorer on Windows), then run 'npm install' again.",
        "familiar": "Directory not empty. Delete node_modules folder manually and reinstall: rm -rf node_modules && npm install"
    },
    {
        "pattern": r"Traceback \(most recent call last\)",
        "beginner": "This is Python's error report. Read it from BOTTOM to TOP - the last line shows the actual error, and the lines above show where in your code it happened. The file names and line numbers help you find exactly where to look.",
        "familiar": "Python traceback. Read bottom-up: last line is the error, above shows call stack with file:line info."
    },
    {
        "pattern": r"ImportError|ModuleNotFoundError",
        "beginner": "Python can't find a module you're trying to import. Solutions: 1) Install it with 'pip install module-name', 2) Check if your virtual environment is activated, 3) Verify the module name spelling. The error message tells you which module is missing.",
        "familiar": "Module not found. Install with pip, verify venv is active, check import spelling."
    },
    {
        "pattern": r"(?:localhost|127\.0\.0\.1):\d+",
        "beginner": "This is a local web address - your computer acting as a server. Open a web browser and go to this address (e.g., http://localhost:3000) to see your app. The number after : is the port. Only you can access this address - it's not on the internet.",
        "familiar": "Local server URL. Access via browser at the specified address. Port number follows the colon."
    },
    {
        "pattern": r"Segmentation fault|segfault|SIGSEGV",
        "beginner": "Your program tried to access memory it shouldn't have, causing it to crash. This is usually caused by bugs in lower-level code, corrupted data, or running out of memory. If you're using Python/JavaScript, it might be a bug in a library you're using.",
        "familiar": "Memory access violation. Check for null pointers, buffer overflows, or library bugs. May need debugging tools."
    },
    {
        "pattern": r"(?:killed|Killed|OOMKilled)",
        "beginner": "Your process was terminated because it used too much memory (RAM). The system stops programs that consume too many resources. Try processing smaller amounts of data at a time, or check for memory leaks in your code (like infinite loops that keep adding data).",
        "familiar": "Out of Memory kill. Reduce memory usage, process data in chunks, check for memory leaks."
    },
    {
        "pattern": r"address already in use|EADDRINUSE",
        "beginner": "Another program is already using this network port. Either: 1) Stop the other program using the port, 2) Change your app to use a different port, or 3) Find and kill the process using: 'lsof -i :PORT' then 'kill PID' (Mac/Linux).",
        "familiar": "Port in use. Find process: 'lsof -i :PORT' or 'netstat -tulpn'. Kill it or use different port."
    },
    {
        "pattern": r"ERR_CONNECTION_REFUSED",
        "beginner": "The server you're trying to reach refused the connection. This usually means: 1) The server isn't running, 2) Wrong address or port, or 3) Firewall blocking. Make sure your backend server is started and listening on the right port.",
        "familiar": "Connection refused. Verify server is running, correct host:port, no firewall blocks."
    },
    {
        "pattern": r"SSL.*certificate|CERT_|self.signed",
        "beginner": "There's an SSL/HTTPS certificate issue. This happens when: 1) Accessing a site with an expired or invalid certificate, 2) Using self-signed certificates in development, or 3) Certificate chain problems. In development, you might need to accept the risk or configure your app to allow insecure connections.",
        "familiar": "SSL certificate error. Check cert validity, trust chain, or configure client to accept self-signed certs in dev."
    },
]


def lookup(text: str, mode: str = "beginner") -> Optional[Dict]:
    """
    Fast lookup in the local knowledge base.
    Returns explanation if found, None if not found.
    
    Args:
        text: The terminal text to look up
        mode: "beginner" or "familiar"
    
    Returns:
        Dict with 'explanation' and 'source' if found, None otherwise
    """
    start_time = time.perf_counter()
    text_lower = text.lower().strip()
    
    # 1. Direct match in knowledge base (sorted by length, longest first for specificity)
    sorted_keys = sorted(KNOWLEDGE_BASE.keys(), key=len, reverse=True)
    for key in sorted_keys:
        if key.lower() in text_lower:
            explanations = KNOWLEDGE_BASE[key]
            elapsed = (time.perf_counter() - start_time) * 1000  # Convert to ms
            return {
                "explanation": explanations.get(mode, explanations["beginner"]),
                "source": "local",
                "matched_pattern": key,
                "lookup_time_ms": round(elapsed, 3)
            }
    
    # 2. Pattern-based matching
    for matcher in PATTERN_MATCHERS:
        if re.search(matcher["pattern"], text, re.IGNORECASE):
            elapsed = (time.perf_counter() - start_time) * 1000
            return {
                "explanation": matcher.get(mode, matcher["beginner"]),
                "source": "local",
                "matched_pattern": matcher["pattern"],
                "lookup_time_ms": round(elapsed, 3)
            }
    
    # 3. No match found
    elapsed = (time.perf_counter() - start_time) * 1000
    return None


def get_all_patterns() -> List[Dict]:
    """Returns all patterns for the knowledge base viewer."""
    patterns = []
    
    for key, explanations in KNOWLEDGE_BASE.items():
        patterns.append({
            "pattern": key,
            "type": "exact",
            "beginner_preview": explanations["beginner"][:100] + "...",
            "familiar_preview": explanations["familiar"][:100] + "..."
        })
    
    for matcher in PATTERN_MATCHERS:
        patterns.append({
            "pattern": matcher["pattern"],
            "type": "regex",
            "beginner_preview": matcher["beginner"][:100] + "...",
            "familiar_preview": matcher["familiar"][:100] + "..."
        })
    
    return patterns


def get_pattern_count() -> int:
    """Returns the total number of patterns in the knowledge base."""
    return len(KNOWLEDGE_BASE) + len(PATTERN_MATCHERS)
