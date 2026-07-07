from __future__ import annotations
from typing import Dict, Any
from aqt import mw
from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QSpinBox,
    QPushButton, QMessageBox, QAction, QTabWidget, QWidget
)
from .constants import (
    CFG_KEY_CENTER, CFG_KEY_HIGHLIGHT, CFG_KEY_RETRY_MS, CFG_KEY_MAX_TRIES, DEFAULTS
)
from .config import get_cfg, get_values, save_cfg
from .tab_support import SupportTabMixin, ADDON_PACKAGE


def _sb(name: str):
    """Return a QMessageBox StandardButton that works on PyQt6 and PyQt5."""
    try:
        # PyQt6-style enums
        return getattr(QMessageBox.StandardButton, name)
    except AttributeError:
        # PyQt5 fallback
        return getattr(QMessageBox, name)


class SettingsDialog(QDialog, SupportTabMixin):
    def __init__(self, parent=None, select_support_tab=False):
        super().__init__(parent)
        self.setWindowTitle("Last Deck Scroller - Settings")
        self._build_ui(select_support_tab)
        self._load_values()

    def _build_ui(self, select_support_tab=False):
        self.layout = QVBoxLayout(self)

        self.tabs = QTabWidget()

        # Settings tab
        self.settings_tab = QWidget()
        settings_layout = QVBoxLayout(self.settings_tab)
        settings_layout.setContentsMargins(15, 15, 15, 15)
        settings_layout.setSpacing(12)

        # Center on scroll
        self.cb_center = QCheckBox("Center on scroll")
        settings_layout.addWidget(self.cb_center)

        # Show highlight
        self.cb_highlight = QCheckBox("Show green outline highlight")
        settings_layout.addWidget(self.cb_highlight)

        # Retry timing
        row_retry = QHBoxLayout()
        row_retry.addWidget(QLabel("Retry interval (ms)"))
        self.spin_retry = QSpinBox()
        self.spin_retry.setRange(20, 5000)
        self.spin_retry.setSingleStep(20)
        row_retry.addWidget(self.spin_retry)
        settings_layout.addLayout(row_retry)

        # Max tries
        row_tries = QHBoxLayout()
        row_tries.addWidget(QLabel("Max tries"))
        self.spin_tries = QSpinBox()
        self.spin_tries.setRange(1, 100)
        self.spin_tries.setSingleStep(1)
        row_tries.addWidget(self.spin_tries)
        settings_layout.addLayout(row_tries)
        settings_layout.addStretch()

        # Add support tab
        self._create_support_tab()

        self.tabs.addTab(self.settings_tab, "Settings")
        self.tabs.addTab(self.support_tab, "Support")
        self.layout.addWidget(self.tabs)

        if select_support_tab:
            self.tabs.setCurrentWidget(self.support_tab)

        # Buttons
        btns = QHBoxLayout()
        self.btn_reset = QPushButton("Reset to defaults")
        self.btn_reset.clicked.connect(self._on_reset)
        btns.addWidget(self.btn_reset)

        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self._on_save)
        btns.addWidget(self.btn_save)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        btns.addWidget(self.btn_cancel)

        self.layout.addLayout(btns)

    def _load_values(self):
        _, _, center, highlight, retry_ms, max_tries = get_values()
        self.cb_center.setChecked(center)
        self.cb_highlight.setChecked(highlight)
        self.spin_retry.setValue(retry_ms)
        self.spin_tries.setValue(max_tries)

    def _on_save(self):
        cfg: Dict[str, Any] = get_cfg()
        cfg[CFG_KEY_CENTER] = bool(self.cb_center.isChecked())
        cfg[CFG_KEY_HIGHLIGHT] = bool(self.cb_highlight.isChecked())
        cfg[CFG_KEY_RETRY_MS] = int(self.spin_retry.value())
        cfg[CFG_KEY_MAX_TRIES] = int(self.spin_tries.value())
        save_cfg(cfg)
        self.accept()

    def _on_reset(self):
        yes = _sb("Yes")
        no = _sb("No")
        # Provide explicit buttons for both PyQt6 and PyQt5 compatibility
        res = QMessageBox.question(
            self,
            "Reset to defaults",
            "Reset all settings to defaults? This will also clear remembered last deck values.",
            yes | no,
            no,
        )
        if res == yes:
            cfg = dict(DEFAULTS)  # copy
            save_cfg(cfg)
            self._load_values()
            
            # Reset supporter opt-out
            meta = mw.addonManager.addonMeta(ADDON_PACKAGE)
            meta["supporter_opt_out"] = False
            mw.addonManager.writeAddonMeta(ADDON_PACKAGE, meta)
            self.load_supporter_state()


def open_settings(select_support_tab: bool = False):
    dlg = SettingsDialog(mw, select_support_tab=select_support_tab)
    # PyQt6 has exec(), PyQt5 has exec_()
    if hasattr(dlg, "exec"):
        dlg.exec()
    else:
        dlg.exec_()


def register_config_action():
    # Tolerate 0/1+ positional args across Anki versions
    def _action(*_args, **_kwargs):
        open_settings()
    try:
        mw.addonManager.setConfigAction(__name__, _action)
    except Exception:
        # Fallback: add a Tools menu item if config action is unavailable
        act = QAction("Last Deck Scroller - Settings", mw)
        act.triggered.connect(open_settings)
        mw.form.menuTools.addAction(act)
