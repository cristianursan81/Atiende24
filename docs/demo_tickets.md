# Demo Tickets — Atiende24 `/copilot/analyze`

> **Contexto:** soporte interno (IT helpdesk + RRHH).  
> KB de referencia: `docs/demo_kb/` (artículos kb-001 a kb-010).  
> Los tickets están diseñados para funcionar **sin OpenAI** (modo template).

---

## ¿Cómo usar estos tickets?

Arranca el servidor:

```bash
cd backend
uvicorn app.main:app --reload
```

Lanza cualquier ticket con `curl` (o con el script al final de este archivo):

```bash
curl -s -X POST http://localhost:8000/copilot/analyze \
  -H "Content-Type: application/json" \
  -d '{"title": "<TÍTULO>", "body": "<CUERPO>"}' | python3 -m json.tool
```

Resultado esperado en el campo `decision`:
- `auto_reply` → el copiloto genera una respuesta sugerida.
- `escalate`   → el copiloto deriva el ticket a un agente humano.

---

## Grupo A — `suggest_reply` (decision: auto_reply)

> **Por qué caen aquí:** ninguno de los tickets contiene palabras clave de escalado
> (`urgente`, `urgencia`, `queja`, `reclamación`, `fraude`, `robo`, `amenaza`,
> `legal`, `abogado`, `denuncia`, `error grave`, `inaceptable`, `roto`,
> `daños`, `emergencia`, etc.) **y** el texto hace match con al menos un artículo
> de la KB, por lo que la confianza supera el umbral de 0.30.
> El copiloto puede generar una respuesta útil a partir del conocimiento disponible.

---

### T-A01 · Restablecer contraseña olvidada

```json
{
  "title": "No puedo acceder, olvidé mi contraseña",
  "body": "Hola, esta mañana intenté entrar al portal y olvidé mi contraseña. ¿Cómo puedo restablecer la contraseña y recuperar el acceso?"
}
```

**KB esperada:** kb-001  
**Por qué `suggest_reply`:** Consulta estándar de autoservicio; la KB contiene los pasos exactos para restablecer la contraseña.

---

### T-A02 · Cuenta bloqueada por intentos fallidos

```json
{
  "title": "Mi cuenta está bloqueada",
  "body": "Intenté entrar varias veces con mi contraseña y ahora la cuenta está bloqueada. ¿Cómo la desbloqueo o restablezco mi contraseña?"
}
```

**KB esperada:** kb-001  
**Por qué `suggest_reply`:** La KB describe el comportamiento de bloqueo y los pasos para resolverlo sin intervención humana.

---

### T-A03 · Problemas para conectar la VPN desde casa

```json
{
  "title": "VPN no conecta en teletrabajo",
  "body": "Estoy trabajando desde casa y GlobalProtect no consigue conectarse al servidor VPN. Me sale un error de certificado."
}
```

**KB esperada:** kb-002  
**Por qué `suggest_reply`:** La KB cubre exactamente el error de certificado en VPN con pasos de resolución concretos.

---

### T-A04 · Dónde descargar el cliente VPN

```json
{
  "title": null,
  "body": "Acabo de recibir mi portátil nuevo y necesito instalar la VPN corporativa. ¿Dónde la descargo?"
}
```

**KB esperada:** kb-002  
**Por qué `suggest_reply`:** Pregunta de onboarding frecuente; la KB indica la URL de descarga y los pasos de instalación.

---

### T-A05 · Solicitar un monitor adicional

```json
{
  "title": "Quiero solicitar un monitor para mi puesto",
  "body": "Necesito un monitor adicional para trabajar más cómodamente. ¿Cómo hago la solicitud de equipo o accesorio?"
}
```

**KB esperada:** kb-003  
**Por qué `suggest_reply`:** La KB explica el portal de solicitud de hardware y la sección de accesorios paso a paso.

---

### T-A06 · Cuántos días de vacaciones me quedan

