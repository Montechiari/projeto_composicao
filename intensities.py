import numpy as np

MIDI2PHON = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
             0.0, 0.0, 0.0, 0.0, 0.013, 0.036, 0.062, 0.087, 0.113, 0.138,
             0.164, 0.19, 0.215, 0.24, 0.265, 0.29, 0.313, 0.336, 0.358,
             0.38, 0.4, 0.42, 0.438, 0.456, 0.474, 0.492, 0.51, 0.528,
             0.545, 0.562, 0.578, 0.595, 0.612, 0.627, 0.642, 0.657,
             0.672, 0.687, 0.702, 0.716, 0.731, 0.745, 0.759, 0.771,
             0.785, 0.797, 0.81, 0.823, 0.835, 0.847, 0.859, 0.871, 0.883,
             0.895, 0.906, 0.916, 0.927, 0.937, 0.946, 0.955, 0.964,
             0.971, 0.979, 0.985, 0.99, 0.995, 0.998, 0.999, 1.0, 0.999,
             0.996, 0.991, 0.986, 0.979, 0.97, 0.961, 0.953, 0.945, 0.941,
             0.942, 0.947, 0.957, 0.971, 0.987, 1.003, 1.02, 1.035, 1.05,
             1.063, 1.074, 1.082, 1.085, 1.082, 1.072, 1.053, 1.029,
             1.004, 0.98, 0.956, 0.933, 0.912, 0.892, 0.872, 0.855, 0.839,
             0.823, 0.809, 0.795, 0.78, 0.766, 0.753, 0.744, 0.738, 0.74,
             0.753]


def get_gesture_component(notes_not_pauses):
    gesture_output = [(np.log1p(nota.duration /
                                notes_not_pauses[i - 1].duration) *
                      MIDI2PHON[nota.pitch])
                      for i, nota in enumerate(notes_not_pauses)]
    gesture_output.insert(0, notes_not_pauses[0].velocity)
    return list(np.interp(gesture_output,
                          (min(gesture_output), max(gesture_output)),
                          (0, 127)))


def get_tempo_at_onsets(notes_not_pauses, tempo_contour):
    tempos = [tempo_contour[int(note.duration * 5)]
              for note in notes_not_pauses]
    return np.interp(tempos, (min(tempos), max(tempos)), (0, 1))


def apply_intensity_formula(notes_not_pauses,
                            gesture_component,
                            tempo_modifier):
    output_array = []
    for i, note in enumerate(notes_not_pauses):
        weight1 = tempo_modifier[i] * 0.25
        weight2 = 1 - weight1
        output_array.append((note.velocity * weight1) +
                            (gesture_component[i] * weight2))
