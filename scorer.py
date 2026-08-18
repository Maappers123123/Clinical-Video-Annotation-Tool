import os
import csv
import math
import cv2
import numpy as np
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Union
from PIL import Image, ImageTk, ImageDraw

# ============================================================
# DESIGN TOKENS
# ============================================================

COLORS = {
    "app_bg": "#eef2ff",
    "card_bg": "#ffffff",
    "panel_bg": "#f8fafc",
    "border": "#e2e8f0",
    "border_soft": "#e5e7eb",
    "text": "#0f172a",
    "muted": "#64748b",
    "primary": "#2563eb",
    "primary_hover": "#1d4ed8",
    "primary_soft": "#dbeafe",
    "primary_xsoft": "#eff6ff",
    "secondary_btn": "#f1f5f9",
    "secondary_hover": "#e2e8f0",
    "disabled_text": "#94a3b8",
    "warning": "#ea580c",
    "danger": "#dc2626",
    "danger_bg": "#fee2e2",
    "danger_hover": "#fecaca",
    "timeline_track": "#EEF2FF",
    "timeline_outline": "#C7D2FE",
    "timeline_selected": "#A3A5F4",
    "timeline_selected_soft": "#BBBCFF",
    "timeline_tick": "#C7D2FE",
    "timeline_label": "#5480F9",
    "timeline_knob": "#2B63FF",
    "overlay_green": (34, 197, 94),
    "overlay_shadow": (0, 0, 0),
}

PRIMARY_BUTTON_KW = {
    "fg_color": COLORS["primary"],
    "hover_color": COLORS["primary_hover"],
    "text_color": "white",
}

SECONDARY_BUTTON_KW = {
    "fg_color": COLORS["secondary_btn"],
    "hover_color": COLORS["secondary_hover"],
    "text_color": COLORS["text"],
}

FONT_MAIN = "Segoe UI"

UNSCORABLE_VALUE = "X"

# ============================================================
# CONFIG / REGION DEFINITIONS
# ============================================================

DIS_ALL_REGIONS = [
    "eye_dystonia", "eye_choreoathetosis",
    "mouth_dystonia", "mouth_choreoathetosis",
    "neck_dystonia", "neck_choreoathetosis",
    "trunk_dystonia", "trunk_choreoathetosis",
    "r_proximal_arm_dystonia", "r_proximal_arm_choreoathetosis",
    "r_distal_arm_dystonia", "r_distal_arm_choreoathetosis",
    "l_proximal_arm_dystonia", "l_proximal_arm_choreoathetosis",
    "l_distal_arm_dystonia", "l_distal_arm_choreoathetosis",
    "r_proximal_leg_dystonia", "r_proximal_leg_choreoathetosis",
    "r_distal_leg_dystonia", "r_distal_leg_choreoathetosis",
    "l_proximal_leg_dystonia", "l_proximal_leg_choreoathetosis",
    "l_distal_leg_dystonia", "l_distal_leg_choreoathetosis",
]

DIS_QUOVADYS_REGIONS = [
    "neck_dystonia", "neck_choreoathetosis",
    "r_proximal_arm_dystonia", "r_proximal_arm_choreoathetosis",
    "r_distal_arm_dystonia", "r_distal_arm_choreoathetosis",
    "l_proximal_arm_dystonia", "l_proximal_arm_choreoathetosis",
    "l_distal_arm_dystonia", "l_distal_arm_choreoathetosis",
    "r_distal_leg_dystonia", "r_distal_leg_choreoathetosis",
    "l_distal_leg_dystonia", "l_distal_leg_choreoathetosis",
]

BADS_REGIONS = [
    "bads_eye",
    "bads_nose",
    "bads_mouth",
    "bads_neck",
    "bads_l_upper_extremity",
    "bads_r_upper_extremity",
    "bads_l_lower_extremity",
    "bads_r_lower_extremity",
]

# UMC preset: BADS without eye/nose items. Mouth stays included.
UMC_REGIONS = [
    region for region in BADS_REGIONS
    if not any(excluded in region for excluded in ("eye", "nose"))
]

REGION_LABELS = {
    "eye_dystonia": "Eye dystonia",
    "eye_choreoathetosis": "Eye choreoathetosis",
    "mouth_dystonia": "Mouth dystonia",
    "mouth_choreoathetosis": "Mouth choreoathetosis",
    "neck_dystonia": "Neck dystonia",
    "neck_choreoathetosis": "Neck choreoathetosis",
    "trunk_dystonia": "Trunk dystonia",
    "trunk_choreoathetosis": "Trunk choreoathetosis",
    "r_proximal_arm_dystonia": "R proximal arm dystonia",
    "r_proximal_arm_choreoathetosis": "R proximal arm choreoathetosis",
    "r_distal_arm_dystonia": "R distal arm dystonia",
    "r_distal_arm_choreoathetosis": "R distal arm choreoathetosis",
    "l_proximal_arm_dystonia": "L proximal arm dystonia",
    "l_proximal_arm_choreoathetosis": "L proximal arm choreoathetosis",
    "l_distal_arm_dystonia": "L distal arm dystonia",
    "l_distal_arm_choreoathetosis": "L distal arm choreoathetosis",
    "r_proximal_leg_dystonia": "R proximal leg dystonia",
    "r_proximal_leg_choreoathetosis": "R proximal leg choreoathetosis",
    "r_distal_leg_dystonia": "R distal leg dystonia",
    "r_distal_leg_choreoathetosis": "R distal leg choreoathetosis",
    "l_proximal_leg_dystonia": "L proximal leg dystonia",
    "l_proximal_leg_choreoathetosis": "L proximal leg choreoathetosis",
    "l_distal_leg_dystonia": "L distal leg dystonia",
    "l_distal_leg_choreoathetosis": "L distal leg choreoathetosis",
    "bads_eye": "BADS eye",
    "bads_nose": "BADS nose",
    "bads_mouth": "BADS mouth",
    "bads_neck": "BADS neck",
    "bads_l_upper_extremity": "BADS L upper extremity",
    "bads_r_upper_extremity": "BADS R upper extremity",
    "bads_l_lower_extremity": "BADS L lower extremity",
    "bads_r_lower_extremity": "BADS R lower extremity",
}

# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class SessionConfig:
    score_max: int
    scoring_mode: str
    movement_mode: str
    selected_scales: List[str]
    dis_mode: Optional[str] = None
    selected_regions: List[str] = field(default_factory=list)
    score_layout_mode: str = "whole_body"
    export_mp4: bool = True
    save_csv: bool = True

@dataclass
class VideoJob:
    path: str

# ============================================================
# HELPERS
# ============================================================

def safe_base_name(video_path: str) -> str:
    return os.path.splitext(video_path)[0]

def ensure_unique(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out

def filter_regions_by_movement(regions: List[str], movement_mode: str) -> List[str]:
    if movement_mode == "both":
        return regions[:]
    if movement_mode == "dystonia":
        return [r for r in regions if "choreoathetosis" not in r]
    return [r for r in regions if "choreoathetosis" in r]

def normalize_score_value(value: object) -> str:
    if value is None:
        return ""
    value = str(value).strip()
    if value.upper() == UNSCORABLE_VALUE:
        return UNSCORABLE_VALUE
    return value

def score_value_is_filled(value: object) -> bool:
    return normalize_score_value(value) != ""

def score_value_is_valid(value: object, score_max: int) -> bool:
    value = normalize_score_value(value)
    if value == UNSCORABLE_VALUE:
        return True
    try:
        intval = int(value)
        return 0 <= intval <= score_max
    except Exception:
        return False

# ============================================================
# CSV STORAGE
# ============================================================

class CSVStorage:
    STATIC_COLUMNS = [
        "video_name", "video_path", "scoring_mode", "scale_max",
        "segment_index", "segment_start_s", "segment_end_s", "region_mode",
    ]

    @staticmethod
    def csv_path_for_video(video_path: str) -> str:
        return f"{safe_base_name(video_path)}_scores.csv"

    @staticmethod
    def export_video_path_for_video(video_path: str) -> str:
        return f"{safe_base_name(video_path)}_scored.mp4"

    @classmethod
    def save_rows(cls, video_path: str, config: SessionConfig, rows: List[Dict[str, str]]) -> str:
        csv_path = cls.csv_path_for_video(video_path)
        fieldnames = cls.STATIC_COLUMNS + config.selected_regions
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: row.get(k, "") for k in fieldnames})
        return csv_path

    @classmethod
    def try_load_rows(cls, video_path: str) -> List[Dict[str, str]]:
        csv_path = cls.csv_path_for_video(video_path)
        if not os.path.exists(csv_path):
            return []
        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            return [dict(row) for row in csv.DictReader(f)]

