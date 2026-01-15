cmake_minimum_required(VERSION 3.10)
project(microtools)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(spdlog REQUIRED)

add_library(microtools STATIC
  DB.cpp
  Env.cpp
  File.cpp
  HttpRequest.cpp
  HttpResponse.cpp
  Json.cpp
  Logger.cpp
  Redis.cpp
  /usr/local/src/nanodbc/nanodbc.cpp
)

target_include_directories(microtools PUBLIC 
  ${CMAKE_CURRENT_SOURCE_DIR}
  /usr/local/include
)

target_link_libraries(microtools PUBLIC 
  spdlog::spdlog
  odbc
  hiredis
)

install(TARGETS microtools DESTINATION lib)
install(FILES microtools.h Data.h DB.h Env.h File.h HttpRequest.h HttpResponse.h Json.h Logger.h Redis.h DESTINATION include/microtools)
