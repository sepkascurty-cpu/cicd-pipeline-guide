# Quiz — CI/CD Pipelines

Test yourself. Answers are hidden — no peeking.

---

**1.** Why is OIDC preferred over storing a cloud access key in GitHub Secrets?

<details><summary>Answer</summary>

OIDC issues short-lived, audience-scoped credentials per workflow run. A leaked
static key works until someone rotates it; a leaked OIDC token expires in
minutes and only carries the permissions of the assumed role.
</details>

**2.** Your team deploys 10× a day to a stateless API and regulators require
instant rollback. Which strategy fits best — rolling, blue/green, or canary — and why?

<details><summary>Answer</summary>

Blue/green: two identical environments, traffic flips in one step, rollback is
instant (flip back). Rolling is slower to roll back; canary is great for
risky changes but adds progressive-traffic complexity you don't need for a
binary "ship it / revert it" flow.
</details>

**3.** A deploy job runs `configure-aws-credentials` but the workflow has no
`permissions:` block at all. What breaks, and what's the minimal fix?

<details><summary>Answer</summary>

OIDC fails: GitHub only mints the OIDC token when the job (or workflow) has
`permissions: id-token: write`. Minimal fix:

```yaml
permissions:
  id-token: write
  contents: read
```
</details>

**4.** Where should the CVE image scan live in the pipeline — build, test,
gate, or deploy — and why?

<details><summary>Answer</summary>

Gate. Build is too early (image may change); deploy is too late (you're
already shipping). The gate exists to say "no" before promotion, so a failed
scan blocks staging, not production.
</details>

**5.** Name two concrete signals that should trigger an automatic rollback
during a canary deploy.

<details><summary>Answer</summary>

Any two of: elevated error rate (5xx) vs baseline, p99 latency SLO breach,
drop in successful-checkout / key-business-metric rate, failed synthetic
health checks, or new crash-looping pods. Rollback must be automated, not a
Slack message saying "someone look at this".
</details>

---

Score: 5/5 → you can review other people's pipelines. 3–4 → re-read the
strategy table. Below 3 → run `pipeline.py` on your own workflow and fix what
it flags.
