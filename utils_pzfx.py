from lxml import etree
import io

def actualizar_archivo_xml(xml_data, nombre_raton, grupo_raton, amplitudes_extraidas):
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(xml_data, parser)

    nsmap = root.nsmap
    default_ns = nsmap.get(None)
    ns_prefix = f"{{{default_ns}}}" if default_ns else ""

    def xpath(element, tag):
        # Convierte 'prism:Tag' en '{namespace}Tag' si hay espacio de nombres por defecto
        if default_ns and tag.startswith("prism:"):
            tag = tag.replace("prism:", "")
            tag = f"{ns_prefix}{tag}"
        return element.findall(tag)

    tablas = xpath(root, "prism:Table" if default_ns else "Table")
    if not tablas:
        raise ValueError("El archivo .pzfx no contiene ninguna tabla con etiquetas <Table>.")

    tabla_destinos = {
        'Escotópico onda B GRAPHS': amplitudes_extraidas.get('Escotópico onda B GRAPHS', []),
        'Mesopico onda B GRAPHS': amplitudes_extraidas.get('Mesopico onda B GRAPHS', []),
        'Mesópico onda A GRAPHS': amplitudes_extraidas.get('Mesópico onda A GRAPHS', []),
        'Fotópico onda B GRAPHS': amplitudes_extraidas.get('Fotópico onda B GRAPHS', []),
    }

    for tabla in tablas:
        titulo_tabla = xpath(tabla, "prism:Title" if default_ns else "Title")
        if not titulo_tabla or titulo_tabla[0].text not in tabla_destinos:
            continue

        datos = tabla_destinos[titulo_tabla[0].text]
        if not datos:
            continue

        ycols = xpath(tabla, "prism:YColumn" if default_ns else "YColumn")
        for ycol in ycols:
            ycol_title_elem = xpath(ycol, "prism:Title" if default_ns else "Title")
            ycol_title = ycol_title_elem[0].text.strip() if ycol_title_elem else ""

            if ycol_title != grupo_raton.strip():
                continue

            subcolumns = xpath(ycol, "prism:Subcolumn" if default_ns else "Subcolumn")

            # Eliminar subcolumnas completamente vacías
            for sc in subcolumns:
                ds = xpath(sc, "prism:d" if default_ns else "d")
                if all((d.text is None or d.text.strip() == "") for d in ds):
                    ycol.remove(sc)

            # Recalcular subcolumns después de eliminar vacías
            subcolumns_actualizados = xpath(ycol, "prism:Subcolumn" if default_ns else "Subcolumn")

            # Crear nueva subcolumna
            nueva_subcol = etree.Element(f"{ns_prefix}Subcolumn")
            for val in datos:
                d = etree.SubElement(nueva_subcol, f"{ns_prefix}d")
                d.text = str(val)

            # Añadir al final (después de la última con datos)
            ycol.append(nueva_subcol)

            # Actualizar atributo Subcolumns
            ycol.attrib["Subcolumns"] = str(len(subcolumns_actualizados) + 1)

    output = io.BytesIO()
    etree.ElementTree(root).write(output, encoding='utf-8', xml_declaration=True, pretty_print=True)

    return output.getvalue()