# ============================================================
# VIDEO HELPERS
# ============================================================

class PILOverlay:
    @staticmethod
    def draw_text_block(
        img: Image.Image,
        lines: List[str],
        xy=(20, 20),
        fill=COLORS["overlay_green"],
        shadow=COLORS["overlay_shadow"],
        line_height=26,
        max_lines=16
    ) -> Image.Image:
        draw = ImageDraw.Draw(img)
        x, y = xy
        for line in lines[:max_lines]:
            draw.text((x + 1, y + 1), line, fill=shadow)
            draw.text((x, y), line, fill=fill)
            y += line_height
        return img

    @staticmethod
    def fit_to_box(img: Image.Image, box_w: int, box_h: int) -> Image.Image:
        if box_w <= 1 or box_h <= 1:
            return img
        src_w, src_h = img.size
        scale = min(box_w / src_w, box_h / src_h)
        new_size = (max(1, int(src_w * scale)), max(1, int(src_h * scale)))
        return img.resize(new_size, Image.Resampling.LANCZOS)

class VideoExporter:
    @staticmethod
    def export_with_overlay(video_path: str, config: SessionConfig, rows: List[Dict[str, str]]) -> Optional[str]:
        out_path = CSVStorage.export_video_path_for_video(video_path)
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        if fps <= 0:
            fps = 30.0

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if width <= 0 or height <= 0:
            cap.release()
            return None

        writer = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
        window_size_frames = max(1, int(round(fps * 5)))

        row_lookup = {}
        for row in rows:
            try:
                row_lookup[int(row["segment_index"])] = row
            except Exception:
                pass

        frame_idx = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            seg_idx = 0 if config.scoring_mode == "full" else frame_idx // window_size_frames
            row = row_lookup.get(seg_idx)
            if row:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil = Image.fromarray(rgb)
                lines = [f"Window: {int(row['segment_index']) + 1}", f"Time: {frame_idx / fps:.1f}s"]
                for region in config.selected_regions:
                    value = normalize_score_value(row.get(region, ""))
                    if value != "":
                        lines.append(f"{REGION_LABELS.get(region, region)}: {value}")
                PILOverlay.draw_text_block(pil, lines, xy=(30, 30), max_lines=16)
                frame = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

            writer.write(frame)
            frame_idx += 1

        cap.release()
        writer.release()
        return out_path

class VideoSession:
    def __init__(self, video_path: str, config: SessionConfig):
        self.video_path = video_path
        self.config = config
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open video: {video_path}")

        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        if self.fps <= 0:
            self.fps = 30.0

        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.window_size_frames = max(1, int(round(self.fps * 5)))
        self.num_segments = 1 if config.scoring_mode == "full" else math.ceil(self.total_frames / self.window_size_frames)

    def get_segment_frame_range(self, segment_index: int) -> Tuple[int, int]:
        if self.config.scoring_mode == "full":
            return 0, self.total_frames
        start = segment_index * self.window_size_frames
        end = min((segment_index + 1) * self.window_size_frames, self.total_frames)
        return start, end

    def get_segment_time_range(self, segment_index: int) -> Tuple[float, float]:
        start_frame, end_frame = self.get_segment_frame_range(segment_index)
        return start_frame / self.fps, end_frame / self.fps

    def seek_to_frame(self, frame_idx: int):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)

    def read_frame(self):
        return self.cap.read()

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None

# ============================================================
# CUSTOM SCORE BUTTONS
# ============================================================

class ScoreButtonGroup(ctk.CTkFrame):
    def __init__(self, parent, score_max: int, command=None):
        super().__init__(parent, fg_color="transparent")
        self.score_max = score_max
        self.command = command
        self.value: str = ""
        self.buttons: Dict[Union[int, str], ctk.CTkButton] = {}
        self.enabled = True

        # Oude afmetingen:
        # numerieke knoppen: width 34, height 32
        # X-knop: width 40, height 32
        # spacing: 6 px tussen knoppen
        for val in list(range(score_max + 1)) + [UNSCORABLE_VALUE]:
            btn = ctk.CTkButton(
                self,
                text=str(val),
                width=(40 if val == UNSCORABLE_VALUE else 34),
                height=32,
                corner_radius=9,
                fg_color=COLORS["primary_xsoft"],
                text_color=COLORS["text"],
                hover_color=COLORS["primary_soft"],
                command=lambda v=val: self.set_value(v, trigger=True),
            )
            btn.pack(side="left", padx=(0 if val == 0 else 6, 0))
            self.buttons[val] = btn

        self._refresh_visuals()

    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        for btn in self.buttons.values():
            btn.configure(state="normal" if enabled else "disabled")
        self._refresh_visuals()

    def set_value(self, value: Union[int, str], trigger: bool = False):
        if not self.enabled:
            return
        self.value = normalize_score_value(value)
        self._refresh_visuals()
        if trigger and self.command:
            self.command(self.value)

    def set_value_from_storage(self, value: object):
        value = normalize_score_value(value)
        if value == "":
            self.clear()
            return
        self.value = value
        self._refresh_visuals()

    def clear(self):
        self.value = ""
        self._refresh_visuals()

    def get_value(self) -> str:
        return self.value

    def is_filled(self) -> bool:
        return self.value != ""

    def _refresh_visuals(self):
        for val, btn in self.buttons.items():
            is_selected = str(val) == self.value
            if is_selected:
                if val == UNSCORABLE_VALUE:
                    btn.configure(fg_color="#ef4444", text_color="white", hover_color="#dc2626")
                else:
                    btn.configure(fg_color=COLORS["primary"], text_color="white", hover_color=COLORS["primary_hover"])
            else:
                btn.configure(
                    fg_color=COLORS["primary_xsoft"],
                    text_color=COLORS["text"],
                    hover_color=COLORS["primary_soft"],
                )
# ============================================================
# MAIN APP
# ============================================================

