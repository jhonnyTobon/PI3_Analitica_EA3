from __future__ import annotations

from pathlib import Path

import pandas as pd


class Reportes:
    """Imprime y guarda un resumen legible de un DataFrame."""

    def generar_reporte(self, df: pd.DataFrame) -> str:
        """Genera el contenido textual del reporte."""
        self._validar_dataframe(df)
        numericas = df.select_dtypes(include="number")
        lineas = [
            "REPORTE DEL DATAFRAME",
            "=" * 60,
            f"Filas: {len(df)}",
            f"Columnas: {len(df.columns)}",
            f"Duplicados: {int(df.duplicated().sum())}",
            "",
            "Columnas y tipos:",
            *[f"- {columna}: {tipo}" for columna, tipo in df.dtypes.items()],
            "",
            "Valores nulos por columna:",
            *[f"- {columna}: {cantidad}" for columna, cantidad in df.isna().sum().items()],
        ]

        if not numericas.empty:
            lineas += [
                "",
                "Estadísticas numéricas:",
                numericas.describe().round(3).to_string(),
            ]

        return "\n".join(lineas) + "\n"

    def imprimir_reporte(self, df: pd.DataFrame) -> None:
        """Imprime en la consola el reporte del DataFrame."""
        print(self.generar_reporte(df), end="")

    def guardar_reporte(self, df: pd.DataFrame, ruta: str | Path) -> Path:
        """Guarda el reporte en un archivo de texto y devuelve su ruta."""
        path = Path(ruta)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.generar_reporte(df), encoding="utf-8")
        return path
        
    def generar_reporte_descriptivo(self, df: pd.DataFrame) -> str:
        """Genera un reporte descriptivo del DataFrame."""

        self._validar_dataframe(df)

        numericas = df.select_dtypes(include="number")

        lineas = [
            "REPORTE DESCRIPTIVO DEL DATAFRAME",
            "=" * 70,
            "",
            "1. DIMENSIONES DEL DATASET",
            f"- Número de filas: {df.shape[0]}",
            f"- Número de columnas: {df.shape[1]}",
            "",
            "2. MUESTRA DE REGISTROS (primeras 5 filas)",
            df.head().to_string(),
            "",
            "3. NOMBRES Y TIPOS DE COLUMNAS",
            *[
                f"- {columna}: {tipo}"
                for columna, tipo in df.dtypes.items()
            ],
            "",
            "4. VALORES NULOS POR COLUMNA",
            *[
                f"- {columna}: {cantidad}"
                for columna, cantidad in df.isna().sum().items()
            ],
            "",
            "5. REGISTROS DUPLICADOS",
            f"- Duplicados encontrados: {int(df.duplicated().sum())}",
            "",
            "6. LONGITUD DE LOS CAMPOS (CARACTERES)"
    ]

        for columna in df.columns:

            longitudes = (
                df[columna]
                .astype(str)
                .fillna("")
                .str.len()
            )

            lineas.append(
                (
                f"- {columna}: "
                f"mínimo={longitudes.min()}, "
                f"máximo={longitudes.max()}, "
                f"promedio={longitudes.mean():.2f}"
                )
            )
        

        if not numericas.empty:
            lineas.extend([
                "",
                "7. ESTADÍSTICAS DESCRIPTIVAS DE VARIABLES NUMÉRICAS",
                numericas.describe().round(2).to_string()
            ])

        return "\n".join(lineas) + "\n"

    def guardar_reporte_descriptivo(self, df: pd.DataFrame, ruta: str | Path) -> Path:
        """Guarda el reporte descriptivo y devuelve la ruta del archivo."""
        path = Path(ruta)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.generar_reporte_descriptivo(df), encoding="utf-8")
        return path


    @staticmethod
    def _validar_dataframe(df: pd.DataFrame) -> None:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df debe ser un pandas.DataFrame.")
        
    