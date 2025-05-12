import streamlit as st
import pandas as pd
import os
from erg_informe_completo import generar_informe_word_completo, mostrar_graficas_ojo_izquierdo
from utils_pzfx import actualizar_archivo_xml

st.set_page_config(page_title="Informe ERG", layout="wide")
st.title("🧠 Generador de Informes ERG")
st.write("Sube un archivo de señales ERG y genera un informe Word completo con análisis detallado.")

grupo_nombres = {
    1: "Escotópico Intensidad 1",
    2: "Escotópico Intensidad 2",
    3: "Escotópico Intensidad 3",
    4: "Mesópico Intensidad 1",
    5: "Mesópico Intensidad 2",
    6: "Potenciales Oscilatorios",
    7: "Fotópico Intensidad 1",
    8: "Fotópico Intensidad 2",
    9: "Flicker"
}

# === Subida del archivo TXT ===
archivo = st.file_uploader("📂 Sube el archivo .txt de señales ERG", type=["txt"])

# === Inicializar nombre del ratón
default_name = ""
if archivo is not None:
    default_name = os.path.splitext(archivo.name)[0]

nombre_raton = st.text_input("🐁 Nombre del ratón", value=default_name)
info_adicional = st.text_area("📝 Observaciones (opcional)", value="ERG sin valoración")
grupo_raton = st.selectbox("🧬 Selecciona el grupo experimental del ratón", ["P21 rd10 (PBS)", "P24 rd10 (PBS)", "P27 rd10 (PBS)"])

# === Procesamiento del archivo de señales ===
data = None
amplitudes_extraidas = None
if archivo is not None:
    try:
        data = pd.read_csv(archivo, delimiter="\t", header=None)
        data.columns = ['Tiempo', 'Grupo', 'OjoDerecho', 'OjoIzquierdo']
        for col in ['Tiempo', 'OjoDerecho', 'OjoIzquierdo']:
            data[col] = data[col].apply(lambda x: float(str(x).replace(',', '.')))

        grupos = sorted(data['Grupo'].unique())
        if len(grupos) != 9:
            st.error("⚠️ El archivo debe contener exactamente 9 grupos.")
        else:
            st.success("✅ Archivo cargado correctamente.")
            st.subheader("👁️ Gráficas del ojo izquierdo por grupo")
            amplitudes_extraidas = mostrar_graficas_ojo_izquierdo(data, grupo_nombres)

            if st.button("📄 Generar y descargar informe Word completo"):
                with st.spinner("Generando informe..."):
                    try:
                        output = generar_informe_word_completo(
                            data, nombre_raton, info_adicional, grupo_nombres
                        )
                        st.success("Informe generado correctamente.")
                        st.download_button(
                            label="📥 Descargar informe",
                            data=output,
                            file_name=f"{nombre_raton}_informe_erg.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    except Exception as e:
                        st.error(f"❌ Error al generar el informe: {e}")

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")

# === Subida del archivo PZFX base ===
pzfx_file = st.file_uploader("📊 Sube el archivo .pzfx experimental (exportado desde Prism)", type=["pzfx"], key="pzfx")

# === Inicializar session_state si no existe
if 'pzfx_data' not in st.session_state:
    st.session_state.pzfx_data = None
    st.session_state.pzfx_filename = None

if pzfx_file and st.session_state.pzfx_data is None:
    st.session_state.pzfx_data = pzfx_file.read()
    st.session_state.pzfx_filename = pzfx_file.name
    st.success(f"📁 Archivo {pzfx_file.name} cargado correctamente.")

# === Botón para añadir al archivo de datos
if st.session_state.pzfx_data:
    if archivo is not None and data is not None and amplitudes_extraidas:
        st.info("💾 El archivo PZFX permanecerá cargado hasta que recargues la app.")
        if st.button("📥 Añadir al archivo de datos"):
            with st.spinner("Añadiendo datos al archivo PZFX..."):
                try:
                    pzfx_modificado = actualizar_archivo_xml(
                        st.session_state.pzfx_data,
                        nombre_raton,
                        grupo_raton,
                        amplitudes_extraidas
                    )
                    # Actualizar el contenido en memoria
                    st.session_state.pzfx_data = pzfx_modificado
                    st.success("✅ Datos añadidos correctamente al archivo .pzfx.")
                except Exception as e:
                    st.error(f"❌ Error al añadir los datos: {e}")

    # Botón para descargar siempre visible
    if st.session_state.pzfx_data:
        st.download_button(
            label="⬇️ Descargar nuevo archivo .pzfx",
            data=st.session_state.pzfx_data,
            file_name=st.session_state.pzfx_filename or "modificado.pzfx",
            mime="application/xml"
        )
