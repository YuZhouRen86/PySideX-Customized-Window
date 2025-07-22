import sys
if sys.platform != 'win32': raise Exception('Windows, ReactOS or Wine is required.')
try:
    from PySide6.QtWidgets import *
    from PySide6.QtGui import *
    from PySide6.QtCore import *
    ISPYSIDE1 = False
except: raise ImportError('Cannot load PySide6.')
import ctypes
try: import winreg
except: import _winreg as winreg
from ctypes.wintypes import MSG, POINT, RECT


__all__ = ['CustomizedWindow', 'BlurWindow']


user32 = ctypes.windll.user32


class LOGFONT(ctypes.Structure):
    _fields_ = [
    ('lfHeight', ctypes.c_long),
    ('lfWidth', ctypes.c_long),
    ('lfEscapement', ctypes.c_long),
    ('lfOrientation', ctypes.c_long),
    ('lfWeight', ctypes.c_long),
    ('lfItalic', ctypes.c_byte),
    ('lfUnderline', ctypes.c_byte),
    ('lfStrikeOut', ctypes.c_byte),
    ('lfCharSet', ctypes.c_byte),
    ('lfOutPrecision', ctypes.c_byte),
    ('lfClipPrecision', ctypes.c_byte),
    ('lfQuality', ctypes.c_byte),
    ('lfPitchAndFamily', ctypes.c_byte),
    ('lfFaceName', ctypes.c_wchar * 32)]


class NONCLIENTMETRICS(ctypes.Structure):
    _fields_ = [
    ('cbSize', ctypes.c_ulong),
    ('iBorderWidth', ctypes.c_long),
    ('iScrollWidth', ctypes.c_long),
    ('iScrollHeight', ctypes.c_long),
    ('iCaptionWidth', ctypes.c_long),
    ('iCaptionHeight', ctypes.c_long),
    ('lfCaptionFont', LOGFONT),
    ('iSmCaptionWidth', ctypes.c_long),
    ('iSmCaptionHeight', ctypes.c_long),
    ('lfSmCaptionFont', LOGFONT),
    ('iMenuWidth', ctypes.c_long),
    ('iMenuHeight', ctypes.c_long),
    ('lfMenuFont', LOGFONT),
    ('lfStatusFont', LOGFONT),
    ('lfMessageFont', LOGFONT),
    ('iPaddedBorderWidth', ctypes.c_long)]


class STYLESTRUCT(ctypes.Structure): _fields_ = [('styleOld', ctypes.c_ulong), ('styleNew', ctypes.c_ulong)]
class NCCALCSIZE_PARAMS(ctypes.Structure): _fields_ = [('rgrc', RECT * 3), ('lppos', ctypes.POINTER(ctypes.c_void_p))]
class MONITORINFO(ctypes.Structure): _fields_ = [('cbSize', ctypes.c_ulong), ('rcMonitor', RECT), ('rcWork', RECT), ('dwFlags', ctypes.c_ulong)]
class APPBARDATA(ctypes.Structure): _fields_ = [('cbSize', ctypes.c_ulong), ('hWnd', ctypes.c_void_p), ('uCallbackMessage', ctypes.c_ulong), ('uEdge', ctypes.c_ulong), ('rc', RECT), ('lParam', ctypes.c_long)]
class WindowCompositionAttribute(ctypes.Structure): _fields_ = [('Attribute', ctypes.c_long), ('Data', ctypes.POINTER(ctypes.c_long)), ('SizeOfData', ctypes.c_ulong)]
class ACCENT_POLICY(ctypes.Structure): _fields_ = [('AccentState', ctypes.c_ulong), ('AccentFlags', ctypes.c_ulong), ('GradientColor', ctypes.c_ulong), ('AnimationId', ctypes.c_ulong)]
class DWM_BLURBEHIND(ctypes.Structure): _fields_ = [('dwFlags', ctypes.c_ulong), ('fEnable', ctypes.c_long), ('hRgnBlur', ctypes.c_void_p), ('fTransitionOnMaximized', ctypes.c_long)]
class MARGINS(ctypes.Structure): _fields_ = [('cxLeftWidth', ctypes.c_long), ('cxRightWidth', ctypes.c_long), ('cyTopHeight', ctypes.c_long), ('cyBottomHeight', ctypes.c_long)]
class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure): _fields_ = [('Attribute', ctypes.c_ulong), ('Data', ctypes.POINTER(ACCENT_POLICY)), ('SizeOfData', ctypes.c_ulong)]


class Win10BlurEffect:
    def __init__(self):
        self.WCA_ACCENT_POLICY, self.ACCENT_ENABLE_BLURBEHIND, self.ACCENT_ENABLE_ACRYLICBLURBEHIND = 19, 3, 4
        self.accentPolicy = ACCENT_POLICY()
        self.winCompAttrData = WINDOWCOMPOSITIONATTRIBDATA()
        self.winCompAttrData.Attribute = self.WCA_ACCENT_POLICY
        self.winCompAttrData.SizeOfData = ctypes.sizeof(self.accentPolicy)
        self.winCompAttrData.Data = ctypes.pointer(self.accentPolicy)
    def __initAP(self, a, b, c, d):
        b = ctypes.c_ulong(int(b, base=16))
        d = ctypes.c_ulong(d)
        accentFlags = ctypes.c_ulong(0x20 | 0x40 | 0x80 | 0x100 | 0x200 if c else 0)
        self.accentPolicy.AccentState = a
        self.accentPolicy.GradientColor = b
        self.accentPolicy.AccentFlags = accentFlags
        self.accentPolicy.AnimationId = d
    def setAeroEffect(self, hWnd, gradientColor='01000000', isEnableShadow=True, animationId=0):
        self.__initAP(self.ACCENT_ENABLE_BLURBEHIND, gradientColor, isEnableShadow, animationId)
        return user32.SetWindowCompositionAttribute(hWnd, ctypes.byref(self.winCompAttrData))
    def setAcrylicEffect(self, hWnd, gradientColor='01000000', isEnableShadow=True, animationId=0):
        self.__initAP(self.ACCENT_ENABLE_ACRYLICBLURBEHIND, gradientColor, isEnableShadow, animationId)
        return user32.SetWindowCompositionAttribute(hWnd, ctypes.byref(self.winCompAttrData))


