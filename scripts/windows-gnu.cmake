# Unicorn's legacy archive creates a Unix symlink on Windows and requires extra OS
# privileges. Its normal static CMake library exports the same API without that step.
set(UNICORN_LEGACY_STATIC_ARCHIVE OFF CACHE BOOL "" FORCE)
set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
set(CMAKE_PROJECT_INCLUDE "${CMAKE_CURRENT_LIST_DIR}/windows-gnu-install.cmake")
