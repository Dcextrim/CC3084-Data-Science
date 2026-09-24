"""
Descarga las bases de Personas de la ENEIC (INE Guatemala) y sus
diccionarios de datos hacia data/raw/. Los archivos no se versionan por su
tamano (16-50 MB cada uno); este script los deja reproducibles.

Fuente: https://www.ine.gob.gt/encuesta-nacional-de-empleo-e-ingresos/
"""
from pathlib import Path
from urllib.request import urlretrieve

RAIZ = Path(__file__).resolve().parent.parent
DIR_RAW = RAIZ / "data" / "raw"

ARCHIVOS = {
    "Personas_ENEIC_2025T1.xlsx": "https://www.ine.gob.gt/wp-content/uploads/2026/01/Personas_ENEIC_T1_2025.xlsx",
    "Personas_ENEIC_2025T2.xlsx": "https://www.ine.gob.gt/wp-content/uploads/2026/01/Personas-ENEIC-T2-2025.xlsx",
    "Personas_ENEIC_2025T3.xlsx": "https://www.ine.gob.gt/wp-content/uploads/2026/05/Base-de-datos-Personas-ENEIC-III-2025.xlsx",
    "Personas_ENEIC_2025T4.xlsx": "https://www.ine.gob.gt/wp-content/uploads/2026/06/Base-de-datos-Personas-ENEIC-IV-2025.xlsx",
    "Personas_ENEIC_2026T1.xlsx": "https://www.ine.gob.gt/wp-content/uploads/2026/09/Base-de-datos-Personas-ENEIC-I-2026.xlsx",
    "Diccionario_Personas_2025T1.xlsx": "https://www.ine.gob.gt/wp-content/uploads/2025/11/Diccionario_Personas_ENEIC_I-2025.xlsx",
    "Diccionario_Personas_2025T2.xlsx": "https://www.ine.gob.gt/wp-content/uploads/2025/11/Diccionario_Personas_ENEIC_II-2025.xlsx",
    "Diccionario_Personas_2025T3.xlsx": "https://www.ine.gob.gt/wp-content/uploads/2026/05/Diccionario-Personas-ENEIC-III-2025.xlsx",
    "Diccionario_Personas_2025T4.xlsx": "https://www.ine.gob.gt/wp-content/uploads/2026/06/Diccionario-Personas-ENEIC-IV-2025.xlsx",
    "Diccionario_Personas_2026T1.xlsx": "https://www.ine.gob.gt/wp-content/uploads/2026/09/Diccionario-Personas-ENEIC-I-2026.xlsx",
}


def main() -> None:
    DIR_RAW.mkdir(parents=True, exist_ok=True)
    for nombre, url in ARCHIVOS.items():
        destino = DIR_RAW / nombre
        if destino.exists():
            print(f"ya existe, se omite: {nombre}")
            continue
        print(f"descargando {nombre} ...")
        urlretrieve(url, destino)
    print("listo.")


if __name__ == "__main__":
    main()
