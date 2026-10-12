from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, PositiveInt, StringConstraints
from typing import Annotated, Literal

app = FastAPI()

nomeCliente = Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1)
        ]

class Evento(BaseModel):
    evento: Literal["novo_pedido", "pedido_cancelado", "pedido_entregue"]
    pedido_id: PositiveInt
    cliente: nomeCliente


@app.post("/webhook")
def receber_webhook(dados: Evento):
    
    match dados.evento:
        case "novo_pedido":
            mensagem = "Novo pedido recebido!"
        
        case "pedido_cancelado":
            mensagem = "Pedido cancelado!"
                
        case "pedido_entregue":
            mensagem = "Pedido entregue!"


        case _:
            raise HTTPException(
                    status_code=400,
                    detail="Tipo de evento inválido"
            )


    print(mensagem)
    print(f"Evento: { dados.evento}")
    print(f"Pedido: {dados.pedido_id}")
    print(f"Cliente: {dados.cliente}")

    return {
            "status": "recebido",
            "evento": dados.evento,
            "pedido_id":dados.pedido_id
            }

