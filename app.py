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
    """Obtiene el directorio de datos en AppData/Local para evitar problemas de permisos"""
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
    fecha_fin: dt.date
    articulo: str
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
        df['fecha_fin'] = pd.to_datetime(df['fecha_fin']).dt.strftime('%d/%m/%Y')
    if 'fecha_carga_gei' in df.columns:
        df['fecha_carga_gei'] = df['fecha_carga_gei'].apply(
            lambda x: pd.to_datetime(x).strftime('%d/%m/%Y') if pd.notna(x) else ''
        )

    columnas_orden = [
        "id", "apellido", "nombre", "rol", "fecha_inicio", "fecha_fin",
        "articulo", "codigo_osep", "estado_carga", "fecha_carga_gei", "observaciones"
    ]
    columnas_disponibles = [col for col in columnas_orden if col in df.columns]
    df = df[columnas_disponibles]

    return df


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
            q = q.order_by(Licencia.apellido, Licencia.nombre, Licencia.fecha_inicio)
            return s.exec(q).all()
    except Exception as e:
        st.error(f"Error al buscar licencias: {e}")
        return []


def marcar_cargada(id_: int):
    return actualizar_licencia(
        id_,
        estado_carga="Cargada",
        fecha_carga_gei=dt.date.today()
    )


def obtener_licencia(id_: int):
    try:
        with Session(engine) as s:
            return s.get(Licencia, id_)
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

st.markdown("""
    <style>
    @media print {
        .stButton, .stTabs, .stDownloadButton {
            display: none !important;
        }
        .dataframe {
            font-size: 10pt !important;
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
            f_fin = st.date_input("Fecha fin*", value=dt.date.today())
            articulo = st.text_input("Artículo*", placeholder="Ej: Art. X inciso Y")

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
            if not articulo or not articulo.strip():
                errores.append("El artículo es obligatorio")
            if f_fin < f_ini:
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
                    fecha_fin=f_fin,
                    articulo=articulo.strip(),
                    codigo_osep=codigo_osep.strip() if codigo_osep.strip() else None,
                    observaciones=observ.strip() if observ.strip() else None,
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

        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()
        col_acc1, col_acc2, col_acc3 = st.columns(3)

        with col_acc1:
            sel_id = st.number_input("ID a marcar como CARGADA", min_value=1, step=1, key="marcar_id")
            if st.button("✅ Marcar como CARGADA", use_container_width=True):
                success, msg = marcar_cargada(int(sel_id))
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
                st.rerun()
            else:
                st.error(msg)

    if cargar_btn:
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
                    f_fin_e = st.date_input("Fecha fin*", value=lic.fecha_fin)
                    articulo_e = st.text_input("Artículo*", value=lic.articulo)

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
                    if not articulo_e or not articulo_e.strip():
                        errores.append("El artículo es obligatorio")
                    if f_fin_e < f_ini_e:
                        errores.append("La fecha de fin no puede ser anterior a la de inicio")

                    if errores:
                        for error in errores:
                            st.error(f"❌ {error}")
                    else:
                        success, msg = actualizar_licencia(
                            int(id_editar),
                            apellido=apellido_e.strip().upper(),
                            nombre=nombre_e.strip().title(),
                            rol=rol_e,
                            fecha_inicio=f_ini_e,
                            fecha_fin=f_fin_e,
                            articulo=articulo_e.strip(),
                            codigo_osep=codigo_osep_e.strip() if codigo_osep_e.strip() else None,
                            estado_carga=estado_e,
                            observaciones=observ_e.strip() if observ_e.strip() else None,
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

    rows_mes = buscar_licencias(f_ini=primer_dia, f_fin=ultimo_dia)
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

        if hoy > ultimo_dia and pendientes > 0:
            st.error(
                f"⚠️ **ATENCIÓN:** Hay {pendientes} licencia(s) PENDIENTE(S) - El plazo venció el {ultimo_dia:%d/%m/%Y}")
        elif pendientes > 0:
            dias_restantes = (ultimo_dia - hoy).days
            st.warning(f"⏰ Quedan {dias_restantes} día(s) para cargar {pendientes} licencia(s) pendiente(s)")
        else:
            st.success("✅ Todas las licencias del mes están cargadas")

        st.divider()
        st.dataframe(df_mes, use_container_width=True, hide_index=True)

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
            st.button("🖨️ Imprimir (Ctrl+P)", use_container_width=True,
                      help="Usa Ctrl+P o Cmd+P para abrir el diálogo de impresión del navegador")

        st.caption("""
        💡 **Tips para imprimir:**
        - Presioná **Ctrl+P** (Windows) o **Cmd+P** (Mac) para imprimir
        - Seleccioná 'Guardar como PDF' en el destino para generar un PDF
        - Ajustá los márgenes y orientación según necesites
        """)

st.divider()
st.caption("🗂️ Sistema de Gestión de Licencias - Secretaría Escolar Mendoza | Versión 2.0")