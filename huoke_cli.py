#!/usr/bin/env python3
"""AI 原生获客工具 —— 从小红书评论中识别想学 AI 的人。

用法：
    python huoke_cli.py <来源关键词>
"""

from __future__ import annotations

import sys
from pathlib import Path

from huoke import Comment, Judgement, Note, run_batch


def fake_fetch(keyword: str) -> list[Comment]:
    note_a = Note(
        note_id="demo_a",
        title=f"搜索「{keyword}」的示例笔记 A",
        url="https://www.xiaohongshu.com/explore/demo_a?xsec_token=demo",
    )
    note_b = Note(
        note_id="demo_b",
        title=f"搜索「{keyword}」的示例笔记 B",
        url="https://www.xiaohongshu.com/explore/demo_b?xsec_token=demo",
    )

    return [
        Comment("c1", "u_eager", "想转行的小张", "零基础想学，有推荐的课吗", "1700000000", note_a),
        Comment("c2", "u_maybe", "路过的猫", "码住", "1700000001", note_a),
        Comment("c3", "u_noise", "爱玩梗的人", "哈哈哈哈哈", "1700000002", note_b),
        Comment("c4", "u_peer", "AI培训老王", "我们机构也开这课", "1700000003", note_b),
    ]


def fake_judge(nickname: str, comments: list[Comment]) -> Judgement:
    judgements = {
        "u_eager": Judgement(
            tier="高意向",
            reason="明确说「零基础想学，有推荐的课吗」，直接求课程推荐。",
            opener="看到你想从零开始学 AI，方便聊聊你的基础和目标吗？",
        ),
        "u_maybe": Judgement(
            tier="潜在意向",
            reason="只留了「码住」，有兴趣信号但表述模糊。",
            opener="看到你收藏了这条，是想系统学一下 AI 吗？",
        ),
        "u_noise": Judgement(
            tier="不相关",
            reason="只是玩梗，与 AI 学习无关。",
            opener="",
        ),
        "u_peer": Judgement(
            tier="排除",
            reason="自称「我们机构也开这课」，是同行。",
            opener="",
        ),
    }
    return judgements[comments[0].user_id]


def main() -> None:
    if len(sys.argv) < 2:
        print("用法: python huoke_cli.py <来源关键词>", file=sys.stderr)
        sys.exit(1)

    keyword = sys.argv[1]
    result = run_batch(keyword=keyword, fetch=fake_fetch, judge=fake_judge)

    output_path = Path(f"{keyword}_leads.md")
    output_path.write_text(result.markdown, encoding="utf-8")

    print(f"✅ 名单已保存至: {output_path.absolute()}")
    print(f"   线索总数: {len(result.leads)}")
    print(f"   高意向: {sum(1 for l in result.leads if l.tier == '高意向')}")
    print(f"   潜在意向: {sum(1 for l in result.leads if l.tier == '潜在意向')}")


if __name__ == "__main__":
    main()
