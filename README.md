## PySideX-Customized-Window
### 简介 Introduction
本Python模块是一个基于PySideX的界面模块，允许用户创建自定义非客户区窗口，非客户区使用PySideX绘制，支持移动、最小化、最大化、贴边自动布局、背景模糊等功能，分为3个版本：PySide1-Customized-Window、PySide2-Customized-Window、PySide6-Customized-Window，分别对应PySide1/PySide2/PySide6。只支持Windows、ReactOS、Wine平台。
<br>
This Python module is a PySideX-based interface module that allows users to create custom non-client windows, which are drawn using PySideX and support moving, minimizing, maximizing, auto-layout of borders, background blurring, etc. There are 3 branches: PySide1-Customized-Window, PySide2- Customized-Window, PySide6-Customized-Window, which correspond to PySide1/PySide2/PySide6 respectively. It only supports Windows, ReactOS and Wine.
### 示例代码 Example code
```
# -*- coding: utf-8 -*-
import sys
#from PySide2 import *
from PySide2_Customized_Window import *
#class MyWindow(BlurWindow):
class MyWindow(CustomizedWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
app = QApplication(sys.argv)
window = MyWindow()
window.setWindowTitle('Window')
window.setDarkTheme(2)
window.resize(int(400.0 * window.dpi / 96.0), int(175.0 * window.dpi / 96.0))
window.setWindowIcon(QIcon('Icon.ico'))
button = QPushButton('Button', window.clientArea)
window.show()
app.exec_()
```
