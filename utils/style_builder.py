"""Style builder utility to generate CSS from config"""
import streamlit as st
from config_loader import load_config


def build_css_from_config():
    """Build complete CSS stylesheet from config"""
    config = load_config()
    
    css_template = config.get("css", {}).get("global", "")
    colors = config.get("ui", {}).get("colors", {})
    typography = config.get("ui", {}).get("typography", {})
    badge = config.get("ui", {}).get("skills_badge", {})
    card = config.get("ui", {}).get("role_card", {})
    phase = config.get("ui", {}).get("phase_card", {})
    
    # Safely format CSS template: escape all literal braces then
    # restore placeholders for keys we intend to format.
    # This allows the CSS to contain normal `{}` blocks without
    # causing format() KeyError for unknown fields.
    if not css_template:
        return ""

    # Escape all braces so literal CSS braces are preserved
    escaped = css_template.replace('{', '{{').replace('}', '}}')

    # Prepare the mapping of available placeholders
    format_map = {
        "primary": colors.get("primary", "#1E3A8A"),
        "secondary": colors.get("secondary", "#0EA5E9"),
        "accent": colors.get("accent", "#10B981"),
        "warning": colors.get("warning", "#F59E0B"),
        "success": colors.get("success", "#10B981"),
        "background": colors.get("background", "#F8FAFC"),
        "card_background": colors.get("card_background", "#FFFFFF"),
        "text_primary": colors.get("text_primary", "#1E293B"),
        "text_secondary": colors.get("text_secondary", "#64748B"),
        "border": colors.get("border", "#E2E8F0"),
        "main_header_size": typography.get("main_header_size", 32),
        "subheader_size": typography.get("subheader_size", 24),
        "section_header_size": typography.get("section_header_size", 20),
        "body_size": typography.get("body_size", 16),
        "badge_bg": badge.get("background_color", "#EFF6FF"),
        "badge_border": badge.get("border_color", "#0EA5E9"),
        "badge_padding": badge.get("padding", 10),
        "badge_padding_x": int(badge.get("padding", 10) * 1.5),
        "badge_radius": badge.get("border_radius", 6),
        "badge_font": badge.get("font_size", 13),
        "role_border_radius": card.get("border_radius", 8),
        "role_padding": card.get("padding", 20),
        "phase_bg": phase.get("background_color", "#F8FAFC"),
        "phase_border_color": phase.get("border_left_color", "#0EA5E9"),
        "phase_border_width": phase.get("border_left_width", 4),
        "phase_padding": phase.get("padding", 16),
        "phase_radius": phase.get("border_radius", 6),
    }

    # Un-escape only the placeholders that we will format
    for key in format_map.keys():
        escaped = escaped.replace('{{' + key + '}}', '{' + key + '}')

    css = escaped.format(**format_map)

    return css


def apply_styles():
    """Apply CSS styles to the page"""
    css = build_css_from_config()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def format_html_template(template_name, **kwargs):
    """Format an HTML template from config with provided values"""
    config = load_config()
    
    html_templates = config.get("html", {})
    template = html_templates.get(template_name, "")
    
    if not template:
        return ""
    
    colors = config.get("ui", {}).get("colors", {})
    typography = config.get("ui", {}).get("typography", {})
    badge = config.get("ui", {}).get("skills_badge", {})
    phase = config.get("ui", {}).get("phase_card", {})
    
    format_params = {
        "primary": colors.get("primary", "#1E3A8A"),
        "secondary": colors.get("secondary", "#0EA5E9"),
        "accent": colors.get("accent", "#10B981"),
        "warning": colors.get("warning", "#F59E0B"),
        "success": colors.get("success", "#10B981"),
        "background": colors.get("background", "#F8FAFC"),
        "card_bg": colors.get("card_background", "#FFFFFF"),
        "text_primary": colors.get("text_primary", "#1E293B"),
        "text_secondary": colors.get("text_secondary", "#64748B"),
        "border": colors.get("border", "#E2E8F0"),
        "main_header_size": typography.get("main_header_size", 32),
        "badge_padding": badge.get("padding", 10),
        "badge_padding_x": badge.get("padding", 10) * 1.5,
        "badge_radius": badge.get("border_radius", 6),
        "badge_font": badge.get("font_size", 13),
        "phase_bg": phase.get("background_color", "#F8FAFC"),
        "phase_border_color": phase.get("border_left_color", "#0EA5E9"),
        "phase_border_width": phase.get("border_left_width", 4),
        "phase_padding": phase.get("padding", 16),
        "phase_radius": phase.get("border_radius", 6),
    }
    
    # Merge user-provided kwargs
    format_params.update(kwargs)

    # Escape all braces in the template, then un-escape only the
    # placeholders we intend to replace. This allows templates to
    # safely include literal `{}` without causing KeyError.
    escaped = template.replace('{', '{{').replace('}', '}}')
    for key in format_params.keys():
        escaped = escaped.replace('{{' + key + '}}', '{' + key + '}')

    return escaped.format(**format_params)


def render_skill_badges(skills, missing=False):
    """Render skill badges from a list of skills"""
    config = load_config()
    colors = config.get("ui", {}).get("colors", {})
    badge = config.get("ui", {}).get("skills_badge", {})
    
    if missing:
        bg_color = "#FEF3C7"
        border_color = colors.get("warning", "#F59E0B")
        text_color = "#92400E"
    else:
        bg_color = badge.get("background_color", "#EFF6FF")
        border_color = badge.get("border_color", "#0EA5E9")
        text_color = colors.get("primary", "#1E3A8A")
    
    badges_html = ""
    for skill in skills:
        badge_html = f"""<span style='display: inline-block; background-color: {bg_color}; border: 1px solid {border_color}; color: {text_color}; padding: {badge.get("padding", 10)}px {badge.get("padding", 10) * 1.5}px; border-radius: {badge.get("border_radius", 6)}px; font-size: {badge.get("font_size", 13)}px; font-weight: 500; margin: 4px;'>{skill}</span>"""
        badges_html += badge_html
    
    return badges_html
