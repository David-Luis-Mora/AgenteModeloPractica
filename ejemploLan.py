# from langchain_ollama import ChatOllama
# from langchain.messages import SystemMessage,HumanMessage
# from langchain.agents import create_agent
# from langchain.tools import tool,ToolRuntime
# from dataclasses import dataclass
# from typing import List


# PERSONA = [
#         {"Nombre": "David","Age":"50"},
#         {"Nombre": "Hugo","Age":"33"},
#         {"Nombre": "Lucia","Age":"20"},
#         {"Nombre": "Paula","Age":"40"},
#     ]




# class ContextClass():
#     LISTA_PERSONAJES: List[dict]


# # modelo = ChatOllama(model="llama3.2:1b")
# modelo = ChatOllama(model="qwen3:8b")

# # print(modelo.invoke("¿comoo estas?"))


# # @tool
# # def ejemplo_david():
# #     """
# #     Al preguntar por David devuelve la edad de manera que sea lenguaje natural
# #     """

# #     Persona = [
# #         {"Nombre": "David","Age":"50"},
# #     ]
# #     return Persona



# @tool
# def obtener_informacion_de_persona(name,contexto:ToolRuntime[ContextClass]):
#     """
#     Esta herramientas es para pasar la edad del nombre que te pasen por el prompt el usuario. Si el usuario no existe te devolvera falso en ese caso
#     le tendra que decir al usuario que no tiene conocimiento de dicha persona
#     """

#     PERSONAJES_RUNTIME=contexto.context.LISTA_PERSONAJE
   
#     for p in PERSONAJES_RUNTIME:
#         if p["Nombre"] == name:
#             return p["Age"]
    
#     return False







# mensaje = {
#     "messages":[
#         SystemMessage("Eres un assistente que dar informacion a la gente. Te pasaran un nombre una persona y en lenguaje natural le tendra que contestar a la iformacion que tiene"),
#         HumanMessage("Quien es David")

#     ]
# }




# agente = create_agent(model = modelo, tools=[obtener_informacion_de_persona], context_schema=ContextClass)



# respuesta = agente.invoke(input=mensaje,context=ContextClass(LISTA_PERSONAJES=PERSONA))

# for msg in respuesta["messages"]:
#     msg.pretty_print()




# from langchain_ollama import ChatOllama
# from langchain.messages import SystemMessage, HumanMessage
# from langchain.agents import create_agent
# from langchain.tools import tool, ToolRuntime
# from dataclasses import dataclass
# from typing import List


# PERSONA = [
#     {"Nombre": "David", "Age": "50"},
#     {"Nombre": "Hugo", "Age": "33"},
#     {"Nombre": "Lucia", "Age": "20"},
#     {"Nombre": "Paula", "Age": "40"},
# ]


# @dataclass
# class ContextClass:
#     LISTA_PERSONAJES: List[dict]


# modelo = ChatOllama(model="qwen3:8b")


# @tool
# def obtener_informacion_de_persona(name: str, contexto: ToolRuntime[ContextClass]):
#     """
#     Devuelve la edad de la persona si existe.
#     Si no existe devuelve False.
#     """

#     PERSONAJES_RUNTIME = contexto.context.LISTA_PERSONAJES

#     for p in PERSONAJES_RUNTIME:
#         if p["Nombre"] == name:
#             return p["Age"]

#     return False


# mensaje = {
#     "messages": [
#         SystemMessage(
#             "Eres un asistente que da informacion a la gente. "
#             "Te pasaran un nombre de una persona y en lenguaje natural "
#             "tendras que contestar la informacion que tienes."
#         ),
#         HumanMessage("Quien es David")
#     ]
# }


# agente = create_agent(
#     model=modelo,
#     tools=[obtener_informacion_de_persona],
#     context_schema=ContextClass
# )


# respuesta = agente.invoke(
#     input=mensaje,
#     context=ContextClass(LISTA_PERSONAJES=PERSONA)
# )


# for msg in respuesta["messages"]:
#     msg.pretty_print()













from langchain_ollama import ChatOllama
from langchain.messages import SystemMessage, HumanMessage
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from dataclasses import dataclass
from typing import List
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.types import Command



PERSONA = [
    {"Nombre": "David", "Age": "50"},
    {"Nombre": "Hugo", "Age": "33"},
    {"Nombre": "Lucia", "Age": "20"},
    {"Nombre": "Paula", "Age": "40"},
]


@dataclass
class ContextClass:
    LISTA_PERSONAJES: List[dict]


modelo = ChatOllama(model="qwen3:8b")


@tool
def obtener_informacion_de_persona(name: str, contexto: ToolRuntime[ContextClass]):
    """
    Devuelve la edad de la persona si existe.
    Si no existe devuelve False.
    """

    PERSONAJES_RUNTIME = contexto.context.LISTA_PERSONAJES

    for p in PERSONAJES_RUNTIME:
        if p["Nombre"] == name:
            return p["Age"]

    return False


mensaje = {
    "messages": [
        SystemMessage(
            "Eres un asistente que da informacion a la gente. "
            "Te pasaran un nombre de una persona y en lenguaje natural "
            "tendras que contestar la informacion que tienes."
        ),
        HumanMessage("Quien es David")
    ]
}


PROMP_SISTEMA = """
Eres un agente que ayuda al usuario a darle informacion al usuario sobre Tenerife y lugares para hacer turismo
Tanto actividades de todo tipo, gastronomia, en relacion a monumento historico, miradores para sacar foto, naturaleza y lugares de centro comerciales
"""

PROMP_SISTEMA = """
Eres un agente que contesta al usuario lo que te pida
"""



agente = create_agent(
    model=modelo,
    tools=[obtener_informacion_de_persona],
    system_prompt=PROMP_SISTEMA,
    checkpointer =InMemorySaver(),
    context_schema=ContextClass,
    middleware = [ HumanInTheLoopMiddleware(interrupt_on={"obtener_informacion_de_persona" : True},)]
)


# respuesta = agente.invoke(
#     input=mensaje,
#     context=ContextClass(LISTA_PERSONAJES=PERSONA)
# )




# for msg in respuesta["messages"]:
#     msg.pretty_print()





while (prompt := input("> ")) != "end":
        for paso in agente.stream({
            "messages": [
                HumanMessage(prompt),
                # SystemMessage()
            ]
        }, stream_mode="values", config = {
                "configurable":{
                     "thread_id": "Alejandro",

                },
                 
            }, context=ContextClass(LISTA_PERSONAJES=PERSONA)):
            ultimo_mensaje = paso["messages"][-1]

            hayRazonamiento = ""
            if hasattr(ultimo_mensaje, "additional_kwargs"): # sí, asi de escondido está el razonamiento
                hayRazonamiento = ultimo_mensaje.additional_kwargs.get("reasoning_content", "")

            if hayRazonamiento:
                print("\n=== PENSANDO ===")
                print(hayRazonamiento)

            print("\n=== MENSAJE ===")
            ultimo_mensaje.pretty_print()
            if "__interrupt__" in paso:
                print("HAY UNA INTERRUPCIÓN")
                input("Pon un dato")

                respuesta =agente.invoke(
                    Command(
                        resume={

                            "decisions":[
                                {
                                    # "type":"approve",
                                    "type":"reject",
                                }

                            ]
                        },
                        
                    ),
                    config ={

                            "configurable":{
                                    "thread_id": "Alejandro"
                                }
                        },
                    context=ContextClass(LISTA_PERSONAJES=PERSONA)
                )

                for msg in respuesta["messages"]:
                    msg.pretty_print()