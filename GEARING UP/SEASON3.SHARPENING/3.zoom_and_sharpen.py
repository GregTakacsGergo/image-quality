'''SEASON3.SHARPENING / 3.zoom_and_sharpen.py

Spy-movie zoom + sharpen.

Workflow:
  1. Open an image.
  2. Click and drag on the image to select a region — or type coordinates.
  3. Choose a zoom level (continuous slider) or a preset (2×, 4×, 8×).
  4. Choose sharpening mode: pure Laplacian, or Gaussian Unsharp Masking.
  5. Adjust the sharpening strength k.
  6. The zoomed, sharpened crop is shown in the bottom-right preview corner.
  7. Click "Save" to write the result to the output folder.

Layout:
  ┌────────────────────────────────────────────────────┐
  │  [Open]  Mode: ● Basic  ○ Gaussian   k: ──slider──  │
  │  ┌──────────────────────────────────────────────┐  │
  │  │                                              │  │
  │  │        Main canvas (drag to select)          │  │
  │  │                                              │  │
  │  │                       ┌──────────────────┐  │  │
  │  │                       │  Zoom preview    │  │  │
  │  │                       │   (4:3, 320×240) │  │  │
  │  └───────────────────────┴──────────────────┘  │  │
  │  Zoom: ──────slider────  [ 2× ] [ 4× ] [ 8× ] [Free]│
  │  x[__] y[__] w[__] h[__]  [Apply coords]        │
  │  [Save Result]      status bar …                │
  └────────────────────────────────────────────────────┘
'''

import os
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import logging

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SEASON_DIR  = "GEARING UP/SEASON3.SHARPENING"
OUTPUT_DIR  = os.path.join(SEASON_DIR, "output", "zoom_sharpened")
LOG_DIR     = os.path.join(SEASON_DIR, "logs")

CANVAS_W    = 1000
CANVAS_H    = 650

PREVIEW_W   = 320   # 4:3 ratio
PREVIEW_H   = 240
PREVIEW_PAD = 8

ZOOM_MIN     = 1.0
ZOOM_MAX     = 16.0
ZOOM_DEFAULT = 2.0
ZOOM_STEP    = 0.1
ZOOM_PRESETS = [2, 4, 8]  # fixed ratio options

K_MIN     = 0.0
K_MAX     = 5.0
K_DEFAULT = 1.0
K_STEP    = 0.05

BLUR_KSIZE_DEFAULT = 5

RECT_COLOR   = "#00ff88"
RECT_WIDTH   = 2
PREVIEW_BORDER_COLOR = "#00ff88"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=os.path.join(LOG_DIR, "3.zoom_and_sharpen.log"),
        filemode="w",
    )


# ---------------------------------------------------------------------------
# Sharpening algorithms (same as files 1 & 2, self-contained)
# ---------------------------------------------------------------------------
def laplacian_sharpen(image_bgr: np.ndarray, k: float) -> np.ndarray:
    """sharpened = image - k * Laplacian(image)"""
    img_float = image_bgr.astype(np.float64)
    lap = cv2.Laplacian(img_float, cv2.CV_64F, ksize=3)
    sharpened = img_float - k * lap
    return np.clip(sharpened, 0, 255).astype(np.uint8)


def unsharp_mask(image_bgr: np.ndarray, k: float, blur_ksize: int) -> np.ndarray:
    """sharpened = image + k * (image - GaussianBlur(image))"""
    blurred   = cv2.GaussianBlur(image_bgr, (blur_ksize, blur_ksize), sigmaX=0)
    mask      = image_bgr.astype(np.float64) - blurred.astype(np.float64)
    sharpened = image_bgr.astype(np.float64) + k * mask
    return np.clip(sharpened, 0, 255).astype(np.uint8)


def measure_sharpness(image_bgr: np.ndarray) -> float:
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F, ksize=5).var())


# ---------------------------------------------------------------------------
# Image helpers
# ---------------------------------------------------------------------------
def bgr_to_photoimage(image_bgr: np.ndarray) -> ImageTk.PhotoImage:
    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    return ImageTk.PhotoImage(Image.fromarray(rgb))


