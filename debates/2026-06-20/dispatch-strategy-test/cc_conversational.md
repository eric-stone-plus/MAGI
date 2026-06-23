This is a real gap, and it's worth addressing — but the urgency depends on your threat model. Let me break it down.

## Why it matters

Your debate system has a specific structural property: five agents cross-checking each other over three rounds. That's a redundancy architecture. But redundancy only buys you something if you know what failure modes you're defending against. Right now you have a mechanism without a claim. You can't say "this system tolerates up to *k* compromised agents" because you've never defined what *compromised* means, what *k* is, or what *tolerates* means in your context.

The concrete risks of leaving this undefined:

- **You can't reason about robustness.** If someone asks "what happens if two of the five agents are adversarial?" you don't have an answer. You have vibes.
- **You can't prioritize fixes.** Without an adversary model, every possible concern sounds equally urgent — or equally ignorable. Neither is useful.
- **You can't audit.** If you ever need to demonstrate the system's integrity (to users, to yourself, to a regulator), "we have five agents" isn't an argument. "We tolerate *f* Byzantine failures under these assumptions" is.

## What the adversary model actually looks like

You don't need a 40-page threat doc. You need answers to three questions:

**1. What are you protecting?**
The integrity of the debate's output — that the final decision reflects genuine multi-perspective reasoning, not a systematic failure or manipulation.

**2. What are the failure modes?**
At minimum, categorize these:

- **Independent failures** — an agent hallucinates, misunderstands the prompt, has a bad context window. These are the easy ones; your cross-checking probably handles them.
- **Correlated failures** — all agents share the same base model, same system prompt template, same training data biases. Cross-checking catches nothing here because the errors are correlated. This is the real risk.
- **Adversarial inputs** — prompt injection through the debate content itself, where one agent's output poisons another's input in later rounds.
- **Protocol gaming** — an agent learns (or is prompted) to produce outputs that satisfy the gate criteria without actually doing useful reasoning. Goodhart's law applied to your verification steps.

**3. What's your actual tolerance?**
This is the business decision. Are you building a system where a wrong answer is embarrassing, or one where it's dangerous? The security model scales with consequences.

## What I'd actually do

Don't boil the ocean. Write a one-page security model that covers:

- **Assumptions**: "We assume the orchestrator and gate logic are trusted. We assume individual agents may fail independently with probability *p*. We assume [0/1/2] agents may be adversarially prompted via input content."
- **Guarantees**: "Under these assumptions, the system produces a correct output with probability ≥ *X*" — or more honestly, "the system detects a single-agent failure with probability *Y*."
- **Known limitations**: "Correlated failures across same-model agents are not detected. The system does not defend against a compromised orchestrator."

That last point matters. Your orchestrator — whatever code runs the gates and routes messages between rounds — is your trusted computing base. If that's compromised, nothing else matters. Make that explicit.

## Is it urgent?

If this is a research tool or internal prototype: low urgency, but write the one-pager now while the design is fresh. It'll take 30 minutes and it'll save you from the "are we even asking the right questions?" spiral later.

If this is heading toward production or handling consequential decisions: it's a blocker. You shouldn't ship a debate system that claims to improve reliability without being able to articulate what it's reliable *against*.

The fact that you're asking the question means you already know the answer. It's not a question of *whether*, it's *how much formalism*. Start with the one-pager. If you want, I can draft it based on your system's specifics.
