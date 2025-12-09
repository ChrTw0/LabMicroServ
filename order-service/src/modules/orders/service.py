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

        # Calculate new balance after payments
        new_balance = balance - new_payments_total

        # Auto-update order status when fully paid
        if new_balance <= 0 and order.status == OrderStatus.REGISTRADA:
            # If order was just registered and now is fully paid, move to EN_PROCESO
            order.status = OrderStatus.EN_PROCESO
            await OrderRepository.update(db, order)

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

    # ==================== REPORTING METHODS ====================

    @staticmethod
    async def get_payment_method_report(
        db: AsyncSession,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        location_id: Optional[int] = None
    ) -> List:
        """Get sales report by payment method - RF-077"""
        from src.modules.orders.schemas import PaymentMethodStats
        from src.modules.orders.models import OrderPayment
        from sqlalchemy import func, select
        from decimal import Decimal

        # Build query
        query = select(
            OrderPayment.payment_method,
            func.sum(OrderPayment.amount).label('total_amount'),
            func.count(OrderPayment.id).label('count')
        ).join(Order).where(Order.status != OrderStatus.ANULADA)

        if date_from:
            query = query.where(Order.created_at >= date_from)
        if date_to:
            query = query.where(Order.created_at <= date_to)
        if location_id:
            query = query.where(Order.location_id == location_id)

        query = query.group_by(OrderPayment.payment_method)

        result = await db.execute(query)
        rows = result.all()

        # Calculate total and percentages
        grand_total = sum(row.total_amount for row in rows) if rows else Decimal(0)

        stats = []
        for row in rows:
            percentage = float((row.total_amount / grand_total * 100)) if grand_total > 0 else 0.0
            stats.append(PaymentMethodStats(
                payment_method=row.payment_method,
                total_amount=row.total_amount,
                count=row.count,
                percentage=round(percentage, 2)
            ))

        return stats

    @staticmethod
    async def get_top_services_report(
        db: AsyncSession,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        location_id: Optional[int] = None,
        limit: int = 10
    ) -> List:
        """Get top requested services report - RF-076"""
        from src.modules.orders.schemas import ServiceStats
        from src.modules.orders.models import OrderItem
        from sqlalchemy import func, select
        from decimal import Decimal

        # Build query
        query = select(
            OrderItem.service_id,
            OrderItem.service_name,
            func.sum(OrderItem.quantity).label('quantity_sold'),
            func.sum(OrderItem.subtotal).label('total_revenue')
        ).join(Order).where(Order.status != OrderStatus.ANULADA)

        if date_from:
            query = query.where(Order.created_at >= date_from)
        if date_to:
            query = query.where(Order.created_at <= date_to)
        if location_id:
            query = query.where(Order.location_id == location_id)

        query = query.group_by(OrderItem.service_id, OrderItem.service_name)
        query = query.order_by(func.sum(OrderItem.quantity).desc())
        query = query.limit(limit)

        result = await db.execute(query)
        rows = result.all()

        # Calculate total revenue for percentage
        grand_total = sum(row.total_revenue for row in rows) if rows else Decimal(0)

        stats = []
        for row in rows:
            percentage = float((row.total_revenue / grand_total * 100)) if grand_total > 0 else 0.0
            stats.append(ServiceStats(
                service_id=row.service_id,
                service_name=row.service_name,
                quantity_sold=row.quantity_sold,
                total_revenue=row.total_revenue,
                percentage=round(percentage, 2)
            ))

        return stats

    @staticmethod
    async def get_monthly_revenue_report(
        db: AsyncSession,
        months: int = 12,
        location_id: Optional[int] = None
    ) -> List:
        """Get monthly revenue comparison - RF-079"""
        from src.modules.orders.schemas import MonthlyRevenueStats
        from sqlalchemy import func, select, extract
        from datetime import datetime, timedelta
        from decimal import Decimal

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30 * months)

        # Build query - usar literal_column para evitar problemas con PostgreSQL
        from sqlalchemy import literal_column

        month_expr = func.to_char(Order.created_at, 'YYYY-MM')

        query = select(
            month_expr.label('month'),
            func.sum(Order.total).label('total_revenue'),
            func.count(Order.id).label('total_orders')
        ).where(
            Order.status != OrderStatus.ANULADA,
            Order.created_at >= start_date
        )

        if location_id:
            query = query.where(Order.location_id == location_id)

        query = query.group_by(literal_column('month'))
        query = query.order_by(literal_column('month'))

        result = await db.execute(query)
        rows = result.all()

        stats = []
        for row in rows:
            avg_value = row.total_revenue / row.total_orders if row.total_orders > 0 else Decimal(0)
            stats.append(MonthlyRevenueStats(
                month=row.month,
                total_revenue=row.total_revenue,
                total_orders=row.total_orders,
                avg_order_value=avg_value
            ))

        return stats

    @staticmethod
    async def get_patient_types_report(
        db: AsyncSession,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        location_id: Optional[int] = None
    ) -> dict:
        """Get new vs recurring patients report - RF-078"""
        from src.modules.orders.schemas import PatientTypeStats
        from sqlalchemy import func, select

        # Build base query
        base_query = select(Order.patient_id, func.count(Order.id).label('order_count'))
        base_query = base_query.where(Order.status != OrderStatus.ANULADA)

        if date_from:
            base_query = base_query.where(Order.created_at >= date_from)
        if date_to:
            base_query = base_query.where(Order.created_at <= date_to)
        if location_id:
            base_query = base_query.where(Order.location_id == location_id)

        base_query = base_query.group_by(Order.patient_id)

        # Execute query
        result = await db.execute(base_query)
        patient_orders = result.all()

        # Count new vs recurring
        new_patients = sum(1 for p in patient_orders if p.order_count == 1)
        recurring_patients = sum(1 for p in patient_orders if p.order_count > 1)
        total_patients = len(patient_orders)

        new_percentage = (new_patients / total_patients * 100) if total_patients > 0 else 0.0
        recurring_percentage = (recurring_patients / total_patients * 100) if total_patients > 0 else 0.0

        return PatientTypeStats(
            new_patients=new_patients,
            recurring_patients=recurring_patients,
            total_patients=total_patients,
            new_percentage=round(new_percentage, 2),
            recurring_percentage=round(recurring_percentage, 2)
        )
