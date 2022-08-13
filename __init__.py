bl_info = {
    "name": "Genshin Addon",
    "author": "M4urlcl0, Zekium, Modder4869, Mken",
    "description": "Easy shading for your Genshin characters",
    "blender": (3, 2, 0),
    "version": (1, 1),
    "location": "3D View > Sidebar",
    "warning": "This addon is still in Development",
    "category": "Lighting",
    "tracker_url": "https://github.com/m4urlclo0/Genshin-Addon/issues",
    "doc_url": "https://github.com/m4urlclo0/Genshin-Addon"
}

from . import ui_panel


def register():
    ui_panel.register()


def unregister():
    ui_panel.unregister()


if __name__ == "__main__":
    register()
