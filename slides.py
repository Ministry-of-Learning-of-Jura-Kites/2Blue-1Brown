"""Shor's Algorithm presentation (~10 min, Thai, non-quantum audience).

Run:
    manim-slides render slides.py ShorTalk
    manim-slides ShorTalk
"""

from manim import *
from manim_slides import Slide
import numpy as np

TH_FONT = "Tahoma"  # ships with Windows, supports Thai

# Frame is y in [-4, 4]. Header occupies top ~1.2 units (title text + underline).
# Treat the remaining area as the "content box" and center things in it.
CONTENT_TOP_Y = 2.6
CONTENT_BOTTOM_Y = -3.8
CONTENT_CENTER_Y = (CONTENT_TOP_Y + CONTENT_BOTTOM_Y) / 2  # ≈ -0.6


def content_center(x=0.0, dy=0.0):
    """Point at (x, CONTENT_CENTER_Y + dy, 0) — i.e. middle of the content
    area below the header. Use instead of raw [x, 0, 0] to avoid drifting
    into the header zone."""
    return np.array([x, CONTENT_CENTER_Y + dy, 0])

# Palette
C_BG = "#0f1020"
C_ACCENT = "#ffcc66"
C_POS = "#66d9a8"
C_NEG = "#ff6b6b"
C_MUTED = "#8a8fa3"

config.background_color = C_BG


def th(text, size=36, color=WHITE, weight=NORMAL):
    return Text(text, font=TH_FONT, font_size=size, color=color, weight=weight)


def title_bar(text):
    t = th(text, size=40, color=C_ACCENT, weight=BOLD)
    t.to_edge(UP, buff=0.5)
    line = Line(LEFT * 6, RIGHT * 6, color=C_ACCENT, stroke_width=2)
    line.next_to(t, DOWN, buff=0.2)
    return VGroup(t, line)


