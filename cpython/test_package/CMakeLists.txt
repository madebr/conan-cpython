project(test_package C)
cmake_minimum_required(VERSION 2.8.11)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(CONAN_CPYTHON_VERSION "" CACHE STRING "Conan CPython version")
message(STATUS "CONAN_CPYTHON_VERSION: ${CONAN_CPYTHON_VERSION}")
if(NOT CONAN_CPYTHON_VERSION)
    message(FATAL_ERROR "CONAN_CPYTHON_VERSION empty")
endif()

set(Python_ADDITIONAL_VERSIONS "${CONAN_CPYTHON_VERSION}")
find_package(PythonInterp REQUIRED)
find_package(PythonLibs REQUIRED)

message(STATUS "PYTHON_VERSION_STRING: ${PYTHON_VERSION_STRING}")

if(NOT CONAN_CPYTHON_VERSION STREQUAL PYTHON_VERSION_STRING)
    message("CONAN_CPYTHON_VERSION does not match PYTHON_VERSION_STRING")
    message(FATAL_ERROR "CMake detected wrong cpython version")
endif()

add_library(spam MODULE test_package.c)
#target_link_libraries(spam ${PYTHON_LIBRARY})
target_include_directories(spam
    PRIVATE
        ${PYTHON_INCLUDE_DIR}
)
set_target_properties(spam PROPERTIES PREFIX "")

enable_testing()
add_test(
    NAME test_spam
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/lib"
    COMMAND "${PYTHON_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/test_spam.py"
)
