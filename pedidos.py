from fastapi import FastAPI
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
def pedidos(pedido: Pedido):
    print(f"Pedido recebido: {pedido}")
    
    return "pedido recebido"

