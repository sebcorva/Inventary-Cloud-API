# Backlog de Rebanadas Verticales (Tracer Bullets) — `ISSUES.md`

Este archivo divide el [PRD-payments-and-rbac.md](file:///Users/sebastiancorvalan/Documents/PROGRAMACION/Portafolio/inventary-cloud-api/docs/PRD-payments-and-rbac.md) en **4 Rebanadas Verticales independientes**. Cada Slice atraviesa todas las capas (Modelo $\rightarrow$ Esquema $\rightarrow$ Servicio/Endpoint $\rightarrow$ Tests) y debe implementarse en una sesión limpia aplicando la skill **`tdd`** (Rojo $\rightarrow$ Verde $\rightarrow$ Refactor).

---

## [ ] Slice 1: RBAC de Administradores (`is_admin`) y Desacoplamiento de `owner_id` en Catálogo
**Objetivo:** Transformar el catálogo para que pertenezca al negocio y solo usuarios `is_admin=True` puedan crear, editar o borrar productos, incluyendo el bootstrap del primer Admin y el endpoint de promoción de roles.

* **Capas tocadas:**
  * `app/models/user.py` (añadir `is_admin=False`) y `app/models/product.py` (eliminar `owner_id` y relación `owner`).
  * `app/schemas/user.py` (exponer `is_admin` en `UserResponse`, mantenerlo fuera de `UserCreate`, agregar `UserRoleUpdate`) y `app/schemas/product.py` (quitar `owner_id` de `ProductResponse`).
  * `app/api/deps.py` (crear dependencia `get_current_admin_user` que lance `403 Forbidden` si `not current_user.is_admin`).
  * `app/api/v1/endpoints/products.py` (usar `get_current_admin_user` en `POST`, `PUT`, `DELETE` y subida de imagen).
  * `app/api/v1/endpoints/users.py` + `app/config.py` (endpoint `PATCH /users/{user_id}/role` para admins y función `ensure_initial_admin` basada en variables de entorno `FIRST_SUPERUSER_*`).
  * Migración Alembic para reflejar el cambio en PostgreSQL.
* **Criterios de Aceptación (Tests TDD en `tests/test_auth.py` y `tests/test_products.py`):**
  1. Un usuario registrado vía `POST /auth/register` siempre nace con `is_admin == False` (incluso si envía `"is_admin": true` en el payload).
  2. Un usuario normal (`is_admin=False`) recibe `403 Forbidden` al intentar `POST /products`, `PUT /products/{id}`, `DELETE /products/{id}` o `POST /products/{id}/image`.
  3. Un usuario Admin (`is_admin=True`) puede hacer CRUD completo de productos sin restricción de `owner_id`.
  4. `ensure_initial_admin` crea el primer administrador desde configuración de forma idempotente, y un Admin puede promover a otro usuario mediante `PATCH /users/{id}/role`.
* **Dependencias:** Ninguna.

---

## [ ] Slice 2: Creación de Órdenes (`Order` + `OrderItem`) con Reserva Atómica de Stock
**Objetivo:** Permitir a cualquier usuario autenticado crear una orden de compra de uno o varios productos, congelando el precio unitario actual, descontando el stock atómicamente y emitiendo alertas a SQS.

* **Capas tocadas:**
  * `app/models/order.py` (Modelos `Order` y `OrderItem`) y registro en `app/models/__init__.py`.
  * `app/schemas/order.py` (`OrderCreate`, `OrderItemCreate`, `OrderResponse`, `OrderItemResponse`).
  * `app/api/v1/endpoints/orders.py` y montaje en `app/main.py` (`POST /orders`, `GET /orders`, `GET /orders/{order_id}`).
  * Migración Alembic para tablas `orders` y `order_items`.
* **Criterios de Aceptación (Tests TDD en `tests/test_orders.py`):**
  1. `POST /orders` con stock suficiente descuenta `Product.stock`, congela `unit_price`, calcula `total_amount` exacto, crea la orden en estado `PENDING` y emite el evento `ORDER_CREATED` (y `LOW_STOCK_ALERT` si el stock restante es `<= 5`) en SQS.
  2. Si posteriormente un Admin cambia el precio del producto, `OrderItem.unit_price` y `Order.total_amount` de la orden creada no cambian.
  3. Si un ítem de la orden pide más cantidad que el `stock` disponible, devuelve `409 Conflict` y hace rollback completo (ningún producto de la orden ve afectado su stock).
  4. `GET /orders` devuelve únicamente las órdenes del usuario autenticado.
* **Dependencias:** Slice 1.

---

## [ ] Slice 3: Checkout con Stripe (`PaymentGatewayPort`) e Idempotencia
**Objetivo:** Iniciar el proceso de cobro de una `Order` en estado `PENDING` a través de una interfaz desacoplada de Stripe, garantizando idempotencia ante reintentos.

* **Capas tocadas:**
  * `app/models/payment.py` (Modelo `Payment` con `idempotency_key`, `stripe_session_id`, `stripe_event_id`, `status`).
  * `app/services/payments/base.py` (`PaymentGatewayPort`) y `app/services/payments/stripe_service.py` (`StripePaymentAdapter`).
  * `app/schemas/payment.py` (`CheckoutRequest`, `CheckoutResponse`).
  * `app/api/v1/endpoints/payments.py` (`POST /payments/checkout` exigiendo header `Idempotency-Key`).
  * `app/config.py` y `requirements.txt` (agregar `stripe` y settings `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_SUCCESS_URL`, `STRIPE_CANCEL_URL`).
* **Criterios de Aceptación (Tests TDD en `tests/test_payments.py`):**
  1. `POST /payments/checkout` sobre una orden `PENDING` del usuario crea un registro `Payment` en estado `PENDING`, invoca `PaymentGatewayPort.create_checkout_session` y retorna `200 OK` con `checkout_url` y `session_id`.
  2. Enviar dos veces `POST /payments/checkout` con el mismo `Idempotency-Key` retorna la misma sesión (`200 OK`) sin duplicar el cobro en Stripe ni crear otro registro en base de datos.
  3. Intentar pagar la orden de otro usuario devuelve `403 Forbidden`; intentar pagar una orden que no está `PENDING` devuelve `409 Conflict`.
* **Dependencias:** Slice 2.

---

## [ ] Slice 4: Webhook de Stripe, Liberación de Stock, Recibo en S3 y Correo con AWS SES
**Objetivo:** Cerrar el ciclo de pago procesando el Webhook firmado por Stripe: si es exitoso, marcar `PAID`, subir recibo a S3, enviar email por AWS SES y publicar en SQS; si falla o expira, marcar `FAILED` y devolver el stock reservado.

* **Capas tocadas:**
  * `app/services/ses_service.py` (Servicio AWS SES con `boto3` para envío de correo de confirmación y fallback seguro a logs en local).
  * `app/services/receipt_service.py` (Generador de comprobante estructurado HTML/JSON y subida mediante `s3_service.upload_file`).
  * `app/api/v1/endpoints/payments.py` (`POST /payments/webhook` con verificación de header `Stripe-Signature` y control de duplicados por `stripe_event_id`).
* **Criterios de Aceptación (Tests TDD en `tests/test_payments.py`):**
  1. Un Webhook con firma inválida (`Stripe-Signature`) es rechazado con `400 Bad Request`.
  2. Evento `checkout.session.completed`: actualiza `Payment.status = "SUCCEEDED"`, `Order.status = "PAID"`, genera y sube el comprobante a S3 guardando `Order.receipt_url`, publica `PAYMENT_SUCCEEDED` en SQS y dispara el correo de confirmación en `ses_service`.
  3. Evento `checkout.session.expired` o `payment_intent.payment_failed`: actualiza `Payment.status = "FAILED"`, `Order.status = "FAILED"`, **restaura el `Product.stock` original** de todos los ítems de la orden y publica `PAYMENT_FAILED` en SQS.
  4. Reenviar el mismo `stripe_event_id` por segunda vez responde `200 OK` de forma idempotente sin volver a descontar/restaurar stock ni reenviar correos.
* **Dependencias:** Slice 3.
