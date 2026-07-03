# C / C++ and Python on Linux — The 80/20

> Mental model: **decisions come from your head, syntax comes from reference.**
> Looking up flags and API signatures is not a learning failure — it's how the tools are used.

---

# C / C++

Three layers — language, compiler, build system.
You only need the build system once your project has more than a couple of files.
Start with the compiler directly; reach for CMake when it earns its place.

## 1. Bare minimum: compile a single file

```bash
# C
gcc main.c -o myapp

# C++ (always pass -std=c++17 — the default is too old)
g++ main.cpp -std=c++17 -o myapp

# Run it
./myapp
```

**Warnings — always on:**
- `-Wall -Wextra` — the baseline; catches the majority of real bugs
- `-Wpedantic` — strict ISO compliance; flags non-standard extensions
- `-Wshadow` — warns when a local variable hides an outer one (a common silent bug)
- `-Werror` — treats all warnings as errors; common in CI so warnings can't accumulate

**Optimisation — pick one per build:**
- `-O0` — no optimisation; fastest compile, easiest to debug (default if you pass nothing)
- `-Og` — light optimisation that preserves debuggability; better default for dev builds than `-O0`
- `-O2` — standard release optimisation; the safe pick for shipping
- `-O3` — aggressive; faster but can expose latent undefined behaviour
- `-Os` — optimise for binary size instead of speed (embedded, small binaries)
- `-march=native` — tune for the exact CPU you're compiling on; don't use when building for other machines

**Debug:**
- `-g` — embed source-level debug symbols (file names, line numbers, variable names)
- `-g3` — includes macro definitions too; useful when debugging heavily macro'd code
- `-DNDEBUG` — disables `assert()` calls; always pass this in release builds

**Sanitizers — runtime bug detectors (dev/test only, never ship):**
- `-fsanitize=address` — AddressSanitizer: catches buffer overflows, use-after-free, leaks
- `-fsanitize=undefined` — UBSan: catches undefined behaviour (signed overflow, null deref, etc.)
- `-fsanitize=thread` — ThreadSanitizer: catches data races in multi-threaded code

Sanitizers require `-g` to give useful output and cannot be combined freely
(address + undefined is fine; thread must be used alone).

**A typical pro dev build:**
```bash
g++ main.cpp -std=c++17 -Wall -Wextra -Wpedantic -Wshadow -Og -g \
    -fsanitize=address,undefined -o myapp
```

**A typical pro release build:**
```bash
g++ main.cpp -std=c++17 -Wall -Wextra -Werror -O2 -DNDEBUG -o myapp
```

## 2. Multiple source files (still no CMake)

```bash
g++ main.cpp physics.cpp controller.cpp -std=c++17 -Wall -o myapp
```

Headers (`.h` / `.hpp`) are `#include`d, not listed on the command line — only
`.cpp` files go to the compiler.

## 3. File layout that scales

```
myproject/
  CMakeLists.txt
  src/
    main.cpp
    physics.cpp
    physics.h
```

Keep headers next to their `.cpp` until you have a reason to separate them.

## 4. Minimal CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.16)
project(myapp)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(myapp
    src/main.cpp
    src/physics.cpp
)

target_include_directories(myapp PRIVATE src)
```

`add_executable` names the binary and lists every `.cpp`.
`target_include_directories` tells the compiler where to find your headers.

## 5. CMake build workflow

```bash
# One-time: configure
cmake -S . -B build

# Every subsequent build (just this line)
cmake --build build

# Run the result
./build/myapp
```

`-S .` = source is here, `-B build` = put all generated files in `build/`.
Never edit files inside `build/` — it's fully regenerated.
To start fresh: `rm -rf build && cmake -S . -B build`.

## 6. Linking an external library

**System library (e.g. pthreads, math):**
```cmake
target_link_libraries(myapp PRIVATE pthread m)
```

**Library CMake has a find-module for (e.g. Eigen, OpenCV, fmt):**
```cmake
find_package(Eigen3 REQUIRED)
target_link_libraries(myapp PRIVATE Eigen3::Eigen)
```

`find_package` searches standard install paths. If a library isn't found,
install it first: `sudo apt install libeigen3-dev` (or its dev package).
The `::` target form automatically pulls in the right include paths — prefer
it over bare library names.

## 7. Debug vs. release build

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug    # assertions on, symbols for gdb
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release  # optimised, smaller binary
```

