from employ_toolkit.core import storage, workflow
from employ_toolkit.modules import intake, demand_analysis

def main():
    storage.init_db()
    wm = workflow.WorkflowManager()

    # 1) Intake
    wm.run_step("intake", intake.intake_wizard)

    # 2) Demand analysis (usa datos del contexto si lo deseas)
    wm.run_step("demand_analysis", demand_analysis.demand_analysis)

    print("\nContexto final:", wm.context)

if __name__ == "__main__":
    main()
