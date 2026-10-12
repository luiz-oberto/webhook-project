from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, StringConstraints, PositiveInt
from typing import Annotated, Literal
import logging
import httpx

app = FastAPI()

NomeCliente = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1)
]


# Inicializa o logger para registrar informações e erros do serviço de pedidos
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

file_handler = logging.FileHandler(
    "pedidos.log", 
    encoding="utf-8"
)

file_handler.setLevel(logging.INFO)

file_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
)

logger.addHandler(file_handler)


# ========================================================
logger.info("Iniciando o serviço de pedidos...")


# Tratamento de erros de validação para capturar e registrar erros de validação de dados enviados para os endpoints da API.
@app.exception_handler(RequestValidationError)
async def tratar_erro_validacao(
    request: Request,
    erro: RequestValidationError
):
    erros = [
        {
            "campo": item["loc"],
            "tipo": item["type"]
        }
        for item in erro.errors()
    ]

    logger.warning(
        "VALIDACAO_API | Endpoint: %s | Erros: %s",
        request.url.path,
        erros
    )

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Dados enviados são inválidos."
        }
    )

class Pedido(BaseModel):
    id: PositiveInt
    cliente: NomeCliente
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

        response.raise_for_status() # -> para indicar se houve erro na resposta HTTP do webhook (4xx ou 5xx)

    except httpx.HTTPStatusError as erro:
        '''
        Este bloco captura erros de status HTTP retornados pelo webhook.
        Para outros códigos de erro, uma exceção HTTP 502 é levantada, indicando um problema na comunicação com o webhook. 
        '''

        logger.error(
            "ERRO_HTTP_WEBHOOK | Pedido: %s | HTTP: %s",
            pedido.id,
            erro.response.status_code
        )

        raise HTTPException(
            status_code=502,
            detail="Falha no serviço de notificações."
        ) from erro

    except httpx.RequestError as erro:
        
        logger.error(
            "FALHA_CONEXAO | Pedido: %s | Erro: %s",
            pedido.id,
            erro
        )
        raise HTTPException(
            status_code=503,
            detail="Não foi possível comunicar com o webhook."
        )


    logger.info(
        "ENVIADO | Pedido: %s | Webhook: %s",
        pedido.id,
        response.status_code
    )
    return {
        "status": "pedido recebido",
        "pedido_id": pedido.id,
        "webhook_status": "enviado"
    }