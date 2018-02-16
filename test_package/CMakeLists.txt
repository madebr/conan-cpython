project(PackageTest CXX)
cmake_minimum_required(VERSION 2.8.12)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(PYTHON_INCLUDE_DIR "${CONAN_INCLUDE_DIRS_CPYTHON}")
find_package(PythonLibs REQUIRED)
find_package(PythonInterp REQUIRED)

add_library(spam SHARED example.cpp)
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
    COMMAND ${PYTHON_EXECUTABLE} "${CMAKE_CURRENT_SOURCE_DIR}/test_spam.py"
    )
