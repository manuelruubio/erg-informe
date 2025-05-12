import streamlit as st
import pandas as pd
import os
from erg_informe_completo import generar_informe_word_completo, mostrar_graficas_ojo_izquierdo

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

# === Carga del archivo ===
archivo = st.file_uploader("📂 Sube el archivo .txt de señales ERG", type=["txt"])

# === Inicializar nombre del ratón
nombre_por_defecto = ""
if archivo is not None:
    nombre_por_defecto = os.path.splitext(archivo.name)[0]  # nombre sin extensión

# === Inputs del usuario ===
nombre_raton = st.text_input("🐁 Nombre del ratón", value=nombre_por_defecto)
info_adicional = st.text_area("📝 Observaciones (opcional)", value="ERG sin valoración")

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

            # Mostrar gráficas por grupo del ojo izquierdo
            st.subheader("👁️ Gráficas del ojo izquierdo por grupo")
            mostrar_graficas_ojo_izquierdo(data, grupo_nombres)

            # Generar informe
            if st.button("📄 Generar y descargar informe Word completo"):
                with st.spinner("Generando informe..."):
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
        st.error(f"❌ Error al procesar el archivo: {e}")