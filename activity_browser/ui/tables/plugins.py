# -*- coding: utf-8 -*-
from PySide2 import QtWidgets, QtCore
from PySide2.QtWidgets import QMessageBox

from ...signals import signals
from .delegates import CheckboxDelegate
from .models.plugins import PluginsModel
from .views import ABDataFrameView

class PluginsTable(ABDataFrameView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.verticalHeader().setVisible(False)
        self.setSelectionMode(QtWidgets.QTableView.SingleSelection)
        self.setItemDelegateForColumn(0, CheckboxDelegate(self))
        self.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Maximum
        ))
        self.model = PluginsModel(parent=self)
        self._connect_signals()

    def _connect_signals(self):
        self.model.updated.connect(self.update_proxy_model)
        self.model.updated.connect(self.custom_view_sizing)
        self.model.updated.connect(self.resizeColumnsToContents)

    def mousePressEvent(self, e):
        """
        NOTE: This is kind of hacky as we are deliberately sidestepping
        the 'delegate' system that should handle this.
        If this is important in the future: call self.edit(index)
        (inspired by: https://stackoverflow.com/a/11778012)
        """
        if e.button() == QtCore.Qt.LeftButton:
            proxy = self.indexAt(e.pos())
            if proxy.column() == 0:
                new_value = not bool(proxy.data())  
                plugin_name = self.model.get_plugin_name(proxy)
                if new_value:
                    signals.plugin_selected.emit(plugin_name)
                else:
                    msgBox = QMessageBox()
                    msgBox.setText("Remove plugin from project ?")
                    msgBox.setInformativeText("This will removed all data created by the plugin.")
                    msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                    msgBox.setDefaultButton(QMessageBox.Cancel)
                    ret = msgBox.exec_()
                    if ret == QMessageBox.Ok:
                        signals.plugin_deselected.emit(plugin_name)
                self.model.sync()
        super().mousePressEvent(e)

    @property
    def selected_plugin(self) -> str:
        """ Return the plugin name of the user-selected index.
        """
        return self.model.get_plugin_name(self.currentIndex())