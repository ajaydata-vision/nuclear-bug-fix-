# External Intelligence Reference

When internal analysis isn't enough — search external sources BEFORE concluding.
A known bug has a known fix. Finding it takes 2 minutes. Rediscovering it takes hours.

---

## DECISION TREE — When to Search

```
Does the error message contain a library/framework name?     YES → Search immediately
Did the bug start after a version update?                    YES → Search changelog
Does the behavior contradict the official docs?              YES → Read the docs
Does the bug involve a protocol (HTTP, WS, OAuth, SMTP)?     YES → Check the RFC
Is the bug auth/security related?                            YES → Check CVEs
Is the framework version < 6 months old?                     YES → Search GitHub issues
Can you explain WHY the code fails just by reading it?       NO  → Search first
```

If 2+ of the above are YES → **search before writing any forensic logs.**

---

## SOURCE HIERARCHY (Search in This Order)

### TIER 1 — Official Sources (Highest Authority)

**1. Official Documentation**
Search: `site:docs.[framework].com [feature] [method]`
Or: `[framework] official docs [feature] [method]`

What to look for:
- Does the method signature match what the code uses?
- Are there version-specific notes or deprecation warnings?
- Are there "gotchas" or "important" sections that contradict assumptions?
- Is there a migration guide for the version in use?

Examples:
- Django docs: `docs.djangoproject.com`
- React docs: `react.dev`
- Spring docs: `docs.spring.io`
- PostgreSQL docs: `postgresql.org/docs/[version]/`
- Node.js docs: `nodejs.org/docs/latest-v[X]/api/`

**2. Official Changelog / Release Notes**
Search: `[library] [version] changelog` or `[library] CHANGELOG.md github`

What to look for:
- Breaking changes between working version and current version
- Bug fixes that describe the exact symptom
- Deprecation of the API being used
- Behavior changes that match the bug description

How to read changelogs effectively:
```
Working version: X.Y.Z
Current (broken) version: X.Y.Z+N

Check EVERY version between X.Y.Z and current for:
- "Breaking change:" entries
- "Fixed:" entries that describe the symptom (may be a regression)
- "Deprecated:" entries for APIs in use
- "Changed behavior:" entries
```

**3. Official Migration Guides**
Search: `[framework] migrate [old version] to [new version]`

Critical for:
- Major version upgrades (v2 → v3, v14 → v15)
- Framework rewrites
- ORM major versions (Hibernate 5 → 6, Prisma 4 → 5)

---

### TIER 2 — Community Bug Reports

**4. GitHub Issues**
Search directly on GitHub or via web:
```
Query pattern: site:github.com/[org]/[repo]/issues "[error message]"
Or: "[library] github issue [version] [symptom]"
```

Search strategy:
```
Step 1: Search with EXACT error message in quotes
Step 2: Filter by: Issues → label:bug → version:[version]
Step 3: Check CLOSED issues (many bugs are fixed but undocumented)
Step 4: Look for "won't fix" labels — indicates known limitation, not fixable
Step 5: Check linked PRs — the fix code shows exactly what was wrong
```

What a good GitHub issue tells you:
- Exact reproduction steps → compare to user's scenario
- Which version introduced it → matches user's version?
- Which version fixed it → is user below that version?
- Workaround in comments → immediate fix even without upgrading

**5. Stack Overflow**
Search: `[exact error message] [framework] [version]`

Use quotes around error message for exact match.
Sort by: Newest (to find version-specific answers, not old ones for old versions)

What to look for:
- Accepted answers with high votes + recent date
- Answers mentioning the exact version
- Comments showing the answer is version-specific

---

### TIER 3 — Protocol & Specification Sources

**6. RFC Lookup (for Protocol Bugs)**

HTTP:
- RFC 9110: HTTP Semantics (methods, headers, status codes)
- RFC 9112: HTTP/1.1 Message Syntax
- RFC 9113: HTTP/2
- RFC 9114: HTTP/3
- RFC 7235: HTTP Authentication
- RFC 6265: HTTP Cookies

