#!/usr/bin/env python3
"""Actualiza los índices (TOC, figuras, tablas, códigos) y la paginación del DOCX con LibreOffice (UNO)
y exporta un PDF de verificación.  Uso: python3 scripts/actualizar_indices_docx.py entrada.docx salida.docx verif.pdf
"""
import subprocess
import sys
import time
from pathlib import Path

import uno
from com.sun.star.beans import PropertyValue


def prop(nombre, valor):
    p = PropertyValue()
    p.Name, p.Value = nombre, valor
    return p


def main():
    entrada, salida, pdf = (Path(a).resolve() for a in sys.argv[1:4])
    proc = subprocess.Popen(["soffice", "--headless", "--invisible", "--nologo", "--norestore",
                             "--accept=socket,host=127.0.0.1,port=2083;urp;"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        local = uno.getComponentContext()
        resolver = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
        for _ in range(60):
            try:
                ctx = resolver.resolve("uno:socket,host=127.0.0.1,port=2083;urp;StarOffice.ComponentContext")
                break
            except Exception:
                time.sleep(1)
        else:
            raise SystemExit("LibreOffice no respondió")
        desktop = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        doc = desktop.loadComponentFromURL(entrada.as_uri(), "_blank", 0, (prop("Hidden", True),))
        for _ in range(2):
            indices = doc.getDocumentIndexes()
            for i in range(indices.getCount()):
                indices.getByIndex(i).update()
            doc.getTextFields().refresh()
            doc.refresh()
        print(f"índices actualizados: {doc.getDocumentIndexes().getCount()}")
        doc.storeToURL(salida.as_uri(), (prop("FilterName", "MS Word 2007 XML"),))
        doc.storeToURL(pdf.as_uri(), (prop("FilterName", "writer_pdf_Export"),))
        doc.close(True)
    finally:
        proc.terminate()


if __name__ == "__main__":
    main()
