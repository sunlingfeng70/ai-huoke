from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Note:
    note_id: str
    title: str
    url: str


@dataclass(frozen=True)
class Comment:
    comment_id: str
    user_id: str
    nickname: str
    content: str
    created_at: str
    note: Note


@dataclass(frozen=True)
class Judgement:
    tier: str
    reason: str
    opener: str


@dataclass(frozen=True)
class Lead:
    user_id: str
    nickname: str
    tier: str
    reason: str
    opener: str
    comments: list[Comment]


@dataclass(frozen=True)
class BatchResult:
    keyword: str
    leads: list[Lead]

    @property
    def markdown(self) -> str:
        lines = [f"# {self.keyword}", ""]

        tier_order = {"高意向": 0, "潜在意向": 1, "不相关": 2, "排除": 3}
        sorted_leads = sorted(self.leads, key=lambda l: tier_order.get(l.tier, 99))

        filtered = [l for l in sorted_leads if l.tier != "不相关"]

        current_tier = None
        for lead in filtered:
            if lead.tier != current_tier:
                lines.append(f"## {lead.tier}")
                lines.append("")
                current_tier = lead.tier

            lines.append(f"**{lead.nickname}** (`{lead.user_id}`)")
            lines.append("")
            lines.append(f"**判定理由**：{lead.reason}")
            lines.append("")
            if lead.opener:
                lines.append(f"**开场白**：{lead.opener}")
                lines.append("")

            lines.append(f"**归因**：来源关键词 `{self.keyword}`")
            for c in lead.comments:
                lines.append(f"- {c.note.title} — {c.note.url}")
            lines.append("")

        return "\n".join(lines)


def run_batch(
    keyword: str,
    fetch: Callable[[str], list[Comment]],
    judge: Callable[[str, list[Comment]], Judgement],
) -> BatchResult:
    comments = fetch(keyword)

    by_user: dict[str, list[Comment]] = {}
    for c in comments:
        by_user.setdefault(c.user_id, []).append(c)

    leads: list[Lead] = []
    for user_id, user_comments in by_user.items():
        nickname = user_comments[0].nickname
        judgement = judge(nickname, user_comments)
        leads.append(
            Lead(
                user_id=user_id,
                nickname=nickname,
                tier=judgement.tier,
                reason=judgement.reason,
                opener=judgement.opener,
                comments=user_comments,
            )
        )

    return BatchResult(keyword=keyword, leads=leads)
