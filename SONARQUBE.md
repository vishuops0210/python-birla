# SonarQube SAST — What & Why

## What is SonarQube

SonarQube is a static code analysis tool. It reads through source code and
reports on code quality and security issues, then enforces a **Quality
Gate** — a pass/fail check that the CI pipeline honors before allowing a
build to proceed.

## Why we need it

- Catches real bugs, security vulnerabilities, and maintainability problems
  automatically, on every push/PR — before a human reviewer has to find them.
- Enforces a hard gate: if the code doesn't meet the bar, the pipeline stops
  before the Docker image is ever built or pushed.
- Checks every push the same way, every time — not dependent on a human noticing.

## What it scans for

| Category | What it means |
|---|---|
| **Bugs** | Code that's likely to behave incorrectly (logic errors) |
| **Vulnerabilities** | Confirmed security flaws (e.g. injection) |
| **Security Hotspots** | Security-sensitive code that needs human review to confirm safe/unsafe (e.g. hardcoded secrets, weak crypto, debug flags) |
| **Code Smells** | Maintainability issues (dead code, duplicated literals, overly complex functions, etc.) |
| **Duplications** | Copy-pasted code instead of reused |
| **Coverage** | How much of the code is exercised by tests |

Bugs/Vulnerabilities/Code Smells all fall under **Issues**; Security Hotspots
are tracked separately and require manual triage (mark Safe/Fixed) in the
SonarQube dashboard rather than being auto-resolved by code changes alone.

## Metrics we've implemented

The quality gate evaluates only **new code** — changes since a fixed
baseline point, not necessarily just the latest push — rather than the
whole legacy codebase, against four conditions:

| Condition | Threshold |
|---|---|
| New code coverage | at least 80% |
| New duplicated lines | at most 3% |
| New Security Hotspots reviewed | 100% |
| New Bugs/Vulnerabilities/Code Smells | 0 |

If any condition fails, the gate fails and the pipeline stops before
building or pushing anything.

## Negative testing we've done

To confirm the pipeline actually catches problems (not just a green rubber
stamp), we deliberately committed known-bad code, clearly marked as
intentional test code, and watched the gate react:

**Round 1 — security issues**, all landed as **Security Hotspots**, not
Issues. The gate failed because none had been reviewed yet.

| Vulnerability | In plain terms |
|---|---|
| SQL Injection | User input pasted directly into a SQL query instead of using safe parameters |
| OS Command Injection | User input passed straight into a shell command |
| Weak Password Hashing | Passwords hashed with MD5, which is fast and easily cracked |
| Insecure Random Token Generation | Session tokens generated with a predictable random function, not a secure one |
| Debug Mode Enabled | Flask's debug mode left on, which can expose a code-execution console if reachable |
| Hardcoded Credential | A password written directly into the source code instead of a secret |

**Round 2 — bugs, code smells, duplication**. SonarQube reported this as
1 Bug, 6 Code Smells, and a duplication percentage well over the allowed
threshold.

| Issue | In plain terms |
|---|---|
| Mutable Default Argument | A function's default value is a shared list, so leftover data quietly carries over between unrelated calls |
| Always-True Comparison | A condition that compares a value to itself, so it's always true and does nothing useful |
| Bare Exception Handler | Catches every possible error without saying which one, hiding real problems |
| Unused Variable | A variable is created but never used anywhere |
| Leftover TODO Comment | A comment marking unfinished work left in the code |
| Copy-Pasted Function | An existing function duplicated instead of reused, so a fix in one place won't apply to the other |

It also caught one issue we didn't plant on purpose — a repeated string
literal that only became a problem once our new code added a third use of
it — confirming it's genuinely analyzing the code, not just matching what
we expected.

In both rounds the gate failed as expected, and the build/push step never
ran — proof the gate actually blocks non-compliant code from shipping, not
just reports on it after the fact.
