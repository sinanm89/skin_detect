cmake_minimum_required (VERSION 2.6) 
project (SPMandEBM) 

set (CMAKE_CXX_COMPILER "g++")
set (CMAKE_C_COMPILER "gcc")

find_package(OpenCV 2.4 REQUIRED core highgui imgproc)

SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-sign-compare")

file(GLOB MYSOURCES	*.cpp *.c)
file(GLOB MYHEADERS	*.h *.hpp)

IF(APPLE)
   include_directories( /usr/local/include/ )
   INCLUDE_DIRECTORIES ( /System/Library/Frameworks )
ENDIF (APPLE)

add_executable(SPMandEBM ${MYSOURCES} ${MYHEADERS})

target_link_libraries(SPMandEBM ${OpenCV_LIBS})