The default is neither — always set one explicitly.

## 8. Installing tools

```bash
sudo apt update
sudo apt install build-essential cmake
```

`build-essential` gives you gcc, g++, make, and the C standard library headers.

## C/C++ one-line takeaway

**Single file → `g++ main.cpp -std=c++17 -o out && ./out`.**
**Multi-file → minimal CMakeLists.txt + `cmake -S . -B build && cmake --build build`.**

## C/C++ long tail (defer — look up when needed)

- `Makefile` syntax — CMake generates these; you rarely write them by hand
- `pkg-config` — older way to find libraries; CMake's `find_package` replaces it
- Static vs. shared libraries (`add_library`)
- Cross-compilation and toolchain files
- CPack (packaging), CTest (testing integration)
- Sanitizers (`-fsanitize=address,undefined`) — reach for when debugging memory bugs

---

# Python

Four layers — language, interpreter, environment, packages.
The interpreter runs your code; the environment isolates your dependencies.
Get the environment right and everything else follows.

## 1. Bare minimum: run a script

```bash
python3 myscript.py
```

`python3` is the one to use — `python` may point to Python 2 or may not exist.

```bash
python3 --version   # aim for 3.10+
```

## 2. Virtual environments (always use one)

A venv gives you an isolated Python + packages per project. Never `pip install`
globally — it creates version conflicts across projects.

```bash
# Create (once per project)
python3 -m venv .venv

# Activate (every new shell session)
source .venv/bin/activate

# Your prompt will show (.venv) — now pip installs go here, not globally
pip install numpy

# Deactivate when done
deactivate
```

Put `.venv/` in `.gitignore`. Recreate it from requirements instead of committing it.

## 3. Managing packages

```bash
pip install requests             # install a package
pip install -r requirements.txt  # install from a file
pip freeze > requirements.txt    # save current environment
pip list                         # see what's installed
```

`requirements.txt` is the standard way to share/reproduce an environment.
Pin versions when stability matters: `numpy==1.26.4`.

## 4. File layout

```
myproject/
  .venv/              ← never commit this
  .gitignore
  requirements.txt
  src/
    main.py
    physics.py
  tests/
    test_physics.py
```

Only add `__init__.py` when you need to import between subdirectories.

## 5. Imports

```python
import os                          # standard library — always available
import numpy as np                 # third-party — must be pip-installed
from physics import compute_force  # your own module in the same folder
```

`ModuleNotFoundError` means either the package isn't installed (`pip install <name>`)
or your venv isn't activated.

## 6. Script entry point pattern

```python
def main():
    print("hello")

if __name__ == "__main__":
    main()
```

The guard lets the file be imported by other modules without running the script body.
Use it in every file that has a `main()`. Skip it in pure library files.

## 7. Installing tools

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

`python3-venv` is sometimes missing from minimal installs — install it explicitly.

## 8. Jupyter notebooks (for interactive / exploratory work)

```bash
pip install jupyterlab
jupyter lab
```

Notebooks (`.ipynb`) mix code, output, and markdown in cells. Good for exploration
and visualisation; bad for production code. Keep notebook logic thin — move real
logic to `.py` files and import them.

## Python one-line takeaway

**`python3 -m venv .venv && source .venv/bin/activate` first, always.**
**Then `pip install`, write your script, `python3 myscript.py`.**

## Python long tail (defer — look up when needed)

- `pyproject.toml` / `setup.py` — only needed if you're publishing a package
- `poetry` / `uv` — alternative env + dependency managers; venv + pip is enough to start
- Type hints and `mypy` — useful for large projects, not required
- `pytest` — the standard test runner; reach for it once you have more than a handful of tests
- `__init__.py` details and package structure — look up when you need cross-folder imports
- Async / `asyncio` — only when you have I/O-bound concurrency
