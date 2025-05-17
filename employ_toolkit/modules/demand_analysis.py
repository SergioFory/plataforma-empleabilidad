def demand_analysis(context, skills: list[str] | None = None):
    """Paso provisional: ingresa cargos manualmente."""
    print("Ingresa 3 cargos relevantes separados por coma:")
    cargos = input("> ").split(",")
    positions = [{"title": c.strip(), "sector": "N/A", "score": 0.8} for c in cargos]
    return positions
