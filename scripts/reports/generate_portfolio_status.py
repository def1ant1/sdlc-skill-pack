def generate_portfolio_status(portfolio):
    return {"summary": "Portfolio status generated", "clients": len(portfolio.get("clients", []))}