def scale_to_fit(image_bgr: np.ndarray, max_w: int, max_h: int) -> np.ndarray:
    h, w  = image_bgr.shape[:2]
    if w == 0 or h == 0:
        return image_bgr
    scale = min(max_w / w, max_h / h)
    return cv2.resize(image_bgr, (int(w * scale), int(h * scale)),
                      interpolation=cv2.INTER_AREA)


def center_crop_for_preview(image_bgr: np.ndarray, pw: int, ph: int) -> np.ndarray:
    """Extract a pw×ph center crop from a zoomed image for spy-movie preview.

    - If the zoomed image is larger than the preview box: center-crop exactly pw×ph,
      preserving the zoom magnification rather than shrinking it.
    - If the zoomed image is smaller: pad with black to pw×ph so the preview
      box size stays consistent. The small zoomed image is centered in the box.
    """
    h, w = image_bgr.shape[:2]
    channels = 1 if image_bgr.ndim == 2 else image_bgr.shape[2]

    if w >= pw and h >= ph:
        # Center-crop: take the middle pw×ph pixels
        y0 = (h - ph) // 2
        x0 = (w - pw) // 2
        return image_bgr[y0:y0 + ph, x0:x0 + pw]

    # Image smaller than preview box in at least one dimension — pad with black
    if channels == 1:
        canvas = np.zeros((ph, pw), dtype=image_bgr.dtype)
    else:
        canvas = np.zeros((ph, pw, channels), dtype=image_bgr.dtype)

    y0 = (ph - h) // 2
    x0 = (pw - w) // 2
    # Clamp in case image exceeds preview on one axis but not the other
    crop_h = min(h, ph)
    crop_w = min(w, pw)
    canvas[y0:y0 + crop_h, x0:x0 + crop_w] = image_bgr[:crop_h, :crop_w]
    return canvas


# ---------------------------------------------------------------------------
# Coordinate conversion helpers
# ---------------------------------------------------------------------------
def canvas_to_image_coords(
    cx: int, cy: int,
    offset_x: float, offset_y: float,
    scale: float,
) -> tuple[int, int]:
    """Convert canvas pixel coords to original-image pixel coords."""
    ix = int((cx - offset_x) / scale)
    iy = int((cy - offset_y) / scale)
    return ix, iy


def clamp_selection(
    x: int, y: int, w: int, h: int, img_w: int, img_h: int
) -> tuple[int, int, int, int]:
    x = max(0, min(x, img_w - 1))
    y = max(0, min(y, img_h - 1))
    w = max(1, min(w, img_w - x))
    h = max(1, min(h, img_h - y))
    return x, y, w, h


