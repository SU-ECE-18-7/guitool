# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import sys
import six  # NOQA
import traceback
from guitool.__PYQT__ import QtCore, QtGui
from guitool.__PYQT__ import QVariantHack
from guitool.__PYQT__.QtCore import Qt, QAbstractItemModel, QModelIndex, QObject
from guitool.__PYQT__.QtGui import QWidget
from guitool import qtype
import utool as ut
ut.noinject(__name__, '[PrefWidget2]', DEBUG=False)

VERBOSE_CONFIG = ut.VERBOSE or ut.get_argflag('--verbconf')

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


def report_thread_error(fn):
    """
    Decorator to help catch errors that QT wont report
    """
    def report_thread_error_wrapper(*args, **kwargs):
        try:
            ret = fn(*args, **kwargs)
            return ret
        except Exception as ex:
            print('\n\n *!!* Thread Raised Exception: ' + str(ex))
            print('\n\n *!!* Thread Exception Traceback: \n\n' + traceback.format_exc())
            sys.stdout.flush()
            et, ei, tb = sys.exc_info()
            raise
    return report_thread_error_wrapper


def qindexstr(index):
    return 'QIndex(%r, %r)' % (index.row(), index.column())


class ConfigValueDelegate(QtGui.QItemDelegate):
    """
    A delegate that decides what the editor should be for each row in a
    specific column

    CommandLine:
        python -m guitool.PrefWidget2 newConfigWidget --show
        python -m guitool.PrefWidget2 newConfigWidget --show --verbconf

    References:
        http://stackoverflow.com/questions/28037126/how-to-use-qcombobox-as-delegate-with-qtableview
        http://www.qtcentre.org/threads/41409-PyQt-QTableView-with-comboBox
        http://stackoverflow.com/questions/28680150/qtableview-data-in-background--cell-is-edited
    """
    def __init__(self, parent):
        super(ConfigValueDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        # Get Item Data
        # value = index.data(QtCore.Qt.DisplayRole).toInt()[0]
        leafNode = index.internalPointer()
        if VERBOSE_CONFIG and False:
            print('[DELEGATE] * painting editor for %s at %s' % (leafNode, qindexstr(index)))
        if leafNode.is_combo:
            curent_value = six.text_type(index.model().data(index))
            # fill style options with item data
            style = QtGui.QApplication.style()
            opt = QtGui.QStyleOptionComboBox()
            #optdict = {key: getattr(opt, key) for key in dir(opt)}
            #import utool
            #utool.embed()
            #print(dir(opt))
            #print('opt = %s' % (ut.repr3(optdict),))
            opt.currentText = curent_value
            opt.rect = option.rect
            opt.editable = False

            #style.State                      style.StateFlag                  style.State_NoChange             style.State_Sibling
            #style.State_Active               style.State_FocusAtBorder        style.State_None                 style.State_Small
            #style.State_AutoRaise            style.State_HasFocus             style.State_Off                  style.State_Sunken
            #style.State_Bottom               style.State_Horizontal           style.State_On                   style.State_Top
            #style.State_Children             style.State_Item                 style.State_Open                 style.State_UpArrow
            #style.State_DownArrow            style.State_KeyboardFocusChange  style.State_Raised               style.State_Window
            #style.State_Editing              style.State_Mini                 style.State_ReadOnly
            #style.State_Enabled              style.State_MouseOver            style.State_Selected

            #opt.state |= style.State_Raised
            #opt.state |= style.State_AutoRaise
            #opt.state |= style.State_Active
            #opt.state |= style.State_Editing

            if leafNode.qt_is_editable():
                opt.state |= style.State_Enabled
            #'activeSubControls': <PyQt4.QtGui.SubControls object at 0x7fb195966578>,
            #'currentIcon': <PyQt4.QtGui.QIcon object at 0x7fb19681b8a0>,
            #'currentText': '',
            #'direction': 0,
            #'editable': False,
            #'fontMetrics': <PyQt4.QtGui.QFontMetrics object at 0x7fb1959665f0>,
            #'frame': True,
            #'iconSize': PyQt4.QtCore.QSize(-1, -1),
            #'init': <built-in method init of QStyleOptionComboBox object at 0x7fb195966230>,
            #'initFrom': <built-in method initFrom of QStyleOptionComboBox object at 0x7fb195966230>,
            #'palette': <PyQt4.QtGui.QPalette object at 0x7fb1959666e0>,
            #'popupRect': PyQt4.QtCore.QRect(),
            #'rect': PyQt4.QtCore.QRect(),
            #'state': <PyQt4.QtGui.State object at 0x7fb195966848>,
            #'subControls': <PyQt4.QtGui.SubControls object at 0x7fb1959668c0>,
            #'type': 983044,
            #'version': 1,
            # draw item data as ComboBox
            #element = QtGui.QStyle.CE_ItemViewItem
            element = QtGui.QStyle.CE_ComboBoxLabel
            control = QtGui.QStyle.CC_ComboBox

            style.drawComplexControl(control, opt, painter)
            style.drawControl(element, opt, painter)
        else:
            return super(ConfigValueDelegate, self).paint(painter, option, index)

    def createEditor(self, parent, option, index):
        """
        Creates different editors for different types of data
        """
        leafNode = index.internalPointer()
        if VERBOSE_CONFIG:
            print('\n\n')
            print('[DELEGATE] newEditor for %s at %s' % (leafNode, qindexstr(index)))
        if leafNode is not None and leafNode.is_combo:
            import guitool
            options = leafNode.valid_values
            curent_value = index.model().data(index)
            if VERBOSE_CONFIG:
                print('[DELEGATE] * current_value = %r' % (curent_value,))
            editor = guitool.newComboBox(parent, options, default=curent_value)
            editor.currentIndexChanged['int'].connect(self.currentIndexChanged)
            editor.setAutoFillBackground(True)
            return editor
        elif leafNode is not None and leafNode.type_ is float:
            editor = QtGui.QDoubleSpinBox(parent)
            # TODO: min / max
            if False:
                editor.setMinimum(0.0)
                editor.setMaximum(1.0)
            editor.setSingleStep(0.1)
            editor.setAutoFillBackground(True)
            editor.setHidden(False)
            return editor
        elif leafNode is not None and leafNode.type_ is int:
            # TODO: Find a way for the user to enter a None into int boxes
            editor = QtGui.QSpinBox(parent)
            if False:
                editor.setMinimum(0)
                editor.setMaximum(1)
            editor.setSingleStep(1)
            editor.setAutoFillBackground(True)
            editor.setHidden(False)
            return editor
        else:
            editor = super(ConfigValueDelegate, self).createEditor(parent, option, index)
            editor.setAutoFillBackground(True)
            return editor

            # return None

    def setEditorData(self, editor, index):
        leafNode = index.internalPointer()
        if VERBOSE_CONFIG:
            print('[DELEGATE] setEditorData for %s at %s' % (leafNode, qindexstr(index)))
        if leafNode is not None and leafNode.is_combo:
            editor.blockSignals(True)
            current_data = index.model().data(index)
            if VERBOSE_CONFIG:
                print('[DELEGATE] * current_data = %r' % (current_data,))
            editor.setCurrentValue(current_data)
            editor.blockSignals(False)
        else:
            return super(ConfigValueDelegate, self).setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        leafNode = index.internalPointer()
        if VERBOSE_CONFIG:
            print('[DELEGATE] setModelData for %s at %s' % (leafNode, qindexstr(index)))
        if leafNode is not None and leafNode.is_combo:
            current_value = editor.currentValue()
            if VERBOSE_CONFIG:
                print('[DELEGATE] * current_value = %r' % (current_value,))
            model.setData(index, current_value)
        else:
            return super(ConfigValueDelegate, self).setModelData(editor, model, index)

    # @QtCore.pyqtSlot()
    def currentIndexChanged(self, combo_idx):
        if VERBOSE_CONFIG:
            print('[DELEGATE] Commit Data with combo_idx=%r' % (combo_idx,))
        self.commitData.emit(self.sender())

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    #def editorChanged(self, index):
    #    check = self.editor.itemText(index)
    #    id_seq = self.parent.selectedIndexes[0][0]
    #    update.updateCheckSeq(self.parent.db, id_seq, check)


class QConfigModel(QAbstractItemModel):
    """
    Convention states only items with column index 0 can have children
    """
    @report_thread_error
    def __init__(self, parent=None, rootNode=None):
        super(QConfigModel, self).__init__(parent)
        self.rootNode  = rootNode

    @report_thread_error
    def index2Pref(self, index=QModelIndex()):
        """ Internal helper method """
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item
        return self.rootNode

    #-----------
    # Overloaded ItemModel Read Functions
    @report_thread_error
    def rowCount(self, parent=QModelIndex()):
        parentPref = self.index2Pref(parent)
        return parentPref.qt_num_rows()

    @report_thread_error
    def columnCount(self, parent=QModelIndex()):
        parentPref = self.index2Pref(parent)
        return parentPref.qt_num_cols()

    @report_thread_error
    def data(self, qtindex, role=Qt.DisplayRole):
        """
        Returns the data stored under the given role
        for the item referred to by the qtindex.
        """
        if not qtindex.isValid():
            return QVariantHack()
        # Specify CheckState Role:
        flags = self.flags(qtindex)
        if role == Qt.CheckStateRole:
            if flags & Qt.ItemIsUserCheckable:
                data = self.index2Pref(qtindex).qt_get_data(qtindex.column())
                return Qt.Checked if data else Qt.Unchecked
        if role != Qt.DisplayRole and role != Qt.EditRole:
            return QVariantHack()
        nodePref = self.index2Pref(qtindex)
        data = nodePref.qt_get_data(qtindex.column())
        if isinstance(data, float):
            var = qtype.locale_float(data, 6)
        else:
            var = data
        return str(var)

    @report_thread_error
    def setData(self, qtindex, value, role=Qt.EditRole):
        """
        Sets the role data for the item at qtindex to value.
        """
        if role == Qt.EditRole:
            data = value
        elif role == Qt.CheckStateRole:
            data = (value == Qt.Checked)
        else:
            return False
        if VERBOSE_CONFIG:
            print('[setData] --- setData() ---')
        leafPref = self.index2Pref(qtindex)
        old_data = leafPref.qt_get_data(qtindex.column())
        if VERBOSE_CONFIG:
            print('[setData] old_data = %r' % (old_data,))
            print('[setData] value = %r' % value)
            print('[setData] type(data) = %r' % type(data))
            print('[setData] type(value) = %r' % type(value))
        result = leafPref.qt_set_data(data)
        if VERBOSE_CONFIG:
            if result:
                print('[setData] Notified of acceptance')
            else:
                print('[setData] Notified of rejection')
        self.dataChanged.emit(qtindex, qtindex)
        if VERBOSE_CONFIG:
            print('[setData] --- FINISH setData() ---')
        return True

    @report_thread_error
    def index(self, row, col, parent=QModelIndex()):
        """
        Returns the index of the item in the model specified
        by the given row, column and parent index.
        """
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()
        parentPref = self.index2Pref(parent)
        childPref  = parentPref.qt_child(row)
        if childPref:
            return self.createIndex(row, col, childPref)
        else:
            return QModelIndex()

    @report_thread_error
    def parent(self, index=None):
        """
        Returns the parent of the model item with the given index.
        If the item has no parent, an invalid QModelIndex is returned.
        """
        if index is None:  # Overload with QObject.parent()
            return QObject.parent(self)
        if not index.isValid():
            return QModelIndex()
        nodePref = self.index2Pref(index)
        parentPref = nodePref.qt_parent()
        if parentPref == self.rootNode:
            return QModelIndex()
        return self.createIndex(parentPref.qt_parents_index_of_me(), 0, parentPref)

    @report_thread_error
    def flags(self, index):
        """
        Returns the item flags for the given index.
        """
        if index.column() == 0:
            # The First Column is just a label and unchangable
            flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        elif not index.isValid():
            flags = Qt.ItemFlag(0)
        else:
            childPref = self.index2Pref(index)
            if childPref and childPref.qt_is_editable():
                if childPref.is_checkable():
                    flags = Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
                else:
                    flags = Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
            else:
                flags = Qt.ItemFlag(0)
        return flags

    @report_thread_error
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        Fills in column headers in table / tree views
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return QVariantHack('Config Key')
            if section == 1:
                return QVariantHack('Config Value')
        return QVariantHack()


BOOL_AS_COMBO = False


class ConfigNodeWrapper(ut.NiceRepr):
    """
    Wraps a dtool.Config object for internal qt use
    """
    def __init__(self, name=None, config=None, parent=None, param_info=None):
        self.name = name
        self.config = config
        self.parent = parent
        self.children = None
        self.value = None
        self.param_info = param_info
        self._populate_children()

    def make_tree_strlist(self, indent='', verbose=False):
        """
        Creates tree structured printable represntation
        """
        if self.parent is None:
            typestr = 'Root'
        elif self.children is None:
            typestr = 'Leaf'
        else:
            typestr = 'Node'

        strlist = []
        if True:
            strlist += [
                indent + '┌── ',
                indent + '┃ %s(name=%r):' % (typestr, self.name,),
            ]
        if self.is_leaf():
            strlist += [
                indent + '┃     value = %r' % (self.value,),
                indent + '┃     default = %r' % (self.default,),
            ]
        if verbose:
            strlist += [
                indent + '┃     type_ = %r' % (self.type_,),
                indent + '┃     is_combo = %r' % (self.is_combo,),
                indent + '┃     is_leaf = %r' % (self.is_leaf(),),
                indent + '┃     qt_num_rows = %r' % (self.qt_num_rows(),),
                indent + '┃     qt_is_editable = %r' % (self.qt_is_editable(),),
                indent + '┃     param_info = %r' % (self.param_info,),
            ]
        if True:
            strlist += [
                indent + '└──',
            ]
        for child in self.iter_children():
            childstr = child.make_tree_strlist(indent=indent + '|  ')
            strlist.extend(childstr)
        return strlist

    def print_tree(self):
        tree_str = '\n'.join(self.make_tree_strlist())
        print(tree_str)

    def __nice__(self):
        if self.is_leaf():
            return ' leaf(%s=%r)' % (self.name, self.value)
        else:
            return ' node(%s)' % (self.name)

    def _populate_children(self):
        if hasattr(self.config, 'items'):
            # Non-leaf
            self.children = []
            param_info_dict = self.config.get_param_info_dict()
            for key, val in self.config.items():
                param_info = param_info_dict[key]
                child_item = ConfigNodeWrapper(key, val, self, param_info)
                self.children.append(child_item)
        else:
            # Populate leaf
            self.value = self.config
            # Mark original value
            self.default = self.value
            self.children = None

    def _reset_to_default(self):
        if self.is_leaf():
            self.value = self.default
        else:
            for child in self.children:
                child._reset_to_default()

    def iter_children(self):
        if self.children is None:
            raise StopIteration()
        for child in self.children:
            yield child

    @property
    def type_(self):
        if self.param_info is None:
            return None
        else:
            return self.param_info.type_

    @property
    def is_combo(self):
        if self.param_info is None:
            return False
        elif BOOL_AS_COMBO and self.type_ is bool:
            return True
        else:
            return self.param_info.valid_values is not None

    @property
    def valid_values(self):
        if self.is_combo:
            if BOOL_AS_COMBO and self.type_ is bool:
                return [True, False]
            else:
                return self.param_info.valid_values
        else:
            return None

    def is_checkable(self):
        return not BOOL_AS_COMBO and self.type_ is bool

    def is_leaf(self):
        return self.children is None

    def qt_child(self, row):
        return self.children[row]

    def qt_parent(self):
        return self.parent

    def qt_is_editable(self):
        if self.is_leaf():
            enabled = self.param_info.is_enabled(self.parent.config)
        else:
            enabled = False
        return enabled

    def qt_num_rows(self):
        if self.children is None:
            return 0
        else:
            return len(self.children)

    def qt_num_cols(self):
        return 2

    def qt_get_data(self, column):
        if column == 0:
            return self.name
        data = self.value
        if data is None:
            data = 'None'
        return data

    def qt_set_data(self, qvar):
        """
        Sets backend data using QVariants
        """
        if VERBOSE_CONFIG:
            print('[Wrapper] Attempting to set data')
        if not self.is_leaf():
            raise Exception(' must be a leaf')
        if self.parent is None:
            raise Exception('[Pref.qtleaf] Cannot set root preference')
        if self.qt_is_editable():
            new_val = '[Pref.qtleaf] BadThingsHappenedInPref'
            new_val = ut.smart_cast(qvar, self.type_)
            if VERBOSE_CONFIG:
                print('[Wrapper] new_val=%r' % new_val)
                # print('[Wrapper] type(new_val)=%r' % type(new_val))
                # print('L____ [config.qt_set_leaf_data]')
            # TODO Add ability to set a callback function when certain
            # preferences are changed.
            self.value = new_val
            self.parent.config[self.name] = new_val
        if VERBOSE_CONFIG:
            print('[Wrapper] Accepted new value.')
        return True


class EditConfigWidget(QWidget):
    """
    Widget to edit a dtool.Config object
    """
    def __init__(self, rootNode):
        super(EditConfigWidget, self).__init__()
        self.init_layout()
        self.rootNode = rootNode
        self.config_model = QConfigModel(self, rootNode=rootNode)
        self.init_mvc()

    def init_layout(self):
        import guitool
        self.resize(668, 530)
        self.vbox = QtGui.QVBoxLayout(self)
        self.tree_view = QtGui.QTreeView(self)
        self.delegate = ConfigValueDelegate(self.tree_view)
        self.tree_view.setItemDelegateForColumn(1, self.delegate)
        self.vbox.addWidget(self.tree_view)
        self.hbox = QtGui.QHBoxLayout()
        self.default_but = guitool.newButton(self, 'Defaults', clicked=self.default_config)
        self.print_internals = guitool.newButton(self, 'Print Internals', clicked=self.print_internals)
        self.hbox.addWidget(self.default_but)
        self.hbox.addWidget(self.print_internals)
        self.vbox.addLayout(self.hbox)
        self.setWindowTitle(_translate('self', 'Edit Config Widget', None))

    def init_mvc(self):
        import operator
        edit_triggers = reduce(operator.__or__, [
            QtGui.QAbstractItemView.CurrentChanged,
            QtGui.QAbstractItemView.DoubleClicked,
            QtGui.QAbstractItemView.SelectedClicked,
            # QtGui.QAbstractItemView.EditKeyPressed,
            # QtGui.QAbstractItemView.AnyKeyPressed,
        ])
        self.tree_view.setEditTriggers(edit_triggers)
        self.tree_view.setModel(self.config_model)
        self.tree_view.header().resizeSection(0, 250)

        # from guitool import api_item_view
        # api_item_view.set_column_persistant_editor(self.tree_view, 1)
        # # Persistant editors
        # num_rows = 4  # self.tree_view.model.rowCount()
        # print('view.set_persistant: %r rows' % num_rows)
        # view = self.tree_view
        # model = self.config_model
        # column = 1
        # for row in range(num_rows):
        #     index  = model.index(row, column)
        #     view.openPersistentEditor(index)

    def default_config(self):
        print('Defaulting')
        self.rootNode._reset_to_default()
        self.refresh_layout()

    def print_internals(self):
        print('Print Internals')
        self.rootNode.print_tree()

    def refresh_layout(self):
        self.config_model.layoutAboutToBeChanged.emit()
        self.config_model.layoutChanged.emit()


def newConfigWidget(config):
    r"""
    Args:
        config (dtool.Config):

    CommandLine:
        python -m guitool.PrefWidget2 newConfigWidget --show
        python -m guitool.PrefWidget2 newConfigWidget --show --verbconf

    Example:
        >>> # DISABLE_DOCTEST
        >>> from guitool.PrefWidget2 import *  # NOQA
        >>> import guitool
        >>> guitool.ensure_qtapp()
        >>> import dtool
        >>> class ExampleConfig(dtool.Config):
        >>>     _param_info_list = [
        >>>         ut.ParamInfo('str_option', 'hello'),
        >>>         ut.ParamInfo('int_option', 42),
        >>>         ut.ParamInfo('float_option', 42.),
        >>>         ut.ParamInfo('combo_option', 'up', valid_values=['up', 'down', 'strange', 'charm', 'top', 'bottom']),
        >>>         ut.ParamInfo('bool_option', False),
        >>>         ut.ParamInfo('hidden_str', 'foobar', hideif=lambda cfg: not cfg['bool_option']),
        >>>         ut.ParamInfo('hidden_combo', 'one', valid_values=['oneA', 'twoB', 'threeC'], hideif=lambda cfg: not cfg['bool_option']),
        >>>     ]
        >>> config = ExampleConfig()
        >>> widget = newConfigWidget(config)
        >>> widget.rootNode.print_tree()
        >>> from plottool import fig_presenter
        >>> fig_presenter.register_qt4_win(widget)
        >>> widget.show()
        >>> ut.quit_if_noshow()
        >>> guitool.qtapp_loop(qwin=widget, freq=10)
    """
    rootNode = ConfigNodeWrapper('root', config)
    widget = EditConfigWidget(rootNode)
    return widget


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m guitool.PrefWidget2
        python -m guitool.PrefWidget2 --allexamples
    """
    import multiprocessing
    multiprocessing.freeze_support()  # for win32
    import utool as ut  # NOQA
    ut.doctest_funcs()