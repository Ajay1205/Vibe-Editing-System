"""Word times (take, source s) from the Hindi-mode Whisper pass + the energy envelope, for captions and sound cues."""
K = {
    "being0": (1, 0.45), "teen": (1, 1.50), "uses": (1, 2.28), "trust": (1, 3.30), "simple": (1, 5.44),
    # use 1
    "u1_jab": (2, 2.24), "u1_alag": (2, 3.24), "u1_behave": (2, 3.52), "u1_you": (2, 6.00), "u1_are": (2, 6.12),
    "u1_being": (2, 6.32), "u1_rude": (2, 6.88), "u1_today": (2, 7.10), "u1_matlab": (2, 8.07), "u1_rude2": (2, 9.90),
    # use 2
    "u2_jab": (3, 1.42), "u2_pehchaan": (3, 2.46), "u2_Being": (3, 7.10), "u2_a": (3, 7.24), "u2_teacher": (3, 7.50),
    "u2_I": (3, 8.20), "u2_understand": (3, 8.36), "u2_my": (3, 8.76), "u2_students": (3, 8.98), "u2_very": (3, 9.40),
    "u2_well": (3, 9.84), "u2_iska": (3, 10.54), "u2_teacher2": (3, 11.56),
    # use 3
    "u3_jab": (4, 1.82), "u3_kaam": (4, 2.24), "u3_hone": (4, 2.70), "u3_the": (4, 11.20), "u3_house": (4, 11.40),
    "u3_is": (4, 11.96), "u3_being": (4, 12.34), "u3_painted": (4, 12.86), "u3_iska": (4, 13.78), "u3_ghar": (4, 14.56),
    # recap / cta
    "r_hope": (5, 0.90), "r_being": (5, 2.10), "r_clarity": (5, 4.60),
    "c_confusing": (6, 2.56), "c_comment": (6, 7.82), "c_next": (6, 8.78), "c_expl": (6, 10.68),
}
