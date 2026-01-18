cmake_minimum_required(VERSION 3.10)
project(mod_status)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find uWebSockets
find_path(UWEBSOCKETS_INCLUDE_DIR uwebsockets/App.h
  PATHS
    ${CMAKE_SOURCE_DIR}/include
    /usr/local/include
    /usr/include
)

if(NOT UWEBSOCKETS_INCLUDE_DIR)
  message(FATAL_ERROR "uWebSockets not found. Please install uWebSockets or set UWEBSOCKETS_INCLUDE_DIR")
endif()

# Find uSockets library
find_library(USOCKETS_LIBRARY
  NAMES uSockets libusockets.a
  PATHS /usr/local/lib /usr/lib
)

if(NOT USOCKETS_LIBRARY)
  message(FATAL_ERROR "uSockets library not found")
endif()

# Find microtools library
find_library(MICROTOOLS_LIBRARY
  NAMES microtools libmicrotools.a
  PATHS /usr/local/lib
  REQUIRED
)

find_path(MICROTOOLS_INCLUDE_DIR microtools/microtools.h
  PATHS /usr/local/include
  REQUIRED
)

# Find spdlog
find_package(spdlog QUIET)

# Find zlib (required by uWebSockets)
find_package(ZLIB REQUIRED)

# Include directories
include_directories(
  ${UWEBSOCKETS_INCLUDE_DIR}
  ${MICROTOOLS_INCLUDE_DIR}
)

# Executable
add_executable(status
  src/main.cpp
)

# Link libraries
target_link_libraries(status
  pthread
  ${USOCKETS_LIBRARY}
  ZLIB::ZLIB
  -Wl,--start-group
  ${MICROTOOLS_LIBRARY}
  hiredis
  odbc
  -Wl,--end-group
)

# Link spdlog if found
if(spdlog_FOUND)
  target_link_libraries(status spdlog::spdlog)
endif()

# Output directory
set_target_properties(status PROPERTIES
  RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bin
)

# Installation
install(TARGETS status DESTINATION bin)
