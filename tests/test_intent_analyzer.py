import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from promotional_gifts.application.intent_analyzer import IntentAnalyzer


def check(query, expect_qty, expect_total, expect_per_unit):
    ia = IntentAnalyzer()
    intent = ia.analyze(query)
    ok = (
        intent.quantity == expect_qty
        and intent.budget_total == expect_total
        and intent.budget_per_unit == expect_per_unit
    )
    status = "PASS" if ok else "FAIL"
    print(
        f"[{status}] {query!r}\n"
        f"        qty={intent.quantity} (exp {expect_qty}) | "
        f"total={intent.budget_total} (exp {expect_total}) | "
        f"per_unit={intent.budget_per_unit} (exp {expect_per_unit})"
    )
    return ok


def main():
    cases = [
        # Casos nuevos (regresión)
        ("3800 regalos con presupuesto de 25000", 3800, None, 25000.0),
        ("3800 regalos con presupuesto máximo de 25000", 3800, None, 25000.0),
        ("3800 regalos con presupuesto total de 95000000", 3800, 95000000.0, None),
        ("3800 regalos hasta 25000 COP", 3800, None, 25000.0),
        ("3800 regalos 25000 COP por unidad", 3800, None, 25000.0),
        # Variaciones del enunciado
        ("3800 regalos de cumpleaños con presupuesto de 25.000", 3800, None, 25000.0),
        ("3800 regalos con presupuesto 25000", 3800, None, 25000.0),
        ("3800 regalos máximo 25000", 3800, None, 25000.0),
        ("3800 regalos 25000 pesos", 3800, None, 25000.0),
        ("3800 regalos 25.000 COP", 3800, None, 25000.0),
        ("3800 regalos 25.000 pesos", 3800, None, 25000.0),
        ("3800 regalos presupuesto por unidad de 25000", 3800, None, 25000.0),
        ("3800 regalos 25000 COP por unidad", 3800, None, 25000.0),
        ("3800 regalos con presupuesto global de 95000000", 3800, 95000000.0, None),
        ("3800 regalos con presupuesto completo de 95000000", 3800, 95000000.0, None),
        # Casos ya soportados (sin regresión)
        ("Necesito 3800 regalos de cumpleaños con un presupuesto máximo de 25000 COP por unidad", 3800, None, 25000.0),
        ("3800 regalos con presupuesto total de 95000000 COP", 3800, 95000000.0, None),
        # Sin cantidad: un número suelto es ambiguo y no debe asumirse por unidad
        ("presupuesto de 25000", None, None, None),
    ]

    passed = 0
    for query, qty, total, per in cases:
        if check(query, qty, total, per):
            passed += 1

    print(f"\nResumen: {passed}/{len(cases)} casos exitosos")
    return passed == len(cases)


if __name__ == "__main__":
    import sys
    ok = main()
    sys.exit(0 if ok else 1)
