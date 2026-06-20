"""FC-Play Terminal UI themes — Swiss Minimalism with OLED Dark aesthetics."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Theme:
    """Visual theme definition for the terminal UI."""

    name: str

    # Core colors
    primary: str
    primary_dim: str
    accent: str
    background: str
    surface: str
    text: str
    text_dim: str
    text_muted: str

    # Semantic colors
    success: str
    warning: str
    error: str
    info: str

    # Special
    border: str
    highlight: str
    link: str

    # Styles
    header_style: str = field(default="bold")
    title_style: str = field(default="bold")

    def __post_init__(self):
        # Derive rich-style formatted strings
        object.__setattr__(self, "primary_fmt", f"bold {self.primary}")
        object.__setattr__(self, "success_fmt", f"bold {self.success}")
        object.__setattr__(self, "error_fmt", f"bold {self.error}")
        object.__setattr__(self, "warning_fmt", f"bold {self.warning}")
        object.__setattr__(self, "info_fmt", f"bold {self.info}")
        object.__setattr__(self, "dim_fmt", f"dim {self.text_muted}")


# ---------------------------------------------------------------------------
# Built-in themes
# ---------------------------------------------------------------------------

MIDNIGHT = Theme(
    name="midnight",
    primary="#6366f1",
    primary_dim="#4f46e5",
    accent="#22c55e",
    background="#0a0a0b",
    surface="#1a1a1e",
    text="#f4f4f5",
    text_dim="#a1a1aa",
    text_muted="#71717a",
    success="#22c55e",
    warning="#f59e0b",
    error="#ef4444",
    info="#3b82f6",
    border="#2a2a2e",
    highlight="#6366f1",
    link="#818cf8",
)

EMERALD = Theme(
    name="emerald",
    primary="#10b981",
    primary_dim="#059669",
    accent="#6366f1",
    background="#0c0c0d",
    surface="#18181b",
    text="#f4f4f5",
    text_dim="#a1a1aa",
    text_muted="#71717a",
    success="#10b981",
    warning="#f59e0b",
    error="#ef4444",
    info="#3b82f6",
    border="#27272a",
    highlight="#10b981",
    link="#34d399",
)

RUBY = Theme(
    name="ruby",
    primary="#e11d48",
    primary_dim="#be123c",
    accent="#f43f5e",
    background="#0a0a0b",
    surface="#1c1917",
    text="#f4f4f5",
    text_dim="#a1a1aa",
    text_muted="#71717a",
    success="#22c55e",
    warning="#f59e0b",
    error="#ef4444",
    info="#3b82f6",
    border="#292524",
    highlight="#e11d48",
    link="#fb7185",
)

# Theme registry
THEMES = {
    "midnight": MIDNIGHT,
    "emerald": EMERALD,
    "ruby": RUBY,
}

DEFAULT_THEME = MIDNIGHT


def get_theme(name: str = "midnight") -> Theme:
    """Get a theme by name, falling back to default."""
    return THEMES.get(name, DEFAULT_THEME)
