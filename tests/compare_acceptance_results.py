"""Compara resultados ANTES vs DESPUÉS de la batería de aceptación.

Produce un reporte Markdown con métricas agregadas por caso y globales.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(ROOT))

BEFORE_DIR = ROOT / "tests" / "results"
AFTER_DIR = ROOT / "tests" / "results_after"


def load_results(directory: Path):
    results = {}
    for path in sorted(directory.glob("test_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        results[path.stem] = data
    return results


def is_clean_category(category: str) -> bool:
    if not category:
        return False
    if len(category) > 30:
        return False
    lower = category.lower()
    noise = {
        "artículos promocionales",
        "articulos promocionales",
        "categorias",
        "categorías",
        "newsletter",
        "marcas",
        "urban",
        "chili",
        "boompods",
        "menú",
        "menu",
        "ver todo",
    }
    return not any(term in lower for term in noise)


def is_clean_reason(reason: str) -> bool:
    if not reason:
        return False
    # Debe ser corto, sin listas de referencias ni fechas de stock.
    if len(reason) > 250:
        return False
    lower = reason.lower()
    bad = ["ref:", "sku", "existencias", "bodega", "caja master", "precio actualizado"]
    return not any(b in lower for b in bad)


def metrics_for_case(data: dict) -> dict:
    proposals = data.get("proposal_set", {}).get("proposals", [])
    stats = data.get("proposal_set", {}).get("statistics", {})
    items = []
    for p in proposals:
        items.extend(p.get("items", []))

    clean_categories = sum(1 for it in items if is_clean_category(it.get("category", "")))
    clean_reasons = sum(1 for it in items if is_clean_reason(it.get("selection_reason", "")))

    categories = [it.get("category", "") for it in items]
    unique_categories = len(set(c for c in categories if c))

    mode_counts = {}
    for p in proposals:
        mode_counts[p.get("generation_mode", "unknown")] = mode_counts.get(
            p.get("generation_mode", "unknown"), 0
        ) + 1

    return {
        "proposals": len(proposals),
        "items": len(items),
        "items_per_proposal": round(len(items) / len(proposals), 2) if proposals else 0,
        "clean_categories": clean_categories,
        "clean_categories_pct": round(100 * clean_categories / len(items), 1) if items else 0,
        "clean_reasons": clean_reasons,
        "clean_reasons_pct": round(100 * clean_reasons / len(items), 1) if items else 0,
        "unique_categories": unique_categories,
        "budget_util_min": stats.get("budget_utilization_min", 0),
        "budget_util_max": stats.get("budget_utilization_max", 0),
        "budget_util_avg": stats.get("budget_utilization_avg", 0),
        "max_similarity": stats.get("max_similarity", 0),
        "category_coverage": stats.get("category_coverage", 0),
        "reused_products": stats.get("reused_products", 0),
        "mode_counts": mode_counts,
    }


def build_report(before: dict, after: dict) -> str:
    lines = [
        "# Quality Pass: Reporte ANTES vs DESPUÉS",
        "",
        "Comparación de la batería de aceptación tras aplicar limpieza de datos, "
        "motor de afinidad por industria, modos de generación configurables y "
        "nuevos criterios de evaluación.",
        "",
        "| Métrica | ANTES | DESPUÉS | Δ |",
        "|---|---|---|---|",
    ]

    def aggregate(results: dict):
        totals = {
            "proposals": 0,
            "items": 0,
            "clean_categories": 0,
            "clean_reasons": 0,
            "budget_util_avg": 0.0,
            "max_similarity": 0.0,
            "category_coverage": 0,
            "reused_products": 0,
        }
        for m in results.values():
            totals["proposals"] += m["proposals"]
            totals["items"] += m["items"]
            totals["clean_categories"] += m["clean_categories"]
            totals["clean_reasons"] += m["clean_reasons"]
            totals["budget_util_avg"] += m["budget_util_avg"]
            totals["max_similarity"] += m["max_similarity"]
            totals["category_coverage"] += m["category_coverage"]
            totals["reused_products"] += m["reused_products"]
        n = len(results)
        return {
            "avg_items_per_proposal": round(totals["items"] / totals["proposals"], 2) if totals["proposals"] else 0,
            "clean_categories_pct": round(100 * totals["clean_categories"] / totals["items"], 1) if totals["items"] else 0,
            "clean_reasons_pct": round(100 * totals["clean_reasons"] / totals["items"], 1) if totals["items"] else 0,
            "budget_util_avg": round(totals["budget_util_avg"] / n, 1) if n else 0,
            "max_similarity": round(totals["max_similarity"] / n, 3) if n else 0,
            "category_coverage": round(totals["category_coverage"] / n, 1) if n else 0,
            "reused_products": totals["reused_products"],
        }

    b = aggregate(before)
    a = aggregate(after)

    def row(label, key, fmt="{:.1f}", is_pct=False):
        bv = b[key]
        av = a[key]
        delta = av - bv
        if is_pct:
            return f"| {label} | {bv:.1f}% | {av:.1f}% | {delta:+.1f}% |"
        if fmt == "{:.0f}":
            return f"| {label} | {bv:.0f} | {av:.0f} | {delta:+.0f} |"
        return f"| {label} | {fmt.format(bv)} | {fmt.format(av)} | {fmt.format(delta)} |"

    lines.append(row("Items por propuesta", "avg_items_per_proposal", "{:.2f}"))
    lines.append(row("Categorías limpias", "clean_categories_pct", is_pct=True))
    lines.append(row("Selection reasons limpias", "clean_reasons_pct", is_pct=True))
    lines.append(row("Utilización presupuesto", "budget_util_avg", is_pct=True))
    lines.append(row("Similitud máxima entre propuestas", "max_similarity", "{:.3f}"))
    lines.append(row("Cobertura de categorías", "category_coverage", "{:.1f}"))
    lines.append(row("Productos reutilizados", "reused_products", "{:.0f}"))

    lines.extend(["", "## Detalle por caso", ""])
    lines.append("| Caso | Items/prop | Cat limpias | Razones limpias | Util % | Sim max | Modos |")
    lines.append("|---|---|---|---|---|---|---|")

    for case_id in sorted(after.keys()):
        m = after[case_id]
        modes = ", ".join(f"{k}={v}" for k, v in m["mode_counts"].items())
        lines.append(
            f"| {case_id} | {m['items_per_proposal']} | {m['clean_categories_pct']}% | "
            f"{m['clean_reasons_pct']}% | {m['budget_util_avg']}% | {m['max_similarity']:.3f} | {modes} |"
        )

    lines.extend(["", "## Observaciones", ""])
    lines.append(
        "- ANTES = resultados del commit base `d41b1d8` (Vertical Slice 11 Global Generation)."
    )
    lines.append(
        "- DESPUÉS = resultados tras el Quality Pass con catálogo re-indexado y sanitizado."
    )
    lines.append(
        "- 'Categorías limpias' mide que la categoría no contenga texto de menú de navegación, "
        "newsletter ni listas de categorías del sitio."
    )
    lines.append(
        "- 'Razones limpias' mide que `selection_reason` no contenga referencias, stock, logística ni textos largos."
    )
    lines.append(
        "- La reutilización controlada de productos entre propuestas del mismo set es aceptable "
        "cuando se justifica por diversidad de categorías y presupuesto."
    )

    return "\n".join(lines)


def main():
    before = load_results(BEFORE_DIR)
    after = load_results(AFTER_DIR)
    before_metrics = {k: metrics_for_case(v) for k, v in before.items()}
    after_metrics = {k: metrics_for_case(v) for k, v in after.items()}
    report = build_report(before_metrics, after_metrics)
    output_path = ROOT / "tests" / "quality_pass_report.md"
    output_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nReporte guardado en: {output_path}")


if __name__ == "__main__":
    main()
