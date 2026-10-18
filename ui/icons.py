"""Inline SVG icons for HTML components (paths from Lucide, ISC licence).

Streamlit widgets use Material Symbols via `icon=":material/name:"`; these are
for the custom HTML pieces, so both sets share a 1.75px outline style.
"""

_PATHS = {
    "file-text": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/>'
    '<path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/>',
    "sparkles": '<path d="M9.94 15.5A2 2 0 0 0 8.5 14.06l-6.14-1.58a.5.5 0 0 1 0-.96L8.5 9.94A2 2 0 0 0 9.94 8.5l1.58-6.14a.5.5 0 0 1 .96 0l1.58 6.14a2 2 0 0 0 1.44 1.44l6.14 1.58a.5.5 0 0 1 0 .96l-6.14 1.58a2 2 0 0 0-1.44 1.44l-1.58 6.14a.5.5 0 0 1-.96 0z"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
    "check": '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
    "alert": '<circle cx="12" cy="12" r="10"/><path d="M12 8v4"/><path d="M12 16h.01"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "quote": '<path d="M16 3a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2 1 1 0 0 1 1 1v1a2 2 0 0 1-2 2 1 1 0 0 0-1 1v2a1 1 0 0 0 1 1 6 6 0 0 0 6-6V5a2 2 0 0 0-2-2z"/>'
    '<path d="M5 3a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2 1 1 0 0 1 1 1v1a2 2 0 0 1-2 2 1 1 0 0 0-1 1v2a1 1 0 0 0 1 1 6 6 0 0 0 6-6V5a2 2 0 0 0-2-2z"/>',
    "file-search": '<path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M4.27 21a2 2 0 0 0 1.73 1H18a2 2 0 0 0 2-2V7l-5-5H6a2 2 0 0 0-2 2v3"/>'
    '<path d="m9 18-1.5-1.5"/><circle cx="5" cy="14" r="3"/>',
}


def icon(name: str, size: int = 16, cls: str = "") -> str:
    return (
        f'<svg class="dm-icon {cls}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true">{_PATHS[name]}</svg>'
    )


def logo(size: int = 32) -> str:
    """Brand mark: a page with text lines on an indigo tile."""
    return (
        f'<svg class="dm-logo" width="{size}" height="{size}" viewBox="0 0 32 32" fill="none" aria-hidden="true">'
        '<defs><linearGradient id="dm-logo-g" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">'
        '<stop stop-color="#818CF8"/><stop offset="1" stop-color="#6366F1"/></linearGradient></defs>'
        '<rect width="32" height="32" rx="9" fill="url(#dm-logo-g)"/>'
        '<path d="M11 8.5h6.6l4.4 4.4V22.5a1.5 1.5 0 0 1-1.5 1.5h-9.5A1.5 1.5 0 0 1 9.5 22.5V10A1.5 1.5 0 0 1 11 8.5Z" fill="#fff"/>'
        '<path d="M17.5 8.6V13h4.4" stroke="#C7D2FE" stroke-width="1.3" stroke-linejoin="round"/>'
        '<path d="M12.6 16.4h6.2M12.6 19.4h4" stroke="#6366F1" stroke-width="1.5" stroke-linecap="round"/>'
        "</svg>"
    )