```json
{
  "title": "Saldo de días de vacaciones",
  "body": "¿Dónde puedo ver cuántos días de vacaciones me quedan disponibles este año?"
}
```

**KB esperada:** kb-004  
**Por qué `suggest_reply`:** Pregunta FAQ de RRHH; la KB indica exactamente la sección del portal donde consultar el saldo vacacional.

---

### T-A07 · Cómo pedir días de vacaciones

```json
{
  "title": "Proceso para solicitar vacaciones",
  "body": "Quiero coger una semana de vacaciones el mes que viene. ¿Cuál es el proceso para solicitarlas y que las apruebe mi manager?"
}
```

**KB esperada:** kb-004  
**Por qué `suggest_reply`:** Solicitud de proceso estándar bien cubierta en la KB con pasos numerados.

---

### T-A08 · Cómo pedir reembolso de un taxi de trabajo

```json
{
  "title": "Reembolso taxi cliente",
  "body": "Tomé un taxi para ir a una reunión con un cliente y pagué 25 euros. ¿Cómo solicito el reembolso del gasto y subo el justificante?"
}
```

**KB esperada:** kb-005  
**Por qué `suggest_reply`:** Gasto dentro del límite estándar de taxi (30 €); la KB detalla el proceso de subida de justificantes y plazos.

---

### T-A09 · Instalar Visual Studio Code

```json
{
  "title": "Quiero instalar VS Code",
  "body": "Necesito instalar Visual Studio Code en mi equipo para desarrollar. ¿Tengo que abrir alguna solicitud o puedo instalarlo directamente?"
}
```

**KB esperada:** kb-006  
**Por qué `suggest_reply`:** VS Code está en el catálogo estándar; la KB indica que se puede instalar sin solicitud adicional.

---

### T-A10 · La impresora de mi planta no imprime

```json
{
  "title": "Impresora planta 2 sin respuesta",
  "body": "La impresora Canon de la segunda planta no responde. He mandado varios documentos a imprimir y no sale nada."
}
```

**KB esperada:** kb-007  
**Por qué `suggest_reply`:** Incidencia de impresora estándar; la KB incluye los pasos de diagnóstico básico (reinicio) antes de escalar.

---

### T-A11 · Reservar sala de reuniones para 8 personas

```json
{
  "title": "Reserva sala para mañana",
  "body": "Necesito reservar una sala para 8 personas mañana por la mañana. ¿Cómo hago la reserva y qué salas hay disponibles?"
}
```

**KB esperada:** kb-008  
**Por qué `suggest_reply`:** Proceso de reserva de sala cubierto completamente en la KB con instrucciones para Outlook/Teams.

---

### T-A12 · Cómo reportar un correo de phishing

```json
{
  "title": "Correo sospechoso recibido",
  "body": "He recibido un correo que parece phishing pidiendo mis credenciales. ¿A quién lo reenvío para reportarlo?"
}
```

**KB esperada:** kb-009  
**Por qué `suggest_reply`:** La KB especifica exactamente la dirección de reporte (`seguridad@empresa.com`) y el procedimiento; no hay señal de incidente activo ni urgencia extrema.

---

## Grupo B — `escalate` (decision: escalate)

> **Por qué caen aquí:** cada ticket contiene al menos una palabra o expresión de la
> lista de escalado (`urgente`, `urgencia`, `queja`, `reclamación`, `fraude`,
> `robo`, `amenaza`, `legal`, `abogado`, `denuncia`, `error grave`, `inaceptable`,
> `emergencia`, `daños`, `roto`, `destrozado`, etc.) **o** el contenido es tan
> específico/complejo que no hay match suficiente en la KB y la confianza cae
> por debajo del umbral de 0.30, haciendo imposible una respuesta automática fiable.

---

### T-B01 · Portátil robado en la oficina

