from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, StringConstraints, PositiveInt
from typing import Annotated, Literal
import logging
import httpx

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

    try:
        response = httpx.post(
            "http://127.0.0.1:8000/webhook",
            json={
                "evento": "novo_pedido",
                "pedido_id": pedido.id,
                "cliente": pedido.cliente
            },
            timeout=5.0
        )

        response.raise_for_status()

    except httpx.HTTPStatusError as erro:
        print(f"Webhook retornou erro: {erro.response.status_code}")

        raise HTTPException(
            status_code=502,
            detail="O webhook rejeitou a notificação."
        )

    except httpx.RequestError as erro:
        print(f"Erro de comunicação: {erro}")

        raise HTTPException(
            status_code=503,
            detail="Não foi possível comunicar com o webhook."
        )

    print(f"Resposta do webhook: {response.status_code}")

    return {
        "status": "pedido recebido",
        "pedido_id": pedido.id,
        "webhook_status": "enviado"
    }