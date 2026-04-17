"""Shor's Algorithm presentation (~10 min, Thai, non-quantum audience).

Run:
    manim-slides render slides.py ShorTalk
    manim-slides ShorTalk
"""

# ruff: noqa: F405
from manim import *  # noqa: F403
from manim_slides import Slide
import numpy as np

TH_FONT = "Tahoma"  # ships with Windows, supports Thai

# Frame is y in [-4, 4]. Header occupies top ~1.2 units (title text + underline).
# Treat the remaining area as the "content box" and center things in it.
CONTENT_TOP_Y = 2.6
CONTENT_BOTTOM_Y = -3.8
CONTENT_CENTER_Y = (CONTENT_TOP_Y + CONTENT_BOTTOM_Y) / 2  # ≈ -0.6

# --- Shared Constants ---
T_INIT = "เริ่มด้วย amplitude เท่ากัน"
T_STEP1 = "Step 1: Oracle ทำงานบน superposition"
T_STEP2 = "Step 2: Diffusion"
T_PROB_1_8 = "ทุกตัวมีโอกาสถูกเลือก 1/8 เท่ากัน"
T_ORACLE_X = "oracle call 1 ครั้ง ทำงานพร้อมกันทุก x"
T_FINAL = "หลัง 1 รอบ: โอกาสถูก ≈ 78%"

HEADER_BUFF = 0.2
CHART_MARK = 6
AMP_INIT = 1 / np.sqrt(8)


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
C_MUTED = "#dae2ff"

config.background_color = C_BG


def th(text, size=36, color=WHITE, weight=NORMAL):
    return Text(text, font=TH_FONT, font_size=size, color=color, weight=weight)


def title_bar(text):
    t = th(text, size=40, color=C_ACCENT, weight=BOLD)
    t.to_edge(UP, buff=HEADER_BUFF)
    line = Line(LEFT * 6, RIGHT * 6, color=C_ACCENT, stroke_width=2)
    line.next_to(t, DOWN, buff=0.2)
    return VGroup(t, line)


# --- Shared Constants ---
S_K_SUP = "สร้าง Superposition ของทุก k"
S_GATE = "ใส่ Quantum Gate ทำงานพร้อมกันทุก k (Parallelism)"
S_COLLAPSE = "วัดค่า Output: ระบบยุบตัวเหลือเพียง k ที่มีคาบเดียวกัน"
S_QFT = "ใช้ QFT แปลงระยะห่างเป็นความถี่เพื่อดึงค่า r"
S_RESULT = "f(k) วนซ้ำทุก 4 ตัว คือคาบ r = 4"

K_VALS = 12
F_PATTERN = [1, 2, 4, 8, 1, 2, 4, 8, 1, 2, 4, 8]
PALETTE = {1: C_ACCENT, 2: "#ff9ecd", 4: "#66d9ff", 8: "#ffdb66"}


