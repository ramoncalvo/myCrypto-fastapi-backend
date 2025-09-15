# API Testing Files

Esta carpeta contiene archivos `.http` para probar la API de MyCrypto FastAPI v2.0.

## Archivos de Testing

### `quick-test.http`
**Uso**: Prueba rápida de funcionalidad básica
- Health check
- Crear usuario y asset
- Crear entrada de portfolio
- Verificar endpoints básicos

### `api.http`
**Uso**: Testing completo de todos los endpoints
- Todos los endpoints de usuarios
- Todos los endpoints de crypto assets
- Todos los endpoints de portfolio
- Incluye operaciones CRUD completas

### `test-scenarios.http`
**Uso**: Escenarios de testing complejos
- Flujo completo usuario → portfolio
- Testing de actualizaciones de precios
- Gestión avanzada de portfolio
- Testing de manejo de errores
- Testing de paginación
- Testing de conexión a base de datos

### `environment.http`
**Uso**: Variables de entorno para los tests
- URLs base y configuración
- IDs de ejemplo para reemplazar
- Datos de prueba predefinidos

## Cómo usar

### 1. Instalar extensión HTTP Client
- **VS Code**: REST Client extension
- **IntelliJ/WebStorm**: HTTP Client (built-in)
- **Postman**: Importar como colección

### 2. Iniciar el servidor
```bash
# Instalar dependencias
pip install -r requirements.txt

# Iniciar MongoDB (si usas local)
brew services start mongodb-community

# Ejecutar servidor
python main.py
```

### 3. Ejecutar tests

#### Opción A: VS Code con REST Client
1. Abrir archivo `.http`
2. Hacer clic en "Send Request" sobre cada endpoint
3. Ver respuestas en panel lateral

#### Opción B: Línea de comandos con curl
```bash
# Health check
curl http://localhost:8000/health

# Crear usuario
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User","password":"test123"}'
```

### 4. Flujo de testing recomendado

1. **Empezar con `quick-test.http`**
   - Verificar que todo funciona básicamente
   - Obtener IDs reales para usar en otros tests

2. **Usar `test-scenarios.http`**
   - Reemplazar placeholders con IDs reales
   - Ejecutar escenarios completos

3. **Usar `api.http`** para testing detallado
   - Probar todos los endpoints individualmente
   - Verificar edge cases

## Variables a reemplazar

En los archivos encontrarás placeholders como:
- `{{user_id}}` → ID real del usuario creado
- `{{asset_id}}` → ID real del asset creado
- `{{portfolio_id}}` → ID real de la entrada de portfolio

**Importante**: Reemplaza estos valores con IDs reales obtenidos de las respuestas de la API.

## Endpoints disponibles

### Health & Info
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /docs` - API documentation (Swagger)

### Users
- `POST /users/` - Crear usuario
- `GET /users/` - Listar usuarios
- `GET /users/{id}` - Obtener usuario
- `PUT /users/{id}` - Actualizar usuario
- `DELETE /users/{id}` - Eliminar usuario
- `GET /users/email/{email}` - Buscar por email

### Crypto Assets
- `POST /crypto-assets/` - Crear asset
- `GET /crypto-assets/` - Listar assets
- `GET /crypto-assets/{id}` - Obtener asset
- `PUT /crypto-assets/{id}` - Actualizar asset
- `DELETE /crypto-assets/{id}` - Eliminar asset
- `GET /crypto-assets/symbol/{symbol}` - Buscar por símbolo

### Portfolio
- `POST /portfolio/` - Crear entrada
- `GET /portfolio/` - Listar entradas
- `GET /portfolio/{id}` - Obtener entrada
- `PUT /portfolio/{id}` - Actualizar entrada
- `DELETE /portfolio/{id}` - Eliminar entrada
- `GET /portfolio/user/{user_id}` - Portfolio de usuario

## Troubleshooting

### Error: Connection refused
- Verificar que el servidor esté ejecutándose en puerto 8000
- Verificar que MongoDB esté ejecutándose

### Error: Database connection
- Verificar configuración en `.env`
- Verificar que MongoDB esté accesible

### Error: Validation error
- Verificar formato JSON en requests
- Verificar que todos los campos requeridos estén presentes

### Error: 404 Not Found
- Verificar que los IDs existan en la base de datos
- Usar IDs reales obtenidos de respuestas previas
