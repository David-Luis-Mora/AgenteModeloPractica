import subprocess
from langchain_ollama import ChatOllama
from langchain.messages import SystemMessage, HumanMessage
from langchain.agents import create_agent
from langchain.tools import tool


modelo = ChatOllama(model="qwen3:8b")


@tool
def listar_directorio(ruta: str = ".") -> str:
    """
    Lista los archivos y carpetas de la ruta indicada.
    """
    try:
        resultado = subprocess.run(
            ["ls", ruta],
            capture_output=True,
            text=True,
            check=True
        )
        return resultado.stdout if resultado.stdout else "No hay contenido en la ruta indicada."
    except subprocess.CalledProcessError as e:
        return f"No se pudo listar '{ruta}': {e.stderr}"


@tool
def crear_carpeta(nombre: str) -> str:
    """
    Crea una carpeta con el nombre indicado.
    """
    try:
        subprocess.run(
            ["mkdir", "-p", nombre],
            capture_output=True,
            text=True,
            check=True
        )
        return f"La carpeta '{nombre}' se creó correctamente."
    except subprocess.CalledProcessError as e:
        return f"No se pudo crear la carpeta '{nombre}': {e.stderr}"
    


@tool
def crear_archivos_con_extension(nombre, extension):
    """
    Crea el archivo con el nombre que te han pasado y con la extension
    """
    try:
        subprocess.run(
            ["touch", f"{nombre}.{extension}", nombre],
            capture_output=True,
            text=True,
            check=True
        )
        return f"El archivo'{nombre}' con la extension {extension} se creó correctamente."
    except subprocess.CalledProcessError as e:
        return f"No se pudo crear la carpeta '{nombre}': {e.stderr}"


agente = create_agent(
    model=modelo,
    tools=[listar_directorio, crear_carpeta,crear_archivos_con_extension]
)


mensaje = {
    "messages": [
        SystemMessage(
            "Eres un agente experto en gestionar documentos y carpetas en Linux. "
            "Cuando el usuario pida crear una carpeta, usa la herramienta crear_carpeta. "
            "Cuando pida listar archivos o directorios, usa la herramienta listar_directorio. "
            "El usuario si quiere crear archivo que te indique el nombre del archivo y la extension, usa la herramienta crear_archivos_con_extension"
            "Responde siempre en español y de manera clara."

        ),
        # HumanMessage("Creame la carpeta prueba2 en este directorio"),
        HumanMessage("Muestra todo los archivo en este directorio"),
        # HumanMessage("Creame el archivo de texto con el nombre de prueba y con la extension txt")
    ]
}


respuesta = agente.invoke(mensaje)

for msg in respuesta["messages"]:
    msg.pretty_print()