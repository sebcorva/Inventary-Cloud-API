# Guía de Ejecución Local y Gestión de AWS S3

Esta guía detalla paso a paso cómo levantar el entorno completo de desarrollo con **Docker Compose**, cómo configurar un bucket en **Amazon S3** con sus credenciales seguras, la política de costos de AWS y el flujo práctico para realizar el **CRUD de usuarios y productos**.

---

## 📋 Tabla de Contenidos
1. [Requisitos Previos](#1-requisitos-previos)
2. [Configuración de Variables de Entorno](#2-configuración-de-variables-de-entorno)
3. [Guía AWS: Crear S3 Bucket y Credenciales IAM](#3-guía-aws-crear-s3-bucket-y-credenciales-iam)
   - [¿Esto genera costos en AWS?](#-esto-genera-costos-en-aws)
   - [Paso A: Crear el Bucket de S3](#paso-a-crear-el-bucket-de-s3)
   - [Paso B: Crear Credenciales IAM (Access Key y Secret Key)](#paso-b-crear-credenciales-iam-access-key-y-secret-key)
4. [Cómo Levantar la API y la Base de Datos con Docker](#4-cómo-levantar-la-api-y-la-base-de-datos-con-docker)
5. [Ejecutar Migraciones de Base de Datos (Alembic)](#5-ejecutar-migraciones-de-base-de-datos-alembic)
6. [Flujo Práctico: CRUD de Usuarios y Productos](#6-flujo-práctico-crud-de-usuarios-y-productos)
   - [Paso 1: Registro de Usuario](#paso-1-registro-de-usuario)
   - [Paso 2: Inicio de Sesión y Token JWT](#paso-2-inicio-de-sesión-y-token-jwt)
   - [Paso 3: Autenticación en Swagger UI](#paso-3-autenticación-en-swagger-ui)
   - [Paso 4: Crear un Producto](#paso-4-crear-un-producto)
   - [Paso 5: Subir Imagen a AWS S3](#paso-5-subir-imagen-a-aws-s3)
   - [Paso 6: Consultar, Actualizar y Eliminar Productos](#paso-6-consultar-actualizar-y-eliminar-productos)
7. [Cómo Detener los Servicios](#7-cómo-detener-los-servicios)

---

## 1. Requisitos Previos

Asegúrate de tener instalado en tu computadora:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) en ejecución.
- Git.
- Un navegador web (para acceder a Swagger UI) o Postman.

---

## 2. Configuración de Variables de Entorno

En la raíz del proyecto, asegúrate de tener tu archivo `.env` configurado. Puedes copiar la plantilla:

```bash
cp .env.example .env
```

Edita el archivo `.env` verificando los siguientes valores base:

```env
PROJECT_NAME="Inventory Cloud API"
ENVIRONMENT="development"

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgrespassword
POSTGRES_DB=inventory_db
POSTGRES_PORT=5432

# URL de conexión para el contenedor de la API (usa el nombre del servicio 'db')
DATABASE_URL="postgresql+psycopg://postgres:postgrespassword@db:5432/inventory_db"

# Clave secreta para firmar tokens JWT
SECRET_KEY="7053735cec0c61249ff4dc30211283de0fa80e49c4e2867cd5bc71aa5847cf25"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Configuración AWS (Completa con tus datos de la sección 3)
AWS_REGION="us-east-1"
S3_BUCKET_NAME="tu-nombre-de-bucket-aqui"
SQS_QUEUE_URL="https://sqs.us-east-1.amazonaws.com/123456789012/inventory-events-queue"
AWS_ACCESS_KEY_ID="tu_access_key_aqui"
AWS_SECRET_ACCESS_KEY="tu_secret_access_key_aqui"
```

> **Nota:** Si aún no creas el bucket o las claves de AWS, puedes dejar `S3_BUCKET_NAME=""` y la API seguirá funcionando localmente generando URLs simuladas.

---

## 3. Guía AWS: Crear S3 Bucket y Credenciales IAM

### 💰 ¿Esto genera costos en AWS?

**Prácticamente NADA ($0.00 USD).**

1. **Capa Gratuita de AWS (Free Tier):**
   - Durante los primeros 12 meses de tu cuenta, AWS incluye **5 GB de almacenamiento estándar en S3**, 20,000 solicitudes GET (lecturas) y 2,000 solicitudes PUT (subidas) completamente gratuitas cada mes.
2. **Si ya no tienes capa gratuita:**
   - Almacenar 10 o 20 fotos de prueba (aproximadamente 20 MB) cuesta alrededor de **$0.0004 USD al mes** (menos de un milésimo de dólar).
   - Crear el usuario IAM y las claves de acceso es **100% gratuito siempre**.

---

### Paso A: Crear el Bucket de S3

1. Inicia sesión en la [Consola de AWS](https://console.aws.amazon.com/).
2. En la barra de búsqueda superior, escribe **S3** y selecciona el servicio.
3. Haz clic en el botón naranja **Crear bucket** (*Create bucket*).
4. Configura las siguientes opciones:
   - **Región de AWS:** Selecciona `us-east-1` (EE.UU. Este - N. Virginia) o tu región preferida.
   - **Nombre del bucket:** Debe ser un nombre único a nivel mundial (por ejemplo: `inventory-assets-tu-nombre-dev`).
   - **Propiedad de objetos:** Deja la opción recomendada (*ACLs disabled*).
   - **Bloquear acceso público (*Block Public Access*):** 
     - Para un ejercicio práctico de portafolio donde quieras abrir la URL de la imagen directamente en el navegador, **desmarca** la casilla *"Bloquear todo el acceso público"* y marca la casilla de confirmación reconociendo que los objetos serán públicos.
5. Haz clic en **Crear bucket** al final de la página.
6. **Política del Bucket (para permitir lectura pública de fotos):**
   - Entra al bucket recién creado y haz clic en la pestaña **Permisos** (*Permissions*).
   - Busca la sección **Política del bucket** (*Bucket policy*) y haz clic en **Editar**.
   - Pega la siguiente política sustituyendo `tu-nombre-de-bucket-dev` por el nombre de tu bucket:
     ```json
     {
       "Version": "2012-10-17",
       "Statement": [
         {
           "Sid": "PublicReadGetObject",
           "Effect": "Allow",
           "Principal": "*",
           "Action": "s3:GetObject",
           "Resource": "arn:aws:s3:::tu-nombre-de-bucket-dev/*"
         }
       ]
     }
     ```
   - Haz clic en **Guardar cambios**.

---

### Paso B: Crear Credenciales IAM (Access Key y Secret Key)

Para que tu API local pueda subir archivos al bucket de S3 sin usar tu usuario raíz de AWS:

1. En la barra de búsqueda de AWS, busca y selecciona **IAM** (*Identity and Access Management*).
2. En el menú lateral izquierdo, haz clic en **Usuarios** (*Users*) y luego en **Crear usuario** (*Create user*).
3. **Paso 1:** Asigna un nombre de usuario (ejemplo: `developer-local-s3`) y haz clic en **Siguiente** (no selecciones acceso a la consola de administración).
4. **Paso 2:** En opciones de permisos, selecciona **Adjuntar directivas directamente** (*Attach policies directly*).
5. En la lista de directivas, busca y marca la casilla de:
   - `AmazonS3FullAccess`
6. Haz clic en **Siguiente** y luego en **Crear usuario**.
7. **Obtener las Claves:**
   - Haz clic sobre el usuario que acabas de crear (`developer-local-s3`).
   - Ve a la pestaña **Credenciales de seguridad** (*Security credentials*).
   - Desplázate hacia abajo hasta la sección **Claves de acceso** (*Access keys*) y haz clic en **Crear clave de acceso** (*Create access key*).
   - Selecciona el caso de uso: **Código local** (*Local code*), marca la casilla de confirmación y haz clic en **Siguiente**.
   - Haz clic en **Crear clave de acceso**.
8. **¡IMPORTANTE!** Verás dos valores en pantalla:
   - **Access Key ID:** Una cadena que empieza por `AKIA...`
   - **Secret Access Key:** Una clave secreta larga.
   - Copia ambos valores inmediatamente y pégalos en tu archivo `.env`:
     ```env
     AWS_ACCESS_KEY_ID="AKIA..."
     AWS_SECRET_ACCESS_KEY="tu_clave_secreta"
     S3_BUCKET_NAME="tu-nombre-de-bucket-dev"
     ```

---

## 4. Cómo Levantar la API y la Base de Datos con Docker

Con Docker Desktop abierto, abre tu terminal en la raíz del proyecto y ejecuta:

```bash
docker compose up --build
```

### ¿Qué hace este comando?
1. Descarga la imagen oficial de PostgreSQL 16 y levanta el contenedor `inventory_postgres`.
2. Espera a que el healthcheck confirme que PostgreSQL está listo (`pg_isready`).
3. Construye la imagen de la API usando el [Dockerfile](file:///Users/sebastiancorvalan/Documents/PROGRAMACION/Portafolio/inventary-cloud-api/Dockerfile) multi-stage y arranca el contenedor `inventory_api`.
4. Mapea el puerto local `8000` y activa el **hot-reload** (cualquier cambio en el código se actualiza al instante).

Verifica que el sistema esté funcionando abriendo en tu navegador:
- **Healthcheck:** [http://localhost:8000/health](http://localhost:8000/health) (debe responder `{"status":"healthy",...}`)
- **Documentación Interactiva (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 5. Ejecutar Migraciones de Base de Datos (Alembic)

Para asegurar que las tablas `users` y `products` estén creadas en PostgreSQL con sus relaciones, abre otra pestaña de terminal y corre:

```bash
docker compose exec api alembic upgrade head
```

Verás una salida confirmando que las revisiones de base de datos se aplicaron exitosamente.

---

## 6. Flujo Práctico: CRUD de Usuarios y Productos

La forma más cómoda y visual de probar todo es a través de **Swagger UI**: abre [http://localhost:8000/docs](http://localhost:8000/docs) en tu navegador.

```
          ┌─────────────────────────────────────────────────────────┐
          │                   FLUJO GENERAL                         │
          │                                                         │
          │  1. POST /auth/register ──> Crea el usuario en Postgres │
          │  2. POST /auth/login    ──> Genera Token JWT            │
          │  3. Authorize (Candado) ──> Inyecta 'Bearer <token>'    │
          │  4. POST /products      ──> Crea producto en Postgres   │
          │                             + Emite evento SQS          │
          │  5. POST /products/{id}/image ──> Sube a AWS S3 real    │
          └─────────────────────────────────────────────────────────┘
```

---

### Paso 1: Registro de Usuario
1. En Swagger, despliega la sección **Autenticación** y busca `POST /auth/register`.
2. Haz clic en **Try it out**.
3. En el cuerpo del JSON, ingresa tus datos:
   ```json
   {
     "email": "juan.perez@example.com",
     "username": "juanperez",
     "password": "PasswordSeguro123!"
   }
   ```
4. Haz clic en **Execute**.
5. **Respuesta esperada:** Código `201 Created` con el ID generado y la fecha de creación (la contraseña queda hasheada con bcrypt).

---

### Paso 2: Inicio de Sesión y Token JWT
1. En Swagger, busca `POST /auth/login`.
2. Haz clic en **Try it out**.
3. Ingresa los datos:
   - `username`: `juan.perez@example.com` (Nota: ingresa el email en el campo username).
   - `password`: `PasswordSeguro123!`
4. Haz clic en **Execute**.
5. **Respuesta esperada:** Código `200 OK` retornando un objeto:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
     "token_type": "bearer"
   }
   ```
6. **Copia el valor del `access_token`** (sin comillas).

---

### Paso 3: Autenticación en Swagger UI
1. Sube al inicio de la página de Swagger y haz clic en el botón verde con forma de candado: **Authorize**.
2. En el campo **Value**, pega el token que acabas de copiar.
3. Haz clic en **Authorize** y luego en **Close**.
4. A partir de este momento, todos los endpoints protegidos enviarán automáticamente el encabezado `Authorization: Bearer <token>`.

---

### Paso 4: Crear un Producto
1. Despliega la sección **Productos** y busca `POST /products`.
2. Haz clic en **Try it out**.
3. En el cuerpo del JSON, ingresa:
   ```json
   {
     "title": "Teclado Mecánico RGB",
     "description": "Switch Brown con conexión inalámbrica",
     "price": 89.99,
     "stock": 15
   }
   ```
4. Haz clic en **Execute**.
5. **Respuesta esperada:** Código `201 Created` con los datos del producto y su nuevo `id` (por ejemplo, `id: 1`).
6. *En segundo plano:* La API guarda en PostgreSQL y emite el evento `PRODUCT_CREATED` a SQS sin bloquear la respuesta.

---

### Paso 5: Subir Imagen a AWS S3
1. En la sección **Productos**, busca `POST /products/{product_id}/image`.
2. Haz clic en **Try it out**.
3. En `product_id`, ingresa el ID del producto que creaste (ej. `1`).
4. En el campo `file`, haz clic en **Seleccionar archivo** y elige cualquier imagen (`.jpg`, `.png` o `.webp`) desde tu computadora.
5. Haz clic en **Execute**.
6. **Respuesta esperada:** Código `200 OK`. 
   - El campo `image_url` ahora contiene la URL real en AWS:
     ```text
     https://tu-nombre-de-bucket-dev.s3.us-east-1.amazonaws.com/products/4f8a9b2c3d4e5f6a.jpg
     ```
7. Abre esa URL en una pestaña nueva de tu navegador o ve a la consola de AWS S3 para ver tu imagen guardada en la nube.

---

### Paso 6: Consultar, Actualizar y Eliminar Productos

- **Listar productos (GET /products):**
  - Permite paginar con `skip=0` y `limit=20`. Retorna todos los productos del catálogo con sus imágenes.
- **Obtener por ID (GET /products/{product_id}):**
  - Consulta un producto específico por su identificador numérico.
- **Actualizar producto (PUT /products/{product_id}):**
  - Permite modificar título, descripción, precio o stock.
  - *Detalle pro:* Si actualizas el stock a `5` unidades o menos, la API emite automáticamente una alerta `LOW_STOCK_ALERT` a SQS.
  - *Seguridad:* Si intentas actualizar un producto de otro usuario, el sistema responderá `403 Forbidden`.
- **Eliminar producto (DELETE /products/{product_id}):**
  - Elimina el registro en PostgreSQL y **borra físicamente el archivo en Amazon S3** en segundo plano para no acumular costos innecesarios.

---

## 7. Cómo Detener los Servicios

Para detener los contenedores y liberar los puertos cuando termines de trabajar:

```bash
# Detener los contenedores preservando los datos de PostgreSQL
docker compose down

# (Opcional) Detener y eliminar volúmenes de datos si quieres reiniciar la DB desde cero
docker compose down -v
```
