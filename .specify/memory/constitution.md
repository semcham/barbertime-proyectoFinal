<!--
=== SYNC IMPACT REPORT ===
Version change: [CONSTITUTION_VERSION] -> 1.0.0
Modified principles:
  - [PRINCIPLE_1_NAME] -> I. La Especificación es la Fuente de Verdad (Specification-First)
  - [PRINCIPLE_2_NAME] -> II. Stack Tecnológico Fijo (Django MVT + PostgreSQL)
  - [PRINCIPLE_3_NAME] -> III. Test-First (No Negociable)
  - [PRINCIPLE_4_NAME] -> IV. Simplicidad (YAGNI)
  - [PRINCIPLE_5_NAME] -> V. Borrado Lógico y Trazabilidad
Added principles:
  - VI. Roles y Privacidad
  - VII. Gestión con Scrum
Added sections:
  - ## Architecture and Framework Constraints (replacing ## [SECTION_2_NAME])
  - ## Development Workflow and Quality Gates (replacing ## [SECTION_3_NAME])
Removed sections:
  - None
Templates requiring updates:
  - .specify/templates/tasks-template.md (✅ updated)
  - .specify/templates/plan-template.md (✅ updated)
Follow-up TODOs:
  - None
==========================
-->

# BarberTime Constitution

## Core Principles

### I. La Especificación es la Fuente de Verdad (Specification-First)
Ninguna línea de código se escribe sin que exista primero una especificación aprobada en `spec.md`. El código es un artefacto derivado, generado con asistencia de un agente de IA. Cualquier discrepancia entre el código implementado y la especificación se resolverá modificando o corrigiendo primero la especificación.

### II. Stack Tecnológico Fijo (Django MVT + PostgreSQL)
Python 3.11+, Django 5 (patrón MVT) y PostgreSQL son las únicas tecnologías de backend y persistencia admitidas. No se introduce ningún framework de frontend adicional (sin React, Vue ni SPA). La interfaz de usuario se debe resolver íntegramente mediante plantillas de Django renderizadas en el servidor.

### III. Test-First (No Negociable)
Toda historia de usuario requiere pruebas automatizadas (unitarias y/o de integración, con el framework de pruebas integrado de Django) antes de considerarse completada. Las pruebas deben escribirse primero y fallar antes de que se escriba la implementación que las haga pasar.

### IV. Simplicidad (YAGNI)
No se implementa funcionalidad que no esté explícitamente descrita en `spec.md` para el incremento vigente. Se evitará la sobreingeniería y el desarrollo anticipado de características que no se requieran de inmediato.

### V. Borrado Lógico y Trazabilidad
Las entidades de negocio (Cliente, Servicio, Cita) nunca se eliminan físicamente de la base de datos, solo se marcan como inactivas mediante una bandera de borrado lógico (e.g., `is_active = False`) para mantener la integridad referencial y permitir auditorías.

### VI. Roles y Privacidad
El sistema tiene dos tipos de usuario claramente separados: administradores/barberos (staff, gestionan todo el negocio) y clientes (público general, se autorregistran y solo ven/gestionan sus propias citas). Ningún cliente puede ver ni modificar datos de otro cliente. Esto debe validarse a nivel de base de datos y de vista.

### VII. Gestión con Scrum
El trabajo se organiza en sprints semanales sobre el flujo de Spec-Driven Development. Cada sprint debe entregar un incremento potencialmente desplegable que cumpla plenamente con los criterios de aceptación y las pruebas correspondientes.

## Architecture and Framework Constraints

El sistema debe estructurarse conforme al patrón MVT clásico de Django. La persistencia de datos se gestionará exclusivamente con el ORM de Django mapeado a PostgreSQL. Se prohíbe el uso de frameworks de JavaScript que gestionen el estado en el cliente (como React, Angular o Vue); en su lugar, se emplearán vistas de Django que devuelvan HTML completo y estilos en cascada (Vanilla CSS).

## Development Workflow and Quality Gates

Antes de iniciar la codificación, debe definirse y aprobarse la especificación de la historia en `spec.md`. Posteriormente, se genera el plan de implementación (`plan.md`) y la lista de tareas en `tasks.md`. El flujo exige la definición de pruebas automáticas que inicialmente fallen. Solo se considerará completada una tarea si pasa todas las pruebas automáticas y cuenta con la especificación actualizada.

## Governance

Esta constitución es la ley suprema del proyecto BarberTime. Cualquier cambio en los principios requiere una enmienda formal de este documento, incrementando la versión según las reglas de versionado semántico. El agente de IA y los desarrolladores deben validar cada contribución contra estos principios.

**Version**: 1.0.0 | **Ratified**: 2026-07-13 | **Last Amended**: 2026-07-13
