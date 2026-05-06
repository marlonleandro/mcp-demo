# Frontend - Cliente React

Cliente React que consume el API Server backend (NO consume MCP directamente).

## 🚀 Instalación

```bash
npm install
```

## ⚙️ Configuración

El archivo `.env` ya está configurado para desarrollo local:

```env
VITE_API_URL=http://localhost:5000/api
```

## ▶️ Ejecución

```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:3000` o `http://localhost:5173`

## 🏗️ Estructura

```
src/
├── App.jsx                  # Componente principal con autenticación
├── main.jsx                 # Punto de entrada
├── index.css                # Estilos globales
├── components/
│   ├── Login.jsx            # Pantalla de login
│   ├── TaskForm.jsx         # Formulario de creación
│   └── TaskList.jsx         # Lista de tareas
└── services/
    └── apiService.js        # Cliente HTTP (axios)
```

## 🔧 Características

- ✅ Autenticación JWT
- ✅ Gestión de tareas (CRUD)
- ✅ Interfaz responsive
- ✅ Manejo de errores
- ✅ Loading states
- ✅ Logout automático en token expirado

## 🔄 Flujo de Datos

```
Usuario interactúa con UI
    ↓
Componente React
    ↓
apiService.js (axios)
    ↓ HTTPS/REST + JWT
API Server (Backend)
    ↓ stdio o HTTP
MCP Servers
```

## 📝 Notas Importantes

### ⚠️ El Frontend NO consume MCP directamente

En esta arquitectura empresarial:
- El frontend solo hace peticiones HTTP al API Server
- El API Server es quien consume los MCP Servers
- Esto es la práctica correcta en producción

### 🔐 Autenticación

1. Usuario hace login
2. Backend retorna JWT token
3. Token se guarda en localStorage
4. Todas las peticiones incluyen el token en el header `Authorization: Bearer <token>`
5. Si el token expira, se redirige al login

## 🎨 Personalización

### Cambiar URL del API

Edita `.env`:
```env
VITE_API_URL=https://tu-api.com/api
```

### Estilos

Los estilos están en `src/index.css` usando CSS vanilla (sin frameworks CSS).

## 🚀 Build para Producción

```bash
npm run build
```

Los archivos estáticos se generarán en `dist/` listos para deploy.

## 📦 Deploy

### Netlify / Vercel

```bash
npm run build
# Subir carpeta dist/
```

### Nginx

```nginx
server {
    listen 80;
    server_name tu-dominio.com;
    
    root /var/www/frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend:5000;
    }
}
```

## 🧪 Testing (opcional)

```bash
npm install --save-dev vitest @testing-library/react
npm run test
```
