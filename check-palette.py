import sys, os, json

from color import ColorRL
from element import Element
from relative_luminance import *

def check_internal_flicker(elements, result):
    print("\nCHECKING FOR INTERNAL FLICKER...")
    for elem in elements:
        if elem.focus_fill:
            risky, diff, thresh = is_dangerous(elem.initial_fill, elem.focus_fill)
            result["internal_element_flicker"].append({"element": elem.id, "initial_fill_hex": elem.initial_fill.hex, "initial_fill_rl": elem.initial_fill.relative_luminance, "focus_fill_hex": elem.focus_fill.hex, "focus_fill_rl": elem.focus_fill.relative_luminance, "rl_difference": diff, "threshold": thresh, "risk_level": "dangerous" if risky else "safe"})
            if risky:
                print("\tElement \"%s\" has dangerous internal flicker." % (elem.id))
                print("\tConsider using a transition with duration >350ms on this element?")
            else:
                print("\tElement \"%s\" has safe internal flicker." % (elem.id))
            print("\tDifference in luminance (L1 - L2) = %.2f and threshold (0.1 * L1) = %.2f\n" % (diff, thresh))
    return result

def print_adjacent_risk(risk, e1, e2):
    if risk:
        print("\tElements \"%s\" and \"%s\" have dangerous adjacent flicker." % (e1, e2))
    else:
        print("\tElements \"%s\" and \"%s\" have safe adjacent flicker." % (e1, e2))


def check_adjacent_flicker(elements, background, result):
    print("\nCHECKING FOR ADJACENT ELEMENT FLICKER...")
    for e1 in elements:
        if e1.is_background:
            continue

        for e2 in elements:
            if e1.id == e2.id or e2.is_background:
                continue
            initial_r,initial_diff,initial_thresh = is_dangerous(e1.initial_fill, e2.initial_fill)
            summary = {"element1": e1.id, "element2": e2.id, "initial_fill1_hex": e1.initial_fill.hex, "initial_fill1_rl": e1.initial_fill.relative_luminance, "initial_fill2_hex": e2.initial_fill.hex, "initial_fill2_rl": e2.initial_fill.relative_luminance, "rl_difference": initial_diff, "threshold": initial_thresh, "risk_level": "dangerous" if initial_r else "safe"}
            result["adjacent_element_flicker"].append(summary)
            print_adjacent_risk(initial_r, e1.id, e2.id)
            print("\tDifference in luminance (L1 - L2) = %.2f and threshold (0.1 * L1) = %.2f\n" % (initial_diff, initial_thresh))

            if e1.focus_fill:
                e1_focus_risk, e1_focus_diff, e1_focus_thresh = is_dangerous(e1.focus_fill, e2.initial_fill)
                e1_focus_summary = {"element1": e1.id, "element2": e2.id, "focus_fill1_hex": e1.focus_fill.hex, "focus_fill1_rl": e1.focus_fill.relative_luminance, "initial_fill2_hex": e2.initial_fill.hex, "initial_fill2_rl": e2.initial_fill.relative_luminance, "rl_difference": e1_focus_diff, "threshold": e1_focus_thresh, "risk_level": "dangerous" if e1_focus_risk else "safe"}
                result["adjacent_element_flicker"].append(e1_focus_summary)
                print_adjacent_risk(e1_focus_risk, e1.id + " (focus)", e2.id)
                print("\tDifference in luminance (L1 - L2) = %.2f and threshold (0.1 * L1) = %.2f\n" % (e1_focus_risk, e1_focus_diff))

            if e2.focus_fill and not e1.focus_fill:
                e2_focus_risk, e2_focus_diff, e2_focus_thresh = is_dangerous(e1.initial_fill, e2.focus_fill)
                e2_focus_summary = {"element1": e1.id, "element2": e2.id, "initial_fill1_hex": e1.initial_fill.hex, "initial_fill1_rl": e1.initial_fill.relative_luminance, "focus_fill2_hex": e2.focus_fill.hex, "focus_fill2_rl": e2.focus_fill.relative_luminance, "rl_difference": e2_focus_diff, "threshold": e2_focus_thresh, "risk_level": "dangerous" if e2_focus_risk else "safe"}
                result["adjacent_element_flicker"].append(e2_focus_summary)
                print_adjacent_risk(e2_focus_risk, e1.id, e2.id + " (focus)")
                print("\tDifference in luminance (L1 - L2) = %.2f and threshold (0.1 * L1) = %.2f\n" % (e2_focus_risk, e2_focus_diff))

            if e1.focus_fill and e2.focus_fill:
                e1_e2_focus_risk, e1_e2_focus_diff, e1_e2_focus_thresh = is_dangerous(e1.focus_fill, e2.focus_fill)
                e1_e2_focus_summary = {"element1": e1.id, "element2": e2.id, "focus_fill1_hex": e1.focus_fill.hex, "focus_fill1_rl": e1.focus_fill.relative_luminance, "focus_fill2_hex": e2.focus_fill.hex, "focus_fill2_rl": e2.focus_fill.relative_luminance, "rl_difference": e1_e2_focus_diff, "threshold": e1_e2_focus_thresh, "risk_level": "dangerous" if e1_e2_focus_risk else "safe"}
                result["adjacent_element_flicker"].append(e1_e2_focus_summary)
                print_adjacent_risk(e1_e2_focus_risk, e1.id + " (focus)", e2.id + " (focus)")
                print("\tDifference in luminance (L1 - L2) = %.2f and threshold (0.1 * L1) = %.2f\n" % (e1_e2_focus_risk, e1_e2_focus_diff))

        e1_bg_risk, e1_bg_diff, e1_bg_thresh = is_dangerous(e1.initial_fill, background)
        e1_bg_summary = {"element1": e1.id, "element2": "background", "initial_fill_hex": e1.initial_fill.hex, "initial_fill_rl": e1.initial_fill.relative_luminance, "background_hex": background.hex, "background_rl": background.relative_luminance, "rl_difference": e1_bg_diff, "threshold": e1_bg_thresh, "risk_level": "dangerous" if e1_bg_risk else "safe"}
        result["adjacent_element_flicker"].append(e1_bg_summary)
        print_adjacent_risk(e1_bg_risk, e1.id, "background")
        print("\tDifference in luminance (L1 - L2) = %.2f and threshold (0.1 * L1) = %.2f\n" % (e1_bg_risk, e1_bg_diff))

        if e1.focus_fill:
            e1_focus_bg_risk, e1_focus_bg_diff, e1_focus_bg_thresh = is_dangerous(e1.focus_fill, background)
            e1_focus_bg_summary = {"element1": e1.id, "element2": "background", "focus_fill_hex": e1.focus_fill.hex, "focus_fill_rl": e1.focus_fill.relative_luminance, "background_hex": background.hex, "background_rl": background.relative_luminance, "rl_difference": e1_focus_bg_diff, "threshold": e1_focus_bg_thresh, "risk_level": "dangerous" if e1_focus_bg_risk else "safe"}
            result["adjacent_element_flicker"].append(e1_focus_bg_summary)
            print_adjacent_risk(e1_focus_bg_risk, e1.id + " (focus)", "background")
            print("\tDifference in luminance (L1 - L2) = %.2f and threshold (0.1 * L1) = %.2f\n" % (e1_focus_bg_risk, e1_focus_bg_diff))

    return result


