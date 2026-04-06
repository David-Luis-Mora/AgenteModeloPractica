
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

def hablarConChat(model, herramientas, prompt_sistema):
    agente = create_agent(model, tools=herramientas,
                      system_prompt=prompt_sistema)
    while (prompt := input("> ")) != "end":
        for paso in agente.stream({
            "messages": [
                HumanMessage(prompt)
            ]
        }, stream_mode="values"):
            ultimo_mensaje = paso["messages"][-1]

            hayRazonamiento = ""
            if hasattr(ultimo_mensaje, "additional_kwargs"): # sí, asi de escondido está el razonamiento
                hayRazonamiento = ultimo_mensaje.additional_kwargs.get("reasoning_content", "")

            if hayRazonamiento:
                print("\n=== PENSANDO ===")
                print(hayRazonamiento)

            print("\n=== MENSAJE ===")
            ultimo_mensaje.pretty_print()

