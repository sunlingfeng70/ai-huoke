# 模型调用走 OpenAI 兼容 HTTP，端点与模型名从环境变量读

判定通过 `requests` 直接向 OpenAI 兼容的 `/chat/completions` 端点发一次 HTTP 请求完成。API key、base URL、模型名全部从环境变量读取，默认指向已在本机配好的火山方舟（`ARK_API_KEY`）。不通过 `claude` / `opencode` / `codex` 这些已安装的 CLI 子进程调用模型。

选直连 HTTP 而非 agent CLI，决定性理由是**输出可约束**：判定要稳定返回意向档、判定理由、开场白三个字段，HTTP 接口可以用 JSON 输出格式约束并直接解析，而 agent CLI 的 stdout 格式不受保证，从里面抠 JSON 是另一类麻烦。其次是吞吐——ADR-0008 规定每批重判全部历史线索，几百到几千个评论者逐个起一次 agent 会话，开销与耗时都不可接受。

把端点与模型名放进环境变量而非写死，是因为这个项目的判定质量与成本直接挂在模型选择上，换模型的概率很高；而这么做的代码量与写死几乎相同，只是把供应商从代码里挪到了配置里。

依赖上没有新增负担：`requests` 在系统 Python（3.9.6）里已可用，而 `openai` 与 `anthropic` 两个包都装不上——这也顺带排除了用官方 SDK 的选项。注意系统 Python 是 3.9，新代码需要 `from __future__ import annotations` 才能使用 `dict[str, str]` 这类注解，取数层脚本已是这么做的。