```json
{
  "title": "Me han robado el portátil",
  "body": "Esta mañana llegué a la oficina y mi portátil no estaba en mi mesa. Creo que me lo han robado. ¿Qué hago ahora?"
}
```

**Señal de escalado:** `robado` / `robo`  
**Por qué `escalate`:** Posible incidente de seguridad y pérdida de activo corporativo; requiere intervención de Seguridad TI y RRHH.

---

### T-B02 · Solicitud de nómina incorrecta — posible fraude

```json
{
  "title": "Cobro incorrecto en nómina de este mes",
  "body": "Este mes me han pagado menos de lo que corresponde según mi contrato. Parece un fraude o un error grave en la nómina. Necesito que lo revisen urgentemente."
}
```

**Señal de escalado:** `fraude`, `error grave`, `urgentemente`  
**Por qué `escalate`:** Afecta a datos salariales confidenciales; requiere revisión por RRHH y posiblemente Finanzas.

---

### T-B03 · Accidente en las instalaciones

```json
{
  "title": "Accidente en la oficina",
  "body": "Un compañero ha tenido un accidente en la escalera y necesita atención médica. Es una emergencia."
}
```

**Señal de escalado:** `accidente`, `emergencia`  
**Por qué `escalate`:** Emergencia sanitaria; debe activarse el protocolo de primeros auxilios y PRL (Prevención de Riesgos Laborales).

---

### T-B04 · Amenaza de acción legal por parte de un empleado

```json
{
  "title": "Aviso legal de empleado",
  "body": "Un empleado del equipo me ha enviado un mensaje amenazando con llevar la situación a los tribunales. ¿Qué debo hacer? Necesito asesoramiento legal."
}
```

**Señal de escalado:** `amenaza`, `legal`, `tribunales`  
**Por qué `escalate`:** Implica asesoramiento jurídico y posibles implicaciones disciplinarias; no es resoluble con la KB actual.

---

### T-B05 · Denuncia por acoso laboral

```json
{
  "title": "Quiero presentar una denuncia por acoso",
  "body": "He sido víctima de acoso laboral por parte de un superior. Quiero presentar una denuncia formal y necesito saber cómo proceder."
}
```

**Señal de escalado:** `denuncia`, `acoso`  
**Por qué `escalate`:** Requiere intervención del Comité de Ética o RRHH senior; proceso confidencial y regulado.

---

### T-B06 · Datos personales expuestos — posible brecha de seguridad

```json
{
  "title": "Posible fuga de datos",
  "body": "He recibido un correo externo que contiene información confidencial de nuestra empresa. Creo que hay una brecha de seguridad grave. Es urgente."
}
```

**Señal de escalado:** `urgente`, `brecha`  
**Por qué `escalate`:** Posible incidente de ciberseguridad que debe atenderse en menos de 1 hora según la política interna (kb-009); el copiloto no puede resolverlo.

---

### T-B07 · Queja formal contra un proveedor

```json
{
  "title": "Queja formal — proveedor no cumple contrato",
  "body": "El proveedor de servicios cloud lleva tres semanas sin cumplir los niveles de servicio acordados. Quiero formalizar una queja y estudiar acciones legales."
}
```

**Señal de escalado:** `queja`, `acciones legales`  
**Por qué `escalate`:** Requiere revisión del contrato y posiblemente al departamento jurídico; fuera del alcance de la KB de soporte interno.

---

### T-B08 · Portátil con daños físicos graves

```json
{
  "title": "Portátil destrozado tras caída",
  "body": "Se me cayó el portátil y la pantalla quedó destrozada, el teclado no funciona y hay daños en la carcasa. No puedo trabajar."
}
```

**Señal de escalado:** `destrozado`, `daños`  
**Por qué `escalate`:** Daño físico grave en activo corporativo; requiere evaluación del técnico de hardware y posible proceso de responsabilidad.

---

### T-B09 · Empleado que no recibe nómina — amenaza con abogado

