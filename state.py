
class State:

    def __init__(self):
        pass

    def update(self, dt):
        pass

    def on_mouse_press(*args, **kwargs):
        pass

    def on_resize(self, width, height):
        pass

    def on_draw(self):
        raise NotImplementedError()

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def on_key_press(self, symbol, modifiers):
        pass

    def on_key_release(self, symbol, modifiers):
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        pass

