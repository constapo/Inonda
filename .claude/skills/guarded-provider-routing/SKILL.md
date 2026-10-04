---
name: guarded-provider-routing
description: Route an LLM/API task across ranked providers with hard cost, timeout and circuit-breaker guardrails. Use when writing or reviewing code that fails over between providers, enforces per-run spend limits, or shadow-tests cheaper models.
---

# Guarded provider routing

Pattern for routing a task across providers without runaway cost.

## Rules

1. **Budget before the call.** Estimate cost up front and cap `max_tokens` so a call cannot exceed what remains. Checking cost after the call only reports spend.
2. **One budget per run.** Track cumulative spend across every provider tried, including discarded results and shadow tests. Stop when the run budget is gone.
3. **Real timeouts.** Pass an `AbortSignal` into the request so the provider stops work and billing, not just the wait.
4. **Circuit breaker with recovery.** Reset failures on success, trip after `maxFailures` consecutive failures, and re-allow one probe call after a cooldown (half-open).
5. **Bounded attempts.** `maxAttempts` limits providers tried per run; do not call it "retries" if each provider is tried once.
6. **Shadow tests are budgeted and isolated.** Sample a small fraction, charge them to a separate budget, always `.catch`, and never send data to a second provider that policy does not allow.
7. **Fail closed.** If every provider is skipped or over budget, throw with the reason for each.

## Reference implementation

```ts
type Limits = { maxAttempts: number; maxCostPerRun: number; timeoutMs: number };

export async function routeTask(task: string, providers: Provider[], limits: Limits) {
  let spent = 0;
  const reasons: string[] = [];
  let attempts = 0;

  for (const p of rankByHistoricalPerformance(providers)) {
    if (attempts >= limits.maxAttempts) break;
    if (!p.breaker.allowRequest()) { reasons.push(`${p.name}: breaker open`); continue; }

    const remaining = limits.maxCostPerRun - spent;
    const maxTokens = Math.floor(remaining / p.costPerToken);
    if (maxTokens <= 0) { reasons.push(`${p.name}: no budget left`); break; }

    attempts++;
    try {
      const result = await p.execute(task, {
        maxTokens,
        signal: AbortSignal.timeout(limits.timeoutMs),
      });
      spent += calculateCost(p, result.tokens);
      p.breaker.recordSuccess();
      maybeShadowTest(task, result, getCheapestProvider(providers)); // sampled, budgeted, .catch inside
      return result;
    } catch (err) {
      p.breaker.recordFailure();
      reasons.push(`${p.name}: ${String(err)}`);
    }
  }
  throw new Error(`All providers failed or were skipped: ${reasons.join("; ")}`);
}
```

Adapt `Provider`, ranking and cost helpers to the codebase; keep the seven rules.