def check_contrast(elements, background, result):
    print("\nCHECKING FOR SUFFICIENT CONTRAST...")
    for elem in elements:
        if elem.is_background:
            continue
        print("\n\tExamining element \"%s\"..." % (elem.id))
        if elem.stroke:
            cr1 = contrast_ratio(elem.stroke, background)
            cr2 = contrast_ratio(elem.stroke, elem.initial_fill)
            print("\tContrast ratio between element stroke and background: %.2f (%s)" % (cr1, "sufficient" if cr1 > 3 else "INSUFFICIENT"))
            print("\tContrast ratio between element stroke and initial fill: %.2f (%s)" % (cr2, "sufficient" if cr2 > 3 else "INSUFFICIENT"))
            summary1 = {"element": elem.id, "element_stroke_hex": elem.stroke.hex, "element_stroke_rl": elem.stroke.relative_luminance, "background_hex": background.hex, "background_rl": background.relative_luminance, "contrast-ratio": cr1, "accessibility": "accessible" if cr1 > 3 else "insufficient contrast"}
            result["contrast_ratios"].append(summary1)

            summary2 = {"element": elem.id, "element_stroke_hex": elem.stroke.hex, "element_stroke_rl": elem.stroke.relative_luminance, "initial_fill_hex": elem.initial_fill.hex, "initial_fill_rl": elem.initial_fill.relative_luminance, "contrast-ratio": cr2, "accessibility": "accessible" if cr2 > 3 else "insufficient contrast"}
            result["contrast_ratios"].append(summary2)

            if elem.focus_fill:
                cr3 = contrast_ratio(elem.stroke, elem.focus_fill)
                summary3 = {"element": elem.id, "element_stroke_hex": elem.stroke.hex, "element_stroke_rl": elem.stroke.relative_luminance, "focus_fill_hex": elem.focus_fill.hex, "focus_fill_rl": elem.focus_fill.relative_luminance, "contrast-ratio": cr3, "accessibility": "accessible" if cr3 > 3 else "insufficient contrast"}
                result["contrast_ratios"].append(summary3)
                print("\tContrast ratio between element stroke and focus fill: %.2f (%s)" % (cr3, "sufficient" if cr3 > 3 else "INSUFFICIENT"))
        else:
            cr1 = contrast_ratio(elem.initial_fill, background)
            summary1 = {"element": elem.id, "element_initial_fill_hex": elem.initial_fill.hex, "element_initial_fill_rl": elem.initial_fill.relative_luminance, "background_hex": background.hex, "background_rl": background.relative_luminance, "contrast-ratio": cr1, "accessibility": "accessible" if cr1 > 3 else "insufficient contrast"}
            result["contrast_ratios"].append(summary1)
            print("\tContrast ratio between element initial fill and background: %.2f (%s)" % (cr1, "sufficient" if cr1 > 3 else "INSUFFICIENT"))

            if elem.focus_fill:
                cr2 = contrast_ratio(elem.focus_fill, background)
                summary2 = {"element": elem.id, "element_focus_fill_hex": elem.focus_fill.hex, "element_focus_fill_rl": elem.focus_fill.relative_luminance, "background_hex": background.hex, "background_rl": background.relative_luminance, "contrast-ratio": cr2, "accessibility": "accessible" if cr2 > 3 else "insufficient contrast"}
                result["contrast_ratios"].append(summary2)
                print("\tContrast ratio between element focus fill and background: %.2f (%s)" % (cr2, "sufficient" if cr2 > 3 else "INSUFFICIENT"))
    return result


