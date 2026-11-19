# codex-plain-style

如果你请 Codex 写说明或回消息，它却总像在写技术交接，这个项目提供了一套可以在本机试用的中文写作规则。它改的是 Codex 收到的提示词，不改模型。例如，让它把“已 read-back，gate passed”写成“保存后重新打开核对过，和改的内容一致”：做了什么、查到什么都还在，读者不用先懂行话。

| 你想做什么 | 从这里开始 |
|---|---|
| 在自己的 Codex 上试用 | 看[安装与预览](#用起来)。可以先看生成的提示词，再决定是否启用。 |
| 按自己的工作习惯改规则 | 看[中文规则](rules/zh.rules.md)和[通用配置](rules/profiles.toml)。自己的职业背景和示例可以只保存在本机。 |
| 用这套方法改别的 AI 助手 | 看[提示词诊断指南](skill/prompt-diagnose/SKILL.md)，从一句不满意的回复追到具体规则。 |
| 看改写到底有没有用 | 看[13 道评测题](eval/questions)、[评分方法](eval/method.md)和[两轮结果](eval/results.md)。 |

## 为什么改提示词

Codex 0.169 的 `gpt-6.2-*` 基础提示词有 27,750 个字符，其中给语气定调、限定措辞的规则占了很大比重：区分大小写的 `Do not` 出现 31 次，平均 895 个字符就有一条（不分大小写则 38 次；`eval/stats.py` 用的是不分大小写的口径），而 `gpt-6.1-sol` 的模板是 21,524 个字符里 15 条、平均 1,435 个字符一条。其中一大块是讲前端和编码风格的，写文档、回消息、整理资料时也用不上，却会一起生效。结果是回答变得像代码交接：短句、名词堆叠、术语多、防御性强，该直说的地方绕一圈说"这不代表……"。

从 6.1 到 6.2，模板长了约 6,200 个字符，新增的很大一部分是限制措辞的禁令，同长度的禁止性表达密度上去了。这套方案按一条原则改：**在语言风格方面，对模型的限制越少，越可能写出好文字。** 这不是凭感觉的判断：约束写得越细，越容易互相打架，也越容易盖过任务本身的要求；能说明"要达到什么"的规则，比说明"不许怎么写"的规则更稳。落实时把约束分成四类，分别处理：

| 约束类型 | 处理 | 理由 |
|---|---|---|
| 措辞与形式（不用分号、不许用对比句式、每条一行） | 删掉或放宽 | 这些规则推着模型写得机械，对好文字没有贡献 |
| 事实诚实（做了什么、没做什么、没验证的要说） | 保留，收成一条 | 这是可靠性的底线，保留但不要写成防御性口吻 |
| 交付格式（文件链接、空白行、渲染规则） | 保留，当接口约定写 | 应用要靠它正确渲染，不涉及语气 |
| 受众与目的（读者是谁、这一问要什么） | 保留并加强 | 这是写好文字真正的抓手 |

## 它做了什么

构建脚本从本机的 Codex 模型缓存里取出原始基础提示词，做八处定点修改，再把一份中文规则追加到末尾：

- 改了五段写作要求：先想读者和问题类型、用平实的语言；把"不要主动提建议"改成"遇到真问题就简短说，并给出建议"；放宽绝对化的对比句式禁令；去掉对分号的死规定、允许表格和完整段落；最终回复的诚实要求从"措辞谨慎"改成"事实严谨"。
- 加了两段：改动前先想会牵动哪些地方；分清"讨论或解释"和"动手改"。
- 把 `Frontend Design Guidance` 和 `Coding Style` 两节（约 3,900 字符）移出基础提示词，换成一句指针，指向 `skill/code-style/SKILL.md` 里的编码规范。不写代码的任务不再被代码规范影响。
- 末尾追加中文写作规则（`rules/zh.rules.md`），覆盖受众判断、平实语言、事实严谨、整体思维、什么时候直接做什么时候先问。

仓库里不存放 OpenAI 的原版提示词。脚本每次从你机器上 Codex 已经下载的缓存里取，OpenAI 更新模板后重新构建即可，也避免了转载别人版权文本的问题。

## 证据

仓库里带了一套可复现的对照评测（`eval/`）：同一批 13 道题、同一个模型、同一组参数，只换提示词文件，跑 A（上一版改版）、B（出厂模板）、C（当前版）三臂。方法是 `eval/method.md`，跑法、抽产物、盲评打包、汇总都做成了脚本（`run-arm.sh` / `extract.py` / `blind_pack.py` / `tally.py`），提示词的客观底数用 `eval/stats.py` 统计。

下面是原评测使用当时那份提示词得到的结果。公开版只保留通用配置，没有用它重跑评测。

评测跑了两轮，两张评分表回答两个不同的问题：

| 轮次 | 评分表 | 问的问题 | 结果（满分 156） |
|---|---|---|---|
| 第一轮 | `eval/rubric.md`，六维各 0—2 | 内容能不能用上 | B 156 / A 154 / C 154，饱和 |
| 第二轮 | `eval/rubric-v2.md`，四维各 0—3，三位盲评 | 读者会不会觉得更好用 | C 140 / A 134 / B 128 |

逐题分数、维度分项、限制说明都在 `eval/results.md`。两轮的联合结论是：**内容三家一样，摆法 C > A > B。改版改的是编排层，不是内容层。** 第一轮因为不评编排所以打平，第二轮因为评编排所以拉开——单看任何一轮都会得到片面结论，所以两轮都写在仓库里。

用这套证据时，有三类结论**不能**从中得出：模型变聪明了（提示词不动权重）、效率更高了（没测）、多轮对话更好了（单轮题测不到）。

这三条边界比分数本身更值得划线。这套评测只能回答"输出有没有变得更好用"，回答不了"模型有没有变聪明"。提示词改的是取什么、先给哪个、怎么分块、哪里停；句子质量来自模型权重，换提示词不会动它。写文章、写说明时把这两层分开说，否则读者会对提示词抱错期望。

## 把方法用到别的提示词上

同样这套流程不只适用于本仓库这套规则。`skill/prompt-diagnose/SKILL.md` 是这个仓库最大的改造经验的抽象：从一个模糊的抱怨（"太啰嗦""总在推卸"）出发，先判断问题属于提示词能处理的那一层，再在提示词里定位是哪类规则导出的，按四类规则分别处理，最后用 `eval/` 里的方法验证。拿去改软件 Agent、自定义 GPT、内部助手的系统提示词都可以。

## 用起来

需要 Git、Python 3，以及已经在本机生成模型缓存的 Codex。下面的命令按 macOS / Linux 写；本项目用 Codex 0.169 的模板验证过。

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

重新开一个对话生效。验证方法：新对话的首个回合结束后，打开 `~/.codex/sessions/` 下最新的 `rollout-*.jsonl`，看第一行 `session_meta` 里的 `base_instructions.provenance`，显示为文件路径就说明替换成功。要还原，把这行恢复成原值（原先没有就删掉），再开一个新对话。

把 `skill/code-style/SKILL.md` 复制到 `~/.codex/skills/code-style/`（CLI 用 `~/.agents/skills/code-style/`），编码指针才找得到目标。

### 换成你自己的背景和规则

`rules/zh.rules.md` 里的 `{{identity}}`、`{{dependency_map}}`、`{{ask_first}}` 等占位符由 `rules/profiles.toml` 里的档案填充。公开版只内置 `generic` 通用档案，适合写作、文档和研究任务。

自己写一个档案放进 `rules/profiles.local.toml`（已 gitignore），然后：

```bash
python3 scripts/build.py --profile 你的档案名
```

规则文件本身可以直接改。想验证改动和预期完全一致，用 `--verify`：

```bash
python3 scripts/build.py --profile generic --verify ~/.codex/prompts/codex-plain-style.md
```

## OpenAI 更新模板之后

八处修改都靠锚点定位（段落开头几个词）。模板大改后构建会直接报错并指出哪一处没找到，不会悄悄产出半改的文件。报错时对照新的模板修 `.patch/plain-style.edits.json` 里的 `anchor` 和 `new` 字段即可。如果新版把这两节编码规范换了写法，同步更新 `skill/code-style/SKILL.md`。

## 适用范围与已知限制

- 这改的是客户端发给模型的系统提示词，不涉及模型权重，也不改服务器端的任何配置。其他入口（网页版、API）不受影响。
- 桌面端会用自己的 developer instructions 覆盖 `config.toml` 里的 `developer_instructions`，所以中文规则必须放在生成文件的末尾，不能只写在配置里。
- 效果证据来自 `eval/` 里的 13 题对照评测加日常使用对比。13 道单轮题覆盖不了多轮、带工具、中途改需求的场景；评分员三人的偏好也不等于真实用户分布。建议保留原版，用 `--verify` 和备份文件随时退回。
- `code-style` 抽出去以后，纯代码任务要靠 skill 加载来补回规范。如果模型没有读 skill，编码规范就不在上下文里。

## English

A prompt-level fix for Codex's writing style. The 6.2 base instructions carry heavy style policing (31 "Do not" in 27,750 characters, one every 895, against 15 in 21,524 for 6.1) plus a large frontend/coding section that fires on non-coding work, which leaves replies terse, jargon-dense and defensive. This repo extracts the template Codex already downloaded into `~/.codex/models_cache.json`, applies eight anchored edits that relax style policing, replace the coding sections with a pointer to a skill, and append plain-language user rules, then writes the result to a file referenced by `model_instructions_file`. No proprietary template text is redistributed; the build always starts from the local cache. Built with `python3 scripts/build.py`, verified against a reference build with `--verify`. Evidence: a reproducible 13-question, three-arm comparison in `eval/` (two rubrics: content usability saturates at B 156 / A 154 / C 154; subjective usability separates them at C 140 / A 134 / B 128). Single-turn questions only; no multi-turn, tool-use or efficiency measurement.

## License

MIT. OpenAI's base instruction template belongs to OpenAI and is never stored in this repository; it is read from the local Codex cache at build time.