class MenuBtn(QAbstractButton):
    def __init__(self, parent):
        super(MenuBtn, self).__init__(parent)
        self.parent = parent
        self.parentattr = lambda a: getattr(parent, '_CustomizedWindow__' + a)
        self.isminbtn, self.ismaxbtn, self.isclosebtn = map(isinstance, [self] * 3, [MinBtn, MaxBtn, CloseBtn])
        self.updateSize = lambda: self.setFixedSize(*list(map(self.parentattr, ['menubtn_w', 'title_h'])))
        self.updateSize()
        self.setFocusPolicy(Qt.NoFocus)
        self.bgclr = Qt.transparent
    def paintEvent(self, *a):
        self.updateSize()
        w, h = self.width(), self.height()
        parent = self.parent
        dpi, realdpi = parent.dpi(), parent.realdpi()
        isdarktheme = parent.isDarkTheme()
        isactivewindow = parent.hwnd() == user32.GetForegroundWindow()
        ISMAX, ISFULL = user32.IsZoomed(parent.hwnd()), parent.isFullScreen()
        hasminbtn, hasmaxbtn = map(self.parentattr, ['hasminbtn', 'hasmaxbtn'])
        painter, path = QPainter(self), QPainterPath()
        painter.setBrush(self.bgclr)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())
        painter.setBrush(Qt.NoBrush)
        isdisabled = (self.isminbtn and not hasminbtn) or (self.ismaxbtn and not hasmaxbtn)
        pen = QPen(self.parentattr('menubtnclr_%s_%s' % ('d' if isdarktheme else 'l', 'ac' if isactivewindow and not isdisabled else 'in')))
        penwidth = int(1.35 * dpi / 96.0)
        pen.setWidth(penwidth)
        painter.setPen(pen)
        f1, f2 = lambda n: int(n * w), lambda n: int(n * h)
        f3, f4 = path.moveTo, path.lineTo
        if realdpi >= 143: painter.setRenderHint(QPainter.Antialiasing)
        if self.isminbtn:
            f3(f1(0.391), f2(0.500))
            f4(f1(0.609), f2(0.500))
        elif self.ismaxbtn:
            if ISMAX:
                f3(f1(0.402), f2(0.406))
                f4(f1(0.559), f2(0.406))
                f4(f1(0.559), f2(0.656))
                f4(f1(0.402), f2(0.656))
                f4(f1(0.402), f2(0.406))
                f3(f1(0.441), f2(0.344))
                f4(f1(0.598), f2(0.344))
                f4(f1(0.598), f2(0.594))
            else:
                f3(f1(0.402), f2(0.344))
                f4(f1(0.598), f2(0.344))
                f4(f1(0.598), f2(0.656))
                f4(f1(0.402), f2(0.656))
                f4(f1(0.402), f2(0.344))
        elif self.isclosebtn:
            f3(f1(0.402), f2(0.344))
            f4(f1(0.598), f2(0.656))
            f3(f1(0.598), f2(0.344))
            f4(f1(0.402), f2(0.656))
        painter.drawPath(path)


class MinBtn(MenuBtn): pass
class MaxBtn(MenuBtn): pass
class CloseBtn(MenuBtn): pass


class SystemVBoxLyt(QVBoxLayout):
    def __init__(self, parent):
        super(SystemVBoxLyt, self).__init__()
        self.setContentsMargins(*[0] * 4)
        self.setSpacing(0)


class SystemHBoxLyt(QHBoxLayout):
    def __init__(self, parent):
        super(SystemHBoxLyt, self).__init__()
        self.parent = parent
        self.istitlebarlyt, self.istitleiconlyt = map(isinstance, [self] * 2, [TitleBarLyt, TitleIconLyt])
        self.updateMargin = lambda: self.setContentsMargins(*[parent._CustomizedWindow__titleicon_mgn if self.istitleiconlyt else 0] * 4)
        self.updateMargin()
        self.setSpacing(0)


class TitleBarLyt(SystemHBoxLyt): pass
class TitleIconLyt(SystemHBoxLyt): pass


class SystemLbl(QAbstractButton):
    def __init__(self, parent):
        super(SystemLbl, self).__init__(parent)
        self.parent = parent
        self.parentattr = lambda a: getattr(parent, '_CustomizedWindow__' + a)
        self.isbglbl, self.istitlebar, self.isclientarealbl, self.istitletextlbl, self.istitleiconcontainerlbl, self.istitleiconlbl = map(isinstance, [self] * 6, [BgLbl, TitleBar, ClientAreaLbl, TitleTextLbl, TitleIconContainerLbl, TitleIconLbl])
        if self.istitlebar: self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed), self.setFixedHeight(self.parentattr('title_h'))
        elif self.isbglbl or self.isclientarealbl or self.istitletextlbl or self.istitleiconlbl: self.setSizePolicy(*[QSizePolicy.Expanding] * 2)
        elif self.istitleiconcontainerlbl: self.setFixedSize(*[self.parentattr('title_h')] * 2)
        self.setFocusPolicy(Qt.NoFocus)
        self.bgclr = Qt.transparent
        self.draw = True
        self.isMax = lambda: user32.IsZoomed(parent.hwnd())
        self.maxWithMgn = lambda: self.isMax() and not parent.isFullScreen() and self.parentattr('maxwithmgn')
    def paintEvent(self, *a):
        parent = self.parent
        isdarktheme = parent.isDarkTheme()
        isblurwindow = self.parentattr('isblurwindow')
        isaeroenabled = isAeroEnabled()
        isactivewindow = parent.hwnd() == user32.GetForegroundWindow()
        NMAXFULL = not (self.isMax() or parent.isFullScreen())
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        bgclr = Qt.transparent
        title_h = self.parentattr('title_h')
        f1 = lambda pen: (painter.setBrush(Qt.NoBrush), painter.setPen(pen))
        f2 = lambda n: QColor(*[0 if isdarktheme else 255] * 3 + [n])
        if self.isbglbl: bgclr = Qt.transparent if (isblurwindow and isaeroenabled) else QColor(*[58 if isdarktheme else 197] * 3)
        elif self.istitlebar:
            self.setFixedHeight(title_h)
            if isblurwindow:
                if self.draw:
                    bgclr = QLinearGradient(*[0] * 3 + [self.height()])
                    list(map(bgclr.setColorAt, [0, 1], [f2(107), f2(197)]))
                else: bgclr = f2(127)
            else: bgclr = f2(255)
        elif self.isclientarealbl:
            self.placeClientArea()
            bgclr = f2(127 if isblurwindow else 255)
        elif self.istitletextlbl:
            pen = QPen(self.parentattr('titletextclr_%s_%s' % ('d' if isdarktheme else 'l', 'ac' if isactivewindow else 'in')))
            f1(pen)
            font = QFont(self.parentattr('captionfont'))
            font.setPixelSize(self.parentattr('title_fontsize'))
            painter.setFont(font)
            if self.draw: painter.drawText(self.rect(), Qt.AlignVCenter, parent.windowTitle())
        elif self.istitleiconcontainerlbl:
            self.setFixedSize(*[title_h] * 2)
        elif self.istitleiconlbl:
            pixmap = parent.windowIcon().pixmap(self.width(), self.height())
            if self.draw: painter.drawPixmap(0, 0, pixmap)
        painter.setBrush(bgclr)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())
        if (self.istitlebar or self.isclientarealbl) and (NMAXFULL or self.maxWithMgn()):
            pen = QPen(QColor(*[127] * 3))
            grey_bd_w = int(2 * parent.dpi() / 96.0)
            pen.setWidth(grey_bd_w)
            f1(pen)
            painter.drawRect(0, -grey_bd_w if self.isclientarealbl else 0, self.width(), self.height() + grey_bd_w * (2 if self.istitlebar else 1))
    def placeClientArea(self):
        parent = self.parent
        bd_w = self.parentattr('bd_w')
        title_h = self.parentattr('title_h')
        NMAXFULL = not (self.isMax() or parent.isFullScreen())
        WITHMARGIN = NMAXFULL or self.maxWithMgn()
        parent.clientArea.setGeometry(QRect(*[bd_w * int(WITHMARGIN), 0, parent.width() - bd_w * (2 if WITHMARGIN else 0), parent.height() - title_h - bd_w * int(WITHMARGIN)]))


