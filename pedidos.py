from fastapi import FastAPI
import httpx
from pydantic import BaseModel, StringConstraints, PositiveInt
from typing import Annotated, Literal

app = FastAPI()

nomeCliente = Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1)
        ]

class Pedido(BaseModel):
    id: PositiveInt
    cliente: nomeCliente
    produto: Literal["camisa", "calça", "sapato"]
    quantidade: PositiveInt


@app.post("/pedido")
def receber_pedidos(pedido: Pedido):

    response = httpx.post(
        "http://localhost:8000/webhook",
        json={
            "evento": "novo_pedido",
            "pedido_id": pedido.id,
            "cliente": pedido.cliente
        }
    )

    print(f"Resposta do webhook: {response.status_code} - {response.text}")
    return "pedido recebido"

