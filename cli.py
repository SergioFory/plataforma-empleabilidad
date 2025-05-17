"""
CLI de la Plataforma de Empleabilidad
------------------------------------
Ejecuta, en orden, los pasos básicos del Módulo 1:

1. Intake & Diagnóstico           → intake_wizard
2. BrandCanvas (Generar PDF/JSON) → brand_canvas_wizard
3. Análisis de Demanda Laboral    → demand_analysis

Cada paso guarda su resultado en el contexto
compartido por el WorkflowManager.
"""

from employ_toolkit.core import storage, workflow
from employ_toolkit.modules import intake, brand_canvas, demand_analysis


def main() -> None:
    # 1) Inicializar base de datos SQLite si no existe
    storage.init_db()

    # 2) Crear gestor de flujo con contexto compartido
    wm = workflow.WorkflowManager()

    # ----- Paso 1: Intake --------------------------------------------------
    wm.run_step("intake", intake.intake_wizard)

    # ----- Paso 2: BrandCanvas --------------------------------------------
    wm.run_step("brand_canvas", brand_canvas.brand_canvas_wizard)

    # ----- Paso 3: Análisis de demanda ------------------------------------
    wm.run_step("demand_analysis", demand_analysis.demand_analysis)

    # 3) Mostrar contexto final (debug/log)
    print("\n=== Contexto final ===")
    for step, result in wm.context.items():
        print(f"• {step}: {result}")


if __name__ == "__main__":
    main()
