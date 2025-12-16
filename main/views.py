from django.http import HttpResponse, FileResponse, Http404
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from PIL import Image, ImageOps
import os

from .forms import PixelArtForm


def home(request):
    return render(request, "home.html")


def apply_color_mode(img, mode: str):
    if mode == "grayscale":
        return img.convert("L").convert("RGB")
    elif mode == "bw":
        gray = img.convert("L")
        bw = gray.point(lambda x: 0 if x < 128 else 255)
        return bw.convert("RGB")
    elif mode == "invert":
        return ImageOps.invert(img)
    elif mode == "retro":
        gray = img.convert("L")
        return ImageOps.colorize(gray, black="#2b1b0f", white="#ffe0a3").convert("RGB")
    else:
        return img


def upload_file(request):
    file_url = None
    pixel_url = None
    error_message = None
    current_file = None
    pixel_download_name = None

    if request.method == "POST":
        form = PixelArtForm(request.POST, request.FILES)

        if form.is_valid():
            storage = FileSystemStorage()

            image_file = form.cleaned_data.get("file")
            original_name = form.cleaned_data.get("original_name") or ""

            if image_file:
                original_name = storage.save(image_file.name, image_file)

            if not original_name or not storage.exists(original_name):
                error_message = "Спочатку завантажте файл."
            else:
                pixels = form.cleaned_data["pixels"]
                scale = form.cleaned_data["scale"]

                resize_enabled = form.cleaned_data.get("resize_enabled", False)
                apply_color = form.cleaned_data.get("apply_color", False)
                color_mode = form.cleaned_data.get("color_mode") or "grayscale"

                original_path = storage.path(original_name)
                file_url = storage.url(original_name)
                current_file = original_name

                img = Image.open(original_path).convert("RGB")

                out_w = form.cleaned_data.get("output_width")
                out_h = form.cleaned_data.get("output_height")

                if resize_enabled and (out_w or out_h):
                    new_w = out_w if out_w else img.width
                    new_h = out_h if out_h else img.height
                    img = img.resize((new_w, new_h), Image.LANCZOS)

                if apply_color:
                    img = apply_color_mode(img, color_mode)

                width, height = img.size
                aspect = height / width if width else 1

                small_width = pixels
                small_height = max(1, int(pixels * aspect))

                small_img = img.resize((small_width, small_height), Image.NEAREST)

                pixel_img = small_img.resize(
                    (small_img.width * scale, small_img.height * scale),
                    Image.NEAREST,
                )

                pixel_name = f"pixel_{original_name}"
                pixel_path = storage.path(pixel_name)
                pixel_img.save(pixel_path, format="PNG")
                pixel_url = storage.url(pixel_name)
                pixel_download_name = pixel_name

                form = PixelArtForm(initial={
                    "pixels": pixels,
                    "scale": scale,
                    "output_width": pixel_img.width,
                    "output_height": pixel_img.height,
                    "keep_aspect": form.cleaned_data.get("keep_aspect", True),
                    "resize_enabled": resize_enabled,
                    "apply_color": apply_color,
                    "color_mode": color_mode,
                    "original_name": original_name,
                })
        else:
            error_message = "Перевірте, будь ласка, введені дані."
    else:
        form = PixelArtForm()

    return render(request, "upload.html", {
        "form": form,
        "file_url": file_url,
        "pixel_url": pixel_url,
        "current_file": current_file,
        "error_message": error_message,
        "pixel_download_name": pixel_download_name,
    })


def download_pixel(request, filename: str):
    storage = FileSystemStorage()
    if not storage.exists(filename):
        raise Http404("Файл не знайдено")

    pixel_path = storage.path(filename)
    return FileResponse(
        open(pixel_path, "rb"),
        as_attachment=True,
        filename=os.path.basename(filename),
    )