class ShorTalk(Slide):
    def play(self, *anims, run_time=None, **kwargs):
        # Snappier default: text/FadeIn/Write at 0.5s instead of manim's 1.0s.
        # Explicit run_time overrides (e.g. walker.animate) still win.
        if run_time is None:
            run_time = 0.5
        super().play(*anims, run_time=run_time, **kwargs)

    def construct(self):
        self.title()
        self.QuantumIntro()
        self.QubitBasic()
        self.Why2n()
        self.QuantumSpeedup()
        self.GroverProblem()
        self.GroverIteration()
        self.GroverIterate()
        # self.GroverPattern()
        self.FactoringKey()
        self.FactoringTrickExample()
        self.ShorFindOrder()
        self.ShorSteps()
        self.ShorRecover()
        self.ShorCaveats()
        self.end()

        # ----- slides -----

        # def slide_hook(self):
        #     header = title_bar("ทำไมเราถึงควรสนใจ?")
        #

        #     lines = VGroup(
        #         th("ทุกครั้งที่เราเข้าเว็บผ่าน https", size=28),
        #         th("เรากำลังเชื่อใจสมมติฐานที่ว่า", size=28),
        #         th('"การแยกตัวประกอบของเลขใหญ่ๆ เป็นเรื่องยาก"',
        #            size=28, color=C_ACCENT),
        #         th("ซึ่งเป็นรากฐานของระบบ RSA", size=26, color=C_MUTED),
        #     ).arrange(DOWN, buff=0.2)

    def _bars(self, values, colors=None, highlight=None):
        n = len(values)
        chart = VGroup()
        width = 0.7
        gap = 0.25
        total_w = n * width + (n - 1) * gap
        x0 = -total_w / 2
        labels = ["000", "001", "010", "011", "100", "101", "110", "111"]
        axis = Line(
            LEFT * (total_w / 2 + 0.3), RIGHT * (total_w / 2 + 0.3), color=C_MUTED
        ).shift(DOWN * 0.05)
        chart.add(axis)
        for i, v in enumerate(values):
            col = C_POS if v >= 0 else C_NEG
            if colors:
                col = colors[i]
            h = abs(v) * 3.0
            if h < 0.01:
                h = 0.01
            bar = Rectangle(
                width=width,
                height=h,
                fill_color=col,
                fill_opacity=0.9,
                stroke_color=col,
                stroke_width=2,
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

    def _grover_bars(
        self, values, mark_idx=None, y_scale=2.5, bar_w=0.55, gap=0.2, baseline_y=None
    ):
        """Build a Grover bar chart anchored at the content center.
        Returns VGroup(axis, labels, bars)."""
        n = len(values)
        total_w = n * bar_w + (n - 1) * gap
        x0 = -total_w / 2
        if baseline_y is None:
            baseline_y = CONTENT_CENTER_Y - 0.3
        axis = Line(
            [x0 - 0.25, baseline_y, 0],
            [x0 + total_w + 0.25, baseline_y, 0],
            color=C_MUTED,
            stroke_width=1.5,
        )
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
                width=bar_w,
                height=h,
                fill_color=color,
                fill_opacity=0.85,
                stroke_color=color,
                stroke_width=2,
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

    # ----- Quantum part of Shor -----

    def _register_strip(
        self, values, center_y, label_text, color_fn, cell_w=0.55, cell_h=0.55, gap=0.08
    ):
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
                width=cell_w,
                height=cell_h,
                fill_color=color,
                fill_opacity=0.15,
                stroke_color=color,
                stroke_width=1.5,
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

    def title(self):
        title = th("Shor's Algorithm", size=72, color=C_ACCENT, weight=BOLD)
        sub = th("แยกตัวประกอบด้วย quantum computer", size=32, color=C_MUTED)
        sub.next_to(title, DOWN, buff=0.4)
        self.play(FadeIn(title, shift=UP * 0.3), FadeIn(sub))
        self.next_slide()
        self.play(FadeOut(title), FadeOut(sub))

    def QuantumIntro(self):
        # 1. Setup Elements
        title = th("QUANTUM คืออะไร?", color=C_ACCENT).to_edge(UP, buff=HEADER_BUFF)

        # Bullet points (These are all VMobjects, so VGroup is fine here)
        bullets = (
            VGroup(
                Text("• ฟิสิกส์ของอนุภาคขนาดเล็ก", font_size=24),
                Text("• มีลักษณะเด่นคือไม่ Deterministic", font_size=24),
                Text("• สถานะคลุมเครือเรียกว่า “Superposition”", font_size=24),
                Text("• เมื่อวัดจะสูญเสีย Superposition ไป", font_size=24),
            )
            .arrange(DOWN, aligned_edge=LEFT, buff=0.4)
            .move_to(LEFT * 3)
        )

        # Image from path "gg"
        cat_img = (
            ImageMobject("image.png")
            .scale(0.7)
            .to_edge(RIGHT, buff=0.3)
            .shift(UP * 0.7)
        )

        # Quote block
        quote = Paragraph(
            "The cat isn’t dead, isn’t alive,",
            "isn’t both dead and alive,",
            "it is in superposition.",
            alignment="center",
            line_spacing=0.8,
            font_size=20,
            color=C_MUTED,
            slant=ITALIC,
        ).next_to(cat_img, DOWN, buff=0.1)

        author = th("- Mahesh Shenoy", size=16, color=C_ACCENT).next_to(
            quote, DOWN, aligned_edge=RIGHT
        )

        # 2. Animation Sequence
        self.play(FadeIn(title))
        self.play(FadeIn(bullets, shift=RIGHT * 0.3), run_time=1)
        self.next_slide()

        # Highlight Superposition and bring in the cat
        self.play(
            bullets[2].animate.set_color(C_POS).scale(1.1),
            FadeIn(cat_img, shift=LEFT * 0.5),
        )
        self.play(Write(quote), FadeIn(author, shift=UP * 0.1))
        self.next_slide()

        # FIX: Use Group instead of VGroup for mixed Mobject types
        all_elements = Group(title, bullets, cat_img, quote, author)
        self.play(FadeOut(all_elements))

    def QubitBasic(self):
        header = th("Quantum State", color=C_ACCENT)
        header.to_edge(UP, buff=0.2)
        analogy = th("นึกภาพเหรียญที่กำลังหมุน ไม่ใช่ทั้งหัว ไม่ใช่ทั้งก้อย", size=24, color=C_MUTED)
        analogy.next_to(header, DOWN, buff=0.2)
        self.play(FadeIn(header), FadeIn(analogy), run_time=0.1)

        # Left: arrow-on-circle diagram
        axes_center = content_center(x=-3.2, dy=-0.6)
        radius = 1.3
        x_axis = Arrow(
            axes_center + LEFT * 0.3,
            axes_center + RIGHT * (radius + 0.6),
            color=C_MUTED,
            buff=0,
            stroke_width=3,
        )
        y_axis = Arrow(
            axes_center + DOWN * 0.3,
            axes_center + UP * (radius + 0.6),
            color=C_MUTED,
            buff=0,
            stroke_width=3,
        )
        lbl0 = MathTex(r"|0\rangle", color=C_MUTED).scale(0.8)
        lbl0.next_to(x_axis.get_end(), RIGHT, buff=0.15)
        lbl1 = MathTex(r"|1\rangle", color=C_MUTED).scale(0.8)
        lbl1.next_to(y_axis.get_end(), UP, buff=0.15)
        circle = Circle(radius=radius, color=C_MUTED, stroke_width=1.5)
        circle.move_to(axes_center)
        self.play(
            Create(x_axis), Create(y_axis), FadeIn(lbl0), FadeIn(lbl1), Create(circle)
        )

        theta = 55 * DEGREES
        tip = axes_center + radius * np.array([np.cos(theta), np.sin(theta), 0])
        state_arrow = Arrow(axes_center, tip, color=C_ACCENT, buff=0, stroke_width=5)
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
            Create(proj_x),
            Create(proj_y),
            Create(alpha_seg),
            Create(beta_seg),
            Write(a_lbl),
            Write(b_lbl),
        )

        # Right panel: equation + explanation
        eq = MathTex(
            r"|\psi\rangle = \alpha|0\rangle + \beta|1\rangle", color=WHITE
        ).scale(1.0)
        explain = VGroup(
            VGroup(
                MathTex(r"|\alpha|^2", color=C_POS).scale(0.8),
                th("= ความหนักไปทาง", size=20, color=C_POS),
                MathTex(r"|0\rangle", color=C_POS).scale(0.75),
            ).arrange(RIGHT, buff=0.15),
            VGroup(
                MathTex(r"|\beta|^2", color=C_NEG).scale(0.8),
                th("= ความหนักไปทาง", size=20, color=C_NEG),
                MathTex(r"|1\rangle", color=C_NEG).scale(0.75),
            ).arrange(RIGHT, buff=0.15),
            MathTex(r"|\alpha|^2 + |\beta|^2 = 1", color=C_ACCENT).scale(0.85),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        right_panel = VGroup(eq, explain).arrange(DOWN, buff=0.3)
        right_panel.move_to(content_center(x=2.8, dy=1.4))
        self.play(Write(eq))
        self.play(FadeIn(explain), run_time=0.1)
        self.next_slide()

        # ---- Measurement phase ----
        ask = th("พอวัด → ลูกศรล้มลงแกนใดแกนหนึ่ง", size=22, color=C_ACCENT, weight=BOLD)
        ask.next_to(right_panel, DOWN, buff=0.4)
        ask.align_to(right_panel, LEFT)
        self.play(Write(ask), run_time=0.1)

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
        for i, (target, name, col) in enumerate(outcomes):
            self.play(
                state_arrow.animate.put_start_and_end_on(axes_center, tip),
                run_time=0.25,
            )
            self.play(
                state_arrow.animate.put_start_and_end_on(axes_center, target),
                run_time=0.35,
            )
            self.next_slide()
        all_qubit_elements = Group(
            header,
            analogy,
            x_axis,
            y_axis,
            lbl0,
            lbl1,
            circle,  # Axes & Circle
            state_arrow,
            state_lbl,  # The Vector
            proj_x,
            proj_y,
            alpha_seg,
            beta_seg,
            a_lbl,
            b_lbl,  # Projections
            right_panel,
            ask,
            probs,  # Equations & Text
        )
        self.next_slide()
        self.play(FadeOut(all_qubit_elements))

    def Why2n(self):
        # 1. SETUP HEADER
        setup = th("n classical bits กับ n qubits ต่างกันยังไง?", size=26, color=C_ACCENT)
        setup.to_edge(UP, buff=0.2)  # ขยับขึ้นเล็กน้อยเพื่อให้มีพื้นที่ด้านล่าง
        self.play(FadeIn(setup))

        configs = ["00", "01", "10", "11"]

        # ------ 2. CLASSICAL PANEL ------
        c_title = th("2 classical bits", size=22, color=C_MUTED)
        c_rows = VGroup(*[MathTex(cfg, color=WHITE).scale(0.75) for cfg in configs])
        c_rows.arrange(DOWN, buff=0.15)

        c_panel = VGroup(c_title, c_rows).arrange(DOWN, buff=0.25)
        c_panel.move_to(content_center(x=-3.5, dy=1.1))

        highlight = SurroundingRectangle(
            c_rows[2], color=C_ACCENT, buff=0.08, stroke_width=3
        )
        c_note = th("อยู่ที่เดียวในเวลาเดียว", size=18, color=C_MUTED)
        c_note.next_to(c_panel, DOWN, buff=0.25)

        self.play(FadeIn(c_panel))
        self.play(Create(highlight), FadeIn(c_note))
        self.next_slide()  # --- หยุดเพื่อให้เห็นว่า Classical เลือกได้แค่ 1 จาก 4 ---

        # ------ 3. QUANTUM PANEL ------
        q_title = th("2 qubits", size=22, color=C_ACCENT)
        q_rows = VGroup()
        amp_labels = [r"\alpha_{00}", r"\alpha_{01}", r"\alpha_{10}", r"\alpha_{11}"]
        for cfg, amp in zip(configs, amp_labels):
            lhs = MathTex(cfg, color=WHITE).scale(0.75)
            arrow = MathTex(r"\to", color=C_MUTED).scale(0.7)
            rhs = MathTex(amp, color=C_ACCENT).scale(0.75)
            row = VGroup(lhs, arrow, rhs).arrange(RIGHT, buff=0.15)
            q_rows.add(row)
        q_rows.arrange(DOWN, buff=0.15, aligned_edge=LEFT)

        q_panel = VGroup(q_title, q_rows).arrange(DOWN, buff=0.25)
        q_panel.move_to(content_center(x=3.2, dy=1.1))

        q_note = VGroup(
            th(
                "แต่ละ state เก็บข้อมูลด้วยจำนวนเชิงซ้อนทำให้เกิดการแทรกสอดได้",
                size=18,
                color=C_MUTED,
            ),
            # MathTex(r"|\alpha_{cfg}|^2 = P(\text{collapse}\to cfg)", color=C_POS).scale(
            #     0.65
            # ),
            th("เป็นไปได้หลายอย่างในเวลาเดียวกัน", size=18, color=C_MUTED),
        ).arrange(DOWN, buff=0.15)
        q_note.next_to(q_panel, DOWN, buff=0.25)

        self.play(FadeIn(q_panel))
        self.play(Write(q_note))
        self.next_slide()  # --- หยุดเพื่อเปรียบเทียบ Classical vs Quantum ---

        # ------ 4. PUNCHLINE (The Why) ------
        punch = VGroup(
            th("50 qubits → 2⁵⁰ ≈ 10¹⁵ amplitudes", size=24, color=C_POS, weight=BOLD),
            th("classical จำลองไม่ไหว (ใช้ RAM มหาศาล)", size=22, color=C_MUTED),
        ).arrange(DOWN, buff=0.15)
        punch.to_edge(DOWN, buff=0.6)

        self.play(Write(punch))
        self.play(Indicate(punch[0], color=C_POS))  # เน้นย้ำตัวเลขมหาศาล
        self.next_slide()

        # ------ 5. CLEAR SCENE ------
        # รวบรวมทุกอย่างเป็น Group เพื่อล้างหน้าจอให้สะอาด
        all_elements = Group(setup, c_panel, highlight, c_note, q_panel, q_note, punch)
        self.play(FadeOut(all_elements))

    def QuantumSpeedup(self):
        header = th("จุดที่ Quantum ได้เปรียบ", color=C_ACCENT)
        header.to_edge(UP, HEADER_BUFF)
        self.play(Write(header))
        # 1. SETUP ELEMENTS (เหมือนเดิมแต่รวบรวมไว้เพื่อจัดการง่าย)
        c_label = th("Classical: ต้องทำทีละค่า (Iterative)", size=20, color=C_MUTED)
        c_label.move_to(content_center(x=-3.5, dy=2.5))
        c_box = RoundedRectangle(height=3, width=2.5, color=C_MUTED)
        c_box.next_to(c_label, DOWN, buff=0.2)
        c_tasks = VGroup(
            *[MathTex(f"f({i})", color=WHITE).scale(0.6) for i in range(6)]
        )
        c_tasks[4] = MathTex("...", color=WHITE).scale(0.6)
        c_tasks[5] = MathTex("f(15)", color=WHITE).scale(0.6)
        c_tasks.arrange_in_grid(rows=3, cols=2, buff=0.2).move_to(c_box.get_center())

        q_label = th("Quantum: ทำงานบนทุก Qubit พร้อมกัน", size=20, color=C_ACCENT)
        q_label.move_to(content_center(x=3.5, dy=2.5))
        psi_state = MathTex(
            r"|\psi\rangle = \sum_{i=0}^{15} \alpha_i |i\rangle", color=WHITE
        ).scale(0.8)
        psi_state.next_to(q_label, DOWN, buff=0.4)
        gate_u = Square(side_length=1.1, color=C_ACCENT)
        gate_u.add(MathTex("U", color=C_ACCENT))
        gate_u.next_to(psi_state, DOWN, buff=0.6)
        arrow_in = Arrow(
            psi_state.get_bottom(), gate_u.get_top(), color=C_MUTED, buff=0.1
        )
        res_text = th("1 Operation on 4 Qubits", size=18, color=C_POS)
        res_text.next_to(gate_u, DOWN, buff=0.3)
        impact = th("กระทบทั้ง 16 states ทันที!", size=22, color=C_POS, weight=BOLD)
        impact.next_to(res_text, DOWN, buff=0.2)

        # 2. ANIMATION STAGE 1: Setup
        self.play(
            Create(c_box),
            FadeIn(c_label),
            FadeIn(q_label),
            Write(psi_state),
        )
        self.next_slide()  # หยุดเพื่อให้คนดูเห็นความต่างของ Initial State ก่อนเริ่มรัน

        # 3. ANIMATION STAGE 2: Processing Loop
        for i in range(6):
            target = c_tasks[i]
            anis = []
            highlight = Square(side_length=0.4, color=C_POS).move_to(target)
            anis.append(
                Succession(
                    Create(highlight, run_time=0.1),
                    AnimationGroup(
                        FadeOut(highlight),
                        target.animate.set_color(C_POS),
                        run_time=0.1,
                    ),
                )
            )

            # Quantum milestones during loop
            if i == 0:
                anis.append(GrowArrow(arrow_in))
            if i == 1:
                anis.append(Create(gate_u))
            if i == 2:
                anis.append(gate_u.animate.set_fill(C_ACCENT, opacity=0.3))
                anis.append(Write(res_text))
            if i == 3:
                anis.append(Indicate(psi_state, color=C_POS))
                anis.append(FadeIn(impact))

            self.play(*anis, run_time=0.4)

        self.next_slide()  # หยุดดูผลลัพธ์ที่ฝั่งหนึ่งเสร็จหมดแล้ว แต่อีกฝั่งเพิ่งเริ่ม

        # 4. ANIMATION STAGE 3: Punchline
        summary = (
            VGroup(
                th("Classical: O(2ⁿ) steps", size=24, color=C_MUTED),
                MathTex(r"\longleftrightarrow", color=WHITE),
                th("Quantum: O(n) step (Quantum Parallelism)", size=24, color=C_POS),
            )
            .arrange(RIGHT, buff=0.5)
            .to_edge(DOWN, buff=0.6)
        )

        divider = Line(LEFT * 6, RIGHT * 6, color=C_MUTED, stroke_width=1).next_to(
            summary, UP, buff=0.4
        )

        self.play(Create(divider), Write(summary))
        self.next_slide()  # จบ Slide นี้อย่างสมบูรณ์

        # 5. CLEAR SCENE
        # รวบรวมทุกอย่างที่สร้างขึ้นมาเพื่อล้างหน้าจอ
        clear = Group(
            c_label,
            c_box,
            c_tasks,  # Classical Section
            q_label,
            psi_state,
            gate_u,
            arrow_in,  # Quantum Section
            res_text,
            impact,  # Results & Impact
            divider,
            summary,  # Summary elements
        )
        self.play(FadeOut(clear), FadeOut(header))

    def GroverProblem(self):
        # 1. Header & Context
        header = th("โจทย์ของ Grover's Algorithm", color=C_ACCENT)
        header.to_edge(UP, buff=HEADER_BUFF)

        setup = (
            VGroup(
                th(
                    "สมมติว่าเรามีข้อมูลที่ 'ไม่เรียงลำดับ' (Unstructured)",
                    size=24,
                    color=C_MUTED,
                ),
                MathTex("N = 8", color=WHITE).scale(0.9),
                th("รายการ", size=24, color=C_MUTED),
            )
            .arrange(RIGHT, buff=0.2)
            .next_to(header, DOWN, buff=0.4)
        )

        self.play(Write(header), FadeIn(setup))

        # 2. Visualizing the Unopened Boxes
        boxes = VGroup()
        for i in range(8):
            sq = Square(side_length=0.8, color=C_MUTED, stroke_width=2)
            lab = MathTex("?", color=C_MUTED).scale(0.7).move_to(sq)
            boxes.add(VGroup(sq, lab))
        boxes.arrange(RIGHT, buff=0.2).move_to(UP * 0.7)

        self.play(LaggedStart(*[FadeIn(b) for b in boxes], lag_ratio=0.1))
        self.next_slide()

        # 3. The Oracle Concept
        oracle_rect = SurroundingRectangle(boxes, color=C_MUTED, buff=0.4)
        oracle_label = th("Oracle: ทำหน้าที่เป็นผู้ตรวจสอบ", size=22, color=WHITE).next_to(
            oracle_rect, UP, buff=0.1
        )

        oracle_logic = (
            VGroup(
                th("ถ้าหยิบข้อมูล ", size=22),
                MathTex("x", color=C_ACCENT),
                th(" ไปถาม... Oracle จะตอบแค่ ใช่ หรือ ไม่ใช่", size=22),
            )
            .arrange(RIGHT, buff=0.2)
            .next_to(oracle_rect, DOWN, buff=0.2)
        )

        self.play(Create(oracle_rect), FadeIn(oracle_label))
        self.play(Write(oracle_logic))
        self.next_slide()

        # 4. Comparison Table (แทนที่ Mystery Box เดิม)
        t_header = ["Strategy", "Method", "Query Time"]
        t_classical = ["Classical", "สุ่มเปิดทีละกล่อง", "O(N)"]
        t_quantum = ["Quantum", "บีบแอมพลิจูด", "O(√N)"]

        # สร้างตารางอย่างง่ายด้วย VGroup และตำแหน่งคงที่
        col_x = [-4, 0, 4]
        row_y = [-1.5, -2.1, -2.7]

        # Table UI
        table_content = VGroup()

        # Row 0: Header
        for idx, text in enumerate(t_header):
            table_content.add(
                th(text, size=20, color=C_MUTED).move_to([col_x[idx], row_y[0], 0])
            )

        # Row 1: Classical
        for idx, text in enumerate(t_classical):
            color = C_NEG if idx == 0 else WHITE
            table_content.add(
                th(text, size=20, color=color).move_to([col_x[idx], row_y[1], 0])
            )

        # Row 2: Quantum
        for idx, text in enumerate(t_quantum):
            color = C_POS if idx == 0 or idx == 2 else WHITE
            table_content.add(
                th(text, size=20, color=color).move_to([col_x[idx], row_y[2], 0])
            )

        h_line = Line(
            [-5.5, row_y[0] - 0.25, 0],
            [5.5, row_y[0] - 0.25, 0],
            color=C_MUTED,
            stroke_width=1,
        )

        table_group = VGroup(table_content, h_line)
        table_group.to_edge(DOWN, buff=0.6)

        self.play(FadeIn(table_group, shift=UP * 0.2))

        # Caveat
        caveat = th(
            "* Oracle ต้องถูกเขียนเป็น Quantum Circuit (Oracle Synthesis)",
            size=16,
            color=C_NEG,
        )
        caveat.to_edge(DR, buff=0.2)
        self.play(FadeIn(caveat))

        self.next_slide()

        # 5. Cleanup
        all_elements = Group(
            header,
            setup,
            boxes,
            oracle_rect,
            oracle_label,
            oracle_logic,
            table_group,
            caveat,
        )
        self.play(FadeOut(all_elements))

    def GroverIteration(self):
        # 1. SETUP HEADER
        header = th("Grover's Algorithm Step-by-Step", color=C_ACCENT)
        header.to_edge(UP, buff=HEADER_BUFF)
        self.play(Write(header))

        # --- 2. INITIAL STATE (Uniform Superposition) ---
        vals_init = [AMP_INIT] * 8
        chart, _, _ = self._grover_bars(vals_init, mark_idx=CHART_MARK)

        cap = (
            VGroup(
                th(T_INIT, size=24, color=C_MUTED),
                MathTex(r"=\tfrac{1}{\sqrt{8}}", color=C_MUTED).scale(0.85),
            )
            .arrange(RIGHT, buff=0.2)
            .next_to(header, DOWN, buff=0.1)
        )

        bot = th(T_PROB_1_8, size=22, color=C_MUTED).move_to(content_center(dy=-2.2))

        self.play(Write(cap), Write(chart), Write(bot))
        self.next_slide()  # --- Click to Oracle ---

        # --- 3. STEP 1: ORACLE (Phase Inversion) ---
        vals_step1 = [AMP_INIT] * 8
        vals_step1[CHART_MARK] = -AMP_INIT

        chart_step1, _, _ = self._grover_bars(vals_step1, mark_idx=CHART_MARK)
        cap_step1 = th(T_STEP1, size=24, color=C_ACCENT).next_to(header, DOWN, buff=0.1)
        bot_step1 = th(T_ORACLE_X, size=22, color=C_MUTED).move_to(bot)

        self.play(
            Transform(chart, chart_step1),
            Transform(cap, cap_step1),
            Transform(bot, bot_step1),
            run_time=1.5,
        )
        self.next_slide()  # --- Click to Diffusion ---

        # --- 4. STEP 2: DIFFUSION (Inversion about the Mean) ---
        mean = sum(vals_step1) / 8
        vals_final = [2 * mean - v for v in vals_step1]

        chart_final, _, _ = self._grover_bars(vals_final, mark_idx=CHART_MARK)
        cap_final = th(T_STEP2, size=24, color=C_ACCENT).next_to(header, DOWN, buff=0.1)
        bot_final = th(T_FINAL, size=22, color=C_POS).move_to(bot)

        self.play(
            Transform(chart, chart_final),
            Transform(cap, cap_final),
            Transform(bot, bot_final),
            run_time=1.5,
        )
        self.next_slide()  # --- จบรอบการ Iteration ---

        # 5. CLEAR SCENE
        # ล้างหน้าจอทั้งหมดเพื่อไปสู่หัวข้อถัดไป
        self.play(FadeOut(Group(header, chart, cap, bot)))

    def GroverIterate(self):
        header = th("ภาพรวมการทำงานของ Grover's Algorithm", color=C_ACCENT)
        header.to_edge(UP, buff=0.2)
        self.play(Write(header))

        a = 1 / np.sqrt(8)

        # Simulate Grover iterations
        def iterate(vals, mark=6):
            out = vals.copy()
            out[mark] = -out[mark]  # phase flip (Oracle)
            mean = sum(out) / len(out)
            return [2 * mean - v for v in out]  # inversion about mean (Diffusion)

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
            axis = Line(
                [x0 - 0.1, center_y, 0],
                [x0 + total_w + 0.1, center_y, 0],
                color=C_MUTED,
                stroke_width=1,
            )
            group.add(axis)
            for i, v in enumerate(vals):
                x = x0 + i * (mini_bar_w + mini_gap) + mini_bar_w / 2
                h = abs(v) * 1.4
                if h < 0.02:
                    h = 0.02  # บังคับให้เห็นเส้นขอบเล็กน้อย
                col = C_ACCENT if i == 6 else (C_POS if v >= 0 else C_NEG)
                bar = Rectangle(
                    width=mini_bar_w,
                    height=h,
                    fill_color=col,
                    fill_opacity=0.85,
                    stroke_color=col,
                    stroke_width=1.5,
                )
                if v >= 0:
                    bar.move_to([x, center_y + h / 2, 0])
                else:
                    bar.move_to([x, center_y - h / 2, 0])
                group.add(bar)
            return group

        # Arrange 4 mini-charts in a row
        xs = [-5.1, -1.7, 1.7, 5.1]
        y_row = 0.2
        mini_charts = []
        mini_titles = VGroup()
        prob_labels = VGroup()

        for (lab, vals), x in zip(labels_frames, xs):
            mc = mini_chart(vals, x, y_row)
            mini_charts.append(mc)
            title = th(lab, size=20, color=C_ACCENT)
            title.move_to([x, y_row + 1.8, 0])
            mini_titles.add(title)

            prob = vals[6] ** 2
            if "วัด" in lab:
                pl = MathTex(r"\checkmark", color=C_POS).scale(1.1)
            else:
                pl = MathTex(rf"P \approx {prob * 100:.0f}\%", color=C_POS).scale(0.7)
            pl.move_to([x, y_row - 1.1, 0])
            prob_labels.add(pl)

        # --- ANIMATION SEQUENCE ---
        for i in range(4):
            mc = mini_charts[i]
            self.play(
                AnimationGroup(
                    Create(mc[0], run_time=0.3),  # Axis
                    Write(mini_titles[i], run_time=0.3),  # Title
                    LaggedStart(
                        *[
                            GrowFromEdge(bar, DOWN if bar.get_y() > y_row else UP)
                            for bar in mc[1:]
                        ],
                        lag_ratio=0.04,
                    ),
                    FadeIn(prob_labels[i], shift=UP * 0.2),
                    lag_ratio=0.2,
                )
            )

        self.next_slide()

        # 4. CONCLUSION PUNCHLINE
        conclusion = (
            VGroup(
                VGroup(
                    th("ทำซ้ำประมาณ", size=24, color=C_MUTED),
                    MathTex(r"\sqrt{N}", color=C_ACCENT).scale(1.1),
                    th("รอบ → โอกาสเจอแทบจะ 100%", size=24, color=C_POS),
                ).arrange(RIGHT, buff=0.2),
                VGroup(
                    th("Classical Search:", size=22, color=C_MUTED),
                    MathTex("O(N)", color=C_MUTED).scale(0.85),
                    th("สุ่มเปิดทีละอัน", size=22, color=C_MUTED),
                ).arrange(RIGHT, buff=0.25),
                VGroup(
                    th("Grover Search:", size=22, color=C_POS, weight=BOLD),
                    MathTex(r"O(\sqrt{N})", color=C_POS).scale(0.9),
                    th("เร็วกว่าแบบ Quadratic Speedup", size=22, color=C_POS),
                ).arrange(RIGHT, buff=0.25),
            )
            .arrange(DOWN, buff=0.3)
            .to_edge(DOWN, buff=0.5)
        )

        self.play(Write(conclusion))
        self.next_slide()

        # 5. CLEAR SCENE
        all_elements = Group(header, *mini_charts, mini_titles, prob_labels, conclusion)
        self.play(FadeOut(all_elements))

    def ShorIntro(self):
        # 1. Header & The Challenge
        header = th("Shor's Algorithm: The RSA Breaker", color=C_ACCENT)
        header.to_edge(UP, buff=HEADER_BUFF)

        challenge = VGroup(
            th(
                "การแยกตัวประกอบ (Integer Factorization) คือกำแพงของโลกไซเบอร์",
                size=24,
                color=C_MUTED,
            ),
            MathTex(r"N = p \times q", color=WHITE).scale(1.5),
            th(
                "ถ้า N มีขนาดใหญ่มาก... คอมพิวเตอร์ปกติอาจใช้เวลาเป็นล้านปี", size=22, color=C_NEG
            ),
        ).arrange(DOWN, buff=0.4)

        self.play(Write(header))
        self.play(FadeIn(challenge[0]), Write(challenge[1]))
        self.play(FadeIn(challenge[2], shift=UP * 0.3))
        self.next_slide()

        # 2. The Shor's Magic
        shor_logic = (
            VGroup(
                th("Shor ไม่ได้สุ่มหาตัวประกอบตรงๆ", size=24, color=C_POS),
                th("แต่เปลี่ยนปัญหาการแยกตัวประกอบ ให้กลายเป็นเรื่องของ", size=24, color=WHITE),
                th(
                    "การหาคาบของฟังก์ชัน (Period Finding)",
                    size=32,
                    color=C_ACCENT,
                    weight=BOLD,
                ),
            )
            .arrange(DOWN, buff=0.3)
            .move_to(challenge)
        )

        # Transition from Challenge to Logic
        self.play(
            FadeOut(challenge, shift=LEFT * 0.5), FadeIn(shor_logic, shift=LEFT * 0.5)
        )
        self.next_slide()

        # 3. Probability Manipulation
        manipulate = (
            VGroup(
                th("โดยใช้หัวใจสำคัญคือการแทรกสอดของคลื่น", size=24, color=C_MUTED),
                th("เพื่อบีบความน่าจะเป็นให้ไปตกอยู่ที่คำตอบเท่านั้น", size=26, color=C_POS),
            )
            .arrange(DOWN, buff=0.3)
            .to_edge(DOWN, buff=1)
        )

        self.play(FadeIn(manipulate, shift=UP))
        self.next_slide()

        # Cleanup
        all_elements = Group(header, shor_logic, manipulate)
        self.play(FadeOut(all_elements))

    def FactoringKey(self):
        # --- Section 1: Setup & Goal ---
        header = th("การแยกตัวประกอบด้วย Shor's algorithm", color=C_ACCENT)
        header.to_edge(UP, buff=0.2)

        setup = (
            VGroup(
                MathTex(r"N = pq"),
                th("เป็นจำนวนเฉพาะคี่", size=30),
            )
            .arrange(RIGHT, buff=0.2)
            .next_to(header, DOWN, buff=0.2)
        )

        goal_text = th(
            "เป้าหมาย: หาค่า y ที่ไม่ใช่ trivial solution (ไม่ใช่ 1 หรือ N)",
            size=28,
            color=C_MUTED,
        )
        equation = MathTex(r"y^2 \equiv 1 \pmod N", color=C_ACCENT).scale(1.2)
        condition = MathTex(r"1 < y < N-1", color=C_MUTED).scale(0.8)

        goal_grp = (
            VGroup(goal_text, equation, condition)
            .arrange(DOWN, buff=0.3)
            .next_to(setup, DOWN, buff=0.5)
        )

        self.play(Write(header))
        self.play(Write(setup))
        self.play(FadeIn(goal_text), Write(equation))
        self.play(FadeIn(condition))
        self.next_slide()

        # --- Section 2: The Math Trick ---
        trick_text = th("ซึ่งหมายความว่า N หารลงตัวใน:", size=28, color=C_MUTED)
        expansion = MathTex(r"(y-1)(y+1) = kN", color=C_ACCENT).scale(1.1)

        trick_grp = (
            VGroup(trick_text, expansion).arrange(DOWN).next_to(setup, DOWN, buff=0.6)
        )

        self.play(FadeOut(goal_grp), FadeIn(trick_grp, shift=UP))
        self.next_slide()

        # --- Section 3: The Conclusion (The "Key") ---
        conc = (
            VGroup(
                th("ดังนั้นตัวประกอบของ N คือ:", size=30, color=C_POS),
                MathTex(
                    r"\gcd(y-1, N) \quad \text{\&} \quad \gcd(y+1, N)", color=C_POS
                ).scale(1.2),
            )
            .arrange(DOWN, buff=0.4)
            .next_to(trick_grp, DOWN, buff=0.8)
        )

        explanation = th(
            "เนื่องจาก p, q แยกกันอยู่ใน (y-1) และ (y+1)", size=22, color=C_MUTED
        )
        explanation.next_to(conc, DOWN, buff=0.4)

        self.play(Write(conc))
        self.play(FadeIn(explanation))

        euclid = th("gcd หาได้เร็วมากด้วย Euclidean Algorithm", size=22, color=C_ACCENT)
        euclid.to_edge(DOWN, buff=0.8)
        self.play(Write(euclid))
        self.next_slide()

        # --- Section 4: Fade Out ---
        # ล้างหน้าจอทั้งหมดเพื่อเริ่มหัวข้อถัดไป
        self.play(FadeOut(Group(header, setup, trick_grp, conc, explanation, euclid)))

    def FactoringTrickExample(self):
        # --- 1. Header & Setup ---
        header = th("การแยกตัวประกอบด้วย Shor's algorithm", color=C_ACCENT)
        header.to_edge(UP, buff=0.2)

        # Act 2: verify with N = 15
        subtitle = (
            VGroup(
                th("ตัวอย่างลองหาใน", size=22, color=C_MUTED),
                MathTex("N = 15", color=C_ACCENT).scale(0.9),
                th("จะมี y ∈ {1, 4, 11, 14} ที่", size=22, color=C_MUTED),
                MathTex(r"y^2 \equiv 1 \pmod{15}", color=C_MUTED).scale(0.85),
            )
            .arrange(RIGHT, buff=0.2)
            .next_to(header, DOWN, buff=0.2)
        )

        self.play(Write(header))
        self.play(FadeIn(subtitle))

        # --- 2. Table Construction ---
        header_row = ["y", r"\gcd(y-1,\,15)", r"\gcd(y+1,\,15)", "ผลลัพธ์"]
        header_kinds = ["math", "math", "math", "text"]
        rows_data = [
            [("math", "1"), ("math", "15"), ("math", "1"), ("text", "—")],
            [("math", "4"), ("math", "3"), ("math", "5"), ("text", "✓")],
            [("math", "11"), ("math", "5"), ("math", "3"), ("text", "✓")],
            [("math", "14"), ("math", "1"), ("math", "15"), ("text", "—")],
        ]
        useful_rows = [False, True, True, False]
        col_x = [-4.8, -1.7, 1.7, 4.6]
        row_h = 0.65

        def make_mobj(kind, content, color):
            if kind == "math":
                return MathTex(content, color=color).scale(0.85)
            return th(content, size=24, color=color)

        # Header row
        header_mobjs = VGroup()
        for j, (kind, h) in enumerate(zip(header_kinds, header_row)):
            m = make_mobj(kind, h, C_ACCENT)
            m.move_to([col_x[j], 0, 0])
            header_mobjs.add(m)

        underline = Line(
            [col_x[0] - 0.5, -row_h * 0.55, 0],
            [col_x[-1] + 0.5, -row_h * 0.55, 0],
            color=C_MUTED,
            stroke_width=1.5,
        )

        # Data rows
        row_mobjs = VGroup()
        for i, (row, useful) in enumerate(zip(rows_data, useful_rows)):
            y_pos = -(i + 1) * row_h - 0.1
            color = C_POS if useful else C_MUTED
            for j, (kind, content) in enumerate(row):
                m = make_mobj(kind, content, color)
                m.move_to([col_x[j], y_pos, 0])
                row_mobjs.add(m)

        full_table = VGroup(header_mobjs, underline, row_mobjs)
        full_table.next_to(subtitle, DOWN, buff=0.4)

        self.play(FadeIn(header_mobjs), Create(underline))
        for i in range(4):
            slice_ = row_mobjs[i * 4 : (i + 1) * 4]
            self.play(FadeIn(slice_, shift=UP * 0.1), run_time=0.3)
        self.next_slide()

        # --- 3. Highlighting Success ---
        # Fade failed rows (Trivial solutions 1 and 14)
        fade_targets = VGroup(
            row_mobjs[0:4],  # Row 0
            row_mobjs[12:16],  # Row 3
        )

        def strike(row_idx):
            cells = row_mobjs[row_idx * 4 : (row_idx + 1) * 4]
            start = cells[0].get_left() + LEFT * 0.25
            end = cells[-1].get_right() + RIGHT * 0.25
            return Line(start, end, color=C_MUTED, stroke_width=1.5)

        strikes = VGroup(strike(0), strike(3))
        self.play(
            fade_targets.animate.set_opacity(0.3),
            Create(strikes),
        )

        # Payoff line: Show how we got 3 and 5
        r1_gcd_left = row_mobjs[1 * 4 + 1]  # "3"
        r1_gcd_right = row_mobjs[1 * 4 + 2]  # "5"

        factor_line = MathTex(
            r"15",
            r"=",
            r"3",
            r"\times",
            r"5",
        ).scale(1.4)
        factor_line[0].set_color(WHITE)
        factor_line[2].set_color(C_POS)
        factor_line[4].set_color(C_POS)
        factor_line.next_to(full_table, DOWN, buff=0.6)

        self.play(
            FadeIn(factor_line[0]),
            FadeIn(factor_line[1]),
            TransformFromCopy(r1_gcd_left, factor_line[2]),
            FadeIn(factor_line[3]),
            TransformFromCopy(r1_gcd_right, factor_line[4]),
        )
        self.next_slide()

        # --- 4. Conclusion & Cleanup ---
        self.play(FadeOut(Group(header, subtitle, full_table, strikes, factor_line)))

    def ShorFindOrder(self):
        # --- 1. Header & Intuition ---
        header = th("การหาคาบ: หัวใจของ Shor's Algorithm", color=C_ACCENT)
        header.to_edge(UP, buff=0.2)

        intuition_text = (
            VGroup(
                th(
                    "สมมติว่ามีค่า x แล้วเรายกกำลังไปเรื่อยๆ เศษจะวนกลับมาเป็น 1",
                    size=22,
                    color=C_MUTED,
                ),
                MathTex(r"x^1, x^2, x^3, \dots \pmod N", color=C_MUTED).scale(0.7),
                th("เราเรียกความยาวรอบการวนนี้ว่า Order (r)", size=24, color=C_ACCENT),
            )
            .arrange(DOWN, buff=0.15)
            .next_to(header, DOWN, buff=0.2)
        )

        self.play(Write(header))
        self.play(FadeIn(intuition_text, shift=UP * 0.2))
        self.next_slide()

        # --- 2. Steps Section (Left Aligned) ---
        # Step 1: สุ่ม x
        s1 = VGroup(
            th("1) กำหนดให้", size=22),
            MathTex(r"x", color=WHITE).scale(0.9),
            th("เป็นเลขที่", size=22),
            MathTex(r"\gcd(x, N) = 1", color=WHITE).scale(0.9),
        ).arrange(RIGHT, buff=0.15)

        # Step 2: นิยาม Order
        s2_label = th("2) หา order r ที่เป็นเลขน้อยที่สุดที่ทำให้:", size=22)
        s2_eq = MathTex(r"x^r \equiv 1 \pmod N", color=C_ACCENT).scale(0.9)
        s2 = VGroup(s2_label, s2_eq).arrange(DOWN, buff=0.1)

        # Step 3: เงื่อนไขเลขคู่
        s3_label = th("3) ถ้า r เป็นเลขคู่ เราจะแตกตัวประกอบได้สำเร็จ", size=22, color=C_POS)
        s3_math = MathTex(r"y = x^{r/2}", color=WHITE).scale(0.9)
        s3_eq = MathTex(r"y^2 \equiv 1 \pmod N", color=C_POS).scale(0.9)

        s3_line2 = VGroup(
            th("โดยใช้ค่า", size=20), s3_math, th("ซึ่งจะได้:", size=20, color=C_MUTED)
        ).arrange(RIGHT, buff=0.15)
        s3 = VGroup(s3_label, s3_line2, s3_eq).arrange(DOWN, buff=0.1)

        # จัดกลุ่มและแสดงผล
        steps = VGroup(s1, s2, s3).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        steps.next_to(intuition_text, DOWN, buff=0.3)

        for s in steps:
            self.play(FadeIn(s, shift=RIGHT * 0.2))

        self.next_slide()

        # --- 3. The Bottleneck & Quantum Hook ---
        bottleneck = (
            VGroup(
                th(
                    "คอมพิวเตอร์ทั่วไปหา r ได้ช้ามาก (ใช้เวลาเป็น Exponential)",
                    size=20,
                    color=C_NEG,
                ),
                th("นี่คือจุดที่จะใช้ Quantum Computer", size=22, color=C_ACCENT, weight=BOLD),
            )
            .arrange(DOWN, buff=0.15)
            .to_edge(DOWN, buff=0.6)
        )

        self.play(Write(bottleneck))
        self.next_slide()

        # --- 4. Cleanup ---
        self.play(FadeOut(Group(header, intuition_text, steps, bottleneck)))

    def ShorSteps(self):
        # --- 0. PREPARE TITLES & LABELS ---
        curr_title = title_bar("Shor's Algorithm: ขั้นตอนเชิงควอนตัม")

        step1_title = th(
            "Step 1: Quantum Parallelism & Modular Exponentiation",
            size=24,
            color=C_ACCENT,
        ).next_to(curr_title, DOWN, buff=0.2)
        step2_title = th(
            "Step 2: Measurement & Wavefunction Collapse", size=24, color=C_ACCENT
        ).next_to(curr_title, DOWN, buff=0.2)
        step3_title = th(
            "Step 3: Quantum Fourier Transform (Period Finding)",
            size=24,
            color=C_ACCENT,
        ).next_to(curr_title, DOWN, buff=0.2)

        # --- 1. INITIAL SETUP & SLIDE 1: PARALLEL ---
        k_strip, _, k_texts = self._register_strip(
            list(range(K_VALS)), center_y=1, label_text="k", color_fn=lambda i: WHITE
        )
        f_strip, f_cells, f_texts = self._register_strip(
            [0] * K_VALS, center_y=-0.3, label_text="f(k)", color_fn=lambda i: C_MUTED
        )

        note = th(S_K_SUP, size=20, color=C_POS).next_to(k_strip, UP, buff=0.2)

        # เริ่มต้นฉาก: แสดงสถานะ Superposition เริ่มต้น
        self.play(Write(curr_title))
        self.next_slide()
        self.play(FadeIn(k_strip), FadeIn(f_strip), FadeIn(note))

        # เข้าสู่ Step 1: คำนวณ f(k) ทั้งหมดพร้อมกัน
        self.play(Write(step1_title))
        new_note_parallel = th(S_GATE, size=20, color=C_POS).move_to(note)

        self.next_slide()
        parallel_anims = [Transform(note, new_note_parallel)]
        for i in range(K_VALS):
            val = (
                MathTex(str(F_PATTERN[i]), color=PALETTE[F_PATTERN[i]])
                .scale(0.55)
                .move_to(f_texts[i])
            )
            parallel_anims.append(Transform(f_texts[i], val))
            parallel_anims.append(
                f_cells[i].animate.set_fill(PALETTE[F_PATTERN[i]], opacity=0.3)
            )

        self.play(*parallel_anims, run_time=1.2)
        self.next_slide()

        # --- SLIDE 2: COLLAPSE ---
        self.play(Transform(step1_title, step2_title))
        new_note_collapse = th(S_COLLAPSE, size=20, color=C_POS).move_to(note)

        keep_k = [3, 7, 11]  # ค่า k ที่ให้ผล f(k) ตรงกับค่าที่ถูกวัด (ตัวอย่าง)
        collapse_anims = [Transform(note, new_note_collapse)]

        for i in range(K_VALS):
            if i not in keep_k:
                collapse_anims.extend(
                    [
                        k_texts[i].animate.set_opacity(0.1),
                        f_cells[i].animate.set_opacity(0.1),
                        f_texts[i].animate.set_opacity(0.1),
                    ]
                )
            else:
                collapse_anims.append(k_texts[i].animate.set_color(C_POS).scale(1.2))

        self.play(*collapse_anims)

        # วาดลูกศรแสดงคาบ (r)
        r_arrows = VGroup()
        for i in range(len(keep_k) - 1):
            arr = DoubleArrow(
                k_texts[keep_k[i]].get_top(),
                k_texts[keep_k[i + 1]].get_top(),
                buff=0.1,
                color=C_ACCENT,
            ).shift(UP * -0.3)
            lbl = MathTex("r", color=C_ACCENT).scale(0.6).next_to(arr, UP, buff=0.05)
            r_arrows.add(arr, lbl)

        self.play(Create(r_arrows))
        self.next_slide()

        # --- SLIDE 3: QFT & PROBABILITY ---
        self.play(Transform(step1_title, step3_title))

        # ฟังก์ชันความน่าจะเป็นหลังทำ QFT
        r_val, Q, M_val = 4, 16, 3

        def prob_func(k):
            denom_val = np.sin(np.pi * k * r_val / Q)
            if abs(denom_val) < 1e-6:
                return 1.0
            num_val = np.sin(np.pi * k * r_val * (M_val + 1) / Q)
            return (num_val / ((M_val + 1) * denom_val)) ** 2

        # เตรียม UI สำหรับผลลัพธ์ QFT
        final_note = th(S_QFT, size=20, color=C_POS).next_to(
            step1_title, DOWN, buff=0.1
        )
        prob_formula = (
            MathTex(
                r"P_{|k\rangle\otimes |f(x_0)\rangle} = \frac{C^2}{2^{4n}} \frac{\sin^2 \frac{\pi kr(M+1)}{2^{2n}}}{\sin^2\frac{\pi kr}{2^{2n}}}",
                color=WHITE,
            )
            .scale(0.6)
            .next_to(final_note, DOWN, buff=0.8)
        )

        formula_label = th(
            "Probability Distribution (QFT Result):", size=18, color=C_ACCENT
        ).next_to(prob_formula, UP, buff=0.2)

        ax = Axes(
            x_range=[0, 16.5, 4],
            y_range=[0, 1.2, 0.5],
            x_length=10,
            y_length=2.5,
            axis_config={"include_numbers": True, "font_size": 18, "color": C_MUTED},
        ).shift(DOWN * 1.5)

        qft_plot = ax.plot(
            prob_func, color=C_POS, x_range=[0, 16], use_smoothing=True, stroke_width=3
        )

        # Transition สุดท้าย: เคลียร์แถบข้อมูลเดิมและแทนที่ด้วยสูตรและกราฟ
        self.play(
            Transform(note, final_note),
            FadeOut(f_strip),
            FadeOut(r_arrows),
            FadeOut(VGroup(*[k_texts[i] for i in range(K_VALS)])),
            FadeTransform(k_strip, prob_formula),
            run_time=1.2,
        )

        self.play(FadeIn(formula_label, shift=UP * 0.2), Create(ax))
        self.play(Create(qft_plot), run_time=1.5, rate_func=smooth)
        self.next_slide()

        # --- CLEANUP ---
        self.play(
            FadeOut(
                Group(
                    curr_title,
                    ax,
                    qft_plot,
                    formula_label,
                    prob_formula,
                    note,
                    step1_title,
                    step3_title,
                    final_note,
                )
            )
        )

    def ShorRecover(self):
        header = title_bar("การใช้ค่า r ใน Shor's Algorithm")
        header.to_edge(UP, buff=HEADER_BUFF)
        self.play(Write(header))

        # --- 1. Success Case ---
        chain = (
            VGroup(
                VGroup(
                    th("Quantum step บอกว่า", size=24, color=C_MUTED),
                    MathTex("r = 4", color=C_ACCENT).scale(1.0),
                ).arrange(RIGHT, buff=0.25),
                VGroup(
                    th("ย้อนสูตร:", size=24, color=C_MUTED),
                    MathTex(r"y = x^{r/2} = 2^{4/2} = 4", color=WHITE).scale(0.95),
                ).arrange(RIGHT, buff=0.25),
                VGroup(
                    th("gcd:", size=24, color=C_MUTED),
                    MathTex(
                        r"\gcd(y-1, N) \text{ \& } \gcd(y+1, N)", color=C_POS
                    ).scale(0.8),
                ).arrange(RIGHT, buff=0.25),
                VGroup(
                    MathTex(r"15 = 3 \times 5", color=C_POS).scale(1.4),
                    th("  แยกตัวประกอบสำเร็จ!", size=28, color=C_POS, weight=BOLD),
                ).arrange(RIGHT, buff=0.3),
            )
            .arrange(DOWN, buff=0.4)
            .move_to(content_center())
        )

        for item in chain:
            self.play(FadeIn(item, shift=UP * 0.1))
            self.next_slide()

        # --- 2. Failure Case: When r is Odd ---
        self.play(chain.animate.set_opacity(0.15), header.animate.set_opacity(0.15))

        fail_box = RoundedRectangle(
            height=3, width=9, color=C_NEG, fill_opacity=0.1
        ).move_to(content_center())
        fail_title = th("ถ้า r เป็นเลขคี่ล่ะ? (Failure Case)", size=26, color=C_NEG).next_to(
            fail_box, UP, buff=0.3
        )

        # ใช้ MathTex สำหรับส่วนของสมการเพื่อให้แสดงผลเลขยกกำลังและเศษส่วนได้สวยงาม
        fail_line1 = VGroup(
            th("เราจะหาค่า", size=22),
            MathTex(r"y = x^{r/2}", color=C_NEG).scale(0.9),
            th("ที่เป็นจำนวนเต็มไม่ได้", size=22),
        ).arrange(RIGHT, buff=0.2)

        fail_line2 = VGroup(
            th("ทำให้ใช้สูตร", size=22),
            MathTex(r"\gcd", color=C_NEG).scale(0.9),
            th("เพื่อแยกตัวประกอบไม่ได้", size=22),
        ).arrange(RIGHT, buff=0.2)

        solution = th(
            "ทางแก้: สุ่มค่า x ใหม่ แล้วเริ่มทำ Quantum Step อีกครั้ง",
            size=24,
            color=C_ACCENT,
            weight=BOLD,
        )

        fail_content = (
            VGroup(fail_line1, fail_line2, solution)
            .arrange(DOWN, buff=0.4)
            .move_to(fail_box)
        )

        self.play(Create(fail_box), Write(fail_title))
        self.play(FadeIn(fail_content, shift=DOWN * 0.2))
        self.next_slide()

        # --- 3. Cleanup ---
        self.play(FadeOut(Group(header, chain, fail_box, fail_title, fail_content)))

    def ShorCaveats(self):
        # --- 1. HEADER & MULTI-FACTOR ---
        header = th("Shor's Algorithm: Complexity & ข้อจำกัด", color=C_ACCENT)
        header.to_edge(UP, buff=0.2)

        multi = (
            VGroup(
                th("If N has > 2 prime factors:", size=20, color=WHITE),
                th("Recurse and repeat", size=20, color=C_MUTED),
                MathTex(r"\gcd(x^{r/2} \pm 1, N)", color=C_ACCENT).scale(0.8),
                th("up to", size=20, color=C_MUTED),
                MathTex(r"\log N", color=C_POS).scale(1.1),
                th("times.", size=20, color=C_MUTED),
            )
            .arrange(RIGHT, buff=0.2)
            .to_edge(UP, buff=0.8)
        )

        self.play(Write(header))
        self.play(FadeIn(multi, shift=UP * 0.2))
        self.next_slide()

        # --- 2. COMPLEXITY DASHBOARD ---
        box_c = RoundedRectangle(height=2.5, width=5, color=C_MUTED, corner_radius=0.1)
        box_q = RoundedRectangle(height=2.5, width=5, color=C_POS, corner_radius=0.1)
        boxes = (
            VGroup(box_c, box_q).arrange(RIGHT, buff=0.5).next_to(multi, DOWN, buff=0.8)
        )

        lbl_c = th("Classical (GNFS)", size=22, color=C_MUTED).next_to(
            box_c, UP, buff=0.2
        )
        lbl_q = th("Shor's Algorithm", size=22, color=C_POS).next_to(
            box_q, UP, buff=0.2
        )

        math_c = (
            MathTex(
                r"O\left(e^{1.9 (\ln N)^{1/3} (\ln \ln N)^{2/3}}\right)", color=WHITE
            )
            .scale(0.7)
            .move_to(box_c)
        )

        math_q = (
            VGroup(
                MathTex(r"O(n^3)", color=WHITE),
                MathTex(r"\rightarrow O(n^2 \log n)", color=C_ACCENT).scale(0.8),
            )
            .arrange(DOWN, buff=0.2)
            .move_to(box_q)
        )

        # Speed visualization (Simple Bars)
        bar_c = (
            Rectangle(width=0.5, height=0.2, fill_opacity=1, color=RED)
            .next_to(box_c, DOWN, buff=0.2)
            .align_to(box_c, LEFT)
        )
        bar_q = (
            Rectangle(width=4.5, height=0.2, fill_opacity=1, color=GREEN)
            .next_to(box_q, DOWN, buff=0.2)
            .align_to(box_q, LEFT)
        )

        self.play(Create(boxes), Write(lbl_c), Write(lbl_q))
        self.play(Write(math_c), Write(math_q))
        self.play(GrowFromEdge(bar_c, LEFT), GrowFromEdge(bar_q, LEFT))

        technical_note = (
            VGroup(
                th("* Total complexity for any N: ", size=14, color=C_MUTED),
                MathTex(
                    r"O(\text{factors} \cdot n^3) \approx O(n^4)", color=C_ACCENT
                ).scale(0.5),
            )
            .arrange(RIGHT, buff=0.1)
            .next_to(bar_q, DOWN, buff=0.2)
            .align_to(bar_q, LEFT)
        )

        self.play(FadeIn(technical_note, shift=UP * 0.1))
        self.next_slide()

        # --- 3. HACKING & QUBIT REALITY ---
        hack_info = (
            VGroup(
                th("To crack RSA-2048:", size=24, color=WHITE),
                MathTex(r"\approx 6,200 \text{ Logical Qubits}", color=C_ACCENT).scale(
                    1.2
                ),
            )
            .arrange(RIGHT, buff=0.4)
            .next_to(boxes, DOWN, buff=1.0)
        )

        warning = (
            VGroup(
                th("Current Bottleneck:", size=20, color=RED, weight=BOLD),
                th("Error Correction & Massive Energy Needs", size=18, color=WHITE),
            )
            .arrange(DOWN, buff=0.1)
            .next_to(hack_info, DOWN, buff=0.4)
        )

        self.play(FadeIn(hack_info, shift=RIGHT * 0.5))
        self.play(Indicate(hack_info[1], color=C_ACCENT))
        self.next_slide()

        self.play(Write(warning))
        self.next_slide()

        # --- 4. CLEANUP ---
        self.play(
            FadeOut(
                Group(
                    header,
                    multi,
                    boxes,
                    lbl_c,
                    lbl_q,
                    math_c,
                    math_q,
                    bar_c,
                    bar_q,
                    technical_note,
                    hack_info,
                    warning,
                )
            )
        )

    def Tradeoffs(self):
        header = title_bar("Time & Space tradeoff")

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
                rect = Rectangle(
                    width=cell_w, height=cell_h, stroke_color=C_MUTED, stroke_width=1
                )
                rect.move_to([(j - 1) * cell_w, -i * cell_h, 0])
                if i == 0:
                    rect.set_fill(C_ACCENT, opacity=0.2)
                txt = Text(
                    val, font=TH_FONT, font_size=26, color=WHITE if i > 0 else C_ACCENT
                )
                txt.move_to(rect.get_center())
                table.add(rect, txt)
        table.move_to(ORIGIN).shift(DOWN * 0.3)
        self.play(FadeIn(table))
        self.next_slide()

        punch = th(
            "RSA-2048 แตกด้วย ~6000 logical qubits", size=32, color=C_NEG, weight=BOLD
        )
        punch.next_to(table, DOWN, buff=0.6)
        self.play(Write(punch))
        self.next_slide()
        self.play(*[FadeOut(m) for m in [header, table, punch]])

    def ShorReality(self):
        header = title_bar("Reality check")

        lines = VGroup(
            th("logical ≠ physical qubits", size=32, color=C_ACCENT),
            th("error correction: physical หลักล้าน ต่อ logical 1 ตัว", size=28),
            th("hardware ตอนนี้: ~1000 physical qubits + noise เยอะ", size=28),
            th("→ ยังห่างไกล", size=30, color=C_MUTED),
        ).arrange(DOWN, buff=0.35)
        lines.to_edge(UP, buff=0.5)
        for l in lines:
            self.play(FadeIn(l, shift=UP * 0.1))
        self.next_slide()

        warn = VGroup(
            th("แต่ข้อมูลที่ถูกดักวันนี้...", size=30),
            th('"Harvest now, decrypt later"', size=34, color=C_NEG, weight=BOLD),
            th("→ post-quantum crypto เริ่มใช้งานแล้ว", size=28, color=C_POS),
        ).arrange(DOWN, buff=0.3)
        warn.next_to(lines, DOWN, buff=0.5)
        self.play(Write(warn))
        self.next_slide()
        self.play(*[FadeOut(m) for m in [header, lines, warn]])

    def end(self):
        end = th("ขอบคุณครับ", size=72, color=C_ACCENT, weight=BOLD)
        q = th("มีคำถามอะไรสามารถถามได้เลย", size=36, color=C_MUTED)
        q.next_to(end, DOWN, buff=0.4)
        self.play(FadeIn(end, shift=UP * 0.3), FadeIn(q))
        self.next_slide()
