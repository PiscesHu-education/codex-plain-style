---
name: code-style
description: 写代码、改代码、做网页或应用界面时使用的编码规范。遇到 Codex 在工作中确实要写或改代码（脚本、工具、网页、小应用、界面样式）时使用；纯文档、教研、配置口语任务不触发。
---

# 编码规范

只在这次任务真的要写或改代码时读。这份规范原本写在基础提示词里，因为多数写作和文档任务用不到，单独抽出来，避免无关任务被代码规范带偏语气。

## 前端与界面

做带界面的网页或应用时：

- 选视觉素材时，一般优先用贴合项目风格和用途的写实图片，来自 ImageGen 或图片搜索。用户明确要 SVG 时才用 SVG。
- 只在文字确实提供用户需要的信息、帮助导航或操作、或满足明确的内容要求时才加文字。去掉装饰性编号、填充徽章、重复标题，以及只是复述界面已经说清楚的内容的解释性文案；必要标签、说明和状态反馈要保留。

以下是备选字体，合适时可以用。用户指定了字体，或项目已有字体体系，就按已有的来。

字体列表：Archivo Black, Archivo Narrow, Asul, Atkinson Hyperlegible Next, Barlow, Barlow Condensed, Barlow Semi Condensed, Baskervville, Bitcount Prop Single, Bricolage Grotesque, Castoro, Chivo, Cinzel, Climate Crisis, Cormorant Garamond, Cossette Texte, Courier Prime, Crimson Text, Cutive Mono, DM Sans, DM Serif Text, Explora, Fahkwang, Geist, Germania One, Gloock, Hedvig Letters Sans, Hedvig Letters Serif, IBM Plex Mono, Instrument Sans, Instrument Serif, Inter, Jacquard 12, Kantumruy Pro, Lexend, Manufacturing Consent, Martian Mono, Montagu Slab, Mulish, Nanum Myeongjo, National Park, Neuton, News Cycle, Nunito, Ojuju, Old Standard TT, Overpass, Playfair Display, PT Serif, Quicksand, Radley, Rethink Sans, Roboto, Rubik, Scoutie Sans, Source Sans 3, Space Mono, Spectral, STIX Two Text, UnifrakturMaguntia, Work Sans, Workbench, Xanh Mono, Young Serif, Zalando Sans Expanded.

## 写代码本身

最高要求是正确、完整地把用户交代的功能做出来。代码要好读，并且从用户实际使用的入口验证结果符合预期。写代码时按这些规则：

(a) 改动要通过功能正常的入口跑通，并保持已有调用方依赖的行为，除非这次任务本来就要改那个行为。覆盖支持的输入范围，包括改动之前产生的数据。如果操作可能中途失败、被重试或并发执行，保证最终状态一致。
(b) 能复用用户项目里已有的逻辑就复用。已有的类、方法、表示方式和 API 只要还能保证正确，就用它们。合并或删除代码之前，保持调用方依赖的行为，除非任务要求改。
(c) 除非用户要求、项目规范要求，或者需要专门测某个现有测试抓不到的回归，否则不新加测试。
(d) 用户要求的交付物一个不少，而且要能用、符合用户的规范。用户没要求的产物不要顺手做，比如额外文件、部署改动、文档重写、格式大改、可选功能、配置调整。也不留用不上的辅助函数或状态。
(e) 代码要人能读懂。不能靠少写几行、短变量名、压缩格式或密集的一行式写法来代替简洁。注释和变量名要让人看得懂。把多个分支、条件或隐含假设塞进一个表达式，算过度复杂。
(f) 避免不必要的圈复杂度。如果新加的 `if`、`for`、`while`、`case`、条件运算符和分支会降低可维护性，就不要加。
(g) 避免不必要的间接和抽象。辅助函数、工具函数、类抽象即使不增加分支，也会增加理解成本。
