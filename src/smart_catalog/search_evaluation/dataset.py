from .models import TestCase


def load_default_dataset() -> list[TestCase]:
    return [
        TestCase(
            query="USB",
            expected_families=["USB"],
            expected_results=["PUERTO USB APEX"],
            expected_count=20,
            tags=["producto_simple"],
        ),
        TestCase(
            query="pendrive",
            expected_families=["USB"],
            tags=["producto_simple", "sinonimo"],
        ),
        TestCase(
            query="memoria USB",
            expected_families=["USB"],
            tags=["producto_simple"],
        ),
        TestCase(
            query="flash drive",
            expected_families=["USB"],
            tags=["sinonimo_ingles"],
        ),
        TestCase(
            query="botilitos",
            expected_families=["BOTELLA"],
            tags=["producto_simple"],
        ),
        TestCase(
            query="botellas metalicas",
            expected_families=["BOTELLA"],
            expected_materials=["METAL"],
            tags=["producto_material"],
        ),
        TestCase(
            query="termos",
            expected_families=["TERMO"],
            expected_categories=["Termos"],
            tags=["producto_simple"],
        ),
        TestCase(
            query="tomatodo",
            expected_families=["BOTELLA"],
            tags=["sinonimo_colombiano"],
        ),
        TestCase(
            query="mugs",
            expected_families=["MUG"],
            tags=["producto_simple"],
        ),
        TestCase(
            query="vasos",
            expected_families=["VASO"],
            tags=["producto_simple"],
        ),
        TestCase(
            query="pocillo",
            expected_families=["VASO"],
            tags=["sinonimo_colombiano"],
        ),
        TestCase(
            query="lapiceros",
            expected_families=["LAPICERO"],
            tags=["producto_simple"],
        ),
        TestCase(
            query="esferos",
            expected_families=["LAPICERO"],
            tags=["sinonimo"],
        ),
        TestCase(
            query="boligrafo",
            expected_families=["BOLIGRAFO"],
            tags=["sinonimo"],
        ),
        TestCase(
            query="agendas",
            expected_families=["AGENDA"],
            tags=["producto_simple"],
        ),
        TestCase(
            query="libretas",
            expected_families=["LIBRETA"],
            tags=["producto_simple"],
        ),
        TestCase(
            query="cuadernos",
            expected_families=["LIBRETA"],
            tags=["producto_simple"],
        ),
        TestCase(
            query="bolsos",
            expected_families=["BOLSO"],
            tags=["producto_simple"],
        ),
        TestCase(
            query="mochilas",
            expected_families=["BOLSO"],
            tags=["producto_simple"],
        ),
        TestCase(
            query="maletines",
            expected_families=["MALETA"],
            tags=["producto_simple"],
        ),
        TestCase(
            query="tula",
            expected_families=["BOLSO"],
            tags=["sinonimo_colombiano"],
        ),
        TestCase(
            query="tote bag",
            expected_families=["BOLSO"],
            tags=["sinonimo_ingles"],
        ),
        TestCase(
            query="neveras",
            expected_families=["NEVERA"],
            tags=["producto_simple"],
        ),
        TestCase(
            query="gorras",
            expected_families=["GORRA"],
            tags=["producto_simple"],
        ),
        TestCase(
            query="llaveros",
            expected_families=["LLAVERO"],
            tags=["producto_simple"],
        ),
        TestCase(
            query="paraguas",
            expected_families=["PARAGUAS"],
            tags=["producto_simple"],
        ),
        TestCase(
            query="toallas",
            expected_families=["TOALLA"],
            tags=["producto_simple"],
        ),
        TestCase(
            query="audifonos",
            expected_families=["AUDIFONOS"],
            tags=["producto_simple"],
        ),
        TestCase(
            query="cascos",
            expected_families=["AUDIFONOS"],
            tags=["sinonimo"],
        ),
        TestCase(
            query="power bank",
            expected_families=["CARGADOR"],
            tags=["producto_simple"],
        ),
        TestCase(
            query="mouse",
            expected_families=["MOUSE"],
            tags=["producto_simple"],
        ),
        TestCase(
            query="raton",
            expected_families=["MOUSE"],
            tags=["sinonimo"],
        ),
        TestCase(
            query="calculadoras",
            expected_families=["CALCULADORA"],
            tags=["producto_simple"],
        ),
        TestCase(
            query="cargadores",
            expected_families=["CARGADOR"],
            tags=["producto_simple"],
        ),
        TestCase(
            query="cables",
            expected_families=["CABLE"],
            tags=["producto_simple"],
        ),
        TestCase(
            query="audifonos bluetooth",
            expected_families=["AUDIFONOS"],
            expected_technologies=["BLUETOOTH"],
            tags=["producto_tecnologia"],
        ),
        TestCase(
            query="cargador inalambrico qi",
            expected_families=["CARGADOR"],
            expected_technologies=["WIRELESS", "QI"],
            tags=["producto_tecnologia"],
        ),
        TestCase(
            query="billetera rfid",
            expected_families=["BILLETERA"],
            expected_technologies=["RFID"],
            tags=["producto_tecnologia"],
        ),
        TestCase(
            query="botella 600 ml",
            expected_families=["BOTELLA"],
            expected_capacity={"volume_ml": 600},
            tags=["producto_capacidad"],
        ),
        TestCase(
            query="termo 500ml",
            expected_families=["TERMO"],
            expected_capacity={"volume_ml": 500},
            tags=["producto_capacidad"],
        ),
        TestCase(
            query="power bank 10000 mah",
            expected_families=["CARGADOR"],
            expected_capacity={"battery_mah": 10000},
            tags=["producto_capacidad"],
        ),
        TestCase(
            query="bambu",
            expected_materials=["BAMBU"],
            tags=["material"],
        ),
        TestCase(
            query="RPET",
            expected_materials=["RPET"],
            tags=["material"],
        ),
        TestCase(
            query="corcho",
            expected_materials=["CORCHO"],
            tags=["material"],
        ),
        TestCase(
            query="madera",
            expected_materials=["MADERA"],
            tags=["material"],
        ),
        TestCase(
            query="metal",
            expected_materials=["METAL"],
            tags=["material"],
        ),
        TestCase(
            query="acero inoxidable",
            expected_materials=["METAL"],
            tags=["material"],
        ),
        TestCase(
            query="algodon",
            expected_materials=["ALGODON"],
            tags=["material"],
        ),
        TestCase(
            query="reciclado",
            expected_materials=["RPET"],
            tags=["material"],
        ),
        TestCase(
            query="ceramica",
            expected_materials=["CERAMICA"],
            tags=["material"],
        ),
        TestCase(
            query="vidrio",
            expected_materials=["VIDRIO"],
            tags=["material"],
        ),
        TestCase(
            query="productos ecologicos",
            expected_categories=["Eco"],
            tags=["concepto"],
        ),
        TestCase(
            query="productos premium",
            expected_attributes=["premium"],
            tags=["concepto"],
        ),
        TestCase(
            query="productos baratos",
            tags=["concepto"],
        ),
        TestCase(
            query="productos ejecutivos",
            tags=["concepto"],
        ),
        TestCase(
            query="productos tecnologicos",
            expected_categories=["Tecnologia"],
            tags=["concepto"],
        ),
        TestCase(
            query="regalos para arquitectos",
            expected_audience="ARQUITECTOS",
            tags=["industria"],
        ),
        TestCase(
            query="regalos para medicos",
            expected_audience="MEDICOS",
            tags=["industria"],
        ),
        TestCase(
            query="regalos para ingenieros",
            expected_audience="INGENIEROS",
            tags=["industria"],
        ),
        TestCase(
            query="regalos para abogados",
            expected_audience="ABOGADOS",
            tags=["industria"],
        ),
        TestCase(
            query="regalos para profesores",
            expected_audience="PROFESORES",
            tags=["industria"],
        ),
        TestCase(
            query="regalos para constructoras",
            expected_audience="CONSTRUCTORAS",
            tags=["industria"],
        ),
        TestCase(
            query="regalos para bancos",
            expected_audience="BANCOS",
            tags=["industria"],
        ),
        TestCase(
            query="clientes VIP",
            expected_audience="VIP",
            tags=["industria"],
        ),
        TestCase(
            query="regalos para feria",
            expected_audience="FERIAS",
            tags=["industria"],
        ),
        TestCase(
            query="botilitos metalicos negros",
            expected_families=["BOTELLA"],
            expected_materials=["METAL"],
            tags=["combinada"],
        ),
        TestCase(
            query="lapiceros baratos",
            expected_families=["LAPICERO"],
            tags=["combinada"],
        ),
        TestCase(
            query="termos premium",
            expected_families=["TERMO"],
            tags=["combinada"],
        ),
        TestCase(
            query="bolsos RPET",
            expected_families=["BOLSO"],
            expected_materials=["RPET"],
            tags=["combinada"],
        ),
        TestCase(
            query="USB ecologicos",
            expected_families=["USB"],
            tags=["combinada"],
        ),
        TestCase(
            query="agendas ejecutivas",
            expected_families=["AGENDA"],
            tags=["combinada"],
        ),
        TestCase(
            query="productos ecologicos baratos",
            expected_categories=["Eco"],
            tags=["combinada"],
        ),
        TestCase(
            query="algo sostenible",
            tags=["dificil"],
        ),
        TestCase(
            query="algo para oficina",
            tags=["dificil"],
        ),
        TestCase(
            query="regalos de bienvenida",
            expected_audience="BIENVENIDA",
            tags=["dificil"],
        ),
        TestCase(
            query="bolsos negros",
            expected_families=["BOLSO"],
            tags=["color"],
        ),
        TestCase(
            query="lapiceros azules",
            expected_families=["LAPICERO"],
            tags=["color"],
        ),
    ]
