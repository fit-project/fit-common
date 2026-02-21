from fit_common.gui import ui_translation


class _FakeAction:
    def __init__(self, name, text="", tooltip="", statustip=""):
        self._name = name
        self._text = text
        self._tooltip = tooltip
        self._statustip = statustip

    def objectName(self):
        return self._name

    def text(self):
        return self._text

    def setText(self, value):
        self._text = value

    def toolTip(self):
        return self._tooltip

    def setToolTip(self, value):
        self._tooltip = value

    def statusTip(self):
        return self._statustip

    def setStatusTip(self, value):
        self._statustip = value


class _FakeWidget:
    def __init__(
        self,
        name="",
        text="",
        placeholder="",
        title="",
        tooltip="",
        statustip="",
        children=None,
        actions=None,
    ):
        self._name = name
        self._text = text
        self._placeholder = placeholder
        self._title = title
        self._tooltip = tooltip
        self._statustip = statustip
        self._children = children or []
        self._actions = actions or []

    def objectName(self):
        return self._name

    def text(self):
        return self._text

    def setText(self, value):
        self._text = value

    def placeholderText(self):
        return self._placeholder

    def setPlaceholderText(self, value):
        self._placeholder = value

    def title(self):
        return self._title

    def setTitle(self, value):
        self._title = value

    def toolTip(self):
        return self._tooltip

    def setToolTip(self, value):
        self._tooltip = value

    def statusTip(self):
        return self._statustip

    def setStatusTip(self, value):
        self._statustip = value

    def findChildren(self, *_args, **_kwargs):
        return self._children

    def actions(self):
        return self._actions


class _FakeTabWidget(_FakeWidget):
    def __init__(self, name, tabs):
        super().__init__(name=name, text="x")
        self._tabs = list(tabs)

    def count(self):
        return len(self._tabs)

    def tabText(self, idx):
        return self._tabs[idx]

    def setTabText(self, idx, value):
        self._tabs[idx] = value


def test_apply_translation_updates_widget_fields_and_tabs(monkeypatch):
    monkeypatch.setattr(ui_translation.QtWidgets, "QTabWidget", _FakeTabWidget)
    widget = _FakeTabWidget("panel", ["One", "Two"])
    widget._tooltip = "tip"
    ui_translation._apply_translation(
        {"PANEL": "Panel", "PANEL__TAB_0": "Uno", "PANEL__TAB_1": "Due"},
        widget,
    )
    assert widget._text == "Panel"
    assert widget._tabs == ["Uno", "Due"]


def test_apply_action_translation_updates_fields():
    action = _FakeAction("open_action", text="Open", tooltip="tip", statustip="st")
    ui_translation._apply_action_translation({"OPEN_ACTION": "Apri"}, action)
    assert action._text == "Apri"
    assert action._tooltip == "Apri"
    assert action._statustip == "Apri"


def test_translate_ui_traverses_children_and_actions(monkeypatch):
    monkeypatch.setattr(ui_translation.QtWidgets, "QTabWidget", _FakeTabWidget)
    child = _FakeWidget(name="child_label", text="Child")
    action = _FakeAction("save_action", text="Save")
    root = _FakeWidget(name="root_label", text="Root", children=[child], actions=[action])

    ui_translation.translate_ui(
        {
            "ROOT_LABEL": "Radice",
            "CHILD_LABEL": "Figlio",
            "SAVE_ACTION": "Salva",
        },
        root,
    )

    assert root._text == "Radice"
    assert child._text == "Figlio"
    assert action._text == "Salva"
