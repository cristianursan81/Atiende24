# Documento 06 — Modelo de Datos

Tablas principales del sistema.

## usuarios

- id
- email
- password_hash
- created_at

## negocios

- id
- nombre
- sector
- owner_id

## conversaciones

- id
- negocio_id
- cliente_id
- created_at

## mensajes

- id
- conversacion_id
- role
- content
- timestamp

## leads

- id
- nombre
- telefono
- email
- negocio_id