from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter(prefix="/products", tags=["Productos"])

@router.get("", response_model=list[ProductResponse])
def list_products(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """Lista los productos disponibles con paginacion"""
    return db.query(Product).offset(skip).limit(limit).all()
    
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Obtiene un producto por su ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return product

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crea un nuevo producto, asociado a un usuario"""
    product = Product(
        **product_in.model_dump(),
        owner_id = current_user.id,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
    
@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza un producto existente"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Producto no encontrado",
        )
    if product.owner_id != current_user.id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "No tienes permiso para actualizar este producto",
        )

    update_data = product_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
  """Elimina un producto (solo el propietario puede eliminarlo)."""
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

  db.delete(product)
  db.commit()
  return None