class BgLbl(SystemLbl): pass
class TitleBar(SystemLbl): pass
class ClientAreaLbl(SystemLbl): pass
class TitleTextLbl(SystemLbl): pass
class TitleIconContainerLbl(SystemLbl): pass
class TitleIconLbl(SystemLbl): pass


def isAeroEnabled():
    try:
        pfEnabled = ctypes.c_ulong()
        ctypes.windll.dwmapi.DwmIsCompositionEnabled(ctypes.byref(pfEnabled))
        return pfEnabled.value
    except: return 0


def isdarktheme():
    try: value = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize'), 'AppsUseLightTheme')[0]
    except: return False
    return False if value else True


def getMonitorRectForWindow(hwnd, workarea=False):
    hMonitor = user32.MonitorFromWindow(hwnd, 2)
    monitorinfo = MONITORINFO()
    monitorinfo.cbSize = ctypes.sizeof(MONITORINFO)
    user32.GetMonitorInfoW(hMonitor, ctypes.byref(monitorinfo))
    return getattr(monitorinfo, 'rcWork' if workarea else 'rcMonitor')


def gethwnd(window):
    hwnd = window.winId()
    if type(hwnd) != int:
        try:
            f = ctypes.pythonapi.PyCapsule_GetPointer
            f.restype, f.argtypes = ctypes.c_void_p, [ctypes.py_object, ctypes.c_char_p]
            hwnd = f(hwnd, None)
        except:
            f = ctypes.pythonapi.PyCObject_AsVoidPtr
            f.restype, f.argtypes = ctypes.c_void_p, [ctypes.py_object]
            hwnd = f(hwnd)
    return hwnd


def getdpiforwindow(hwnd):
    dpi = 96
    try:
        dpi_x, dpi_y = [ctypes.c_ulong()] * 2
        monitor_h = user32.MonitorFromWindow(hwnd, 2)
        ctypes.windll.shcore.GetDpiForMonitor(monitor_h, 0, ctypes.byref(dpi_x), ctypes.byref(dpi_y))
        dpi = dpi_x.value
    except:
        dpiaware = user32.IsProcessDPIAware() if hasattr(user32, 'IsProcessDPIAware') else True
        if dpiaware:
            hDC = user32.GetDC(None)
            dpi = ctypes.windll.gdi32.GetDeviceCaps(hDC, 88)
            user32.ReleaseDC(None, hDC)
    return dpi


def getautohidetbpos(rc=RECT(*[0] * 4)):
    ABM_GETAUTOHIDEBAR, ABM_GETAUTOHIDEBAREX = 0x7, 0xb
    data = APPBARDATA()
    data.cbSize = ctypes.sizeof(APPBARDATA)
    data.rc = rc
    shell32 = ctypes.windll.shell32
    tb_rc = RECT()
    user32.GetWindowRect(user32.FindWindowA(b'Shell_TrayWnd', None), ctypes.byref(tb_rc))
    for i in range(4):
        data.uEdge = i
        if shell32.SHAppBarMessage(ABM_GETAUTOHIDEBAREX, ctypes.byref(data)): return i
        else:
            if (tb_rc.left == rc.left) + (tb_rc.top == rc.top) + (tb_rc.right == rc.right) + (tb_rc.bottom == rc.bottom) >= 2:
                if shell32.SHAppBarMessage(ABM_GETAUTOHIDEBAR, ctypes.byref(data)): return i
    return 4


def setwin11blur(hWnd):
    ENTRY_21H2, ENTRY_22H2, VALUE_21H2, VALUE_22H2 = 1029, 38, 1, 3
    return list(map(ctypes.windll.dwmapi.DwmSetWindowAttribute, [hWnd] * 2, [ENTRY_21H2, ENTRY_22H2], [ctypes.byref(ctypes.c_long(VALUE_21H2)), ctypes.byref(ctypes.c_long(VALUE_22H2))], [ctypes.sizeof(ctypes.c_long)] * 2))


def getcaptionfont():
    res = NONCLIENTMETRICS()
    res.cbSize = ctypes.sizeof(NONCLIENTMETRICS)
    user32.SystemParametersInfoW(0x29, ctypes.sizeof(NONCLIENTMETRICS), ctypes.byref(res), 0)
    return res.lfCaptionFont.lfFaceName


