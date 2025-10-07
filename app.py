import datetime as dt
import os
import sys
from pathlib import Path
from dateutil.relativedelta import relativedelta
from typing import Optional, List

import pandas as pd
import streamlit as st
from sqlmodel import SQLModel, Field, create_engine, Session, select
from sqlalchemy import text


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
    dni: str
    dni_familiar: Optional[str] = None
    rol: str
    fecha_inicio: dt.date
    fecha_fin: Optional[dt.date] = None
    articulo: Optional[str] = None
    codigo_osep: Optional[str] = None
    estado_carga: str = "Pendiente"
    fecha_carga_gei: Optional[dt.date] = None
    documentacion: str = "Pendiente"
    observaciones: Optional[str] = None
    fecha_creacion: dt.datetime = Field(default_factory=dt.datetime.now)


def ensure_columns():
    """Asegura que existan las columnas dni y dni_familiar si la DB es vieja."""
    try:
        with engine.connect() as conn:
            # nombre de tabla por defecto en SQLModel = nombre de clase en minúscula
            cols = {row[1] for row in conn.execute(text("PRAGMA table_info('licencia')"))}
            if "dni" not in cols:
                conn.execute(text("ALTER TABLE licencia ADD COLUMN dni TEXT"))
            if "dni_familiar" not in cols:
                conn.execute(text("ALTER TABLE licencia ADD COLUMN dni_familiar TEXT"))
    except Exception as e:
        st.error(f"Error asegurando columnas: {e}")


def init_db():
    try:
        SQLModel.metadata.create_all(engine)
        ensure_columns()
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


@st.cache_data
def get_estados_documentacion() -> List[str]:
    return ["Pendiente", "Subida"]


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
    if 'articulo' in df.columns:
        df['articulo'] = df['articulo'].fillna('(Pendiente)')
    if 'documentacion' in df.columns:
        df['documentacion'] = df['documentacion'].fillna('Pendiente')

    columnas_orden = [
        "id", "apellido", "nombre", "dni", "dni_familiar", "rol", "fecha_inicio", "fecha_fin",
        "articulo", "codigo_osep", "estado_carga", "fecha_carga_gei", "documentacion", "observaciones"
    ]
    columnas_disponibles = [col for col in columnas_orden if col in df.columns]
    df = df[columnas_disponibles]

    return df


def df_to_html_table(df: pd.DataFrame) -> str:
    """Genera tabla HTML para impresión con estilos inline y colores"""
    if df.empty:
        return "<p>No hay datos</p>"
    
    columnas_legibles = {
        'id': 'ID',
        'apellido': 'Apellido',
        'nombre': 'Nombre',
        'dni': 'DNI',
        'dni_familiar': 'DNI familiar',
        'rol': 'Rol',
        'fecha_inicio': 'Inicio',
        'fecha_fin': 'Fin',
        'articulo': 'Artículo',
        'codigo_osep': 'Código',
        'estado_carga': 'Estado',
        'fecha_carga_gei': 'Carga GEI',
        'documentacion': 'Documentación',
        'observaciones': 'Observaciones'
    }
    
    html = '<table class="print-table" style="width:100%; border-collapse:collapse; font-size:9pt;">'
    html += '<thead><tr style="background-color:#f0f0f0;">'
    
    for col in df.columns:
        col_name = columnas_legibles.get(col, col)
        html += f'<th style="border:1px solid #ddd; padding:4px 6px; text-align:left; font-weight:bold;">{col_name}</th>'
    
    html += '</tr></thead><tbody>'
    
    for _, row in df.iterrows():
        es_cargada = (
            row.get('estado_carga') == 'Cargada' and
            row.get('fecha_carga_gei') not in [None, '']
        )
        
        if es_cargada:
            row_style = 'background-color:#d4edda; color:#000000;'
        else:
            row_style = 'background-color:white;'
        
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
        estado_doc: Optional[str] = None,
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
            if estado_doc and estado_doc != "Todos":
                q = q.where(Licencia.documentacion == estado_doc)
            if articulo:
                q = q.where(Licencia.articulo.ilike(f"%{articulo}%"))
            if f_ini:
                q = q.where(Licencia.fecha_inicio >= f_ini)
            if f_fin:
                q = q.where(Licencia.fecha_fin <= f_fin)
            q = q.order_by(Licencia.id.desc())
            return s.exec(q).all()
    except Exception as e:
        st.error(f"Error al buscar licencias: {e}")
        return []


def marcar_cargada(id_: int, fecha_carga: Optional[dt.date] = None):
    """Marca una licencia como cargada con la fecha especificada"""
    if fecha_carga is None:
        fecha_carga = dt.date.today()
    
    try:
        with Session(engine) as s:
            lic = s.get(Licencia, id_)
            if not lic:
                return False, "No se encontró la licencia"
            
            if fecha_carga < lic.fecha_inicio:
                return False, f"La fecha de carga GEI ({fecha_carga:%d/%m/%Y}) no puede ser anterior a la fecha de inicio de la licencia ({lic.fecha_inicio:%d/%m/%Y})"
    except Exception as e:
        return False, f"Error al validar: {e}"
    
    return actualizar_licencia(
        id_,
        estado_carga="Cargada",
        fecha_carga_gei=fecha_carga
    )