class ShorTalk(Slide):
    def play(self, *anims, run_time=None, **kwargs):
        # Snappier default: text/FadeIn/Write at 0.5s instead of manim's 1.0s.
        # Explicit run_time overrides (e.g. walker.animate) still win.
        if run_time is None:
            run_time = 0.5
        super().play(*anims, run_time=run_time, **kwargs)

    def construct(self):
        self.slide_title()
        self.slide_hook()
        self.slide_qubit_basics()
        self.slide_why_2n()
        self.slide_grover_problem()
        self.slide_grover_one_iteration()
        self.slide_grover_iterate()
        self.slide_grover_pattern()
        self.slide_shor_roadmap()
        self.slide_factoring_trick()
        self.slide_order_finding()
        self.slide_shor_caveats()
        self.slide_shor_parallel()
        self.slide_shor_collapse()
        self.slide_shor_qft()
        self.slide_shor_recover()
        self.slide_tradeoffs()
        self.slide_reality()
        self.slide_end()

    # ----- slides -----

    def slide_title(self):
        title = th("Shor's Algorithm", size=72, color=C_ACCENT, weight=BOLD)
        sub = th("แยกตัวประกอบด้วย quantum computer", size=32, color=C_MUTED)
        sub.next_to(title, DOWN, buff=0.4)
        self.play(FadeIn(title, shift=UP * 0.3), FadeIn(sub))
        self.next_slide()
        self.play(FadeOut(title), FadeOut(sub))

    def slide_hook(self):
        header = title_bar("ทำไมเราถึงควรสนใจ?")
        self.play(FadeIn(header))

        lines = VGroup(
            th("ทุกครั้งที่เราเข้าเว็บผ่าน https", size=28),
            th("เรากำลังเชื่อใจสมมติฐานที่ว่า", size=28),
            th('"การแยกตัวประกอบของเลขใหญ่ๆ เป็นเรื่องยาก"',
               size=28, color=C_ACCENT),
            th("ซึ่งเป็นรากฐานของระบบ RSA", size=26, color=C_MUTED),
        ).arrange(DOWN, buff=0.2)
        lines.next_to(header, DOWN, buff=0.5)
        self.play(Write(lines))
        self.next_slide()

        cmp = VGroup(
            th("อัลกอริทึม classical ที่ดีที่สุดตอนนี้ (GNFS)",
               size=24, color=C_MUTED),
            th("ใช้เวลา", size=22, color=C_MUTED),
            MathTex(r"O\!\left(2^{n^{1/3}}\right)", color=WHITE).scale(1.0),
            th("กับ RSA-2048 ก็คือหลายพันปี", size=24, color=C_MUTED),
        ).arrange(RIGHT, buff=0.25)
        cmp.next_to(lines, DOWN, buff=0.4)
        self.play(FadeIn(cmp, shift=UP * 0.2))
        self.next_slide()

        shor_line = VGroup(
            th("แต่ในปี 1994 Peter Shor แสดงให้เห็นว่า",
               size=26, color=C_POS),
            th("quantum computer ทำได้ใน",
               size=26, color=C_POS),
            MathTex(r"O(n^3)", color=C_POS).scale(1.1),
        ).arrange(RIGHT, buff=0.2)
        shor_line.next_to(cmp, DOWN, buff=0.5)
        self.play(Write(shor_line))
        self.next_slide()
        self.play(*[FadeOut(m) for m in [header, lines, cmp, shor_line]])

    def slide_qubit_basics(self):
        header = title_bar("Qubit: หัวใจของ quantum")
        self.play(FadeIn(header))

        analogy = th("นึกภาพเหรียญที่กำลังหมุน — ยังไม่ใช่หัว ยังไม่ใช่ก้อย",
                     size=24, color=C_MUTED)
        analogy.next_to(header, DOWN, buff=0.2)
        self.play(FadeIn(analogy))

        # Left: arrow-on-circle diagram
        axes_center = content_center(x=-3.2, dy=-0.6)
        radius = 1.3
        x_axis = Arrow(axes_center + LEFT * 0.3,
                       axes_center + RIGHT * (radius + 0.6),
                       color=C_MUTED, buff=0, stroke_width=3)
        y_axis = Arrow(axes_center + DOWN * 0.3,
                       axes_center + UP * (radius + 0.6),
                       color=C_MUTED, buff=0, stroke_width=3)
        lbl0 = MathTex(r"|0\rangle", color=C_MUTED).scale(0.8)
        lbl0.next_to(x_axis.get_end(), RIGHT, buff=0.15)
        lbl1 = MathTex(r"|1\rangle", color=C_MUTED).scale(0.8)
        lbl1.next_to(y_axis.get_end(), UP, buff=0.15)
        circle = Circle(radius=radius, color=C_MUTED, stroke_width=1.5)
        circle.move_to(axes_center)
        self.play(Create(x_axis), Create(y_axis),
                  FadeIn(lbl0), FadeIn(lbl1), Create(circle))

        theta = 55 * DEGREES
        tip = axes_center + radius * np.array(
            [np.cos(theta), np.sin(theta), 0])
        state_arrow = Arrow(axes_center, tip, color=C_ACCENT,
                            buff=0, stroke_width=5)
        state_lbl = MathTex(r"|\psi\rangle", color=C_ACCENT).scale(0.9)
        state_lbl.next_to(tip, UR, buff=0.1)

        # Projections
        proj_x_end = axes_center + np.array([radius * np.cos(theta), 0, 0])
        proj_y_end = axes_center + np.array([0, radius * np.sin(theta), 0])
        alpha_seg = Line(axes_center, proj_x_end, color=C_POS, stroke_width=6)
        beta_seg = Line(axes_center, proj_y_end, color=C_NEG, stroke_width=6)
        proj_x = DashedLine(tip, proj_x_end, color=C_POS, stroke_width=2)
        proj_y = DashedLine(tip, proj_y_end, color=C_NEG, stroke_width=2)
        a_lbl = MathTex(r"\alpha", color=C_POS).scale(0.8)
        a_lbl.next_to(alpha_seg, DOWN, buff=0.1)
        b_lbl = MathTex(r"\beta", color=C_NEG).scale(0.8)
        b_lbl.next_to(beta_seg, LEFT, buff=0.1)

        self.play(GrowArrow(state_arrow), Write(state_lbl))
        self.play(
            Create(proj_x), Create(proj_y),
            Create(alpha_seg), Create(beta_seg),
            Write(a_lbl), Write(b_lbl),
        )

        # Right panel: equation + explanation
        eq = MathTex(r"|\psi\rangle = \alpha|0\rangle + \beta|1\rangle",
                     color=WHITE).scale(1.0)
        explain = VGroup(
            VGroup(
                MathTex(r"\alpha", color=C_POS).scale(0.8),
                th("= ความหนักไปทาง", size=20, color=C_POS),
                MathTex(r"|0\rangle", color=C_POS).scale(0.75),
            ).arrange(RIGHT, buff=0.15),
            VGroup(
                MathTex(r"\beta", color=C_NEG).scale(0.8),
                th("= ความหนักไปทาง", size=20, color=C_NEG),
                MathTex(r"|1\rangle", color=C_NEG).scale(0.75),
            ).arrange(RIGHT, buff=0.15),
            MathTex(r"|\alpha|^2 + |\beta|^2 = 1",
                    color=C_ACCENT).scale(0.85),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        right_panel = VGroup(eq, explain).arrange(DOWN, buff=0.3)
        right_panel.move_to(content_center(x=2.8, dy=1.4))
        self.play(Write(eq))
        self.play(FadeIn(explain))
        self.next_slide()

        # ---- Measurement phase ----
        ask = th("พอวัด → ลูกศรล้มลงแกนใดแกนหนึ่ง",
                 size=22, color=C_ACCENT, weight=BOLD)
        ask.next_to(right_panel, DOWN, buff=0.4)
        ask.align_to(right_panel, LEFT)
        self.play(Write(ask))

        probs = VGroup(
            MathTex(r"P(0) = |\alpha|^2", color=C_POS).scale(0.8),
            MathTex(r"P(1) = |\beta|^2", color=C_NEG).scale(0.8),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        probs.next_to(ask, DOWN, buff=0.2)
        probs.align_to(ask, LEFT)
        self.play(FadeIn(probs))
        self.next_slide()

        # Collapse animation: 2 trials, packed tight
        horizontal_tip = axes_center + RIGHT * radius
        vertical_tip = axes_center + UP * radius

        outcomes = [
            (horizontal_tip, "|0\\rangle", C_POS),
            (vertical_tip, "|1\\rangle", C_NEG),
        ]
        result_labels = VGroup()
        anchor = probs
        for i, (target, name, col) in enumerate(outcomes):
            self.play(
                state_arrow.animate.put_start_and_end_on(axes_center, tip),
                run_time=0.25,
            )
            self.play(
                state_arrow.animate.put_start_and_end_on(axes_center, target),
                run_time=0.35,
            )
            r_lbl = VGroup(
                th(f"ลอง {i+1} →", size=18, color=col),
                MathTex(name, color=col).scale(0.65),
            ).arrange(RIGHT, buff=0.1)
            r_lbl.next_to(anchor, DOWN, aligned_edge=LEFT, buff=0.15)
            self.play(FadeIn(r_lbl), run_time=0.25)
            result_labels.add(r_lbl)
            anchor = r_lbl
        self.next_slide()

        self.play(*[FadeOut(m) for m in [
            header, analogy, x_axis, y_axis, lbl0, lbl1, circle,
            state_arrow, state_lbl, proj_x, proj_y,
            alpha_seg, beta_seg, a_lbl, b_lbl,
            eq, explain, ask, probs, result_labels,
        ]])

    # ----- Grover -----

    def _bars(self, values, colors=None, highlight=None):
        n = len(values)
        chart = VGroup()
        width = 0.7
        gap = 0.25
        total_w = n * width + (n - 1) * gap
        x0 = -total_w / 2
        labels = ["000", "001", "010", "011", "100", "101", "110", "111"]
        axis = Line(LEFT * (total_w / 2 + 0.3), RIGHT * (total_w / 2 + 0.3),
                    color=C_MUTED).shift(DOWN * 0.05)
        chart.add(axis)
        for i, v in enumerate(values):
            col = C_POS if v >= 0 else C_NEG
            if colors:
                col = colors[i]
            h = abs(v) * 3.0
            if h < 0.01:
                h = 0.01
            bar = Rectangle(
                width=width, height=h,
                fill_color=col, fill_opacity=0.9,
                stroke_color=col, stroke_width=2,
            )
            x = x0 + i * (width + gap) + width / 2
            if v >= 0:
                bar.move_to([x, h / 2, 0])
            else:
                bar.move_to([x, -h / 2, 0])
            chart.add(bar)
            lab = Text(labels[i], font_size=18, color=C_MUTED)
            lab.move_to([x, -0.35, 0])
            chart.add(lab)
        return chart

    def slide_why_2n(self):
        header = title_bar("Qubit: เก็บอะไรได้บ้าง?")
        self.play(FadeIn(header))

        setup = th("n classical bits กับ n qubits ต่างกันยังไง?",
                   size=26, color=C_MUTED)
        setup.next_to(header, DOWN, buff=0.3)
        self.play(FadeIn(setup))

        configs = ["00", "01", "10", "11"]

        # ------ Classical panel ------
        c_title = th("2 classical bits", size=22, color=C_MUTED)
        c_rows = VGroup()
        for cfg in configs:
            row = MathTex(cfg, color=WHITE).scale(0.75)
            c_rows.add(row)
        c_rows.arrange(DOWN, buff=0.15)
        c_panel = VGroup(c_title, c_rows).arrange(DOWN, buff=0.25)
        c_panel.move_to(content_center(x=-3.5, dy=1.1))
        self.play(FadeIn(c_panel))

        highlight = SurroundingRectangle(c_rows[2], color=C_ACCENT,
                                         buff=0.08, stroke_width=3)
        c_note = th("อยู่ที่เดียวในเวลาเดียว", size=18, color=C_MUTED)
        c_note.next_to(c_panel, DOWN, buff=0.25)
        self.play(Create(highlight), FadeIn(c_note))
        self.next_slide()

        # ------ Quantum panel ------
        q_title = th("2 qubits", size=22, color=C_ACCENT)
        q_rows = VGroup()
        amp_labels = [r"\alpha_{00}", r"\alpha_{01}",
                      r"\alpha_{10}", r"\alpha_{11}"]
        for cfg, amp in zip(configs, amp_labels):
            lhs = MathTex(cfg, color=WHITE).scale(0.75)
            arrow = MathTex(r"\to", color=C_MUTED).scale(0.7)
            rhs = MathTex(amp, color=C_ACCENT).scale(0.75)
            row = VGroup(lhs, arrow, rhs).arrange(RIGHT, buff=0.15)
            q_rows.add(row)
        q_rows.arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        q_panel = VGroup(q_title, q_rows).arrange(DOWN, buff=0.25)
        q_panel.move_to(content_center(x=3.2, dy=1.1))
        self.play(FadeIn(q_panel))

        q_note = VGroup(
            th("มีน้ำหนักทุกที่พร้อมกัน", size=18, color=C_ACCENT),
            MathTex(r"|\alpha_{cfg}|^2 = P(\text{collapse}\to cfg)",
                    color=C_POS).scale(0.65),
        ).arrange(DOWN, buff=0.1)
        q_note.next_to(q_panel, DOWN, buff=0.25)
        self.play(FadeIn(q_note))
        self.next_slide()

        punch = VGroup(
            th("50 qubits → 2⁵⁰ ≈ 10¹⁵ amplitude",
               size=24, color=C_POS, weight=BOLD),
            th("classical จำลองไม่ไหว", size=22, color=C_MUTED),
        ).arrange(DOWN, buff=0.1)
        punch.to_edge(DOWN, buff=0.4)
        self.play(Write(punch))
        self.next_slide()

        self.play(*[FadeOut(m) for m in [header, setup, c_panel,
                                          highlight, c_note,
                                          q_panel, q_note, punch]])

    def _grover_bars(self, values, mark_idx=None, y_scale=2.5,
                     bar_w=0.55, gap=0.2, baseline_y=None):
        """Build a Grover bar chart anchored at the content center.
        Returns VGroup(axis, labels, bars)."""
        n = len(values)
        total_w = n * bar_w + (n - 1) * gap
        x0 = -total_w / 2
        if baseline_y is None:
            baseline_y = CONTENT_CENTER_Y - 0.3
        axis = Line([x0 - 0.25, baseline_y, 0],
                    [x0 + total_w + 0.25, baseline_y, 0],
                    color=C_MUTED, stroke_width=1.5)
        bars = VGroup()
        labels = VGroup()
        for i, v in enumerate(values):
            x = x0 + i * (bar_w + gap) + bar_w / 2
            h = abs(v) * y_scale
            if h < 0.001:
                h = 0.001
            if mark_idx is not None and i == mark_idx:
                color = C_ACCENT
            elif v < 0:
                color = C_NEG
            else:
                color = C_POS
            bar = Rectangle(
                width=bar_w, height=h,
                fill_color=color, fill_opacity=0.85,
                stroke_color=color, stroke_width=2,
            )
            if v >= 0:
                bar.move_to([x, baseline_y + h / 2, 0])
            else:
                bar.move_to([x, baseline_y - h / 2, 0])
            bars.add(bar)
            lab = MathTex(format(i, "03b"), color=C_MUTED).scale(0.5)
            lab.move_to([x, baseline_y - 0.3, 0])
            labels.add(lab)
        return VGroup(axis, bars, labels), bars, baseline_y

    # ----- Grover -----

    def slide_grover_problem(self):
        header = title_bar("Grover: หาเข็มในกองฟาง")
        self.play(FadeIn(header))

        setup = VGroup(
            th("มี", size=26, color=C_MUTED),
            MathTex("n = 8", color=WHITE).scale(0.95),
            th("ตัวเลือก และมีแค่", size=26, color=C_MUTED),
            MathTex("1", color=C_ACCENT).scale(0.95),
            th("ตัวที่ใช่", size=26, color=C_MUTED),
        ).arrange(RIGHT, buff=0.2)
        setup.move_to(content_center(dy=1.5))
        self.play(FadeIn(setup))

        # 8 boxes row
        boxes = VGroup()
        for i in range(8):
            sq = Square(side_length=0.7, color=C_MUTED, stroke_width=2)
            lab = MathTex(str(i), color=C_MUTED).scale(0.6).move_to(sq)
            boxes.add(VGroup(sq, lab))
        boxes.arrange(RIGHT, buff=0.18)
        boxes.move_to(content_center(dy=0.3))
        self.play(FadeIn(boxes))

        # Oracle description
        oracle_desc = VGroup(
            th("Oracle:", size=24, color=C_ACCENT),
            th("ถามว่า", size=22, color=C_MUTED),
            MathTex("x", color=WHITE).scale(0.85),
            th("ใช่หรือไม่ใช่? —", size=22, color=C_MUTED),
            MathTex(r"f(x) \in \{0, 1\}",
                    color=WHITE).scale(0.85),
        ).arrange(RIGHT, buff=0.2)
        oracle_desc.move_to(content_center(dy=-0.5))
        self.play(FadeIn(oracle_desc))

        caveat = VGroup(
            th("ข้อแม้: oracle ต้องเขียนเป็น quantum circuit",
               size=20, color=C_NEG),
            th("ถึงจะรับ superposition ของ", size=20, color=C_NEG),
            MathTex("x", color=C_NEG).scale(0.75),
            th("ได้", size=20, color=C_NEG),
        ).arrange(RIGHT, buff=0.15)
        caveat.next_to(oracle_desc, DOWN, buff=0.2)
        self.play(FadeIn(caveat))
        self.next_slide()

        # Classical vs Quantum
        compare = VGroup(
            VGroup(
                th("Classical:", size=24, color=C_MUTED),
                th("เปิดทีละกล่อง เฉลี่ย", size=24, color=C_MUTED),
                MathTex("n/2 = 4", color=C_MUTED).scale(0.9),
                th("ครั้ง", size=24, color=C_MUTED),
            ).arrange(RIGHT, buff=0.2),
            VGroup(
                th("Grover:", size=24, color=C_POS, weight=BOLD),
                MathTex(r"\sqrt{n} \approx 3", color=C_POS).scale(0.9),
                th("ครั้ง — โดยใช้ quantum interference",
                   size=24, color=C_POS),
            ).arrange(RIGHT, buff=0.2),
        ).arrange(DOWN, buff=0.25)
        compare.move_to(content_center(dy=-2.3))
        self.play(FadeIn(compare))
        self.next_slide()

        self.play(*[FadeOut(m) for m in [header, setup, boxes,
                                          oracle_desc, caveat, compare]])

    def slide_grover_one_iteration(self):
        header = title_bar("Grover 1 รอบ: ทำอะไรกับ amplitude")
        self.play(FadeIn(header))

        caption = VGroup(
            th("เริ่มด้วย amplitude เท่ากัน", size=24, color=C_MUTED),
            MathTex(r"=\tfrac{1}{\sqrt{8}}", color=C_MUTED).scale(0.85),
        ).arrange(RIGHT, buff=0.2)
        caption.next_to(header, DOWN, buff=0.25)
        self.play(FadeIn(caption))

        a = 1 / np.sqrt(8)
        vals_uniform = [a] * 8
        chart, _, _ = self._grover_bars(vals_uniform, mark_idx=6)
        self.play(FadeIn(chart))

        bottom = th("ทุกตัวมีโอกาสถูกเลือก 1/8 เท่ากัน",
                    size=22, color=C_MUTED)
        bottom.move_to(content_center(dy=-2.2))
        self.play(FadeIn(bottom))
        self.next_slide()

        # Step 1: Oracle phase flip
        new_caption = VGroup(
            th("Step 1: Oracle ทำงานบน superposition",
               size=24, color=C_ACCENT),
            th("— ใส่เครื่องหมายลบให้คำตอบที่ถูก",
               size=22, color=C_MUTED),
        ).arrange(DOWN, buff=0.1)
        new_caption.move_to(caption)
        self.play(Transform(caption, new_caption))

        vals_flipped = [a] * 8
        vals_flipped[6] = -a
        chart2, _, _ = self._grover_bars(vals_flipped, mark_idx=6)
        self.play(Transform(chart, chart2))

        kickback = VGroup(
            th("oracle call 1 ครั้ง ทำงานพร้อมกันทุก", size=22, color=C_MUTED),
            MathTex("x", color=C_MUTED).scale(0.85),
            th("—", size=22, color=C_MUTED),
            th("เราไม่ต้องรู้ว่าคำตอบคือตัวไหน",
               size=22, color=C_MUTED),
        ).arrange(RIGHT, buff=0.15)
        kickback.move_to(bottom)
        self.play(Transform(bottom, kickback))
        self.next_slide()

        # Step 2: Diffusion
        new_caption2 = VGroup(
            th("Step 2: Diffusion", size=24, color=C_ACCENT),
            th("— ขยายตัวที่ 'ต่าง' จากตัวอื่น",
               size=22, color=C_MUTED),
        ).arrange(DOWN, buff=0.1)
        new_caption2.move_to(caption)
        self.play(Transform(caption, new_caption2))

        mean_value = sum(vals_flipped) / 8
        vals_after = [2 * mean_value - v for v in vals_flipped]
        chart3, _, _ = self._grover_bars(vals_after, mark_idx=6)
        self.play(Transform(chart, chart3))

        p_after = vals_after[6] ** 2
        result = VGroup(
            th("หลัง 1 รอบ: คำตอบมีความน่าจะเป็น",
               size=22, color=C_POS),
            MathTex(rf"\approx {p_after * 100:.0f}\%",
                    color=C_POS).scale(0.9),
        ).arrange(RIGHT, buff=0.2)
        result.move_to(bottom)
        self.play(Transform(bottom, result))
        self.next_slide()

        self.play(*[FadeOut(m) for m in [header, caption, chart, bottom]])

    def slide_grover_iterate(self):
        header = title_bar("ทำซ้ำจนเกือบ 100%")
        self.play(FadeIn(header))

        a = 1 / np.sqrt(8)

        # Simulate 3 Grover iterations
        def iterate(vals, mark=6):
            out = vals.copy()
            out[mark] = -out[mark]  # phase flip
            mean = sum(out) / len(out)
            return [2 * mean - v for v in out]

        frame0 = [a] * 8
        frame1 = iterate(frame0)
        frame2 = iterate(frame1)

        # Build a "measurement" frame: collapse to the target
        frame_measured = [0.0] * 8
        frame_measured[6] = 1.0

        labels_frames = [
            ("เริ่มต้น", frame0),
            ("รอบที่ 1", frame1),
            ("รอบที่ 2 (เกือบสุด)", frame2),
            ("วัด → เจอ!", frame_measured),
        ]

        mini_bar_w = 0.18
        mini_gap = 0.06

        def mini_chart(vals, center_x, center_y):
            n = len(vals)
            total_w = n * mini_bar_w + (n - 1) * mini_gap
            x0 = center_x - total_w / 2
            group = VGroup()
            axis = Line([x0 - 0.1, center_y, 0],
                        [x0 + total_w + 0.1, center_y, 0],
                        color=C_MUTED, stroke_width=1)
            group.add(axis)
            for i, v in enumerate(vals):
                x = x0 + i * (mini_bar_w + mini_gap) + mini_bar_w / 2
                h = abs(v) * 1.4
                if h < 0.01:
                    h = 0.01
                col = C_ACCENT if i == 6 else (C_POS if v >= 0 else C_NEG)
                bar = Rectangle(
                    width=mini_bar_w, height=h,
                    fill_color=col, fill_opacity=0.85,
                    stroke_color=col, stroke_width=1.5,
                )
                if v >= 0:
                    bar.move_to([x, center_y + h / 2, 0])
                else:
                    bar.move_to([x, center_y - h / 2, 0])
                group.add(bar)
            return group

        # Arrange 4 mini-charts in a row
        xs = [-5.1, -1.7, 1.7, 5.1]
        y_row = CONTENT_CENTER_Y + 0.2
        mini_charts = []
        mini_titles = VGroup()
        prob_labels = VGroup()

        for (lab, vals), x in zip(labels_frames, xs):
            mc = mini_chart(vals, x, y_row)
            mini_charts.append(mc)
            title = th(lab, size=22, color=C_ACCENT)
            title.move_to([x, y_row + 1.4, 0])
            mini_titles.add(title)
            prob = vals[6] ** 2
            if lab.startswith("วัด"):
                pl = MathTex(r"\checkmark", color=C_POS).scale(1.1)
            else:
                pl = MathTex(rf"P = {prob * 100:.0f}\%",
                             color=C_POS).scale(0.75)
            pl.move_to([x, y_row - 1.1, 0])
            prob_labels.add(pl)

        self.play(FadeIn(mini_titles[0]), FadeIn(mini_charts[0]),
                  FadeIn(prob_labels[0]))
        for i in range(1, 4):
            self.play(FadeIn(mini_titles[i]), FadeIn(mini_charts[i]),
                      FadeIn(prob_labels[i]))
        self.next_slide()

        conclusion = VGroup(
            th("หลัง", size=26, color=C_MUTED),
            MathTex(r"\sqrt{n}", color=C_ACCENT).scale(1.0),
            th("รอบ → วัดครั้งเดียวได้คำตอบเกือบแน่นอน",
               size=26, color=C_POS, weight=BOLD),
        ).arrange(RIGHT, buff=0.2)
        conclusion.move_to(content_center(dy=-2.5))
        self.play(Write(conclusion))
        self.next_slide()

        self.play(*[FadeOut(m) for m in [
            header, mini_titles, *mini_charts, prob_labels, conclusion,
        ]])

    def slide_grover_pattern(self):
        header = title_bar("Pattern ที่ Shor จะใช้ซ้ำ")
        self.play(FadeIn(header))

        recipe = VGroup(
            VGroup(
                MathTex("1.", color=C_ACCENT).scale(0.95),
                th("เตรียม superposition เท่ากันทุกคำตอบ",
                   size=26, color=C_MUTED),
            ).arrange(RIGHT, buff=0.25),
            VGroup(
                MathTex("2.", color=C_ACCENT).scale(0.95),
                th("Oracle ใส่ phase ให้คำตอบที่ถูก",
                   size=26, color=C_MUTED),
            ).arrange(RIGHT, buff=0.25),
            VGroup(
                MathTex("3.", color=C_ACCENT).scale(0.95),
                th("Interference ขยาย amplitude ของคำตอบนั้น",
                   size=26, color=C_MUTED),
            ).arrange(RIGHT, buff=0.25),
            VGroup(
                MathTex("4.", color=C_ACCENT).scale(0.95),
                th("วัด — ได้คำตอบเกือบแน่นอน",
                   size=26, color=C_MUTED),
            ).arrange(RIGHT, buff=0.25),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        recipe.move_to(content_center(dy=0.7))
        for step in recipe:
            self.play(FadeIn(step, shift=RIGHT * 0.2))
        self.next_slide()

        shor = VGroup(
            th("Shor ใช้ recipe เดียวกัน —", size=26, color=C_POS),
            th("แต่ใช้ QFT แทน diffusion ในขั้น ขยาย amplitude",
               size=24, color=C_POS, weight=BOLD),
        ).arrange(DOWN, buff=0.15)
        shor.next_to(recipe, DOWN, buff=0.5)
        self.play(Write(shor))
        self.next_slide()
        self.play(*[FadeOut(m) for m in [header, recipe, shor]])

    # ----- Shor -----

    def slide_factoring_key(self):
        header = title_bar("Factoring → Period finding")
        self.play(FadeIn(header))

        setup = VGroup(
            MathTex(r"N = pq, \quad p,q").scale(1.0),
            th("เฉพาะคี่", size=30),
        ).arrange(RIGHT, buff=0.25)
        setup.next_to(header, DOWN, buff=0.4)
        self.play(Write(setup))

        key = th("Key identity: ถ้าเจอ y ที่...", size=28, color=C_MUTED)
        eq1 = MathTex(r"y^2 \equiv 1 \pmod N, \quad y \not\equiv \pm 1",
                      color=C_ACCENT).scale(1.1)
        eq2 = MathTex(r"(y-1)(y+1) \equiv 0 \pmod N").scale(1.0)
        grp = VGroup(key, eq1, eq2).arrange(DOWN, buff=0.35)
        grp.next_to(setup, DOWN, buff=0.5)
        self.play(FadeIn(key))
        self.play(Write(eq1))
        self.play(Write(eq2))
        self.next_slide()

        conc = VGroup(
            MathTex(r"\gcd(y-1, N)", color=C_POS).scale(1.1),
            th("คือเฉพาะของ", size=30, color=C_POS),
            MathTex("N", color=C_POS).scale(1.1),
        ).arrange(RIGHT, buff=0.25)
        conc.next_to(grp, DOWN, buff=0.4)
        self.play(Write(conc))
        euclid = th("Euclidean: O(n²) — classical หมด", size=24, color=C_MUTED)
        euclid.next_to(conc, DOWN, buff=0.25)
        self.play(FadeIn(euclid))
        self.next_slide()
        self.play(*[FadeOut(m) for m in [header, setup, grp, conc, euclid]])

    def slide_order_finding(self):
        header = title_bar("หา y ยังไง?")
        self.play(FadeIn(header))

        steps = VGroup(
            th("1) สุ่ม a ที่ gcd(a, N) = 1", size=30),
            th("2) หา order r — เลขเล็กสุดที่...", size=30),
            MathTex(r"a^r \equiv 1 \pmod N", color=C_ACCENT).scale(1.1),
            th("3) ถ้า r เป็นเลขคู่ ตั้ง y = a^(r/2)", size=30),
            MathTex(r"y^2 = a^r \equiv 1 \pmod N \;\checkmark",
                    color=C_POS).scale(1.0),
        ).arrange(DOWN, buff=0.35)
        steps.next_to(header, DOWN, buff=0.5)

        for s in steps:
            self.play(FadeIn(s, shift=UP * 0.15))
        self.next_slide()
        self.play(FadeOut(header), FadeOut(steps))

    # ----- Classical part of Shor -----

    def slide_shor_roadmap(self):
        header = title_bar("Shor's algorithm: ภาพรวม")
        self.play(FadeIn(header))

        intro = th("ขั้นตอนของ Shor ทั้งหมด (N = 15 เป็นตัวอย่าง)",
                   size=24, color=C_MUTED)
        intro.next_to(header, DOWN, buff=0.25)
        self.play(FadeIn(intro))

        # 4 steps in boxes
        box_specs = [
            ("สุ่ม", MathTex("a", color=WHITE).scale(0.9), "classical"),
            ("หา order", MathTex("r", color=C_ACCENT).scale(1.1), "quantum"),
            ("คำนวณ", MathTex("y = a^{r/2}", color=WHITE).scale(0.8),
             "classical"),
            ("gcd", MathTex(r"\gcd(y \pm 1, N)",
                            color=WHITE).scale(0.7), "classical"),
        ]

        boxes = VGroup()
        kind_labels = VGroup()
        for label_txt, math_obj, kind in box_specs:
            rect = Rectangle(width=2.3, height=1.4,
                             color=(C_ACCENT if kind == "quantum"
                                    else C_MUTED),
                             stroke_width=(3 if kind == "quantum" else 1.5))
            top_lbl = th(label_txt, size=22,
                         color=(C_ACCENT if kind == "quantum" else C_MUTED))
            top_lbl.move_to(rect.get_center() + UP * 0.3)
            math_obj.move_to(rect.get_center() + DOWN * 0.25)
            kind_lbl = th(kind, size=16,
                          color=(C_ACCENT if kind == "quantum" else C_MUTED))
            kind_lbl.next_to(rect, DOWN, buff=0.1)
            boxes.add(VGroup(rect, top_lbl, math_obj))
            kind_labels.add(kind_lbl)

        boxes.arrange(RIGHT, buff=0.35)
        boxes.move_to(content_center(dy=0.3))

        for kl, bx in zip(kind_labels, boxes):
            kl.next_to(bx, DOWN, buff=0.1)

        # Arrows between boxes
        arrows = VGroup()
        for i in range(3):
            arr = Arrow(boxes[i].get_right(), boxes[i + 1].get_left(),
                        color=C_MUTED, stroke_width=3,
                        buff=0.1, tip_length=0.2)
            arrows.add(arr)

        for i, (bx, kl) in enumerate(zip(boxes, kind_labels)):
            self.play(FadeIn(bx), FadeIn(kl), run_time=0.35)
            if i < 3:
                self.play(GrowArrow(arrows[i]), run_time=0.25)
        self.next_slide()

        punch = VGroup(
            th("ขั้นที่ 2 (หา order r) คือขั้นที่", size=24, color=C_MUTED),
            th("ยากที่สุด", size=24, color=C_NEG, weight=BOLD),
            th("— classical: exponential, quantum: polynomial",
               size=22, color=C_ACCENT),
        ).arrange(RIGHT, buff=0.15)
        punch.next_to(kind_labels, DOWN, buff=0.6)
        self.play(Write(punch))
        self.next_slide()

        self.play(*[FadeOut(m) for m in [header, intro, boxes,
                                          kind_labels, arrows, punch]])

    def slide_factoring_trick(self):
        header = title_bar("ขั้น 3–4: รากพิเศษของ 1 → gcd")
        self.play(FadeIn(header))

        # Act 1: the identity
        claim = VGroup(
            th("ถ้าเจอ", size=24, color=C_MUTED),
            MathTex("y", color=C_MUTED).scale(0.95),
            th("ที่", size=24, color=C_MUTED),
            MathTex(r"y^2 \equiv 1 \pmod N,\; y \not\equiv \pm 1",
                    color=C_ACCENT).scale(1.0),
        ).arrange(RIGHT, buff=0.2)

        arrow = MathTex(r"\Downarrow", color=C_MUTED).scale(0.9)

        step2 = MathTex(r"(y-1)(y+1) \equiv 0 \pmod N",
                        color=WHITE).scale(1.0)

        gcd_line = MathTex(
            r"\gcd(y \pm 1,\, N) \;=\; \text{factor of } N",
            color=C_POS).scale(1.0)

        act1 = VGroup(claim, arrow, step2, gcd_line).arrange(DOWN, buff=0.35)
        act1.move_to(content_center(dy=0.1))

        self.play(Write(claim))
        self.next_slide()
        self.play(FadeIn(arrow), Write(step2))
        self.next_slide()
        self.play(Write(gcd_line))
        self.next_slide()

        self.play(FadeOut(act1))

        # Act 2: verify with N = 15
        subtitle = VGroup(
            th("ลองหาใน", size=22, color=C_MUTED),
            MathTex("N = 15", color=C_ACCENT).scale(0.9),
            th("— มี y ∈ {1, 4, 11, 14} ที่", size=22, color=C_MUTED),
            MathTex(r"y^2 \equiv 1", color=C_MUTED).scale(0.85),
        ).arrange(RIGHT, buff=0.2)
        subtitle.next_to(header, DOWN, buff=0.3)
        self.play(FadeIn(subtitle))

        header_row = ["y", r"\gcd(y-1,\,15)", r"\gcd(y+1,\,15)", "ผล"]
        header_kinds = ["math", "math", "math", "text"]
        rows_data = [
            [("math", "1"),  ("math", "15"), ("math", "1"),  ("text", "—")],
            [("math", "4"),  ("math", "3"),  ("math", "5"),  ("text", "✓")],
            [("math", "11"), ("math", "5"),  ("math", "3"),  ("text", "✓")],
            [("math", "14"), ("math", "1"),  ("math", "15"), ("text", "—")],
        ]
        useful_rows = [False, True, True, False]
        col_x = [-4.8, -1.7, 1.7, 4.6]
        row_h = 0.65

        def make_mobj(kind, content, color):
            if kind == "math":
                return MathTex(content, color=color).scale(0.85)
            return Text(content, font=TH_FONT, font_size=24, color=color)

        # Header row
        header_mobjs = VGroup()
        for j, (kind, h) in enumerate(zip(header_kinds, header_row)):
            m = make_mobj(kind, h, C_ACCENT)
            m.move_to([col_x[j], 0, 0])
            header_mobjs.add(m)

        underline = Line(
            [col_x[0] - 0.5, -row_h * 0.55, 0],
            [col_x[-1] + 0.5, -row_h * 0.55, 0],
            color=C_MUTED, stroke_width=1.5,
        )

        # Data rows
        row_mobjs = VGroup()
        for i, (row, useful) in enumerate(zip(rows_data, useful_rows)):
            y = -(i + 1) * row_h - 0.1
            color = C_POS if useful else C_MUTED
            for j, (kind, content) in enumerate(row):
                m = make_mobj(kind, content, color)
                m.move_to([col_x[j], y, 0])
                row_mobjs.add(m)

        full_table = VGroup(header_mobjs, underline, row_mobjs)
        full_table.next_to(subtitle, DOWN, buff=0.4)

        self.play(FadeIn(header_mobjs), Create(underline))
        for i in range(4):
            slice_ = row_mobjs[i * 4:(i + 1) * 4]
            self.play(FadeIn(slice_, shift=UP * 0.1), run_time=0.3)
        self.next_slide()

        # Fade failed rows, strikethrough
        fade_targets = VGroup(
            row_mobjs[0], row_mobjs[1], row_mobjs[2], row_mobjs[3],
            row_mobjs[12], row_mobjs[13], row_mobjs[14], row_mobjs[15],
        )

        def strike(row_idx):
            cells = row_mobjs[row_idx * 4:(row_idx + 1) * 4]
            start = cells[0].get_left() + LEFT * 0.25
            end = cells[-1].get_right() + RIGHT * 0.25
            return Line(start, end, color=C_MUTED, stroke_width=1.5)

        strikes = VGroup(strike(0), strike(3))
        self.play(
            fade_targets.animate.set_opacity(0.35),
            Create(strikes[0]), Create(strikes[1]),
        )

        # Payoff line
        r1_gcd_left = row_mobjs[1 * 4 + 1]   # "3"
        r1_gcd_right = row_mobjs[1 * 4 + 2]  # "5"

        factor_line = MathTex(
            r"15", r"=", r"3", r"\times", r"5",
        ).scale(1.4)
        factor_line[0].set_color(WHITE)
        factor_line[1].set_color(WHITE)
        factor_line[2].set_color(C_POS)
        factor_line[3].set_color(WHITE)
        factor_line[4].set_color(C_POS)
        factor_line.next_to(full_table, DOWN, buff=0.35)

        self.play(
            TransformFromCopy(r1_gcd_left, factor_line[2]),
            TransformFromCopy(r1_gcd_right, factor_line[4]),
            FadeIn(factor_line[0]), FadeIn(factor_line[1]),
            FadeIn(factor_line[3]),
        )
        self.next_slide()

        self.play(*[FadeOut(m) for m in [
            header, subtitle, full_table, strikes, factor_line,
        ]])

    def slide_order_finding(self):
        header = title_bar("หา y จาก order ของ a")
        self.play(FadeIn(header))

        # Left: concept
        concept = VGroup(
            th("Trick:", size=26, color=C_ACCENT),
            VGroup(
                th("1) สุ่ม", size=22, color=C_MUTED),
                MathTex("a", color=WHITE).scale(0.85),
            ).arrange(RIGHT, buff=0.15),
            VGroup(
                th("2) ยกกำลังไปเรื่อยๆ จนได้ 1", size=22, color=C_MUTED),
            ),
            MathTex(r"a,\; a^2,\; a^3,\; \ldots \to 1",
                    color=WHITE).scale(0.9),
            VGroup(
                th("3)", size=22, color=C_MUTED),
                MathTex("r", color=C_ACCENT).scale(0.85),
                th("= จำนวนก้าวที่ใช้ (เรียกว่า order)",
                   size=22, color=C_MUTED),
            ).arrange(RIGHT, buff=0.15),
            VGroup(
                th("4)", size=22, color=C_MUTED),
                MathTex(r"y = a^{r/2}", color=C_POS).scale(0.9),
            ).arrange(RIGHT, buff=0.15),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        concept.move_to(content_center(x=-3.7, dy=-0.2))

        self.play(FadeIn(concept[0]))
        self.play(FadeIn(concept[1]))
        self.play(FadeIn(concept[2]), FadeIn(concept[3]))
        self.play(FadeIn(concept[4]))
        self.play(FadeIn(concept[5]))
        self.next_slide()

        # Right: concrete example with modular clock
        demo_title = VGroup(
            th("ลอง", size=22, color=C_MUTED),
            MathTex("N = 15,\\; a = 2", color=C_ACCENT).scale(0.85),
        ).arrange(RIGHT, buff=0.2)
        demo_title.move_to(content_center(x=2.8, dy=2.9))
        self.play(FadeIn(demo_title))

        N = 15
        radius = 1.15
        center = content_center(x=2.8, dy=0.55)
        clock = VGroup()
        positions = {}
        for i in range(N):
            angle = PI / 2 - 2 * PI * i / N
            direction = np.array([np.cos(angle), np.sin(angle), 0])
            pos = center + radius * direction
            positions[i] = pos
            dot = Dot(pos, color=C_MUTED, radius=0.05)
            lab = MathTex(str(i), color=C_MUTED).scale(0.45)
            lab.move_to(center + (radius + 0.25) * direction)
            clock.add(dot, lab)
        self.play(FadeIn(clock))

        sequence = [1, 2, 4, 8, 1]
        walker = Dot(positions[1], color=C_ACCENT, radius=0.1)
        self.play(FadeIn(walker, scale=1.5))

        arrows = VGroup()
        for i in range(len(sequence) - 1):
            a_pos = positions[sequence[i]]
            b_pos = positions[sequence[i + 1]]
            arr = CurvedArrow(a_pos, b_pos, color=C_POS,
                              angle=-TAU / 6, tip_length=0.12)
            self.play(walker.animate.move_to(b_pos),
                      Create(arr), run_time=0.5)
            arrows.add(arr)
        self.next_slide()

        # Result panel
        result = VGroup(
            MathTex(r"r = 4", color=C_ACCENT).scale(0.9),
            MathTex(r"y = 2^{r/2} = 4", color=C_POS).scale(0.85),
            th("← ตรงกับรากพิเศษจากก่อนหน้า!",
               size=18, color=C_POS, weight=BOLD),
        ).arrange(DOWN, buff=0.1)
        result.next_to(clock, DOWN, buff=0.2)
        self.play(FadeIn(result))
        self.next_slide()

        self.play(*[FadeOut(m) for m in [
            header, concept, demo_title, clock, walker, arrows, result,
        ]])

    def slide_shor_caveats(self):
        header = title_bar("ถ้าโชคไม่ดีล่ะ?")
        self.play(FadeIn(header))

        case1 = VGroup(
            MathTex("r", color=WHITE).scale(0.9),
            th("ออกมาเป็นเลขคี่ →", size=24, color=C_MUTED),
            MathTex(r"r/2", color=WHITE).scale(0.85),
            th("ใช้ไม่ได้", size=24, color=C_MUTED),
        ).arrange(RIGHT, buff=0.2)

        case2 = VGroup(
            MathTex("y", color=WHITE).scale(0.9),
            th("ออกมาเป็น", size=24, color=C_MUTED),
            MathTex(r"\pm 1", color=WHITE).scale(0.85),
            th("— ไม่ใช่รากพิเศษ", size=24, color=C_MUTED),
        ).arrange(RIGHT, buff=0.2)

        cases = VGroup(case1, case2).arrange(DOWN, buff=0.3)
        cases.move_to(content_center(dy=1.6))
        self.play(FadeIn(cases))
        self.next_slide()

        good = VGroup(
            th("ข่าวดี: สุ่ม", size=26, color=C_POS),
            MathTex("a", color=C_POS).scale(0.9),
            th("ครั้งเดียวสำเร็จ ≥", size=26, color=C_POS),
            MathTex(r"50\%", color=C_POS).scale(1.0),
        ).arrange(RIGHT, buff=0.2)
        good.move_to(content_center(dy=0.1))
        self.play(Write(good))

        retry = th("โชคร้าย → สุ่มใหม่ เฉลี่ย 2 รอบก็จบ",
                   size=22, color=C_MUTED)
        retry.next_to(good, DOWN, buff=0.3)
        self.play(FadeIn(retry))
        self.next_slide()

        multi = VGroup(
            th("ถ้า N มีตัวประกอบเฉพาะมากกว่า 2 →",
               size=22, color=C_MUTED),
            th("recurse แยกต่อได้ ไม่เกิน", size=22, color=C_MUTED),
            MathTex(r"\log_2 N", color=C_ACCENT).scale(0.85),
            th("รอบ", size=22, color=C_MUTED),
        ).arrange(RIGHT, buff=0.15)
        multi.next_to(retry, DOWN, buff=0.4)
        self.play(FadeIn(multi))
        self.next_slide()

        conclusion = th("เหลือปัญหาเดียว: หา order r — ถึงคิว quantum",
                        size=26, color=C_ACCENT, weight=BOLD)
        conclusion.next_to(multi, DOWN, buff=0.5)
        self.play(Write(conclusion))
        self.next_slide()

        self.play(*[FadeOut(m) for m in [
            header, cases, good, retry, multi, conclusion,
        ]])

    # ----- Quantum part of Shor -----

    def _register_strip(self, values, center_y, label_text, color_fn,
                        cell_w=0.55, cell_h=0.55, gap=0.08):
        """Build a horizontal strip of numbered cells."""
        n = len(values)
        total_w = n * cell_w + (n - 1) * gap
        x0 = -total_w / 2
        cells = VGroup()
        texts = VGroup()
        for i, v in enumerate(values):
            x = x0 + i * (cell_w + gap) + cell_w / 2
            color = color_fn(i)
            cell = Rectangle(
                width=cell_w, height=cell_h,
                fill_color=color, fill_opacity=0.15,
                stroke_color=color, stroke_width=1.5,
            )
            cell.move_to([x, center_y, 0])
            cells.add(cell)
            t = MathTex(str(v), color=color).scale(0.55)
            t.move_to(cell.get_center())
            texts.add(t)
        label = th(label_text, size=20, color=C_MUTED)
        label.move_to([x0 - 0.4, center_y, 0])
        label.shift(LEFT * (label.width / 2 + 0.1))
        return VGroup(cells, texts, label), cells, texts

    def slide_shor_parallel(self):
        header = title_bar("Step 1: คำนวณ f(k) ทุก k พร้อมกัน")
        self.play(FadeIn(header))

        intro = VGroup(
            th("เราอยากหา r ของ", size=24, color=C_MUTED),
            MathTex(r"f(k) = 2^k \bmod 15",
                    color=C_ACCENT).scale(0.9),
        ).arrange(RIGHT, buff=0.25)
        intro.next_to(header, DOWN, buff=0.2)
        self.play(FadeIn(intro))

        N = 15
        a = 2
        K = 16
        k_values = list(range(K))
        f_values = [pow(a, k, N) for k in k_values]

        input_strip, input_cells, input_texts = self._register_strip(
            k_values,
            center_y=CONTENT_CENTER_Y + 0.6,
            label_text="k",
            color_fn=lambda i: WHITE,
        )

        # Step: input superposition
        self.play(FadeIn(input_strip))
        sp_note = th("input register: superposition ของทุก k (amplitude เท่ากัน)",
                     size=20, color=C_MUTED)
        sp_note.next_to(input_strip, UP, buff=1.0)
        self.play(FadeIn(sp_note))
        self.next_slide()

        # Reveal output strip (initially all 0s)
        zero_strip, zero_cells, zero_texts = self._register_strip(
            [0] * K,
            center_y=CONTENT_CENTER_Y - 0.5,
            label_text="f(k)",
            color_fn=lambda i: C_MUTED,
        )
        self.play(FadeIn(zero_strip))
        zero_note = VGroup(
            th("output register เริ่มที่", size=20, color=C_MUTED),
            MathTex(r"|0\rangle", color=C_MUTED).scale(0.75),
            th("ทุกตัว", size=20, color=C_MUTED),
        ).arrange(RIGHT, buff=0.15)
        zero_note.next_to(zero_strip, DOWN, buff=0.3)
        self.play(FadeIn(zero_note))
        self.next_slide()

        # Show the unitary action on a single basis state first
        single_explain = VGroup(
            th("Quantum gate", size=20, color=C_ACCENT),
            MathTex(r"U_f", color=C_ACCENT).scale(0.85),
            th("ทำงานแบบนี้:", size=20, color=C_ACCENT),
            MathTex(r"|k\rangle |0\rangle \;\to\; |k\rangle |f(k)\rangle",
                    color=C_ACCENT).scale(0.85),
        ).arrange(RIGHT, buff=0.15)
        single_explain.move_to(zero_note)
        self.play(Transform(zero_note, single_explain))

        # Highlight one example: k=2, f(2) = 4
        ex_input = SurroundingRectangle(input_cells[2], color=C_POS,
                                        buff=0.05, stroke_width=3)
        ex_output = SurroundingRectangle(zero_cells[2], color=C_POS,
                                         buff=0.05, stroke_width=3)
        ex_label = MathTex(
            r"|2\rangle|0\rangle \to |2\rangle|4\rangle",
            color=C_POS).scale(0.7)
        ex_label.next_to(ex_input, UP, buff=0.2)
        self.play(Create(ex_input), Create(ex_output))
        # Update the example output cell content to show 4
        new_4 = MathTex("4", color=C_POS).scale(0.55)
        new_4.move_to(zero_texts[2])
        self.play(Transform(zero_texts[2], new_4),
                  zero_cells[2].animate.set_stroke(C_POS).set_fill(
                      C_POS, opacity=0.3))
        self.play(Write(ex_label))
        self.next_slide()

        # Now apply to all k in superposition simultaneously
        self.play(FadeOut(ex_input), FadeOut(ex_output), FadeOut(ex_label))

        apply_note = th(
            "เพราะ input อยู่ใน superposition → gate ครั้งเดียว"
            " ทำงานพร้อมกันทุก k",
            size=20, color=C_POS)
        apply_note.move_to(zero_note)
        self.play(Transform(zero_note, apply_note))

        # Update all output cells to actual f(k) values
        anims = []
        for i in range(K):
            new_text = MathTex(str(f_values[i]),
                               color=C_ACCENT).scale(0.55)
            new_text.move_to(zero_texts[i])
            anims.append(Transform(zero_texts[i], new_text))
            anims.append(zero_cells[i].animate.set_stroke(
                C_ACCENT).set_fill(C_ACCENT, opacity=0.15))
        self.play(*anims)
        self.next_slide()

        # Replace the placeholder strip references with actual ones
        out_strip = zero_strip
        out_cells = zero_cells
        out_texts = zero_texts
        apply_note_ref = zero_note

        # Highlight periodic pattern — same color for same f value
        palette = {
            1: C_ACCENT,
            2: "#ff9ecd",
            4: "#66d9ff",
            8: "#ffdb66",
        }
        self.play(*[
            out_cells[i].animate.set_stroke(palette[f_values[i]]).set_fill(
                palette[f_values[i]], opacity=0.3)
            for i in range(K)
        ] + [
            out_texts[i].animate.set_color(palette[f_values[i]])
            for i in range(K)
        ])

        pattern = th("สังเกต: f(k) วนซ้ำทุก 4 ตัว — คาบ r = 4",
                     size=24, color=C_POS, weight=BOLD)
        pattern.move_to(apply_note_ref)
        self.play(Transform(apply_note_ref, pattern))
        self.next_slide()

        self.shor_input_strip = input_strip
        self.shor_input_cells = input_cells
        self.shor_input_texts = input_texts
        self.shor_out_strip = out_strip
        self.shor_out_cells = out_cells
        self.shor_out_texts = out_texts
        self.shor_header = header
        self.shor_intro = intro
        self.shor_top_note = sp_note
        self.shor_bot_note = apply_note_ref
        self.shor_palette = palette
        self.shor_f_values = f_values

    def slide_shor_collapse(self):
        # Change header
        new_header = title_bar("Step 2: วัด output → input ยุบเหลือ AP")
        self.play(Transform(self.shor_header, new_header))

        new_top = th("สมมติวัด output register ได้ค่า 8",
                     size=22, color=C_ACCENT)
        new_top.move_to(self.shor_top_note)
        self.play(Transform(self.shor_top_note, new_top))

        # Keep only k's where f(k) == 8; fade the rest
        keep_k = [i for i, v in enumerate(self.shor_f_values) if v == 8]
        drop_k = [i for i in range(len(self.shor_f_values)) if i not in keep_k]

        self.play(*(
            [self.shor_input_cells[i].animate.set_opacity(0.15)
             for i in drop_k]
            + [self.shor_input_texts[i].animate.set_opacity(0.15)
               for i in drop_k]
            + [self.shor_out_cells[i].animate.set_opacity(0.15)
               for i in drop_k]
            + [self.shor_out_texts[i].animate.set_opacity(0.15)
               for i in drop_k]
            + [self.shor_input_cells[i].animate.set_stroke(
                C_POS).set_fill(C_POS, opacity=0.35)
               for i in keep_k]
            + [self.shor_input_texts[i].animate.set_color(C_POS)
               for i in keep_k]
        ))
        self.next_slide()

        # Annotate the surviving k's as an AP with spacing r
        surviving_cells = [self.shor_input_cells[i] for i in keep_k]
        y_above = surviving_cells[0].get_top()[1] + 0.6
        arrow_y = surviving_cells[0].get_top()[1] + 0.15

        bracket_items = VGroup()
        for i in range(len(surviving_cells) - 1):
            a_pt = surviving_cells[i].get_top() + UP * 0.08
            b_pt = surviving_cells[i + 1].get_top() + UP * 0.08
            br = DoubleArrow(a_pt, b_pt, color=C_ACCENT,
                             stroke_width=2, tip_length=0.12, buff=0)
            mid = (a_pt + b_pt) / 2
            lbl = MathTex("r", color=C_ACCENT).scale(0.7)
            lbl.move_to([mid[0], mid[1] + 0.2, 0])
            bracket_items.add(br, lbl)
        self.play(FadeIn(bracket_items))
        self.next_slide()

        insight = VGroup(
            th("k ที่เหลือห่างกันเท่ากับคาบ", size=24, color=C_POS),
            MathTex("r = 4", color=C_POS).scale(0.9),
            th("— คาบถูกฝังอยู่ในระยะห่าง",
               size=24, color=C_POS, weight=BOLD),
        ).arrange(RIGHT, buff=0.2)
        insight.move_to(self.shor_bot_note)
        self.play(Transform(self.shor_bot_note, insight))
        self.next_slide()

        self.shor_bracket_items = bracket_items
        self.shor_keep_k = keep_k

    def slide_shor_qft(self):
        new_header = title_bar("Step 3: QFT ดึงคาบออกมาเป็นความถี่")
        self.play(Transform(self.shor_header, new_header))

        # Fade out old visuals except header
        self.play(*[FadeOut(m) for m in [
            self.shor_intro, self.shor_top_note, self.shor_bot_note,
            self.shor_input_strip, self.shor_out_strip,
            self.shor_bracket_items,
        ]])

        analogy = th("เหมือน Fourier — แปลงคาบให้เป็น peak ที่ความถี่",
                     size=20, color=C_MUTED)
        analogy.next_to(self.shor_header, DOWN, buff=0.15)
        self.play(FadeIn(analogy))

        # Time-domain: AP spikes at 3, 7, 11, 15 (matches collapse: f(k)=8)
        ax_time = Axes(
            x_range=[0, 16, 4], y_range=[0, 1.2, 0.5],
            x_length=9, y_length=1.0,
            axis_config={"color": C_MUTED, "include_tip": False},
        )
        time_label = th("Before: k เหลือ = {3, 7, 11, 15}",
                        size=18, color=C_ACCENT)
        time_label.next_to(analogy, DOWN, buff=0.2)
        ax_time.next_to(time_label, DOWN, buff=0.1)
        self.play(Create(ax_time), FadeIn(time_label))

        time_bars = VGroup()
        for k in [3, 7, 11, 15]:
            bar = Line(ax_time.c2p(k, 0), ax_time.c2p(k, 1.0),
                       color=C_ACCENT, stroke_width=5)
            time_bars.add(bar)
        self.play(LaggedStart(*[Create(b) for b in time_bars],
                              lag_ratio=0.1))
        self.next_slide()

        # Prism
        prism = Triangle(color=C_ACCENT, fill_opacity=0.3).scale(0.2)
        prism.next_to(ax_time, DOWN, buff=0.15)
        qft_lbl = MathTex(r"\text{QFT}", color=C_ACCENT).scale(0.7)
        qft_lbl.next_to(prism, RIGHT, buff=0.1)
        self.play(FadeIn(prism), Write(qft_lbl))

        # Frequency domain: spikes at multiples of 16/r = 4
        ax_freq = Axes(
            x_range=[0, 16, 4], y_range=[0, 1.2, 0.5],
            x_length=9, y_length=1.0,
            axis_config={"color": C_MUTED, "include_tip": False},
        )
        ax_freq.next_to(prism, DOWN, buff=0.15)
        freq_label = th("After: spike ที่ j = 0, 4, 8, 12  (ห่างกัน 2²ⁿ/r)",
                        size=18, color=C_POS)
        freq_label.next_to(ax_freq, DOWN, buff=0.1)
        self.play(Create(ax_freq))

        freq_bars = VGroup()
        for j in range(16):
            if j % 4 == 0:
                h = 1.0
                col = C_POS
            else:
                h = 0.05
                col = C_MUTED
            bar = Line(ax_freq.c2p(j, 0), ax_freq.c2p(j, h),
                       color=col, stroke_width=4)
            freq_bars.add(bar)
        self.play(LaggedStart(*[Create(b) for b in freq_bars],
                              lag_ratio=0.04),
                  FadeIn(freq_label))
        self.next_slide()

        # How to actually extract r — measure once + continued fraction
        explain1 = th("วัดครั้งเดียว → ได้ค่า j สุ่มจากบรรดา spike",
                      size=18, color=C_POS)

        explain2 = VGroup(
            MathTex(r"\tfrac{j}{2^{2n}} \approx \tfrac{c}{r}",
                    color=C_ACCENT).scale(0.75),
            th("→ continued fraction ดึง r ออกมา",
               size=18, color=C_ACCENT),
        ).arrange(RIGHT, buff=0.2)

        retry = th("ถ้าโชคไม่ดี (c กับ r มีตัวประกอบร่วม) → ลองใหม่",
                   size=16, color=C_MUTED)

        conclusion_block = VGroup(explain1, explain2, retry).arrange(
            DOWN, buff=0.1)
        conclusion_block.to_edge(DOWN, buff=0.2)
        self.play(Write(explain1))
        self.next_slide()
        self.play(Write(explain2), FadeIn(retry))
        self.next_slide()

        self.play(*[FadeOut(m) for m in [
            self.shor_header, analogy, ax_time, time_label, time_bars,
            prism, qft_lbl, ax_freq, freq_label, freq_bars,
            conclusion_block,
        ]])

    def slide_shor_recover(self):
        header = title_bar("ได้ r แล้ว — ปิดจ็อบ!")
        self.play(FadeIn(header))

        chain = VGroup(
            VGroup(
                th("Quantum step บอกว่า", size=24, color=C_MUTED),
                MathTex("r = 4", color=C_ACCENT).scale(1.0),
            ).arrange(RIGHT, buff=0.25),
            VGroup(
                th("ย้อนสูตร:", size=24, color=C_MUTED),
                MathTex(r"y = 2^{r/2} = 2^2 = 4",
                        color=WHITE).scale(0.95),
            ).arrange(RIGHT, buff=0.25),
            VGroup(
                th("gcd:", size=24, color=C_MUTED),
                MathTex(r"\gcd(3, 15) = 3,\;\; \gcd(5, 15) = 5",
                        color=C_POS).scale(0.9),
            ).arrange(RIGHT, buff=0.25),
            VGroup(
                MathTex(r"15 = 3 \times 5",
                        color=C_POS).scale(1.4),
                th("  แยกตัวประกอบสำเร็จ!",
                   size=28, color=C_POS, weight=BOLD),
            ).arrange(RIGHT, buff=0.3),
        ).arrange(DOWN, buff=0.4)
        chain.move_to(content_center())

        for item in chain:
            self.play(FadeIn(item, shift=UP * 0.1))
        self.next_slide()
        self.play(FadeOut(header), FadeOut(chain))

    def slide_tradeoffs(self):
        header = title_bar("Time & Space tradeoff")
        self.play(FadeIn(header))

        table = VGroup()
        rows = [
            ["", "Classical (GNFS)", "Shor"],
            ["Time", "exp(O(n^(1/3)))", "O(n² log n)"],
            ["Space", "O(n)", "O(n) qubits"],
        ]
        cell_w = 3.8
        cell_h = 0.9
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                rect = Rectangle(width=cell_w, height=cell_h,
                                 stroke_color=C_MUTED, stroke_width=1)
                rect.move_to([(j - 1) * cell_w, -i * cell_h, 0])
                if i == 0:
                    rect.set_fill(C_ACCENT, opacity=0.2)
                txt = Text(val, font=TH_FONT, font_size=26,
                           color=WHITE if i > 0 else C_ACCENT)
                txt.move_to(rect.get_center())
                table.add(rect, txt)
        table.move_to(ORIGIN).shift(DOWN * 0.3)
        self.play(FadeIn(table))
        self.next_slide()

        punch = th("RSA-2048 แตกด้วย ~6000 logical qubits",
                   size=32, color=C_NEG, weight=BOLD)
        punch.next_to(table, DOWN, buff=0.6)
        self.play(Write(punch))
        self.next_slide()
        self.play(*[FadeOut(m) for m in [header, table, punch]])

    def slide_reality(self):
        header = title_bar("Reality check")
        self.play(FadeIn(header))

        lines = VGroup(
            th("logical ≠ physical qubits", size=32, color=C_ACCENT),
            th("error correction: physical หลักล้าน ต่อ logical 1 ตัว", size=28),
            th("hardware ตอนนี้: ~1000 physical qubits + noise เยอะ", size=28),
            th("→ ยังห่างไกล", size=30, color=C_MUTED),
        ).arrange(DOWN, buff=0.35)
        lines.next_to(header, DOWN, buff=0.5)
        for l in lines:
            self.play(FadeIn(l, shift=UP * 0.1))
        self.next_slide()

        warn = VGroup(
            th("แต่ข้อมูลที่ถูกดักวันนี้...", size=30),
            th('"Harvest now, decrypt later"',
               size=34, color=C_NEG, weight=BOLD),
            th("→ post-quantum crypto เริ่มใช้งานแล้ว", size=28, color=C_POS),
        ).arrange(DOWN, buff=0.3)
        warn.next_to(lines, DOWN, buff=0.5)
        self.play(Write(warn))
        self.next_slide()
        self.play(*[FadeOut(m) for m in [header, lines, warn]])

    def slide_end(self):
        end = th("ขอบคุณครับ", size=72, color=C_ACCENT, weight=BOLD)
        q = th("Questions?", size=36, color=C_MUTED)
        q.next_to(end, DOWN, buff=0.4)
        self.play(FadeIn(end, shift=UP * 0.3), FadeIn(q))
        self.next_slide()
