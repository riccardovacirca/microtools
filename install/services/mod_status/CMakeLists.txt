cmake_minimum_required(VERSION 3.10)
project(mod_status_example)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find httplib (header-only library)
find_path(HTTPLIB_INCLUDE_DIR httplib.h
  PATHS
    ${CMAKE_SOURCE_DIR}/include
    /usr/local/include
    /usr/include
)

if(NOT HTTPLIB_INCLUDE_DIR)
  message(FATAL_ERROR "httplib.h not found. Please install cpp-httplib or set HTTPLIB_INCLUDE_DIR")
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

# Include directories
include_directories(
  ${HTTPLIB_INCLUDE_DIR}
  ${MICROTOOLS_INCLUDE_DIR}
)

# Executable
add_executable(status
  src/main.cpp
)

# Link libraries (circular dependencies require --start-group/--end-group)
target_link_libraries(status
  pthread
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
