# -*- coding: utf-8 -*-
"""Featureflow 软件开发流程（AI 应用整体）泳道图生成器。
横向泳道 = 角色；从左到右 = 流程；每个活动框下挂 Featureflow 命令标签。
"""
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

def font(sz):
    return ImageFont.truetype(FONT, sz)

f_title = font(34)
f_lane = font(21)
f_box = font(16)
f_num = font(13)
f_tag = font(12)
f_note = font(15)
f_out = font(15)

# ---- 调色 ----
C_AI_FILL = (218, 232, 252)      # AI 蓝
C_AI_LINE = (108, 142, 191)
C_HUMAN_FILL = (213, 232, 212)   # 人工 绿
C_HUMAN_LINE = (130, 179, 102)
C_REVIEW_FILL = (255, 242, 204)  # 评审 黄
C_REVIEW_LINE = (214, 182, 86)
C_OUT_FILL = (255, 235, 156)     # 文档产物 深黄
C_OUT_LINE = (214, 182, 86)
C_TERM_FILL = (245, 245, 245)    # 开始/结束
C_TERM_LINE = (130, 130, 130)
C_TAG = (28, 99, 145)
C_RED = (184, 84, 80)
C_LANEHDR = (242, 246, 250)
C_LANE_ALT = (250, 252, 254)
C_ARROW = (90, 90, 90)
C_TEXT = (30, 30, 30)

# ---- 画布与栅格 ----
LH = 180          # 左侧泳道标题宽
X0 = LH + 80      # 第 0 列中心
STEP = 168
TOP = 96          # 标题区
LANE_H = 212
BOX_W = 152
BOX_H = 58

LANES = ["需求下发人员", "AI", "开发人员", "测试人员"]

N_COLS = 16
W = X0 + (N_COLS - 1) * STEP + BOX_W // 2 + 40
H = TOP + len(LANES) * LANE_H + 36

def lane_cy(i):
    return TOP + i * LANE_H + LANE_H // 2

def colx(c):
    return X0 + c * STEP

img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)

