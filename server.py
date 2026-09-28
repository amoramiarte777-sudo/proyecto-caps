from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crewai import Agent, Task, Crew, LLM
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configuración de CORS: Permite que tu landing se comunique con este servidor
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Cambia "*" por "https://landing.pestanatech.com" en producción
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración del modelo
llm = LLM(
    model="openrouter/meta-llama/llama-3.1-8b-instruct", 
    api_key=os.getenv("OPENROUTER_API_KEY")
)

class Cliente(BaseModel):
    nombre: str
    empresa: str

# Agente definido globalmente para mayor eficiencia
redactor = Agent(
    role='Consultor de Transformación Digital B2B',
    goal='Redactar una propuesta de valor persuasiva y técnica.',
    backstory="""Eres un experto en redes Cisco y soporte IT con gran capacidad técnica. 
    Estudias Ingeniería de Sistemas y te destacas por tu profesionalismo en Cartagena. 
    Tu tono es ejecutivo, enfocado en resolver problemas de conectividad y soporte técnico.""",
    llm=llm,
    verbose=True,
    allow_delegation=False
)

@app.post("/redactar")
async def redactar_correo(cliente: Cliente):
    try:
        def ejecutar_crew():
            tarea = Task(
                description=f"Redacta un correo profesional para {cliente.nombre} de la empresa {cliente.empresa}. Ofrécele servicios de soporte técnico especializado en redes Cisco y reparación de TV. Menciona tu perfil como estudiante de Ingeniería de Sistemas. Enfócate en el valor de una visita diagnóstica para mejorar su infraestructura.",
                expected_output='Correo electrónico profesional y persuasivo.',
                agent=redactor
            )
            equipo = Crew(agents=[redactor], tasks=[tarea])
            return equipo.kickoff()

        resultado = await asyncio.to_thread(ejecutar_crew)
        return {"correo": str(resultado)}
    
    except Exception as e:
        return {"error": str(e)}

# Para correrlo usa: uvicorn server:app --reload