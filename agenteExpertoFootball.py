from langchain_ollama import ChatOllama
from langchain.messages import SystemMessage, HumanMessage
from langchain.agents import create_agent
from langchain.tools import tool
import sqlite3







modelo = ChatOllama(model="qwen3:8b")



@tool
def consulta_diferentes_tabla(consulta_sql) -> str:
    """
    Esta herramienta se le pasa el parametro en string y lo ejecuta.
    Si te da error cambia la consulta algo mas sencillo
    Si no sabe algun campo de alguna tabla consulta que columna tiene dicha tabla y vuelve a ejecutar la herramienta
    """
    conn = sqlite3.connect('sports_league.sqlite')
    cur = conn.cursor()
    cur.execute(f'{consulta_sql}')
    rows = cur.fetchall()
    conn.close()
    consulta = []
    for row in rows:
        consulta.append(row)

    if len(consulta) > 0:
        return consulta
    else:
        return False


agente = create_agent(
    model=modelo,
    tools=[consulta_diferentes_tabla]
)



mensaje = {
    "messages": [
        SystemMessage(
            """
            El usuario te va a pedir informacion y tu tiene que crear la sentencia en SQL y la funcion lo ejecuto la que pases por parametro, tiene que pasarlo en string"
            Aqui tiene el nombre de las tablas: coaches, leagues, matches, players, referees, scores, seasons, stadiums, standings, teams
            Se te va a devolver la informacion en una lista y le tiene que desarollar en lemguaje natural para el usuario
            Solo muestra los 5 primeros resultados
            """
        ),
        HumanMessage("Muestra los jugadores Españoles"),
    ]
}



respuesta = agente.invoke(mensaje)


for msg in respuesta["messages"]:
    msg.pretty_print()