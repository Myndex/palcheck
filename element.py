
class Element:

    def __init__(self, id):
        self.initial_fill = None
        self.focus_fill = None
        self.opacity_focus = -1
        self.stroke = None
        self.id = id
        self.is_background = False

    def __str__(self):
        return "ID: %s \tInitial fill: %s\t Focus fill: %s\t Stroke: %s" % (self.id,self.initial_fill, self.focus_fill, self.stroke)
