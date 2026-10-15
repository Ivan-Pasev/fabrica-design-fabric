---
name: fdf-spatial-web-architect
description: "First-party audited 3D WebGL/WebGPU/R3F scene planning for opt-in project-independent design, with static fallback, performance, license and accessibility gates."
license: MIT
---

# FDF Spatial Web Architect — reference contract v0.10.0

## Scope
Project-neutral 3D scene planning. 3D is **opt-in**; never introduce a WebGL canvas or replace a product interface solely because a demonstration is visually striking. No auto imports, package managers, downloads, code execution, renders or project writes.

## Gate 1: Existing product and platform
Read the frozen product/design contract and identify target framework, WebGL capability, current 3D renderer, existing assets, interaction paths and visual language. Distinguish static/interactive/product-critical 3D and determine whether a simpler SVG/CSS/2D image works better.

## Gate 2: Technical routing
- Framework without React: Three.js or explicit compatible declarative adapter as a later proposal.
- React: React Three Fiber, Drei and compatible Three.js versions are separately pinned and tested before use. Avoid R3F hooks outside Canvas, per-frame allocations, GPU resource leaks, unbounded pixel ratio, heavy postprocessing or unmanaged raycasts.
- Explicitly distinguish WebGL and WebGPU capabilities. Design feature detection and progressive fallback; never declare supported GPUs without tests.
- Prefer compressed assets with documented source licenses and retained attribution. Do not automatically vendor textures, fonts, 3D models, videos, HDRI or effects.

## Gate 3: Nonvisual access and performance
Mandatory content-equivalent static/HTML fallback, keyboard route, accessible names and usable focus order, reduced-motion no-camera-spin mode, loading/error/no-GPU states. Capture mobile thermals/battery/frame latency and WebGL context-loss recovery where feasible. Preserve SEO and primary content as actual HTML where possible.

## Sources and disposition
Reference: https://github.com/Impertio-Studio/Three.js-Claude-Skill-Package (MIT; subpath audit needed before copying), Three.js and pmndrs. Reuse ideas but do not redistribute upstream skills here. Emit design proposal, benchmark fixture proposal, license register, rollback and explicit `HOLD_RUNTIME_AND_HUMAN_APPROVAL`.
