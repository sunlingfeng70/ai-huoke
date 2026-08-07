"""测试子评论拍平功能。

取数层返回的评论是嵌套结构，主评论的「子评论」字段下挂着子评论列表。
flatten_comments 把它拍平成统一的 Comment 列表。
"""

from __future__ import annotations

from huoke import Comment, Judgement, Note, flatten_comments, run_batch

NOTE_A = Note(
    note_id="note_a",
    title="测试笔记 A",
    url="https://www.xiaohongshu.com/explore/note_a",
)


def test_拍平空列表() -> None:
    result = flatten_comments([], NOTE_A)
    assert result == []


def test_拍平无子评论的主评论() -> None:
    raw = [
        {
            "评论ID": "c1",
            "用户昵称": "小张",
            "用户ID": "u1",
            "评论内容": "零基础想学",
            "发布时间": "1700000000",
            "点赞数量": "5",
            "回复数量": "0",
            "子评论": [],
        }
    ]
    result = flatten_comments(raw, NOTE_A)
    assert len(result) == 1
    assert result[0].comment_id == "c1"
    assert result[0].user_id == "u1"
    assert result[0].nickname == "小张"
    assert result[0].content == "零基础想学"
    assert result[0].created_at == "1700000000"
    assert result[0].note == NOTE_A


def test_拍平含子评论的主评论() -> None:
    raw = [
        {
            "评论ID": "c1",
            "用户昵称": "小张",
            "用户ID": "u1",
            "评论内容": "零基础想学",
            "发布时间": "1700000000",
            "点赞数量": "5",
            "回复数量": "2",
            "子评论": [
                {
                    "评论ID": "c1_sub1",
                    "用户昵称": "博主",
                    "用户ID": "u_author",
                    "评论内容": "可以的",
                    "发布时间": "1700000001",
                    "点赞数量": "1",
                    "回复数量": "0",
                    "子评论": [],
                },
                {
                    "评论ID": "c1_sub2",
                    "用户昵称": "小张",
                    "用户ID": "u1",
                    "用户内容": "谢谢",
                    "发布时间": "1700000002",
                    "点赞数量": "0",
                    "回复数量": "0",
                    "子评论": [],
                },
            ],
        }
    ]
    result = flatten_comments(raw, NOTE_A)
    assert len(result) == 3
    assert result[0].comment_id == "c1"
    assert result[1].comment_id == "c1_sub1"
    assert result[2].comment_id == "c1_sub2"
    assert all(c.note == NOTE_A for c in result)


def test_同一人在多条笔记下评论_其中一条是子评论() -> None:
    note_b = Note("note_b", "测试笔记 B", "https://www.xiaohongshu.com/explore/note_b")

    raw_a = [
        {
            "评论ID": "c1",
            "用户昵称": "小张",
            "用户ID": "u1",
            "评论内容": "零基础想学",
            "发布时间": "1700000000",
            "点赞数量": "5",
            "回复数量": "0",
            "子评论": [],
        }
    ]
    raw_b = [
        {
            "评论ID": "c2",
            "用户昵称": "其他人",
            "用户ID": "u_other",
            "评论内容": "这个工具好用吗",
            "发布时间": "1700000010",
            "点赞数量": "2",
            "回复数量": "1",
            "子评论": [
                {
                    "评论ID": "c2_sub1",
                    "用户昵称": "小张",
                    "用户ID": "u1",
                    "评论内容": "我也想知道",
                    "发布时间": "1700000011",
                    "点赞数量": "0",
                    "回复数量": "0",
                    "子评论": [],
                }
            ],
        }
    ]
    raw_c = [
        {
            "评论ID": "c3",
            "用户昵称": "小张",
            "用户ID": "u1",
            "评论内容": "已关注",
            "发布时间": "1700000020",
            "点赞数量": "1",
            "回复数量": "0",
            "子评论": [],
        }
    ]

    note_c = Note("note_c", "测试笔记 C", "https://www.xiaohongshu.com/explore/note_c")

    all_comments = (
        flatten_comments(raw_a, NOTE_A)
        + flatten_comments(raw_b, note_b)
        + flatten_comments(raw_c, note_c)
    )

    def fetch(keyword: str) -> list[Comment]:
        return all_comments

    def judge(nickname: str, comments: list[Comment]) -> Judgement:
        return Judgement(tier="高意向", reason="测试用", opener="测试用")

    result = run_batch(keyword="测试", fetch=fetch, judge=judge)

    小张的线索 = [l for l in result.leads if l.user_id == "u1"]
    assert len(小张的线索) == 1, "同一人在 3 条笔记下的评论应聚合为 1 条线索"

    线索 = 小张的线索[0]
    assert len(线索.comments) == 3
    assert [c.note for c in 线索.comments] == [NOTE_A, note_b, note_c]
    assert "c2_sub1" in [c.comment_id for c in 线索.comments], "藏在子评论里的发言不能漏掉"
