'''SEASON3.SHARPENING / 2.laplacian_sharpen_gaussian.py

Laplacian sharpening with Gaussian pre-blur (Unsharp Masking).

Algorithm:
  mask      = original - GaussianBlur(original)    ← approximates the Laplacian
  sharpened = original + k * mask

The Gaussian blur removes high-frequency noise before we amplify edges,
so this is more robust than pure Laplacian sharpening on noisy images.

Controls:
  k slider         — sharpening aggressiveness (0 = no change, 5 = heavy)
  Blur kernel size — radius of Gaussian smoothing before sharpening
  Sharpen button   — apply and show before / after
  Save button      — write result to output folder
'''

import os
import sys
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import logging

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
_BASE_DIR  = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) \
             else os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(_BASE_DIR, "output", "laplacian_gaussian")
LOG_DIR    = os.path.join(_BASE_DIR, "logs")

CANVAS_W = 700
CANVAS_H = 500

K_MIN     = 0.0
K_MAX     = 5.0
K_DEFAULT = 1.0
K_STEP    = 0.05

BLUR_SIZES = [3, 5, 7, 9]   # must be odd

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=os.path.join(LOG_DIR, "2.laplacian_sharpen_gaussian.log"),
        filemode="w",
    )


# ---------------------------------------------------------------------------
# Sharpening algorithms
# ---------------------------------------------------------------------------
def measure_sharpness(image_bgr: np.ndarray) -> float:
    """Laplacian variance — higher = sharper."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F, ksize=5).var())


def unsharp_mask(image_bgr: np.ndarray, k: float, blur_ksize: int) -> np.ndarray:
    """Unsharp masking: sharpened = image + k * (image - GaussianBlur(image))."""
    ksize = (blur_ksize, blur_ksize)
    blurred = cv2.GaussianBlur(image_bgr, ksize, sigmaX=0)
    mask     = image_bgr.astype(np.float64) - blurred.astype(np.float64)
    sharpened = image_bgr.astype(np.float64) + k * mask
    return np.clip(sharpened, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------------------
# Image helpers
# ---------------------------------------------------------------------------
def scale_image_to_fit(image_bgr: np.ndarray, max_w: int, max_h: int) -> np.ndarray:
    h, w  = image_bgr.shape[:2]
    scale = min(max_w / w, max_h / h, 1.0)
    new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(image_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)


def bgr_to_photoimage(image_bgr: np.ndarray) -> ImageTk.PhotoImage:
    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    return ImageTk.PhotoImage(Image.fromarray(rgb))


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
class GaussianSharpenApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Laplacian Sharpening — Gaussian Unsharp Masking (Season 3)")

        self.image_cv      = None
        self.sharpened_cv  = None
        self.image_path    = ""

        self.k_var          = tk.DoubleVar(value=K_DEFAULT)
        self.blur_ksize_var = tk.IntVar(value=5)

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        self._build_ui()
        logging.info("GaussianSharpenApp started.")

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        self._build_toolbar()
        self._build_canvases()
        self._build_controls()
        self._build_status_bar()

    def _build_toolbar(self):
        bar = tk.Frame(self.root, bg="#333", pady=5)
        bar.pack(fill="x")
        tk.Button(bar, text="Open Image", command=self._open_image,
                  bg="#555", fg="white", padx=10).pack(side="left", padx=10)

    def _build_canvases(self):
        frame = tk.Frame(self.root, bg="#222")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        left = tk.Frame(frame, bg="#222")
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))
        tk.Label(left, text="Original", bg="#222", fg="#aaa",
                 font=("Helvetica", 11, "bold")).pack()
        self.canvas_before = tk.Canvas(left, width=CANVAS_W, height=CANVAS_H,
                                       bg="#111", highlightthickness=0)
        self.canvas_before.pack()
        self.sharpness_label_before = tk.Label(left, text="Sharpness: —",
                                               bg="#222", fg="#7fc")
        self.sharpness_label_before.pack(pady=4)

        right = tk.Frame(frame, bg="#222")
        right.pack(side="left", fill="both", expand=True, padx=(5, 0))
        tk.Label(right, text="Sharpened (Gaussian Unsharp Masking)",
                 bg="#222", fg="#aaa", font=("Helvetica", 11, "bold")).pack()
        self.canvas_after = tk.Canvas(right, width=CANVAS_W, height=CANVAS_H,
                                      bg="#111", highlightthickness=0)
        self.canvas_after.pack()
        self.sharpness_label_after = tk.Label(right, text="Sharpness: —",
                                              bg="#222", fg="#7fc")
        self.sharpness_label_after.pack(pady=4)

    def _build_controls(self):
        ctrl = tk.Frame(self.root, bg="#2a2a2a", pady=8)
        ctrl.pack(fill="x", padx=10, pady=(0, 5))

        # k slider
        tk.Label(ctrl, text="Sharpening strength  k:",
                 bg="#2a2a2a", fg="white").grid(row=0, column=0, padx=10, sticky="w")
        tk.Scale(
            ctrl, from_=K_MIN, to=K_MAX, resolution=K_STEP,
            orient="horizontal", variable=self.k_var, length=250,
            bg="#2a2a2a", fg="white", highlightthickness=0, troughcolor="#555",
        ).grid(row=0, column=1, padx=5)
        tk.Label(ctrl, textvariable=self.k_var, bg="#2a2a2a", fg="#7fc",
                 width=5).grid(row=0, column=2)

        # Blur kernel size radio buttons
        blur_frame = tk.LabelFrame(ctrl, text="Gaussian blur kernel",
                                   bg="#2a2a2a", fg="#aaa", padx=6, pady=4)
        blur_frame.grid(row=0, column=3, padx=15)
        for ksize in BLUR_SIZES:
            tk.Radiobutton(
                blur_frame, text=f"{ksize}×{ksize}",
                variable=self.blur_ksize_var, value=ksize,
                bg="#2a2a2a", fg="white", selectcolor="#444",
                activebackground="#2a2a2a",
            ).pack(side="left", padx=4)

        # Buttons
        btn_frame = tk.Frame(ctrl, bg="#2a2a2a")
        btn_frame.grid(row=0, column=4, padx=20)
        tk.Button(btn_frame, text="Sharpen", command=self._apply_sharpening,
                  bg="#2a7", fg="white", padx=12).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Save Result", command=self._save_result,
                  bg="#27a", fg="white", padx=12).pack(side="left", padx=5)

    def _build_status_bar(self):
        self.status_var = tk.StringVar(value="Open an image to begin.")
        tk.Label(self.root, textvariable=self.status_var, relief="sunken",
                 anchor="w", bg="#1a1a1a", fg="#ccc", padx=8).pack(
            fill="x", side="bottom")

    # ------------------------------------------------------------------
    # Image operations
    # ------------------------------------------------------------------
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
        self.sharpened_cv = None

        self._display_on_canvas(self.canvas_before, image)
        self._clear_canvas(self.canvas_after)
        sharpness = measure_sharpness(image)
        self.sharpness_label_before.config(text=f"Sharpness: {sharpness:.2f}")
        self.sharpness_label_after.config(text="Sharpness: —")
        self.status_var.set(f"Loaded: {os.path.basename(path)}  |  "
                            f"{image.shape[1]}×{image.shape[0]} px")
        logging.info(f"Image loaded: {path}, sharpness={sharpness:.2f}")

    def _apply_sharpening(self):
        if self.image_cv is None:
            messagebox.showerror("Error", "Please open an image first.")
            return

        k      = self.k_var.get()
        ksize  = self.blur_ksize_var.get()
        logging.info(f"Applying unsharp masking: k={k:.2f}, blur_ksize={ksize}")

        self.sharpened_cv = unsharp_mask(self.image_cv, k, ksize)

        self._display_on_canvas(self.canvas_after, self.sharpened_cv)
        sharpness = measure_sharpness(self.sharpened_cv)
        self.sharpness_label_after.config(text=f"Sharpness: {sharpness:.2f}")
        self.status_var.set(
            f"Sharpened — k={k:.2f}, blur {ksize}×{ksize}  |  "
            f"Result sharpness: {sharpness:.2f}"
        )
        logging.info(f"Sharpening done. Result sharpness={sharpness:.2f}")

    def _save_result(self):
        if self.sharpened_cv is None:
            messagebox.showerror("Error", "No sharpened image to save. "
                                         "Click 'Sharpen' first.")
            return

        base   = os.path.splitext(os.path.basename(self.image_path))[0]
        k_str  = f"{self.k_var.get():.2f}".replace(".", "p")
        ksize  = self.blur_ksize_var.get()
        fname  = f"{base}_gaussian_k{k_str}_blur{ksize}.png"
        output_path = os.path.join(OUTPUT_DIR, fname)

        cv2.imwrite(output_path, self.sharpened_cv)
        self.status_var.set(f"Saved: {output_path}")
        logging.info(f"Sharpened image saved to: {output_path}")
        messagebox.showinfo("Saved", f"Image saved to:\n{output_path}")

    # ------------------------------------------------------------------
    # Canvas helpers
    # ------------------------------------------------------------------
    def _display_on_canvas(self, canvas: tk.Canvas, image_bgr: np.ndarray):
        scaled = scale_image_to_fit(image_bgr, CANVAS_W, CANVAS_H)
        photo  = bgr_to_photoimage(scaled)
        canvas.delete("all")
        canvas.create_image(CANVAS_W // 2, CANVAS_H // 2,
                            anchor="center", image=photo)
        canvas.image = photo

    def _clear_canvas(self, canvas: tk.Canvas):
        canvas.delete("all")
        canvas.image = None


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    setup_logging()
    root = tk.Tk()
    root.configure(bg="#222")
    app = GaussianSharpenApp(root)
    root.mainloop()
