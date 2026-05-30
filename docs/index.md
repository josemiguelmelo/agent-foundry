---
hide:
  - navigation
  - toc
  - title
---

<div class="af-home" markdown="1">

<section class="af-hero" markdown="1">

<div class="af-hero__content" markdown="1">

<span class="af-hero__tagline">Install once. Use everywhere.</span>

<h1 class="af-hero__title">agent-foundry</h1>

<p class="af-hero__subtitle">Install skills, agents, and MCP configs into the AI tools you already use — from one registry, one CLI.</p>

<div class="af-hero__actions" markdown="1">

[Get started :octicons-arrow-right-24:](user/getting-started.md){ .md-button .md-button--primary }
[Browse plugins :octicons-package-24:](plugins/index.md){ .md-button }

</div>

<p class="af-hero__meta">Open source · Apache-2.0 · <a href="https://github.com/josemiguelmelo/agent-foundry">GitHub</a></p>

</div>

<div class="af-terminal" markdown="1">

<div class="af-terminal__chrome">
<span class="af-terminal__dot af-terminal__dot--red"></span>
<span class="af-terminal__dot af-terminal__dot--yellow"></span>
<span class="af-terminal__dot af-terminal__dot--green"></span>
<span class="af-terminal__title">terminal</span>
</div>

```bash
# Install the CLI
pipx install git+https://github.com/josemiguelmelo/agent-foundry.git

# Install a plugin
agent-foundry install-plugin cursor-cli git

# Or install a single skill
agent-foundry install skill cursor-cli git:commit --in-project
```

</div>

</section>

<section class="af-strip" markdown="1">

<p class="af-strip__label">Works with</p>
<div class="af-strip__items">
<span class="af-chip">Claude Code</span>
<span class="af-chip">Codex</span>
<span class="af-chip">Copilot CLI</span>
<span class="af-chip">Cursor IDE</span>
<span class="af-chip">Cursor CLI</span>
</div>

</section>

<section class="af-section" markdown="1">

<div class="af-section__header">
<h2 class="af-section__title">How it works</h2>
<p class="af-section__lead">Three steps from zero to a working plugin in your editor or CLI.</p>
</div>

<div class="af-steps">

<div class="af-step" markdown="1">

<span class="af-step__num">1</span>
<h3 class="af-step__title">Install the CLI</h3>
<p class="af-step__text">One command via pipx. No global Python pollution.</p>

</div>

<div class="af-step" markdown="1">

<span class="af-step__num">2</span>
<h3 class="af-step__title">Pick a provider</h3>
<p class="af-step__text">Target Claude, Codex, Copilot, or Cursor — globally or per project.</p>

</div>

<div class="af-step" markdown="1">

<span class="af-step__num">3</span>
<h3 class="af-step__title">Install what you need</h3>
<p class="af-step__text">Full plugin bundles, or individual agents, skills, and MCP configs.</p>

</div>

</div>

</section>

<section class="af-section" markdown="1">

<div class="af-section__header">
<h2 class="af-section__title">Why agent-foundry</h2>
<p class="af-section__lead">Built for teams shipping AI workflows across multiple tools.</p>
</div>

<div class="grid cards af-benefits" markdown>

-   :material-package-variant:{ .lg .middle } __Registry-first__

    ---

    Curated plugins with validation built in. No copy-paste configs.

-   :material-swap-horizontal:{ .lg .middle } __One CLI, five providers__

    ---

    Same workflow whether you use Cursor, Claude Code, Codex, or Copilot.

-   :material-filter-variant:{ .lg .middle } __Install at any granularity__

    ---

    Full plugins, single skills, individual agents — you choose.

-   :material-source-branch:{ .lg .middle } __Your repos, your rules__

    ---

    Install from the public registry or any git repo with a compatible layout.

</div>

</section>

<section class="af-section" markdown="1">

<div class="af-section__header">
<h2 class="af-section__title">Choose your path</h2>
<p class="af-section__lead">New here? Start with Getting Started. Building plugins? Head to Contributing.</p>
</div>

<div class="grid cards af-paths" markdown>

-   :material-rocket-launch:{ .lg .middle } __Getting Started__

    ---

    Install the CLI and add your first plugin in minutes.

    [Start here :octicons-arrow-right-24:](user/getting-started.md)

-   :material-console:{ .lg .middle } __CLI Reference__

    ---

    Every command, flag, and provider option in one place.

    [View commands :octicons-arrow-right-24:](user/cli-reference.md)

-   :material-puzzle:{ .lg .middle } __Plugin catalog__

    ---

    git, software-development-agents, project-management, and more.

    [Browse plugins :octicons-arrow-right-24:](plugins/index.md)

-   :material-hand-heart:{ .lg .middle } __Contributing__

    ---

    Create plugins, improve the CLI, and open pull requests.

    [Join in :octicons-arrow-right-24:](contributors/contributing.md)

</div>

</section>

<section class="af-cta" markdown="1">

<h2 class="af-cta__title">Ready to install your first plugin?</h2>
<p class="af-cta__text">The getting started guide walks you through prerequisites, install, and your first command.</p>

[Get started :octicons-arrow-right-24:](user/getting-started.md){ .md-button .md-button--primary }

</section>

</div>
