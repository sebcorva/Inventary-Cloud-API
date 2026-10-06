from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.s3_service import s3_service
from app.services.sqs_service import sqs_service

router = APIRouter(prefix="/products", tags=["Productos"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE_MB = 5

@router.get("", response_model=list[ProductResponse])
def list_products(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """Lista los productos disponibles con paginación."""
    return db.query(Product).offset(skip).limit(limit).all()
    
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Obtiene un producto por su ID."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return product

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crea un nuevo producto y emite un evento asíncrono a SQS."""
    product = Product(
        **product_in.model_dump(),
        owner_id=current_user.id,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    # Publicar evento a SQS en segundo plano sin bloquear la respuesta HTTP
    background_tasks.add_task(
        sqs_service.send_event,
        event_type="PRODUCT_CREATED",
        payload={
            "product_id": product.id,
            "title": product.title,
            "price": float(product.price),
            "stock": product.stock,
            "owner_id": current_user.id,
        },
    )

    return product

@router.post("/{product_id}/image", response_model=ProductResponse)
async def upload_product_image(
    product_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Sube una imagen para un producto a AWS S3 y notifica por SQS."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    if product.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar este producto",
        )

    # Validar tipo de archivo
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato no permitido. Formatos válidos: {', '.join(ALLOWED_IMAGE_TYPES)}",
        )

    # Subir imagen a AWS S3
    image_url = s3_service.upload_file(
        file_obj=file.file,
        filename=file.filename or "product_image.jpg",
        content_type=file.content_type,
        folder="products",
    )

    # Actualizar URL en la base de datos
    product.image_url = image_url
    db.commit()
    db.refresh(product)

    # Enviar evento asíncrono a SQS para procesamiento/redimensionamiento
    background_tasks.add_task(
        sqs_service.send_event,
        event_type="PRODUCT_IMAGE_UPLOADED",
        payload={
            "product_id": product.id,
            "image_url": image_url,
            "owner_id": current_user.id,
        },
    )

    return product
    
@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza un producto existente y notifica cambios de stock vía SQS."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    if product.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este producto",
        )

    update_data = product_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    # Si el stock bajó de 5 unidades, emitir alerta de stock bajo
    if product.stock <= 5:
        background_tasks.add_task(
            sqs_service.send_event,
            event_type="LOW_STOCK_ALERT",
            payload={
                "product_id": product.id,
                "title": product.title,
                "current_stock": product.stock,
                "owner_id": current_user.id,
            },
        )

    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina un producto y remueve su imagen asociada en S3."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    if product.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar este producto",
        )

    # Limpiar imagen de S3 si existía
    if product.image_url:
        background_tasks.add_task(s3_service.delete_file_by_url, product.image_url)

    db.delete(product)
    db.commit()
    return None