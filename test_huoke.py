"""意向名单工具的测试。

主缝是 `run_batch` —— 取评论与判定都是函数参数，测试用返回固定数据的
假实现代入，因此这里不发任何网络请求、不调模型。
"""

from __future__ import annotations

from huoke import Comment, Judgement, Note, run_batch

NOTE_A = Note(
    note_id="note_a",
    title="零基础怎么入门 AI",
    url="https://www.xiaohongshu.com/explore/note_a?xsec_token=tok_a",
)
NOTE_B = Note(
    note_id="note_b",
    title="AI 工具推荐合集",
    url="https://www.xiaohongshu.com/explore/note_b?xsec_token=tok_b",
)


def fake_fetch(keyword: str) -> list[Comment]:
    return [
        Comment(
            comment_id="c1",
            user_id="u_eager",
            nickname="想转行的小张",
            content="零基础想学，有推荐的课吗",
            created_at="1700000000",
            note=NOTE_A,
        ),
        Comment(
            comment_id="c2",
            user_id="u_maybe",
            nickname="路过的猫",
            content="码住",
            created_at="1700000001",
            note=NOTE_A,
        ),
        Comment(
            comment_id="c3",
            user_id="u_noise",
            nickname="爱玩梗的人",
            content="哈哈哈哈哈",
            created_at="1700000002",
            note=NOTE_B,
        ),
        Comment(
            comment_id="c4",
            user_id="u_peer",
            nickname="AI培训老王",
            content="我们机构也开这课",
            created_at="1700000003",
            note=NOTE_B,
        ),
    ]


_JUDGEMENTS = {
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


def fake_judge(nickname: str, comments: list[Comment]) -> Judgement:
    return _JUDGEMENTS[comments[0].user_id]


def render(keyword: str = "AI入门", fetch=fake_fetch, judge=fake_judge) -> str:
    return run_batch(keyword=keyword, fetch=fetch, judge=judge).markdown


def test_名单按意向档排序_高意向在前() -> None:
    md = render()
    assert md.index("高意向") < md.index("潜在意向")


def test_每条线索打印用户ID_供人工复制进回流文件() -> None:
    md = render()
    assert "u_eager" in md
    assert "u_maybe" in md


def test_每条线索打印判定理由与开场白() -> None:
    md = render()
    assert "明确说「零基础想学，有推荐的课吗」，直接求课程推荐。" in md
    assert "看到你想从零开始学 AI，方便聊聊你的基础和目标吗？" in md


def test_每条线索打印归因_来源关键词与来源笔记() -> None:
    md = render(keyword="AI入门")
    assert "来源关键词 `AI入门`" in md
    assert "零基础怎么入门 AI" in md
    assert "https://www.xiaohongshu.com/explore/note_a?xsec_token=tok_a" in md


def test_不相关不占名单篇幅() -> None:
    md = render()
    assert "u_noise" not in md
    assert "哈哈哈哈哈" not in md


def test_排除档出现在名单中供人工审查() -> None:
    md = render()
    assert "u_peer" in md
    assert "AI培训老王" in md
    assert "排除" in md


def test_同一评论者在多条笔记下的评论合成一条线索() -> None:
    def fetch_same_person(keyword: str) -> list[Comment]:
        return [
            Comment("c1", "u_eager", "想转行的小张", "零基础想学", "1700000000", NOTE_A),
            Comment("c2", "u_eager", "想转行的小张", "有推荐的课吗", "1700000001", NOTE_B),
        ]

    result = run_batch(keyword="AI入门", fetch=fetch_same_person, judge=fake_judge)

    assert len(result.leads) == 1
    assert result.leads[0].user_id == "u_eager"
    assert len(result.leads[0].comments) == 2


def test_判定看到的是该评论者的全部评论() -> None:
    seen: list[int] = []

    def fetch_same_person(keyword: str) -> list[Comment]:
        return [
            Comment("c1", "u_eager", "小张", "零基础想学", "1700000000", NOTE_A),
            Comment("c2", "u_eager", "小张", "有推荐的课吗", "1700000001", NOTE_B),
        ]

    def recording_judge(nickname: str, comments: list[Comment]) -> Judgement:
        seen.append(len(comments))
        return _JUDGEMENTS["u_eager"]

    run_batch(keyword="AI入门", fetch=fetch_same_person, judge=recording_judge)

    assert seen == [2], "判断单位是评论者，模型应一次看到他的全部评论"


def test_同一意向档的多条线索只打印一次节标题() -> None:
    def fetch_two_eager(keyword: str) -> list[Comment]:
        return [
            Comment("c1", "u_eager1", "小张", "零基础想学", "1700000000", NOTE_A),
            Comment("c2", "u_eager2", "小李", "有推荐的课吗", "1700000001", NOTE_B),
        ]

    def judge_all_eager(nickname: str, comments: list[Comment]) -> Judgement:
        return _JUDGEMENTS["u_eager"]

    md = run_batch(keyword="AI入门", fetch=fetch_two_eager, judge=judge_all_eager).markdown
    assert md.count("## 高意向") == 1
