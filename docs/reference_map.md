# Reference Map

These references were inspected as design inspiration. GeoSciLoop v0.1 uses original implementation code and does not copy source code from these projects.

| Source | URL | What it contributes | What GeoSciLoop borrows conceptually | What GeoSciLoop deliberately does differently | Source code used |
|---|---|---|---|---|---|
| Sakana AI Scientist v2 | https://github.com/sakanaai/ai-scientist-v2 | End-to-end agentic scientific loop with hypothesis, experiment, analysis, and writing stages. | Closed-loop artifact flow and explicit experiment management. | v0.1 is offline, deterministic, and does not execute LLM-written code or require API keys. | No |
| Sakana AI Scientist v1 | https://github.com/sakanaai/ai-scientist | Template-driven automated research framing. | The idea that research automation needs staged artifacts. | No claim of autonomous discovery; no manuscript automation. | No |
| Agent Laboratory | https://github.com/SamuelSchmidgall/AgentLaboratory and https://agentlaboratory.github.io/ | Human-assisted research workflow framing. | Stage separation between idea, implementation, and report support. | v0.1 uses deterministic rules and tests instead of live LLM agents. | No |
| OpenEarthAgent | https://github.com/mbzuai-oryx/OpenEarthAgent and https://arxiv.org/abs/2602.17665 | Tool-augmented geospatial agents with structured multi-step reasoning and validated tool trajectories. | Tool/validator separation and geospatial reasoning benchmarks. | No model training, no tool server, no large datasets, no web demo. | No |
| Earth-Agent | https://github.com/opendatalab/Earth-Agent | Earth-observation agent implementation reference. | Future inspiration for EO task decomposition. | Deferred until v0.1 offline artifacts and validators pass. | No |
| ThinkGeo | https://github.com/mbzuai-oryx/ThinkGeo and https://arxiv.org/abs/2505.23752 | Remote-sensing agent benchmark with step-wise and final-answer evaluation. | Layered evaluation and benchmark framing. | v0.1 evaluates a deterministic synthetic workflow, not general tool-use agents. | No |
| AutoGEEval | https://github.com/szx-0633/AutoGEEval and https://arxiv.org/abs/2505.12900 | Automated evaluation for GEE Python API code generation. | Pass/fail evaluation, error categories, and GEE adapter caution. | v0.1 does not require GEE projects, authentication, or LLM API keys. | No |
| AutoGEEval++ | https://arxiv.org/abs/2506.10365 | Multi-level geospatial code-generation evaluation on GEE. | Future benchmark ideas for optional GEE adapters. | Deferred; offline tests remain the baseline. | No |
| LLM-Geo | https://github.com/gladcolor/LLM-Geo | Autonomous GIS prototype with solution graphs, generated programs, maps, and case studies. | The need for logs, testing, and geospatial task decomposition. | v0.1 avoids live LLM code generation and emphasizes deterministic validation. | No |
| LLM-Find | https://github.com/gladcolor/LLM-Find | Geospatial data retrieval agent reference. | Future data-source search pattern. | Not included in v0.1 to avoid network and credential dependencies. | No |
| RS-Agent | https://github.com/intellisensing/rs-agent | LLM-driven remote-sensing intelligent agent reference. | Future remote-sensing agent framing. | No live LLM agent in v0.1. | No |
| Awesome Remote Sensing Agents | https://github.com/PolyX-Research/Awesome-Remote-Sensing-Agents | Survey/list of remote-sensing agent projects. | Landscape awareness and future comparison set. | v0.1 remains a narrow offline demo. | No |
| Google Earth Engine Python API tutorial | https://developers.google.com/earth-engine/tutorials/community/intro-to-python-api | GEE Python API, LST handling, authentication, scale/projection, cloud/missing-data caveats. | Future GEE adapter requirements and LST caveats. | GEE is deferred; v0.1 requires no authentication. | No |
| Google Earth Engine API | https://github.com/google/earthengine-api | Python and JavaScript bindings for Earth Engine. | Optional future adapter target. | Not a dependency of v0.1. | No |
| geemap | https://geemap.org/ and https://github.com/gee-community/geemap | Interactive geospatial analysis and visualization with GEE. | Future visualization and GEE workflow ideas. | No web UI or GEE dependency in v0.1. | No |

## Notes

- Reference availability can change. If a source cannot be fetched in a future session, update this table with the access status instead of inventing details.
- Conceptual borrowing here means architecture inspiration only; it does not imply code reuse.