```json
{
  "title": "Llevo dos meses sin cobrar",
  "body": "Llevo dos meses sin recibir mi nómina y nadie me da respuesta desde RRHH. Si esto no se soluciona hoy, hablaré con mi abogado."
}
```

**Señal de escalado:** `abogado`  
**Por qué `escalate`:** Impago de nómina con implicaciones legales inminentes; requiere actuación inmediata de RRHH y Finanzas.

---

### T-B10 · Incumplimiento grave de política de seguridad

```json
{
  "title": "Compañero compartiendo contraseñas",
  "body": "He descubierto que un compañero está compartiendo sus credenciales corporativas con personas externas. Es un incumplimiento inaceptable de la política de seguridad."
}
```

**Señal de escalado:** `inaceptable`, `incumplimiento`  
**Por qué `escalate`:** Posible brecha de seguridad activa; debe investigarse por el equipo de seguridad TI con carácter urgente.

---

### T-B11 · Reclamación de horas extra no pagadas

```json
{
  "title": "Reclamación horas extra",
  "body": "Trabajé 40 horas extra el mes pasado y no me las han compensado ni en dinero ni en días libres. Quiero presentar una reclamación formal."
}
```

**Señal de escalado:** `reclamación`  
**Por qué `escalate`:** Reclamación laboral que requiere revisión del registro horario y aplicación del convenio; fuera del alcance de la KB de soporte.

---

### T-B12 · Situación con lesión en el trabajo

```json
{
  "title": "Lesión trabajando en almacén",
  "body": "Un compañero del almacén tiene una lesión en la muñeca después de cargar cajas. Necesitamos ayuda."
}
```

**Señal de escalado:** `lesión`  
**Por qué `escalate`:** Lesión laboral que activa el protocolo de PRL y puede requerir parte de accidente de trabajo.

---

## Script de prueba rápida (bash)

Guarda como `/tmp/test_tickets.sh` y dale permisos de ejecución:

