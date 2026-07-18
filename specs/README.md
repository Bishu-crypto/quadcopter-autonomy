# Interface & Protocol Specifications

This directory contains specifications, interface contracts, serialization schemas, and protocol definitions for the Voyager ecosystem.

---

## Purpose

To enforce our core philosophy of **Interface-Driven Design**, all cross-module boundaries must be documented and versioned here before code is written.

### Key Focus Areas
1. **Voyager Protocol Spec**: Schema layouts, byte framing, heartbeat rules, and parameter transactions.
2. **Simulator Plugin API**: Interface definitions for sensor data providers and actuator command consumers.
3. **SDK Vehicle API**: Language-agnostic class schemas and response formats for high-level scripting.
4. **Message Schemas**: Serialized structure definitions (e.g., Protocol Buffer files or custom IDL definitions).