Auth / Security:
- RFC 6749: OAuth 2.0 Authorization Framework
- RFC 7636: PKCE (Proof Key for Code Exchange)
- RFC 7519: JSON Web Tokens (JWT)
- RFC 7517: JSON Web Key (JWK)
- RFC 8693: Token Exchange

Email:
- RFC 5321: SMTP
- RFC 5322: Internet Message Format
- RFC 3501: IMAP4rev1
- RFC 9051: IMAP4rev2

Real-time:
- RFC 6455: WebSocket Protocol
- RFC 8441: WebSocket over HTTP/2

Data formats:
- RFC 3339: Date/Time on the Internet (timestamps)
- RFC 4648: Base64 Encoding
- RFC 3986: URI Generic Syntax
- RFC 8259: JSON

How to use RFCs for debugging:
```
1. Find the section describing the behavior in question
2. Read what MUST / MUST NOT / SHOULD / SHOULD NOT the implementation do
3. Compare to what the code does
4. Deviation from MUST = bug in the code
5. Deviation from SHOULD = likely bug, may be intentional
```

Search RFCs at: tools.ietf.org/html/rfc[number]
Or: rfcs.io/rfc/[number]

---

### TIER 4 — Security & Vulnerability Sources

**7. CVE Database**
Search: `[library] [version] CVE` or `[library] vulnerability [year]`

Sources:
- NVD: nvd.nist.gov/vuln/search
- OSV: osv.dev (open source vulnerabilities)
- GitHub Security Advisories: github.com/advisories

What to look for:
- Is the version in use flagged as vulnerable?
- Is the bug actually a known security issue?
- Is there a patched version?

**8. Package Registry Advisories**
```
npm:    npmjs.com/advisories  OR  npm audit (run in project)
PyPI:   pypi.org/project/[pkg]/#history  +  safety check (run in venv)
Maven:  mvnrepository.com/artifact/[group]/[artifact]
Go:     pkg.go.dev/[module]  +  govulncheck ./...
Cargo:  crates.io/crates/[crate]  +  cargo audit
```

---

### TIER 5 — Browser & Compatibility Sources

**9. MDN Web Docs (for Web APIs)**
Search: `mdn [api name] [method]` or `site:developer.mozilla.org [api]`

What to look for:
- Browser compatibility table at bottom of page
- "Experimental" or "Deprecated" flags
- Browser-specific quirks in Notes section
- Polyfill requirements

**10. caniuse.com (for CSS/HTML features)**
Search: `caniuse [feature]`

What to look for:
- Is the feature supported in the browser where bug occurs?
- Partial support with known limitations?
- Required vendor prefix?
- Version where support was added?

---

## QUERY CONSTRUCTION GUIDE

### For error message bugs:
```
"[exact error message]" [library] [version]
"[exact error message]" site:github.com
"[exact error message]" stackoverflow
```

### For behavioral bugs (no error message):
```
[library] [version] [feature] not working
[library] [version] [method] returns wrong value
[library] [version] [method] breaking change
[library] [version] regression [behavior]
```

### For version compatibility bugs:
```
[library-a] [version] compatible with [library-b] [version]
[library] [version] requires [dependency] [version]
[library] peer dependency [version] mismatch
```

### For protocol bugs:
```
[protocol] RFC [section topic] compliance [library]
[protocol] [specific header/feature] [library] bug
[library] [protocol] spec violation
```

### For breaking changes:
```
[library] [old-version] to [new-version] breaking change
[library] [version] migration guide breaking
[library] CHANGELOG [version] breaking
```

---

## HOW TO INTERPRET AND USE RESULTS

### Case 1: Found an EXACT match (same error, same version)
```
→ State explicitly: "This is a confirmed bug in [library] [version]"
→ Provide: fixed version number
→ Provide: workaround if not upgrading
→ Link: issue URL or changelog entry
→ Skip further forensic analysis — root cause is confirmed externally
```

### Case 2: Found a SIMILAR match (same symptom, different version)
```
→ State: "Known issue in [library] [version range], possibly related"
→ Check if user's version falls in affected range
→ Provide the fix/workaround from the issue
→ Note: may be a different root cause at user's exact version
→ Continue to forensic logging to confirm
```

