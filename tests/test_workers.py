import pytest
from app.workers.sqs_consumer import lambda_handler, process_event

def test_process_event_product_created(caplog):
    """Verifica que el evento PRODUCT_CREATED se procese y registre en logs."""
    payload = {"product_id": 42, "title": "Cámara Digital"}
    with caplog.at_level("INFO"):
        process_event("PRODUCT_CREATED", payload)
    assert "Notificando creación del producto ID 42" in caplog.text

def test_process_event_low_stock_alert(caplog):
    """Verifica que el evento LOW_STOCK_ALERT emita un log de advertencia."""
    payload = {"product_id": 10, "current_stock": 2}
    with caplog.at_level("WARNING"):
        process_event("LOW_STOCK_ALERT", payload)
    assert "ALERTA: Producto ID 10 tiene stock crítico" in caplog.text

def test_lambda_handler_success():
    """Verifica que lambda_handler procese los registros SQS retornando status exitoso."""
    sqs_event = {
        "Records": [
            {
                "messageId": "msg-001",
                "body": '{"event_type": "PRODUCT_CREATED", "payload": {"product_id": 1, "title": "Test"}}',
            },
            {
                "messageId": "msg-002",
                "body": '{"event_type": "LOW_STOCK_ALERT", "payload": {"product_id": 1, "current_stock": 3}}',
            },
        ]
    }
    result = lambda_handler(sqs_event, context={})
    assert result["status"] == "success"
    assert result["processed_records"] == 2

def test_lambda_handler_error_raises():
    """Verifica que un mensaje con JSON malformado arroje error para que SQS reintente."""
    sqs_event = {
        "Records": [
            {
                "messageId": "msg-broken",
                "body": "MALFORMED_JSON_STRING",
            }
        ]
    }
    with pytest.raises(Exception):
        lambda_handler(sqs_event, context={})
