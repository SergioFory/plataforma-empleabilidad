from employ_toolkit.core.workflow import WorkflowManager

def test_context_starts_empty():
    wm = WorkflowManager()
    assert wm.context == {}
