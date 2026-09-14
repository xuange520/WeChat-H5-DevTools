# -*- coding: utf-8 -*-
from PySide6.QtCore import QObject, Signal

class BridgeSignals(QObject):
    log_emitted = Signal(str, str)          # level, text
    status_updated = Signal(str, bool, str) # key, is_ok, msg
    progress_updated = Signal(int, str)     # percent, msg

bridge_signals = BridgeSignals()