class SplashScreen(QSplashScreen):
    def __init__(self, parent):
        super(SplashScreen, self).__init__()
        self.__hwnd = gethwnd(self)
        dpi = parent.dpi()
        sc = QApplication.screens()[0].size() if hasattr(QApplication, 'screens') else QDesktopWidget().screenGeometry(0)
        f1 = lambda n: int(n * dpi / 96.0)
        f2 = lambda obj1, obj2: [(obj1.width() - obj2.width()) // 2, (obj1.height() - obj2.height()) // 2]
        self.resize(*[f1(500)] * 2)
        self.move(*f2(sc, self))
        self.mainlbl = QLabel(self)
        bgclr, bdclr = ['#000000', '#AFAFAF'] if parent.isDarkTheme() else ['#FFFFFF', '#505050']
        self.mainlbl.setStyleSheet('background: %s; border: %dpx solid %s' % (bgclr, f1(2), bdclr))
        self.mainlbl.resize(self.width(), self.height())
        self.mainlbl.move(*f2(self, self.mainlbl))
        self.iconlbl = QLabel(self)
        iconsize = [f1(175)] * 2
        pixmap = QPixmap.fromImage(parent.windowIcon().pixmap(*iconsize).toImage()).scaled(*iconsize)
        self.iconlbl.setPixmap(pixmap)
        self.iconlbl.resize(*iconsize)
        self.iconlbl.move(*f2(self, self.iconlbl))
        shadow = QGraphicsBlurEffect(self)
        shadow.setBlurRadius(f1(10))
        self.mainlbl.setGraphicsEffect(shadow)


class CustomizedWindow(QWidget):
    '''A customized window based on PySideX.'''
    def __init__(self):
        super(CustomizedWindow, self).__init__()
        self.__hwnd = gethwnd(self)
        hwnd = self.hwnd()
        self.__isblurwindow = isinstance(self, BlurWindow)
        self.setAttribute(Qt.WA_TranslucentBackground, True) if ISPYSIDE1 else self.setStyleSheet('CustomizedWindow{background: rgba(0, 0, 0, 0)}')
        self.__flashinnextmessage_inf = [False, 0, 0, 0, 0]
        self.__maxwithmgn = False
        SWP_NOSIZE, SWP_NOMOVE, SWP_NOZORDER, SWP_FRAMECHANGED, SWP_NOSENDCHANGING = 0x1, 0x2, 0x4, 0x20, 0x400
        self.__updatencarea = lambda: user32.SetWindowPos(hwnd, None, 0, 0, 0, 0, SWP_NOSIZE | SWP_NOMOVE | SWP_NOZORDER | SWP_FRAMECHANGED | SWP_NOSENDCHANGING)
        self.__SWL = getattr(user32, 'SetWindowLongPtrW' if hasattr(user32, 'SetWindowLongPtrW') else 'SetWindowLongW')
        self.__defaultSWL = lambda: self.__SWL(self.hwnd(), -16, user32.GetWindowLongW(self.hwnd(), -16) & ~0x80000)
        self.__WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_long, ctypes.c_ulong, ctypes.c_long, ctypes.c_long)
        self.__BasicMHAddr = ctypes.cast(self.__WNDPROC(self.__BasicMH), ctypes.c_void_p)
        if hasattr(user32, 'GetWindowLongPtrW'): self.__orig_BasicMH = user32.GetWindowLongPtrW(hwnd, -4)
        else: self.__orig_BasicMH = user32.GetWindowLongW(hwnd, -4)
        self.__handle_setWindowFlags()
        if isAeroEnabled(): self.__setDWMEffect(self.__isblurwindow)
        self.__realdpi = getdpiforwindow(hwnd)
        self.__hdpisfroundingpolicy = 3
        self.__hdpiscalingenabled = hasattr(Qt, 'AA_EnableHighDpiScaling') and QApplication.testAttribute(Qt.AA_EnableHighDpiScaling)
        if hasattr(Qt, 'HighDpiScaleFactorRoundingPolicy'):
            QHDSFRP = Qt.HighDpiScaleFactorRoundingPolicy
            QADSFRP = QApplication.highDpiScaleFactorRoundingPolicy()
            policy_dict = {QHDSFRP.Ceil: 1, QHDSFRP.Floor: 2, QHDSFRP.PassThrough: 3, QHDSFRP.Round: 4, QHDSFRP.RoundPreferFloor: 5}
            self.__hdpisfroundingpolicy = 3 if hasattr(QHDSFRP, 'Unset') and QADSFRP == QHDSFRP.Unset else policy_dict[QADSFRP]
        dpi = self.dpi()
        self.__themeclr = 0
        self.__isdarktheme = isdarktheme()
        self.__titletextclr_l_ac, self.__titletextclr_d_ac, self.__titletextclr_l_in, self.__titletextclr_d_in, self.__menubtnclr_l_ac, self.__menubtnclr_d_ac, self.__menubtnclr_l_in, self.__menubtnclr_d_in = [Qt.black, Qt.white, QColor(*[99] * 3), QColor(*[155] * 3)] * 2
        self.__updatedpiconstants()
        self.__inminbtn, self.__inmaxbtn, self.__inclosebtn, self.__intitlebar, self.__inbd_t, self.__inbd_l, self.__inbd_b, self.__inbd_r = [False] * 8
        self.__captionfont = getcaptionfont()
        self.__mgn_l, self.__mgn_t, self.__mgn_r, self.__mgn_b = [0] * 4
        self.__bgLbl = BgLbl(self)
        self.__mainLyt = SystemVBoxLyt(self)
        self.setLayout(self.__mainLyt)
        self.__mainLyt.addWidget(self.__bgLbl)
        self.__bgLyt = SystemVBoxLyt(self)
        self.__bgLbl.setLayout(self.__bgLyt)
        self.__titleBar = TitleBar(self)
        self.__titleBarLyt = TitleBarLyt(self)
        self.__titleBar.setLayout(self.__titleBarLyt)
        self.__clientAreaLbl = ClientAreaLbl(self)
        self.clientArea = QWidget(self.__clientAreaLbl)
        self.__titleIconLyt = TitleIconLyt(self)
        self.__titleIconContainerLbl = TitleIconContainerLbl(self)
        self.__titleIconContainerLbl.setLayout(self.__titleIconLyt)
        self.__titleIconLbl = TitleIconLbl(self)
        self.__titleIconLyt.addWidget(self.__titleIconLbl)
        self.__titleTextLbl = TitleTextLbl(self)
        self.__minBtn, self.__maxBtn, self.__closeBtn = MinBtn(self), MaxBtn(self), CloseBtn(self)
        list(map(self.__bgLyt.addWidget, [self.__titleBar, self.__clientAreaLbl]))
        list(map(self.__titleBarLyt.addWidget, [self.__titleIconContainerLbl, self.__titleTextLbl, self.__minBtn, self.__maxBtn, self.__closeBtn]))
        self.setDarkTheme(0)
        if not ISPYSIDE1: self.windowHandle().screenChanged.connect(self.__updatencarea)
    def dpi(self):
        '''DPI divided by 96.0 is the scale factor of PySideX UI.
Example:
DPI = window.dpi()
window.resize(int(400.0 * DPI / 96.0), int(175.0 * DPI / 96.0))'''
        return self.__getdpibyrealdpi(self.realdpi())
    def realdpi(self):
        '''REALDPI divided by 96.0 is the scale factor of System UI.'''
        return self.__realdpi
    def hwnd(self):
        '''HWND is the window handle of this window.'''
        return self.__hwnd
    def isDarkTheme(self):
        '''Detect whether dark theme is enabled or not.
You can use 'setDarkTheme' to change setting.'''
        return self.__isdarktheme
    def setDarkTheme(self, themecolour=0):
        '''themecolour=0: Auto; themecolour=1: Light; themecolour=2: Dark'''
        self.__themeclr = themecolour
        try: self.__isdarktheme = {0: isdarktheme(), 1: False, 2: True}[themecolour]
        except:
            ErrorType = ValueError if type(themecolour) == int else TypeError
            raise ErrorType('Parameter themecolour must be 0, 1 or 2.')
        self.__minBtn.update()
        self.__maxBtn.update()
        self.__closeBtn.update()
        self.__titleBar.update()
        self.__clientAreaLbl.update()
        SWP_NOSIZE, SWP_NOMOVE, SWP_NOZORDER = 0x1, 0x2, 0x4
        hwnd = self.hwnd()
        try: list(map(ctypes.windll.dwmapi.DwmSetWindowAttribute, [hwnd] * 2, [19, 20], [ctypes.byref(ctypes.c_long(self.isDarkTheme()))] * 2, [ctypes.sizeof(ctypes.c_long(self.isDarkTheme()))] * 2))
        except: pass
        user32.SetWindowPos(hwnd, None, 0, 0, 0, 0, SWP_NOSIZE | SWP_NOMOVE | SWP_NOZORDER)
    def getWindowSizeByClientSize(self, size, dpimode=0):
        '''size=[width, height]: The size of client area
dpimode=0: Use PySideX DPI; dpimode=1: Use system DPI
Example:
client_size = [int(400 * window.dpi() / 96.0), int(175 * window.dpi() / 96.0)]
window_size = window.getWindowSizeByClientSize(client_size)
window.resize(*window_size)'''
        try: assert type(size[0]) == int and type(size[1]) == int and len(size) == 2
        except:
            ErrorType = ValueError if type(size) == list else TypeError
            raise ErrorType('Parameter size must be a list composed of two integers.')
        if dpimode not in [0, 1]:
            ErrorType = ValueError if type(dpimode) == int else TypeError
            raise ErrorType('Parameter dpimode must be 0 or 1.')
        NMAXFULL = not (user32.IsZoomed(self.hwnd()) or self.isFullScreen())
        f1 = lambda a: getattr(self, '_CustomizedWindow__' + ('real_' if dpimode else '') + a)
        bd_w, title_h = f1('bd_w'), f1('title_h')
        return [int(bd_w * (2 if NMAXFULL else 0) + size[0]), int(bd_w * int(NMAXFULL) + title_h + size[1])]
    def isAeroEnabled(self):
        '''Detect whether Aero is enabled or not.'''
        return isAeroEnabled()
    def setTitleTextColour(self, colour, theme=0, state=0):
        '''colour=0: Default; colour=Qt....: Qt.GlobalColor; colour=QColor(...): QColor
theme=0: Auto; theme=1: Light; theme=2: Dark
state=0: All; state=1: Active; state=2: Inactive'''
        if theme not in [0, 1, 2]:
            ErrorType = ValueError if type(theme) == int else TypeError
            raise ErrorType('Parameter theme must be 0, 1 or 2.')
        if state not in [0, 1, 2]:
            ErrorType = ValueError if type(state) == int else TypeError
            raise ErrorType('Parameter state must be 0, 1 or 2.')
        setlightclr, setdarkclr = theme in [0, 1], theme in [0, 2]
        setactiveclr, setinactiveclr = state in [0, 1], state in [0, 2]
        clr_l_ac, clr_d_ac, clr_l_in, clr_d_in = self.__titletextclr_l_ac, self.__titletextclr_d_ac, self.__titletextclr_l_in, self.__titletextclr_d_in
        if colour == 0:
            if setlightclr:
                if setactiveclr: clr_l_ac = Qt.black
                if setinactiveclr: clr_l_in = QColor(*[99] * 3)
            if setdarkclr:
                if setactiveclr: clr_d_ac = Qt.white
                if setinactiveclr: clr_d_in = QColor(*[155] * 3)
        elif type(colour) in [Qt.GlobalColor, QColor]:
            if setlightclr:
                if setactiveclr: clr_l_ac = colour
                if setinactiveclr: clr_l_in = colour
            if setdarkclr:
                if setactiveclr: clr_d_ac = colour
                if setinactiveclr: clr_d_in = colour
        else:
            ErrorType = ValueError if type(colour) == int else TypeError
            raise ErrorType('Parameter colour must be 0, %s or %s.' % (Qt.GlobalColor, QColor))
        self.__titletextclr_l_ac, self.__titletextclr_d_ac, self.__titletextclr_l_in, self.__titletextclr_d_in = clr_l_ac, clr_d_ac, clr_l_in, clr_d_in
        self.__titleTextLbl.update()
    def setMenuButtonColour(self, colour, theme=0, state=0):
        '''colour=0: Default; colour=Qt....: Qt.GlobalColor; colour=QColor(...): QColor
theme=0: Auto; theme=1: Light; theme=2: Dark
state=0: All; state=1: Active; state=2: Inactive'''
        if theme not in [0, 1, 2]:
            ErrorType = ValueError if type(theme) == int else TypeError
            raise ErrorType('Parameter theme must be 0, 1 or 2.')
        if state not in [0, 1, 2]:
            ErrorType = ValueError if type(state) == int else TypeError
            raise ErrorType('Parameter state must be 0, 1 or 2.')
        setlightclr, setdarkclr = theme in [0, 1], theme in [0, 2]
        setactiveclr, setinactiveclr = state in [0, 1], state in [0, 2]
        clr_l_ac, clr_d_ac, clr_l_in, clr_d_in = self.__menubtnclr_l_ac, self.__menubtnclr_d_ac, self.__menubtnclr_l_in, self.__menubtnclr_d_in
        if colour == 0:
            if setlightclr:
                if setactiveclr: clr_l_ac = Qt.black
                if setinactiveclr: clr_l_in = QColor(*[99] * 3)
            if setdarkclr:
                if setactiveclr: clr_d_ac = Qt.white
                if setinactiveclr: clr_d_in = QColor(*[155] * 3)
        elif type(colour) in [Qt.GlobalColor, QColor]:
            if setlightclr:
                if setactiveclr: clr_l_ac = colour
                if setinactiveclr: clr_l_in = colour
            if setdarkclr:
                if setactiveclr: clr_d_ac = colour
                if setinactiveclr: clr_d_in = colour
        else:
            ErrorType = ValueError if type(colour) == int else TypeError
            raise ErrorType('Parameter colour must be 0, %s or %s.' % (Qt.GlobalColor, QColor))
        self.__menubtnclr_l_ac, self.__menubtnclr_d_ac, self.__menubtnclr_l_in, self.__menubtnclr_d_in = clr_l_ac, clr_d_ac, clr_l_in, clr_d_in
        self.__minBtn.update()
        self.__maxBtn.update()
        self.__closeBtn.update()
    def setWindowTitle(self, arg__1):
        super(CustomizedWindow, self).setWindowTitle(arg__1)
        self.__titleTextLbl.update()
    def setWindowIcon(self, icon):
        super(CustomizedWindow, self).setWindowIcon(icon)
        self.__titleIconLbl.update()
    def setWindowFlag(self, arg__1, on=True):
        super(CustomizedWindow, self).setWindowFlag(arg__1, on)
        self.__handle_setWindowFlags()
    def setWindowFlags(self, type):
        super(CustomizedWindow, self).setWindowFlags(type)
        self.__handle_setWindowFlags()
    def __handle_setWindowFlags(self):
        self.__hwnd = gethwnd(self)
        hwnd = self.hwnd()
        windowlong = user32.GetWindowLongW(hwnd, -16)
        BasicMHAddr = self.__BasicMHAddr
        self.__orig_BasicMH = getattr(user32, 'GetWindowLong%sW' % ('Ptr' if hasattr(user32, 'GetWindowLongPtrW') else ''))(hwnd, -4)
        self.__orig_BasicMHFunc = self.__WNDPROC(self.__orig_BasicMH)
        self.__ncsizeinited, self.__windowinited = [False] * 2
        if ISPYSIDE1:
            self.__SWL(hwnd, -4, BasicMHAddr.value)
            ctypes.cdll.msvcrt._aligned_free(BasicMHAddr.value)
        self.__defaultSWL()
        self.__hasresizablebd, self.__hasminbtn, self.__hasmaxbtn = windowlong & 0x40000, windowlong & 0x20000, windowlong & 0x10000
        if isAeroEnabled(): self.__setDWMEffect(self.__isblurwindow)
        self.__updatencarea()
    def __setMBS(self, button, state=1):
        bgclr1, bgclr2, bgclr3 = [Qt.transparent] * 3
        f1 = lambda n: QColor(*[255 if self.isDarkTheme() else 0] * 3 + [n])
        _minmaxbg1, _minmaxbg2 = map(f1, [25, 50])
        if button == 1: bgclr1 = {1: _minmaxbg1, 2: _minmaxbg2}[state]
        elif button == 2: bgclr2 = {1: _minmaxbg1, 2: _minmaxbg2}[state]
        elif button == 3: bgclr3 = QColor(255, 0, 0, {0: 0, 1: 199, 2: 99}[state])
        self.__minBtn.bgclr, self.__maxBtn.bgclr, self.__closeBtn.bgclr = bgclr1, bgclr2, bgclr3
        self.__titleTextLbl.update()
        self.__minBtn.update()
        self.__maxBtn.update()
        self.__closeBtn.update()
    def MessageHandler(self, hwnd, message, wParam, lParam):
        '''Example:
class MyOwnWindow(BlurWindow):
|->|...
|->|def MessageHandler(self, hwnd, message, wParam, lParam):
|->||->|print(hwnd, message, wParam, lParam)
|->||->|...'''
        pass
    def __BasicMH(self, hwnd, message, wParam, lParam):
        WM_SIZE, WM_SHOWWINDOW, WM_SETTINGCHANGE, WM_STYLECHANGED, WM_NCCALCSIZE, WM_NCHITTEST, WM_NCLBUTTONDOWN, WM_NCLBUTTONUP, WM_SYSCOMMAND, WM_DPICHANGED, WM_DWMCOMPOSITIONCHANGED = 0x5, 0x18, 0x1a, 0x7d, 0x83, 0x84, 0xa1, 0xa2, 0x112, 0x2e0, 0x31e
        SC_SIZE, SC_MOVE, SC_MINIMIZE, SC_MAXIMIZE, SC_CLOSE, SC_RESTORE = 0xf000, 0xf010, 0xf020, 0xf030, 0xf060, 0xf120
        HTCLIENT, HTCAPTION, HTMINBUTTON, HTMAXBUTTON, HTCLOSE = 0x1, 0x2, 0x8, 0x9, 0x14
        HTLEFT, HTRIGHT, HTTOP, HTTOPLEFT, HTTOPRIGHT, HTBOTTOM, HTBOTTOMLEFT, HTBOTTOMRIGHT, HTBORDER = range(0xa, 0x13)
        SPI_SETNONCLIENTMETRICS, SPI_SETWORKAREA = 0x2a, 0x2f
        SWP_NOZORDER, SWP_FRAMECHANGED, SWP_NOSENDCHANGING = 0x4, 0x20, 0x400
        PM = lambda a: user32.PostMessageW(hwnd, WM_SYSCOMMAND, a, 0)
        try:
            dpi, realdpi = self.dpi(), self.realdpi()
            real_bd_w = self.__real_bd_w
            real_title_h = self.__real_title_h
            real_menubtn_w = self.__real_menubtn_w
            mgn_l, mgn_t, mgn_r, mgn_b = self.__mgn_l, self.__mgn_t, self.__mgn_r, self.__mgn_b
            flashinf = self.__flashinnextmessage_inf
        except: dpi, realdpi, real_bd_w, real_title_h, real_menubtn_w, mgn_l, mgn_t, mgn_r, mgn_b, flashinf = [96] * 2 + [0] * 7 + [[False, 0, 0, 0, 0]]
        resizable_h, resizable_v = self.minimumWidth() != self.maximumWidth(), self.minimumHeight() != self.maximumHeight()
        resizable_hv = resizable_h and resizable_v
        windowrc = RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(windowrc))
        windowx, windowy = windowrc.left, windowrc.top
        w, h = windowrc.right - windowx, windowrc.bottom - windowy
        globalpos = POINT()
        try:
            user32.GetPhysicalCursorPos(ctypes.byref(globalpos))
            user32.PhysicalToLogicalPoint(hwnd, ctypes.byref(globalpos))
        except: user32.GetCursorPos(ctypes.byref(globalpos))
        x, y = globalpos.x - windowx, globalpos.y - windowy
        intitlebar = mgn_t <= y < real_title_h + mgn_t
        inminbtn = w - mgn_r - 3 * real_menubtn_w <= x < w - mgn_r - 2 * real_menubtn_w and intitlebar
        inmaxbtn = w - mgn_r - 2 * real_menubtn_w <= x < w - mgn_r - real_menubtn_w and intitlebar
        inclosebtn = w - mgn_r - real_menubtn_w <= x < w - mgn_r and intitlebar
        inbd_t, inbd_l, inbd_b, inbd_r = y <= real_bd_w, x <= real_bd_w, h - y <= real_bd_w, w - x <= real_bd_w
        self.__inminbtn, self.__inmaxbtn, self.__inclosebtn, self.__intitlebar, self.__inbd_t, self.__inbd_l, self.__inbd_b, self.__inbd_r = inminbtn, inmaxbtn, inclosebtn, intitlebar, inbd_t, inbd_l, inbd_b, inbd_r
        if message == WM_SIZE:
            if flashinf[0]:
                user32.SetWindowPos(hwnd, None, flashinf[1], flashinf[2], flashinf[3], flashinf[4], SWP_NOZORDER | SWP_NOSENDCHANGING | 0x20)
                self.__flashinnextmessage_inf = [False, 0, 0, 0, 0]
            self.update()
        if message == WM_NCCALCSIZE:
            rc = (ctypes.cast(lParam, ctypes.POINTER(NCCALCSIZE_PARAMS)).contents.rgrc[0] if wParam else ctypes.cast(lParam, ctypes.POINTER(RECT)).contents)
            ISMAX, ISFULL = user32.IsZoomed(hwnd), self.isFullScreen()
            self.__mgn_l, self.__mgn_r, self.__mgn_t, self.__mgn_b = [0] * 4
            if ISMAX:
                width, height = rc.right - rc.left, rc.bottom - rc.top
                bestrc = getMonitorRectForWindow(hwnd, not ISFULL)
                maxmgn_list = [bestrc.left - rc.left, bestrc.top - rc.top, rc.right - bestrc.right, rc.bottom - bestrc.bottom]
                autohidetbpos = getautohidetbpos(bestrc)
                autohidetbwidth_list = [2 if i == autohidetbpos and not ISFULL else 0 for i in range(4)]
                f1 = lambda n: autohidetbwidth_list[n]
                f2 = lambda i: maxmgn_list[i] + f1(i)
                rcleft, rctop, rcright, rcbottom = bestrc.left + f1(0), bestrc.top + f1(1), rc.right, rc.bottom
                if maxmgn_list[2] >= 0 and resizable_h:
                    rcright = bestrc.right - f1(2)
                    rc.left, rc.right = rcleft, rcright
                if maxmgn_list[3] >= 0 and resizable_v:
                    rcbottom = bestrc.bottom - f1(3)
                    rc.top, rc.bottom = rctop, rcbottom
                if not (maxmgn_list[2] >= 0 and resizable_h and maxmgn_list[3] >= 0 and resizable_v): self.__maxwithmgn, self.__flashinnextmessage_inf = True, [True, rcleft, rctop, width, height]
                else: self.__maxwithmgn, self.__mgn_l, self.__mgn_t, self.__mgn_r, self.__mgn_b = False, f2(0), f2(1), f2(2), f2(3)
            if hasattr(self, '_CustomizedWindow__ncsizeinited'):
                __ncsizeinited = self.__ncsizeinited
                if not __ncsizeinited:
                    self.__ncsizeinited = True
                    if not ISPYSIDE1: return 0
                else: return 0
            else: return 0
        if message == WM_NCHITTEST:
            ISMAX, ISFULL = user32.IsZoomed(hwnd), self.isFullScreen()
            VK_LBUTTON = 0x1
            islbuttonpressed = user32.GetKeyState(VK_LBUTTON) not in [0, 1]
            if (resizable_h or resizable_v) and self.__hasresizablebd and not (ISMAX or ISFULL):
                if resizable_hv:
                    if inbd_t and inbd_l: res = HTTOPLEFT
                    elif inbd_t and inbd_r: res = HTTOPRIGHT
                    elif inbd_b and inbd_l: res = HTBOTTOMLEFT
                    elif inbd_b and inbd_r: res = HTBOTTOMRIGHT
                if not 'res' in vars():
                    if resizable_h:
                        if inbd_l: res = HTLEFT
                        elif inbd_r: res = HTRIGHT
                    if resizable_v:
                        if inbd_t: res = HTTOP
                        elif inbd_b: res = HTBOTTOM
            if not 'res' in vars():
                if inminbtn:
                    if self.__hasminbtn:
                        if not islbuttonpressed: self.__setMBS(1, 1)
                        res = HTMINBUTTON
                    else: res = HTBORDER
                elif inmaxbtn:
                    if self.__hasmaxbtn:
                        if not islbuttonpressed: self.__setMBS(2, 1)
                        res = HTMAXBUTTON
                    else: res = HTBORDER
                elif inclosebtn:
                    if not islbuttonpressed: self.__setMBS(3, 1)
                    res = HTCLOSE
                elif intitlebar: res = HTCAPTION
            if not 'res' in vars(): res = HTBORDER if (inbd_t or inbd_l or inbd_b or inbd_r) and not (ISMAX or ISFULL) else HTCLIENT
            if res not in [HTMINBUTTON, HTMAXBUTTON, HTCLOSE] and not islbuttonpressed: self.__setMBS(0)
            return res
        if message == WM_SHOWWINDOW:
            if not self.__windowinited:
                f1 = lambda a: user32.SetWindowPos(hwnd, None, windowx, windowy, w + a, h + a, SWP_NOZORDER | SWP_FRAMECHANGED | SWP_NOSENDCHANGING)
                f1(1), f1(0)
                self.__windowinited = True
        if message == WM_NCLBUTTONDOWN:
            if wParam in [HTMINBUTTON, HTMAXBUTTON, HTCLOSE]:
                self.__setMBS({HTMINBUTTON: 1, HTMAXBUTTON: 2, HTCLOSE: 3}[wParam], 2)
                return 0
            if wParam == HTCAPTION:
                ISMAX, ISFULL = user32.IsZoomed(hwnd), self.isFullScreen()
                f1 = lambda: user32.SetForegroundWindow(hwnd)
                if ISFULL:
                    f1()
                    return 0
                try: ctypes.windll.dwmapi.DwmSetIconicThumbnail
                except:
                    if ISMAX:
                        f1()
                        return 0
        if message == WM_NCLBUTTONUP:
            self.__setMBS(0)
            if wParam == HTMINBUTTON: PM(SC_MINIMIZE)
            elif wParam == HTMAXBUTTON:
                if user32.IsZoomed(hwnd): PM(SC_RESTORE)
                elif self.isFullScreen(): PM(SC_RESTORE)
                else: PM(SC_MAXIMIZE)
            elif wParam == HTCLOSE: PM(SC_CLOSE)
        if message == WM_DPICHANGED:
            rc = RECT.from_address(lParam)
            realdpi = wParam >> 16
            self.__realdpi = realdpi
            if not self.__hdpiscalingenabled:
                if not resizable_h: self.setFixedWidth(rc.right - rc.left)
                if not resizable_v: self.setFixedHeight(rc.bottom - rc.top)
                user32.SetWindowPos(hwnd, None, rc.left, rc.top, rc.right - rc.left, rc.bottom - rc.top, SWP_NOZORDER)
            self.__updatedpiconstants()
            self.__minBtn.update()
            self.__maxBtn.update()
            self.__closeBtn.update()
            self.__titleTextLbl.update()
            self.__titleIconLyt.updateMargin()
            self.__titleIconLbl.update()
            self.__clientAreaLbl.update()
            self.__updatencarea()
        if message == WM_SETTINGCHANGE:
            lParam_string = ctypes.c_wchar_p(lParam).value
            if wParam == SPI_SETWORKAREA or lParam_string == 'TraySettings': self.__updatencarea()
            if wParam == SPI_SETNONCLIENTMETRICS:
                self.__captionfont = getcaptionfont()
                self.__titleTextLbl.update()
            if lParam_string == 'ImmersiveColorSet': self.setDarkTheme(self.__themeclr)
        if message == WM_DWMCOMPOSITIONCHANGED:
            if isAeroEnabled(): self.__setDWMEffect(self.__isblurwindow)
            self.__bgLbl.update()
        if message == WM_STYLECHANGED:
            if hasattr(self, '_CustomizedWindow__ncsizeinited') and self.__ncsizeinited:
                newlong = user32.GetWindowLongW(hwnd, -16)
                if newlong & 0x80000: self.__defaultSWL()
                self.__hasresizablebd, self.__hasminbtn, self.__hasmaxbtn = newlong & 0x40000, newlong & 0x20000, newlong & 0x10000
        messagehandlerres = self.MessageHandler(hwnd, message, wParam, lParam)
        if messagehandlerres is not None: return messagehandlerres
        if ISPYSIDE1: return self.__orig_BasicMHFunc(hwnd, message, wParam, lParam)
    def nativeEvent(self, eventType, msg):
        '''For PySide2/6, you should define MessageHandler instead of nativeEvent.'''
        _msg = MSG.from_address(msg.__int__())
        basicmhres = self.__BasicMH(*list(map(getattr, [_msg] * 4, ['hWnd', 'message', 'wParam', 'lParam'])))
        if basicmhres is not None: return True, basicmhres
        return super(CustomizedWindow, self).nativeEvent(eventType, msg)
    def __setDWMEffect(self, blur=False):
        hwnd = self.hwnd()
        try:
            dwmapi = ctypes.windll.dwmapi
            f1 = lambda n: dwmapi.DwmExtendFrameIntoClientArea(hwnd, ctypes.byref(MARGINS(*[n] * 4)))
            if blur:
                w11_21h2_blur_code, w11_22h2_blur_code = setwin11blur(hwnd)
                if w11_22h2_blur_code:
                    f1(1)
                    dwmapi.DwmEnableBlurBehindWindow(ctypes.c_long(hwnd), ctypes.byref(DWM_BLURBEHIND(1, 1, 0, 0)))
                else:
                    f1(-1)
                    return 3
                try:
                    AeroEffect = Win10BlurEffect()
                    w10_blur_code = AeroEffect.setAeroEffect(hwnd, isEnableShadow=False)
                    if w10_blur_code != 0: return 2
                except: pass
            else: f1(1)
            return 1
        except: return 0
    def __getdpibyrealdpi(self, realdpi):
        realsf = realdpi / 96.0
        dpi = realdpi
        policy = self.__hdpisfroundingpolicy
        if self.__hdpiscalingenabled:
            try: sf = {1: int(realsf + 1 if realsf - int(realsf) > 0 else realsf), 2: int(realsf), 4: int(realsf + 1 if realsf - int(realsf) >= 0.5 else realsf), 5: int(realsf + 1 if realsf - int(realsf) > 0.5 else realsf)}[policy]
            except: sf = realsf
            dpi = int(float(realdpi) / sf)
        return dpi
    def __updatedpiconstants(self):
        dpi, realdpi = self.dpi(), self.realdpi()
        f1, f2 = lambda n: int(n * dpi / 96.0), lambda n: int(n * realdpi / 96.0)
        self.__bd_w, self.__real_bd_w = f1(4), f2(4)
        self.__title_h, self.__real_title_h = f1(30), f2(30)
        self.__menubtn_w, self.__real_menubtn_w = f1(46), f2(46)
        self.__title_fontsize = f1(13)
        self.__titleicon_mgn = f1(7)
    def splashScreen(self):
        '''You should call splashscreen.show after window.setWindowIcon, window.setDarkTheme.
Example:
window.resize(int(400 * window.dpi() / 96.0), int(175 * window.dpi() / 96.0))
window.setWindowIcon(QIcon('Icon.ico'))
splashscreen = window.splashScreen()
splashscreen.show()
...
window.show()
splashscreen.finish(window)'''
        return SplashScreen(self)