# ---------------------------------------------------------------------------
# Main Application
# ---------------------------------------------------------------------------
class ZoomSharpenApp:
    """Spy-movie zoom + sharpen application."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Zoom & Sharpen — Season 3")

        # Image state
        self.image_cv      = None   # original BGR
        self.sharpened_cv  = None   # last zoom+sharpen result
        self.image_path    = ""
        self.display_scale = 1.0    # scale from original to canvas display
        self.canvas_offset = (0.0, 0.0)  # (x, y) where image starts on canvas

        # Selection state
        self.selection   = None  # (x, y, w, h) in original-image coords
        self.rect_start  = None  # canvas coords of drag start
        self.rect_id     = None  # canvas rectangle item id

        # Control variables
        self.k_var             = tk.DoubleVar(value=K_DEFAULT)
        self.zoom_slider_var   = tk.DoubleVar(value=ZOOM_DEFAULT)
        self.zoom_preset_var   = tk.StringVar(value="free")
        self.mode_var          = tk.StringVar(value="basic")
        self.blur_ksize_var    = tk.IntVar(value=BLUR_KSIZE_DEFAULT)

        # Manual coordinate entry
        self.coord_x_var = tk.StringVar()
        self.coord_y_var = tk.StringVar()
        self.coord_w_var = tk.StringVar()
        self.coord_h_var = tk.StringVar()

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        self._build_ui()
        logging.info("ZoomSharpenApp started.")

    # -----------------------------------------------------------------------
    # UI construction
    # -----------------------------------------------------------------------
    def _build_ui(self):
        self._build_top_bar()
        self._build_canvas()
        self._build_zoom_controls()
        self._build_coord_bar()
        self._build_bottom_bar()

    def _build_top_bar(self):
        bar = tk.Frame(self.root, bg="#333", pady=6)
        bar.pack(fill="x")

        tk.Button(bar, text="Open Image", command=self._open_image,
                  bg="#555", fg="white", padx=10).pack(side="left", padx=10)

        # Sharpening mode
        mode_frame = tk.LabelFrame(bar, text="Sharpening mode",
                                   bg="#333", fg="#ccc", padx=6)
        mode_frame.pack(side="left", padx=15)
        tk.Radiobutton(mode_frame, text="Basic Laplacian",
                       variable=self.mode_var, value="basic",
                       bg="#333", fg="white", selectcolor="#555",
                       activebackground="#333").pack(side="left")
        tk.Radiobutton(mode_frame, text="Gaussian Unsharp",
                       variable=self.mode_var, value="gaussian",
                       bg="#333", fg="white", selectcolor="#555",
                       activebackground="#333").pack(side="left", padx=8)

        # Blur kernel (only relevant in gaussian mode)
        blur_frame = tk.LabelFrame(bar, text="Blur kernel",
                                   bg="#333", fg="#ccc", padx=4)
        blur_frame.pack(side="left", padx=5)
        for ksize in [3, 5, 7, 9]:
            tk.Radiobutton(blur_frame, text=str(ksize),
                           variable=self.blur_ksize_var, value=ksize,
                           bg="#333", fg="white", selectcolor="#555",
                           activebackground="#333").pack(side="left", padx=3)

        # k slider
        tk.Label(bar, text="  k:", bg="#333", fg="white").pack(side="left")
        tk.Scale(
            bar, from_=K_MIN, to=K_MAX, resolution=K_STEP,
            orient="horizontal", variable=self.k_var, length=200,
            bg="#333", fg="white", highlightthickness=0, troughcolor="#555",
            command=lambda _: self._update_preview(),
        ).pack(side="left", padx=5)
        tk.Label(bar, textvariable=self.k_var, bg="#333",
                 fg="#7fc", width=5).pack(side="left")

    def _build_canvas(self):
        canvas_frame = tk.Frame(self.root, bg="#111")
        canvas_frame.pack(fill="both", expand=True, padx=8, pady=(4, 0))

        self.canvas = tk.Canvas(
            canvas_frame, width=CANVAS_W, height=CANVAS_H,
            bg="#111", cursor="crosshair", highlightthickness=0,
        )
        self.canvas.pack()

        self.canvas.bind("<ButtonPress-1>",   self._on_drag_start)
        self.canvas.bind("<B1-Motion>",        self._on_drag_move)
        self.canvas.bind("<ButtonRelease-1>", self._on_drag_end)

    def _build_zoom_controls(self):
        zoom_bar = tk.Frame(self.root, bg="#2a2a2a", pady=5)
        zoom_bar.pack(fill="x", padx=8)

        tk.Label(zoom_bar, text="Zoom:", bg="#2a2a2a", fg="white").pack(
            side="left", padx=(10, 4))

        self.zoom_slider = tk.Scale(
            zoom_bar, from_=ZOOM_MIN, to=ZOOM_MAX, resolution=ZOOM_STEP,
            orient="horizontal", variable=self.zoom_slider_var, length=280,
            bg="#2a2a2a", fg="white", highlightthickness=0, troughcolor="#555",
            command=lambda _: self._on_zoom_slider_changed(),
        )
        self.zoom_slider.pack(side="left", padx=5)

        self.zoom_value_label = tk.Label(
            zoom_bar, textvariable=self.zoom_slider_var,
            bg="#2a2a2a", fg="#7fc", width=5)
        self.zoom_value_label.pack(side="left")

        tk.Label(zoom_bar, text="×", bg="#2a2a2a", fg="white").pack(side="left")

        # Preset radio buttons
        preset_frame = tk.LabelFrame(zoom_bar, text="Presets",
                                     bg="#2a2a2a", fg="#aaa", padx=4)
        preset_frame.pack(side="left", padx=20)

        tk.Radiobutton(
            preset_frame, text="Free",
            variable=self.zoom_preset_var, value="free",
            command=self._on_preset_changed,
            bg="#2a2a2a", fg="white", selectcolor="#444",
            activebackground="#2a2a2a",
        ).pack(side="left", padx=4)

        for preset in ZOOM_PRESETS:
            tk.Radiobutton(
                preset_frame, text=f"{preset}×",
                variable=self.zoom_preset_var, value=str(preset),
                command=self._on_preset_changed,
                bg="#2a2a2a", fg="white", selectcolor="#444",
                activebackground="#2a2a2a",
            ).pack(side="left", padx=4)

    def _build_coord_bar(self):
        coord_bar = tk.Frame(self.root, bg="#242424", pady=5)
        coord_bar.pack(fill="x", padx=8)

        tk.Label(coord_bar, text="Manual selection:",
                 bg="#242424", fg="#ccc").pack(side="left", padx=(10, 6))

        for label, var in [("x", self.coord_x_var), ("y", self.coord_y_var),
                           ("w", self.coord_w_var), ("h", self.coord_h_var)]:
            tk.Label(coord_bar, text=f"{label}:",
                     bg="#242424", fg="#aaa").pack(side="left")
            tk.Entry(coord_bar, textvariable=var, width=6,
                     bg="#333", fg="white", insertbackground="white").pack(
                side="left", padx=(2, 8))

        tk.Button(coord_bar, text="Apply", command=self._apply_manual_coords,
                  bg="#555", fg="white", padx=8).pack(side="left")

    def _build_bottom_bar(self):
        bottom = tk.Frame(self.root, bg="#2a2a2a", pady=5)
        bottom.pack(fill="x", padx=8, pady=(0, 4))

        tk.Button(bottom, text="Save Result", command=self._save_result,
                  bg="#27a", fg="white", padx=14).pack(side="left", padx=10)

        self.status_var = tk.StringVar(value="Open an image, then drag to select a region.")
        tk.Label(bottom, textvariable=self.status_var, anchor="w",
                 bg="#2a2a2a", fg="#ccc").pack(side="left", padx=10)

    # -----------------------------------------------------------------------
    # Image loading
    # -----------------------------------------------------------------------
    def _open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not path:
            return
        image = cv2.imread(path)
        if image is None:
            messagebox.showerror("Error", "Could not read the image.")
            return

        self.image_path   = path
        self.image_cv     = image
        self.selection    = None
        self.sharpened_cv = None

        self._render_main_image()
        self.status_var.set(
            f"Loaded: {os.path.basename(path)}  |  "
            f"{image.shape[1]}×{image.shape[0]} px  |  "
            "Drag to select a region."
        )
        logging.info(f"Image loaded: {path}")

    # -----------------------------------------------------------------------
    # Canvas rendering
    # -----------------------------------------------------------------------
    def _render_main_image(self):
        """Display the original image on the main canvas, centered."""
        if self.image_cv is None:
            return

        h, w = self.image_cv.shape[:2]
        scale = min(CANVAS_W / w, CANVAS_H / h, 1.0)
        disp_w, disp_h = int(w * scale), int(h * scale)

        self.display_scale  = scale
        offset_x = (CANVAS_W - disp_w) / 2
        offset_y = (CANVAS_H - disp_h) / 2
        self.canvas_offset  = (offset_x, offset_y)

        scaled = cv2.resize(self.image_cv, (disp_w, disp_h),
                            interpolation=cv2.INTER_AREA)
        photo  = bgr_to_photoimage(scaled)
        self.canvas.delete("all")
        self.canvas.create_image(offset_x, offset_y, anchor="nw", image=photo)
        self.canvas.image = photo

    def _render_preview(self, preview_bgr: np.ndarray):
        """Draw the zoom preview in the bottom-right corner of the canvas."""
        photo = bgr_to_photoimage(preview_bgr)
        px = CANVAS_W - PREVIEW_W - PREVIEW_PAD
        py = CANVAS_H - PREVIEW_H - PREVIEW_PAD

        # Remove old preview and border
        self.canvas.delete("preview")

        # Border rectangle
        self.canvas.create_rectangle(
            px - 2, py - 2,
            px + PREVIEW_W + 2, py + PREVIEW_H + 2,
            outline=PREVIEW_BORDER_COLOR, width=2,
            tags="preview",
        )
        # Preview image
        self.canvas.create_image(px, py, anchor="nw", image=photo,
                                 tags="preview")
        self.canvas.preview_image = photo  # prevent GC

    def _draw_selection_rect(self, x0: int, y0: int, x1: int, y1: int):
        """Draw the drag rectangle on the canvas."""
        if self.rect_id is not None:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            x0, y0, x1, y1,
            outline=RECT_COLOR, width=RECT_WIDTH,
        )

    # -----------------------------------------------------------------------
    # Mouse drag — region selection
    # -----------------------------------------------------------------------
    def _on_drag_start(self, event: tk.Event):
        if self.image_cv is None:
            return
        self.rect_start = (event.x, event.y)

    def _on_drag_move(self, event: tk.Event):
        if self.rect_start is None:
            return
        x0, y0 = self.rect_start
        self._draw_selection_rect(x0, y0, event.x, event.y)

    def _on_drag_end(self, event: tk.Event):
        if self.rect_start is None or self.image_cv is None:
            return

        cx0, cy0 = self.rect_start
        cx1, cy1 = event.x, event.y
        self.rect_start = None

        # Normalize (handle right-to-left or bottom-to-top drags)
        cx0, cx1 = min(cx0, cx1), max(cx0, cx1)
        cy0, cy1 = min(cy0, cy1), max(cy0, cy1)

        if cx1 - cx0 < 4 or cy1 - cy0 < 4:
            self.status_var.set("Selection too small — drag a larger area.")
            return

        offset_x, offset_y = self.canvas_offset
        ix0, iy0 = canvas_to_image_coords(cx0, cy0, offset_x, offset_y, self.display_scale)
        ix1, iy1 = canvas_to_image_coords(cx1, cy1, offset_x, offset_y, self.display_scale)

        img_h, img_w = self.image_cv.shape[:2]
        sel = clamp_selection(ix0, iy0, ix1 - ix0, iy1 - iy0, img_w, img_h)
        self.selection = sel
        self._sync_coord_entries(sel)
        self._update_preview()
        logging.info(f"Region selected: x={sel[0]}, y={sel[1]}, w={sel[2]}, h={sel[3]}")

    # -----------------------------------------------------------------------
    # Manual coordinate input
    # -----------------------------------------------------------------------
    def _apply_manual_coords(self):
        if self.image_cv is None:
            messagebox.showerror("Error", "Please open an image first.")
            return
        try:
            x = int(self.coord_x_var.get())
            y = int(self.coord_y_var.get())
            w = int(self.coord_w_var.get())
            h = int(self.coord_h_var.get())
        except ValueError:
            messagebox.showerror("Error",
                                 "Please enter valid integers for x, y, w, h.")
            return

        img_h, img_w = self.image_cv.shape[:2]
        sel = clamp_selection(x, y, w, h, img_w, img_h)
        self.selection = sel
        self._sync_coord_entries(sel)
        self._draw_canvas_selection_from_image_coords(sel)
        self._update_preview()
        logging.info(f"Manual coords applied: {sel}")

    def _sync_coord_entries(self, sel: tuple):
        x, y, w, h = sel
        self.coord_x_var.set(str(x))
        self.coord_y_var.set(str(y))
        self.coord_w_var.set(str(w))
        self.coord_h_var.set(str(h))

    def _draw_canvas_selection_from_image_coords(self, sel: tuple):
        x, y, w, h = sel
        offset_x, offset_y = self.canvas_offset
        s = self.display_scale
        cx0 = int(x * s + offset_x)
        cy0 = int(y * s + offset_y)
        cx1 = int((x + w) * s + offset_x)
        cy1 = int((y + h) * s + offset_y)
        self._draw_selection_rect(cx0, cy0, cx1, cy1)

    # -----------------------------------------------------------------------
    # Zoom preset / slider interaction
    # -----------------------------------------------------------------------
    def _on_preset_changed(self):
        preset = self.zoom_preset_var.get()
        if preset == "free":
            self.zoom_slider.config(state="normal")
        else:
            zoom_val = float(preset)
            self.zoom_slider_var.set(zoom_val)
            self.zoom_slider.config(state="disabled")
        self._update_preview()

    def _on_zoom_slider_changed(self):
        # Slider moved — switch to free mode if preset was active
        if self.zoom_preset_var.get() != "free":
            self.zoom_preset_var.set("free")
            self.zoom_slider.config(state="normal")
        self._update_preview()

    # -----------------------------------------------------------------------
    # Core: compute and display the zoom+sharpen preview
    # -----------------------------------------------------------------------
    def _update_preview(self):
        if self.selection is None or self.image_cv is None:
            return

        crop          = self._crop_selection()
        zoomed        = self._zoom_crop(crop)
        sharpened     = self._sharpen(zoomed)
        self.sharpened_cv = sharpened

        preview = center_crop_for_preview(sharpened, PREVIEW_W, PREVIEW_H)
        self._render_preview(preview)

        sharpness = measure_sharpness(sharpened)
        zoom      = self.zoom_slider_var.get()
        mode      = self.mode_var.get()
        self.status_var.set(
            f"Zoom: {zoom:.1f}×  |  Mode: {mode}  |  "
            f"k={self.k_var.get():.2f}  |  Preview sharpness: {sharpness:.1f}"
        )

    def _crop_selection(self) -> np.ndarray:
        x, y, w, h = self.selection
        return self.image_cv[y: y + h, x: x + w].copy()

    def _zoom_crop(self, crop: np.ndarray) -> np.ndarray:
        """Upscale the crop by the zoom factor using bicubic interpolation."""
        zoom  = self.zoom_slider_var.get()
        h, w  = crop.shape[:2]
        new_w = max(1, int(w * zoom))
        new_h = max(1, int(h * zoom))
        return cv2.resize(crop, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

    def _sharpen(self, image: np.ndarray) -> np.ndarray:
        k    = self.k_var.get()
        mode = self.mode_var.get()
        if mode == "gaussian":
            return unsharp_mask(image, k, self.blur_ksize_var.get())
        return laplacian_sharpen(image, k)

    # -----------------------------------------------------------------------
    # Save result
    # -----------------------------------------------------------------------
    def _save_result(self):
        if self.sharpened_cv is None:
            messagebox.showerror("Error",
                                 "No result to save. Select a region first.")
            return

        base     = os.path.splitext(os.path.basename(self.image_path))[0]
        zoom_str = f"{self.zoom_slider_var.get():.1f}x".replace(".", "p")
        k_str    = f"{self.k_var.get():.2f}".replace(".", "p")
        mode     = self.mode_var.get()
        fname    = f"{base}_zoom{zoom_str}_k{k_str}_{mode}.png"
        path_out = os.path.join(OUTPUT_DIR, fname)

        cv2.imwrite(path_out, self.sharpened_cv)
        self.status_var.set(f"Saved: {path_out}")
        logging.info(f"Result saved: {path_out}")
        messagebox.showinfo("Saved", f"Result saved to:\n{path_out}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    setup_logging()
    root = tk.Tk()
    root.configure(bg="#111")
    app = ZoomSharpenApp(root)
    root.mainloop()