def marcar_documentacion_subida(id_: int):
    """Marca la documentación como subida"""
    return actualizar_licencia(id_, documentacion="Subida")


def obtener_licencia(id_: int):
    try:
        with Session(engine) as s:
            lic = s.get(Licencia, id_)
            if lic:
                return Licencia(
                    id=lic.id,
                    apellido=lic.apellido,
                    nombre=lic.nombre,
                    dni=lic.dni,
                    dni_familiar=lic.dni_familiar,
                    rol=lic.rol,
                    fecha_inicio=lic.fecha_inicio,
                    fecha_fin=lic.fecha_fin,
                    articulo=lic.articulo,
                    codigo_osep=lic.codigo_osep,
                    estado_carga=lic.estado_carga,
                    fecha_carga_gei=lic.fecha_carga_gei,
                    documentacion=lic.documentacion,
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

# Estilos CSS
st.markdown("""
    <style>
    @media screen {
        .print-table { display: none !important; }
        .print-container { display: none !important; }
    }
    
    @media print {
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [data-testid="stMainMenu"],
        header, footer, .stApp > header, .stDeployButton,
        button, .stTabs, .stMarkdown > div > div > button,
        iframe, .no-print, h1:first-of-type,
        [data-testid="stExpander"], hr:last-of-type,
        .stMarkdown:has(hr) ~ .stMarkdown,
        [data-testid="stDataFrame"] {
            display: none !important;
            visibility: hidden !important;
        }
        
        .print-container {
            display: block !important;
            visibility: visible !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 20px !important;
        }
        
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
        
        @page { size: landscape; margin: 1.5cm 1cm; }
        body { -webkit-print-color-adjust: exact !important; }
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
            dni = st.text_input("DNI*", max_chars=15)
            dni_familiar = st.text_input("DNI familiar", max_chars=15, help="Solo si corresponde")
            rol = st.selectbox("Rol*", options=get_roles())

        with col2:
            f_ini = st.date_input("Fecha inicio*", value=dt.date.today())
            f_fin = st.date_input("Fecha fin", value=None, help="Opcional")
            articulo = st.text_input("Artículo", placeholder="Ej: Art. X inciso Y", help="Opcional")

        with col3:
            codigo_osep = st.text_input("Código de licencia", placeholder="Ej: AUS-12345")
            documentacion = st.selectbox("Documentación*", options=get_estados_documentacion())
            observ = st.text_area("Observaciones", height=90)

        submitted = st.form_submit_button("💾 Guardar licencia", type="primary", use_container_width=True)

        if submitted:
            errores = []
            if not apellido or not apellido.strip():
                errores.append("El apellido es obligatorio")
            if not nombre or not nombre.strip():
                errores.append("El nombre es obligatorio")
            # Validación DNI obligatorio y numérico
            if not dni or not dni.strip():
                errores.append("El DNI es obligatorio")
            elif not dni.strip().isdigit():
                errores.append("El DNI debe tener solo números")
            # DNI familiar opcional pero numérico si se brinda
            if dni_familiar and dni_familiar.strip() and not dni_familiar.strip().isdigit():
                errores.append("El DNI familiar debe tener solo números")

            if f_fin and f_fin < f_ini:
                errores.append("La fecha de fin no puede ser anterior a la de inicio")

            if errores:
                for error in errores:
                    st.error(f"❌ {error}")
            else:
                lic, error = crear_licencia(
                    apellido=apellido.strip().upper(),
                    nombre=nombre.strip().title(),
                    dni=dni.strip(),
                    dni_familiar=dni_familiar.strip() if dni_familiar and dni_familiar.strip() else None,
                    rol=rol,
                    fecha_inicio=f_ini,
                    fecha_fin=f_fin if f_fin else None,
                    articulo=articulo.strip() if articulo and articulo.strip() else None,
                    codigo_osep=codigo_osep.strip() if codigo_osep and codigo_osep.strip() else None,
                    documentacion=documentacion,
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
        estado_doc=None,
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

        st.caption("💡 **Leyenda:** Las filas con fondo verde claro indican licencias **marcadas como CARGADAS** en el sistema GEI")
        
        def highlight_complete_rows(row):
            es_cargada = (
                row.get('estado_carga') == 'Cargada' and
                row.get('fecha_carga_gei') not in [None, '']
            )
            color = 'background-color: #d4edda; color: #000000' if es_cargada else ''
            return [color] * len(row)
        
        df_styled = df.style.apply(highlight_complete_rows, axis=1)
        st.dataframe(df_styled, use_container_width=True, hide_index=True)
        
        html_table = df_to_html_table(df)
        docentes = len([r for r in rows if r.rol == "Docente"])
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
        </div>
        """
        st.markdown(print_html, unsafe_allow_html=True)

        st.divider()
        col_acc1, col_acc2, col_acc3 = st.columns(3)

        with col_acc1:
            st.markdown("##### Marcar como CARGADA")
            sel_id = st.number_input("ID", min_value=1, step=1, key="marcar_id")
            fecha_carga_sel = st.date_input("Fecha carga GEI", value=dt.date.today(), key="fecha_carga_gei")
            if st.button("✅ Marcar CARGADA", use_container_width=True):
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
                    dni_e = st.text_input("DNI*", value=lic.dni or "", max_chars=15)
                    rol_e = st.selectbox("Rol*", options=get_roles(), index=get_roles().index(lic.rol))

                with col2:
                    dni_familiar_e = st.text_input("DNI familiar", value=lic.dni_familiar or "", max_chars=15)
                    f_ini_e = st.date_input("Fecha inicio*", value=lic.fecha_inicio)
                    f_fin_e = st.date_input("Fecha fin", value=lic.fecha_fin, help="Opcional")
                    articulo_e = st.text_input("Artículo", value=lic.articulo or "", help="Opcional")

                with col3:
                    codigo_osep_e = st.text_input("Código de licencia", value=lic.codigo_osep or "")
                    estado_e = st.selectbox("Estado*", options=get_estados(),
                                            index=get_estados().index(lic.estado_carga))
                    documentacion_e = st.selectbox("Documentación*", options=get_estados_documentacion(),
                                                   index=get_estados_documentacion().index(lic.documentacion))
                    observ_e = st.text_area("Observaciones", value=lic.observaciones or "", height=90)

                actualizar = st.form_submit_button("💾 Actualizar licencia", type="primary", use_container_width=True)

                if actualizar:
                    errores = []
                    if not apellido_e or not apellido_e.strip():
                        errores.append("El apellido es obligatorio")
                    if not nombre_e or not nombre_e.strip():
                        errores.append("El nombre es obligatorio")
                    # DNI obligatorio y numérico
                    if not dni_e or not dni_e.strip().isdigit():
                        errores.append("El DNI es obligatorio y debe tener solo números")
                    # DNI familiar opcional pero numérico si se brinda
                    if dni_familiar_e and dni_familiar_e.strip() and not dni_familiar_e.strip().isdigit():
                        errores.append("El DNI familiar debe tener solo números")
                    if f_fin_e and f_fin_e < f_ini_e:
                        errores.append("La fecha de fin no puede ser anterior a la de inicio")

                    if errores:
                        for error in errores:
                            st.error(f"❌ {error}")
                    else:
                        codigo_osep_valor = codigo_osep_e.strip() if codigo_osep_e and codigo_osep_e.strip() else None
                        articulo_valor = articulo_e.strip() if articulo_e and articulo_e.strip() else None
                        
                        success, msg = actualizar_licencia(
                            int(id_editar),
                            apellido=apellido_e.strip().upper(),
                            nombre=nombre_e.strip().title(),
                            dni=dni_e.strip(),
                            dni_familiar=dni_familiar_e.strip() if dni_familiar_e and dni_familiar_e.strip() else None,
                            rol=rol_e,
                            fecha_inicio=f_ini_e,
                            fecha_fin=f_fin_e if f_fin_e else None,
                            articulo=articulo_valor,
                            codigo_osep=codigo_osep_valor,
                            estado_carga=estado_e,
                            documentacion=documentacion_e,
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

    try:
        with Session(engine) as s:
            q = select(Licencia)
            q = q.where(Licencia.fecha_inicio >= primer_dia)
            q = q.where(Licencia.fecha_inicio <= ultimo_dia)
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
        **Período:** {primer_dia:%d/%m/%Y} – {ultimo_dia:%d/%m/%Y}
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
        
        st.caption("💡 **Leyenda:** Las filas con fondo verde claro indican licencias **marcadas como CARGADAS** en el sistema GEI")
        
        def highlight_complete_rows(row):
            es_cargada = (
                row.get('estado_carga') == 'Cargada' and
                row.get('fecha_carga_gei') not in [None, '']
            )
            color = 'background-color: #d4edda; color: #000000' if es_cargada else ''
            return [color] * len(row)
        
        df_styled = df_mes.style.apply(highlight_complete_rows, axis=1)
        st.dataframe(df_styled, use_container_width=True, hide_index=True)

        st.divider()
        
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
    <div class="subtitle">Período: {primer_dia:%d/%m/%Y} – {ultimo_dia:%d/%m/%Y}</div>
    
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
st.caption("🗂️ Sistema de Gestión de Licencias - Secretaría Escolar Mendoza | Versión 2.1")
st.caption("💻 Desarrollado por **Nicolas Maure** | [nicomaure.com.ar](https://nicomaure.com.ar)")