class BlurWindow(CustomizedWindow):
    '''A blur window based on PySideX.
Blur effect is avaliable on Windows Vista and newer.'''
    pass


if __name__ == '__main__':
    try:
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    except: pass
    app = QApplication(sys.argv)
    window = BlurWindow()
    window.setWindowFlags(Qt.WindowMaximizeButtonHint)
    help(window.MessageHandler)
    clr_list = [[QColor(0, 0, 139), QColor(119, 235, 255)], [1, 2], [1] * 2]
    list(map(*[window.setTitleTextColour] + clr_list))
    help(window.setTitleTextColour)
    list(map(*[window.setMenuButtonColour] + clr_list))
    help(window.setMenuButtonColour)
    window.setDarkTheme(0)
    help(window.setDarkTheme)
    window.setWindowIcon(QIcon('Icon.ico'))
    splashscreen = window.splashScreen()
    help(window.splashScreen)
    splashscreen.show()
    window.resize(*window.getWindowSizeByClientSize([int(400 * window.dpi() / 96.0), int(175 * window.dpi() / 96.0)]))
    window.setWindowTitle('Window')
    btn = QPushButton('Button', window.clientArea)
    btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    lbl = QLabel('Label', window.clientArea)
    lbl.setStyleSheet('background: rgba(255, 0, 0, 159)')
    lbl.setSizePolicy(*[QSizePolicy.Expanding] * 2)
    mainlyt = QVBoxLayout()
    mainlyt.setContentsMargins(*[0] * 4)
    mainlyt.setSpacing(0)
    window.clientArea.setLayout(mainlyt)
    list(map(mainlyt.addWidget, [btn, lbl]))
    window.show()
    splashscreen.finish(window)
    getattr(app, 'exec' if hasattr(app, 'exec') else 'exec_')()
