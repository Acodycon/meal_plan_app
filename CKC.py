#Custom Kivy Classes

from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.list import ThreeLineIconListItem, ThreeLineAvatarIconListItem, ThreeLineListItem, IRightBodyTouch
from kivy.properties import NumericProperty, StringProperty, ObjectProperty

from sympy import Rational, pretty



class Custom_MDGridLayout(MDGridLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))

class MDLabelFraction(MDLabel):
    numerator = NumericProperty(0)
    denominator = NumericProperty(0)

    def on_numerator(self, instance, value):
        self.text = pretty(Rational(self.numerator, self.denominator), use_unicode=True)

    def on_denominator(self, instance, value):
        self.text = pretty(Rational(self.numerator, self.denominator), use_unicode=True)

class MDIconButtonSpinner(MDIconButton):
    text = ObjectProperty(None)
    value = ObjectProperty(None)

class ThreeLineIconObjectListItem(ThreeLineIconListItem):
    obj = ObjectProperty(None)
    icon = StringProperty(None)

class ThreeLineAvatarIconObjectListItem(ThreeLineAvatarIconListItem):
    obj = ObjectProperty(None)
    asc_obj_id = NumericProperty(None)
    meal_id = NumericProperty(None)
    ingredient_id = NumericProperty(None)
    ing_unit = StringProperty(None)
    divisible_by = NumericProperty(None)

class Container(IRightBodyTouch, MDBoxLayout):
    adaptive_width = True

class ThreeLineObjectListItem(ThreeLineListItem):
    obj = ObjectProperty(None)

class ThreeLineValueListItem(ThreeLineListItem):
    meal_plan_id = NumericProperty(None)
