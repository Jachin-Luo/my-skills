---
name: my-skills
description: List, summarize, and help users browse the actively installed skills available in an AI platform or local skill directories. Use when the user asks what skills are installed, available, active, personally installed, usable, or how to trigger/use their skills; especially for prompts like "我有哪些 skill", "列出已安装技能", "show my skills", "available skills", "skill list", or "how do I use my skills".
---

# My Skills

Use this skill to show the user the skills they can actively use in the current AI platform from a static catalog.

## Core Behavior

1. Prefer the static catalog at `catalog/skills.json` when answering normal "what skills do I have?" requests.
2. Do not scan skill directories on every trigger.
3. Rebuild the static catalog only when the user asks to initialize, refresh, update, add, remove, or resync skills.
4. Exclude built-in/system skills by default so the answer focuses on user-installed or actively added skills.
5. Present results in a compact table with parent skill, skill name, short purpose, trigger examples, and source/status when nested skills exist.
6. Offer practical next prompts the user can copy, such as `Use $skill-name to ...`.

## What Counts As Actively Installed

Include:

- Skills in user-managed skill folders, such as `~/.codex/skills`, `~/.agents/skills`, workspace skill folders, or configured skill roots.
- Skills explicitly listed by the current AI platform as available to the user.
- Plugin-provided skills only when the user asks for all available skills, not only personally installed skills.

Exclude by default:

- `.system` skills.
- Bundled platform internals.
- Duplicate copies of the same skill name; keep the user-managed copy first.

For nested skills, treat the nearest ancestor folder that also contains a `SKILL.md` as the parent skill. For example, `deep-analysis/investor-panel/SKILL.md` should be shown as parent `deep-analysis` and skill `investor-panel`.

If the platform exposes only a skill list and not filesystem paths, use that list and clearly mark the source as "platform context".

## Fast Workflow

When the user asks to view skills:

1. Read `catalog/skills.json` or run `python scripts/list_skills.py show`.
2. Use the catalog contents to answer. Do not update it unless the user asked for init/update/refresh or mentioned a skill install/removal.
3. If the catalog is missing, initialize it:

```bash
python scripts/list_skills.py init
```

4. If a skill was added or removed, update it:

```bash
python scripts/list_skills.py update
```

5. If the script cannot infer roots, pass likely roots explicitly:

```bash
python scripts/list_skills.py update --root ~/.codex/skills --root ~/.agents/skills
```

6. Summarize by category only when obvious from names/descriptions. Do not invent categories.
7. Mention any skipped system/plugin skills only briefly, for example: "已隐藏内置/system skills，可要求我显示全部。"

## Output Shape

Prefer Chinese when the user asks in Chinese.

Recommended concise format:

```markdown
我找到了 N 个主动安装的 skills：

| 父 Skill | Skill | 用途 | 触发/使用方式 |
|---|---|---|---|
| deep-analysis | investor-panel | ... | `Use $investor-panel to ...` |
| - | my-skill | ... | `Use $my-skill to ...` |

常用问法：
- `Use $skill-name to ...`
- `列出所有 skill，包括内置和插件`
- `按用途给我的 skills 分组`
```

For long lists, group by source first, then show the highest-signal description for each skill.

## Script

Use `scripts/list_skills.py` to initialize, update, or display the static catalog. It:

- Reads `catalog/skills.json` by default with `show`.
- Rebuilds `catalog/skills.json` with `init` or `update`.
- Recursively finds `SKILL.md` only during init/update/scan.
- Parses `name` and `description` from YAML frontmatter.
- Detects nested child skills from the nearest parent directory that also has `SKILL.md`.
- Excludes `.system`, plugin cache folders, and hidden/system roots unless `--include-system` is used.
- Emits Markdown, JSON, or TSV.

Examples:

```bash
python scripts/list_skills.py show --format markdown
python scripts/list_skills.py init
python scripts/list_skills.py update --root /path/to/skills --root /another/root
python scripts/list_skills.py scan --format json --include-system
```

If Python is unavailable, read `catalog/skills.json` directly for normal viewing. Update the catalog manually after adding or removing skills by following the same inclusion rules.
