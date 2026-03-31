---
applyTo: "frontend/src/**/*.{js,jsx,ts,tsx}"
---

> **Scope**: Se aplica al frontend de PetTech (directorio `MVP_FrontEnd/`). Stack: **React 18 + TypeScript + Vite + Tailwind CSS + Zustand + Zod**.

# Instrucciones para Archivos de Frontend (React 18 + TypeScript + Vite)

## Stack

| Componente | Tecnología |
|---|---|
| Framework | React 18 + TypeScript 5 |
| Build tool | Vite 5 |
| Estilos | **Tailwind CSS** (obligatorio — NUNCA CSS Modules globales ni Bootstrap) |
| Estado global | **Zustand** (store en `src/shared/store/`) |
| Validación de formularios | **Zod** + `react-hook-form` + `@hookform/resolvers` |
| HTTP client | **Axios** |
| Routing | **React Router v6** (`react-router-dom`) |
| Notificaciones | `react-hot-toast` |
| Tests | Vitest + Testing Library |

## Directorio de trabajo

```
MVP_FrontEnd/src/
  features/
    adopciones/    ← api/, components/, hooks/, pages/
    auth/          ← api/, pages/
    dashboard/     ← componentes del dashboard
    familias/      ← api/, components/, hooks/, pages/
    mascotas/      ← api/, components/, hooks/, pages/, formSchema.ts
  shared/
    api/           ← configuración base de axios
    components/    ← componentes reutilizables
    constants/     ← constantes globales
    store/         ← authStore.ts (Zustand)
  router/
    AppRouter.tsx  ← todas las rutas de la app
  App.tsx
  main.tsx
```

## Convenciones Obligatorias

- **Estilos**: SIEMPRE Tailwind CSS — NUNCA crear archivos `*.module.css` ni clases globales.
- **Tipado**: TypeScript en todos los archivos (`.ts`, `.tsx`) — prohibido `any`.
- **Nombres**: PascalCase para componentes y páginas (`.tsx`), camelCase para hooks (`.ts`) y servicios (`.ts`).
- **Auth state**: SIEMPRE consumir del store Zustand `useAuthStore` (`src/shared/store/authStore.ts`) — nunca crear estado de autenticación paralelo.
- **Env vars**: SIEMPRE con prefijo `VITE_` para que Vite las exponga.
- **Extensión de archivos de componentes**: `.tsx`. Hooks y servicios: `.ts`.

## Auth Store (Zustand)

```typescript
// src/shared/store/authStore.ts — fuente única de verdad para auth
import { useAuthStore } from '@/shared/store/authStore';

const { token, user, setAuth, clearAuth } = useAuthStore();
```

NUNCA crear estado de autenticación adicional fuera del store.

## Llamadas a la API Backend

Usar siempre **Axios** (no `fetch`). Las llamadas van en los archivos de `api/` dentro de cada feature, nunca directamente en componentes o páginas.

```typescript
// features/mascotas/api/mascotasApi.ts
import axios from 'axios';
const API_BASE = import.meta.env.VITE_API_URL;

export async function getMascotas(token: string) {
  const res = await axios.get(`${API_BASE}/api/v1/mascotas/`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return res.data;
}
```

El token se obtiene siempre desde `useAuthStore()`:
```typescript
const { token } = useAuthStore();
```

## Validación de Formularios

Usar **Zod** + `react-hook-form` + `@hookform/resolvers`. El schema Zod vive junto a la feature:

```typescript
// features/mascotas/formSchema.ts
import { z } from 'zod';
export const mascotaSchema = z.object({
  nombre: z.string().min(1, 'El nombre es obligatorio'),
  especie: z.enum(['perro', 'gato']),
});
```

## Rutas (React Router v6)

Las rutas se registran en `src/router/AppRouter.tsx`:
```tsx
<Route path="/mascotas" element={<ProtectedRoute><MascotasPage /></ProtectedRoute>} />
```

Roles de usuario (`ADMIN` | `FAMILIA`) deber chequearse en las rutas protegidas.

## Estructura por Feature

```
features/<modulo>/
  api/          ← llamadas HTTP al backend (Axios)
  components/   ← componentes UI del módulo
  hooks/        ← hooks custom del módulo
  pages/        ← páginas/vistas completas
  formSchema.ts ← schemas Zod (si hay formularios)
```

## Nunca hacer

- `any` en TypeScript.
- Llamadas a la API directamente en componentes o páginas — siempre en `api/`.
- Crear estado de autenticación paralelo — solo `useAuthStore`.
- CSS Modules o estilos inline — solo Tailwind CSS.
