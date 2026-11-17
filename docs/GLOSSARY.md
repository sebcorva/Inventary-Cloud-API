# Glosario del Dominio (Ubiquitous Language) — `inventary-cloud-api`

Este documento define el vocabulario estricto del dominio. Todo nuevo código (modelos SQLAlchemy, esquemas Pydantic, endpoints, servicios y eventos SQS) **debe usar exactamente estos nombres** para evitar ambigüedad.

| Término en Código | Definición en el Dominio |
| :--- | :--- |
| **`User`** | Cuenta autenticada en el sistema (`users`). Puede ser un **Cliente** (`is_admin=False`) que compra productos, o un **Administrador** (`is_admin=True`) que gestiona el catálogo y roles. |
| **`Admin` (`is_admin`)** | Atributo booleano en `User`. Único rol autorizado para hacer CRUD de productos (`POST`, `PUT`, `DELETE /products`, subida de imágenes) y promover otros usuarios (`PATCH /users/{id}/role`). |
| **`Product`** | Ítem del catálogo global de la tienda (`products`) con precio unitario (`price`), inventario disponible (`stock`) e imagen en S3 (`image_url`). Ya no pertenece a un `owner_id` individual, sino al catálogo del negocio. |
| **`Order`** | Orden de compra creada por un `User` (`orders`). Agrupa uno o más `OrderItem`, congela el monto total (`total_amount`) y transiciona por los estados: `PENDING` $\rightarrow$ `PAID` | `FAILED` | `CANCELLED`. |
| **`OrderItem`** | Línea individual dentro de una `Order` (`order_items`). Vincula un `product_id`, la cantidad solicitada (`quantity`) y el precio unitario congelado en el momento de la compra (`unit_price`). |
| **`Stock Reservation`** | Descuento atómico e inmediato de `Product.stock` al momento de crear la `Order` / iniciar el Checkout, protegido contra condiciones de carrera. Si el pago falla o se cancela, el stock se restaura (**Stock Release**). |
| **`Payment`** | Registro de una transacción financiera asociada a una `Order` (`payments`). Contiene el proveedor (`stripe`), identificadores externos (`stripe_session_id`, `stripe_event_id`), `idempotency_key`, monto y estado (`PENDING`, `SUCCEEDED`, `FAILED`). |
| **`PaymentGatewayPort`** | Interfaz abstracta (`Protocol` / `ABC`) que desacopla nuestra lógica de negocio del SDK de Stripe. Permite inyectar `StripePaymentAdapter` en producción y un `FakePaymentAdapter` determinista en tests. |
| **`IdempotencyKey`** | Clave única enviada por el cliente (o generada por orden) que garantiza que reintentos de red o dobles clics en `POST /payments/checkout` nunca generen dos cobros ni descuenten stock dos veces. |
| **`WebhookEvent`** | Notificación HTTP asíncrona firmada criptográficamente por Stripe (`POST /payments/webhook`) que confirma el resultado final del pago (`checkout.session.completed` o fallo/expiración). |
| **`Receipt`** | Comprobante estructurado (HTML/JSON) generado automáticamente al confirmarse un pago (`PAID`), almacenado en **Amazon S3** (`Order.receipt_url`) y enviado por correo al comprador vía **Amazon SES**. |
