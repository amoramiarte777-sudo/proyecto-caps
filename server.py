from fastapi import FastAPI
from pydantic import BaseModel
from crewai import Agent, Task, Crew, LLM
import os
import litellm
import asyncio
from dotenv import load_dotenv

# Configuración de seguridad y entorno
litellm.drop_params = True 
load_dotenv()

app = FastAPI()

# Modelo definido para OpenRouter
llm = LLM(
    model="openrouter/meta-llama/llama-3.1-8b-instruct", 
    api_key=os.getenv("OPENROUTER_API_KEY")
)

class Cliente(BaseModel):
    nombre: str
    empresa: str

@app.post("/redactar")
async def redactar_correo(cliente: Cliente):
    try:
        print(f"--- Recibiendo solicitud para: {cliente.nombre} en {cliente.empresa} ---")
        
        # Función que corre el agente en un hilo separado
        def ejecutar_crew():
            redactor = Agent(
                role='Especialista en Soporte IT',
                goal='Redactar un mensaje persuasivo.',
                backstory='Eres un técnico experto en reparación de televisores en Cartagena y estudiante de Ingeniería de Sistemas.',
                llm=llm,
                verbose=True,
                allow_delegation=False
            )
            
            tarea = Task(
                description=f"Redacta un correo profesional para {cliente.nombre} de la empresa {cliente.empresa}. Ofrécele reparación de TV y redes Cisco, mencionando que eres estudiante de Ingeniería de Sistemas. Sé formal y ofrece una visita técnica de diagnóstico.",
                expected_output='Correo electrónico profesional.',
                agent=redactor
            )
            
            equipo = Crew(agents=[redactor], tasks=[tarea])
            return equipo.kickoff()

        # Ejecución segura para FastAPI
        resultado = await asyncio.to_thread(ejecutar_crew)
        
        return {"correo": str(resultado)}
    
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {"error": str(e)}

# Comando para ejecutar en terminal:
# "C:\Users\cesar\AppData\Local\Programs\Python\Python312\python.exe" -m uvicorn server:app --reload