```bash
#!/bin/bash
BASE="http://localhost:8000/copilot/analyze"

run_ticket() {
  local id="$1"
  local title="$2"
  local body="$3"
  local expected="$4"

  result=$(curl -s -X POST "$BASE" \
    -H "Content-Type: application/json" \
    -d "{\"title\": $(echo "$title" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read().strip()))'), \"body\": $(echo "$body" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read().strip()))')}")

  decision=$(echo "$result" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("decision","ERROR"))' 2>/dev/null)
  status="OK"
  [[ "$decision" != "$expected" ]] && status="FAIL (got: $decision, expected: $expected)"
  echo "[$id] $status"
}

# Grupo A — suggest_reply (auto_reply)
run_ticket "T-A01" "No puedo acceder, olvidé mi contraseña" "Hola, esta mañana intenté entrar al portal y olvidé mi contraseña. ¿Cómo puedo restablecer la contraseña y recuperar el acceso?" "auto_reply"
run_ticket "T-A02" "Mi cuenta está bloqueada" "Intenté entrar varias veces con mi contraseña y ahora la cuenta está bloqueada. ¿Cómo la desbloqueo o restablezco mi contraseña?" "auto_reply"
run_ticket "T-A03" "VPN no conecta en teletrabajo" "Estoy trabajando desde casa y GlobalProtect no consigue conectarse al servidor VPN. Me sale un error de certificado." "auto_reply"
run_ticket "T-A04" "" "Acabo de recibir mi portátil nuevo y necesito instalar la VPN corporativa. ¿Dónde la descargo?" "auto_reply"
run_ticket "T-A05" "Quiero solicitar un monitor para mi puesto" "Necesito un monitor adicional para trabajar más cómodamente. ¿Cómo hago la solicitud de equipo o accesorio?" "auto_reply"
run_ticket "T-A06" "Saldo de días de vacaciones" "¿Dónde puedo ver cuántos días de vacaciones me quedan disponibles este año?" "auto_reply"
run_ticket "T-A07" "Proceso para solicitar vacaciones" "Quiero coger una semana de vacaciones el mes que viene. ¿Cuál es el proceso para solicitarlas y que las apruebe mi manager?" "auto_reply"
run_ticket "T-A08" "Reembolso taxi cliente" "Tomé un taxi para ir a una reunión con un cliente y pagué 25 euros. ¿Cómo solicito el reembolso del gasto y subo el justificante?" "auto_reply"
run_ticket "T-A09" "Quiero instalar VS Code" "Necesito instalar Visual Studio Code en mi equipo para desarrollar. ¿Tengo que abrir alguna solicitud o puedo instalarlo directamente?" "auto_reply"
run_ticket "T-A10" "Impresora planta 2 sin respuesta" "La impresora Canon de la segunda planta no responde. He mandado varios documentos a imprimir y no sale nada." "auto_reply"
run_ticket "T-A11" "Reserva sala para mañana" "Necesito reservar una sala para 8 personas mañana por la mañana. ¿Cómo hago la reserva y qué salas hay disponibles?" "auto_reply"
run_ticket "T-A12" "Correo sospechoso recibido" "He recibido un correo que parece phishing pidiendo mis credenciales. ¿A quién lo reenvío para reportarlo?" "auto_reply"

# Grupo B — escalate
run_ticket "T-B01" "Me han robado el portátil" "Esta mañana llegué a la oficina y mi portátil no estaba en mi mesa. Creo que me lo han robado. ¿Qué hago ahora?" "escalate"
run_ticket "T-B02" "Cobro incorrecto en nómina" "Este mes me han pagado menos de lo que corresponde según mi contrato. Parece un fraude o un error grave en la nómina. Necesito que lo revisen urgentemente." "escalate"
run_ticket "T-B03" "Accidente en la oficina" "Un compañero ha tenido un accidente en la escalera y necesita atención médica. Es una emergencia." "escalate"
run_ticket "T-B04" "Aviso legal de empleado" "Un empleado del equipo me ha enviado un mensaje amenazando con llevar la situación a los tribunales. ¿Qué debo hacer? Necesito asesoramiento legal." "escalate"
run_ticket "T-B05" "Quiero presentar una denuncia por acoso" "He sido víctima de acoso laboral por parte de un superior. Quiero presentar una denuncia formal y necesito saber cómo proceder." "escalate"
run_ticket "T-B06" "Posible fuga de datos" "He recibido un correo externo que contiene información confidencial de nuestra empresa. Creo que hay una brecha de seguridad grave. Es urgente." "escalate"
run_ticket "T-B07" "Queja formal — proveedor no cumple contrato" "El proveedor de servicios cloud lleva tres semanas sin cumplir los niveles de servicio acordados. Quiero formalizar una queja y estudiar acciones legales." "escalate"
run_ticket "T-B08" "Portátil destrozado tras caída" "Se me cayó el portátil y la pantalla quedó destrozada, el teclado no funciona y hay daños en la carcasa. No puedo trabajar." "escalate"
run_ticket "T-B09" "Llevo dos meses sin cobrar" "Llevo dos meses sin recibir mi nómina y nadie me da respuesta desde RRHH. Si esto no se soluciona hoy, hablaré con mi abogado." "escalate"
run_ticket "T-B10" "Compañero compartiendo contraseñas" "He descubierto que un compañero está compartiendo sus credenciales corporativas con personas externas. Es un incumplimiento inaceptable de la política de seguridad." "escalate"
run_ticket "T-B11" "Reclamación horas extra" "Trabajé 40 horas extra el mes pasado y no me las han compensado ni en dinero ni en días libres. Quiero presentar una reclamación formal." "escalate"
run_ticket "T-B12" "Lesión trabajando en almacén" "Un compañero del almacén tiene una lesión en la muñeca después de cargar cajas. Necesitamos ayuda." "escalate"
```
