# ICM Credit

icm-studio applies the Interpretable Context Methodology (ICM) by Jake Van Clief.

- Paper: https://arxiv.org/abs/2603.16021
- Origin repo: https://github.com/RinDig/Content-Agent-Routing-Promptbase, the content system ICM grew out of.
- `ICM_LICENSE`: the upstream MIT license, unchanged.

ICM is also called the Model Workspace Protocol (MWP).

## What We Took

- Folders are the agent architecture.
- One stage does one job.
- Each stage reads plain files as input and writes plain files as output.
- A person reviews the work between stages.

## Where The Live Rules Are

- [`_core/CONVENTIONS.md`](../../CONVENTIONS.md) is how this repo applies ICM.
- [`AGENTS.md`](../../../AGENTS.md) is where agents start.
