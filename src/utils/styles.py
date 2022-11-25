import seaborn as sn

custom_palette_cmap = sn.blend_palette(
    colors=[
        (0.737, 0.573, 0.26, 1),
        (0.89, 0.00, 0.102, 1),
        (0.0008, 0.0008, 0.0008, 1),
    ],
    n_colors=100,
    as_cmap=True,
)
custom_palette = sn.blend_palette(
    colors=[
        (0.737, 0.573, 0.26, 1),
        (0.89, 0.00, 0.102, 1),
        (0.0008, 0.0008, 0.0008, 1),
    ],
    n_colors=100,
    as_cmap=False,
)
custom_palette1 = sn.blend_palette(
    colors=[
        (0.945, 0.933, 0.914, 1),
        (0.737, 0.573, 0.26, 1),
        (0.89, 0.00, 0.102, 1),
        (0.0008, 0.0008, 0.0008, 1),
    ],
    n_colors=100,
    as_cmap=False,
)
custom_palette1_inv = sn.blend_palette(
    colors=[
        (0.0008, 0.0008, 0.0008, 1),
        (0.89, 0.00, 0.102, 1),
        (0.737, 0.573, 0.26, 1),
        (0.945, 0.933, 0.914, 1),
    ],
    n_colors=100,
    as_cmap=False,
)
custom_palette_cmap1 = sn.blend_palette(
    colors=[
        (0.945, 0.933, 0.914, 1),
        (0.737, 0.573, 0.26, 1),
        (0.89, 0.00, 0.102, 1),
        (0.0008, 0.0008, 0.0008, 1),
    ],
    n_colors=100,
    as_cmap=True,
)
