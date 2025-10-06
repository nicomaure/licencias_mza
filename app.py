import datetime as dt
import os
import sys
from pathlib import Path
from dateutil.relativedelta import relativedelta
from typing import Optional, List

import pandas as pd
import streamlit as st
from sqlmodel import SQLModel, Field, create_engine, Session, select


# ---------- Config ----------
def get_app_path():
    """Obtiene el directorio de la aplicación"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent


def get_data_path():
    """Obtiene el directorio de datos en AppData para evitar problemas de permisos"""
    if sys.platform == "win32":
        data_dir = Path(os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))) / "LicenciasEscolares"
    else:
        data_dir = Path.home() / ".licencias_escolares"

    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


DB_PATH = get_data_path() / "licencias.db"
DB_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DB_URL, echo=False)


# ---------- Modelo ----------
class Licencia(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}

    id: Optional[int] = Field(default=None, primary_key=True)
    apellido: str
    nombre: str
    rol: str
    fecha_inicio: dt.date
    fecha_fin: Optional[dt.date] = None
    articulo: Optional[str] = None
    codigo_osep: Optional[str] = None
    estado_carga: str = "Pendiente"
    fecha_carga_gei: Optional[dt.date] = None
    observaciones: Optional[str] = None
    fecha_creacion: dt.datetime = Field(default_factory=dt.datetime.now)


def init_db():
    try:
        SQLModel.metadata.create_all(engine)
        return True
    except Exception as e:
        st.error(f"Error al inicializar la base de datos: {e}")
        return False


@st.cache_data
def get_roles() -> List[str]:
    return ["Docente", "Celador"]


@st.cache_data
def get_estados() -> List[str]:
    return ["Pendiente", "Cargada"]


def to_df(rows: List[Licencia]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()

    data = [r.model_dump() for r in rows]
    df = pd.DataFrame(data)

    if 'fecha_inicio' in df.columns:
        df['fecha_inicio'] = pd.to_datetime(df['fecha_inicio']).dt.strftime('%d/%m/%Y')
    if 'fecha_fin' in df.columns:
        df['fecha_fin'] = df['fecha_fin'].apply(
            lambda x: pd.to_datetime(x).strftime('%d/%m/%Y') if pd.notna(x) else '(Sin definir)'
        )
    if 'fecha_carga_gei' in df.columns:
        df['fecha_carga_gei'] = df['fecha_carga_gei'].apply(
            lambda x: pd.to_datetime(x).strftime('%d/%m/%Y') if pd.notna(x) else ''
        )
    
    # Reemplazar None en articulo con texto indicativo
    if 'articulo' in df.columns:
        df['articulo'] = df['articulo'].fillna('(Pendiente)')

    columnas_orden = [
        "id", "apellido", "nombre", "rol", "fecha_inicio", "fecha_fin",
        "articulo", "codigo_osep", "estado_carga", "fecha_carga_gei", "observaciones"
    ]
    columnas_disponibles = [col for col in columnas_orden if col in df.columns]
    df = df[columnas_disponibles]

    return df


def df_to_html_table(df: pd.DataFrame) -> str:
    """Genera tabla HTML para impresión con estilos inline y colores para licencias completas"""
    if df.empty:
        return "<p>No hay datos</p>"
    
    # Renombrar columnas para mejor legibilidad
    columnas_legibles = {
        'id': 'ID',
        'apellido': 'Apellido',
        'nombre': 'Nombre',
        'rol': 'Rol',
        'fecha_inicio': 'Inicio',
        'fecha_fin': 'Fin',
        'articulo': 'Artículo',
        'codigo_osep': 'OSEP',
        'estado_carga': 'Estado',
        'fecha_carga_gei': 'Carga GEI',
        'observaciones': 'Observaciones'
    }
    
    html = '<table class="print-table" style="width:100%; border-collapse:collapse; font-size:9pt;">'
    html += '<thead><tr style="background-color:#f0f0f0;">'
    
    for col in df.columns:
        col_name = columnas_legibles.get(col, col)
        html += f'<th style="border:1px solid #ddd; padding:4px 6px; text-align:left; font-weight:bold;">{col_name}</th>'
    
    html += '</tr></thead><tbody>'
    
    for _, row in df.iterrows():
        # Determinar si la licencia está completa
        # Completa = tiene fecha_fin, articulo, codigo_osep y fecha_carga_gei
        es_completa = (
            row.get('fecha_fin') not in [None, '', '(Sin definir)'] and
            row.get('articulo') not in [None, '', '(Pendiente)'] and
            row.get('codigo_osep') not in [None, ''] and
            row.get('fecha_carga_gei') not in [None, ''] and
            row.get('estado_carga') == 'Cargada'
        )
        
        # Color de fondo y texto según si está completa
        if es_completa:
            row_style = 'background-color:#d4edda; color:#000000;'  # Verde claro con texto negro
        else:
            row_style = 'background-color:white;'  # Blanco normal
        
        html += f'<tr style="{row_style}">'
        for col in df.columns:
            val = row[col] if pd.notna(row[col]) else ''
            html += f'<td style="border:1px solid #ddd; padding:4px 6px;">{val}</td>'
        html += '</tr>'
    
    html += '</tbody></table>'
    return html



def crear_licencia(**kwargs):
    try:
        with Session(engine) as s:
            lic = Licencia(**kwargs)
            s.add(lic)
            s.commit()
            s.refresh(lic)
            return lic, None
    except Exception as e:
        return None, str(e)


def actualizar_licencia(id_: int, **kwargs):
    try:
        with Session(engine) as s:
            lic = s.get(Licencia, id_)
            if not lic:
                return False, "Licencia no encontrada"

            for key, value in kwargs.items():
                if hasattr(lic, key):
                    setattr(lic, key, value)

            s.add(lic)
            s.commit()
            return True, "Licencia actualizada correctamente"
    except Exception as e:
        return False, str(e)


def eliminar_licencia(id_: int):
    try:
        with Session(engine) as s:
            lic = s.get(Licencia, id_)
            if not lic:
                return False, "Licencia no encontrada"
            s.delete(lic)
            s.commit()
            return True, "Licencia eliminada correctamente"
    except Exception as e:
        return False, str(e)


def buscar_licencias(
        apellido: str = "",
        nombre: str = "",
        rol: Optional[str] = None,
        estado: Optional[str] = None,
        f_ini: Optional[dt.date] = None,
        f_fin: Optional[dt.date] = None,
        articulo: str = "",
):
    try:
        with Session(engine) as s:
            q = select(Licencia)
            if apellido:
                q = q.where(Licencia.apellido.ilike(f"%{apellido}%"))
            if nombre:
                q = q.where(Licencia.nombre.ilike(f"%{nombre}%"))
            if rol and rol != "Todos":
                q = q.where(Licencia.rol == rol)
            if estado and estado != "Todos":
                q = q.where(Licencia.estado_carga == estado)
            if articulo:
                q = q.where(Licencia.articulo.ilike(f"%{articulo}%"))
            if f_ini:
                q = q.where(Licencia.fecha_inicio >= f_ini)
            if f_fin:
                q = q.where(Licencia.fecha_fin <= f_fin)
            # Ordenar por ID descendente (más recientes primero)
            q = q.order_by(Licencia.id.desc())
            return s.exec(q).all()
    except Exception as e:
        st.error(f"Error al buscar licencias: {e}")
        return []


def marcar_cargada(id_: int, fecha_carga: Optional[dt.date] = None):
    """Marca una licencia como cargada con la fecha especificada (o hoy si no se especifica)"""
    if fecha_carga is None:
        fecha_carga = dt.date.today()
    
    return actualizar_licencia(
        id_,
        estado_carga="Cargada",
        fecha_carga_gei=fecha_carga
    )


def obtener_licencia(id_: int):
    try:
        with Session(engine) as s:
            lic = s.get(Licencia, id_)
            if lic:
                # Crear una copia independiente del objeto para evitar problemas de sesión
                return Licencia(
                    id=lic.id,
                    apellido=lic.apellido,
                    nombre=lic.nombre,
                    rol=lic.rol,
                    fecha_inicio=lic.fecha_inicio,
                    fecha_fin=lic.fecha_fin,
                    articulo=lic.articulo,
                    codigo_osep=lic.codigo_osep,
                    estado_carga=lic.estado_carga,
                    fecha_carga_gei=lic.fecha_carga_gei,
                    observaciones=lic.observaciones,
                    fecha_creacion=lic.fecha_creacion
                )
            return None
    except Exception as e:
        st.error(f"Error al obtener licencia: {e}")
        return None


# ---------- UI ----------
st.set_page_config(
    page_title="Licencias – Secretaría Escolar",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS mejorados para impresión
st.markdown("""
    <style>
    /* Estilos para pantalla - ocultar tabla de impresión */
    @media screen {
        .print-table {
            display: none !important;
        }
        .print-container {
            display: none !important;
        }
    }
    
    /* Estilos para impresión */
    @media print {
        /* Ocultar elementos de Streamlit */
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [data-testid="stMainMenu"],
        header,
        footer,
        .stApp > header,
        .stDeployButton,
        button,
        .stTabs,
        .stMarkdown > div > div > button,
        iframe,
        .no-print {
            display: none !important;
            visibility: hidden !important;
        }
        
        /* Ocultar el título principal de la app */
        h1:first-of-type {
            display: none !important;
        }
        
        /* Ocultar el expander de información */
        [data-testid="stExpander"] {
            display: none !important;
        }
        
        /* Ocultar divider y captions del footer */
        hr:last-of-type,
        .stMarkdown:has(hr) ~ .stMarkdown {
            display: none !important;
        }
        
        /* Ocultar últimos 3 captions (divider + 2 líneas de créditos) */
        .stMarkdown > div:has(hr),
        body > div:last-child .stMarkdown:nth-last-of-type(1),
        body > div:last-child .stMarkdown:nth-last-of-type(2),
        body > div:last-child .stMarkdown:nth-last-of-type(3) {
            display: none !important;
        }
        
        /* Ocultar dataframe interactivo */
        [data-testid="stDataFrame"] {
            display: none !important;
        }
        
        /* Mostrar contenedor de impresión */
        .print-container {
            display: block !important;
            visibility: visible !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 20px !important;
        }
        
        /* Tabla de impresión */
        .print-table {
            display: table !important;
            visibility: visible !important;
            width: 100% !important;
            border-collapse: collapse !important;
            margin: 20px 0 !important;
            font-family: Arial, sans-serif !important;
        }
        
        .print-table thead tr {
            background-color: #e0e0e0 !important;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
        
        .print-table th {
            border: 1px solid #000 !important;
            padding: 6px 8px !important;
            text-align: left !important;
            font-weight: bold !important;
            font-size: 9pt !important;
            background-color: #e0e0e0 !important;
        }
        
        .print-table td {
            border: 1px solid #000 !important;
            padding: 5px 8px !important;
            font-size: 8pt !important;
        }
        
        .print-table tr {
            page-break-inside: avoid !important;
        }
        
        /* Título y encabezados */
        h1, h2, h3, h4, h5, h6 {
            color: #000 !important;
            page-break-after: avoid !important;
        }
        
        .print-title {
            font-size: 20pt !important;
            font-weight: bold !important;
            margin-bottom: 15px !important;
            color: #000 !important;
        }
        
        .print-subtitle {
            font-size: 14pt !important;
            margin-bottom: 10px !important;
            color: #333 !important;
        }
        
        .print-metrics {
            display: flex !important;
            justify-content: space-around !important;
            margin: 15px 0 !important;
            font-size: 11pt !important;
        }
        
        .print-metric {
            text-align: center !important;
            padding: 5px 10px !important;
        }
        
        /* Configuración de página */
        @page {
            size: landscape;
            margin: 1.5cm 1cm;
        }
        
        body {
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
        
        /* Forzar visibilidad */
        .element-container,
        .stMarkdown,
        [data-testid="stVerticalBlock"] {
            display: block !important;
            visibility: visible !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("🗂️ Licencias – Secretaría Escolar (Mendoza)")

if not init_db():
    st.stop()

with st.expander("ℹ️ Información del sistema"):
    st.info(f"**Base de datos:** `{DB_PATH}`")
    st.caption("Los datos se guardan automáticamente y persisten entre sesiones.")

tab1, tab2, tab3, tab4 = st.tabs([
    "➕ Nueva licencia",
    "🔎 Listado / Gestión",
    "✏️ Editar / Eliminar",
    "📅 Reporte mensual"
])

# --- Tab 1: Alta ---
with tab1:
    st.subheader("Cargar nueva licencia")

    with st.form("form_nueva_licencia", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            apellido = st.text_input("Apellido*", max_chars=80)
            nombre = st.text_input("Nombre*", max_chars=80)
            rol = st.selectbox("Rol*", options=get_roles())

        with col2:
            f_ini = st.date_input("Fecha inicio*", value=dt.date.today())
            f_fin = st.date_input("Fecha fin", value=None, help="Opcional: se puede completar después")
            articulo = st.text_input("Artículo", placeholder="Ej: Art. X inciso Y", help="Opcional: se puede completar después")

        with col3:
            codigo_osep = st.text_input("Código OSEP", placeholder="Ej: AUS-12345")
            observ = st.text_area("Observaciones", height=90)

        submitted = st.form_submit_button("💾 Guardar licencia", type="primary", use_container_width=True)

        if submitted:
            errores = []
            if not apellido or not apellido.strip():
                errores.append("El apellido es obligatorio")
            if not nombre or not nombre.strip():
                errores.append("El nombre es obligatorio")
            # Validar fecha_fin solo si se ingresó
            if f_fin and f_fin < f_ini:
                errores.append("La fecha de fin no puede ser anterior a la de inicio")

            if errores:
                for error in errores:
                    st.error(f"❌ {error}")
            else:
                lic, error = crear_licencia(
                    apellido=apellido.strip().upper(),
                    nombre=nombre.strip().title(),
                    rol=rol,
                    fecha_inicio=f_ini,
                    fecha_fin=f_fin if f_fin else None,
                    articulo=articulo.strip() if articulo and articulo.strip() else None,
                    codigo_osep=codigo_osep.strip() if codigo_osep and codigo_osep.strip() else None,
                    observaciones=observ.strip() if observ and observ.strip() else None,
                )
                if lic:
                    st.success(f"✅ Licencia #{lic.id} guardada correctamente")
                    st.balloons()
                else:
                    st.error(f"❌ Error al guardar: {error}")

# --- Tab 2: Listado / Gestión ---
with tab2:
    st.subheader("Buscar y gestionar licencias")

    with st.form("form_busqueda"):
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            f_ap = st.text_input("Apellido contiene")
            f_nom = st.text_input("Nombre contiene")
        with fc2:
            f_rol = st.selectbox("Rol", options=["Todos"] + get_roles())
            f_estado = st.selectbox("Estado", options=["Todos"] + get_estados())
        with fc3:
            f_articulo = st.text_input("Artículo contiene")
            buscar = st.form_submit_button("🔍 Buscar", use_container_width=True)

    fc4, fc5 = st.columns(2)
    with fc4:
        f_ini = st.date_input("Desde (inicio)", value=None, key="busq_ini")
    with fc5:
        f_fin = st.date_input("Hasta (fin)", value=None, key="busq_fin")

    rows = buscar_licencias(
        apellido=f_ap.strip(),
        nombre=f_nom.strip(),
        rol=f_rol,
        estado=f_estado,
        f_ini=f_ini if isinstance(f_ini, dt.date) else None,
        f_fin=f_fin if isinstance(f_fin, dt.date) else None,
        articulo=f_articulo.strip(),
    )

    df = to_df(rows)

    if df.empty:
        st.warning("No se encontraron licencias con los criterios especificados")
    else:
        st.success(f"✅ Se encontraron {len(df)} licencias")

        col_est1, col_est2, col_est3 = st.columns(3)
        with col_est1:
            pendientes = len([r for r in rows if r.estado_carga == "Pendiente"])
            st.metric("Pendientes", pendientes)
        with col_est2:
            cargadas = len([r for r in rows if r.estado_carga == "Cargada"])
            st.metric("Cargadas", cargadas)
        with col_est3:
            docentes = len([r for r in rows if r.rol == "Docente"])
            st.metric("Docentes", docentes)

        # Leyenda de colores
        st.caption("💡 **Leyenda:** Las filas con fondo verde claro indican licencias **completamente cargadas** (con todos los datos obligatorios + fecha de carga GEI)")
        
        # Función para colorear filas completas
        def highlight_complete_rows(row):
            """Aplica color verde claro a licencias completas"""
            es_completa = (
                row.get('fecha_fin') not in [None, '', '(Sin definir)'] and
                row.get('articulo') not in [None, '', '(Pendiente)'] and
                row.get('codigo_osep') not in [None, ''] and
                row.get('fecha_carga_gei') not in [None, ''] and
                row.get('estado_carga') == 'Cargada'
            )
            color = 'background-color: #d4edda; color: #000000' if es_completa else ''
            return [color] * len(row)
        
        # Tabla interactiva con estilos
        df_styled = df.style.apply(highlight_complete_rows, axis=1)
        st.dataframe(df_styled, use_container_width=True, hide_index=True)
        
        # HTML completo para impresión
        html_table = df_to_html_table(df)
        celadores = len([r for r in rows if r.rol == "Celador"])
        print_html = f"""
        <div class="print-container">
            <div class="print-title">🔎 Listado de Licencias - Secretaría Escolar Mendoza</div>
            
            <div class="print-metrics">
                <div class="print-metric"><strong>Total:</strong> {len(df)}</div>
                <div class="print-metric"><strong>Pendientes:</strong> {pendientes}</div>
                <div class="print-metric"><strong>Cargadas:</strong> {cargadas}</div>
                <div class="print-metric"><strong>Docentes:</strong> {docentes} | <strong>Celadores:</strong> {celadores}</div>
            </div>
            
            {html_table}
            
            <div style="margin-top: 20px; font-size: 9pt; text-align: center; border-top: 1px solid #ccc; padding-top: 10px;">
                <p>Sistema de Gestión de Licencias - Secretaría Escolar Mendoza | Versión 2.0</p>
                <p>Desarrollado por Nicolas Maure | nicomaure.com.ar</p>
            </div>
        </div>
        """
        st.markdown(print_html, unsafe_allow_html=True)

        st.divider()
        col_acc1, col_acc2, col_acc3 = st.columns(3)

        with col_acc1:
            st.markdown("##### Marcar como CARGADA")
            sel_id = st.number_input("ID a marcar como CARGADA", min_value=1, step=1, key="marcar_id")
            fecha_carga_sel = st.date_input(
                "Fecha de carga en GEI", 
                value=dt.date.today(),
                key="fecha_carga_gei",
                help="Seleccioná la fecha en que se cargó en GEI"
            )
            if st.button("✅ Marcar como CARGADA", use_container_width=True):
                success, msg = marcar_cargada(int(sel_id), fecha_carga_sel)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        with col_acc2:
            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "📥 Descargar CSV",
                csv,
                file_name=f"licencias_{dt.date.today():%Y%m%d}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col_acc3:
            try:
                excel_name = f"temp_{dt.date.today():%Y%m%d}.xlsx"
                with pd.ExcelWriter(excel_name, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Licencias')

                with open(excel_name, 'rb') as f:
                    excel_data = f.read()

                st.download_button(
                    "📊 Descargar Excel",
                    excel_data,
                    file_name=f"licencias_{dt.date.today():%Y%m%d}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

                if os.path.exists(excel_name):
                    os.remove(excel_name)
            except Exception as e:
                st.error(f"Error al generar Excel: {e}")

# --- Tab 3: Editar / Eliminar ---
with tab3:
    st.subheader("Editar o eliminar licencia")

    id_editar = st.number_input("ID de licencia a editar", min_value=1, step=1, key="edit_id")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        cargar_btn = st.button("📋 Cargar datos", use_container_width=True)
    with col_btn2:
        eliminar_btn = st.button("🗑️ Eliminar licencia", type="secondary", use_container_width=True)

    if eliminar_btn:
        if st.session_state.get('confirmar_eliminar') != id_editar:
            st.session_state.confirmar_eliminar = id_editar
            st.warning("⚠️ Hacé clic nuevamente para confirmar la eliminación")
        else:
            success, msg = eliminar_licencia(int(id_editar))
            if success:
                st.success(msg)
                del st.session_state.confirmar_eliminar
                if 'licencia_cargada_id' in st.session_state:
                    del st.session_state.licencia_cargada_id
                st.rerun()
            else:
                st.error(msg)

    # Cargar datos cuando se presiona el botón o después de actualizar
    if cargar_btn or st.session_state.get('licencia_cargada_id') == id_editar:
        st.session_state.licencia_cargada_id = id_editar
        lic = obtener_licencia(int(id_editar))

        if not lic:
            st.error("❌ No se encontró la licencia con ese ID")
        else:
            st.info(f"Editando licencia #{lic.id}")

            with st.form("form_editar_licencia"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    apellido_e = st.text_input("Apellido*", value=lic.apellido, max_chars=80)
                    nombre_e = st.text_input("Nombre*", value=lic.nombre, max_chars=80)
                    rol_e = st.selectbox("Rol*", options=get_roles(), index=get_roles().index(lic.rol))

                with col2:
                    f_ini_e = st.date_input("Fecha inicio*", value=lic.fecha_inicio)
                    f_fin_e = st.date_input("Fecha fin", value=lic.fecha_fin, help="Opcional: se puede completar después")
                    articulo_e = st.text_input("Artículo", value=lic.articulo or "", help="Opcional: se puede completar después")

                with col3:
                    codigo_osep_e = st.text_input("Código OSEP", value=lic.codigo_osep or "")
                    estado_e = st.selectbox("Estado*", options=get_estados(),
                                            index=get_estados().index(lic.estado_carga))
                    observ_e = st.text_area("Observaciones", value=lic.observaciones or "", height=90)

                actualizar = st.form_submit_button("💾 Actualizar licencia", type="primary", use_container_width=True)

                if actualizar:
                    errores = []
                    if not apellido_e or not apellido_e.strip():
                        errores.append("El apellido es obligatorio")
                    if not nombre_e or not nombre_e.strip():
                        errores.append("El nombre es obligatorio")
                    # Validar fecha_fin solo si se ingresó
                    if f_fin_e and f_fin_e < f_ini_e:
                        errores.append("La fecha de fin no puede ser anterior a la de inicio")

                    if errores:
                        for error in errores:
                            st.error(f"❌ {error}")
                    else:
                        # Preparar código OSEP: permite actualizar con string vacío o con valor
                        codigo_osep_valor = codigo_osep_e.strip() if codigo_osep_e and codigo_osep_e.strip() else None
                        articulo_valor = articulo_e.strip() if articulo_e and articulo_e.strip() else None
                        
                        success, msg = actualizar_licencia(
                            int(id_editar),
                            apellido=apellido_e.strip().upper(),
                            nombre=nombre_e.strip().title(),
                            rol=rol_e,
                            fecha_inicio=f_ini_e,
                            fecha_fin=f_fin_e if f_fin_e else None,
                            articulo=articulo_valor,
                            codigo_osep=codigo_osep_valor,
                            estado_carga=estado_e,
                            observaciones=observ_e.strip() if observ_e and observ_e.strip() else None,
                        )

                        if success:
                            st.success(f"✅ {msg}")
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {msg}")

# --- Tab 4: Reporte mensual ---
with tab4:
    st.subheader("Reporte mensual para imprimir")

    hoy = dt.date.today()
    mes_base = st.date_input(
        "📅 Elegí un mes (cualquier día dentro del mes)",
        value=dt.date(hoy.year, hoy.month, 1),
        key="mes_reporte"
    )

    primer_dia = dt.date(mes_base.year, mes_base.month, 1)
    proximo_mes = primer_dia + relativedelta(months=1)
    ultimo_dia = proximo_mes - dt.timedelta(days=1)

    # Buscar licencias que INICIEN en el mes seleccionado
    # Incluye licencias con o sin fecha_fin
    try:
        with Session(engine) as s:
            q = select(Licencia)
            # Licencias que inicien en el mes
            q = q.where(Licencia.fecha_inicio >= primer_dia)
            q = q.where(Licencia.fecha_inicio <= ultimo_dia)
            # Ordenar por fecha_inicio y luego por apellido
            q = q.order_by(Licencia.fecha_inicio, Licencia.apellido, Licencia.nombre)
            rows_mes = s.exec(q).all()
    except Exception as e:
        st.error(f"Error al buscar licencias: {e}")
        rows_mes = []
    
    df_mes = to_df(rows_mes)

    if df_mes.empty:
        st.warning("⚠️ No hay licencias registradas en ese mes")
    else:
        pendientes = len([r for r in rows_mes if r.estado_carga == "Pendiente"])
        cargadas = len([r for r in rows_mes if r.estado_carga == "Cargada"])
        docentes = len([r for r in rows_mes if r.rol == "Docente"])
        celadores = len([r for r in rows_mes if r.rol == "Celador"])

        st.markdown(f"""
        ### 📋 Reporte de Licencias
        **Período:** {primer_dia:%d/%m/%Y} — {ultimo_dia:%d/%m/%Y}
        """)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total", len(df_mes))
        with col2:
            st.metric("Cargadas", cargadas, delta=f"{cargadas / len(df_mes) * 100:.0f}%" if len(df_mes) > 0 else "0%")
        with col3:
            st.metric("Pendientes", pendientes,
                      delta=f"-{pendientes / len(df_mes) * 100:.0f}%" if len(df_mes) > 0 else "0%")
        with col4:
            st.metric("Docentes / Celadores", f"{docentes} / {celadores}")

        # Alertas (ocultas en impresión)
        with st.container():
            if hoy > ultimo_dia and pendientes > 0:
                st.error(
                    f"⚠️ **ATENCIÓN:** Hay {pendientes} licencia(s) PENDIENTE(S) - El plazo venció el {ultimo_dia:%d/%m/%Y}")
            elif pendientes > 0:
                dias_restantes = (ultimo_dia - hoy).days
                st.warning(f"⏰ Quedan {dias_restantes} día(s) para cargar {pendientes} licencia(s) pendiente(s)")
            else:
                st.success("✅ Todas las licencias del mes están cargadas")

        st.divider()
        
        # Leyenda de colores
        st.caption("💡 **Leyenda:** Las filas con fondo verde claro indican licencias **completamente cargadas** (con todos los datos obligatorios + fecha de carga GEI)")
        
        # Función para colorear filas completas
        def highlight_complete_rows(row):
            """Aplica color verde claro a licencias completas"""
            es_completa = (
                row.get('fecha_fin') not in [None, '', '(Sin definir)'] and
                row.get('articulo') not in [None, '', '(Pendiente)'] and
                row.get('codigo_osep') not in [None, ''] and
                row.get('fecha_carga_gei') not in [None, ''] and
                row.get('estado_carga') == 'Cargada'
            )
            # Verde claro con texto negro para completas, transparente para incompletas
            color = 'background-color: #d4edda; color: #000000' if es_completa else ''
            return [color] * len(row)
        
        # Aplicar estilos y mostrar tabla
        df_styled = df_mes.style.apply(highlight_complete_rows, axis=1)
        st.dataframe(df_styled, use_container_width=True, hide_index=True)

        st.divider()
        
        # Botones de exportación e impresión
        col_exp1, col_exp2, col_exp3 = st.columns(3)

        with col_exp1:
            csv = df_mes.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "📥 Descargar CSV",
                csv,
                file_name=f"reporte_licencias_{primer_dia:%Y_%m}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col_exp2:
            try:
                excel_name = f"reporte_{primer_dia:%Y_%m}.xlsx"
                with pd.ExcelWriter(excel_name, engine='openpyxl') as writer:
                    df_mes.to_excel(writer, index=False, sheet_name='Licencias')

                    resumen = pd.DataFrame({
                        'Concepto': ['Total', 'Cargadas', 'Pendientes', 'Docentes', 'Celadores'],
                        'Cantidad': [len(df_mes), cargadas, pendientes, docentes, celadores]
                    })
                    resumen.to_excel(writer, index=False, sheet_name='Resumen')

                with open(excel_name, 'rb') as f:
                    excel_data = f.read()

                st.download_button(
                    "📊 Descargar Excel completo",
                    excel_data,
                    file_name=f"reporte_licencias_{primer_dia:%Y_%m}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

                if os.path.exists(excel_name):
                    os.remove(excel_name)
            except Exception as e:
                st.error(f"Error al generar Excel: {e}")

        with col_exp3:
            # Botón de impresión - genera HTML descargable
            html_table_print = df_to_html_table(df_mes)
            
            print_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Reporte de Licencias</title>
    <style>
        @page {{ size: landscape; margin: 1cm; }}
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
        }}
        .title {{
            font-size: 20pt;
            font-weight: bold;
            margin-bottom: 10px;
            text-align: center;
        }}
        .subtitle {{
            font-size: 14pt;
            margin-bottom: 15px;
            text-align: center;
        }}
        .metrics {{
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            padding: 10px;
            background-color: #f5f5f5;
            border: 1px solid #ddd;
        }}
        .metric {{
            text-align: center;
            font-size: 11pt;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 9pt;
        }}
        th {{
            border: 1px solid #000;
            padding: 6px 8px;
            text-align: left;
            font-weight: bold;
            background-color: #e0e0e0;
        }}
        td {{
            border: 1px solid #000;
            padding: 5px 8px;
        }}
        @media print {{
            button {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="title">📋 Reporte de Licencias - Secretaría Escolar Mendoza</div>
    <div class="subtitle">Período: {primer_dia:%d/%m/%Y} — {ultimo_dia:%d/%m/%Y}</div>
    
    <div class="metrics">
        <div class="metric"><strong>Total:</strong> {len(df_mes)}</div>
        <div class="metric"><strong>Cargadas:</strong> {cargadas} ({cargadas / len(df_mes) * 100:.0f}%)</div>
        <div class="metric"><strong>Pendientes:</strong> {pendientes} ({pendientes / len(df_mes) * 100:.0f}%)</div>
        <div class="metric"><strong>Docentes:</strong> {docentes} | <strong>Celadores:</strong> {celadores}</div>
    </div>
    
    {html_table_print}
    
    <div style="text-align: center; margin-top: 20px;">
        <button onclick="window.print()" style="padding: 10px 20px; font-size: 14px; background-color: #ff4b4b; color: white; border: none; border-radius: 5px; cursor: pointer;">
            🖨️ Imprimir este reporte
        </button>
    </div>
</body>
</html>"""
            
            # Descargar como archivo HTML
            st.download_button(
                label="🖨️ Descargar vista de impresión",
                data=print_content,
                file_name=f"reporte_licencias_{primer_dia:%Y_%m}.html",
                mime="text/html",
                use_container_width=True,
                help="Descarga el reporte en HTML. Luego ábrelo y presiona Ctrl+P para imprimir"
            )

        st.caption("""
        💡 **Para imprimir:**
        1. Haz clic en "🖨️ Descargar vista de impresión"
        2. Abre el archivo HTML descargado en tu navegador
        3. Presiona Ctrl+P o haz clic en el botón "Imprimir"
        4. Selecciona tu impresora o "Guardar como PDF"
        """)

st.divider()
st.caption("🗂️ Sistema de Gestión de Licencias - Secretaría Escolar Mendoza | Versión 2.0")
st.caption("💻 Desarrollado por **Nicolas Maure** | [nicomaure.com.ar](https://nicomaure.com.ar)")