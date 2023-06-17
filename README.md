## PySideX-Customized-Window
### 简介 Introduction
本Python模块是一个基于PySideX的界面模块，允许用户创建自定义非客户区窗口，非客户区使用PySideX绘制，支持移动、最小化、最大化、贴边自动布局、背景模糊等功能，分为3个版本：PySide1-Customized-Window、PySide2-Customized-Window、PySide6-Customized-Window，分别对应PySide1/PySide2/PySide6。只支持Windows、ReactOS、Wine平台。
<br>
This Python module is a PySideX-based interface module that allows users to create windows with customized non-client area, which are drawn using PySideX, support moving, minimizing, maximizing, auto-layout of borders, background blurring, etc. There are 3 branches: PySide1-Customized-Window, PySide2- Customized-Window, PySide6-Customized-Window, which correspond to PySide1/PySide2/PySide6 respectively. It only supports Windows, ReactOS and Wine.
### 截图 Screenshots
![ReactOS](https://github.com/YuZhouRen86/PySideX-Customized-Window/raw/main/jietu/ReactOS.png)
<br>
![WinVista](https://github.com/YuZhouRen86/PySideX-Customized-Window/raw/main/jietu/WinVista.png)
<br>
![Win10](https://github.com/YuZhouRen86/PySideX-Customized-Window/raw/main/jietu/Win10.png)
<br>
![Win11](https://github.com/YuZhouRen86/PySideX-Customized-Window/raw/main/jietu/Win11.png)
### 安装命令 Installation command
*`python -m pip install PySide1-Customized-Window`*
<br>
*`python -m pip install PySide2-Customized-Window`*
<br>
*`python -m pip install PySide6-Customized-Window`*
### 示例代码 Example code
```
# -*- coding: utf-8 -*-
import sys
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2_Customized_Window import *
#class MyWindow(BlurWindow):
class MyWindow(CustomizedWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
    def MessageHandler(self, hwnd, message, wParam, lParam):
        print(hwnd, message, wParam, lParam)
QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
app = QApplication(sys.argv)
window = MyWindow()
list(map(window.setTitleTextColour, [QColor(0, 0, 139), QColor(119, 235, 255)], [1, 2], [1] * 2))
window.setWindowTitle('Window')
window.setDarkTheme(2)
window.setWindowIcon(QIcon('Icon.ico'))
splashscreen = window.splashScreen()
splashscreen.show()
window.resize(int(400.0 * window.dpi() / 96.0), int(175.0 * window.dpi() / 96.0))
button = QPushButton('Button', window.clientArea)
window.show()
splashscreen.finish(window)
app.exec_()
```
