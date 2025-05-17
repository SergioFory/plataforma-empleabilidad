"""
CLI · Plataforma de Empleabilidad
================================
Ejecuta, en orden, los pasos del Módulo 1:

1. Intake & Diagnóstico            -> intake_wizard
2. BrandCanvas (PDF + JSON)        -> brand_canvas_wizard
3. Plan de Contenidos (DOCX)       -> content_plan_wizard
4. Guía de Networking LinkedIn     -> networking_ppt
5. Análisis de Demanda Laboral     -> demand_analysis

Cada paso guarda su resultado en el contexto compartido del WorkflowManager.
"""

from employ_toolkit.core import storage, workflow
from employ_toolkit.modules import (
    intake,
    brand_canvas,
    content_plan,
    linkedin_networking,
    demand_analysis,
)


def main() -> None:
    # 1) Asegurar la base de datos SQLite
    storage.init_db()

    # 2) Crear gestor de flujo
    wm = workflow.WorkflowManager()

    # -------------------------- PASOS -------------------------- #
    wm.run_step("intake", intake.intake_wizard)

    wm.run_step("brand_canvas", brand_canvas.brand_canvas_wizard)

    wm.run_step("content_plan", content_plan.content_plan_wizard)

    wm.run_step("linkedin_networking", linkedin_networking.networking_ppt)

    wm.run_step("demand_analysis", demand_analysis.demand_analysis)
    # ----------------------------------------------------------- #

    # 3) Contexto final (debug)
    print("\n=== Contexto final ===")
    for step, result in wm.context.items():
        print(f"• {step}: {result}")


if __name__ == "__main__":
    main()

