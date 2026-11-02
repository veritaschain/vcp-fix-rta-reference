# Changelog

All notable changes to the VCP FIX Evidence Pack structure are documented here.

## Publication correction — 2026-11-02

- Label the WorldFirst report as historical AI-assisted research, not an independent assessment or current priority claim.
- The current verifier reports local consistency only; unauthenticated packs remain `INDETERMINATE`, and observed mismatches are `INVALID`. Earlier compliance and production claims below are historical, not current findings.
- Preserve the original file manifest under `archive/` and regenerate the current checksum inventory after the verifier/README repair. Neither manifest authenticates origin or establishes conformity.

## [1.1.0] - 2025-01-06

### Added

- **VCP v1.1 Full Compliance**
  - PolicyIdentification (Section 5.5) in all 27 events
  - VerificationDepth declaration
  - Three-layer architecture metadata

- **FIX Protocol Integration**
  - `fix_messages.jsonl`: 18 FIX messages with VCP event correlation
  - `mapping.md`: Complete FIX Tag → VCP Field transformation reference
  - Lossless/Lossy field classification with rationale

- **Cryptographic Artifacts**
  - `keys/`: Ed25519 public key (PEM + JWK) with key manifest
  - `events.jsonl`: Streaming format for scale
  - Enhanced `hash_manifest.json` covering all 18+ files

- **Verification Outputs**
  - `verifier_outputs/verification_report.json`: Machine-readable
  - `verifier_outputs/verification_report.txt`: Human-readable
  - `examples/verify_expected.txt`: Fixed expected output

- **Datasets**
  - `datasets/metadata.json`: Pack-wide machine-readable declaration

- **Certificates**
  - Expanded to 4 event types: ORD, ACK, EXE, REJ
  - Demonstrates coverage across order lifecycle

### Changed

- `hash_manifest.json` now includes all pack files (was 3, now 18)
- `mapping.md` now includes Lossless/Lossy classification at top
- `README.md` enhanced with Trust Model, Limitations, Key warnings

### Security

- Demo public key clearly marked as non-production
- Key manifest includes fingerprints for verification
- Production requirements documented

## [1.0.0] - 2025-01-06

### Added

- Initial VCP v1.1 evidence pack structure
- Core files: events.json, batches.json, anchors.json
- Basic verification script

---

## Version Numbering

This changelog follows [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes to pack structure
- **MINOR**: New files/features, backward compatible
- **PATCH**: Bug fixes, documentation updates

---

*Maintained by VeritasChain Standards Organization (VSO)*
