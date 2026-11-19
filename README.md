# codex-plain-style

[中文说明](#为什么改提示词) · [English overview and quick start](#english)

如果你请 Codex 写说明或回消息，它却总像在写技术交接，这个项目提供了一套可以在本机试用的中文写作规则。它改的是 Codex 收到的提示词，不改模型。例如，让它把“已 read-back，gate passed”写成“保存后重新打开核对过，和改的内容一致”：做了什么、查到什么都还在，读者不用先懂行话。

| 你想做什么 | 从这里开始 |
|---|---|
| 在自己的 Codex 上试用 | 看[安装与预览](#用起来)。可以先看生成的提示词，再决定是否启用。 |
| 按自己的工作习惯改规则 | 看[中文规则](rules/zh.rules.md)和[通用配置](rules/profiles.toml)。自己的职业背景和示例可以只保存在本机。 |
| 用这套方法改别的 AI 助手 | 看[提示词诊断指南](skill/prompt-diagnose/SKILL.md)，从一句不满意的回复追到具体规则。 |
| 看改写到底有没有用 | 看[13 道评测题](eval/questions)、[评分方法](eval/method.md)和[两轮结果](eval/results.md)。 |

## 为什么改提示词

Codex 0.169 的 `gpt-6.2-*` 基础提示词有 27,750 个字符，其中给语气定调、限定措辞的规则占了很大比重：直接写着 `Do not` 的禁令就有 31 条，平均每 895 个字符出现一次；相比之下，`gpt-6.1-sol` 的模板共 21,524 个字符，同类禁令只有 15 条，平均 1,435 个字符才出现一次（以上按区分大小写统计；如果不区分大小写，新版共有 38 条，`eval/stats.py` 采用的是这一口径）。此外，其中一大块是讲前端和编码风格的，写文档、回消息、整理资料时根本用不上，却会一起生效。结果是回答变得像代码交接：短句、名词堆叠、术语多、防御性强，该直说的地方绕一圈说“这不代表……”。

从 6.1 到 6.2，模板增加了约 6,200 个字符，其中很大一部分是限制措辞的禁令——不只是总字数变长了，同样篇幅里“不要这样、不许那样”的约束也密得多。这套方案按一条原则改：**在语言风格方面，对模型的限制越少，越可能写出好文字。** 这不是凭感觉的判断：约束写得越细，越容易互相打架，也越容易盖过任务本身的要求；能说明“要达到什么”的规则，比说明“不许怎么写”的规则更稳。落实时把约束分成四类，分别处理：

| 约束类型 | 处理 | 理由 |
|---|---|---|
| 措辞与形式（不用分号、不许用对比句式、每条一行） | 删掉或放宽 | 这些规则推着模型写得机械，对好文字没有贡献 |
| 事实诚实（做了什么、没做什么、没验证的要说） | 保留，收成一条 | 这是可靠性的底线，保留但不要写成防御性口吻 |
| 交付格式（文件链接、空白行、渲染规则） | 保留，只当格式规范来写 | 应用要靠它正确渲染，不涉及语气 |
| 受众与目的（读者是谁、这一问要什么） | 保留并加强 | 这是决定文字好不好读的关键 |

## 它做了什么

构建脚本会从本机的 Codex 模型缓存里取出原始提示词，先做八处定点调整，再在末尾补上一份中文写作规则：

- **改了 5 段写作要求**：先想清楚读者是谁、要解决什么问题，用平实的话表达；把“不要主动提建议”改成“发现真问题就简短指出并给建议”；放宽对“不是……而是……”这类对比句式的硬性禁令；去掉对分号的死规定，允许使用表格和完整段落；把最终回复的要求从“措辞保守谨慎”改成“事实交代清楚”。
- **加了 2 段提醒**：动手改动前先想清楚会影响哪些地方；分清用户是在“讨论或问原理”，还是让你“直接动手改”。
- **拆出 2 节编码规范（合并为 1 处替换）**：把 `Frontend Design Guidance` 和 `Coding Style`（共约 3,900 字符）移出基础提示词，原地只留一句提示，让模型在需要写代码时再去读取 `skill/code-style/SKILL.md`。这样不写代码时，回复就不会被代码规范带偏。
- **末尾追加中文写作规则**（`rules/zh.rules.md`）：覆盖受众判断、平实语言、事实严谨、整体思维，以及什么时候直接做、什么时候先问。

仓库里不存放 OpenAI 的原版提示词。脚本每次从你机器上 Codex 已经下载的缓存里取，OpenAI 更新模板后重新构建即可，也避免了转载别人版权文本的问题。

## 证据

仓库里带了一套可复现的对照评测（`eval/`）：同一批 13 道题、同一个模型、同一套参数，只替换提示词文件，分三组跑对照——A 组用上一版改写，B 组用原版出厂模板，C 组用当前版本。具体流程写在 `eval/method.md`，从批量运行、提取回答、打乱顺序打包供盲评，到最后汇总分数，都配了对应脚本（`run-arm.sh` / `extract.py` / `blind_pack.py` / `tally.py`）；提示词字数和禁令条数等基础数据由 `eval/stats.py` 统计。

下面是原评测使用当时那份提示词得到的结果。公开版只保留通用配置，没有用它重跑评测。

评测跑了两轮，两张评分表回答两个不同的问题：

| 轮次 | 评分表 | 问的问题 | 结果（满分 156） |
|---|---|---|---|
| 第一轮 | `eval/rubric.md`，六个维度各 0—2 分 | 内容能不能用上 | B 156 / A 154 / C 154（接近全满分，分不出高下） |
| 第二轮 | `eval/rubric-v2.md`，四个维度各 0—3 分，三位盲评 | 读者会不会觉得更好用 | C 140 / A 134 / B 128 |

逐题分数、维度分项、限制说明都在 `eval/results.md`。两轮合起来看，结论很明确：**三组给出的实质内容差不多，但组织和呈现方式上 C > A > B。这次改写改善的是“怎么把内容摆清楚”，不是“内容本身有多强”。** 第一轮只看内容有没有用，所以三组打平；第二轮开始评读起来顺不顺手，差距才拉开——单看任何一轮都会得到片面结论，所以两轮结果都保留在仓库里。

用这套证据时，有三类结论**不能**从中得出：模型变聪明了（提示词不动权重）、效率更高了（没测）、多轮对话更好了（单轮题测不到）。

这三条边界比分数本身更重要，必须先说清楚。这套评测只能说明“回复有没有变好读”，不能证明“模型变聪明了”。提示词能影响的是选哪些信息、先说哪部分、怎么分段、在哪里收尾；至于底层的表达功底和推理能力，取决于模型本身，换提示词改不了它。写文章、写说明时要把这两层分开说，否则读者会对提示词抱错期望。

## 把方法用到别的提示词上

同样这套流程不只适用于本仓库这套规则。`skill/prompt-diagnose/SKILL.md` 把这次改写提示词的经验总结成了通用流程：先从一句模糊的不满（比如“太啰嗦”“总在推卸责任”）出发，判断这个问题是不是靠改提示词就能解决；接着在原提示词里找出是哪类规则引起的，按前面说的四类约束分别处理；最后再用 `eval/` 里的方法验证效果。这套步骤同样适用于各类 AI Agent、自定义 GPT 或公司内部助手的系统提示词。

## 用起来

需要 Git、Python 3，以及已经在本机运行过一次的 Codex（这样本地才会有它下载好的模型提示词缓存）。下面的命令按 macOS / Linux 写；本项目用 Codex 0.169 的模板验证过。

```bash
git clone https://github.com/PiscesHu-education/codex-plain-style.git
cd codex-plain-style
python3 scripts/build.py --list          # 看缓存里有哪些模型和对应模板长度
python3 scripts/build.py --dry-run        # 预览完整提示词，不写入文件
```

决定试用后，再生成文件并查看它的完整路径：

```bash
python3 scripts/build.py
python3 -c 'from pathlib import Path; print(Path.home() / ".codex/prompts/codex-plain-style.md")'
```

把上一步输出的完整路径填到 `~/.codex/config.toml` 的顶层配置中。下面只是路径示例；如果已经有这个设置，先记下原值，再替换，不要重复添加：

```toml
model_instructions_file = "/Users/you/.codex/prompts/codex-plain-style.md"
```

再把 `skill/code-style/SKILL.md` 复制到 `~/.codex/skills/code-style/`（如果用 CLI，放到 `~/.agents/skills/code-style/`），这样写代码时 Codex 才能读到被拆出去的编码规范。

完成后，重新开一个对话即可生效。验证方法：新对话发完第一轮消息后，打开 `~/.codex/sessions/` 下最新的 `rollout-*.jsonl`，看第一行 `session_meta` 里的 `base_instructions.provenance`，显示为文件路径就说明替换成功。要还原，把配置里的这一行恢复成原值（原先没有就删掉），再开一个新对话。

### 换成你自己的背景和规则

`rules/zh.rules.md` 里的 `{{identity}}`、`{{dependency_map}}`、`{{ask_first}}` 等占位符由 `rules/profiles.toml` 里的配置方案（profile）填充。公开版只内置 `generic` 通用配置，适合写作、文档和研究任务。

自己写一个配置方案放进 `rules/profiles.local.toml`（已 gitignore），然后：

```bash
python3 scripts/build.py --profile 你的配置名
```

规则文件本身可以直接改。想验证改动和预期完全一致，用 `--verify`：

```bash
python3 scripts/build.py --profile generic --verify ~/.codex/prompts/codex-plain-style.md
```

## OpenAI 更新模板之后

脚本是按段落开头的关键词（锚点）来定位这八处修改的。模板大改后构建会直接报错并指出哪一处没找到，不会悄悄产出改了一半的残缺文件。报错时对照新的模板修 `.patch/plain-style.edits.json` 里的 `anchor` 和 `new` 字段即可。如果新版把这两节编码规范换了写法，同步更新 `skill/code-style/SKILL.md`。

## 适用范围与已知限制

- 这改的是客户端发给模型的系统提示词，不涉及模型权重，也不改服务器端的任何配置。其他入口（网页版、API）不受影响。
- Codex 桌面端会用内置的 `developer instructions` 覆盖你在 `config.toml` 里手动写的同类配置，所以中文规则必须直接拼到生成的提示词文件末尾，不能只写在配置文件里。
- 效果证据来自 `eval/` 里的 13 题对照评测加日常使用对比。13 道单轮题覆盖不了多轮、带工具、中途改需求的场景；三位评分人的口味也代表不了所有用户。建议保留原版，用 `--verify` 和备份文件随时退回。
- `code-style` 抽出去以后，纯代码任务要靠加载 skill 来补回规范。如果某次写代码时 Codex 没有触发读取这个 skill，那些编码规范就不会生效。

## English

**Plain-language writing for Codex.** If you ask Codex to explain a change and get a handoff full of jargon, these rules ask it to say what it did and what it checked. For example, “Read-back complete; gate passed” becomes “I reopened the saved file and checked that it matched the edit.” The included rules focus on Chinese writing. The method also works as a starting point for editing your own assistant’s instructions.

### Try it locally

You need Git, Python 3, and a Codex installation that has already downloaded its model cache. The template was tested with Codex 0.169. On macOS or Linux, run:

```bash
git clone https://github.com/PiscesHu-education/codex-plain-style.git
cd codex-plain-style
python3 scripts/build.py --dry-run
```

This previews the instructions without changing your settings. To use them:

1. Run `python3 scripts/build.py`. It generates a prompt file and prints its path.
2. Set `model_instructions_file` in `~/.codex/config.toml` to that file’s **absolute path**. If the setting already exists, note its old value before replacing it. See the [configuration example](config-examples/config-snippet.toml).
3. Copy the [coding skill](skill/code-style/SKILL.md) into your Codex skills directory under `code-style/SKILL.md`, then start a new chat. To switch back, restore the previous setting (or remove it if it was new) and start another chat.

To adapt the rules, start with the [generic profile](rules/profiles.toml). For the reasoning behind the edits, see the [prompt diagnosis guide](skill/prompt-diagnose/SKILL.md). The [evaluation results](eval/results.md) compare three prompt versions on 13 single-turn tasks. They report the original experiment, not a new evaluation of this public profile.

## License

MIT. OpenAI's base instruction template belongs to OpenAI and is never stored in this repository; it is read from the local Codex cache at build time.
