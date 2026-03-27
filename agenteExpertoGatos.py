import requests
from langchain_ollama import ChatOllama
from langchain.messages import SystemMessage, HumanMessage
from langchain.agents import create_agent
from langchain.tools import tool


modelo = ChatOllama(model="qwen3:8b")
# modelo = ChatOllama(model="llama3.2:1b")


@tool
def obtener_datos_curiosos_gatos(count: int = 1) -> list[str]:
    """
    Devuelve datos curiosos aleatorios sobre gatos.
    count indica cuántos datos devolver.
    """
    # if count < 1:
    #     count = 1
    # if count > 20:
    #     count = 20

    url = "https://meowfacts.herokuapp.com/"
    params = {"count": count}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        payload = response.json()

        facts = payload.get("data", [])
        if not facts:
            return ["No he encontrado datos curiosos en este momento."]

        return facts

    except requests.RequestException as e:
        return [f"Error al consultar la API: {str(e)}"]
    except ValueError:
        return ["La respuesta de la API no es un JSON válido."]


agente = create_agent(
    model=modelo,
    tools=[obtener_datos_curiosos_gatos]
)


mensaje = {
    "messages": [
        SystemMessage(
            "Eres un agente experto en gatos. "
            "Tu especialidad es ofrecer datos curiosos sobre gatos. "
            "Cuando el usuario pida uno o varios datos curiosos, usa siempre la herramienta. "
            "Si pide N datos, llama a la herramienta con ese valor. "
            "Devuelve la respuesta en español. "
            "Si recibes varios datos, preséntalos numerados. "
            "No inventes datos si la herramienta ya ha respondido."
        ),
        HumanMessage("Dame 10 curiosidades de gatos")
    ]
}


respuesta = agente.invoke(mensaje)

for msg in respuesta["messages"]:
    msg.pretty_print()