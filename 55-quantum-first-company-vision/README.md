# Quantum-First Venture Evidence Room

Proyecto 55 · Plan 10 · semanas 222–223 · días globales 1548–1561.

Laboratorio local para seleccionar una tesis empresarial con evidencia trazable,
comparaciones reproducibles y condiciones para cambiar de decisión. No es un SaaS
ni una demostración de ventaja cuántica.

## Estado y alcance

Implementación y desk research disponibles. El quality gate comprueba el estado
técnico actual; su resultado se guarda en
[quality-gate.local.json](reports/week-223/quality-gate.local.json).

**El cierre formal sigue pendiente de revisión y aprobación humana.**
No se realizaron entrevistas, ventas, pilotos pagados ni mediciones de mercado.
No hay commits automáticos, despliegue Azure, credenciales ni entrenamiento largo.

El wedge candidato es un assessment de preparación postcuántica para dos servicios
acordados. Su promesa de cuatro semanas y precio son hipótesis a validar, no
resultados obtenidos. Las otras dos tesis se conservan con su evidencia contraria.

## Ejecutar y verificar en Windows

Requisitos: Python 3.13 x64, Node.js 22 o posterior y Git. No requiere Docker/GPU.

```powershell
Set-Location "C:\JeanLoa\Path-AI-Engineer\Quantum-First-Business-Product-Developer-Platform\55-quantum-first-company-vision"
.\scripts\complete-project.ps1
```

Instala dependencias bloqueadas, ejecuta pruebas, compila la web, verifica los
flujos reales de navegador y genera/verifica el bundle candidato.
Es un gate local; **no lanza una matriz de entrenamiento de varios días**.

Si ya instalaste las dependencias:

```powershell
.\scripts\complete-project.ps1 -SkipSetup
```

Para abrir la consola después del gate:

```powershell
.\scripts\start-local.ps1
```

Mantén la terminal abierta. App: http://127.0.0.1:3055
y Swagger local: http://127.0.0.1:8955/docs.
Ctrl+C cierra el preview y su propio proceso de API. No detiene otros proyectos.
Si un puerto está ocupado, el script se detiene sin matar procesos ajenos.

## Qué contiene

- 14 fuentes públicas primarias y 32 registros de evidencia parafraseados.
- 12 arquetipos en cuatro verticales, 18 JTBD y 15 alternativas.
- Tres oportunidades, catorce dimensiones, tres escenarios, ocho stresses
  y 28 perturbaciones individuales de pesos.
- Seis modelos de precio, economics paramétricos y límites de capacidad.
- 24 preguntas de descubrimiento y plan de 15 entrevistas futuras.
- 24 respuestas de autocrítica, seis objeciones y seis trazas decisión–fuente.
- Diez superficies de UI, API de solo lectura y CLI.
- Handoff JSON/Markdown + JSON Schema 2020-12 + ZIP determinista y SHA-256.

Los intervalos reflejan supuestos del analista, no confianza estadística.
Budget y acceso al comprador son desconocidos; no se convierten en cero.
La selección provisional conserva la superposición de intervalos y el dissent.

## CLI

Usa el intérprete local sin activar el entorno:

```powershell
.\.venv\Scripts\python.exe -m venture_evidence.cli evidence validate
.\.venv\Scripts\python.exe -m venture_evidence.cli evidence lint
.\.venv\Scripts\python.exe -m venture_evidence.cli opportunity score --scenario base
.\.venv\Scripts\python.exe -m venture_evidence.cli opportunity sensitivity
.\.venv\Scripts\python.exe -m venture_evidence.cli report build
.\.venv\Scripts\python.exe -m venture_evidence.cli handoff export --version company-vision-v1
.\.venv\Scripts\python.exe -m venture_evidence.cli handoff verify
```

La exportación regenera un candidato, **nunca una aprobación**. El verificador
rechaza cambios en payloads, miembros del ZIP, versión y lineage. SHA-256
detecta cambios; no sustituye una firma de identidad.

## Guía de revisión

1. [Charter y límites](docs/venture-charter.md).
2. [Política de evidencia](docs/source-policy.md).
3. [Protocolo y fragilidad de selección](docs/decisions/scoring-protocol.md).
4. [Tesis generada](reports/week-223/company-thesis.md).
5. [ICP/JTBD](docs/discovery/icp-jtbd-atlas.md) y
   [alternativas](docs/discovery/alternatives.md).
6. [Pricing/supuestos](docs/thesis/pricing-assumptions.md) y
   [producto/moats](docs/product/capability-sequence-moat.md).
7. [Experimentos](experiments/validation-backlog.md) y
   [decisión/challenge](docs/decisions/wedge-and-challenge.md).
8. [Bundle candidato](reports/handoff/company-vision-v1/manifest.json) y
   [matriz de entrega/cierre formal](docs/delivery-matrix.md).

Arquitectura: [ADR-001](docs/decisions/ADR-001-local-evidence-room.md).
Interfaz: [DESIGN.md](docs/DESIGN.md).
Las capturas de [reports/visual](reports/visual) proceden de Playwright real.

## Fuentes de autoridad y mantenimiento

`scripts/build_research.py` materializa el corpus canónico y el protocolo.
No se ejecuta automáticamente desde setup/gate para no sobrescribir una edición
del investigador. Tras un cambio deliberado, regenera y revisa el diff:

```powershell
.\.venv\Scripts\python.exe .\scripts\build_research.py
.\scripts\quality-gate.ps1
```

`scripts/build_documents.py` genera vistas legibles/categorías desde el corpus.
La API trabaja en memoria de solo lectura; tras modificar datos, reinicia
el preview. Los cambios en Next no alteran la identidad de la evidencia de negocio.

El gate valida Ruff, formato, mypy, dependencias, contratos, pruebas negativas/
property/API/CLI, npm audit, TypeScript, ESLint, build, E2E responsive y bundle.
Los avisos de deprecación del test client/CLI son visibles y no se silencian.

El mapa actualizado prevalece sobre el
[README de planificación anterior](docs/legacy-planning-readme.md).
No se afirma haber completado la cadencia de catorce días ni sus commits.
La aprobación de la tesis y el permiso para avanzar a 56 deben ser reales.
Software Engineer consume únicamente artefactos aprobados y su propio mapa;
no importa código, bases de datos, credenciales ni estado de este proyecto.
