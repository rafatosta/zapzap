cmake_minimum_required(VERSION 3.16)

project(ZapZap)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_AUTOMOC ON)

find_package(Qt6 REQUIRED COMPONENTS Widgets WebEngineWidgets)

add_executable(zapzap
    src/main.cpp
    src/MainWindow.cpp
    src/MainWindow.h
)

target_link_libraries(zapzap
    Qt6::Widgets
    Qt6::WebEngineWidgets
)
