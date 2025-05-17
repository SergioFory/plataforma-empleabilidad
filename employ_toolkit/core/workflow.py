from typing import Dict, Any, Callable

class WorkflowManager:
    """Encadena pasos (sub-módulos) y comparte contexto."""
    def __init__(self) -> None:
        self.context: Dict[str, Any] = {}

    def run_step(self, name: str, func: Callable[..., Any], **kwargs) -> Any:
        print(f"▶ Ejecutando {name}…")
        output = func(self.context, **kwargs)
        self.context[name] = output
        return output