class VideoScorerApp(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        super().__init__()

        self.title("Clinical Video Annotation Tool")
        self.geometry("1280x760")
        self.minsize(1150, 700)
        self.configure(fg_color=COLORS["app_bg"])

        self.config_data: Optional[SessionConfig] = None
        self.jobs: List[VideoJob] = []

        self.container = ctk.CTkFrame(self, fg_color=COLORS["app_bg"])
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for frame_cls in (ConfigScreen, FileSelectionScreen, AnnotationScreen):
            frame = frame_cls(self.container, self)
            self.frames[frame_cls.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show("ConfigScreen")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def show(self, name: str):
        self.frames[name].tkraise()
        self.after(100, self.focus_force)

    def start_annotation(self, config: SessionConfig, jobs: List[VideoJob]):
        self.config_data = config
        self.jobs = jobs
        self.frames["AnnotationScreen"].start_session(config, jobs)
        self.show("AnnotationScreen")

    def on_close(self):
        try:
            self.frames["AnnotationScreen"].shutdown()
        except Exception:
            pass
        self.destroy()

# ============================================================
# CONFIG SCREEN
# ============================================================

class ConfigScreen(ctk.CTkFrame):
    def __init__(self, parent, app: VideoScorerApp):
        super().__init__(parent, fg_color=COLORS["app_bg"])
        self.app = app
        self.dis_region_vars: Dict[str, ctk.BooleanVar] = {}
        self.bads_region_vars: Dict[str, ctk.BooleanVar] = {}
        self.body_part_container = None
        self.warning_label = None
        self._build_ui()
        self._apply_preset()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(18, 8))
        ctk.CTkLabel(header, text="Clinical Video Annotation", font=(FONT_MAIN, 30, "bold"), text_color=COLORS["text"]).pack(anchor="w")
        ctk.CTkLabel(header, text="Configure your annotation session", font=(FONT_MAIN, 15), text_color=COLORS["muted"]).pack(anchor="w", pady=(4, 0))

        card = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=22, border_width=1, border_color=COLORS["border"])
        card.grid(row=1, column=0, sticky="nsew", padx=28, pady=(10, 24))
        card.grid_columnconfigure(0, weight=0)
        card.grid_columnconfigure(1, weight=1)
        card.grid_rowconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=0)

        left_scroll = ctk.CTkScrollableFrame(card, fg_color=COLORS["card_bg"], corner_radius=18, width=310)
        left_scroll.grid(row=0, column=0, sticky="nsew", padx=(28, 18), pady=24)

        right = ctk.CTkFrame(card, fg_color=COLORS["card_bg"])
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 28), pady=24)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        bottom = ctk.CTkFrame(card, fg_color=COLORS["card_bg"])
        bottom.grid(row=1, column=0, columnspan=2, sticky="ew", padx=28, pady=(0, 24))
        bottom.grid_columnconfigure(0, weight=1)

        self.scale_var = ctk.IntVar(value=4)
        self.scoring_mode_var = ctk.StringVar(value="window")
        self.movement_var = ctk.StringVar(value="both")
        self.use_dis_var = ctk.BooleanVar(value=True)
        self.use_bads_var = ctk.BooleanVar(value=False)
        self.dis_mode_var = ctk.StringVar(value="quovadys")
        self.layout_mode_var = ctk.StringVar(value="whole_body")
        self.export_mp4_var = ctk.BooleanVar(value=True)
        self.save_csv_var = ctk.BooleanVar(value=True)
        self.preset_var = ctk.StringVar(value="QUOVADYS")

        self._section_label(left_scroll, "Project Preset")
        self.preset_combo = ctk.CTkComboBox(
            left_scroll,
            variable=self.preset_var,
            values=[
                "None (Manual Selection)",
                "Dystonia Impairment Scale (DIS)",
                "QUOVADYS",
                "BADS",
                "UMC",
                "DIS + BADS",
            ],
            command=lambda _value: self._apply_preset(),
            height=40,
            corner_radius=12,
            fg_color=COLORS["panel_bg"],
            border_color="#cbd5e1",
            button_color="#e0e7ff",
            button_hover_color="#c7d2fe",
            dropdown_fg_color="white",
            text_color=COLORS["text"]
        )
        self.preset_combo.pack(fill="x", pady=(0, 18))

        self._section_label(left_scroll, "Point Scale")
        self._radio(left_scroll, "3-point scale (0-2)", self.scale_var, 2)
        self._radio(left_scroll, "5-point scale (0-4)", self.scale_var, 4)
        self._spacer(left_scroll)

        self._section_label(left_scroll, "Timing Mode")
        self._radio(left_scroll, "Score every 5-second window", self.scoring_mode_var, "window")
        self._radio(left_scroll, "Score full video", self.scoring_mode_var, "full")
        self._spacer(left_scroll)

        self._section_label(left_scroll, "Body Scoring Mode")
        self._radio(left_scroll, "Score whole body at once", self.layout_mode_var, "whole_body")
        self._radio(left_scroll, "Score each body part separately", self.layout_mode_var, "region_by_region")
        self._spacer(left_scroll)

        self._section_label(left_scroll, "Clinical Scale Type")
        self._check(left_scroll, "Dystonia Impairment Scale (DIS)", self.use_dis_var, self._refresh_body_parts)

        self.dis_movement_box = ctk.CTkFrame(left_scroll, fg_color=COLORS["panel_bg"], corner_radius=12)
        self.dis_movement_box.pack(fill="x", padx=(18, 0), pady=(6, 12))
        self.dis_movement_buttons = [
            self._radio(self.dis_movement_box, "Score Dystonia", self.movement_var, "dystonia", self._refresh_body_parts),
            self._radio(self.dis_movement_box, "Score Choreoathetosis", self.movement_var, "choreoathetosis", self._refresh_body_parts),
            self._radio(self.dis_movement_box, "Score both", self.movement_var, "both", self._refresh_body_parts),
        ]

        self._check(left_scroll, "Barry Albright Dystonia Scale (BADS)", self.use_bads_var, self._refresh_body_parts)
        self._spacer(left_scroll)

        self._section_label(left_scroll, "Saving Options")
        self._check(left_scroll, "Save CSV score file", self.save_csv_var, self._update_continue_state)
        self._check(left_scroll, "Create annotated MP4 control video", self.export_mp4_var, self._update_continue_state)

        body_header = ctk.CTkFrame(right, fg_color=COLORS["card_bg"])
        body_header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        body_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(body_header, text="Body Parts to Score", font=(FONT_MAIN, 19, "bold"), text_color=COLORS["text"]).pack(anchor="w")
        ctk.CTkLabel(
            body_header,
            text="This list updates automatically based on the selected preset and scale type. UMC = BADS without eye/nose items. (L = Left, R = Right)",
            font=(FONT_MAIN, 13),
            text_color=COLORS["muted"]
        ).pack(anchor="w", pady=(4, 0))

        self.body_part_container = ctk.CTkScrollableFrame(
            right,
            fg_color=COLORS["panel_bg"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["border"],
            scrollbar_button_color="#cbd5e1",
            scrollbar_button_hover_color="#94a3b8"
        )
        self.body_part_container.grid(row=1, column=0, sticky="nsew", pady=(16, 0))
        self.body_part_container.grid_columnconfigure(0, weight=1)
        self.body_part_container.grid_columnconfigure(1, weight=1)

        self.warning_label = ctk.CTkLabel(bottom, text="", font=(FONT_MAIN, 13), text_color=COLORS["warning"])
        self.warning_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.continue_btn = ctk.CTkButton(
            bottom,
            text="Start Annotation Session",
            height=48,
            corner_radius=14,
            font=(FONT_MAIN, 15, "bold"),
            command=self._confirm,
            **PRIMARY_BUTTON_KW
        )
        self.continue_btn.grid(row=1, column=0, sticky="ew")

    def _section_label(self, parent, text: str):
        ctk.CTkLabel(parent, text=text, font=(FONT_MAIN, 15, "bold"), text_color=COLORS["text"]).pack(anchor="w", pady=(0, 6))

    def _spacer(self, parent):
        ctk.CTkFrame(parent, height=16, fg_color="transparent").pack(fill="x")

    def _radio(self, parent, text, variable, value, command=None):
        btn = ctk.CTkRadioButton(
            parent,
            text=text,
            variable=variable,
            value=value,
            command=command,
            radiobutton_width=18,
            radiobutton_height=18,
            border_width_checked=6,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color="#1e293b",
            font=(FONT_MAIN, 13)
        )
        btn.pack(anchor="w", pady=4, padx=8)
        return btn

    def _check(self, parent, text, variable, command=None):
        ctk.CTkCheckBox(
            parent,
            text=text,
            variable=variable,
            command=command,
            checkbox_width=18,
            checkbox_height=18,
            corner_radius=5,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color="#1e293b",
            font=(FONT_MAIN, 13)
        ).pack(anchor="w", pady=5)

    def _apply_preset(self):
        preset = self.preset_var.get()

        if preset == "None (Manual Selection)":
            self.use_dis_var.set(True)
            self.use_bads_var.set(False)
            self.dis_mode_var.set("manual")
            self.movement_var.set("both")
        elif preset == "Dystonia Impairment Scale (DIS)":
            self.use_dis_var.set(True)
            self.use_bads_var.set(False)
            self.dis_mode_var.set("dis_i")
            self.movement_var.set("both")
        elif preset == "QUOVADYS":
            self.use_dis_var.set(True)
            self.use_bads_var.set(False)
            self.dis_mode_var.set("quovadys")
            self.movement_var.set("both")
        elif preset == "BADS":
            self.use_dis_var.set(False)
            self.use_bads_var.set(True)
            self.dis_mode_var.set("manual")
            self.movement_var.set("dystonia")
        elif preset == "UMC":
            self.use_dis_var.set(False)
            self.use_bads_var.set(True)
            self.dis_mode_var.set("manual")
            self.movement_var.set("dystonia")
        elif preset == "DIS + BADS":
            self.use_dis_var.set(True)
            self.use_bads_var.set(True)
            self.dis_mode_var.set("dis_i")
            self.movement_var.set("both")

        self._refresh_body_parts()

    def _clear_body_parts(self):
        if not self.body_part_container:
            return
        for widget in self.body_part_container.winfo_children():
            widget.destroy()
        self.dis_region_vars.clear()
        self.bads_region_vars.clear()

    def _body_part_checkbox(self, region, var, row, col):
        box = ctk.CTkFrame(self.body_part_container, fg_color=COLORS["card_bg"], corner_radius=13)
        box.grid(row=row, column=col, sticky="ew", padx=10, pady=7)
        ctk.CTkCheckBox(
            box,
            text=REGION_LABELS.get(region, region),
            variable=var,
            command=self._update_continue_state,
            checkbox_width=18,
            checkbox_height=18,
            corner_radius=5,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color=COLORS["text"],
            font=(FONT_MAIN, 13)
        ).pack(fill="x", padx=12, pady=11)

    def _refresh_body_parts(self):
        self._clear_body_parts()
        items = []

        if self.use_dis_var.get():
            if self.dis_mode_var.get() == "quovadys":
                dis_regions = DIS_QUOVADYS_REGIONS[:]
            elif self.dis_mode_var.get() == "dis_i":
                dis_regions = DIS_ALL_REGIONS[:]
            else:
                dis_regions = DIS_ALL_REGIONS[:]

            dis_regions = filter_regions_by_movement(dis_regions, self.movement_var.get())
            for region in dis_regions:
                default_checked = self.dis_mode_var.get() in ("quovadys", "dis_i")
                if self.preset_var.get() == "None (Manual Selection)":
                    default_checked = False
                var = ctk.BooleanVar(value=default_checked)
                self.dis_region_vars[region] = var
                items.append((region, var))

        if self.use_bads_var.get():
            bads_regions = UMC_REGIONS[:] if self.preset_var.get() == "UMC" else BADS_REGIONS[:]
            for region in bads_regions:
                var = ctk.BooleanVar(value=True)
                self.bads_region_vars[region] = var
                items.append((region, var))

        for idx, (region, var) in enumerate(items):
            self._body_part_checkbox(region, var, idx // 2, idx % 2)

        if hasattr(self, "dis_movement_buttons"):
            state = "normal" if self.use_dis_var.get() else "disabled"
            for btn in self.dis_movement_buttons:
                btn.configure(state=state)

        self._update_continue_state()

    def _get_selected_regions(self) -> List[str]:
        selected = []
        if self.use_dis_var.get():
            selected.extend([r for r, v in self.dis_region_vars.items() if v.get()])
        if self.use_bads_var.get():
            selected.extend([r for r, v in self.bads_region_vars.items() if v.get()])
        return ensure_unique(selected)

    def _update_continue_state(self):
        selected_regions = self._get_selected_regions()

        if not self.use_dis_var.get() and not self.use_bads_var.get():
            self.warning_label.configure(text="Please select at least one clinical scale")
            self.continue_btn.configure(state="disabled")
            return

        if not selected_regions:
            self.warning_label.configure(text="Please select at least one body part")
            self.continue_btn.configure(state="disabled")
            return

        if not self.save_csv_var.get() and not self.export_mp4_var.get():
            self.warning_label.configure(text="Please select at least one saving option")
            self.continue_btn.configure(state="disabled")
            return

        self.warning_label.configure(text="")
        self.continue_btn.configure(state="normal")

    def _confirm(self):
        selected_regions = self._get_selected_regions()

        if not self.use_dis_var.get() and not self.use_bads_var.get():
            messagebox.showwarning("Selection required", "Select at least one clinical scale.")
            return

        if not selected_regions:
            messagebox.showwarning("Selection required", "Select at least one body part to score.")
            return

        if not self.save_csv_var.get() and not self.export_mp4_var.get():
            messagebox.showwarning("Selection required", "Select at least one saving option.")
            return

        selected_scales = []
        dis_mode = None
        if self.use_dis_var.get():
            selected_scales.append("DIS")
            dis_mode = self.dis_mode_var.get()
        if self.use_bads_var.get():
            selected_scales.append("BADS")

        self.app.config_data = SessionConfig(
            score_max=self.scale_var.get(),
            scoring_mode=self.scoring_mode_var.get(),
            movement_mode=self.movement_var.get(),
            selected_scales=selected_scales,
            dis_mode=dis_mode,
            selected_regions=selected_regions,
            score_layout_mode=self.layout_mode_var.get(),
            export_mp4=self.export_mp4_var.get(),
            save_csv=self.save_csv_var.get()
        )
        self.app.show("FileSelectionScreen")

# ============================================================
# FILE SELECTION SCREEN
# ============================================================

class FileSelectionScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["app_bg"])
        self.app = app
        self.paths: List[str] = []
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(18, 8))
        ctk.CTkLabel(header, text="Select Videos", font=(FONT_MAIN, 30, "bold"), text_color=COLORS["text"]).pack(anchor="w")
        ctk.CTkLabel(header, text="Add one or more MP4 files, or select a folder containing MP4 files.", font=(FONT_MAIN, 15), text_color=COLORS["muted"]).pack(anchor="w", pady=(4, 0))

        card = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=22, border_width=1, border_color=COLORS["border"])
        card.grid(row=1, column=0, sticky="nsew", padx=28, pady=(10, 24))
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        btns = ctk.CTkFrame(card, fg_color=COLORS["card_bg"])
        btns.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 12))

        ctk.CTkButton(btns, text="Add MP4 files", command=self._add_files, height=40, corner_radius=12, **PRIMARY_BUTTON_KW).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btns, text="Add folder", command=self._add_folder, height=40, corner_radius=12, **PRIMARY_BUTTON_KW).pack(side="left", padx=10)
        ctk.CTkButton(btns, text="Remove selected", command=self._remove_selected, height=40, corner_radius=12, **SECONDARY_BUTTON_KW).pack(side="left", padx=10)
        ctk.CTkButton(btns, text="Clear list", command=self._clear, height=40, corner_radius=12, **SECONDARY_BUTTON_KW).pack(side="left", padx=10)

        list_frame = ctk.CTkFrame(card, fg_color=COLORS["panel_bg"], corner_radius=16, border_width=1, border_color=COLORS["border"])
        list_frame.grid(row=1, column=0, sticky="nsew", padx=24, pady=12)
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.listbox = tk.Listbox(
            list_frame,
            selectmode="extended",
            bd=0,
            highlightthickness=0,
            bg=COLORS["panel_bg"],
            fg=COLORS["text"],
            font=(FONT_MAIN, 11),
            activestyle="none"
        )
        self.listbox.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        scrollbar = ctk.CTkScrollbar(list_frame, command=self.listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=12, padx=(0, 12))
        self.listbox.configure(yscrollcommand=scrollbar.set)
        self.listbox.bind("<Delete>", lambda e: self._remove_selected())
        self.listbox.bind("<Double-Button-1>", lambda e: self._remove_double_clicked())

        nav = ctk.CTkFrame(card, fg_color=COLORS["card_bg"])
        nav.grid(row=2, column=0, sticky="ew", padx=24, pady=(12, 24))
        nav.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(nav, text="Back", command=lambda: self.app.show("ConfigScreen"), height=42, corner_radius=12, **SECONDARY_BUTTON_KW).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(nav, text="Start Annotation", command=self._start, height=42, corner_radius=12, font=(FONT_MAIN, 14, "bold"), **PRIMARY_BUTTON_KW).grid(row=0, column=2, sticky="e")

    def _refresh(self):
        self.listbox.delete(0, "end")
        for path in self.paths:
            self.listbox.insert("end", path)

    def _add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("MP4 files", "*.mp4"), ("Video files", "*.mp4 *.avi *.mov *.mkv *.m4v")])
        if files:
            self.paths = sorted(set(self.paths).union(files), key=str.lower)
            self._refresh()

    def _add_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        files = [
            os.path.join(folder, name)
            for name in sorted(os.listdir(folder), key=str.lower)
            if name.lower().endswith(".mp4") and os.path.isfile(os.path.join(folder, name))
        ]
        if not files:
            messagebox.showinfo("No MP4 files", "No MP4 files found in selected folder.")
            return
        self.paths = sorted(set(self.paths).union(files), key=str.lower)
        self._refresh()

    def _remove_selected(self):
        selected = list(self.listbox.curselection())
        if not selected:
            return
        selected_paths = {self.listbox.get(i) for i in selected}
        self.paths = [p for p in self.paths if p not in selected_paths]
        self._refresh()

    def _remove_double_clicked(self):
        sel = self.listbox.curselection()
        if sel:
            path = self.listbox.get(sel[0])
            self.paths = [p for p in self.paths if p != path]
            self._refresh()

    def _clear(self):
        self.paths = []
        self._refresh()

    def _start(self):
        if not self.paths:
            messagebox.showwarning("No videos selected", "Add at least one MP4 video or a folder containing MP4 videos.")
            return
        if not self.app.config_data:
            messagebox.showwarning("No configuration", "Please configure the annotation session first.")
            self.app.show("ConfigScreen")
            return
        self.app.start_annotation(self.app.config_data, [VideoJob(path=p) for p in self.paths])

