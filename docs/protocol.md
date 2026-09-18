# Automation protocol v1

The Editor owns the HTTP server and scene semantics. This repository owns the
Python client, MCP adapter and Agent Skill. They communicate over loopback; no
engine source import or shared filesystem layout is needed at runtime.

## Requests

- `GET /health` returns `editor_get_status`.
- `POST /call` accepts `tool`, `arguments` and the absolute bound `project` path.
- Writes also require `session_id`, `scene_version` and `request_id`.
- Each request uses `Authorization: Bearer <token>`.
- HTTP bodies are JSON. IDs and int64/uint64 values are decimal strings.
- The server accepts loopback connections only, rejects browser Origin headers
  and unsupported HTTP framing, caps headers at 8 KiB and bodies at 1 MiB, and
  serves one connection at a time.

The health payload contains the project, session ID, current scene path, scene
version, edit/play/pause state, dirty flag and `protocol_version`. The client
requires version 1, checks the configured project, and detects Editor restart.
The component schema is queried live; tool arguments are listed by
`tomcat-skills list` and MCP `tools/list`.

## Results

```json
{"ok": true, "data": {}}
```

```json
{"ok": false, "error": {"code": "EDIT_MODE_REQUIRED", "message": "Stop Play first."}}
```

MCP retains structured content and maps errors to `isError=true`. The client
attaches the request ID to write results and ambiguous transport errors.
Transport timeouts do not imply that an operation was rolled back.

## Editing and concurrency

Writes execute on the Editor main thread, including while minimized. Component
edits use the registered property validators. Authoring edits stage a Scene copy
and serialize history before publishing; each changed scene operation becomes one
undo entry. Multiple tool calls do not form an atomic transaction.

Authoring writes require Edit mode. Active undo transactions and pending
destructive/recovery/migration dialogs block writes. Transform writes preserve
world/local hierarchy semantics; rotation units are radians.

The client obtains a fresh health result before a new request. To protect a plan
based on an earlier inspection, pass that inspection's `scene_version` explicitly.
`SCENE_CHANGED` requires rereading and reconsidering the operation.

`editor_step` completes one fixed 1/60 second step in Pause mode and renders to
the Game framebuffer. Stop restores the authoring scene. Save requires an
existing scene path. Undo can also undo manual edits.

## Retry lifecycle

The Editor retains the last 256 distinct write bodies/results. An identical ID
and body returns the cached response; changed bodies are rejected. Expired IDs
remain tombstoned so eviction by another client cannot cause duplicate execution.
A session accepts at most 65,536 distinct write IDs, then requires an Editor
restart after saving.

The Python client retains the last 256 write bodies. It does not retry writes
automatically. After `OUTCOME_UNKNOWN`, retry in the same Client/MCP session with
the returned `request_id` and original tool arguments. The original session and
scene-version preconditions are preserved in the wire body.

`REQUEST_EXPIRED`, lost client state or `SESSION_MISMATCH` require actual scene
inspection. Do not recreate a possibly completed operation with a fresh ID.
Separate CLI processes do not share the retry cache.

Queued requests that have not started are cancelled on server timeout/shutdown.
An already-dispatched request can complete after the client times out.
