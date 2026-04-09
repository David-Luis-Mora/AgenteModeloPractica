from dataclasses import dataclass
from typing import Optional

import json
from datetime import datetime

import pandas as pd

from langchain_ollama import ChatOllama
from langchain.messages import HumanMessage
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.types import Command


@dataclass
class ContextClass:
    csv_path: str
    reservas_path: str




# modelo = ChatOllama(model="qwen3:8b")


modelo = ChatOllama(
    model="gemma4:e4b",
    base_url="http://192.168.117.48:11434"
)



def cargar_destinos(csv_path):
    """
    Carga el CSV de destinos y valida columnas mínimas.
    """
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"No existe el fichero CSV: {csv_path}")
    except Exception as e:
        raise RuntimeError(f"No se pudo leer el CSV: {e}")

    
    df.columns = [c.strip().lower() for c in df.columns]

    columnas_minimas = {"pais", "destino"}
    faltan = columnas_minimas - set(df.columns)
    if faltan:
        raise ValueError(
            f"Al CSV le faltan columnas obligatorias: {', '.join(sorted(faltan))}"
        )

    
    if "tipo" not in df.columns:
        df["tipo"] = ""
    if "descripcion" not in df.columns:
        df["descripcion"] = ""
    if "precio_base" not in df.columns:
        df["precio_base"] = 0

    return df


def buscar_destino(df, destino):
    """
    Busca un destino ignorando mayúsculas/minúsculas y espacios.
    """
    destino_norm = destino.strip().lower()
    return df[df["destino"].astype(str).str.strip().str.lower() == destino_norm]




@tool
def recomendar_destinos_por_pais(pais,runtime):
    """
    Devuelve una lista de destinos disponibles de un país.
    Úsala cuando el usuario pida recomendaciones o destinos de un país.
    """
    # if runtime.context is None:
    #     return "Error: no se recibió el contexto del sistema."
    df = cargar_destinos(runtime.context.csv_path)

    pais_norm = pais.strip().lower()
    filtrado = df[df["pais"].astype(str).str.strip().str.lower() == pais_norm]

    if filtrado.empty:
        paises_disponibles = sorted(df["pais"].dropna().astype(str).unique().tolist())
        return {
            "ok": False,
            "mensaje": f"No hay destinos para el país '{pais}'.",
            "paises_disponibles": paises_disponibles
        }

    resultados = []
    for _, row in filtrado.iterrows():
        resultados.append({
            "pais": str(row.get("pais", "")),
            "destino": str(row.get("destino", "")),
            "tipo": str(row.get("tipo", "")),
            "descripcion": str(row.get("descripcion", "")),
            "precio_base": float(row.get("precio_base", 0)) if str(row.get("precio_base", "")).strip() != "" else 0
        })

    return {
        "ok": True,
        "pais": pais,
        "total": len(resultados),
        "destinos": resultados
    }