def contrast_ratio(c1, c2):
    l1 = max(c1.relative_luminance,c2.relative_luminance)
    l2 = min(c1.relative_luminance,c2.relative_luminance)
    return (l1 + 0.05) / (l2 + 0.05)

def is_dangerous(c1, c2):
    l1 = round(max(c1.relative_luminance,c2.relative_luminance),2)
    l2 = round(min(c1.relative_luminance,c2.relative_luminance),2)
    diff = round(l1-l2,2)
    threshold = round(0.1 * l1,2)

    return diff > threshold and l2 < 0.8, diff, threshold

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("USAGE: check-palette.py [input.json] [output.json]")
        sys.exit()

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    colors = []
    elements = []
    background_color = None
    black = ColorRL("000000")

    result = {"internal_element_flicker": [],"adjacent_element_flicker": [], "contrast_ratios": [], }

    with open(input_file, "r") as f:
        color_data = json.load(f)

        background_color = ColorRL(list(filter(lambda elem: (elem["id"] == "background"), color_data["elements"]))[0]["fill-initial"])
        background_color.is_background = True
        # colors.append(background_color)

        for elem in color_data["elements"]:
            element = Element(elem["id"])
            if element.id == "background":
                element.is_background = True
            if elem["fill-initial"] not in colors:
                initial_color = ColorRL(elem["fill-initial"])
                colors.append(initial_color)
                element.initial_fill = initial_color

            if "opacity-initial" in elem.keys():
                element.opacity_initial = float(elem["opacity-initial"])
                blended_hex = element.initial_fill.blend(background_color, element.opacity_initial)
                element.initial_fill = ColorRL(blended_hex)
                colors.append(element.initial_fill)

            if "fill-focus" in elem.keys() and elem["fill-focus"] not in colors and elem["fill-focus"] != "none":
                focus_color = ColorRL(elem["fill-focus"])
                colors.append(focus_color)
                element.focus_fill = focus_color

            if "opacity-focus" in elem.keys() and elem["opacity-focus"] != "none":
                element.opacity_focus = float(elem["opacity-focus"])
                blended_hex = element.initial_fill.blend(background_color,element.opacity_focus)
                blended_color = ColorRL(blended_hex)
                element.focus_fill = blended_color
                colors.append(blended_color)

            if "stroke" in elem.keys() and elem["stroke"] != "none":
                element.stroke = ColorRL(elem["stroke"])
                colors.append(element.stroke)

            if "stroke-darker" in elem.keys():
                darker_k = float(elem["stroke-darker"])
                blended_hex = element.initial_fill.blend(black, 0.7 * darker_k)
                blended_stroke = ColorRL(blended_hex)
                element.stroke = blended_stroke
                colors.append(blended_stroke)

            elements.append(element)

        for e in elements:
            print(e)
        result = check_internal_flicker(elements, result)
        if color_data["check-adjacent"] == "true":
            result["adjacent_element_flicker"] = []
            result = check_adjacent_flicker(elements, background_color, result)
        result = check_contrast(elements, background_color, result)

        with open(output_file, "w") as o:
            json.dump(result, o, indent=4)
