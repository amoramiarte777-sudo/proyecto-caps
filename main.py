import os
import csv
from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv

load_dotenv()

llm = LLM(model="openrouter/meta-llama/llama-3.1-8b-instruct", api_key=os.getenv("OPENROUTER_API_KEY"))

# Definimos al agente
redactor = Agent(
    role='Especialista en Soporte IT',
    goal='Redactar correos personalizados usando el nombre y empresa del cliente.',
    backstory='Experto en redes Cisco y TV, ahora redactando propuestas personalizadas.',
    llm=llm
)

def procesar_clientes():
    with open('clientes.csv', mode='r', encoding='utf-8') as archivo:
        lector = csv.DictReader(archivo)
        for cliente in lector:
            print(f"\n--- Preparando propuesta para {cliente['nombre']} de {cliente['empresa']} ---")
            
            tarea = Task(
                description=f"Escribe un correo profesional para {cliente['nombre']} de la empresa {cliente['empresa']}. Ofrécele reparación de TV y soporte de redes Cisco.",
                expected_output='Correo electrónico redactado.',
                agent=redactor
            )
            
            equipo = Crew(agents=[redactor], tasks=[tarea])
            resultado = equipo.kickoff()
            
            print(f"\nCorreo generado para {cliente['empresa']}:\n")
            print(resultado)

if __name__ == "__main__":
    procesar_clientes()