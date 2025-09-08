import sys
from PySide2.QtCore import QUrl, Qt
from PySide2.QtGui import QIcon, QKeySequence
from PySide2.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QToolBar, QAction,
    QLineEdit, QShortcut
)
from PySide2.QtWebEngineWidgets import QWebEngineView

HOME_URL = "https://www.duckduckgo.com"  # 원하면 다른 기본 페이지로 교체

def to_url(text: str) -> QUrl:
    # 사용자가 'example.com'만 입력해도 자동으로 http(s) 붙여줌
    return QUrl.fromUserInput(text.strip())

class BrowserWebView(QWebEngineView):
    """새 창 요청(=새 탭 열기)을 메인윈도우에 위임"""
    def __init__(self, main_window):
        super().__init__(parent=main_window)
        self.main_window = main_window

    def createWindow(self, _type):
        # target=_blank / window.open() → 새 탭으로 열기
        return self.main_window.add_blank_tab(switch_to=True)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini Browser (PySide2)")
        self.resize(1200, 800)

        # ---- 탭 위젯 ----
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(True)          # 드래그로 탭 순서 변경
        self.tabs.setTabsClosable(True)     # 탭 닫기 X 버튼
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_current_tab_changed)
        self.setCentralWidget(self.tabs)

        # ---- 툴바 & 주소창 ----
        nav = QToolBar("Navigation")
        nav.setMovable(False)
        self.addToolBar(nav)

        self.act_back = QAction("←", self)
        self.act_back.setStatusTip("뒤로 (Alt+Left)")
        self.act_back.triggered.connect(lambda: self.current_view().back())
        nav.addAction(self.act_back)

        self.act_forward = QAction("→", self)
        self.act_forward.setStatusTip("앞으로 (Alt+Right)")
        self.act_forward.triggered.connect(lambda: self.current_view().forward())
        nav.addAction(self.act_forward)

        self.act_reload = QAction("↻", self)
        self.act_reload.setStatusTip("새로고침 (Ctrl+R)")
        self.act_reload.triggered.connect(lambda: self.current_view().reload())
        nav.addAction(self.act_reload)

        nav.addSeparator()

        self.address_bar = QLineEdit(self)
        self.address_bar.setPlaceholderText("주소 또는 검색어 입력 후 Enter")
        self.address_bar.returnPressed.connect(self.load_from_address_bar)
        nav.addWidget(self.address_bar)

        self.act_new_tab = QAction("＋ 새 탭", self)
        self.act_new_tab.triggered.connect(lambda: self.add_new_tab(HOME_URL, switch_to=True))
        nav.addAction(self.act_new_tab)

        # ---- 단축키 ----
        self._setup_shortcuts()

        # ---- 첫 탭 ----
        self.add_new_tab(HOME_URL, switch_to=True)

    # ========= 탭 생성/연결 =========
    def add_blank_tab(self, switch_to: bool = True) -> BrowserWebView:
        view = BrowserWebView(self)
        idx = self.tabs.addTab(view, "새 탭")
        if switch_to:
            self.tabs.setCurrentIndex(idx)

        # 신호 연결: URL/제목/아이콘 변화 → UI 반영
        view.urlChanged.connect(lambda url, v=view: self._on_url_changed(v, url))
        view.titleChanged.connect(lambda title, v=view: self._on_title_changed(v, title))
        view.iconChanged.connect(lambda icon, v=view: self._on_icon_changed(v, icon))
        return view

    def add_new_tab(self, url_or_str=None, switch_to: bool = True) -> BrowserWebView:
        view = self.add_blank_tab(switch_to=switch_to)
        qurl = to_url(url_or_str) if isinstance(url_or_str, str) else (url_or_str or QUrl(HOME_URL))
        view.load(qurl)
        return view

    def current_view(self) -> BrowserWebView:
        return self.tabs.currentWidget()

    # ========= 신호 핸들러 =========
    def _on_url_changed(self, view: BrowserWebView, qurl: QUrl):
        if view is self.current_view():
            self.address_bar.setText(qurl.toDisplayString())

    def _on_title_changed(self, view: BrowserWebView, title: str):
        i = self.tabs.indexOf(view)
        if i != -1:
            self.tabs.setTabText(i, title if title else "새 탭")
        if view is self.current_view():
            self.setWindowTitle(f"{title} - Mini Browser" if title else "Mini Browser")

    def _on_icon_changed(self, view: BrowserWebView, icon: QIcon):
        i = self.tabs.indexOf(view)
        if i != -1:
            self.tabs.setTabIcon(i, icon)

    def on_current_tab_changed(self, index: int):
        view = self.current_view()
        if view:
            self.address_bar.setText(view.url().toDisplayString())
            self.setWindowTitle(f"{view.title()} - Mini Browser" if view.title() else "Mini Browser")
        # 뒤/앞 이동 가능 여부 업데이트(선택사항)
        self.act_back.setEnabled(view and view.history().canGoBack())
        self.act_forward.setEnabled(view and view.history().canGoForward())

    # ========= 동작 =========
    def load_from_address_bar(self):
        text = self.address_bar.text()
        if not text:
            return
        self.current_view().load(to_url(text))

    def load_from_address_bar_in_new_tab(self):
        text = self.address_bar.text()
        if not text:
            return
        self.add_new_tab(text, switch_to=True)

    def close_tab(self, index: int = None):
        if index is None:
            index = self.tabs.currentIndex()
        if self.tabs.count() > 1:
            w = self.tabs.widget(index)
            self.tabs.removeTab(index)
            w.deleteLater()
        else:
            # 마지막 탭은 비우기만
            self.current_view().setUrl(QUrl("about:blank"))

    def switch_relative(self, delta: int):
        n = self.tabs.count()
        if n == 0:
            return
        self.tabs.setCurrentIndex((self.tabs.currentIndex() + delta) % n)

    def switch_to_index(self, index: int):
        if 0 <= index < self.tabs.count():
            self.tabs.setCurrentIndex(index)

    # ========= 단축키 =========
    def _setup_shortcuts(self):
        # 새 탭 / 닫기 / 새로고침 / 주소창 포커스
        QShortcut(QKeySequence("Ctrl+T"), self, activated=lambda: self.add_new_tab(HOME_URL, switch_to=True))
        QShortcut(QKeySequence("Ctrl+W"), self, activated=lambda: self.close_tab())
        QShortcut(QKeySequence("Ctrl+R"), self, activated=lambda: self.current_view().reload())
        QShortcut(QKeySequence("Ctrl+L"), self, activated=self._focus_address_bar)

        # 앞/뒤로 (브라우저 유사)
        QShortcut(QKeySequence("Alt+Left"), self, activated=lambda: self.current_view().back())
        QShortcut(QKeySequence("Alt+Right"), self, activated=lambda: self.current_view().forward())

        # 탭 전환
        QShortcut(QKeySequence("Ctrl+Tab"), self, activated=lambda: self.switch_relative(+1))
        QShortcut(QKeySequence("Ctrl+Shift+Tab"), self, activated=lambda: self.switch_relative(-1))

        # 번호로 탭 이동 (Ctrl+1..8), Ctrl+9=마지막 탭
        for i in range(1, 9):
            QShortcut(QKeySequence(f"Ctrl+{i}"), self, activated=lambda i=i: self.switch_to_index(i - 1))
        QShortcut(QKeySequence("Ctrl+9"), self, activated=lambda: self.switch_to_index(self.tabs.count() - 1))

        # 주소창의 입력을 "새 탭으로 열기" (Chrome의 Alt+Enter 유사)
        QShortcut(QKeySequence("Alt+Return"), self.address_bar, activated=self.load_from_address_bar_in_new_tab)

    def _focus_address_bar(self):
        self.address_bar.setFocus(Qt.ShortcutFocusReason)
        self.address_bar.selectAll()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Mini Browser")
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
