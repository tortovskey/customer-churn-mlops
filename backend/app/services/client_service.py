from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.client import Client
from app.schemas.client_schema import ClientCreate, ClientUpdate


def list_clients(db: Session) -> list[Client]:
    return list(db.scalars(select(Client).order_by(Client.id.desc())).all())


def get_client(db: Session, client_id: int) -> Client:
    client = db.get(Client, client_id)
    if client is None:
        raise NotFoundError(f"Client {client_id} was not found")
    return client


def create_client(db: Session, payload: ClientCreate) -> Client:
    client = Client(**payload.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def update_client(db: Session, client_id: int, payload: ClientUpdate) -> Client:
    client = get_client(db, client_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    db.commit()
    db.refresh(client)
    return client


def delete_client(db: Session, client_id: int) -> None:
    client = get_client(db, client_id)
    db.delete(client)
    db.commit()

