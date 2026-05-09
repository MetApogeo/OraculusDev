Este es un excelente punto de partida para tu proyecto **Oraculus**. Un README que cuenta la historia detrás del código no solo lo hace más humano, sino que demuestra tu capacidad de planeación y evolución arquitectónica como arquitecto de software y educador.

Aquí tienes una estructura profesional y narrativa para tu archivo `README.md`:

---

# 👁️ Oraculus: Financial Repo Analytics

**Oraculus** es una herramienta de interfaz de línea de comandos (CLI) diseñada para transformar métricas técnicas de repositorios (GitHub/Jira) en indicadores financieros claros para stakeholders. Permite calcular el costo real de desarrollo basado en el esfuerzo técnico y la eficiencia operativa.

## 📜 La Historia Detrás del Código

El desarrollo de Oraculus no empezó frente a un monitor, sino en los espacios entre clases y horas libres durante mi labor como profesor.

### 1. Las Primeras Semillas (Bocetos en Papel)

Todo comenzó con la necesidad de centralizar la comunicación entre ramas de GitHub y tareas de Jira. Estos esquemas iniciales fueron trazados "entre clases", capturando la esencia de lo que hoy es el ecosistema de análisis.

_Figura 1: Arquitectura inicial de flujo entre Jira, GitHub y el cálculo de Story Points._

_Figura 2: Definición de esquemas estrictos con Pydantic y la lógica de mappers entre PHP y Python._

### 2. La Formalización Matemática (La Pizarra)

Durante una hora libre, las ideas se convirtieron en fórmulas. El **7 de mayo de 2026**, definí la lógica financiera que rige el sistema actual, incluyendo el filtro de **Rango Intercuartílico (IQR)** para detectar anomalías en los commits.

_Figura 3: Definición del Índice de Eficiencia Financiera ($IEF$) y fórmulas de costo por commit._

---

## 🛠️ Estado Actual del Desarrollo

Hoy, Oraculus ha evolucionado de garabatos en papel a una herramienta CLI funcional que aplica principios sólidos de ingeniería de software:

- **Arquitectura DTO:** Uso de `dataclasses` para el transporte de datos limpio y tipado.
- **Responsabilidad Única (SRP):** El sistema está dividido en estaciones: obtención de datos (Fetcher), cálculo de métricas (Calculadora) y ejecución (CLI).
- **Métricas en Tiempo Real:** Integración con la API REST de GitHub para analizar impacto de código.

### Lógica Financiera Implementada

El sistema calcula actualmente el costo de la siguiente manera:

1. **Costo por Hora ($C_h$):**
   $$C_h = \frac{\text{Salario Mensual}}{\text{Horas Efectivas}}$$

2. **Tiempo por Commit ($T_{horas}$):**
   $$T_{horas} = \frac{LOC_{commit}}{60}$$

3. **Costo del Commit ($C_{commit}$):**
   $$C_{commit} = C_h \cdot T_{horas}$$

---

## 🚀 Hoja de Ruta (Roadmap)

Aunque el núcleo es funcional, el proyecto se encuentra en una fase de optimización continua:

- [ ] **Migración a GraphQL:** Para resolver el problema de $N+1$ llamadas y obtener todos los datos en una sola petición.
- [ ] **Análisis Git Local:** Implementación de lectura directa de la carpeta `.git` para máxima velocidad sin dependencia de API.
- [ ] **Integración con Jira:** Siguiendo los bocetos originales para cruzar costos con Story Points.

---

## 📄 Licencia

Este proyecto es de código abierto (Open Source).

> _"De la pizarra al despliegue: Arquitectura sistémica para decisiones lógicas."_

---
