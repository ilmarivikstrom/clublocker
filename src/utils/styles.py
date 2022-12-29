import seaborn as sn

custom_palette_3 = sn.blend_palette(
    colors=[
        (0.856, 0.666, 0.299, 1),  # daaa4c
        (0.657, 0.000, 0.235, 1),  # a7003c
        (0.327, 0.000, 0.438, 1),  # 530070
    ],
    n_colors=3,
    as_cmap=False,
)
