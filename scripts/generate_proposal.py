from promotional_gifts.container import build_generate_proposal_use_case


def main() -> None:
    use_case = build_generate_proposal_use_case()

    print("Asistente de propuestas comerciales (modo consola)")
    print("Ejemplo: Necesito 3800 regalos de cumpleaños con un "
          "presupuesto máximo de 25000 COP por unidad")
    print("Escribe 'q' para salir.\n")

    while True:
        text = input("Solicitud: ").strip()
        if text.lower() in ("q", "quit", "salir"):
            break
        if not text:
            continue

        proposals = use_case.execute(text)
        if not proposals:
            print("No se encontraron propuestas para esa solicitud.\n")
            continue

        for proposal in proposals:
            print("=" * 40)
            print(proposal.name)
            print(f"Score: {proposal.score:.1f}")
            print(f"Costo por unidad: {proposal.per_unit_cost}")
            print(f"Costo total: {proposal.total_cost}")
            print("Productos")
            for item in proposal.items:
                print(f"- {item.name} "
                      f"(ref {item.reference}, {item.quantity} uds)")
            for warning in proposal.warnings:
                print(f"! {warning}")
            if proposal.commercial_description:
                print()
                print("Descripción comercial")
                print(proposal.commercial_description)
            print()

        print()


if __name__ == "__main__":
    main()