### Case 3: Found a DOCS DISCREPANCY (code doesn't match docs)
```
→ State: "The code uses the API incorrectly per official documentation"
→ Quote the relevant docs section
→ Provide corrected code matching docs
→ This IS the verdict — no further forensic analysis needed
```

### Case 4: Found an RFC VIOLATION (protocol misimplemented)
```
→ State: "The implementation violates RFC [number], Section [X]"
→ Quote the MUST/MUST NOT clause being violated
→ Provide correct implementation per RFC
→ Note: RFC violations cause cross-client/cross-server incompatibility
```

### Case 5: Found a CVE (security vulnerability)
```
→ State: "This is a known security vulnerability: CVE-[number]"
→ Provide: severity, affected versions, patched version
→ Provide: immediate mitigation steps
→ Flag: this is not just a bug — it's a security issue requiring urgent patching
```

### Case 6: Found NOTHING
```
→ State: "No known external issue found for this combination"
→ This is a new/unique bug
→ Continue to Phase 3.7 (Find the Lies) and Phase 3.8 (Forensic Logging)
→ The forensic approach will prove the root cause
```

---

## SILENT ORM BEHAVIOR CHANGE TRIGGER

**Signal:** ORM write returns success (200/no error), but the field value in the database is unchanged. No exception thrown. Only happens after a major ORM version upgrade.

This pattern bypasses the normal external search triggers (no error message, no exception stack trace). It is easy to misdiagnose as an application bug — wrong query, wrong variable, wrong endpoint.

**What to do immediately — before debugging application code:**
```
1. Log the exact ORM query being generated (enable ORM query logging)
2. Run that exact query directly in the database console
3. If the direct query works but ORM does not → ORM is transforming the query
4. Check the ORM's CHANGELOG for the exact major version jump for:
   - "query transformation" changes
   - "sanitize" or "filter" behavior changes
   - null/undefined handling changes
   - update operator changes ($set, $unset behavior)
   - strict mode changes
```

**Common ORM breaking change patterns by library:**
- **Mongoose 6→7:** `sanitizeFilter` changes affect how null values are treated in updates. `findByIdAndUpdate({ field: null })` may be silently dropped. Use explicit `{ $set: { field: null } }`.
- **Sequelize 5→6:** `returning` option behavior changed. Raw queries may differ.
- **Prisma 4→5:** `null` vs `undefined` distinction in updates — `undefined` means "don't update", `null` means "set to null". Swapping them produces silent no-ops.
- **TypeORM 0.2→0.3:** `update()` behavior for partial updates changed.

**Search query template:** `[ORMName] [version] [field] not updating site:github.com` — or search the ORM's GitHub Issues directly: `is:issue [field] null not persisted`

## VERSION COMPATIBILITY QUICK REFERENCE

When checking compatibility between commonly paired technologies:

**Node.js ecosystem:**
- Check: `engines` field in package.json for min Node version
- Check: `.nvmrc` or `.node-version` for project's pinned version
- Tool: `npx check-node-version --node X.Y.Z`

**Python ecosystem:**
- Check: `python_requires` in setup.py / pyproject.toml
- Check: `tox.ini` for tested versions
- Tool: `pip install pipdeptree && pipdeptree` (dependency tree)

**Java ecosystem:**
- Check: Spring Boot compatibility matrix at start.spring.io
- Check: `java.version` in pom.xml vs runtime `java -version`
- Tool: Maven Enforcer Plugin for version validation

**Database + ORM compatibility:**
- Hibernate: compatible Hibernate ORM → DB version matrix in docs
- Prisma: CHANGELOG for DB version support additions
- SQLAlchemy: dialect support per DB version in docs

**Docker + base image:**
- Check: base image OS version and its default package versions
- Alpine vs Debian/Ubuntu behavior differences (musl vs glibc)
- Architecture: arm64 vs amd64 for M1/M2 Mac → Linux prod mismatch
