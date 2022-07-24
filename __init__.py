bl_info = {
    "name": "Genshin Addon",
    "author": "M4urlcl0, Zekium, Modder4869",
    "description": "Easy shading for your Genshin characters",
    "blender": (3, 2, 0),
    "location": "3D View > Sidebar",
    "warning": "This addon is still in Development",
    "category": "Lighting"
}

from . import ui_panel


def register():
    ui_panel.register()


def unregister():
    ui_panel.unregister()


if __name__ == "__main__":
    register()