# ---- 泳道底纹 + 标题列 ----
for i, name in enumerate(LANES):
    y1 = TOP + i * LANE_H
    y2 = y1 + LANE_H
    d.rectangle([0, y1, W, y2], fill=(C_LANE_ALT if i % 2 else (255, 255, 255)))
    d.rectangle([0, y1, LH, y2], fill=C_LANEHDR, outline=(200, 210, 220))
    # 虚线泳道分隔
    for x in range(LH, W, 14):
        d.line([x, y1, x + 7, y1], fill=(205, 213, 222), width=1)
    # 标题（竖排居中）
    bb = d.textbbox((0, 0), name, font=f_lane)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.text((LH // 2 - tw // 2, (y1 + y2) // 2 - th // 2 - 4), name, font=f_lane, fill=(60, 70, 90))
d.line([0, TOP + len(LANES) * LANE_H, W, TOP + len(LANES) * LANE_H], fill=(200, 210, 220), width=1)
d.line([LH, TOP, LH, TOP + len(LANES) * LANE_H], fill=(180, 190, 200), width=1)

# ---- 标题 ----
title = "Featureflow 软件开发流程（AI 应用整体）"
bb = d.textbbox((0, 0), title, font=f_title)
d.text(((W - (bb[2] - bb[0])) // 2, 28), title, font=f_title, fill=(31, 99, 145))

def wrap_cjk(text, n):
    return [text[i:i + n] for i in range(0, len(text), n)]

def draw_box(cx, cy, num, name, tag, kind="ai", w=BOX_W, h=BOX_H):
    if kind == "ai":
        fill, line = C_AI_FILL, C_AI_LINE
    elif kind == "human":
        fill, line = C_HUMAN_FILL, C_HUMAN_LINE
    elif kind == "review":
        fill, line = C_REVIEW_FILL, C_REVIEW_LINE
    else:
        fill, line = C_AI_FILL, C_AI_LINE
    x1, y1, x2, y2 = cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2
    d.rounded_rectangle([x1, y1, x2, y2], radius=6, fill=fill, outline=line, width=2)
    # 编号条
    if num:
        d.text((x1 + 7, y1 + 4), num, font=f_num, fill=(120, 120, 120))
    # 名称（自动换行）
    lines = []
    for seg in name.split("\n"):
        lines += wrap_cjk(seg, 9)
    ty = y1 + 17
    for ln in lines[:2]:
        bb = d.textbbox((0, 0), ln, font=f_box)
        d.text((cx - (bb[2] - bb[0]) // 2, ty), ln, font=f_box, fill=C_TEXT)
        ty += 19
    # 命令标签（框下方）
    if tag:
        for j, ln in enumerate(wrap_cjk(tag, 14)[:2]):
            bb = d.textbbox((0, 0), ln, font=f_tag)
            d.text((cx - (bb[2] - bb[0]) // 2, y2 + 3 + j * 14), ln, font=f_tag, fill=C_TAG)
    return (x1, y1, x2, y2)

def draw_term(cx, cy, text):
    w, h = 96, 40
    d.rounded_rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], radius=20,
                        fill=C_TERM_FILL, outline=C_TERM_LINE, width=2)
    bb = d.textbbox((0, 0), text, font=f_box)
    d.text((cx - (bb[2] - bb[0]) // 2, cy - (bb[3] - bb[1]) // 2 - 4), text, font=f_box, fill=(60, 60, 60))

def draw_doc(cx, cy, text):
    import math
    w, h = 138, 52
    x1, y1, x2, y2 = cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2
    body_bottom = y2 - 8
    # 文档主体（上平）
    d.polygon([(x1, y1), (x2, y1), (x2, body_bottom), (x1, body_bottom)],
              fill=C_OUT_FILL, outline=None)
    # 波浪底
    steps = 28
    top_line = [(x1, body_bottom), (x2, body_bottom)]
    wave = []
    for s in range(steps + 1):
        xx = x1 + w * s / steps
        yy = body_bottom + 7 + 7 * math.sin(s / steps * math.pi * 4)
        wave.append((xx, yy))
    fill_poly = [(x1, body_bottom)] + wave + [(x2, body_bottom)]
    d.polygon(fill_poly, fill=C_OUT_FILL)
    # 边框：左、上、右 + 波浪
    d.line([(x1, body_bottom), (x1, y1), (x2, y1), (x2, body_bottom)], fill=C_OUT_LINE, width=2)
    d.line(wave, fill=C_OUT_LINE, width=2)
    for ln_i, ln in enumerate(wrap_cjk(text, 8)[:2]):
        bb = d.textbbox((0, 0), ln, font=f_out)
        d.text((cx - (bb[2] - bb[0]) // 2, y1 + 9 + ln_i * 18), ln, font=f_out, fill=(90, 70, 0))

def arrow(p, q, color=C_ARROW, width=2):
    """正交连线：先水平后垂直再水平，带箭头。"""
    (x1, y1), (x2, y2) = p, q
    pts = [(x1, y1)]
    if y1 == y2:
        pts.append((x2, y2))
    else:
        midx = (x1 + x2) // 2
        pts += [(midx, y1), (midx, y2), (x2, y2)]
    d.line(pts, fill=color, width=width, joint="curve")
    # 箭头头部
    import math
    ax, ay = pts[-1]
    bx, by = pts[-2]
    ang = math.atan2(ay - by, ax - bx)
    L = 9
    d.polygon([
        (ax, ay),
        (ax - L * math.cos(ang - 0.4), ay - L * math.sin(ang - 0.4)),
        (ax - L * math.cos(ang + 0.4), ay - L * math.sin(ang + 0.4)),
    ], fill=color)

def rc(box, side):
    x1, y1, x2, y2 = box
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    return {"r": (x2, cy), "l": (x1, cy), "t": (cx, y1), "b": (cx, y2)}[side]

# ---- 节点定义：(key, lane, col, num, name, tag, kind) ----
boxes = {}
def B(key, lane, col, num, name, tag, kind="ai"):
    boxes[key] = draw_box(colx(col), lane_cy(lane), num, name, tag, kind)

# 先画红色协同框（底层），范围覆盖 AI+开发 两条泳道、col5~col11
rb_x1 = colx(5) - BOX_W // 2 - 16
rb_x2 = colx(11) + BOX_W // 2 + 16
rb_y1 = lane_cy(1) - BOX_H // 2 - 18
rb_y2 = lane_cy(2) + BOX_H // 2 + 66
d.rounded_rectangle([rb_x1, rb_y1, rb_x2, rb_y2], radius=10, outline=C_RED, width=2)

# 终端
draw_term(colx(0), lane_cy(0), "开始")

# 需求下发人员
B("n001", 0, 1, "001", "需求开发任务下发", "Boss 提需求→《需求描述.md》")
# 开发人员
B("n002", 2, 1, "002", "AI 环境配置", "CODEBUDDY.md+.codebuddy/", "human")
B("n003", 2, 2, "003", "需求分析", "/Featureflow→devflow-router", "human")
B("n005", 2, 3, "005", "需求分析内容确认", "Boss 确认·/requirement-review", "human")
B("n008", 2, 4, "008", "软件设计内容确认", "/walkthrough(概要)·Boss", "human")
# AI
B("n004", 1, 3, "004", "需求澄清和拓展", "/brainstorm(+/openapi)")
B("n007", 1, 4, "007", "方案设计和拓展", "/spec-lite(H/M/L)")
B("n010so", 1, 5, "010", "系统测试用例输出", "/testcase(8 维度)")
B("n010cg", 1, 6, "010", "代码生成", "/write-plan→/execute-plan")
B("n010cr", 1, 7, "010", "代码 review", "/code-review(增量·立方)")
B("n010ug", 1, 8, "010", "单元测试用例生成", "/test-gen|/unified-test")
B("n010ue", 1, 9, "010", "单元测试执行", "/unified-test(覆盖率)")
B("n010cm", 1, 10, "010", "代码上库", "门禁通过·/ci-setup")
B("n010st", 1, 11, "010", "系统测试", "/system-test(端到端)")
# 开发人员（协同确认，多为“非必须”）
B("n009c", 2, 5, "010", "系统测试用例确认与补全", "五维评审·Boss 确认", "review")
B("n010cgc", 2, 6, "010", "代码生成效果确认", "(非必须) Boss 检查点", "human")
B("n010crc", 2, 7, "010", "review 结果确认", "(非必须)·/code-self-check", "human")
B("n010ugc", 2, 8, "010", "单元测试用例确认", "(非必须)", "human")
B("n010tcr", 2, 9, "010", "测试用例评审", "(非必须)", "review")
B("n010jt", 2, 10, "010", "联调", "/parallel-delivery", "human")
B("n010stc", 2, 11, "010", "系统测试结果确认与补全", "/requirement-coverage", "human")
# 验收段
B("n011", 1, 12, "011", "验收测试用例补全", "/testcase(验收)")
B("n014", 1, 13, "014", "验收测试执行", "执行·提单 /defect-loop")
B("n012", 3, 12, "012", "验收测试用例确认与补全", "Boss/测试确认", "human")
B("n013", 3, 13, "013", "测试用例评审", "测试评审", "review")
B("n015", 3, 14, "015", "验收测试结果确认与补全", "/release·/status 收尾", "human")
draw_term(colx(15), lane_cy(3), "结束")

# 文档产物
out_docs = []
def OUT(col, lane, text, src):
    cx = colx(col)
    cy = lane_cy(lane) + 92
    draw_doc(cx, cy, text)
    # 连线 源框底 → 文档
    sb = boxes[src]
    arrow(((sb[0]+sb[2])//2, sb[3]), (cx, cy - 25))
OUT(3, 2, "需求分析文档", "n005")
OUT(4, 2, "软件方案设计文档", "n008")
OUT(13, 3, "测试用例", "n013")
OUT(14, 3, "测试报告", "n015")

# 红框说明
note = "说明：红色协同框内环节由 Featureflow 命令（AI）协作完成，或按场景需要人工支持；非必须环节可裁剪，不做流程明细要求。"
d.text((rb_x1 + 12, rb_y2 - 24), note, font=f_note, fill=C_RED)

# ---- 连线 ----
A = arrow
A(rc(boxes_term_start := (colx(0)-48, lane_cy(0)-20, colx(0)+48, lane_cy(0)+20), "r"), rc(boxes["n001"], "l"))
A(rc(boxes["n001"], "b"), rc(boxes["n002"], "t"))
A(rc(boxes["n002"], "r"), rc(boxes["n003"], "l"))
A(rc(boxes["n003"], "r"), rc(boxes["n004"], "l"))
A(rc(boxes["n004"], "b"), rc(boxes["n005"], "t"))
A(rc(boxes["n005"], "r"), rc(boxes["n007"], "l"))
A(rc(boxes["n007"], "b"), rc(boxes["n008"], "t"))
A(rc(boxes["n008"], "r"), rc(boxes["n010so"], "l"))
# AI 主链
for a, b in [("n010so","n010cg"),("n010cg","n010cr"),("n010cr","n010ug"),
             ("n010ug","n010ue"),("n010ue","n010cm"),("n010cm","n010st"),
             ("n010st","n011")]:
    A(rc(boxes[a], "r"), rc(boxes[b], "l"))
# AI→开发确认（向下）
for a, b in [("n010so","n009c"),("n010cg","n010cgc"),("n010cr","n010crc"),
             ("n010ug","n010ugc"),("n010ue","n010tcr"),("n010cm","n010jt"),
             ("n010st","n010stc")]:
    A(rc(boxes[a], "b"), rc(boxes[b], "t"))
# 验收段
A(rc(boxes["n011"], "b"), rc(boxes["n012"], "t"))
A(rc(boxes["n012"], "r"), rc(boxes["n013"], "l"))
A(rc(boxes["n013"], "t"), rc(boxes["n014"], "b"))
A(rc(boxes["n014"], "r"), rc(boxes["n015"], "t"))
A(rc(boxes["n015"], "r"), (colx(15), lane_cy(3)))

import os
_out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "featureflow-swimlane.png")
img.save(_out)
print("saved", _out, W, H)
