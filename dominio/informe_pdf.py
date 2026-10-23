from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle

from dominio.informe import Informe


class InformePDF(Informe):
    def generar(self):
        self._preparar_destino(".pdf")

        documento = SimpleDocTemplate(
            str(self.ruta_archivo),
            pagesize=landscape(A4),
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        estilos = getSampleStyleSheet()
        estilos["BodyText"].fontSize = 8
        estilos["BodyText"].leading = 11
        contenido = [
            Paragraph("Informe de EcoTech Solutions", estilos["Title"]),
            Paragraph(
                "Informe " + str(self.get_id()) + " | Fecha: " + self.fecha_generacion.isoformat(),
                estilos["Normal"]
            ),
            Spacer(1, 18)
        ]

        for titulo, encabezados, filas in self._obtener_secciones():
            contenido.append(Paragraph(titulo, estilos["Heading2"]))

            if not filas:
                contenido.append(Paragraph("Sin datos para mostrar.", estilos["Normal"]))
            else:
                datos = []
                for fila in [encabezados] + filas:
                    celdas = []
                    for valor in fila:
                        texto = escape(str(valor)).replace("\n", "<br/>")
                        celdas.append(Paragraph(texto, estilos["BodyText"]))
                    datos.append(celdas)

                tabla = LongTable(
                    datos,
                    colWidths=[documento.width / len(encabezados)] * len(encabezados),
                    repeatRows=1,
                    splitInRow=1
                )
                tabla.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCEBE6")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LINEBELOW", (0, 0), (-1, 0), 1, colors.HexColor("#477565")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
                ]))
                contenido.append(tabla)

            contenido.append(Spacer(1, 18))

        documento.build(contenido)
