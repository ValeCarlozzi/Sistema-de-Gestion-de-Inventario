-- Migration: Agregar columna stock_minimo a la tabla productos
-- Fecha: 2026-05-14
-- Descripción: Agrega el campo stock_minimo para alertas de stock bajo

-- Agregar columna stock_minimo si no existe
ALTER TABLE productos
ADD COLUMN IF NOT EXISTS stock_minimo INTEGER NOT NULL DEFAULT 10;

-- Agregar constraint de validación
ALTER TABLE productos
ADD CONSTRAINT chk_stock_minimo_positivo 
CHECK (stock_minimo >= 0);