# ============================================================
# ANNOTATION SCREEN
# ============================================================

class AnnotationScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["app_bg"])
        self.app = app
        self.config: Optional[SessionConfig] = None
        self.jobs: List[VideoJob] = []
        self.video_session: Optional[VideoSession] = None
        self.current_video_idx = 0
        self.current_segment_idx = 0
        self.current_region_idx = 0
        self.rows: List[Dict[str, str]] = []
        self.playing = False
        self.play_job = None
        self.segment_start_frame = 0
        self.segment_end_frame = 0
        self.segment_finished = False
        self.current_pil_frame: Optional[Image.Image] = None
        self.tk_preview = None
        self.score_groups: Dict[str, ScoreButtonGroup] = {}
        self.score_cards: List[Tuple[str, ctk.CTkFrame]] = []
        self.active_score_index = 0
        self.first_play_done_for_step = False
        self.current_play_mode = "first_watch"
        self.review_existing_video = False
        self._build_ui()
        self._bind_keys()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(14, 8))

        self.title_row = ctk.CTkFrame(header, fg_color="transparent")
        self.title_row.pack(anchor="w", fill="x")

        self.video_prefix_label = ctk.CTkLabel(self.title_row, text="Video", font=(FONT_MAIN, 22, "bold"), text_color=COLORS["text"])
        self.video_prefix_label.pack(side="left")

        self.video_name_label = ctk.CTkLabel(self.title_row, text="", font=(FONT_MAIN, 22, "bold"), text_color=COLORS["primary"])
        self.video_name_label.pack(side="left")

        self.status_label = ctk.CTkLabel(header, text="", font=(FONT_MAIN, 12), text_color=COLORS["primary"])
        self.status_label.pack(anchor="w", pady=(4, 0))

        self.subheader = ctk.CTkLabel(header, text="", font=(FONT_MAIN, 13), text_color=COLORS["muted"])
        self.subheader.pack(anchor="w", pady=(2, 0))

        self.segment_label = ctk.CTkLabel(header, text="", font=(FONT_MAIN, 14, "bold"), text_color=COLORS["text"])
        self.segment_label.pack(anchor="w", pady=(4, 0))

        self.region_mode_label = ctk.CTkLabel(header, text="", font=(FONT_MAIN, 12), text_color=COLORS["muted"])
        self.region_mode_label.pack(anchor="w")

        main = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=22, border_width=1, border_color=COLORS["border"])
        main.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 16))
        main.grid_columnconfigure(0, weight=3)
        main.grid_columnconfigure(1, weight=1, minsize=360)
        main.grid_rowconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=0)

        video_area = ctk.CTkFrame(main, fg_color=COLORS["card_bg"])
        video_area.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        video_area.grid_rowconfigure(0, weight=1)
        video_area.grid_rowconfigure(1, weight=0)
        video_area.grid_columnconfigure(0, weight=1)

        self.video_canvas = tk.Label(video_area, bg="black")
        self.video_canvas.grid(row=0, column=0, sticky="nsew")

        self.timeline_canvas = tk.Canvas(video_area, height=44, bg=COLORS["card_bg"], highlightthickness=0)
        self.timeline_canvas.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        self.timeline_canvas.bind("<Configure>", lambda e: self._draw_timeline())

        score_panel = ctk.CTkFrame(main, fg_color=COLORS["panel_bg"], corner_radius=16, border_width=1, border_color=COLORS["border"])
        score_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        score_panel.grid_columnconfigure(0, weight=1)
        score_panel.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(score_panel, text="Scores", font=(FONT_MAIN, 18, "bold"), text_color=COLORS["text"]).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 8))
        ctk.CTkLabel(score_panel, text="↑/↓ navigate • 0–4 score • X unscorable", font=(FONT_MAIN, 12), text_color=COLORS["muted"]).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 8))

        self.score_scroll = ctk.CTkScrollableFrame(
            score_panel,
            fg_color="transparent",
            scrollbar_button_color="#cbd5e1",
            scrollbar_button_hover_color="#94a3b8"
        )
        self.score_scroll.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))

        nav = ctk.CTkFrame(main, fg_color=COLORS["card_bg"])
        nav.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 20))
        nav.grid_columnconfigure(5, weight=1)

        self.back_btn = ctk.CTkButton(nav, text="Back", command=self._go_back, corner_radius=12, height=40, **SECONDARY_BUTTON_KW)
        self.back_btn.grid(row=0, column=0, padx=(0, 8))

        self.prev_video_btn = ctk.CTkButton(nav, text="← Previous video", command=self.go_to_previous_video, corner_radius=12, height=40, **SECONDARY_BUTTON_KW)
        self.prev_video_btn.grid(row=0, column=1, padx=4)

        self.prev_step_btn = ctk.CTkButton(nav, text="← Previous window", command=self.go_to_previous_step, corner_radius=12, height=40, **SECONDARY_BUTTON_KW)
        self.prev_step_btn.grid(row=0, column=2, padx=4)

        self.replay_btn = ctk.CTkButton(nav, text="↻ Replay", command=self.replay_current_segment, corner_radius=12, height=40, **SECONDARY_BUTTON_KW)
        self.replay_btn.grid(row=0, column=3, padx=4)

        self.copy_prev_btn = ctk.CTkButton(nav, text="Copy previous scores", command=self.copy_previous_segment_scores, corner_radius=12, height=40, **SECONDARY_BUTTON_KW)
        self.copy_prev_btn.grid(row=0, column=4, padx=4)

        self.next_btn = ctk.CTkButton(
            nav,
            text="Next",
            command=self.submit_and_next,
            corner_radius=12,
            height=40,
            font=(FONT_MAIN, 13, "bold"),
            **PRIMARY_BUTTON_KW
        )
        self.next_btn.grid(row=0, column=6, padx=(8, 0), sticky="e")

        self.video_canvas.bind("<Configure>", lambda e: self._rerender_current_frame())

    def _bind_keys(self):
        self.app.bind_all("<KeyPress-n>", lambda e: self.submit_and_next())
        self.app.bind_all("<KeyPress-b>", lambda e: self.go_to_previous_step())
        self.app.bind_all("<KeyPress-r>", lambda e: self.replay_current_segment())
        self.app.bind_all("<KeyPress-c>", lambda e: self.copy_previous_segment_scores())
        self.app.bind_all("<KeyPress-Up>", lambda e: self.move_active_score(-1))
        self.app.bind_all("<KeyPress-Down>", lambda e: self.move_active_score(1))
        self.app.bind_all("<KeyPress-x>", lambda e: self.apply_unscorable_shortcut())
        self.app.bind_all("<KeyPress-X>", lambda e: self.apply_unscorable_shortcut())
        for digit in "01234":
            self.app.bind_all(f"<KeyPress-{digit}>", lambda e, d=int(digit): self.apply_numeric_shortcut(d))

    def set_status(self, text: str):
        self.status_label.configure(text=text)
        self.update_idletasks()

    def show_progress_popup(self, title="Processing..."):
        popup = ctk.CTkToplevel(self)
        popup.title(title)
        popup.geometry("380x130")
        popup.transient(self.app)
        popup.grab_set()
        ctk.CTkLabel(popup, text=title, font=(FONT_MAIN, 14)).pack(pady=(22, 10))
        progress = ctk.CTkProgressBar(popup)
        progress.pack(fill="x", padx=24, pady=10)
        progress.start()
        return popup

    def shutdown(self):
        self._stop_playback()
        self._close_video_session()

    def _go_back(self):
        self.shutdown()
        self.app.show("FileSelectionScreen")

    def _close_video_session(self):
        if self.video_session:
            self.video_session.release()
            self.video_session = None

    def _stop_playback(self):
        self.playing = False
        if self.play_job is not None:
            try:
                self.after_cancel(self.play_job)
            except Exception:
                pass
            self.play_job = None

    def _set_button_state(self, btn, enabled: bool):
        btn.configure(state="normal" if enabled else "disabled")

    def _set_scoring_enabled(self, enabled: bool):
        for group in self.score_groups.values():
            group.set_enabled(enabled)

    def _set_next_enabled(self, enabled: bool):
        self._set_button_state(self.next_btn, enabled)

    def start_session(self, config: SessionConfig, jobs: List[VideoJob]):
        self.config = config
        self.jobs = jobs
        self.current_video_idx = 0
        self.review_existing_video = False
        self.set_status("")
        self._load_video(0)

    def _load_video(self, video_idx: int):
        self._stop_playback()
        self._close_video_session()
        self.set_status("")
        self.current_video_idx = video_idx
        video_path = self.jobs[video_idx].path

        try:
            self.video_session = VideoSession(video_path, self.config)
        except Exception as e:
            messagebox.showerror("Video error", str(e))
            return

        self.rows = self._prepare_rows_for_video(video_path)

        if self.config.score_layout_mode == "whole_body":
            self.current_segment_idx = self._find_first_incomplete_segment_for_all_regions()
            self.current_region_idx = 0
        else:
            self.current_region_idx, self.current_segment_idx = self._find_first_incomplete_region_and_segment()

        self.video_prefix_label.configure(text=f"Video {video_idx + 1}/{len(self.jobs)} - ")
        self.video_name_label.configure(text=os.path.basename(video_path))
        self.subheader.configure(
            text=f"Mode: {'5-second windows' if self.config.scoring_mode == 'window' else 'Full video'} | "
                 f"Scale: 0-{self.config.score_max} | "
                 f"Layout: {'whole body at once' if self.config.score_layout_mode == 'whole_body' else 'one body region at a time'}"
        )

        completed = (
            self.current_segment_idx >= self.video_session.num_segments
            if self.config.score_layout_mode == "whole_body"
            else self.current_region_idx >= len(self.config.selected_regions)
        )

        if completed:
            if messagebox.askyesno("Already completed", "This video already appears fully scored from the existing CSV. Review from the start?"):
                self.review_existing_video = True
                self.current_region_idx = 0
                self.current_segment_idx = 0
            else:
                self._finish_current_video_and_continue(reexport=False)
                return
        else:
            self.review_existing_video = False

        self._build_score_controls()
        self._load_scores_into_controls()
        self._enable_review_if_already_scored()
        self.play_current_segment(first_watch=True)
        self.app.after(100, self.app.focus_force)

    def _prepare_rows_for_video(self, video_path: str) -> List[Dict[str, str]]:
        loaded = CSVStorage.try_load_rows(video_path)
        row_map = {}
        for row in loaded:
            try:
                row_map[int(row.get("segment_index", "-1"))] = row
            except ValueError:
                pass

        rows = []
        for seg_idx in range(self.video_session.num_segments):
            start_s, end_s = self.video_session.get_segment_time_range(seg_idx)
            row = {
                "video_name": os.path.basename(video_path),
                "video_path": video_path,
                "scoring_mode": self.config.scoring_mode,
                "scale_max": str(self.config.score_max),
                "segment_index": str(seg_idx),
                "segment_start_s": f"{start_s:.3f}",
                "segment_end_s": f"{end_s:.3f}",
                "region_mode": self.config.score_layout_mode,
            }
            for region in self.config.selected_regions:
                row[region] = normalize_score_value(row_map.get(seg_idx, {}).get(region, ""))
            rows.append(row)
        return rows

    def _find_first_incomplete_segment_for_all_regions(self) -> int:
        for idx, row in enumerate(self.rows):
            if any(not score_value_is_valid(row.get(region, ""), self.config.score_max) for region in self.config.selected_regions):
                return idx
        return len(self.rows)

    def _find_first_incomplete_region_and_segment(self) -> Tuple[int, int]:
        for region_idx, region in enumerate(self.config.selected_regions):
            for seg_idx, row in enumerate(self.rows):
                if not score_value_is_valid(row.get(region, ""), self.config.score_max):
                    return region_idx, seg_idx
        return len(self.config.selected_regions), 0

    def _clear_score_ui(self):
        for child in self.score_scroll.winfo_children():
            child.destroy()
        self.score_groups.clear()
        self.score_cards.clear()
        self.active_score_index = 0

    def _build_score_controls(self):
        self._clear_score_ui()
        regions = (
            self.config.selected_regions
            if self.config.score_layout_mode == "whole_body"
            else [self.config.selected_regions[self.current_region_idx]]
        )

        for region in regions:
            # Oude scorecard-afmetingen/styling
            cell = ctk.CTkFrame(
                self.score_scroll,
                fg_color=COLORS["card_bg"],
                corner_radius=14,
                border_width=0,
                border_color=COLORS["primary"],
            )
            cell.pack(fill="x", pady=8, padx=4)

            ctk.CTkLabel(
                cell,
                text=REGION_LABELS.get(region, region),
                font=(FONT_MAIN, 13, "bold"),
                text_color=COLORS["text"],
            ).pack(anchor="w", padx=12, pady=(10, 6))

            group = ScoreButtonGroup(
                cell,
                self.config.score_max,
                command=lambda _v: self._on_score_changed(),
            )
            group.pack(anchor="w", padx=12, pady=(0, 12))

            self.score_groups[region] = group
            self.score_cards.append((region, cell))

        self._refresh_region_mode_caption()
        self._update_nav_states()
        self.highlight_active_score_card()

    def highlight_active_score_card(self):
        if self.config is None or not self.score_cards:
            return

        if self.config.score_layout_mode != "whole_body":
            for _, card in self.score_cards:
                card.configure(fg_color=COLORS["card_bg"], border_width=0)
            return

        self.active_score_index = max(0, min(self.active_score_index, len(self.score_cards) - 1))

        for idx, (_, card) in enumerate(self.score_cards):
            if idx == self.active_score_index:
                card.configure(fg_color=COLORS["primary_soft"], border_width=2, border_color=COLORS["primary"])
                self.after(50, lambda c=card: self._scroll_score_card_into_view(c))
            else:
                card.configure(fg_color=COLORS["card_bg"], border_width=0)


    def _scroll_score_card_into_view(self, card):
        try:
            frame = self.score_scroll
            canvas = frame._parent_canvas
            card_y = card.winfo_y()
            card_h = card.winfo_height()
            view_h = canvas.winfo_height()
            current_top = canvas.canvasy(0)
            current_bottom = current_top + view_h
            margin = 18

            if card_y < current_top + margin:
                target = max(card_y - margin, 0)
                canvas.yview_moveto(target / max(frame.winfo_height(), 1))
            elif card_y + card_h > current_bottom - margin:
                target = card_y + card_h - view_h + margin
                canvas.yview_moveto(target / max(frame.winfo_height(), 1))
        except Exception:
            pass

    def _scroll_active_score_into_view(self):
        """Auto-scroll score panel so the active card remains visible."""
        if not self.score_cards:
            return

        try:
            canvas = self.score_scroll._parent_canvas
            scroll_frame = self.score_scroll
            _, active_card = self.score_cards[self.active_score_index]

            self.update_idletasks()

            canvas_height = canvas.winfo_height()
            content_height = max(1, scroll_frame.winfo_height())

            card_top = active_card.winfo_y()
            card_bottom = card_top + active_card.winfo_height()

            view_top = canvas.canvasy(0)
            view_bottom = view_top + canvas_height

            margin = 16
            if card_top < view_top + margin:
                target = max(0, card_top - margin)
                canvas.yview_moveto(target / content_height)
            elif card_bottom > view_bottom - margin:
                target = min(content_height, card_bottom - canvas_height + margin)
                canvas.yview_moveto(target / content_height)
        except Exception:
            pass

    def move_active_score(self, direction: int):
        if self.config is None or self.config.score_layout_mode != "whole_body" or not self.score_cards or not self.first_play_done_for_step:
            return
        self.active_score_index = max(0, min(len(self.score_cards) - 1, self.active_score_index + direction))
        self.highlight_active_score_card()

    def _get_current_active_regions(self) -> List[str]:
        if self.config.score_layout_mode == "whole_body":
            return self.config.selected_regions
        return [self.config.selected_regions[self.current_region_idx]]

    def _refresh_region_mode_caption(self):
        if self.config.score_layout_mode == "whole_body":
            self.region_mode_label.configure(
                text=f"Scoring all {len(self.config.selected_regions)} selected items. "
                     f"↑/↓ navigate • 0–{self.config.score_max} score • X unscorable."
            )
        else:
            region = self.config.selected_regions[self.current_region_idx]
            self.region_mode_label.configure(
                text=f"Current item {self.current_region_idx + 1}/{len(self.config.selected_regions)}: "
                     f"{REGION_LABELS.get(region, region)}. 0–{self.config.score_max} score • X unscorable."
            )

    def _load_scores_into_controls(self):
        self._build_score_controls()

        for group in self.score_groups.values():
            group.clear()

        row = self.rows[self.current_segment_idx]
        for region in self._get_current_active_regions():
            value = normalize_score_value(row.get(region, ""))
            if value != "" and region in self.score_groups:
                self.score_groups[region].set_value_from_storage(value)

        self._refresh_segment_label()
        self._refresh_region_mode_caption()
        self._update_nav_states()

        self.segment_finished = False
        self.first_play_done_for_step = False
        self.current_play_mode = "first_watch"
        self._set_scoring_enabled(False)
        self._set_next_enabled(False)
        self.active_score_index = 0
        self.highlight_active_score_card()

    def _refresh_segment_label(self):
        start_s, end_s = self.video_session.get_segment_time_range(self.current_segment_idx)
        label = "Full video" if self.config.scoring_mode == "full" else "Window"
        self.segment_label.configure(text=f"{label} {self.current_segment_idx + 1}/{self.video_session.num_segments} | {start_s:.1f}s - {end_s:.1f}s")
        self._draw_timeline()

    def _update_nav_states(self):
        self._set_button_state(self.prev_video_btn, self.current_video_idx > 0)

        allow_prev = (
            (self.current_segment_idx > 0 or self.current_video_idx > 0)
            if self.config.score_layout_mode == "whole_body"
            else (self.current_segment_idx > 0 or self.current_region_idx > 0 or self.current_video_idx > 0)
        )
        self._set_button_state(self.prev_step_btn, allow_prev)

        can_copy = self.current_segment_idx > 0 and (self.segment_finished or self.first_play_done_for_step or self._row_scores_complete())
        self._set_button_state(self.copy_prev_btn, can_copy)

    def _on_score_changed(self):
        self._save_current_ui_scores_partial()
        self.first_play_done_for_step = True
        self._set_scoring_enabled(True)
        self._set_next_enabled(self._current_scores_complete())
        self._update_nav_states()
        self.highlight_active_score_card()

    def _save_current_ui_scores_partial(self):
        if self.current_segment_idx >= len(self.rows):
            return
        row = self.rows[self.current_segment_idx]
        for region in self._get_current_active_regions():
            if region in self.score_groups:
                value = self.score_groups[region].get_value()
                if value != "":
                    row[region] = value

    def _current_scores_complete(self) -> bool:
        for region in self._get_current_active_regions():
            if region not in self.score_groups or not self.score_groups[region].is_filled():
                return False
        return True

    def _row_scores_complete(self) -> bool:
        idx = getattr(self, "current_segment_idx", 0)
        if idx >= len(self.rows):
            return False
        row = self.rows[idx]
        for region in self._get_current_active_regions():
            if not score_value_is_valid(row.get(region, ""), self.config.score_max):
                return False
        return True

    def can_edit_scores(self) -> bool:
        return self.first_play_done_for_step or self._current_scores_complete() or self._row_scores_complete() or self.review_existing_video

    def _validate_current_ui(self) -> Tuple[bool, str]:
        for region in self._get_current_active_regions():
            if region not in self.score_groups or not self.score_groups[region].is_filled():
                return False, f"Please assign a score for {REGION_LABELS.get(region, region)} or mark it as unscorable."
        return True, ""

    def copy_previous_segment_scores(self):
        if not (self.segment_finished or self.first_play_done_for_step or self._row_scores_complete()) or self.current_segment_idx <= 0:
            return

        prev_row = self.rows[self.current_segment_idx - 1]
        current_row = self.rows[self.current_segment_idx]
        for region in self._get_current_active_regions():
            current_row[region] = normalize_score_value(prev_row.get(region, ""))

        self._load_scores_into_controls()
        self.first_play_done_for_step = True
        self._set_scoring_enabled(True)
        self._set_next_enabled(self._current_scores_complete())
        self._update_nav_states()

    def _enable_review_if_already_scored(self):
        if self._current_scores_complete() or self._row_scores_complete() or self.review_existing_video:
            self.first_play_done_for_step = True
            self.segment_finished = True
            self._set_scoring_enabled(True)
            self._set_next_enabled(self._current_scores_complete() or self._row_scores_complete())
            self._update_nav_states()
            self.highlight_active_score_card()

    def go_to_previous_step(self):
        self._stop_playback()
        if self.config.score_layout_mode == "whole_body":
            if self.current_segment_idx > 0:
                self.current_segment_idx -= 1
                self._load_scores_into_controls()
                self._enable_review_if_already_scored()
                self.play_current_segment(first_watch=True)
                return
            if self.current_video_idx > 0:
                self.go_to_previous_video()
                return
        else:
            if self.current_segment_idx > 0:
                self.current_segment_idx -= 1
                self._load_scores_into_controls()
                self._enable_review_if_already_scored()
                self.play_current_segment(first_watch=True)
                return
            if self.current_region_idx > 0:
                self.current_region_idx -= 1
                self.current_segment_idx = self.video_session.num_segments - 1
                self._load_scores_into_controls()
                self._enable_review_if_already_scored()
                self.play_current_segment(first_watch=True)
                return
            if self.current_video_idx > 0:
                self.go_to_previous_video()

    def go_to_previous_video(self):
        if self.current_video_idx <= 0:
            return

        self._persist_current_video_csv()
        self._load_video(self.current_video_idx - 1)

        if not self.video_session:
            return

        if self.config.score_layout_mode == "whole_body":
            self.current_segment_idx = max(0, self.video_session.num_segments - 1)
            self.current_region_idx = 0
        else:
            self.current_region_idx = max(0, len(self.config.selected_regions) - 1)
            self.current_segment_idx = max(0, self.video_session.num_segments - 1)

        self._load_scores_into_controls()
        self._enable_review_if_already_scored()
        self.play_current_segment(first_watch=True)

    def apply_numeric_shortcut(self, value: int):
        if self.config is None or value > self.config.score_max or not self.first_play_done_for_step:
            return

        if self.config.score_layout_mode == "region_by_region":
            active = self._get_current_active_regions()
            if active and active[0] in self.score_groups:
                self.score_groups[active[0]].set_value(value, trigger=True)
            return

        if self.config.score_layout_mode == "whole_body":
            if not self.score_cards:
                return
            region = self.score_cards[self.active_score_index][0]
            if region in self.score_groups:
                self.score_groups[region].set_value(value, trigger=True)
                self.move_active_score(1)

    def apply_unscorable_shortcut(self):
        if self.config is None or not self.first_play_done_for_step:
            return

        if self.config.score_layout_mode == "region_by_region":
            active = self._get_current_active_regions()
            if active and active[0] in self.score_groups:
                self.score_groups[active[0]].set_value(UNSCORABLE_VALUE, trigger=True)
            return

        if self.config.score_layout_mode == "whole_body":
            if not self.score_cards:
                return
            region = self.score_cards[self.active_score_index][0]
            if region in self.score_groups:
                self.score_groups[region].set_value(UNSCORABLE_VALUE, trigger=True)
                self.move_active_score(1)

    def _persist_current_video_csv(self):
        if self.current_video_idx < len(self.jobs) and self.config and self.config.save_csv:
            CSVStorage.save_rows(self.jobs[self.current_video_idx].path, self.config, self.rows)

    def submit_and_next(self):
        if self.video_session is None:
            return

        ok, msg = self._validate_current_ui()
        if not ok:
            messagebox.showwarning("Incomplete scores", msg)
            return

        self._save_current_ui_scores_partial()

        if self.config.score_layout_mode == "whole_body":
            if self.current_segment_idx < self.video_session.num_segments - 1:
                self.current_segment_idx += 1
                self._persist_current_video_csv()
                self._load_scores_into_controls()
                self._enable_review_if_already_scored()
                self.play_current_segment(first_watch=True)
                return
            self._persist_current_video_csv()
            self._finish_current_video_and_continue(reexport=True)
            return

        if self.current_segment_idx < self.video_session.num_segments - 1:
            self.current_segment_idx += 1
            self._persist_current_video_csv()
            self._load_scores_into_controls()
            self._enable_review_if_already_scored()
            self.play_current_segment(first_watch=True)
            return

        if self.current_region_idx < len(self.config.selected_regions) - 1:
            self.current_region_idx += 1
            self.current_segment_idx = 0
            self._persist_current_video_csv()
            self._load_scores_into_controls()
            self._enable_review_if_already_scored()
            self.play_current_segment(first_watch=True)
            return

        self._persist_current_video_csv()
        self._finish_current_video_and_continue(reexport=True)

    def _finish_current_video_and_continue(self, reexport: bool):
        if self.current_video_idx >= len(self.jobs):
            return

        video_path = self.jobs[self.current_video_idx].path
        csv_path = None
        out_path = None

        self.set_status("Annotation complete. Preparing output files...")
        self.update()

        if self.config.save_csv:
            self.set_status("Saving CSV score file...")
            self.update()
            csv_path = CSVStorage.save_rows(video_path, self.config, self.rows)

        if self.config.export_mp4 and reexport:
            popup = self.show_progress_popup("Creating annotated MP4... This may take a while")
            self.set_status("Creating annotated MP4 control video...")
            self.update()
            try:
                out_path = VideoExporter.export_with_overlay(video_path, self.config, self.rows)
            finally:
                popup.destroy()

        self.set_status("Finished processing video.")

        msg = f"Finished {os.path.basename(video_path)}"
        if csv_path:
            msg += f"\nCSV saved: {os.path.basename(csv_path)}"
        elif self.config.save_csv:
            msg += "\nCSV save failed or was skipped."

        if out_path:
            msg += f"\nMP4 saved: {os.path.basename(out_path)}"
        elif self.config.export_mp4 and reexport:
            msg += "\nMP4 export failed or was skipped."

        if self.current_video_idx < len(self.jobs) - 1:
            messagebox.showinfo("Video completed", msg)
            self._load_video(self.current_video_idx + 1)
            return

        messagebox.showinfo("Done", msg + "\n\nAll videos processed successfully.")
        self.shutdown()
        self.app.show("FileSelectionScreen")

    def play_current_segment(self, first_watch=True):
        if self.video_session is None:
            return

        self._stop_playback()
        self.segment_finished = False
        self.current_play_mode = "first_watch" if first_watch else "replay"
        self.segment_start_frame, self.segment_end_frame = self.video_session.get_segment_frame_range(self.current_segment_idx)
        self.video_session.seek_to_frame(self.segment_start_frame)
        self.playing = True

        editable = self.can_edit_scores()
        if first_watch and not editable:
            self._set_scoring_enabled(False)
            self._set_next_enabled(False)
        else:
            self._set_scoring_enabled(True)
            self._set_next_enabled(self._current_scores_complete() or self._row_scores_complete())

        delay = max(1, int(round(1000 / self.video_session.fps)))
        self._tick(delay)

    def replay_current_segment(self):
        if self.video_session is None:
            return
        self.first_play_done_for_step = True
        self._set_scoring_enabled(True)
        self._set_next_enabled(self._current_scores_complete() or self._row_scores_complete())
        self.play_current_segment(first_watch=False)

    def _tick(self, delay_ms: int):
        if not self.playing or self.video_session is None:
            return

        current_pos = int(self.video_session.cap.get(cv2.CAP_PROP_POS_FRAMES))
        if current_pos >= self.segment_end_frame:
            self._stop_playback()
            self.segment_finished = True
            if self.current_play_mode == "first_watch":
                self.first_play_done_for_step = True
            self._set_scoring_enabled(True)
            self._set_next_enabled(self._current_scores_complete() or self._row_scores_complete())
            self._update_nav_states()
            self.highlight_active_score_card()
            self._draw_timeline()
            return

        ok, frame = self.video_session.read_frame()
        if not ok:
            self._stop_playback()
            self.segment_finished = True
            if self.current_play_mode == "first_watch":
                self.first_play_done_for_step = True
            self._set_scoring_enabled(True)
            self._set_next_enabled(self._current_scores_complete() or self._row_scores_complete())
            self._update_nav_states()
            self.highlight_active_score_card()
            self._draw_timeline()
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        self.current_pil_frame = self._draw_preview_overlay(pil)
        self._render_pil_to_canvas(self.current_pil_frame)
        self._draw_timeline()
        self.play_job = self.after(delay_ms, lambda: self._tick(delay_ms))

    def _rounded_rect(self, canvas, x1, y1, x2, y2, radius=10, **kwargs):
        radius = max(0, min(radius, abs(x2 - x1) / 2, abs(y2 - y1) / 2))
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return canvas.create_polygon(points, smooth=True, **kwargs)

    def _draw_timeline(self):
        if not hasattr(self, "timeline_canvas") or self.video_session is None:
            return

        c = self.timeline_canvas
        c.delete("all")
        w = max(1, c.winfo_width())
        h = max(1, c.winfo_height())

        left = 16
        right = w - 98
        y = h // 2 + 5
        bar_h = 10

        if right <= left:
            return

        total_frames = max(1, self.video_session.total_frames)
        total_s = total_frames / max(1, self.video_session.fps)

        start_f, end_f = self.video_session.get_segment_frame_range(self.current_segment_idx)
        cur_f = int(self.video_session.cap.get(cv2.CAP_PROP_POS_FRAMES)) if self.video_session.cap is not None else start_f
        cur_f = max(0, min(cur_f, total_frames))

        def x_for_frame(frame_idx):
            return left + (right - left) * frame_idx / total_frames

        self._rounded_rect(
            c,
            left,
            y - bar_h // 2,
            right,
            y + bar_h // 2,
            radius=bar_h // 2,
            fill=COLORS["timeline_track"],
            outline=COLORS["timeline_outline"],
            width=1
        )

        sx = x_for_frame(start_f)
        ex = x_for_frame(end_f)
        self._rounded_rect(
            c,
            sx,
            y - bar_h // 2 - 1,
            ex,
            y + bar_h // 2 + 1,
            radius=bar_h // 2 + 1,
            fill=COLORS["timeline_selected_soft"],
            outline=COLORS["timeline_selected"],
            width=1
        )

        if self.config.scoring_mode == "window":
            for idx in range(self.video_session.num_segments):
                ws, _we = self.video_session.get_segment_frame_range(idx)
                x = x_for_frame(ws)

                self._rounded_rect(
                    c,
                    x - 1.3,
                    y - 10,
                    x + 1.3,
                    y + 10,
                    radius=2,
                    fill=COLORS["timeline_selected"] if idx == self.current_segment_idx else COLORS["timeline_tick"],
                    outline=""
                )

                show_label = (
                    self.video_session.num_segments <= 10
                    or idx == self.current_segment_idx
                    or idx % 5 == 0
                )
                if show_label:
                    c.create_text(
                        x + 4,
                        8,
                        text=f"Window {idx + 1}",
                        anchor="w",
                        fill=COLORS["timeline_label"],
                        font=(FONT_MAIN, 9, "bold")
                    )

        px = x_for_frame(cur_f)
        c.create_oval(px - 7, y - 7, px + 7, y + 7, fill="white", outline=COLORS["timeline_knob"], width=2)
        c.create_oval(px - 4, y - 4, px + 4, y + 4, fill=COLORS["timeline_knob"], outline=COLORS["timeline_knob"])

        c.create_text(
            right + 10,
            y,
            text=f"{cur_f / self.video_session.fps:.1f}s / {total_s:.1f}s",
            anchor="w",
            fill=COLORS["timeline_label"],
            font=(FONT_MAIN, 9, "bold")
        )

    def _draw_preview_overlay(self, img: Image.Image) -> Image.Image:
        row = self.rows[self.current_segment_idx]
        lines = [f"Video {self.current_video_idx + 1}/{len(self.jobs)}", f"Window {self.current_segment_idx + 1}"]
        for region in self._get_current_active_regions():
            value = normalize_score_value(row.get(region, ""))
            if value != "":
                lines.append(f"{REGION_LABELS.get(region, region)}: {value}")
        return PILOverlay.draw_text_block(img, lines, xy=(20, 20), max_lines=10)

    def _render_pil_to_canvas(self, pil_img: Image.Image):
        w = self.video_canvas.winfo_width()
        h = self.video_canvas.winfo_height()
        if w < 2 or h < 2:
            return
        fitted = PILOverlay.fit_to_box(pil_img, w, h)
        self.tk_preview = ImageTk.PhotoImage(fitted)
        self.video_canvas.config(image=self.tk_preview)

    def _rerender_current_frame(self):
        if self.current_pil_frame is not None:
            self._render_pil_to_canvas(self.current_pil_frame)

# ============================================================
# ENTRYPOINT
# ============================================================

def main():
    app = VideoScorerApp()
    app.mainloop()

if __name__ == "__main__":
    main()
