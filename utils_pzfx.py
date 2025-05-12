from lxml import etree
import io

def actualizar_archivo_xml(xml_data, nombre_raton, grupo_raton, amplitudes_extraidas):
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(xml_data, parser)

    nsmap = root.nsmap
    default_ns = nsmap.get(None)
    ns_prefix = "{%s}" % default_ns if default_ns else ""

    def xpath(element, path):
        if default_ns:
            path = path.replace("prism:", ns_prefix)
        return element.xpath(path, namespaces={'prism': default_ns} if default_ns else None)

    tabla_destinos = {
        'Escotópico onda B GRAPHS': amplitudes_extraidas.get('Escotópico onda B GRAPHS', []),
        'Mesopico onda B GRAPHS': amplitudes_extraidas.get('Mesopico onda B GRAPHS', []),
        'Mesópico onda A GRAPHS': amplitudes_extraidas.get('Mesópico onda A GRAPHS', []),
        'Fotópico onda B GRAPHS': amplitudes_extraidas.get('Fotópico onda B GRAPHS', []),
    }

    for tabla in xpath(root, ".//prism:Table" if default_ns else ".//Table"):
        titulo_tabla = xpath(tabla, "./prism:Title" if default_ns else "./Title")
        if not titulo_tabla or titulo_tabla[0].text not in tabla_destinos:
            continue

        datos = tabla_destinos[titulo_tabla[0].text]
        if not datos:
            continue

        for ycol in xpath(tabla, "./prism:YColumn" if default_ns else "./YColumn"):
            ycol_title_elem = xpath(ycol, "./prism:Title" if default_ns else "./Title")
            ycol_title = ycol_title_elem[0].text.strip() if ycol_title_elem else ""

            if ycol_title != grupo_raton.strip():
                continue

            # Eliminar Subcolumns completamente vacías
            subcolumns = xpath(ycol, "./prism:Subcolumn" if default_ns else "./Subcolumn")
            for sc in subcolumns:
                ds = xpath(sc, "./prism:d" if default_ns else "./d")
                if all((d.text is None or d.text.strip() == "") for d in ds):
                    ycol.remove(sc)

            # Añadir nueva Subcolumn como última
            nueva_subcol = etree.Element(f"{ns_prefix}Subcolumn")
            for val in datos:
                d = etree.SubElement(nueva_subcol, f"{ns_prefix}d")
                d.text = str(val)
            ycol.append(nueva_subcol)

            # Actualizar el atributo Subcolumns
            subcols_finales = xpath(ycol, "./prism:Subcolumn" if default_ns else "./Subcolumn")
            ycol.attrib["Subcolumns"] = str(len(subcols_finales))

    # Guardar el XML modificado
    output = io.BytesIO()
    tree = etree.ElementTree(root)
    tree.write(output, encoding='utf-8', xml_declaration=True, pretty_print=True)
    return output.getvalue()
