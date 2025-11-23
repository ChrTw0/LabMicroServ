"""
Order Service (Business logic)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional, List, Dict
from datetime import date
from decimal import Decimal

from src.modules.orders.models import Order, OrderItem, OrderPayment, OrderStatus
from src.modules.orders.repository import OrderRepository, OrderItemRepository, OrderPaymentRepository
from src.modules.catalog.repository import ServiceRepository
from src.modules.orders.schemas import (
    OrderCreate, OrderUpdate, OrderUpdateStatus, OrderAddPayment,
    OrderResponse, OrderDetailResponse, OrderListResponse,
    OrderItemResponse, OrderPaymentResponse, OrderStats
)


class OrderService:
    """Business logic for Order operations"""

    @staticmethod
    async def get_all_orders(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 50,
        search: Optional[str] = None,
        patient_id: Optional[int] = None,
        location_id: Optional[int] = None,
        status: Optional[OrderStatus] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> OrderListResponse:
        """Get all orders with filters and pagination"""
        orders, total = await OrderRepository.get_all(
            db, page, page_size, search, patient_id, location_id, status, date_from, date_to
        )

        order_responses = [OrderResponse.model_validate(o) for o in orders]

        return OrderListResponse(
            total=total,
            page=page,
            page_size=page_size,
            orders=order_responses
        )

    @staticmethod
    async def get_order_by_id(db: AsyncSession, order_id: int) -> OrderDetailResponse:
        """Get order by ID with details"""
        order = await OrderRepository.get_by_id_with_details(db, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orden con ID {order_id} no encontrada"
            )

        # Calculate total paid and balance
        total_paid = sum(payment.amount for payment in order.payments)
        balance = order.total - total_paid

        # Convert to response
        order_dict = {
            "id": order.id,
            "order_number": order.order_number,
            "patient_id": order.patient_id,
            "location_id": order.location_id,
            "status": order.status,
            "total": order.total,
            "created_at": order.created_at,
            "items": [OrderItemResponse.model_validate(item) for item in order.items],
            "payments": [OrderPaymentResponse.model_validate(payment) for payment in order.payments],
            "total_paid": total_paid,
            "balance": balance
        }
        return OrderDetailResponse(**order_dict)

    @staticmethod
    async def get_order_by_number(db: AsyncSession, order_number: str) -> OrderDetailResponse:
        """Get order by order number"""
        order = await OrderRepository.get_by_order_number(db, order_number)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orden {order_number} no encontrada"
            )

        # Reload with details
        order = await OrderRepository.get_by_id_with_details(db, order.id)

        # Calculate total paid and balance
        total_paid = sum(payment.amount for payment in order.payments)
        balance = order.total - total_paid

        order_dict = {
            "id": order.id,
            "order_number": order.order_number,
            "patient_id": order.patient_id,
            "location_id": order.location_id,
            "status": order.status,
            "total": order.total,
            "created_at": order.created_at,
            "items": [OrderItemResponse.model_validate(item) for item in order.items],
            "payments": [OrderPaymentResponse.model_validate(payment) for payment in order.payments],
            "total_paid": total_paid,
            "balance": balance
        }
        return OrderDetailResponse(**order_dict)

    @staticmethod
    async def create_order(
        db: AsyncSession,
        data: OrderCreate
    ) -> OrderDetailResponse:
        """Create a new order"""
        # Validate all services exist and get their prices
        items_data = []
        total = Decimal("0.00")

        for item_create in data.items:
            service = await ServiceRepository.get_by_id(db, item_create.service_id)
            if not service:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Servicio con ID {item_create.service_id} no encontrado"
                )

            if not service.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El servicio '{service.name}' no está activo"
                )

            subtotal = service.current_price * item_create.quantity
            total += subtotal

            items_data.append({
                "service_id": service.id,
                "service_name": service.name,
                "unit_price": service.current_price,
                "quantity": item_create.quantity,
                "subtotal": subtotal
            })

        # Generate order number
        order_number = await OrderRepository.generate_order_number(db)

        # Create order
        order = Order(
            order_number=order_number,
            patient_id=data.patient_id,
            location_id=data.location_id,
            status=OrderStatus.REGISTRADA,
            total=total
        )
        order = await OrderRepository.create(db, order)

        # Create order items
        order_items = [
            OrderItem(order_id=order.id, **item_data)
            for item_data in items_data
        ]
        await OrderItemRepository.create_many(db, order_items)
        await db.commit()

        # Reload order with details
        return await OrderService.get_order_by_id(db, order.id)

    @staticmethod
    async def update_order(
        db: AsyncSession,
        order_id: int,
        data: OrderUpdate
    ) -> OrderResponse:
        """Update order (only location)"""
        order = await OrderRepository.get_by_id(db, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orden con ID {order_id} no encontrada"
            )

        # Can't update if order is completed or cancelled
        if order.status in [OrderStatus.COMPLETADA, OrderStatus.ANULADA]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede modificar una orden con estado {order.status.value}"
            )

        # Update location
        if data.location_id is not None:
            order.location_id = data.location_id

        order = await OrderRepository.update(db, order)
        return OrderResponse.model_validate(order)

    @staticmethod
    async def update_order_status(
        db: AsyncSession,
        order_id: int,
        data: OrderUpdateStatus
    ) -> OrderResponse:
        """Update order status"""
        order = await OrderRepository.get_by_id(db, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orden con ID {order_id} no encontrada"
            )

        # Validate status transitions
        if order.status == OrderStatus.ANULADA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede cambiar el estado de una orden anulada"
            )

        if order.status == OrderStatus.COMPLETADA and data.status != OrderStatus.ANULADA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Una orden completada solo puede ser anulada"
            )

        order.status = data.status
        order = await OrderRepository.update(db, order)
        return OrderResponse.model_validate(order)

    @staticmethod
    async def add_payment_to_order(
        db: AsyncSession,
        order_id: int,
        data: OrderAddPayment
    ) -> OrderDetailResponse:
        """Add payment(s) to order"""
        order = await OrderRepository.get_by_id_with_details(db, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orden con ID {order_id} no encontrada"
            )

        # Can't add payment to cancelled order
        if order.status == OrderStatus.ANULADA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede agregar pagos a una orden anulada"
            )

        # Calculate current balance
        total_paid = sum(payment.amount for payment in order.payments)
        balance = order.total - total_paid

        # Calculate new payments total
        new_payments_total = sum(payment.amount for payment in data.payments)

        # Validate not overpaying
        if new_payments_total > balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El total de pagos (S/ {new_payments_total}) excede el saldo pendiente (S/ {balance})"
            )

        # Create payments
        payments = [
            OrderPayment(
                order_id=order_id,
                payment_method=payment.payment_method,
                amount=payment.amount
            )
            for payment in data.payments
        ]
        await OrderPaymentRepository.create_many(db, payments)
        await db.commit()

        # Reload order with details
        return await OrderService.get_order_by_id(db, order_id)

    @staticmethod
    async def cancel_order(db: AsyncSession, order_id: int) -> OrderResponse:
        """Cancel order"""
        order = await OrderRepository.get_by_id(db, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orden con ID {order_id} no encontrada"
            )

        if order.status == OrderStatus.ANULADA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La orden ya está anulada"
            )

        order.status = OrderStatus.ANULADA
        order = await OrderRepository.update(db, order)
        return OrderResponse.model_validate(order)

    @staticmethod
    async def get_statistics(
        db: AsyncSession,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> OrderStats:
        """Get order statistics"""
        stats = await OrderRepository.get_statistics(db, date_from, date_to)
        return OrderStats(**stats)
