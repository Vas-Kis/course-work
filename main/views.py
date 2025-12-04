from django.http import HttpResponse
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from PIL import Image, ImageOps

from .forms import PixelArtForm


def home(request):
    return HttpResponse("<h1>Привіт із Django!</h1><p>Це моя перша сторінка.</p>")


def about(request):
    return HttpResponse("<h1>Про проєкт</h1><p>Це простий офлайн-проєкт для знайомства з Django.</p>")


def hello_template(request):
    context = {
        "name": "Василь",
        "framework": "Django",
    }
    return render(request, "hello.html", context)


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

    if request.method == "POST":
        form = PixelArtForm(request.POST, request.FILES)

        if form.is_valid():
            storage = FileSystemStorage()

            image_file = form.cleaned_data.get("file")
            original_name = form.cleaned_data.get("original_name") or ""

            if image_file:
                original_name = storage.save(image_file.name, image_file)

            if not original_name:
                error_message = "Спочатку завантажте файл."
            else:
                pixels = form.cleaned_data["pixels"]
                scale = form.cleaned_data["scale"]

                # НОВЕ: читаємо чекбокс та режим фільтра
                apply_color = form.cleaned_data.get("apply_color", False)
                color_mode = form.cleaned_data.get("color_mode") or "grayscale"

                original_path = storage.path(original_name)
                file_url = storage.url(original_name)
                current_file = original_name

                img = Image.open(original_path).convert("RGB")

                width, height = img.size
                aspect = height / width if width else 1

                small_width = pixels
                small_height = max(1, int(pixels * aspect))

                out_w = form.cleaned_data.get("output_width")
                out_h = form.cleaned_data.get("output_height")

                # resize ДО пікселізації
                if out_w or out_h:
                    new_w = out_w if out_w else img.width
                    new_h = out_h if out_h else img.height
                    img = img.resize((new_w, new_h), Image.LANCZOS)

                # НОВЕ: застосовуємо фільтр тільки якщо чекбокс увімкнений
                if apply_color:
                    img = apply_color_mode(img, color_mode)

                # далі – усе як раніше
                width, height = img.size
                aspect = height / width if width else 1

                small_width = pixels
                small_height = max(1, int(pixels * aspect))

                small_img = img.resize((small_width, small_height), Image.NEAREST)

                pixel_img = small_img.resize(
                    (small_img.width * scale, small_img.height * scale),
                    Image.NEAREST,
                )

                out_w = form.cleaned_data.get("output_width")
                out_h = form.cleaned_data.get("output_height")

                if (out_w and out_w > 0) or (out_h and out_h > 0):
                    new_w = out_w if out_w and out_w > 0 else pixel_img.width
                    new_h = out_h if out_h and out_h > 0 else pixel_img.height
                    pixel_img = pixel_img.resize((new_w, new_h), Image.NEAREST)

                pixel_name = f"pixel_{original_name}"
                pixel_path = storage.path(pixel_name)
                pixel_img.save(pixel_path, format="PNG")
                pixel_url = storage.url(pixel_name)

                form = PixelArtForm(initial={
                    "pixels": pixels,
                    "scale": scale,
                    "output_width": pixel_img.width,
                    "output_height": pixel_img.height,
                    "keep_aspect": form.cleaned_data.get("keep_aspect", True),
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
    })