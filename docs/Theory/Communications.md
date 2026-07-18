# Voyager Theory — Communication Protocols & Telemetry

This document details the serialization, packet framing, and link management protocols used to transmit data reliably between the Ground Control Station (GCS), the SDK, and the vehicle.

---

## 1. Packet Framing Design

Serial links (like UART radios) and network links (like UDP) transmit raw byte streams. To reconstruct structured messages, we envelope payloads in a **Framing Layer**. A frame enables the receiver to scan the incoming byte stream, identify the start of a packet, validate its length, and verify data integrity.

### Voyager Frame Specification

A standard Voyager frame has a fixed 7-byte overhead:

```
┌───────┬───────┬────────┬─────────┬─────────┬─────────────────┬─────────┬─────────┐
│ START │ START │ MSG ID │ SEQ NUM │ LEN (N) │ PAYLOAD DATA    │ CRC LSB │ CRC MSB │
│ 0xAA  │ 0x55  │ 1 byte │ 1 byte  │ 1 byte  │ N bytes (0-255) │ 1 byte  │ 1 byte  │
└───────┴───────┴────────┴─────────┴─────────┴─────────────────┴─────────┴─────────┘
```

| Field Name | Size (Bytes) | Description |
|---|---|---|
| **START 1** | 1 | Magic byte `0xAA` (indicating start of frame). |
| **START 2** | 1 | Magic byte `0x55` (confirms alignment). |
| **MSG ID** | 1 | Message identifier (determines parser schema). |
| **SEQ NUM** | 1 | Rolling counter (0–255) to detect dropped or reordered packets. |
| **LENGTH** | 1 | Size $N$ of the payload section in bytes. |
| **PAYLOAD** | $N$ | Serialized message data. |
| **CRC-16** | 2 | Cyclic Redundancy Check (CCITT-FALSE, polynomial `0x1021`) of all bytes from `MSG ID` to the last byte of `PAYLOAD`. |

---

## 2. Binary Serialization

To maximize throughput over low-bandwidth RF links (e.g., 57600 bps telemetry radios), Voyager avoids text-based formats (like JSON or XML) in favor of strict, packed binary serialization.

### I. Endianness
All multi-byte numeric fields are serialized in **Little-Endian** byte order. This aligns with the native hardware representation of both the STM32 flight controller (ARM Cortex) and standard x86 Ground Control Station processors, eliminating CPU overhead for byte swapping.

### II. Structure Packing
Compilers introduce padding bytes into structures to align variables with memory boundaries (e.g., aligning `uint32_t` on 4-byte boundaries). To prevent these padding bytes from bloating packet sizes or creating compiler-specific differences, all shared communication structs must be strictly packed.
- In **C++**: Mark structs with `#pragma pack(push, 1)` and `#pragma pack(pop)`.
- In **Python**: Use the `struct` module with the `<` prefix (e.g., `struct.pack('<ffB', val1, val2, val3)`).

---

## 3. Link Management & Failsafes

### Heartbeats (Keep-Alive)
Both the vehicle (FC) and the Ground Control Station (GCS) must broadcast a periodic **HEARTBEAT** message (typically at 1 Hz). 
- **Heartbeat Payload**: Contains vehicle type, flight mode (ARMED/DISARMED/WAYPOINT/FAILSAFE), and system status flags.
- **Link Monitoring State Machine**:
  - The receiver resets a `last_heartbeat_time` timer every time a valid heartbeat packet is decoded.
  - If the timer exceeds **$3.0$ seconds**, the connection is marked as `LOST`.
  - On the vehicle, a lost link triggers the **RC/GCS Loss Failsafe** (initiating an autonomous Return-to-Launch or Landing routine).

---

## 4. Parameter Exchange Protocol

Configuring flight control gains (like PID values) requires a transactional, loss-tolerant protocol over the telemetry link to guarantee that parameters are read or written successfully without corruption.

```
       GCS (Client)                                      FC (Server)
            │                                                 │
            │ ── PARAM_REQUEST_READ (param_id: "PID_ROLL_P") ─► │
            │                                                 │
            │ ◄── PARAM_VALUE (param_id: "PID_ROLL_P", 1.25) ─│ (Acknowledge)
            │                                                 │
            │                                                 │
            │ ── PARAM_REQUEST_WRITE ("PID_ROLL_P", 1.50) ───► │
            │                                                 │
            │ ◄── PARAM_VALUE ("PID_ROLL_P", 1.50) ───────────│ (Confirm Write)
            │                                                 │
```

1. **Parameter Struct**:
   - `param_id`: 16-character ASCII string (unique parameter name).
   - `param_value`: 32-bit float value.
   - `param_type`: 8-bit type field (float, int32, uint8, etc.).
2. **Transaction Integrity**:
   - The writing party sends a `PARAM_REQUEST_WRITE` packet.
   - The receiving party writes the value to RAM (or flash) and immediately replies with a `PARAM_VALUE` packet reflecting the newly stored value.
   - If the sender does not receive the confirmation within **$500$ ms**, it retries the write up to 3 times before declaring a communication timeout.

---

## 5. Bandwidth Allocation & Optimization

To avoid saturating the link, messages are prioritized and throttled:

| Priority | Message Type | Rate (Hz) | Description |
|---|---|---|---|
| **Critical** | Heartbeats, Failsafe Alert | 1 | Keeps connection alive; signals emergency states. |
| **High** | IMU, Attitude, Rates | 20–50 | Required for real-time artificial horizon and estimation tracking. |
| **Medium** | GPS, Battery status, Altitude | 5–10 | Required for flight path maps and slow status monitoring. |
| **Low** | Parameters, Mission Waypoints | On-Demand | Only sent during initialization, configuration, or upload. |
