# Council — history and measurements

- The design is inspired by Ole Lehmann’s “Claude Council” and `karpathy/llm-council`; written here from scratch (issue #28), with no third-party code installed.
- The rationale for the design (models’ tendency to be sycophantic toward the person asking) comes from Anthropic, *Towards Understanding Sycophancy in Language Models*, 2023, arXiv:2310.13548.
- The small version (one subagent in the five roles plus the President) was measured in its first run, on 14/10/2026: about 90,000 tokens, under a minute. The full council is an estimate, not a measurement.