@tool
def reservar_destino(
    destino: str,
    personas: int,
    nombre_cliente: str,
    runtime: ToolRuntime[ContextClass]
):
    """
    Reserva un destino para un número de personas y lo guarda en reservas.txt.
    Úsala solo cuando el usuario quiera confirmar una reserva real.
    
    """
    if runtime.context is None:
        return "Error: no se recibió el contexto del sistema."

    if not destino or not destino.strip():
        return {"ok": False, "mensaje": "Debes indicar un destino válido."}

    if not nombre_cliente or not nombre_cliente.strip():
        return {"ok": False, "mensaje": "Debes indicar un nombre de cliente válido."}

    if not isinstance(personas, int) or personas <= 0:
        return {"ok": False, "mensaje": "El número de personas debe ser un entero mayor que 0."}

    try:
        df = cargar_destinos(runtime.context.csv_path)
    except Exception as e:
        return {"ok": False, "mensaje": f"Error leyendo destinos: {e}"}

    encontrado = buscar_destino(df, destino)
    if encontrado.empty:
        destinos_disponibles = sorted(df["destino"].dropna().astype(str).unique().tolist())
        return {
            "ok": False,
            "mensaje": f"El destino '{destino}' no existe en la base de datos.",
            "destinos_disponibles": destinos_disponibles
        }

    row = encontrado.iloc[0]

    precio_base = row.get("precio_base", 0)
    try:
        precio_base = float(precio_base)
    except Exception:
        precio_base = 0.0

    total = precio_base * personas

    reserva = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nombre_cliente": nombre_cliente.strip(),
        "pais": str(row.get("pais", "")),
        "destino": str(row.get("destino", "")),
        "personas": personas,
        "precio_base": precio_base,
        "precio_total": total
    }

    try:
        with open(runtime.context.reservas_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(reserva, ensure_ascii=False) + "\n")
    except Exception as e:
        return {
            "ok": False,
            "mensaje": f"No se pudo escribir la reserva en el fichero: {e}"
        }

    return {
        "ok": True,
        "mensaje": "Reserva realizada correctamente.",
        "reserva": reserva
    }




PROMPT_SISTEMA = """
Eres el chatbot de una agencia de viajes especializada en destinos europeos.

Tu comportamiento:
- Puedes mantener conversación general sobre viajes, países, turismo y recomendaciones.
- Cuando el usuario pida destinos o recomendaciones de un país, usa la herramienta
  recomendar_destinos_por_pais.
- Cuando el usuario quiera reservar un destino para una o más personas, usa la herramienta
  reservar_destino.
- No inventes destinos que no estén en la base de datos.
- Si falta algún dato para reservar (destino, número de personas o nombre del cliente),
  pídelo con claridad.
- Si una herramienta devuelve error o no encuentra resultados, explícalo de forma amable.
- Cuando recomiendes destinos, resume la información de forma natural y útil.
- Cuando hagas una reserva, confirma claramente el destino, país, personas y precio total.
"""




agente = create_agent(
    model=modelo,
    tools=[recomendar_destinos_por_pais, reservar_destino],
    system_prompt=PROMPT_SISTEMA,
    checkpointer=InMemorySaver(),
    context_schema=ContextClass,
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "reservar_destino": True
            }
        )
    ]
)





print("=== BOT DE VIAJES ===")
print("Escribe 'end' para salir.\n")

config = {
"configurable": {
    "thread_id": "usuario_agencia_viajes"
}
}

contexto = ContextClass(
csv_path="destinations.csv",
reservas_path="reservas.txt"
    )

while (prompt := input("> ").strip()) != "end":
    for paso in agente.stream(
        {
            "messages": [HumanMessage(prompt)]
        },
        stream_mode="values",
        config=config,
        context=contexto
    ):
        ultimo_mensaje = paso["messages"][-1]

        razonamiento = ""
        if hasattr(ultimo_mensaje, "additional_kwargs"):
            razonamiento = ultimo_mensaje.additional_kwargs.get("reasoning_content", "")

        if razonamiento:
            print("\n=== PENSANDO ===")
            print(razonamiento)

        print("\n=== MENSAJE ===")
        ultimo_mensaje.pretty_print()

        # Si hay interrupción HITL
        if "__interrupt__" in paso:
            print("\n=== HITL: RESERVA PENDIENTE DE APROBACIÓN ===")
            decision = input("¿Aprobar reserva? (approve/reject): ").strip().lower()

            if decision not in {"approve", "reject"}:
                print("Decisión no válida. Se tomará como reject.")
                decision = "reject"

            respuesta = agente.invoke(
                Command(
                    resume={
                        "decisions": [
                            {
                                "type": decision
                            }
                        ]
                    }
                ),
                config=config,
                context=contexto
            )

            print("\n=== RESPUESTA FINAL ===")
            for msg in respuesta["messages"]:
                msg.pretty_print()




