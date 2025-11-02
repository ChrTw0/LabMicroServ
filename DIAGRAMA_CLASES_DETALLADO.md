# 📐 Diagrama de Clases Detallado - Sistema de Laboratorio Clínico

**Versión:** 2.0 (Arquitectura Optimizada - 6 DBs)
**Fecha:** 2025-10-31

---

## 📚 Índice

1. [user_db - User Service](#1-user_db---user-service)
2. [patient_db - Patient Service](#2-patient_db---patient-service)
3. [catalog_db - Catalog Service](#3-catalog_db---catalog-service)
4. [order_db - Order Service + Lab Integration](#4-order_db---order-service--lab-integration-compartida)
5. [billing_db - Billing Service + Reconciliation](#5-billing_db---billing-service--reconciliation-compartida)
6. [config_db - Configuration Service + Notification](#6-config_db---configuration-service--notification-compartida)

---

## 1. user_db - User Service

### **Tablas:**

####