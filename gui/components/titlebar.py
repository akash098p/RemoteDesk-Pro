"""
===============================================================================
RemoteDesk Pro
File: gui/components/titlebar.py

Custom title bar for the main application window.
Provides window controls (minimize, maximize, close) and the application title.
===============================================================================
"""

from __future__ import annotations

from typing import Optional

import customtkinter

from core.constants import WINDOW_WIDTH, WINDOW_HEIGHT, PADDING, ICON_SIZE
from core.theme_manager import get_theme_manager
from core.utils import load_image

theme_manager = get_theme_manager()


class TitleBar(customtkinter.CTkFrame):
    """Custom title bar with theme-aware controls."""

    def __init__(
        self,
        master: customtkinter.CTk,
        title: str = "RemoteDesk Pro",
        icon_path: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            master,
            height=46,
            fg_color=theme_manager.get_color("titlebar_bg", "#1E1E1E"),
            corner_radius=0,
            border_width=1,
            border_color=theme_manager.get_color("border", "#333333"),
            **kwargs,
        )
        self._master = master
        self._title = title
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._is_maximized = False
        self._control_icons: dict[str, customtkinter.CTkImage | None] = {}

        self._create_widgets(icon_path)

        self.bind("<ButtonPress-1>", self._on_drag_press)
        self.bind("<B1-Motion>", self._on_drag_motion)
        self.bind("<ButtonRelease-1>", self._on_drag_release)
        self.bind("<Double-Button-1>", self._on_double_click)

        theme_manager.register_theme_change_callback(self._on_theme_change)

    def _create_widgets(self, icon_path: Optional[str]) -> None:
        self.configure(height=46)

        self._icon_label = None
        if icon_path:
            icon = load_image(icon_path, size=(ICON_SIZE, ICON_SIZE))
            if icon:
                self._icon_label = customtkinter.CTkLabel(self, image=icon, text="", anchor="w")
                self._icon_label.pack(side="left", padx=(PADDING, 0))

        self._title_label = customtkinter.CTkLabel(
            self,
            text=self._title,
            font=customtkinter.CTkFont(family="Inter", size=12, weight="bold"),
            text_color=theme_manager.get_color("titlebar_text", "#FFFFFF"),
            anchor="w",
        )
        if self._icon_label:
            self._title_label.pack(side="left", padx=(PADDING, 0), fill="x", expand=True)
        else:
            self._title_label.pack(fill="x", expand=True, padx=PADDING)

        self._create_window_controls()

    def _create_window_controls(self) -> None:
        self._controls_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self._controls_frame.pack(side="right", padx=PADDING)
        self._load_control_icons()

        self._minimize_btn = customtkinter.CTkButton(
            self._controls_frame,
            text="",
            image=self._control_icons.get("minimize"),
            command=self._minimize_window,
            width=34,
            height=32,
            corner_radius=10,
            fg_color=theme_manager.get_color("titlebar_minimize_bg", "#444444"),
            hover_color=theme_manager.get_color("titlebar_control_hover", "#555555"),
            font=customtkinter.CTkFont(size=15, weight="bold"),
            text_color=theme_manager.get_color("titlebar_text", "#FFFFFF"),
        )
        self._minimize_btn.pack(side="left", padx=3)

        self._maximize_btn = customtkinter.CTkButton(
            self._controls_frame,
            text="",
            image=self._control_icons.get("maximize"),
            command=self._toggle_maximize,
            width=34,
            height=32,
            corner_radius=10,
            fg_color=theme_manager.get_color("titlebar_maximize_bg", "#444444"),
            hover_color=theme_manager.get_color("titlebar_control_hover", "#555555"),
            font=customtkinter.CTkFont(size=12, weight="bold"),
            text_color=theme_manager.get_color("titlebar_text", "#FFFFFF"),
        )
        self._maximize_btn.pack(side="left", padx=3)

        self._close_btn = customtkinter.CTkButton(
            self._controls_frame,
            text="",
            image=self._control_icons.get("close"),
            command=self._close_window,
            width=34,
            height=32,
            corner_radius=10,
            fg_color=theme_manager.get_color("titlebar_close_bg", "#F44336"),
            hover_color=theme_manager.get_color("titlebar_close_hover", "#D32F2F"),
            font=customtkinter.CTkFont(size=14, weight="bold"),
            text_color=theme_manager.get_color("titlebar_text", "#FFFFFF"),
        )
        self._close_btn.pack(side="left", padx=3)

    def _load_control_icons(self) -> None:
        self._control_icons["minimize"] = load_image("minimize.png", size=(14, 14))
        self._control_icons["maximize"] = load_image("maximize.png", size=(14, 14))
        self._control_icons["restore"] = load_image("maximize.png", size=(14, 14))
        self._control_icons["close"] = load_image("close.png", size=(14, 14))

    def _on_theme_change(self, theme_name: str) -> None:
        self._load_control_icons()
        self.configure(
            fg_color=theme_manager.get_color("titlebar_bg", "#1E1E1E"),
            border_color=theme_manager.get_color("border", "#333333"),
        )
        self._title_label.configure(text_color=theme_manager.get_color("titlebar_text", "#FFFFFF"))
        self._minimize_btn.configure(
            image=self._control_icons.get("minimize"),
            fg_color=theme_manager.get_color("titlebar_minimize_bg", "#444444"),
            hover_color=theme_manager.get_color("titlebar_control_hover", "#555555"),
            text_color=theme_manager.get_color("titlebar_text", "#FFFFFF"),
        )
        self._maximize_btn.configure(
            image=self._control_icons.get("restore") if self._is_maximized else self._control_icons.get("maximize"),
            fg_color=theme_manager.get_color("titlebar_maximize_bg", "#444444"),
            hover_color=theme_manager.get_color("titlebar_control_hover", "#555555"),
            text_color=theme_manager.get_color("titlebar_text", "#FFFFFF"),
        )
        self._close_btn.configure(
            image=self._control_icons.get("close"),
            fg_color=theme_manager.get_color("titlebar_close_bg", "#F44336"),
            hover_color=theme_manager.get_color("titlebar_close_hover", "#D32F2F"),
            text_color=theme_manager.get_color("titlebar_text", "#FFFFFF"),
        )

    def _minimize_window(self) -> None:
        self._master.iconify()

    def _toggle_maximize(self) -> None:
        if self._is_maximized:
            self._restore_window()
        else:
            self._maximize_window()

    def _maximize_window(self) -> None:
        self._master.state("zoomed")
        self._is_maximized = True
        self._update_maximize_button()

    def _restore_window(self) -> None:
        self._master.state("normal")
        self._is_maximized = False
        self._update_maximize_button()

    def _update_maximize_button(self) -> None:
        self._maximize_btn.configure(
            image=self._control_icons.get("restore") if self._is_maximized else self._control_icons.get("maximize")
        )

    def _close_window(self) -> None:
        self._master.destroy()

    def _on_drag_press(self, event) -> None:
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root

    def _on_drag_motion(self, event) -> None:
        if self._is_maximized:
            return
        dx = event.x_root - self._drag_start_x
        dy = event.y_root - self._drag_start_y
        x = self._master.winfo_x() + dx
        y = self._master.winfo_y() + dy
        self._master.geometry(f"+{x}+{y}")
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root

    def _on_drag_release(self, event) -> None:
        return

    def _on_double_click(self, event) -> None:
        self._toggle_maximize()

    def set_title(self, title: str) -> None:
        self._title = title
        self._title_label.configure(text=title)

    def get_title(self) -> str:
        return self._title

    def destroy(self) -> None:
        theme_manager.unregister_theme_change_callback(self._on_theme_change)
        super().destroy()


def create_titlebar(
    master: customtkinter.CTk,
    title: str = "RemoteDesk Pro",
    icon_path: Optional[str] = None,
) -> TitleBar:
    return TitleBar(master, title=title, icon_path=icon_path)


if __name__ == "__main__":
    demo = customtkinter.CTk()
    demo.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    demo.title("Title Bar Demo")
    demo.configure(fg_color=theme_manager.get_color("background", "#0D0D0D"))
    titlebar = TitleBar(demo, title="RemoteDesk Pro Demo")
    titlebar.pack(fill="x", side="top")
    content = customtkinter.CTkFrame(demo, fg_color=theme_manager.get_color("surface", "#1A1A1A"))
    content.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
    label = customtkinter.CTkLabel(
        content,
        text="Drag the title bar to move the window.\nDouble-click to maximize.\nClick the buttons to test window controls.",
        font=customtkinter.CTkFont(size=14),
        text_color=theme_manager.get_color("text_primary", "#FFFFFF"),
    )
    label.pack(expand=True)
    demo.mainloop()
