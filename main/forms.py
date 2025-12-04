from django import forms


COLOR_CHOICES = [
    ("grayscale", "Відтінки сірого"),
    ("bw", "Чорно-білий"),
    ("invert", "Інверсія"),
    ("retro", "Ретро"),
]


class PixelArtForm(forms.Form):
    file = forms.ImageField(
        label="Оберіть зображення.",
        required=False,
    )

    pixels = forms.IntegerField(
        label="Кількість 'пікселів' по ширині",
        min_value=4,
        max_value=256,
        initial=32,
    )

    scale = forms.IntegerField(
        label="Масштаб збільшення",
        min_value=1,
        max_value=40,
        initial=10,
    )

    output_width = forms.IntegerField(
        label="Ширина результату (px)",
        required=False,
        min_value=1,
        max_value=4000,
    )

    output_height = forms.IntegerField(
        label="Висота результату (px)",
        required=False,
        min_value=1,
        max_value=4000,
    )

    keep_aspect = forms.BooleanField(
        label="Зберігати пропорції",
        required=False,
        initial=True,
    )

    # НОВЕ: чекбокс – чи застосовувати фільтр взагалі
    apply_color = forms.BooleanField(
        label="",
        required=False,
        initial=False,
    )

    # НОВЕ: вибір самого фільтра
    color_mode = forms.ChoiceField(
        label="Кольорова гамма",
        choices=COLOR_CHOICES,
        initial="grayscale",
        required=False,
    )

    original_name = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )
