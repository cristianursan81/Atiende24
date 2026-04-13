# KB-002 · Acceso VPN

**Categoría:** Acceso remoto

## ¿Cómo conecto la VPN corporativa?

1. Descarga el cliente **GlobalProtect** desde `https://intranet.empresa.com/vpn`.
2. Introduce el servidor: `vpn.empresa.com`.
3. Inicia sesión con tu usuario y contraseña corporativos.
4. Acepta la autenticación de dos factores (2FA) que llegará a tu móvil.

## Requisitos

- Windows 10/11 o macOS 12+.
- Antivirus corporativo instalado y actualizado.
- Certificado de dispositivo válido (se renueva automáticamente cada año).

## Problemas frecuentes

| Síntoma | Solución |
|---------|----------|
| "No se puede conectar al servidor" | Verifica tu conexión a internet y que el servidor VPN sea `vpn.empresa.com` |
| Error de certificado | Ejecuta `Renovar certificado` desde el icono de GlobalProtect en la bandeja del sistema |
| 2FA no llega | Comprueba que el número de teléfono en tu perfil de directorio es correcto |

Si el problema persiste tras seguir estos pasos, abre un ticket en soporte.
