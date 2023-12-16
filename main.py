import kivy
import kivymd

from kivy.config import Config
Config.set("graphics", "width","500")
Config.set("graphics", "height","1000")
from sqlalchemy import func, Table, Column, Integer, ForeignKey, String, CHAR, Float, Boolean, create_engine
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import and_, or_
import random as rd
from calorie_calculator import compute_BMR, compute_TDEE
from CKC import *
from sympy import Rational, pretty



from kivy.lang import Builder
from kivy.app import App
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, ListProperty
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle, SmoothLine
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.widget import MDWidget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.pagelayout import PageLayout
from kivymd.uix.toolbar import MDTopAppBar, MDBottomAppBar
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.uix.navigationdrawer import MDNavigationLayout
from kivymd.uix.list import MDList
from kivymd.uix.list import ThreeLineListItem
from kivymd.uix.list import ThreeLineIconListItem
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.list import IconLeftWidget
from kivymd.uix.list import IconRightWidget
from kivymd.uix.list import OneLineAvatarIconListItem, ThreeLineAvatarIconListItem, IRightBodyTouch
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDIconButton, MDRectangleFlatButton, MDRaisedButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox, MDSwitch
from kivymd.uix.dialog import MDDialog
from kivymd.uix.widget import Widget
from icecream import ic
from kivymd.uix.floatlayout import MDFloatLayout

engine = create_engine('sqlite:///D:\\Coding\\Neuer Ordner\\Meal_Plan\\Data_Base.txt', echo=False) 
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Active(Base):
    __tablename__ = "active"
    id = Column(Integer,primary_key=True)
    name = Column(String)
    meal_plan_id = Column(Integer)

    def __init__(self,name, meal_plan_id):
        self.name = name # is currently the method for searching for the active settings object should be converted to use id instead !!!
        self.meal_plan_id = meal_plan_id

class Meal_Plan(Base):
    __tablename__ = "meal_plan"
    id = Column(Integer,primary_key=True)
    name = Column(String)
    breakfast = Column(Boolean)
    lunch = Column(Boolean)
    dinner = Column(Boolean)
    snack = Column(Boolean)
    day_range = Column(Integer)
    meal_plan_id_list = Column(String)

    def init(self,name,breakfast,lunch,dinner,snack, day_range, meal_plan_id_list):
        self.name = name
        self.breakfast = breakfast
        self.lunch = lunch
        self.dinner = dinner
        self.snack = snack
        self.day_range  = day_range
        self.meal_plan_id_list = meal_plan_id_list

class Settings(Base):
    __tablename__ = "settings"
    id = Column(Integer,primary_key=True)
    name = Column(String)
    gender = Column(String)
    weight = Column(Float)
    height = Column(Float)
    age = Column(Integer)
    activity = Column(String)
    weight_gain_goal = Column(String)
    calories_per_day = Column(Float)

    def __init__(self,name,gender,weight,height,age,activity,weight_gain_goal,calories_per_day):
        self.name = name
        self.gender = gender
        self.weight = weight
        self.height = height
        self.age = age
        self.activity = activity
        self.weight_gain_goal = weight_gain_goal
        self.calories_per_day = calories_per_day

class Association(Base):
    __tablename__ = 'meal_ingredients'
    id = Column(Integer,primary_key=True)
    meal_id = Column(Integer, ForeignKey('meals.id'))
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'))
    amount_numerator = Column(Integer)
    amount_denominator = Column(Integer)
    ingredient = relationship("Ingredient", back_populates="meals")
    meal = relationship("Meal", back_populates="ingredients")

    def __init__(self,meal,ingredient,amount_numerator,amount_denominator):
        self.meal = meal
        self.ingredient = ingredient
        self.amount_numerator = amount_numerator
        self.amount_denominator = amount_denominator

class Meal(Base):
    __tablename__ = 'meals'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    ingredients = relationship("Association", back_populates="meal")
    breakfast = Column(Boolean)
    lunch = Column(Boolean)
    dinner = Column(Boolean)
    snack = Column(Boolean)
    hot_cold = Column(Boolean)
    sweet_savory = Column(Boolean)

    def __init__(self, name, breakfast:bool, lunch:bool, dinner:bool, snack:bool, hot_cold:bool, sweet_savory:bool):
        """
        name : Name of the Meal\n
        Breakfast\n
        Lunch\n
        Dinner\n
        Snack\n
        hot_cold (False/True)\n
        sweet_savory (False/True)
        """
        self.name = name
        self.breakfast = breakfast
        self.lunch = lunch
        self.dinner = dinner
        self.snack = snack
        self.hot_cold = hot_cold
        self.sweet_savory = sweet_savory
     
    def __repr__(self):
        return self.name

    @property
    def calories(self):
        return sum([i.ingredient.calories * i.amount_numerator / i.amount_denominator / 100 if i.ingredient.unit == 'gram' or i.ingredient.unit == 'ml' else i.ingredient.calories * i.amount_numerator / i.amount_denominator for i in self.ingredients])
    @property
    def carbohydrates(self):
        return sum([i.ingredient.carbohydrates * i.amount_numerator / i.amount_denominator / 100 if i.ingredient.unit == 'gram' or i.ingredient.unit == 'ml' else i.ingredient.carbohydrates * i.amount_numerator / i.amount_denominator for i in self.ingredients])
    @property
    def fats(self):
        return sum([i.ingredient.fats * i.amount_numerator / i.amount_denominator / 100 if i.ingredient.unit == 'gram' or i.ingredient.unit == 'ml' else i.ingredient.fats * i.amount_numerator / i.amount_denominator for i in self.ingredients])
    @property
    def proteins(self):
        return sum([i.ingredient.proteins * i.amount_numerator / i.amount_denominator / 100 if i.ingredient.unit == 'gram' or i.ingredient.unit == 'ml' else i.ingredient.proteins * i.amount_numerator / i.amount_denominator for i in self.ingredients])

    def print_recipe(self):
        from fractions import Fraction as F
        if not self.ingredients:
            print(f"{self} has no ingredients yet")
        else:
            print(f"Ingredients for ({self.name}):")
            print()
            Max_Ing_Len = max([len(i.ingredient.name) for i in self.ingredients])                       	                                                                               # Just some lines to format the output
            Max_Amount_Len = max([len(str(i.amount_numerator / i.amount_denominator)) if not i.ingredient.divisible_by else len(str(F(i.amount_numerator / i.amount_denominator).limit_denominator(10).numerator)) + len(str(F(i.amount_numerator / i.amount_denominator).limit_denominator(10).denominator)) + 1 for i in self.ingredients])                        	                                                                               #
            Max_Stat_Len = max([len(str(round(self.calories,2))),len(str(round(self.carbohydrates,2))),len(str(round(self.fats,2))),len(str(round(self.proteins,2)))])             #
            for i in self.ingredients:
                print(f"{i.ingredient.name:<{Max_Ing_Len}} : {i.amount_numerator / i.amount_denominator if not i.ingredient.divisible_by else str(F(i.amount_numerator / i.amount_denominator).limit_denominator(i.ingredient.divisible_by)):<{Max_Amount_Len}} {i.ingredient.unit}")
            print()
            print(f"Total Nutrition Facts:")
            print()
            print(f"Calories      : {round(self.calories,2):<{Max_Stat_Len}} kcal")
            print(f"Carbohydrates : {round(self.carbohydrates,2):<{Max_Stat_Len}} g")
            print(f"Fats          : {round(self.fats,2):<{Max_Stat_Len}} g")
            print(f"Proteins      : {round(self.proteins,2):<{Max_Stat_Len}} g")

class Ingredient(Base):
    """
    name          : str  = Name of the Ingredient\n

    unit          : str  = Unit the Ingredient is measured in g / ml / tsp / or whatever you want\n
    for g and ml Nutrition is per 100 g/ml\n
    for anything else it's per whatever unit\n
    snack         : bool = If it's a snack (True), if it's part of a meal (False)\n
    type          : str  = Options are:\n

    m => Meat\n
    f => Fish\n
    g => Grains (Bread, Pasta)\n
    d => Dairy\n
    v => Vegetable\n
    f => Fruit\n
    n => Nut\n
    o => Oil / Fats (olive oil, butter)\n
    c => Condiment\n
    s => Spice / herb\n
    \n
    calories      : float/int = per 100 g / 100 ml / other unit\n
    carbohydrates : float/int = per 100 g / 100 ml / other unit\n
    fats          : float/int = per 100 g / 100 ml / other unit\n
    proteins      : float/int = per 100 g / 100 ml / other unit\n
    \n
    divisible_by  : Number of piece the Ingredient can be divided in\n
    1 if it is not divisible\n
    2 if it can be halfed etc.\n
    leave blank if it doesn't matter!
    """
    __tablename__ = 'ingredients'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    unit = Column(String)
    snack = Column(Boolean)
    type = Column(String)
    calories = Column(Float)
    carbohydrates = Column(Float)
    fats = Column(Float)
    proteins = Column(Float)
    indivisible = Column(Boolean)
    divisible_by = Column(Integer)
    meals = relationship("Association", back_populates="ingredient")

    def __init__(self, name, unit, snack, type, calories, carbohydrates, fats, proteins, divisible_by):
        self.unit = unit
        self.snack = snack
        self.type = type
        self.name = name
        self.calories = calories
        self.carbohydrates = carbohydrates
        self.fats = fats
        self.proteins = proteins
        self.divisible_by = divisible_by if divisible_by else False
        self.indivisible = True if divisible_by == 1 else False

    def __repr__(self):
        return self.name

class Ingredient_Copy:
    # out of date !!!!
    def __init__(self,Ingredient,amount):
        self.unit = Ingredient.ingredient.unit
        self.snack = Ingredient.ingredient.snack
        self.type = Ingredient.ingredient.type
        self.name = Ingredient.ingredient.name
        self.calories = Ingredient.ingredient.calories
        self.carbohydrates = Ingredient.ingredient.carbohydrates
        self.fats = Ingredient.ingredient.fats
        self.proteins = Ingredient.ingredient.proteins
        self.amount = amount
        self.divisible_by = Ingredient.ingredient.divisible_by
        self.indivisible = Ingredient.ingredient.indivisible

    def __repr__(self):
        if self.indivisible:
            return f"{self.name} : {self.amount}"
        else:
            return f"{self.name} : {self.amount} {self.unit}"

class Meal_Copy:
    # out of date !!!
    def __init__(self,Meal):
        self.name = Meal.name
        self.type = Meal.type
        self.ingredients = [Ingredient_Copy(i,i.amount) for i in Meal.ingredients]
    
    @property
    def calories(self):
        return round(sum([i.calories * i.amount / 100 if not i.indivisible and not i.divisible_by else i.calories * i.amount for i in self.ingredients]),2)
    @property
    def carbohydrates(self):
        return round(sum([i.carbohydrates * i.amount / 100 if not i.indivisible and not i.divisible_by else i.carbohydrates * i.amount for i in self.ingredients]),2)
    @property
    def fats(self):
        return round(sum([i.fats * i.amount / 100 if not i.indivisible and not i.divisible_by else i.fats * i.amount for i in self.ingredients]),2)
    @property
    def proteins(self):
        return round(sum([i.proteins * i.amount / 100 if not i.indivisible and not i.divisible_by else i.proteins * i.amount for i in self.ingredients]),2)
    
    def __repr__(self):
        return f"{self.name} copy"
        
    def print_recipe(self):
        from fractions import Fraction as F
        print(f"Ingredients for ({self.name}):")
        print()
        Max_Ing_Len = max([len(i.name) for i in self.ingredients])                       	                                                                               # Just some lines to format the output
        Max_Amount_Len = max([len(str(i.amount)) for i in self.ingredients])                        	                                                                               #
        Max_Stat_Len = max([len(str(self.calories)),len(str(self.carbohydrates)),len(str(self.fats)),len(str(self.proteins))])             #
        for i in self.ingredients:
            print(f"{i.name:<{Max_Ing_Len}} : {i.amount if not i.divisible_by else str(F(i.amount).limit_denominator(i.divisible_by)):<{Max_Amount_Len}} {i.unit}")
        print()
        print(f"Total Nutrition Facts:")
        print()
        print(f"Calories      : {round(self.calories,2):<{Max_Stat_Len}} kcal")
        print(f"Carbohydrates : {round(self.carbohydrates,2):<{Max_Stat_Len}} g")
        print(f"Fats          : {round(self.fats,2):<{Max_Stat_Len}} g")
        print(f"Proteins      : {round(self.proteins,2):<{Max_Stat_Len}} g")

Base.metadata.create_all(bind=engine)

def generate_Meal_List(Day_range,b,l,d,sn):
    """
    returns a Meal_List\n
    Day_range => Length of the List in Days\n
    b  => Breakfast included Y/N True/False\n
    l  => Lunch included Y/N True/False\n
    d  => Dinner included Y/N True/False\n
    sn => Snack included Y/N True/False
    """
    s = Session()
    Breakfast_id = [i.id for i in s.query(Meal).filter(Meal.type == "Breakfast").all()]
    Lunch_id = [i.id for i in s.query(Meal).filter(Meal.type == "Lunch").all()]
    Dinner_id = [i.id for i in s.query(Meal).filter(Meal.type == "Dinner").all()]
    Snack_id = [i.id for i in s.query(Meal).filter(Meal.type == "Snack").all()]
    Meal_List = list()
    for index, i in enumerate(range(Day_range)):
        Meal_List.append(list())
        if b:
            Meal_List[index].append(Meal_Copy(s.query(Meal).get(rd.choice(Breakfast_id))))
        if l:
            Meal_List[index].append(Meal_Copy(s.query(Meal).get(rd.choice(Lunch_id))))
        if d:
            Meal_List[index].append(Meal_Copy(s.query(Meal).get(rd.choice(Dinner_id))))
        if sn:
            Meal_List[index].append(Meal_Copy(s.query(Meal).get(rd.choice(Snack_id))))
    s.close()
    return Meal_List
# not necessary anymore
def add_meal_to_database(name:str , breakfast:bool, lunch:bool, dinner:bool, snack:bool, hot_cold:bool, sweet_savory:bool):
    """
    name : Name of the Meal\n
    Breakfast\n
    Lunch\n
    Dinner\n
    Snack\n
    hot_cold (True/False)\n
    sweet_savory (True/False)
    """
    s = Session()
    if s.query(Meal).filter(Meal.name == name).first():
        print(f"{name} already exists!")
    else:
        s.add(Meal(name,breakfast, lunch, dinner, snack, hot_cold, sweet_savory))
        s.commit()
    s.close()
# not necessary anymore
def add_ingredient_to_database(name, unit, snack, ing_type, calories, carbohydrates, fats, proteins, divisible_by):
    """
    name          : str  = Name of the Ingredient\n

    unit          : str  = Unit the Ingredient is measured in (g / ml)\n
    /// If measured per piece or spoon etc. put weight in g per piece/spoon\n
    !!! Nutritions also per piece !!!\n
    snack         : bool = If it's a snack (True), if it's part of a meal (False)\n
    type          : str  = Options are:\n

    m => Meat\n
    f => Fish\n
    g => Grains (Bread, Pasta)\n
    d => Dairy\n
    v => Vegetable\n
    f => Fruit\n
    n => Nut\n
    o => Oil / Fats (olive oil, butter)\n
    c => Condiment\n
    s => Spice / herb\n

    calories      : float/int = per 100 g / ml\n
    carbohydrates : float/int = per 100 g / ml\n
    fats          : float/int = per 100 g / ml\n
    proteins      : float/int = per 100 g / ml\n
    \n
    divisible_by  : Number of pieces the Ingredient can be divided in\n
    1 if it is not divisible\n
    2 if it can be halfed etc.\n
    Put None/False if it doesn't matter!
    """
    s = Session()
    ing = s.query(Ingredient).filter(Ingredient.name == name).first()
    if ing:
        ing.name = name
        ing.unit = unit
        ing.snack = snack
        ing.type = ing_type
        ing.calories = calories
        ing.carbohydrates = carbohydrates
        ing.fats = fats
        ing.proteins = proteins
        ing.divisible_by = divisible_by
        s.commit()
        print(f"{name} was updated!")
    else:
        s.add(Ingredient(name, unit, snack, ing_type, calories, carbohydrates, fats, proteins, divisible_by))
        s.commit()
        print(f"{name} was added!")
    s.close()
# not necessary anymore
def add_ingredient_to_meal(meal:str , ingredient:str , amount_numerator:int, amount_denominator:int):
    # out of date
    """
    adds an ingredient and an amount to a meal!\n
    ingredient -> str : Is the ingredient to be added\n
    amount -> int     : Is the amount in g / ml / pieces / spoons\n
    If update is desired put new total amount !!!
    """
    s = Session()
    s.add(Association(
        meal=s.query(Meal).filter(Meal.name == meal).first(),
        ingredient=s.query(Ingredient).filter(Ingredient.name == ingredient).first(),
        amount_numerator=amount_numerator,
        amount_denominator=amount_denominator
        )
    )
    s.commit()
    s.close()

def get_Cals_per_Day(Meal_List:list , n:int):
    """
    returns the sum of the current Calories per Day\n
    Meal_List : List of Days where Days : List of Meals\n
    n : index of day in Meal_List
    """
    # accounts for wether or not the ingredient is indivisible
    return sum([i.calories for i in Meal_List[n]])

def get_percent_factor(Meal_List:list , n:int):
    """
    returns a list of a factor that represents the percent of calories a meal makes up in a day
    """
    # accounts for wether or not the ingredient is indivisible
    return [i.calories / sum([i.calories for i in Meal_List[n]]) for i in Meal_List[n]]

def print_table(table, *args):
    """prints all attributes of all objects in a given table!\n
    table : Name of the Class that generates the table\n
    attribute : Name of the Attribute in string form
    """
    from icecream import ic
    s = Session()
    for i in s.query(table).all():
        ic([getattr(i, j) for j in args])
    s.close()

def Create_Entries():
    # Meats:
    # Loop through each line and replace the first occurrence of double quotes
    add_ingredient_to_database("Hühnchen", "gram" , False, "Meat", 239, 0, 14, 27,False)
    add_ingredient_to_database("Hühnerfleischwurst", "gram", False, "Meat", 211, 1, 17, 13.5,False)
    add_ingredient_to_database("Salami", "gram", False, "Meat", 380, 1, 32, 22,False)
    add_ingredient_to_database("Salami Sticks", "gram", True, "Meat", 507, 1, 41, 33, 10)

    # Fishs:

    # Grains:

    add_ingredient_to_database("Knusper Müsli", "gram", False, "Grains / Bread", 439, 57, 18, 9.5,False)
    add_ingredient_to_database("Nudeln", "gram", False, "Grains / Bread", 359, 71, 2, 13,False)
    add_ingredient_to_database("Sushi-Reis", "gram", False, "Grains / Bread", 354, 80.4, 0.4, 6.7,False)
    add_ingredient_to_database("Wraps", "piece", False, "Grains / Bread", 192, 32.2, 4.5, 5, 1)
    add_ingredient_to_database("Haferdrink", "ml", False, "Grains / Bread", 40, 6, 1.4, 0.6,False)
    # Dairy:

    add_ingredient_to_database("körniger Frischkäse", "gram", False, "Dairy", 97, 3, 4.5, 11,False)
    add_ingredient_to_database("Frischkäse", "gram", False, "Dairy", 201, 3.5, 17, 7.3,False)
    add_ingredient_to_database("Mozarella", "gram", False, "Dairy", 245, 1.5, 18.5, 18,False)
    add_ingredient_to_database("Parmesan", "gram", False, "Dairy", 298, 0, 29, 33,False)
    add_ingredient_to_database("Schafskäse", "gram", False, "Dairy", 256, 1, 20, 18,False)
    add_ingredient_to_database("Gouda", "gram", False, "Dairy", 337, 0.5, 27, 23,False)
    add_ingredient_to_database("Fettarme Milch", "ml", False, "Dairy", 48, 5.1, 1.5, 3.5,False)
    add_ingredient_to_database("Vollmilch", "ml", False, "Dairy", 65, 4.9, 3.5, 3.4,False)
    add_ingredient_to_database("Joghurt", "gram", False, "Dairy", 59, 6.2, 1.5, 5.2,False)
    add_ingredient_to_database("Magerquark", "gram", False, "Dairy", 69, 4, 0.3, 12,False)
    add_ingredient_to_database("Schmelzkäse", "gram", False, "Dairy", 314, 8.5, 23.3, 17.1,False)
    # Vegetables:

    add_ingredient_to_database("Mais","gram", False, "Vegetable",91,15,1.5,2.9,False)
    add_ingredient_to_database("Tomaten-Soße", "gram", False, "Vegetable", 24, 3.6, 0.2, 1.4,False)
    add_ingredient_to_database("Knoblauchzehe", "piece", False, "Vegetable", 4.5, 1, 0, 0.2,1)
    add_ingredient_to_database("Gurke", "gram", False, "Vegetable", 15, 3.6, 0.1, 0.6,False)
    add_ingredient_to_database("Eisbergsalat", "gram", False, "Vegetable", 17, 3.1, 0.3, 1.2,False)
    add_ingredient_to_database("Paprika Gemüse", "gram", False, "Vegetable", 30, 7.5, 0.2, 1,False)
    add_ingredient_to_database("Rukula", "gram", False, "Vegetable", 25, 3.7, 0.7, 2.6,False)
    # Fruits:

    add_ingredient_to_database("Minitomate", "piece", False, "Fruit", 11, 2.4, 0.1, 0.6, 1)
    add_ingredient_to_database("Tomate", "piece", False, "Fruit", 22, 4.8, 0.3, 1.1, 2)
    add_ingredient_to_database("Banane", "piece", False, "Fruit", 105, 27, 0.4, 1.3, 2)
    # Nuts / Seeds:

    add_ingredient_to_database("Haferkochcreme", "ml", False, "Nuts / Seeds", 146, 5.8, 13, 1,False)
    add_ingredient_to_database("Pistazien", "gram", True, "Nuts / Seeds", 582, 12, 47, 24,False)
    add_ingredient_to_database("Sonnenblumenkerne", "gram", False, "Nuts / Seeds", 546, 15.2, 50, 19.3,False)
    # Oils:

    add_ingredient_to_database("Oliven Öl", "ml", False, "Oil / Fats", 823, 0, 91, 0,False)
    # Condiments:

    add_ingredient_to_database("Pesto-Basilikum", "gram", False, "Condiment", 426, 13.3, 40, 2.5,False)
    add_ingredient_to_database("Pesto_Parmesan_Ror", "gram", False, "Condiment", 405, 13.2, 36.5, 5.2,False)
    add_ingredient_to_database("Fleischsalat", "gram", False, "Condiment", 370, 6.3, 35.6, 5.7,False)
    add_ingredient_to_database("Mayonnaise", "gram", False, "Condiment", 660, 0.6, 70, 0.9,False)
    add_ingredient_to_database("Senf", "gram", False, "Condiment", 58, 5.7, 3.2, 3.6,False)
    add_ingredient_to_database("Tomatenmark", "gram", False, "Condiment", 80, 19, 0.5, 4.1,False)
    add_ingredient_to_database("Aceto Balsamico", "ml", False, "Condiment", 245, 55, 0, 1.1,False)
    # Spices:

    add_ingredient_to_database("Vollmilchschokolade", "gram", False, "Spice", 539, 57, 31, 65.,False)
    add_ingredient_to_database("Salz","gram", False, "Spice", 0, 0, 0, 0,False)
    add_ingredient_to_database("Pfeffer", "gram", False, "Spice", 252.2, 65.2, 4.35, 8.7,False)
    add_ingredient_to_database("Basilikum frisch", "gram", False, "Spice", 20, 0, 0, 0,False)
    add_ingredient_to_database("Rosmarin", "gram", False, "Spice", 333.3, 66.6, 16.6, 8.3,False)
    add_ingredient_to_database("Dillspitzen", "gram", False, "Spice", 40, 10, 0, 0,False)
    add_ingredient_to_database("Thymian", "gram", False, "Spice", 278.57, 64.29, 7.14, 7.14,False)
    add_ingredient_to_database("Oregano", "gram", False, "Spice", 270.0, 70.0, 0.0, 10.0,False)
    add_ingredient_to_database("Kakao", "gram", False, "Spice", 357, 86, 3.6, 6,False)
    add_ingredient_to_database("Paprika Gewürz", "gram", False, "Spice", 282.61, 52.17, 8.7, 13.04,False)

    # Meals
    ## Breakfast
    add_meal_to_database("Bananen Joghurt Müsli",True,False,False,False,True,False)

    add_ingredient_to_meal("Bananen Joghurt Müsli","Joghurt", 100,1)
    add_ingredient_to_meal("Bananen Joghurt Müsli","Banane",1,1)
    add_ingredient_to_meal("Bananen Joghurt Müsli","Vollmilchschokolade",20,1)
    add_ingredient_to_meal("Bananen Joghurt Müsli","Kakao",20,1)




    add_meal_to_database("Pistazien",False,False,False,True,True,True)

    add_ingredient_to_meal("Pistazien", "Pistazien", 100,1)



    add_meal_to_database("Salami Sticks",False,False,False,True,True,True)

    add_ingredient_to_meal("Salami Sticks", "Salami Sticks", 100,1)



    ## Dinner
    add_meal_to_database("Nudeln mit Hühnchen in Käsesoße",False,True,True,False,False,True)

    add_ingredient_to_meal("Nudeln mit Hühnchen in Käsesoße","Nudeln", 125,1)

    add_ingredient_to_meal("Nudeln mit Hühnchen in Käsesoße","Hühnchen",150,1)
    add_ingredient_to_meal("Nudeln mit Hühnchen in Käsesoße","Salz",5,1)
    add_ingredient_to_meal("Nudeln mit Hühnchen in Käsesoße","Pfeffer",5,1)
    add_ingredient_to_meal("Nudeln mit Hühnchen in Käsesoße","Paprika Gewürz",1,1)
    add_ingredient_to_meal("Nudeln mit Hühnchen in Käsesoße","Rosmarin",5,1)
    add_ingredient_to_meal("Nudeln mit Hühnchen in Käsesoße","Dillspitzen",5,1)
    add_ingredient_to_meal("Nudeln mit Hühnchen in Käsesoße","Thymian",5,1)
    add_ingredient_to_meal("Nudeln mit Hühnchen in Käsesoße","Oregano",5,1)

    add_ingredient_to_meal("Nudeln mit Hühnchen in Käsesoße","Tomate", 1,1)
    add_ingredient_to_meal("Nudeln mit Hühnchen in Käsesoße","Haferkochcreme", 100,1)
    add_ingredient_to_meal("Nudeln mit Hühnchen in Käsesoße","Schmelzkäse", 25,1)
    add_ingredient_to_meal("Nudeln mit Hühnchen in Käsesoße","Parmesan", 25,1)
    add_ingredient_to_meal("Nudeln mit Hühnchen in Käsesoße","Gouda", 50,1)



    add_meal_to_database("Nudeln mit Pesto (selbstgemacht)",False,True,True,False,False,True)

    add_ingredient_to_meal("Nudeln mit Pesto (selbstgemacht)","Nudeln", 125,1)
    add_ingredient_to_meal("Nudeln mit Pesto (selbstgemacht)","Rukula", 30,1)
    add_ingredient_to_meal("Nudeln mit Pesto (selbstgemacht)","Schafskäse", 75,1)

    add_ingredient_to_meal("Nudeln mit Pesto (selbstgemacht)","Paprika Gemüse", 50,1)
    add_ingredient_to_meal("Nudeln mit Pesto (selbstgemacht)","Knoblauchzehe", 2,1)
    add_ingredient_to_meal("Nudeln mit Pesto (selbstgemacht)","Sonnenblumenkerne", 20,1)
    add_ingredient_to_meal("Nudeln mit Pesto (selbstgemacht)","Parmesan", 20,1)
    add_ingredient_to_meal("Nudeln mit Pesto (selbstgemacht)","Basilikum frisch", 10,1)
    add_ingredient_to_meal("Nudeln mit Pesto (selbstgemacht)","Oliven Öl", 10,1)
    add_ingredient_to_meal("Nudeln mit Pesto (selbstgemacht)","Aceto Balsamico", 10,1)
    add_ingredient_to_meal("Nudeln mit Pesto (selbstgemacht)","Pfeffer", 2,1)
    add_ingredient_to_meal("Nudeln mit Pesto (selbstgemacht)","Salz", 4,1)



    add_meal_to_database("Chicken Wraps",False,True,True,False,False,True)

    add_ingredient_to_meal("Chicken Wraps","Hühnchen",150,1)
    add_ingredient_to_meal("Chicken Wraps","Knoblauchzehe",1,1)
    add_ingredient_to_meal("Chicken Wraps","Salz",5,1)
    add_ingredient_to_meal("Chicken Wraps","Pfeffer",5,1)
    add_ingredient_to_meal("Chicken Wraps","Basilikum frisch",10,1)
    add_ingredient_to_meal("Chicken Wraps","Rosmarin",5,1)
    add_ingredient_to_meal("Chicken Wraps","Dillspitzen",5,1)
    add_ingredient_to_meal("Chicken Wraps","Thymian",5,1)
    add_ingredient_to_meal("Chicken Wraps","Oregano",5,1)
    add_ingredient_to_meal("Chicken Wraps","Gouda",100,1)

    add_ingredient_to_meal("Chicken Wraps","Tomate",1,1)
    add_ingredient_to_meal("Chicken Wraps","Gurke",75,1)
    add_ingredient_to_meal("Chicken Wraps","Eisbergsalat",50,1)
    add_ingredient_to_meal("Chicken Wraps","Mayonnaise",50,1)
    add_ingredient_to_meal("Chicken Wraps","Senf",10,1)
    add_ingredient_to_meal("Chicken Wraps","Tomatenmark",20,1)
    add_ingredient_to_meal("Chicken Wraps","Parmesan",10,1)

    add_ingredient_to_meal("Chicken Wraps","Wraps",2,1)
#Create_Entries()
Calories_Per_Day = 1500

def Adjust_Calories_Per_Day(Meal_List:list , n:int,Calories_Per_Day) -> None:
    """
    Meal_List : List of Days where Days : List of Meals\n
    n         : index of day in Meal_List
    """
    # Out of Date !!!
    # List of calories per ingredient to be added
    # shouldn't change for the whole function call of self !!!
    # Except for indivisible Ingredients

    # User Input
    #ic(Calories_Per_Day)

    # works as intented
    #ic(get_Cals_per_Day(Meal_List,n))

    # works as intented
    # Amount of calories that are too much/little
    Difference = Calories_Per_Day - get_Cals_per_Day(Meal_List,n)

    #ic(Difference)

    # works as intented
    # List of percent of cals each meal makes up for in a day
    Cals_To_Be_Added = [Difference * i for i in get_percent_factor(Meal_List,n)]

    # For loop that adjusts one meal in each cycle
    for index, i in enumerate(Meal_List[n]):
        
        # supports indivisible ingredients
        # List of calories per ingredient in total for a given meal
        Total_Cals_Per_Ingredient = [j.calories * j.amount / 100 if not j.divisible_by else j.calories * j.amount for j in Meal_List[n][index].ingredients]

        # List of the percentage(of calories) each ingredient makes up for in one meal
        Factor_Per_Ingredient = [j / sum(Total_Cals_Per_Ingredient) for j in Total_Cals_Per_Ingredient]
       
        # List of Amount of calories per ingredient that need to be added/subtracted
        Cals_To_Be_Added_Per_Ingredient = [Cals_To_Be_Added[index] * j for j in Factor_Per_Ingredient]

        # Counter from the inner for loop that counts calories added from indivisible ingredients
        Calories_Already_Added_From_Indivisible_Ingredients = 0

        # For loop that handles the indivisible ingredients
        for index2, j in enumerate(Meal_List[n][index].ingredients):
            if j.indivisible:
                if j.calories == 0:
                   continue
                New_Amount = int(Cals_To_Be_Added_Per_Ingredient[index2]/j.calories)
                if New_Amount > 0:
                    Meal_List[n][index].ingredients[index2].amount += New_Amount
                    Calories_Already_Added_From_Indivisible_Ingredients += New_Amount * Meal_List[n][index].ingredients[index2].calories
            elif j.divisible_by:
                from fractions import Fraction as F
                if j.calories == 0:
                    continue
                New_Amount = F(int((Total_Cals_Per_Ingredient[index2] + Cals_To_Be_Added_Per_Ingredient[index2]) / (j.calories / j.divisible_by)),j.divisible_by)
                if float(New_Amount) > 0:
                    Calories_Already_Added_From_Indivisible_Ingredients += New_Amount * j.calories
                    Meal_List[n][index].ingredients[index2].amount = New_Amount
        ## If I move to divisible by the following part should stay the same functionally ##

        # sets the calorie difference to the new value after indivisible ingredients have been handled
        Cals_To_Be_Added[index] -= Calories_Already_Added_From_Indivisible_Ingredients

        # new evaluation after value adjustment
        # indivisible ingredients are ignored (set to 0)
        Total_Cals_Per_Ingredient = [j.calories * j.amount / 100 if not j.divisible_by else 0 for j in Meal_List[n][index].ingredients]
        
        # new evaluation after value adjustment
        # indivisible ingredients are ingnored (set to 0)
        Factor_Per_Ingredient = [j / sum(Total_Cals_Per_Ingredient) for j in Total_Cals_Per_Ingredient]

        # Amount of calories that needs to be added
        # indivisible ingredients are ingnored (set to 0)
        New_Calorie_Amount_Per_Ingredient = [Cals_To_Be_Added[index] * j for j in Factor_Per_Ingredient]
        
        # For loop that handles the remaining divisible ingredients
        for index2, j in enumerate(Meal_List[n][index].ingredients):
            if not j.divisible_by:
                if j.calories == 0:
                    Meal_List[n][index].ingredients[index2].amount *= 1 + Factor_Per_Ingredient[index2]
                else:
                    ###########Ingredient to be changed###########    ##################################Calculates the amount to be added##################################
                    Meal_List[n][index].ingredients[index2].amount += int(New_Calorie_Amount_Per_Ingredient[index2] / Meal_List[n][index].ingredients[index2].calories * 100)

def Adjust_All(Meal_List,Calories_Per_Day): 
    for i in range(len(Meal_List)):
        Adjust_Calories_Per_Day(Meal_List,i,Calories_Per_Day)

class MDLabelNumber(MDLabel):
    number = NumericProperty(0)

    def on_number(self, instance, value):
        self.text = pretty(value, use_unicode=True)

# class MDLabelFraction(MDLabel):
#     numerator = NumericProperty(0)
#     denominator = NumericProperty(0)

#     def on_numerator(self, instance, value):
#         self.text = pretty(Rational(self.numerator, self.denominator), use_unicode=True)

#     def on_denominator(self, instance, value):
#         self.text = pretty(Rational(self.numerator, self.denominator), use_unicode=True)

# class MDIconButtonSpinner(MDIconButton):
#     text = ObjectProperty(None)
#     value = ObjectProperty(None)

# class ThreeLineIconObjectListItem(ThreeLineIconListItem):
#     obj = ObjectProperty(None)
#     icon = StringProperty(None)

# class ThreeLineAvatarIconObjectListItem(ThreeLineAvatarIconListItem):
#     obj = ObjectProperty(None)
#     asc_obj_id = NumericProperty(None)
#     meal_id = NumericProperty(None)
#     ingredient_id = NumericProperty(None)
#     ing_unit = StringProperty(None)
#     divisible_by = NumericProperty(None)

# class Container(IRightBodyTouch, MDBoxLayout):
#     adaptive_width = True

# class ThreeLineObjectListItem(ThreeLineListItem):
#     obj = ObjectProperty(None)

class Main(MDScreen):
    pass

class Settings_Screen(MDScreen):
    def open_gender_dropdown(self):
        self.choices_gender = [
            {
                "viewclass": "OneLineIconListItem",
                "text": "Male",
                "icon": "gender-male",
                "height": dp(56),
                "on_release": lambda x="gender-male",y="Male": self.set_gender_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Female",
                "icon": "gender-female",
                "height": dp(56),
                "on_release": lambda x="gender-female",y="Female": self.set_gender_icon(x,y)
            }
        ]
        self.menu_list_gender = MDDropdownMenu(
            caller=self.ids.gender_input,
            items=self.choices_gender,
            position="auto",
            width_mult=4
        )
        self.menu_list_gender.open()

    def set_gender_icon(self, icon, text):
        self.ids.gender_input.text = text
        self.ids.gender_input.icon = icon
        self.menu_list_gender.dismiss()
        self.display_BMR()
        self.display_TDEE()
        self.display_cals_per_day()
    
    def open_activity_dropdown(self):
        self.choices_activity = [
            {
                "viewclass": "OneLineIconListItem",
                "text": "Sedentary",
                "icon": "cancel",
                "height": dp(56),
                "on_release": lambda x="cancel",y=1: self.set_activity_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Lightly Active",
                "icon": "walk",
                "height": dp(56),
                "on_release": lambda x="walk",y=1.2: self.set_activity_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Moderately Active",
                "icon": "dumbbell",
                "height": dp(56),
                "on_release": lambda x="dumbbell",y=1.375: self.set_activity_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Very Active",
                "icon": "weight-lifter",
                "height": dp(56),
                "on_release": lambda x="weight-lifter",y=1.725: self.set_activity_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Extremely Active",
                "icon": "weight",
                "height": dp(56),
                "on_release": lambda x="weight",y=1.9: self.set_activity_icon(x,y)
            }
        ]
        self.menu_list_activity = MDDropdownMenu(
            caller=self.ids.activity_input,
            items=self.choices_activity,
            position="auto",
            width_mult=4
        )
        self.menu_list_activity.open()
    
    def set_activity_icon(self, icon, text):
        self.ids.activity_input.text = text
        self.ids.activity_input.icon = icon
        self.menu_list_activity.dismiss()
        self.display_BMR()
        self.display_TDEE()
        self.display_cals_per_day()
    
    def open_weightgain_dropdown(self):
        self.choices_weightgain = [
            {
                "viewclass": "OneLineIconListItem",
                "text": "- 1 kg/week",
                "icon": "arrow-down-bold-circle",
                "height": dp(56),
                "on_release": lambda x="arrow-down-bold-circle",y=-1100: self.set_weightgain_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "- 1/2 kg/week",
                "icon": "arrow-down-bold-circle-outline",
                "height": dp(56),
                "on_release": lambda x="arrow-down-bold-circle-outline",y=-550: self.set_weightgain_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "- 1/4 kg/week",
                "icon": "arrow-down-bold-outline",
                "height": dp(56),
                "on_release": lambda x="arrow-down-bold-outline",y=-275: self.set_weightgain_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Maintain",
                "icon": "checkbox-blank-circle-outline",
                "height": dp(56),
                "on_release": lambda x="checkbox-blank-circle-outline",y=0: self.set_weightgain_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "+ 1/4 kg/week",
                "icon": "arrow-up-bold-outline",
                "height": dp(56),
                "on_release": lambda x="arrow-up-bold-outline",y=275: self.set_weightgain_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "+ 1/2 kg/week",
                "icon": "arrow-up-bold-circle-outline",
                "height": dp(56),
                "on_release": lambda x="arrow-up-bold-circle-outline",y=550: self.set_weightgain_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "+ 1 kg/week",
                "icon": "arrow-up-bold-circle",
                "height": dp(56),
                "on_release": lambda x="arrow-up-bold-circle",y=1100: self.set_weightgain_icon(x,y)
            }
        ]
        self.menu_list_weightgain = MDDropdownMenu(
            caller=self.ids.weight_gain_input,
            items=self.choices_weightgain,
            position="auto",
            width_mult=4
        )
        self.menu_list_weightgain.open()
    
    def set_weightgain_icon(self, icon, text):
        self.ids.weight_gain_input.text = text
        self.ids.weight_gain_input.icon = icon
        self.menu_list_weightgain.dismiss()
        self.display_cals_per_day()

    def display_BMR(self):
        gender = self.ids.gender_input.text if self.ids.gender_input.icon != "close" else False
        weight = float(self.ids.weight_input.text) if self.ids.weight_input.text else False
        height = float(self.ids.height_input.text) if self.ids.height_input.text else False
        age  = float(self.ids.age_input.text) if self.ids.age_input.text else False
        ic(gender,weight,height,age)
        if all ([gender,weight,height,age]) and gender != "Choose":
            self.ids.bmr.text = str(round(compute_BMR(gender,weight,height,age),2))
    
    def display_TDEE(self):
        activity = float(self.ids.activity_input.text) if self.ids.activity_input.icon != "close" else False
        BMR = float(self.ids.bmr.text) if self.ids.bmr.text else False
        ic(activity,BMR)
        if all([activity,BMR]) and self.ids.activity_input.icon != "close":
            self.ids.tdee.text = str(round(compute_TDEE(BMR,activity),2))
    
    def display_cals_per_day(self):
        TDEE = float(self.ids.tdee.text) if self.ids.tdee.text else False
        WG = float(self.ids.weight_gain_input.text) if self.ids.weight_gain_input.icon != "close" else False
        ic(TDEE,WG)
        if TDEE and self.ids.weight_gain_input.icon != "close":
            cpd = round(float(TDEE) + float(WG),2)
            ic(cpd)
            self.ids.calories_per_day.text = str(cpd)
    ## no support for multiple settings profiles
    def save_settings(self):
        if all([self.ids.profile_name_input.text,
                self.ids.gender_input.text,
                self.ids.weight_input.text,
                self.ids.height_input.text,
                self.ids.age_input.text,
                self.ids.activity_input.text,
                self.ids.calories_per_day.text]) and self.ids.weight_gain_input.icon != "close":
            s = Session()
            settings_query = s.query(Settings).filter(Settings.name == self.ids.profile_name_input.text).first()
            if not settings_query:
                self.active_settings = Settings(self.ids.profile_name_input.text,
                                        self.ids.gender_input.text,
                                        float(self.ids.weight_input.text),
                                        float(self.ids.height_input.text),
                                        float(self.ids.age_input.text),
                                        float(self.ids.activity_input.text),
                                        float(self.ids.weight_gain_input.text),
                                        float(self.ids.calories_per_day.text))
                
                active_query = s.query(Active).first().name = self.active_settings.name
                s.commit()
                ic(f"added settings for {self.active_settings.name}")
                s.close()
            else:
                s.close()
                c = Settings_Already_Exist_Dialog()
                self.settings_already_exist_dialog = MDDialog(
                    title="Profile already exists, would you like to overwrite?",
                    type="custom",
                    content_cls=c,
                    radius=[20, 7, 20, 7]
                )
                c.settings_already_exist_dialog = self.settings_already_exist_dialog
                c.settings_screen = self
                self.settings_already_exist_dialog.open()
        else:
            ic("Please fill out all fields")
    
    def update_settings(self): # is expected to only be called from save settings function with all fields filled
        s = Session()
        settings_query = s.query(Settings).filter(Settings.name == self.active_settings.name).first()
        self.active_settings = Settings(self.ids.profile_name_input.text,
                                        self.ids.gender_input.text,
                                        float(self.ids.weight_input.text),
                                        float(self.ids.height_input.text),
                                        float(self.ids.age_input.text),
                                        float(self.ids.activity_input.text),
                                        float(self.ids.weight_gain_input.text),
                                        float(self.ids.calories_per_day.text))
        settings_query.gender = self.active_settings.gender
        settings_query.weight = self.active_settings.weight
        settings_query.height = self.active_settings.height
        settings_query.age = self.active_settings.age
        settings_query.activity = self.active_settings.activity
        settings_query.weight_gain_goal = self.active_settings.weight_gain_goal
        settings_query.calories_per_day = self.active_settings.calories_per_day
        ic(f"updated settings for {self.active_settings.name}")
        s.commit()
        s.close()

    def load_active_settings(self):
        icon_dict = {
            "Male":"gender-male",
            "Female":"gender-female",
            "1.0":"cancel",
            "1.2":"walk",
            "1.375":"dumbbell",
            "1.725":"weight-lifter",
            "1.9":"weight",
            "-1100.0":"arrow-down-bold-circle",
            "-550.0":"arrow-down-bold-circle-outline",
            "-275.0":"arrow-down-bold-outline",
            "0.0":"checkbox-blank-circle-outline",
            "275.0":"arrow-up-bold-outline",
            "550.0":"arrow-up-bold-circle-outline",
            "1100.0":"arrow-up-bold-circle"
        }
        s = Session()
        active_query = s.query(Active).first()
        if active_query:
            self.active_settings = s.query(Settings).filter(Settings.name == active_query.name).first()
            if self.active_settings:
                self.ids.profile_name_input.text = self.active_settings.name
                self.ids.gender_input.icon = icon_dict[self.active_settings.gender]
                self.ids.gender_input.text = self.active_settings.gender
                self.ids.weight_input.text = str(self.active_settings.weight)
                self.ids.height_input.text = str(self.active_settings.height)
                self.ids.age_input.text = str(self.active_settings.age)
                self.ids.activity_input.icon = icon_dict[self.active_settings.activity]
                self.ids.activity_input.text = str(self.active_settings.activity)
                self.ids.weight_gain_input.icon = icon_dict[self.active_settings.weight_gain_goal]
                self.ids.weight_gain_input.text = str(self.active_settings.weight_gain_goal)
                self.ids.calories_per_day.text = str(self.active_settings.calories_per_day)
                self.display_BMR()
                self.display_TDEE()
                self.display_cals_per_day()
            else:
                active_query.name = None
                self.ids.profile_name_input.text = ""
                self.ids.gender_input.icon = "close"
                self.ids.gender_input.text = ""
                self.ids.weight_input.text = ""
                self.ids.height_input.text = ""
                self.ids.age_input.text = ""
                self.ids.activity_input.icon = "close"
                self.ids.activity_input.text = ""
                self.ids.weight_gain_input.icon = "close"
                self.ids.weight_gain_input.text = ""
                self.ids.calories_per_day.text = ""
                self.ids.bmr.text = ""
                self.ids.tdee.text = ""
                self.ids.calories_per_day.text = ""
        s.close()
    
    def open_settings_search(self):
        c = Settings_Dialog()
        self.popup_base = MDDialog(
            title= "Search Setting Profiles",
            type="custom",
            content_cls=c,
            on_open=c.display_search
        )
        c.popup_base = self.popup_base
        self.popup_base.open()

class Settings_Already_Exist_Dialog(MDBoxLayout):
    
    def overwrite(self):
        self.settings_screen.update_settings()
        self.settings_already_exist_dialog.dismiss()
    
    def cancel(self):
        self.settings_already_exist_dialog.dismiss()
        
class Settings_Dialog(MDBoxLayout):

    def display_search(self,instance):
        """
        instance is expected to be a MDTextField
        """
        icon_dict = {
            "Male":"gender-male",
            "Female":"gender-female",
            "1.0":"cancel",
            "1.2":"walk",
            "1.375":"dumbbell",
            "1.725":"weight-lifter",
            "1.9":"weight",
            "-1100.0":"arrow-down-bold-circle",
            "-550.0":"arrow-down-bold-circle-outline",
            "-275.0":"arrow-down-bold-outline",
            "0.0":"checkbox-blank-circle-outline",
            "275.0":"arrow-up-bold-outline",
            "550.0":"arrow-up-bold-circle-outline",
            "1100.0":"arrow-up-bold-circle"
        }
        search = instance.text
        s = Session()
        settings_query = s.query(Settings).filter(Settings.name.contains(search)).all()
        if search:
            if settings_query:
                self.ids.settings_search_result_list.clear_widgets()
                for i in settings_query:
                    Item = ThreeLineAvatarIconObjectListItem(
                        text=i.name,
                        obj=i,
                        secondary_text=f"{i.weight} kg",
                        tertiary_text=f"{i.height} cm",
                        on_release=self.open_profile_settings
                    )
                    Icon_l = IconLeftWidget(icon=icon_dict[str(i.weight_gain_goal)])
                    Icon_r = IconRightWidget(icon=icon_dict[str(i.activity)])
                    Item.add_widget(Icon_l)
                    Item.add_widget(Icon_r)
                    self.ids.settings_search_result_list.add_widget(Item)
            else:
                self.ids.settings_search_result_list.clear_widgets()
        else:
            self.ids.settings_search_result_list.clear_widgets()
            for i in s.query(Settings).all():
                Item = ThreeLineAvatarIconObjectListItem(
                    text=i.name,
                    obj=i,
                    secondary_text=f"{i.weight} kg",
                    tertiary_text=f"{i.height} cm",
                    on_release=self.open_profile_settings
                )
                Icon_l = IconLeftWidget(icon=icon_dict[str(i.weight_gain_goal)])
                Icon_r = IconRightWidget(icon=icon_dict[str(i.activity)])
                Item.add_widget(Icon_l)
                Item.add_widget(Icon_r)
                self.ids.settings_search_result_list.add_widget(Item)
        s.close()
    
    def open_profile_settings(self,instance): #instance is expected to be a ThreeLineListItem
        c = Settings_Settings_Dialog(obj=instance.obj)
        self.popup_layer2 = MDDialog(
            title=instance.text,
            type="custom",
            content_cls=c,
            radius=[20, 7, 20, 7]
        )
        c.popup_layer2 = self.popup_layer2
        c.popup_base = self.popup_base
        self.popup_layer2.open()

class Settings_Settings_Dialog(MDBoxLayout):
    
    def __init__(self,obj):
        super(Settings_Settings_Dialog,self).__init__()
        self.obj = obj
    # For Future: Add another popup to validate deletion
    def delete(self):
        c = Delete_Settings_Dialog(obj=self.obj)
        self.popup_delete_layer3 = MDDialog(
            title="Delete profile?",
            type="custom",
            content_cls=c,
            radius=[20, 7, 20, 7]
        )
        c.popup_delete_layer3 = self.popup_delete_layer3
        c.popup_layer2 = self.popup_layer2
        c.popup_base = self.popup_base
        self.popup_delete_layer3.open()

    def use(self):
        Settings_Screen = MDApp.get_running_app().root.ids.screen_manager.get_screen("Settings_Screen")
        Settings_Screen.active_settings = self.obj
        s = Session()
        active = s.query(Active).first()
        if active:
            active.name = self.obj.name
        else:
            s.add(Active(name=self.obj.name))
        s.commit()
        s.close()
        Settings_Screen.load_active_settings()
        self.popup_base.dismiss()
        self.popup_layer2.dismiss()

class Delete_Settings_Dialog(MDBoxLayout):
    
    def __init__(self,obj):
        super().__init__()
        self.obj = obj

    def delete(self):
        s = Session()
        s.delete(self.obj)
        s.commit()
        s.close()
        Settings_Screen = MDApp.get_running_app().root.ids.screen_manager.get_screen("Settings_Screen")
        Settings_Screen.load_active_settings()
        self.popup_base.content_cls.display_search(self.popup_base.content_cls.ids.settings_search_input),
        self.popup_delete_layer3.dismiss()
        self.popup_layer2.dismiss()
    
    def cancel(self):
        self.popup_delete_layer3.dismiss()

class Ingredients_Screen(MDScreen):

    def __init__(self, *args,**kwargs):
        super(Ingredients_Screen,self).__init__(*args,**kwargs)
        self.ing_icon_dict = {
            "Meat":"food-steak",
            "Fish":"fish",
            "Grains / Bread":"bread-slice-outline",
            "Dairy":"cheese",
            "Vegetable":"carrot",
            "Fruit":"food-apple-outline",
            "Nuts / Seeds":"peanut",
            "Oil / Fats":"bottle-tonic",
            "Condiment":"soy-sauce",
            "Spice":"shaker-outline"
        }
        self.ing_icon_color_dict = {
            "All":(1,1,1,1),
            "Meat":(.39,.24,.04,1),
            "Fish":(1,.61,.39,1),
            "Grains / Bread":(1,.67,.35,1),
            "Dairy":(1,.78,.24,1),
            "Vegetable":(1,.55,.1,1),
            "Fruit":(.9,.16,0,1),
            "Nuts / Seeds":(.78,.53,0,1),
            "Oil / Fats":(.96,.75,0,1),
            "Condiment":(.78,.69,.24,1),
            "Spice":(.95,.95,.99,1)
        }
        self.refresh_and_sort_all_ingredients_list()
        
    def expand_collapse(self,btn):
        if btn.collapsed:
            btn.icon = "chevron-up"
            self.ids.layout.size_hint_y = 1
            self.ids.layout.height = self.ids.layout.minimum_height
            btn.pos_hint = {"top":.15}
            btn.collapsed = False
        else:
            btn.icon = "chevron-double-down"
            self.ids.layout.size_hint_y = None
            self.ids.layout.height = 0
            btn.pos_hint = {"top":.8}
            btn.collapsed = True
    
    def refresh_and_sort_all_ingredients_list(self): # this should only be called when an ingredient is added or deleted or edited and on start to sort the list
        s = Session()
        self.all_ingredient_id_and_stats_list_sorted = [i for i in sorted([(i.id,i.name,i.calories,i.unit,i.type) for i in s.query(Ingredient).all()],key=lambda x: x[4])]
        s.close()
        self.refresh_internal_list()

    def refresh_internal_list(self):
        self.ing_type = self.ids.filter.text if self.ids else "All"
        if self.ing_type == "All":
            self.display_ingredient_id_and_stats_list = self.all_ingredient_id_and_stats_list_sorted
        else:
            s = Session()
            ic(self.all_ingredient_id_and_stats_list_sorted)
            self.display_ingredient_id_and_stats_list = list(filter(lambda x: x[4] == self.ing_type,self.all_ingredient_id_and_stats_list_sorted))
            s.close()
        self.refresh_display_list() if self.ids else None

    def refresh_display_list(self):
        self.ing_search = self.ids.ing_search.text if self.ids else ""
        self.ids.ingredients_display_list.clear_widgets()
        for i in self.display_ingredient_id_and_stats_list:
            if self.ing_search.lower() in i[1].lower():
                Item = ThreeLineAvatarIconObjectListItem(
                    ingredient_id=i[0],
                    text=i[1],
                    secondary_text=f"{i[2]} kcals",
                    tertiary_text=f"per {'100' if i[3] =='gram' or i[3] =='ml' else ''} {i[3]}{'s' if i[3] == 'gram' or i[3] == 'ml' else ''}",
                    on_release=self.open_ingredient_options_dialog,
                )
                Icon = IconLeftWidget(
                    icon=self.ing_icon_dict[i[4]],
                    theme_text_color="Custom",
                    text_color=self.ing_icon_color_dict[i[4]],
                    )
                Item.add_widget(Icon)
                self.ids.ingredients_display_list.add_widget(Item)

    def open_add_ingredients_dialog(self):
        c = Add_Ingredient_Dialog()
        self.popup_base = MDDialog(
            title="Add Ingredient",
            type="custom",
            size_hint=(.9, None),
            height=MDApp.get_running_app().root.height*.8,
            pos_hint={"center_x": .5, "center_y": .5},
            content_cls=c,
            radius=[20, 7, 20, 7]
        )
        c.popup_base = self.popup_base
        self.popup_base.open()
    
    def open_ingredient_options_dialog(self,listitem): 
        c = Ingredient_Options_Dialog(ingredient_id=listitem.ingredient_id,
                                      ingredient_name=listitem.text)
        self.popup_base = MDDialog(
            title=f"{listitem.text} Options",
            type="custom",
            size_hint=(.9, None),
            pos_hint={"center_x": .5, "center_y": .5},
            content_cls=c,
            radius=[20, 7, 20, 7]
        )
        c.popup_base = self.popup_base
        self.popup_base.open()

    def open_filter_dropdown(self):
        self.choices_filter = [
            {
                "viewclass": "OneLineIconListItem",
                "text": "All",
                "icon":"filter-variant",
                "height": dp(56),
                "on_release": lambda x="filter-variant",y="All": self.set_filter_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Meat",
                "icon": "food-steak",
                "height": dp(56),
                "on_release": lambda x="food-steak",y="Meat": self.set_filter_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Fish",
                "icon": "fish",
                "height": dp(56),
                "on_release": lambda x="fish",y="Fish": self.set_filter_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Grains / Bread",
                "icon": "bread-slice-outline",
                "height": dp(56),
                "on_release": lambda x="bread-slice-outline",y="Grains / Bread": self.set_filter_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Dairy",
                "icon": "cheese",
                "height": dp(56),
                "on_release": lambda x="cheese",y="Dairy": self.set_filter_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Vegetable",
                "icon": "carrot",
                "height": dp(56),
                "on_release": lambda x="carrot",y="Vegetable": self.set_filter_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Fruit",
                "icon": "food-apple-outline",
                "height": dp(56),
                "on_release": lambda x="food-apple-outline",y="Fruit": self.set_filter_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Nuts / Seeds",
                "icon": "peanut",
                "height": dp(56),
                "on_release": lambda x="peanut",y="Nuts / Seeds": self.set_filter_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Oil / Fats",
                "icon": "bottle-tonic",
                "height": dp(56),
                "on_release": lambda x="bottle-tonic",y="Oil / Fats": self.set_filter_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Condiment",
                "icon": "soy-sauce",
                "height": dp(56),
                "on_release": lambda x="soy-sauce",y="Condiment": self.set_filter_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Spice",
                "icon": "shaker-outline",
                "height": dp(56),
                "on_release": lambda x="shaker-outline",y="Spice": self.set_filter_icon(x,y)
            },
        ]
        self.menu_list_type = MDDropdownMenu(
            caller=self.ids.filter,
            items=self.choices_filter,
            position="auto",
            width_mult=4
        )
        self.menu_list_type.open()

    def set_filter_icon(self, icon, text):
        self.ids.filter.icon = icon
        self.ids.filter.text_color = self.ing_icon_color_dict[text]
        self.ids.filter.text = text
        self.refresh_internal_list()
        self.menu_list_type.dismiss()

class Add_Ingredient_Dialog(MDBoxLayout):
    
    def __init__(self, *args, **kwargs):
        super(Add_Ingredient_Dialog, self).__init__(*args, **kwargs)
        self.ing_icon_dict = {
            "Meat":"food-steak",
            "Fish":"fish",
            "Grains / Bread":"bread-slice-outline",
            "Dairy":"cheese",
            "Vegetable":"carrot",
            "Fruit":"food-apple-outline",
            "Nuts / Seeds":"peanut",
            "Oil / Fats":"bottle-tonic",
            "Condiment":"soy-sauce",
            "Spice":"shaker-outline",
            "1":"cancel",
            "2":"numeric-2",
            "3":"numeric-3",
            "4":"numeric-4",
            "5":"numeric-5",
            "6":"numeric-6",
            "7":"numeric-7",
            "8":"numeric-8",
            "9":"numeric-9",
            "10":"numeric-10",
            "False":"all-inclusive",
            "gram":"weight-gram",
            "ml":"cup",
            "piece":"puzzle-outline"
        }
        self.ing_screen = MDApp.get_running_app().root.ids.ingredients_screen
    
    def open_divisibility_dropdown(self):
        self.choices_divisibility = [
            {
                "viewclass": "OneLineIconListItem",
                "text": "Indivisible",
                "icon": "cancel",
                "height": dp(56),
                "on_release": lambda x="cancel",y=1: self.set_divisibility_icon(x,y),
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "2",
                "icon": "numeric-2",
                "height": dp(56),
                "on_release": lambda x="numeric-2",y=2: self.set_divisibility_icon(x,y),
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "3",
                "icon": "numeric-3",
                "height": dp(56),
                "on_release": lambda x="numeric-3",y=3: self.set_divisibility_icon(x,y),
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "4",
                "icon": "numeric-4",
                "height": dp(56),
                "on_release": lambda x="numeric-4",y=4: self.set_divisibility_icon(x,y),
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "5",
                "icon": "numeric-5",
                "height": dp(56),
                "on_release": lambda x="numeric-5",y=5: self.set_divisibility_icon(x,y),
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "6",
                "icon": "numeric-6",
                "height": dp(56),
                "on_release": lambda x="numeric-6",y=6: self.set_divisibility_icon(x,y),
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "7",
                "icon": "numeric-7",
                "height": dp(56),
                "on_release": lambda x="numeric-7",y=7: self.set_divisibility_icon(x,y),
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "8",
                "icon": "numeric-8",
                "height": dp(56),
                "on_release": lambda x="numeric-8",y=8: self.set_divisibility_icon(x,y),
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "9",
                "icon": "numeric-9",
                "height": dp(56),
                "on_release": lambda x="numeric-9",y=9: self.set_divisibility_icon(x,y),
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "10",
                "icon": "numeric-10",
                "height": dp(56),
                "on_release": lambda x="numeric-10",y=10: self.set_divisibility_icon(x,y),
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "By any amount",
                "icon": "all-inclusive",
                "height": dp(56),
                "on_release": lambda x="all-inclusive",y=False: self.set_divisibility_icon(x,y),
            }
        ]
        self.menu_list_divisibility = MDDropdownMenu(
            caller=self.ids.add_ing_divisibility,
            items=self.choices_divisibility,
            position="auto",
            width_mult=4
        )
        self.menu_list_divisibility.open()
    
    def set_divisibility_icon(self, icon, value):
        self.ids.add_ing_divisibility.icon = icon
        self.ids.add_ing_divisibility.value = value
        self.menu_list_divisibility.dismiss()
        self.add_button_check_validity()
    
    def open_type_dropdown(self):
        self.choices_type = [
            {
                "viewclass": "OneLineIconListItem",
                "text": "Meat",
                "icon": "food-steak",
                "height": dp(56),
                "on_release": lambda x="food-steak",y="Meat": self.set_type_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Fish",
                "icon": "fish",
                "height": dp(56),
                "on_release": lambda x="fish",y="Fish": self.set_type_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Grains / Bread",
                "icon": "bread-slice-outline",
                "height": dp(56),
                "on_release": lambda x="bread-slice-outline",y="Grains / Bread": self.set_type_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Dairy",
                "icon": "cheese",
                "height": dp(56),
                "on_release": lambda x="cheese",y="Dairy": self.set_type_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Vegetable",
                "icon": "carrot",
                "height": dp(56),
                "on_release": lambda x="carrot",y="Vegetable": self.set_type_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Fruit",
                "icon": "food-apple-outline",
                "height": dp(56),
                "on_release": lambda x="food-apple-outline",y="Fruit": self.set_type_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Nuts / Seeds",
                "icon": "peanut",
                "height": dp(56),
                "on_release": lambda x="peanut",y="Nuts / Seeds": self.set_type_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Oil / Fats",
                "icon": "bottle-tonic",
                "height": dp(56),
                "on_release": lambda x="bottle-tonic",y="Oil / Fats": self.set_type_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Condiment",
                "icon": "soy-sauce",
                "height": dp(56),
                "on_release": lambda x="soy-sauce",y="Condiment": self.set_type_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Spice",
                "icon": "shaker-outline",
                "height": dp(56),
                "on_release": lambda x="shaker-outline",y="Spice": self.set_type_icon(x,y)
            },
        ]
        self.menu_list_type = MDDropdownMenu(
            caller=self.ids.add_ing_type,
            items=self.choices_type,
            position="auto",
            width_mult=4
        )
        self.menu_list_type.open()
    
    def set_type_icon(self, icon, text):
        self.ids.add_ing_type.icon = icon
        self.ids.add_ing_type.text = text
        self.menu_list_type.dismiss()
        self.add_button_check_validity()
    
    def open_unit_dropdown(self):
        self.choices_unit = [
            {
                "viewclass": "OneLineIconListItem",
                "text": "grams",
                "icon": "weight-gram",
                "height": dp(56),
                "on_release": lambda x="weight-gram",y="gram": self.set_unit_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "milliliters",
                "icon": "cup",
                "height": dp(56),
                "on_release": lambda x="cup",y="ml": self.set_unit_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "pieces",
                "icon": "puzzle-outline",
                "height": dp(56),
                "on_release": lambda x="puzzle-outline",y="piece": self.set_unit_icon(x,y)
            }
        ]
        self.menu_list_unit = MDDropdownMenu(
            caller=self.ids.add_ing_unit,
            items=self.choices_unit,
            position="auto",
            width_mult=4
        )
        self.menu_list_unit.open()
    
    def set_unit_icon(self, icon, text):
        self.ids.add_ing_unit.icon = icon
        self.ids.add_ing_unit.text = text
        self.menu_list_unit.dismiss()
        self.add_ing_divisibility_check_validity()
        self.add_button_check_validity()
    
    def add_ing_divisibility_check_validity(self):
        if self.ids.add_ing_unit.text == "gram" or self.ids.add_ing_unit.text == "ml":
            self.ids.add_ing_divisibility.disabled = True
            self.ids.divisibility_label.color = (1,1,1,.5)
            self.ids.add_ing_divisibility.value = False
            self.ids.add_ing_divisibility.icon = "all-inclusive"
        else:
            self.ids.add_ing_divisibility.disabled = False
            self.ids.divisibility_label.color = (1,1,1,1)
    
    def cancel(self):
        self.popup_base.dismiss()
    
    def add_button_check_validity(self):
        if all(
            [
                self.ids.add_ing_name.text,
                self.ids.add_ing_calories.text,
                self.ids.add_ing_fats.text,
                self.ids.add_ing_carbohydrates.text,
                self.ids.add_ing_proteins.text
            ]
        ) and self.ids.add_ing_unit.icon != "close" and self.ids.add_ing_type.icon != "close" and self.ids.add_ing_divisibility.icon != "close":
            self.ids.add_ing_button.disabled = False
        else:
            self.ids.add_ing_button.disabled = True
    
    def add_ingredient(self):
        s = Session()
        ing_query = s.query(Ingredient).filter(Ingredient.name == self.ids.add_ing_name.text).first()
        if not ing_query:
            new_ingredient = Ingredient(
                name = self.ids.add_ing_name.text,
                type = self.ids.add_ing_type.text,
                unit = self.ids.add_ing_unit.text,
                divisible_by = self.ids.add_ing_divisibility.value,
                calories = self.ids.add_ing_calories.text,
                fats = self.ids.add_ing_fats.text,
                carbohydrates = self.ids.add_ing_carbohydrates.text,
                proteins = self.ids.add_ing_proteins.text,
                snack=False
            )
            s.add(new_ingredient)
            s.commit()
            s.close()
            self.ing_screen.refresh_and_sort_all_ingredients_list()
            self.popup_base.dismiss()
        else:
            s.close()
            c = Ingredient_Already_Exists_Dialog(ingredient_id=ing_query.id)
            self.ingredient_already_exists_dialog = MDDialog(
                title=f"{self.ids.add_ing_name.text} Already Exists, would you like to update it?",
                type="custom",
                content_cls=c,
                size_hint_x=.9,
                radius=[20, 7, 20, 7]
            )
            c.logic = self
            c.popup_base = self.popup_base
            c.ingredient_already_exists_dialog = self.ingredient_already_exists_dialog
            self.ingredient_already_exists_dialog.open()

class Ingredient_Already_Exists_Dialog(MDBoxLayout):
    
    def __init__(self, ingredient_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ingredient_id = ingredient_id
        self.ing_screen = MDApp.get_running_app().root.ids.ingredients_screen

    def cancel(self):
        self.ingredient_already_exists_dialog.dismiss()
        self.popup_base.dismiss()
    
    def update(self): # updates the ingredient in the database
        s = Session()
        self.ing = s.query(Ingredient).get(self.ingredient_id)
        self.ing.name = self.logic.add_ing_name.text
        self.ing.unit = self.logic.add_ing_unit.text
        self.ing.type = self.logic.add_ing_type.text
        self.ing.calories = self.logic.add_ing_calories.text
        self.ing.fats = self.logic.add_ing_fats.text
        self.ing.carbohydrates = self.logic.add_ing_carbohydrates.text
        self.ing.proteins = self.logic.add_ing_proteins.text
        self.ing.divisible_by = self.logic.add_ing_divisibility.value
        s.commit()
        s.close()
        self.ing_screen.refresh_and_sort_all_ingredients_list()
        self.ingredient_already_exists_dialog.dismiss()
        self.popup_base.dismiss()

class Ingredient_Options_Dialog(MDBoxLayout):
    
    def __init__(self, ingredient_id, ingredient_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ingredient_id = ingredient_id
        self.ingredient_name = ingredient_name
        self.ing_icon_dict = {
            "Meat":"food-steak",
            "Fish":"fish",
            "Grains / Bread":"bread-slice-outline",
            "Dairy":"cheese",
            "Vegetable":"carrot",
            "Fruit":"food-apple-outline",
            "Nuts / Seeds":"peanut",
            "Oil / Fats":"bottle-tonic",
            "Condiment":"soy-sauce",
            "Spice":"shaker-outline",
            "1":"cancel",
            "2":"numeric-2",
            "3":"numeric-3",
            "4":"numeric-4",
            "5":"numeric-5",
            "6":"numeric-6",
            "7":"numeric-7",
            "8":"numeric-8",
            "9":"numeric-9",
            "10":"numeric-10",
            "False":"all-inclusive",
            "0":"all-inclusive",
            "gram":"weight-gram",
            "ml":"cup",
            "piece":"puzzle-outline"
        }
    
    def edit(self):
        s = Session()
        self.ing = s.query(Ingredient).get(self.ingredient_id)
        c = Edit_Ingredient_Dialog(ingredient_id=self.ing.id,
                                   ingredient_name=self.ing.name)
        self.popup_layer2_edit = MDDialog(
            title=f"Edit {self.ing.name}?",
            type="custom",
            size_hint=(.9, None),
            pos_hint={"center_x": .5, "center_y": .5},
            content_cls=c,
            radius=[20, 7, 20, 7]
        )
        c.popup_layer2_edit = self.popup_layer2_edit
        c.popup_base = self.popup_base
        c.ids.update_ing_name.text = self.ing.name
        c.ids.update_ing_calories.text = str(self.ing.calories)
        c.ids.update_ing_fats.text = str(self.ing.fats)
        c.ids.update_ing_carbohydrates.text = str(self.ing.carbohydrates)
        c.ids.update_ing_proteins.text = str(self.ing.proteins)
        c.ids.update_ing_unit.text = str(self.ing.unit)
        c.ids.update_ing_unit.icon = self.ing_icon_dict[str(self.ing.unit)]
        c.ids.update_ing_type.text = str(self.ing.type)
        c.ids.update_ing_type.icon = self.ing_icon_dict[str(self.ing.type)]
        c.ids.update_ing_divisibility.value = str(self.ing.divisible_by)
        c.ids.update_ing_divisibility.icon = self.ing_icon_dict[str(self.ing.divisible_by)]
        s.close()
        self.popup_layer2_edit.open()
   
    def open_delete_ingredient_dialog(self):
        c = Delete_Ingredient_Dialog(ingredient_id=self.ingredient_id)
        self.popup_layer2_delete = MDDialog(
            title=f"Delete {self.ingredient_name} ?",
            type="custom",
            content_cls=c,
            radius=[20, 7, 20, 7]
        )
        c.popup_layer2_delete = self.popup_layer2_delete
        c.popup_base = self.popup_base
        self.popup_layer2_delete.open()

class Delete_Ingredient_Dialog(MDBoxLayout):
    
    def __init__(self, ingredient_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ingredient_id = ingredient_id
        self.ing_screen = MDApp.get_running_app().root.ids.ingredients_screen
    
    def cancel(self):
        self.popup_layer2_delete.dismiss()
    
    def delete(self):
        s = Session()
        self.ing = s.query(Ingredient).get(self.ingredient_id)
        self.asc_objs = s.query(Association).filter(Association.ingredient_id == self.ing.id).all()
        for i in self.asc_objs: # makes sure that the associations are also deleted
            s.delete(i)
        s.delete(self.ing)
        s.commit()
        s.close()
        self.ing_screen.refresh_and_sort_all_ingredients_list()
        self.popup_layer2_delete.dismiss()
        self.popup_base.dismiss()

class Edit_Ingredient_Dialog(MDBoxLayout):
    
    def __init__(self, ingredient_id, ingredient_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ingredient_id = ingredient_id
        self.ingredient_name = ingredient_name
        self.ing_screen = MDApp.get_running_app().root.ids.ingredients_screen
        s = Session()
        self.ingredient_name_list = [i.name if i.name != self.ingredient_name else None for i in s.query(Ingredient).all()]
        s.close()

    def open_divisibility_dropdown(self):
        self.choices_divisibility = [
            {
                "viewclass": "OneLineIconListItem",
                "text": "Indivisible",
                "icon": "cancel",
                "height": dp(56),
                "on_release": lambda x="cancel",y=1: self.set_divisibility_icon(x,y),
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "2",
                "icon": "numeric-2",
                "height": dp(56),
                "on_release": lambda x="numeric-2",y=2: self.set_divisibility_icon(x,y),
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "3",
                "icon": "numeric-3",
                "height": dp(56),
                "on_release": lambda x="numeric-3",y=3: self.set_divisibility_icon(x,y),
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "4",
                "icon": "numeric-4",
                "height": dp(56),
                "on_release": lambda x="numeric-4",y=4: self.set_divisibility_icon(x,y),
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "5",
                "icon": "numeric-5",
                "height": dp(56),
                "on_release": lambda x="numeric-5",y=5: self.set_divisibility_icon(x,y),
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "6",
                "icon": "numeric-6",
                "height": dp(56),
                "on_release": lambda x="numeric-6",y=6: self.set_divisibility_icon(x,y),
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "7",
                "icon": "numeric-7",
                "height": dp(56),
                "on_release": lambda x="numeric-7",y=7: self.set_divisibility_icon(x,y),
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "8",
                "icon": "numeric-8",
                "height": dp(56),
                "on_release": lambda x="numeric-8",y=8: self.set_divisibility_icon(x,y),
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "9",
                "icon": "numeric-9",
                "height": dp(56),
                "on_release": lambda x="numeric-9",y=9: self.set_divisibility_icon(x,y),
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "10",
                "icon": "numeric-10",
                "height": dp(56),
                "on_release": lambda x="numeric-10",y=10: self.set_divisibility_icon(x,y),
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "By any amount",
                "icon": "all-inclusive",
                "height": dp(56),
                "on_release": lambda x="all-inclusive",y=False: self.set_divisibility_icon(x,y),
            }
        ]
        self.menu_list_divisibility = MDDropdownMenu(
            caller=self.ids.update_ing_divisibility,
            items=self.choices_divisibility,
            position="auto",
            width_mult=4
        )
        self.menu_list_divisibility.open()
    
    def set_divisibility_icon(self, icon, value):
        self.ids.update_ing_divisibility.icon = icon
        self.ids.update_ing_divisibility.value = value
        self.menu_list_divisibility.dismiss()
        self.update_button_check_validity()
    
    def open_type_dropdown(self):
        self.choices_type = [
            {
                "viewclass": "OneLineIconListItem",
                "text": "Meat",
                "icon": "food-steak",
                "height": dp(56),
                "on_release": lambda x="food-steak",y="Meat": self.set_type_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Fish",
                "icon": "fish",
                "height": dp(56),
                "on_release": lambda x="fish",y="Fish": self.set_type_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Grains / Bread",
                "icon": "bread-slice-outline",
                "height": dp(56),
                "on_release": lambda x="bread-slice-outline",y="Grains / Bread": self.set_type_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Dairy",
                "icon": "cheese",
                "height": dp(56),
                "on_release": lambda x="cheese",y="Dairy": self.set_type_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Vegetable",
                "icon": "carrot",
                "height": dp(56),
                "on_release": lambda x="carrot",y="Vegetable": self.set_type_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Fruit",
                "icon": "food-apple-outline",
                "height": dp(56),
                "on_release": lambda x="food-apple-outline",y="Fruit": self.set_type_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Nuts / Seeds",
                "icon": "peanut",
                "height": dp(56),
                "on_release": lambda x="peanut",y="Nuts / Seeds": self.set_type_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Oil / Fats",
                "icon": "bottle-tonic",
                "height": dp(56),
                "on_release": lambda x="bottle-tonic",y="Oil / Fats": self.set_type_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Condiment",
                "icon": "soy-sauce",
                "height": dp(56),
                "on_release": lambda x="soy-sauce",y="Condiment": self.set_type_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Spice",
                "icon": "shaker-outline",
                "height": dp(56),
                "on_release": lambda x="shaker-outline",y="Spice": self.set_type_icon(x,y)
            },
        ]
        self.menu_list_type = MDDropdownMenu(
            caller=self.ids.update_ing_type,
            items=self.choices_type,
            position="auto",
            width_mult=4
        )
        self.menu_list_type.open()
    
    def set_type_icon(self, icon, text):
        self.ids.update_ing_type.icon = icon
        self.ids.update_ing_type.text = text
        self.menu_list_type.dismiss()
        self.update_button_check_validity()
    
    def open_unit_dropdown(self):
        self.choices_unit = [
            {
                "viewclass": "OneLineIconListItem",
                "text": "grams",
                "icon": "weight-gram",
                "height": dp(56),
                "on_release": lambda x="weight-gram",y="gram": self.set_unit_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "milliliters",
                "icon": "cup",
                "height": dp(56),
                "on_release": lambda x="cup",y="ml": self.set_unit_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "pieces",
                "icon": "puzzle-outline",
                "height": dp(56),
                "on_release": lambda x="puzzle-outline",y="piece": self.set_unit_icon(x,y)
            }
        ]
        self.menu_list_unit = MDDropdownMenu(
            caller=self.ids.update_ing_unit,
            items=self.choices_unit,
            position="auto",
            width_mult=4
        )
        self.menu_list_unit.open()
    
    def set_unit_icon(self, icon, text):
        self.ids.update_ing_unit.icon = icon
        self.ids.update_ing_unit.text = text
        self.menu_list_unit.dismiss()
        self.update_button_check_validity()
        self.update_ing_divisibility_check_validity()

    def update_ing_divisibility_check_validity(self):
        if self.ids.update_ing_unit.text == "gram" or self.ids.update_ing_unit.text == "ml":
            self.ids.update_ing_divisibility.disabled = True
            self.ids.divisibility_label.color = (1,1,1,.5)
            self.ids.update_ing_divisibility.value = False
            self.ids.update_ing_divisibility.icon = "all-inclusive"
        else:
            self.ids.update_ing_divisibility.disabled = False
            self.ids.divisibility_label.color = (1,1,1,1)

    def ing_name_check_validity(self):
        if self.ids.update_ing_name.text in self.ingredient_name_list:
            self.ids.update_ing_name.hint_text = "Already exists!"
            self.ids.update_ing_name.text_color_normal = (1,0,0,1)
            return False
        else:
            self.ids.update_ing_name.hint_text = ""
            self.ids.update_ing_name.text_color_normal = (1,1,1,.25) # MDApp.get_running_app().theme_cls.primary_color
            return True

    def stats_check_validity(self):
        if all(
            [
                self.ids.update_ing_name.text,
                self.ids.update_ing_calories.text,
                self.ids.update_ing_fats.text,
                self.ids.update_ing_carbohydrates.text,
                self.ids.update_ing_proteins.text
            ]
        ) and self.ids.update_ing_unit.icon != "close" and self.ids.update_ing_type.icon != "close" and self.ids.update_ing_divisibility.icon != "close":
            return True
        else:
            return False

    def update_button_check_validity(self):
        if self.ing_name_check_validity() and self.stats_check_validity():
            self.ids.update_ing_button.disabled = False
        else:
            self.ids.update_ing_button.disabled = True
    
    def cancel(self):
        self.popup_layer2_edit.dismiss()
    
    def update_ingredient(self):
        s = Session()
        self.ing = s.query(Ingredient).get(self.ingredient_id)
        self.ing.name = self.ids.update_ing_name.text
        self.ing.calories = self.ids.update_ing_calories.text
        self.ing.fats = self.ids.update_ing_fats.text
        self.ing.carbohydrates = self.ids.update_ing_carbohydrates.text
        self.ing.proteins = self.ids.update_ing_proteins.text
        self.ing.unit = self.ids.update_ing_unit.text
        self.ing.type = self.ids.update_ing_type.text
        self.ing.divisible_by = self.ids.update_ing_divisibility.value
        s.commit()
        s.close()
        self.ing_screen.refresh_and_sort_all_ingredients_list()
        self.popup_layer2_edit.dismiss()
        self.popup_base.dismiss()

class Meals_Screen(MDScreen):
        # migrate the inglist to this instance to midigate more frequent loading and queries
    def __init__(self, *args, **kwargs):
        super(Meals_Screen, self).__init__(*args, **kwargs)
        self.meal_icon_dict = {
            "hot":"thermometer",
            "cold":"snowflake",
            "sweet":"candy-outline",
            "savory":"french-fries",
            "breakfast_hot":"egg-fried",
            "breakfast_cold":"bowl-mix-outline",
            "dinner_lunch_hot":"pot-steam-outline",
            "dinner_lunch_cold":"fridge-outline",
            "snack_sweet":"cookie-outline",
            "snack_savory":"sausage",
        }
        self.meal_icon_color_dict = {
            "thermometer":(1,0,0,1),
            "snowflake":(0,.7,1,1),
            "candy-outline":(1,.4,.8,1),
            "french-fries":(1,.8,0,1),
            "egg-fried":(1,.5,0,1),
            "bowl-mix-outline":(1,.9,0,1),
            "pot-steam-outline":(.7,0,0.1),
            "fridge-outline":(0.4,.2,1),
            "cookie-outline":(.7,0,.15,1),
            "sausage":(.7,.2,.04,1)
        }
        self.show_all_meals = True
        self.ignore_sweet_savory = True
        self.ignore_hot_cold = True
        self.breakfast = False
        self.lunch = False
        self.dinner = False
        self.snack = False
        self.hot_cold = False
        self.sweet_savory = False
    
    def expand_collapse(self,btn):
        if btn.collapsed:
            btn.icon = "chevron-up"
            self.ids.layout.size_hint_y = 1
            self.ids.layout.height = self.ids.layout.minimum_height
            btn.pos_hint = {"top":.15}
            btn.collapsed = False
        else:
            btn.icon = "chevron-double-down"
            self.ids.layout.size_hint_y = None
            self.ids.layout.height = 0
            btn.pos_hint = {"top":.8}
            btn.collapsed = True

    def open_filter_dialog(self):
        c = Filter_Dialog()
        self.popup_base = MDDialog(
            title="Search filter",
            type="custom",
            size_hint=(.9, None),
            height=MDApp.get_running_app().root.height*.8,
            pos_hint={"center_x": .5, "center_y": .5},
            content_cls=c,
            radius=[20, 7, 20, 7]
        )
        c.popup_base = self.popup_base
        c.ids.breakfast.active = self.breakfast
        c.ids.lunch.active = self.lunch
        c.ids.dinner.active = self.dinner
        c.ids.snack.active = self.snack
        c.ids.hot_cold.active = self.hot_cold
        c.ids.sweet_savory.active = self.sweet_savory
        c.ids.ignore_hot_cold.active = not(self.ignore_hot_cold)
        c.ids.ignore_sweet_savory.active = not(self.ignore_sweet_savory)
        self.popup_base.open()

    def refresh_internal_list(self):
        ic(self.breakfast,
           self.lunch,
           self.dinner,
           self.snack,
           self.hot_cold,
           self.sweet_savory,
           self.ignore_hot_cold,
           self.ignore_sweet_savory)
        s = Session()
        if self.show_all_meals:
            self.meal_list = s.query(Meal).all()
        else:
            filter_conditions = [
                Meal.breakfast == True,
                Meal.lunch == True,
                Meal.dinner == True,
                Meal.snack == True
            ]
            filter_condition_inputs = [self.breakfast,self.lunch,self.dinner,self.snack]
            for index, i in enumerate(filter_conditions.copy()):
                if not filter_condition_inputs[index]:
                    filter_conditions.remove(i)
            ic(filter_conditions)
            if self.ignore_hot_cold and self.ignore_sweet_savory:
                self.meal_list = s.query(Meal).filter(
                    or_(
                        *filter_conditions
                    )
                ).all()
            elif self.ignore_hot_cold:
                self.meal_list = s.query(Meal).filter(
                    and_(
                        or_(
                            *filter_conditions
                        ),
                        Meal.sweet_savory == self.sweet_savory
                    )
                ).all()
            elif self.ignore_sweet_savory:
                self.meal_list = s.query(Meal).filter(
                    and_(
                        or_(
                            *filter_conditions
                        ),
                        Meal.hot_cold == self.hot_cold
                    )
                ).all()
            else:
                self.meal_list = s.query(Meal).filter(
                    and_(
                        or_(
                            *filter_conditions
                        ),
                        Meal.hot_cold == self.hot_cold,
                        Meal.sweet_savory == self.sweet_savory
                    )
                ).all()
        s.close()
        ic(self.meal_list)

    def refresh_display_list(self):
        search = self.ids.meal_search.text
        self.ids.meals_display_list.clear_widgets()
        if self.meal_list:
            self.meal_list_for_search = list(filter(lambda x: True if search.lower() in x.name.lower() else False, self.meal_list))
            s = Session()
            for index, i in enumerate(self.meal_list_for_search):
                s.add(i)
                icon_hot_cold = self.meal_icon_dict["cold" if i.hot_cold else "hot"]
                icon_hot_cold_color = self.meal_icon_color_dict[icon_hot_cold]
                icon_sweet_savory = self.meal_icon_dict["savory" if i.sweet_savory else "sweet"]
                icon_sweet_savor_color = self.meal_icon_color_dict[icon_sweet_savory]
                icon_type = self.meal_icon_dict["breakfast_hot" if i.breakfast and not i.hot_cold else "breakfast_cold" if i.breakfast and i.hot_cold else "dinner_lunch_hot" if i.dinner and not i.hot_cold or i.lunch and not i.hot_cold else "dinner_lunch_cold" if i.dinner and i.hot_cold or i.lunch and i.hot_cold else "snack_sweet" if i.snack and not i.sweet_savory else "snack_savory"]
                icon_type_color = self.meal_icon_color_dict[icon_type]
                Item = ThreeLineAvatarIconObjectListItem(
                    obj=i,
                    text=i.name,
                    secondary_text=f"{round(i.calories,2)} kcals",
                    tertiary_text=f"{round(i.proteins,2)}g protein, {round(i.carbohydrates,2)}g carbs, {round(i.fats,2)}g fat",
                    on_release=self.open_meal_options_dialog
                    )
                
                Item.add_widget(
                    IconLeftWidget(
                        icon=icon_type,
                        theme_text_color="Custom",
                        text_color=icon_type_color
                    )
                )
                Item.add_widget(
                    MDBoxLayout(
                        Widget(size_hint_x=15),
                        MDIconButton(
                            size_hint_x=2,
                            pos_hint={"center_y":.6},
                            icon=icon_sweet_savory,
                            theme_text_color="Custom",
                            text_color=icon_sweet_savor_color
                        ),
                        MDIconButton(
                            size_hint_x=2,
                            pos_hint={"center_y":.6},
                            icon=icon_hot_cold,
                            theme_text_color="Custom",
                            text_color=icon_hot_cold_color
                        ),
                        orientation='horizontal',
                        size_hint_x=None,
                        width=MDApp.get_running_app().root.width*.95,
                        pos_hint={"center_y": .5}
                    )
                )
                self.ids.meals_display_list.add_widget(Item)
            s.close()

    def open_add_meal_dialog(self):
        c = Add_Meal_Dialog()
        self.popup_base = MDDialog(
            title="Add Meal",
            type="custom",
            size_hint=(.9, None),
            height=MDApp.get_running_app().root.height*.8,
            pos_hint={"center_x": .5, "center_y": .5},
            content_cls=c,
            radius=[20, 7, 20, 7]
        )
        c.popup_base = self.popup_base
        self.popup_base.open()
    
    def open_meal_options_dialog(self,listitem):
        c = Meal_Options_Dialog(meal=listitem.obj)
        self.popup_base = MDDialog(
            title="Meal Options",
            type="custom",
            size_hint=(.9, None),
            height=MDApp.get_running_app().root.height*.8,
            pos_hint={"center_x": .5, "center_y": .5},
            content_cls=c,
            radius=[20, 7, 20, 7]
        )
        c.popup_base = self.popup_base
        self.popup_base.open()

class Filter_Dialog(MDBoxLayout):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.meals_screen = MDApp.get_running_app().root.ids.meals_screen
    
    def cancel(self):
        self.popup_base.dismiss()
    
    def apply_filter(self):
        self.meals_screen.breakfast = self.ids.breakfast.active
        self.meals_screen.lunch = self.ids.lunch.active
        self.meals_screen.dinner = self.ids.dinner.active
        self.meals_screen.snack = self.ids.snack.active
        self.meals_screen.hot_cold = self.ids.hot_cold.active
        self.meals_screen.sweet_savory = self.ids.sweet_savory.active
        self.meals_screen.show_all_meals = False
        ic(self.meals_screen.ignore_sweet_savory)
        ic(self.meals_screen.ignore_hot_cold)
        self.meals_screen.refresh_internal_list()
        self.meals_screen.refresh_display_list()
        self.popup_base.dismiss()

    def activate_deactivate_sweet_savory_filter(self,state):
        if state == "down":
            self.ids.sweet_savory.disabled = False
            self.ids.label_sweet.text_color = 1,1,1,1
            self.ids.label_savory.text_color = 1,1,1,1
            self.meals_screen.ignore_sweet_savory = False
            ic(self.meals_screen.ignore_sweet_savory)
        else:
            self.ids.sweet_savory.disabled = True
            self.ids.label_sweet.text_color = 1,1,1,.25
            self.ids.label_savory.text_color = 1,1,1,.25
            self.meals_screen.ignore_sweet_savory = True
            ic(self.meals_screen.ignore_sweet_savory)
    
    def activate_deactivate_hot_cold_filter(self,state):
        if state == "down":
            self.ids.hot_cold.disabled = False
            self.ids.label_hot.text_color = 1,1,1,1
            self.ids.label_cold.text_color = 1,1,1,1
            self.meals_screen.ignore_hot_cold = False
            ic(self.meals_screen.ignore_hot_cold)
        else:
            self.ids.hot_cold.disabled = True
            self.ids.label_hot.text_color = 1,1,1,.25
            self.ids.label_cold.text_color = 1,1,1,.25
            self.meals_screen.ignore_hot_cold = True
            ic(self.meals_screen.ignore_hot_cold)

    def reset_filter(self):
        self.meals_screen.show_all_meals = True
        self.meals_screen.ignore_sweet_savory = True
        self.meals_screen.ignore_hot_cold = True
        self.meals_screen.breakfast = False
        self.meals_screen.lunch = False
        self.meals_screen.dinner = False
        self.meals_screen.snack = False
        self.meals_screen.hot_cold = False
        self.meals_screen.sweet_savory = False
        self.meals_screen.refresh_internal_list()
        self.meals_screen.refresh_display_list()
        self.popup_base.dismiss()
    
    def check_apply_filter_button_validity(self):
        ic("check")
        if self.ids.breakfast.active or self.ids.lunch.active or self.ids.dinner.active or self.ids.snack.active:
            self.ids.apply_filter_button.disabled = False
        else:
            self.ids.apply_filter_button.disabled = True

class Add_Meal_Dialog(MDBoxLayout):
    
    def __init__(self, *args, **kwargs):
        super(Add_Meal_Dialog, self).__init__(*args, **kwargs)
        self.meal_screen = MDApp.get_running_app().root.ids.meals_screen
    
    def cancel(self):
        self.popup_base.dismiss()

    def check_add_meal_button_validity(self):
        if any([self.ids.breakfast.active,self.ids.lunch.active,self.ids.dinner.active,self.ids.snack.active]) and self.ids.meal_name.text != "":
            self.ids.add_meal_button.disabled = False
        else:
            self.ids.add_meal_button.disabled = True

    def add_meal(self):
        s = Session()
        meal_query = s.query(Meal).filter(Meal.name == self.ids.meal_name.text).first()
        if meal_query:
            s.close()
            self.open_meal_already_exists_dialog(meal_query)
        else:
            new_meal = Meal(
                name = self.ids.meal_name.text,
                breakfast = self.ids.breakfast.active,
                lunch = self.ids.lunch.active,
                dinner = self.ids.dinner.active,
                snack = self.ids.snack.active,
                hot_cold = self.ids.hot_cold.active,
                sweet_savory = self.ids.sweet_savory.active
            )
            s.add(new_meal)
            s.commit()
            s.close()
            self.meal_screen.refresh_internal_list()
            self.meal_screen.refresh_display_list()
            self.popup_base.dismiss()

    def open_meal_already_exists_dialog(self,meal):
        c = Meal_Already_Exists_Dialog(meal)
        self.popup_layer2 = MDDialog(
            title=f"{meal.name} Already Exists, would you like to update it?",
            type="custom",
            content_cls=c,
            size_hint_x=.9,
            radius=[20, 7, 20, 7]
        )
        c.popup_base = self.popup_base
        c.popup_layer2 = self.popup_layer2
        self.popup_layer2.open()

class Meal_Already_Exists_Dialog(MDBoxLayout):

    def __init__(self, meal, *args, **kwargs):
        super(Meal_Already_Exists_Dialog, self).__init__(*args, **kwargs)
        self.meal = meal
    
    def cancel(self):
        self.popup_layer2.dismiss()
    
    def update(self):
        ic("yet to be added")
        pass # should open the display meal screen that is yet to be added

class Meal_Options_Dialog(MDBoxLayout):

    def __init__(self, meal, *args, **kwargs):
        super(Meal_Options_Dialog, self).__init__(*args, **kwargs)
        self.meal = meal
        self.screen_manager = MDApp.get_running_app().root.ids.screen_manager

    def open_delete_meal_dialog(self):
        c = Delete_Meal_Dialog(self.meal)
        self.popup_layer2 = MDDialog(
            title=f"Delete {self.meal.name} ?",
            type="custom",
            content_cls=c,
            size_hint_x=.9,
            radius=[20, 7, 20, 7]
        )
        c.popup_base = self.popup_base
        c.popup_layer2 = self.popup_layer2
        self.popup_layer2.open()
    
    def edit(self):
        self.screen_manager.add_widget(
            Display_Meal_Screen(meal_id=self.meal.id)
        )
        self.screen_manager.get_screen("Display_Meal_Screen").ids.meal_name.text = self.meal.name
        self.screen_manager.get_screen("Display_Meal_Screen").refresh_internal_ingredient_list()
        self.screen_manager.get_screen("Display_Meal_Screen").refresh_display_ingredient_list()
        self.screen_manager.current = "Display_Meal_Screen"
        self.screen_manager.transition.direction = "left"
        self.popup_base.dismiss()

class Delete_Meal_Dialog(MDBoxLayout):

    def __init__(self, meal, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.meal = meal
        self.meal_screen = MDApp.get_running_app().root.ids.meals_screen
    def cancel(self):
        self.popup_layer2.dismiss()
    
    def delete(self):
        s = Session()
        s.add(self.meal)
        s.delete(self.meal)
        s.commit()
        s.close()
        self.meal_screen.refresh_internal_list()
        self.meal_screen.refresh_display_list()
        self.popup_layer2.dismiss()
        self.popup_base.dismiss()

class Display_Meal_Screen(MDScreen):

    def __init__(self, meal_id, *args, **kwargs):
        super(Display_Meal_Screen, self).__init__(*args, **kwargs)
        s = Session()
        self.ing_icon_dict = {
            "Meat":"food-steak",
            "Fish":"fish",
            "Grains / Bread":"bread-slice-outline",
            "Dairy":"cheese",
            "Vegetable":"carrot",
            "Fruit":"food-apple-outline",
            "Nuts / Seeds":"peanut",
            "Oil / Fats":"bottle-tonic",
            "Condiment":"soy-sauce",
            "Spice":"shaker-outline"
        }
        self.ing_icon_color_dict = {
            "All":(1,1,1,1),
            "Meat":(.39,.24,.04,1),
            "Fish":(1,.61,.39,1),
            "Grains / Bread":(1,.67,.35,1),
            "Dairy":(1,.78,.24,1),
            "Vegetable":(1,.55,.1,1),
            "Fruit":(.9,.16,0,1),
            "Nuts / Seeds":(.78,.53,0,1),
            "Oil / Fats":(.96,.75,0,1),
            "Condiment":(.78,.69,.24,1),
            "Spice":(.95,.95,.99,1)
        }
        self.screen_manager = MDApp.get_running_app().root.ids.screen_manager
        self.meal_id = meal_id
        self.asc_obj_id_list = [i.id for i in s.query(Association).filter(Association.meal_id == self.meal_id).all()]
        self.all_ingredient_id_list = [i.id for i in s.query(Ingredient).all()]
        s.close()

    def remove_display_screen(self):
        self.screen_manager.remove_widget(self.screen_manager.current_screen)

    def refresh_internal_ingredient_list(self):
        s = Session()
        self.asc_obj_id_list = [i.id for i in s.query(Association).filter(Association.meal_id == self.meal_id).all()]
        self.meal_ingredient_id_list = [i.ingredient_id for i in s.query(Association).filter(Association.meal_id == self.meal_id).all()]
        s.close()

    def refresh_display_ingredient_list(self):
        self.ids.meal_ingredient_list.clear_widgets()
        s = Session()
        for i in s.query(Association).filter(Association.meal_id == self.meal_id).all():
            s.add(i)
            Item = ThreeLineAvatarIconObjectListItem(
                    asc_obj_id=i.id,
                    meal_id=i.meal_id,
                    ingredient_id=i.ingredient_id,
                    text=i.ingredient.name,
                    secondary_text=f"{i.ingredient.calories * i.amount_numerator / 100 if i.ingredient.unit == 'gram' or i.ingredient.unit == 'ml' else round(i.ingredient.calories * i.amount_numerator / i.amount_denominator,2)} kcals",
                    tertiary_text=f"{i.amount_numerator if i.ingredient.unit == 'gram' or i.ingredient.unit == 'ml' else str(int(i.amount_numerator/i.amount_denominator))} {pretty(Rational(i.amount_numerator%i.amount_denominator,i.amount_denominator),use_unicode=True) if i.amount_numerator%i.amount_denominator != 0 else ''} {i.ingredient.unit}{'s' if (i.amount_numerator / i.amount_denominator != 1) else ''}",
                    on_release=self.open_meal_ingredient_options_dialog,
                )
            Icon = IconLeftWidget(
                icon=self.ing_icon_dict[i.ingredient.type],
                theme_text_color="Custom",
                text_color=self.ing_icon_color_dict[i.ingredient.type]
                )
            Item.add_widget(Icon)
            self.ids.meal_ingredient_list.add_widget(Item)
        Add_Item = OneLineIconListItem(
            text="Add Ingredient",
            on_release=self.open_add_meal_ingredient_dialog
        )
        Add_Item.add_widget(
            IconLeftWidget(
                icon="plus"
            )
        )
        self.ids.meal_ingredient_list.add_widget(Add_Item)
        s.close()

    def open_meal_ingredient_options_dialog(self, listitem):
        c = Meal_Ingredient_Options_Dialog(asc_obj_id=listitem.asc_obj_id,ing_name=listitem.text)
        self.popup_base_ing_opt = MDDialog(
            title=f"{listitem.text} Options",
            type="custom",
            size_hint=(.9, None),
            pos_hint={"center_x": .5, "center_y": .5},
            content_cls=c,
            radius=[20, 7, 20, 7]
        )
        c.display_meal_screen = self
        c.popup_base_ing_opt = self.popup_base_ing_opt
        self.popup_base_ing_opt.open()

    def open_add_meal_ingredient_dialog(self,junk):
        c = Add_Meal_Ingredient_Dialog(meal_id=self.meal_id,all_ingredient_id_list=self.all_ingredient_id_list)
        self.popup_base_add_ing = MDDialog(
            title="Add Ingredient",
            type="custom",
            size_hint=(.9, None),
            height=MDApp.get_running_app().root.height*.8,
            pos_hint={"center_x": .5, "center_y": .5},
            content_cls=c,
            radius=[20, 7, 20, 7]
        )
        c.refresh_and_sort_all_ingredients_list()
        c.display_meal_screen = self
        c.popup_base_add_ing = self.popup_base_add_ing
        self.popup_base_add_ing.open()

class Add_Meal_Ingredient_Dialog(MDBoxLayout):

    def __init__(self, meal_id, all_ingredient_id_list, *args, **kwargs):
        super(Add_Meal_Ingredient_Dialog, self).__init__(*args, **kwargs)
        self.all_ingredient_id_list = all_ingredient_id_list # should never change
        self.display_ingredient_id_list = all_ingredient_id_list        # is supposed to be modified based on the filter settings
        self.meal_id = meal_id                               # should never change
        s = Session()
        self.meal_name = s.query(Meal).filter(Meal.id == self.meal_id).first().name
        s.close()
        self.ing_icon_dict = {
            "All":"filter-variant",
            "Meat":"food-steak",
            "Fish":"fish",
            "Grains / Bread":"bread-slice-outline",
            "Dairy":"cheese",
            "Vegetable":"carrot",
            "Fruit":"food-apple-outline",
            "Nuts / Seeds":"peanut",
            "Oil / Fats":"bottle-tonic",
            "Condiment":"soy-sauce",
            "Spice":"shaker-outline"
        }
        self.ing_icon_color_dict = {
            "All":(1,1,1,1),
            "Meat":(.39,.24,.04,1),
            "Fish":(1,.61,.39,1),
            "Grains / Bread":(1,.67,.35,1),
            "Dairy":(1,.78,.24,1),
            "Vegetable":(1,.55,.1,1),
            "Fruit":(.9,.16,0,1),
            "Nuts / Seeds":(.78,.53,0,1),
            "Oil / Fats":(.96,.75,0,1),
            "Condiment":(.78,.69,.24,1),
            "Spice":(.95,.95,.99,1)
        }

    def cancel(self):
        self.popup_base_add_ing.dismiss()

    def open_filter_dropdown(self):
        self.choices_filter = [
            {
                "viewclass": "OneLineIconListItem",
                "text": "All",
                "icon":"filter-variant",
                "height": dp(56),
                "on_release": lambda x="filter-variant",y="All": self.set_filter_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Meat",
                "icon": "food-steak",
                "height": dp(56),
                "on_release": lambda x="food-steak",y="Meat": self.set_filter_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Fish",
                "icon": "fish",
                "height": dp(56),
                "on_release": lambda x="fish",y="Fish": self.set_filter_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Grains / Bread",
                "icon": "bread-slice-outline",
                "height": dp(56),
                "on_release": lambda x="bread-slice-outline",y="Grains / Bread": self.set_filter_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Dairy",
                "icon": "cheese",
                "height": dp(56),
                "on_release": lambda x="cheese",y="Dairy": self.set_filter_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Vegetable",
                "icon": "carrot",
                "height": dp(56),
                "on_release": lambda x="carrot",y="Vegetable": self.set_filter_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Fruit",
                "icon": "food-apple-outline",
                "height": dp(56),
                "on_release": lambda x="food-apple-outline",y="Fruit": self.set_filter_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Nuts / Seeds",
                "icon": "peanut",
                "height": dp(56),
                "on_release": lambda x="peanut",y="Nuts / Seeds": self.set_filter_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Oil / Fats",
                "icon": "bottle-tonic",
                "height": dp(56),
                "on_release": lambda x="bottle-tonic",y="Oil / Fats": self.set_filter_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Condiment",
                "icon": "soy-sauce",
                "height": dp(56),
                "on_release": lambda x="soy-sauce",y="Condiment": self.set_filter_icon(x,y)
            },
            {
                "viewclass": "OneLineIconListItem",
                "text": "Spice",
                "icon": "shaker-outline",
                "height": dp(56),
                "on_release": lambda x="shaker-outline",y="Spice": self.set_filter_icon(x,y)
            },
        ]
        self.menu_list_type = MDDropdownMenu(
            caller=self.ids.filter,
            items=self.choices_filter,
            position="auto",
            width_mult=4
        )
        self.menu_list_type.open()

    def set_filter_icon(self, icon, text):
        self.ids.filter.icon = icon
        self.ids.filter.text_color = self.ing_icon_color_dict[text]
        self.ids.filter.text = text
        self.refresh_internal_list()
        self.menu_list_type.dismiss()

    def refresh_and_sort_all_ingredients_list(self): # this should only be called when an ingredient is added or deleted and on initialization to sort the list
        s = Session()
        self.all_ingredient_id_and_stats_list_sorted = [i for i in sorted([(i.id,i.name,i.unit,i.divisible_by,i.calories,i.type) for i in s.query(Ingredient).all()],key=lambda x: x[5])]
        s.close()
        self.refresh_internal_list()

    def refresh_internal_list(self):
        self.ing_type = self.ids.filter.text if self.ids else "All"
        if self.ing_type == "All":
            self.display_ingredient_id_and_stats_list = self.all_ingredient_id_and_stats_list_sorted
        else:
            self.display_ingredient_id_and_stats_list = list(filter(lambda x: x[5] == self.ing_type,self.all_ingredient_id_and_stats_list_sorted))
        self.refresh_display_list()

    def refresh_display_list(self):
        self.ing_search = self.ids.ing_search.text
        self.ids.ingredients_display_list.clear_widgets()
        for i in self.display_ingredient_id_and_stats_list:
            if self.ing_search.lower() in i[1].lower():
                Item = ThreeLineAvatarIconObjectListItem(
                    ingredient_id=i[0],
                    meal_id=self.meal_id,
                    text=i[1],
                    ing_unit=i[2],
                    divisible_by=i[3],
                    secondary_text=f"{i[4]} kcals",
                    tertiary_text=f"per {'100' if i[2] =='gram' or i[2] =='ml' else ''} {i[2]}{'s' if i[2] == 'gram' or i[2] == 'ml' else ''}",
                    on_release=self.open_ingredient_amount_input_dialog,
                )
                Icon = IconLeftWidget(
                    icon=self.ing_icon_dict[i[5]],
                    theme_text_color="Custom",
                    text_color=self.ing_icon_color_dict[i[5]],
                    )
                Item.add_widget(Icon)
                self.ids.ingredients_display_list.add_widget(Item)
    
    def open_ingredient_amount_input_dialog(self,listitem):
        s = Session()
        asc_obj = s.query(Association).filter(Association.ingredient_id==listitem.ingredient_id,Association.meal_id==listitem.meal_id).first()
        if asc_obj:
            asc_obj_id = asc_obj.id
            s.close()
            c = Ingredient_Is_Already_In_Meal_Dialog(listitem=listitem,
                                                     asc_obj_id=asc_obj_id)
            self.popup_ingredient_is_already_in_meal = MDDialog(
                title=f"{listitem.text} is already in {self.meal_name}, would you like to change the amount?",
                type="custom",
                size_hint=(.9, None),
                height=MDApp.get_running_app().root.height*.8,
                pos_hint={"center_x": .5, "center_y": .5},
                content_cls=c,
                radius=[20, 7, 20, 7]
            )
            c.display_meal_screen = self.display_meal_screen
            c.popup_ingredient_is_already_in_meal = self.popup_ingredient_is_already_in_meal
            self.popup_ingredient_is_already_in_meal.open()
        else:
            s.close()
            if listitem.ing_unit == "gram" or listitem.ing_unit == "ml":
                c = Add_Ing_To_Meal_Unit_Gram_Ml_Dialog(caller_already_exists=False,
                                                        caller_change=False,
                                                        asc_obj_id=None,
                                                        ingredient_id=listitem.ingredient_id,
                                                        meal_id=listitem.meal_id)
                self.popup_add_ing_gram_ml = MDDialog(
                    title=f"Add {listitem.text}",
                    type="custom",
                    size_hint=(.9, None),
                    height=MDApp.get_running_app().root.height*.8,
                    pos_hint={"center_x": .5, "center_y": .5},
                    content_cls=c,
                    radius=[20, 7, 20, 7]
                )
                c.display_meal_screen = self.display_meal_screen
                c.popup_add_ing_gram_ml = self.popup_add_ing_gram_ml
                c.ids.unit_label.text = listitem.ing_unit
                c.ids.ing_stats_label.text = listitem.text
                c.ids.meal_stats_label.text = self.meal_name
                c.refresh_stats()
                c.confirm_button_check_validity()
                self.popup_add_ing_gram_ml.open()
                ic("yet to be added")
            else:
                if listitem.divisible_by > 1:
                    c = Add_Ing_To_Meal_Unit_Piece_Divisible_Dialog(caller_already_exists=False,
                                                                    caller_change=False,
                                                                    asc_obj_id=None,
                                                                    ingredient_id=listitem.ingredient_id,
                                                                    meal_id=listitem.meal_id)
                    self.popup_add_ing_piece_divisible = MDDialog(
                        title=f"Add {listitem.text}",
                        type="custom",
                        size_hint=(.9, None),
                        height=MDApp.get_running_app().root.height*.8,
                        pos_hint={"center_x": .5, "center_y": .5},
                        content_cls=c,
                        radius=[20, 7, 20, 7]
                    )
                    c.display_meal_screen = self.display_meal_screen
                    c.popup_add_ing_piece_divisible = self.popup_add_ing_piece_divisible
                    c.ids.pieces_amount_label.text = "0"
                    c.ids.pieces_amount_label.number = 0
                    c.ids.slices_amount_label.numerator = 0
                    c.ids.slices_amount_label.denominator = listitem.divisible_by
                    c.ids.ing_stats_label.text = listitem.text
                    c.ids.meal_stats_label.text = self.meal_name
                    c.refresh_stats()
                    c.confirm_button_check_validity()
                    self.popup_add_ing_piece_divisible.open()
                else:
                    c = Add_Ing_To_Meal_Unit_Piece_Indivisible_Dialog(caller_already_exists=False,
                                                                      caller_change=False,
                                                                      asc_obj_id=None,
                                                                      ingredient_id=listitem.ingredient_id,
                                                                      meal_id=listitem.meal_id)
                    self.popup_add_ing_piece_indivisible = MDDialog(
                        title=f"Add {listitem.text}",
                        type="custom",
                        size_hint=(.9, None),
                        height=MDApp.get_running_app().root.height*.8,
                        pos_hint={"center_x": .5, "center_y": .5},
                        content_cls=c,
                        radius=[20, 7, 20, 7]
                    )
                    c.display_meal_screen = self.display_meal_screen
                    c.popup_add_ing_piece_indivisible = self.popup_add_ing_piece_indivisible
                    c.ids.pieces_amount_label.text = "0"
                    c.ids.pieces_amount_label.number = 0
                    c.ids.ing_stats_label.text = listitem.text
                    c.ids.meal_stats_label.text = self.meal_name
                    c.refresh_stats()
                    c.confirm_button_check_validity()
                    self.popup_add_ing_piece_indivisible.open()

class Ingredient_Is_Already_In_Meal_Dialog(MDBoxLayout):

    def __init__(self, listitem, asc_obj_id, *args, **kwargs):
        super(Ingredient_Is_Already_In_Meal_Dialog, self).__init__(*args, **kwargs)
        self.listitem = listitem
        self.asc_obj_id = asc_obj_id
        s = Session()
        asc_obj = s.query(Association).get(self.asc_obj_id)
        self.meal_name = asc_obj.meal.name
        self.amount_numerator = asc_obj.amount_numerator
        self.amount_denominator = asc_obj.amount_denominator
        s.close()

    def cancel(self):
        self.popup_ingredient_is_already_in_meal.dismiss()
    
    def change_amount(self):
        if self.listitem.ing_unit == "gram" or self.listitem.ing_unit == "ml":
            c = Add_Ing_To_Meal_Unit_Gram_Ml_Dialog(caller_already_exists=True,
                                                    caller_change=False,
                                                    asc_obj_id=self.asc_obj_id,
                                                    ingredient_id=self.listitem.ingredient_id,
                                                    meal_id=self.listitem.meal_id)
            self.popup_add_ing_gram_ml = MDDialog(
                title=f"Change amount of {self.listitem.text}",
                type="custom",
                size_hint=(.9, None),
                height=MDApp.get_running_app().root.height*.8,
                pos_hint={"center_x": .5, "center_y": .5},
                content_cls=c,
                radius=[20, 7, 20, 7]
            )
            c.popup_ingredient_is_already_in_meal = self.popup_ingredient_is_already_in_meal
            c.display_meal_screen = self.display_meal_screen
            c.popup_add_ing_gram_ml = self.popup_add_ing_gram_ml
            c.ids.amount_input.text = str(self.amount_numerator)
            c.ids.unit_label.text = self.listitem.ing_unit
            c.ids.ing_stats_label.text = self.listitem.text
            c.ids.meal_stats_label.text = self.meal_name
            c.refresh_stats()
            c.confirm_button_check_validity()
            self.popup_add_ing_gram_ml.open()
            ic("yet to be added")
        else:
            if self.listitem.divisible_by > 1:
                c = Add_Ing_To_Meal_Unit_Piece_Divisible_Dialog(caller_already_exists=True,
                                                                caller_change=False,
                                                                asc_obj_id=self.asc_obj_id,
                                                                ingredient_id=self.listitem.ingredient_id,
                                                                meal_id=self.listitem.meal_id)
                self.popup_add_ing_piece_divisible = MDDialog(
                    title=f"Change amount of {self.listitem.text}",
                    type="custom",
                    size_hint=(.9, None),
                    height=MDApp.get_running_app().root.height*.8,
                    pos_hint={"center_x": .5, "center_y": .5},
                    content_cls=c,
                    radius=[20, 7, 20, 7]
                )
                c.popup_ingredient_is_already_in_meal = self.popup_ingredient_is_already_in_meal
                c.display_meal_screen = self.display_meal_screen
                c.popup_add_ing_piece_divisible = self.popup_add_ing_piece_divisible
                c.ids.pieces_amount_label.text = str(int(self.amount_numerator / self.listitem.divisible_by))
                c.ids.pieces_amount_label.number = int(self.amount_numerator / self.listitem.divisible_by)
                c.ids.slices_amount_label.numerator = int(self.amount_numerator % self.listitem.divisible_by)
                c.ids.slices_amount_label.denominator = self.listitem.divisible_by
                c.ids.ing_stats_label.text = self.listitem.text
                c.ids.meal_stats_label.text = self.meal_name
                c.refresh_stats()
                c.confirm_button_check_validity()
                self.popup_add_ing_piece_divisible.open()
            else:
                c = Add_Ing_To_Meal_Unit_Piece_Indivisible_Dialog(caller_already_exists=True,
                                                                  caller_change=False,
                                                                  asc_obj_id=self.asc_obj_id,
                                                                  ingredient_id=self.listitem.ingredient_id,
                                                                  meal_id=self.listitem.meal_id)
                self.popup_add_ing_piece_indivisible = MDDialog(
                    title=f"Change amount of {self.listitem.text}",
                    type="custom",
                    size_hint=(.9, None),
                    height=MDApp.get_running_app().root.height*.8,
                    pos_hint={"center_x": .5, "center_y": .5},
                    content_cls=c,
                    radius=[20, 7, 20, 7]
                )
                c.popup_ingredient_is_already_in_meal = self.popup_ingredient_is_already_in_meal
                c.display_meal_screen = self.display_meal_screen
                c.popup_add_ing_piece_indivisible = self.popup_add_ing_piece_indivisible
                c.ids.pieces_amount_label.text = str(self.amount_numerator)
                c.ids.pieces_amount_label.number = self.amount_numerator
                c.ids.ing_stats_label.text = self.listitem.text
                c.ids.meal_stats_label.text = self.meal_name
                c.refresh_stats()
                c.confirm_button_check_validity()
                self.popup_add_ing_piece_indivisible.open()

class Add_Ing_To_Meal_Unit_Piece_Divisible_Dialog(MDBoxLayout):

    def __init__(self, asc_obj_id, ingredient_id, meal_id, caller_already_exists:bool, caller_change:bool, *args, **kwargs):
        super(Add_Ing_To_Meal_Unit_Piece_Divisible_Dialog, self).__init__(*args, **kwargs)
        self.asc_obj_id = asc_obj_id
        self.caller_already_exists = caller_already_exists
        self.caller_change = caller_change
        self.ingredient_id = ingredient_id
        self.meal_id = meal_id
        s = Session()
        self.amount_numerator = s.query(Association).get(self.asc_obj_id).amount_numerator if self.caller_already_exists or self.caller_change else None
        self.amount_denominator = s.query(Association).get(self.asc_obj_id).amount_denominator if self.caller_already_exists or self.caller_change else None

    def cancel(self):
        if self.caller_already_exists:
            self.popup_add_ing_piece_divisible.dismiss()
            self.popup_ingredient_is_already_in_meal.dismiss()
        elif self.caller_change:
            self.popup_add_ing_piece_divisible.dismiss()
            self.popup_base_ing_opt.dismiss()
        else:
            self.popup_add_ing_piece_divisible.dismiss()

    def confirm_button_check_validity(self):
        if self.ids.pieces_amount_label.number == 0 and self.ids.slices_amount_label.numerator == 0:
            self.ids.confirm_button.disabled = True
        else:
            self.ids.confirm_button.disabled = False

    def increment_pieces(self):
        self.ids.pieces_amount_label.number += 1
        self.confirm_button_check_validity()

    def decrement_pieces(self):
        if self.ids.pieces_amount_label.number > 0:
            self.ids.pieces_amount_label.number -= 1
        self.confirm_button_check_validity()

    def increment_slices(self):
        if self.ids.slices_amount_label.numerator < self.ingredient.divisible_by - 1:
            self.ids.slices_amount_label.numerator += 1
            self.confirm_button_check_validity()
        else:
            self.ids.slices_amount_label.numerator = 0
            self.increment_pieces()

    def decrement_slices(self):
        if self.ids.slices_amount_label.numerator > 0:
            self.ids.slices_amount_label.numerator -= 1
            self.confirm_button_check_validity()
        elif self.ids.slices_amount_label.numerator == 0 and self.ids.pieces_amount_label.number != 0:
            self.ids.slices_amount_label.numerator = self.ingredient.divisible_by - 1
            self.decrement_pieces()

    def refresh_stats(self):
        s = Session()
        self.ingredient = s.query(Ingredient).get(self.ingredient_id)
        self.meal = s.query(Meal).get(self.meal_id)
        self.ids.ing_calories.text = str(round(self.ingredient.calories * self.ids.pieces_amount_label.number + self.ingredient.calories * self.ids.slices_amount_label.numerator / self.ingredient.divisible_by,2))
        self.ids.ing_fats.text = f"{str(round(self.ingredient.fats * self.ids.pieces_amount_label.number + self.ingredient.fats * self.ids.slices_amount_label.numerator / self.ingredient.divisible_by,2))} g"
        self.ids.ing_carbohydrates.text = f"{str(round(self.ingredient.carbohydrates * self.ids.pieces_amount_label.number + self.ingredient.carbohydrates * self.ids.slices_amount_label.numerator / self.ingredient.divisible_by,2))} g"
        self.ids.ing_proteins.text = f"{str(round(self.ingredient.proteins * self.ids.pieces_amount_label.number + self.ingredient.proteins * self.ids.slices_amount_label.numerator / self.ingredient.divisible_by,2))} g"
        if self.caller_already_exists or self.caller_change:
            self.ids.meal_calories.text = str(round((self.meal.calories - self.ingredient.calories * self.amount_numerator / self.amount_denominator) + self.ingredient.calories * self.ids.pieces_amount_label.number + self.ingredient.calories * self.ids.slices_amount_label.numerator / self.ingredient.divisible_by,2))
            self.ids.meal_fats.text = f"{str(round((self.meal.fats - self.ingredient.fats * self.amount_numerator / self.amount_denominator) + self.ingredient.fats * self.ids.pieces_amount_label.number + self.ingredient.fats * self.ids.slices_amount_label.numerator / self.ingredient.divisible_by,2))} g"
            self.ids.meal_carbohydrates.text = f"{str(round((self.meal.carbohydrates - self.ingredient.carbohydrates * self.amount_numerator / self.amount_denominator) + self.ingredient.carbohydrates * self.ids.pieces_amount_label.number + self.ingredient.carbohydrates * self.ids.slices_amount_label.numerator / self.ingredient.divisible_by,2))} g"
            self.ids.meal_proteins.text = f"{str(round((self.meal.proteins - self.ingredient.proteins * self.amount_numerator / self.amount_denominator) + self.ingredient.proteins * self.ids.pieces_amount_label.number + self.ingredient.proteins * self.ids.slices_amount_label.numerator / self.ingredient.divisible_by,2))} g"
        else:
            self.ids.meal_calories.text = str(round(self.meal.calories + self.ingredient.calories * self.ids.pieces_amount_label.number + self.ingredient.calories * self.ids.slices_amount_label.numerator / self.ingredient.divisible_by,2))
            self.ids.meal_fats.text = f"{str(round(self.meal.fats + self.ingredient.fats * self.ids.pieces_amount_label.number + self.ingredient.fats * self.ids.slices_amount_label.numerator / self.ingredient.divisible_by,2))} g"
            self.ids.meal_carbohydrates.text = f"{str(round(self.meal.carbohydrates + self.ingredient.carbohydrates * self.ids.pieces_amount_label.number + self.ingredient.carbohydrates * self.ids.slices_amount_label.numerator / self.ingredient.divisible_by,2))} g"
            self.ids.meal_proteins.text = f"{str(round(self.meal.proteins + self.ingredient.proteins * self.ids.pieces_amount_label.number + self.ingredient.proteins * self.ids.slices_amount_label.numerator / self.ingredient.divisible_by,2))} g"
        s.close()
    
    def add_to_meal(self):
        ic("add to meal")
        s = Session()
        if self.caller_already_exists or self.caller_change:
            asc_obj = s.query(Association).get(self.asc_obj_id)
            asc_obj.amount_numerator = self.ids.pieces_amount_label.number * self.ingredient.divisible_by + self.ids.slices_amount_label.numerator
            asc_obj.amount_denominator = self.ingredient.divisible_by
        else:
            s.add(Association(
                meal = s.query(Meal).get(self.meal_id),
                ingredient = s.query(Ingredient).get(self.ingredient_id),
                amount_numerator = self.ids.pieces_amount_label.number * self.ingredient.divisible_by + self.ids.slices_amount_label.numerator,
                amount_denominator = self.ingredient.divisible_by
                )
            )
        s.commit()
        s.close()
        self.display_meal_screen.refresh_internal_ingredient_list()
        self.display_meal_screen.refresh_display_ingredient_list()
        self.cancel()

class Add_Ing_To_Meal_Unit_Piece_Indivisible_Dialog(MDBoxLayout):

    def __init__(self, asc_obj_id, ingredient_id, meal_id, caller_already_exists:bool, caller_change:bool, *args, **kwargs):
        super(Add_Ing_To_Meal_Unit_Piece_Indivisible_Dialog, self).__init__(*args, **kwargs)
        self.asc_obj_id = asc_obj_id
        self.caller_already_exists = caller_already_exists
        self.caller_change = caller_change
        self.ingredient_id = ingredient_id
        self.meal_id = meal_id
        s = Session()
        self.amount = s.query(Association).get(self.asc_obj_id).amount_numerator if self.caller_already_exists or self.caller_change else None
        s.close()

    def cancel(self):
        if self.caller_already_exists:
            self.popup_add_ing_piece_indivisible.dismiss()
            self.popup_ingredient_is_already_in_meal.dismiss()
        elif self.caller_change:
            self.popup_add_ing_piece_indivisible.dismiss()
            self.popup_base_ing_opt.dismiss()
        else:
            self.popup_add_ing_piece_indivisible.dismiss()

    def confirm_button_check_validity(self):
        if self.ids.pieces_amount_label.number > 0:
            self.ids.confirm_button.disabled = False
        else:
            self.ids.confirm_button.disabled = True

    def increment_pieces(self):
        self.ids.pieces_amount_label.number += 1
        self.confirm_button_check_validity()

    def decrement_pieces(self):
        if self.ids.pieces_amount_label.number > 0:
            self.ids.pieces_amount_label.number -= 1
            self.confirm_button_check_validity()

    def refresh_stats(self):
        s = Session()
        self.ingredient = s.query(Ingredient).get(self.ingredient_id)
        self.meal = s.query(Meal).get(self.meal_id)
        self.ids.ing_calories.text = str(round(self.ingredient.calories * self.ids.pieces_amount_label.number,2))
        self.ids.ing_fats.text = f"{str(round(self.ingredient.fats * self.ids.pieces_amount_label.number,2))} g"
        self.ids.ing_carbohydrates.text = f"{str(round(self.ingredient.carbohydrates * self.ids.pieces_amount_label.number,2))} g"
        self.ids.ing_proteins.text = f"{str(round(self.ingredient.proteins * self.ids.pieces_amount_label.number,2))} g"
        if self.caller_already_exists or self.caller_change:
            self.ids.meal_calories.text = str(round((self.meal.calories - self.ingredient.calories * self.amount) + self.ingredient.calories * self.ids.pieces_amount_label.number,2))
            self.ids.meal_fats.text = f"{str(round((self.meal.fats - self.ingredient.fats * self.amount) + self.ingredient.fats * self.ids.pieces_amount_label.number,2))} g"
            self.ids.meal_carbohydrates.text = f"{str(round((self.meal.carbohydrates - self.ingredient.carbohydrates * self.amount) + self.ingredient.carbohydrates * self.ids.pieces_amount_label.number,2))} g"
            self.ids.meal_proteins.text = f"{str(round((self.meal.proteins - self.ingredient.proteins * self.amount) + self.ingredient.proteins * self.ids.pieces_amount_label.number,2))} g"
        else:
            self.ids.meal_calories.text = str(round(self.meal.calories + self.ingredient.calories * self.ids.pieces_amount_label.number,2))
            self.ids.meal_fats.text = f"{str(round(self.meal.fats + self.ingredient.fats * self.ids.pieces_amount_label.number,2))} g"
            self.ids.meal_carbohydrates.text = f"{str(round(self.meal.carbohydrates + self.ingredient.carbohydrates * self.ids.pieces_amount_label.number,2))} g"
            self.ids.meal_proteins.text = f"{str(round(self.meal.proteins + self.ingredient.proteins * self.ids.pieces_amount_label.number,2))} g"
        s.close()
    
    def add_to_meal(self):
        ic("add to meal")
        s = Session()
        if self.caller_already_exists or self.caller_change: # could integrate check if amount has changed or not if no change is made just dismiss
            s.query(Association).get(self.asc_obj_id).amount_numerator = self.ids.pieces_amount_label.number
        else:
            s.add(Association(
                meal = s.query(Meal).get(self.meal_id),
                ingredient = s.query(Ingredient).get(self.ingredient_id),
                amount_numerator = self.ids.pieces_amount_label.number,
                amount_denominator = 1   
                )
            )
        s.commit()
        s.close()
        self.display_meal_screen.refresh_internal_ingredient_list()
        self.display_meal_screen.refresh_display_ingredient_list()
        self.cancel()

class Add_Ing_To_Meal_Unit_Gram_Ml_Dialog(MDBoxLayout):
    
    def __init__(self, asc_obj_id:int, ingredient_id:int, meal_id:int, caller_already_exists:bool, caller_change:bool, *args, **kwargs):
        super(Add_Ing_To_Meal_Unit_Gram_Ml_Dialog, self).__init__(*args, **kwargs)
        self.asc_obj_id = asc_obj_id
        self.caller_already_exists = caller_already_exists
        self.caller_change = caller_change
        self.ingredient_id = ingredient_id
        self.meal_id = meal_id
        s = Session()
        self.amount = s.query(Association).get(self.asc_obj_id).amount_numerator if self.caller_already_exists or self.caller_change else None
        s.close()
    
    def cancel(self):
        if self.caller_already_exists:
            self.popup_add_ing_gram_ml.dismiss()
            self.popup_ingredient_is_already_in_meal.dismiss()
        elif self.caller_change:
            self.popup_add_ing_gram_ml.dismiss()
            self.popup_base_ing_opt.dismiss()
        else:
            self.popup_add_ing_gram_ml.dismiss()

    def confirm_button_check_validity(self):
        if self.ids.amount_input.text == "" or self.ids.amount_input.text == "0":
            self.ids.confirm_button.disabled = True
        else:
            self.ids.confirm_button.disabled = False

    def refresh_stats(self):
        s = Session()
        self.ingredient = s.query(Ingredient).get(self.ingredient_id) # another exception where I use the ingredient object itself # Optimization == get all the necessary stats on initialization
        self.meal = s.query(Meal).get(self.meal_id)
        self.ids.ing_calories.text = str(round(self.ingredient.calories * int(self.ids.amount_input.text if self.ids.amount_input.text.isdigit() else 0) / 100,2))
        self.ids.ing_fats.text = f"{str(round(self.ingredient.fats * int(self.ids.amount_input.text if self.ids.amount_input.text.isdigit() else 0) / 100,2))} g"
        self.ids.ing_carbohydrates.text = f"{str(round(self.ingredient.carbohydrates * int(self.ids.amount_input.text if self.ids.amount_input.text.isdigit() else 0) / 100,2))} g"
        self.ids.ing_proteins.text = f"{str(round(self.ingredient.proteins * int(self.ids.amount_input.text if self.ids.amount_input.text.isdigit() else 0) / 100,2))} g"
        if self.caller_already_exists or self.caller_change:
            self.ids.meal_calories.text = str(round((self.meal.calories - self.ingredient.calories * self.amount / 100) + self.ingredient.calories * int(self.ids.amount_input.text if self.ids.amount_input.text.isdigit() else 0) / 100,2))
            self.ids.meal_fats.text = f"{str(round((self.meal.fats - self.ingredient.fats * self.amount / 100) + self.ingredient.fats * int(self.ids.amount_input.text if self.ids.amount_input.text.isdigit() else 0) / 100,2))} g"
            self.ids.meal_carbohydrates.text = f"{str(round((self.meal.carbohydrates - self.ingredient.carbohydrates * self.amount / 100) + self.ingredient.carbohydrates * int(self.ids.amount_input.text if self.ids.amount_input.text.isdigit() else 0) / 100,2))} g"
            self.ids.meal_proteins.text = f"{str(round((self.meal.proteins - self.ingredient.proteins * self.amount / 100) + self.ingredient.proteins * int(self.ids.amount_input.text if self.ids.amount_input.text.isdigit() else 0) / 100,2))} g"
        else:
            self.ids.meal_calories.text = str(round(self.meal.calories + self.ingredient.calories * int(self.ids.amount_input.text if self.ids.amount_input.text.isdigit() else 0) / 100,2))
            self.ids.meal_fats.text = f"{str(round(self.meal.fats + self.ingredient.fats * int(self.ids.amount_input.text if self.ids.amount_input.text.isdigit() else 0) / 100,2))} g"
            self.ids.meal_carbohydrates.text = f"{str(round(self.meal.carbohydrates + self.ingredient.carbohydrates * int(self.ids.amount_input.text if self.ids.amount_input.text.isdigit() else 0) / 100,2))} g"
            self.ids.meal_proteins.text = f"{str(round(self.meal.proteins + self.ingredient.proteins * int(self.ids.amount_input.text if self.ids.amount_input.text.isdigit() else 0) / 100,2))} g"
        s.close()

    def add_to_meal_button_check_validity(self):
        if int(self.ids.amount_input.text if self.ids.amount_input.text.isdigit() else 0) > 0:
            self.ids.add_to_meal_button.disabled = False
        else:
            self.ids.add_to_meal_button.disabled = True

    def add_to_meal(self):
        s = Session()
        if self.caller_already_exists or self.caller_change:
            s.query(Association).get(self.asc_obj_id).amount_numerator = int(self.ids.amount_input.text)
        else:
            s.add(
                Association(
                    meal=s.query(Meal).get(self.meal_id),
                    ingredient=s.query(Ingredient).get(self.ingredient_id),
                    amount_numerator=int(self.ids.amount_input.text),
                    amount_denominator=1
                )
            )
        s.commit()
        s.close()
        self.display_meal_screen.refresh_internal_ingredient_list()
        self.display_meal_screen.refresh_display_ingredient_list()
        self.cancel()

class Meal_Ingredient_Options_Dialog(MDBoxLayout):

    def __init__(self, asc_obj_id, ing_name, *args, **kwargs):
        super(Meal_Ingredient_Options_Dialog, self).__init__(*args, **kwargs)
        self.asc_obj_id = asc_obj_id
        s = Session()
        asc_obj = s.query(Association).get(self.asc_obj_id)
        self.meal_name = asc_obj.meal.name
        self.meal_id = asc_obj.meal.id
        self.ingredient_name = asc_obj.ingredient.name
        self.ingredient_unit = asc_obj.ingredient.unit
        self.ingredient_id = asc_obj.ingredient.id
        self.ingredient_divisible_by = asc_obj.ingredient.divisible_by
        self.amount_numerator = asc_obj.amount_numerator
        self.amount_denominator = asc_obj.amount_denominator
        s.close()

    def cancel(self):
        self.popup_base_ing_opt.dismiss()

    def open_change_amount_dialog(self):
        if self.ingredient_unit == "gram" or self.ingredient_unit == "ml":
            c = Add_Ing_To_Meal_Unit_Gram_Ml_Dialog(caller_change=True,
                                                    caller_already_exists=False,
                                                    asc_obj_id=self.asc_obj_id,
                                                    ingredient_id=self.ingredient_id,
                                                    meal_id=self.meal_id)
            self.popup_add_ing_gram_ml = MDDialog(
                title=f"Change amount of {self.ingredient_name}",
                type="custom",
                size_hint=(.9, None),
                height=MDApp.get_running_app().root.height*.8,
                pos_hint={"center_x": .5, "center_y": .5},
                content_cls=c,
                radius=[20, 7, 20, 7]
            )
            c.popup_base_ing_opt = self.popup_base_ing_opt
            c.display_meal_screen = self.display_meal_screen
            c.popup_add_ing_gram_ml = self.popup_add_ing_gram_ml
            c.ids.amount_input.text = str(self.amount_numerator)
            c.ids.unit_label.text = self.ingredient_unit
            c.ids.ing_stats_label.text = self.ingredient_name
            c.ids.meal_stats_label.text = self.meal_name
            c.refresh_stats()
            c.confirm_button_check_validity()
            self.popup_add_ing_gram_ml.open()
            ic("yet to be added")
        else:
            if self.ingredient_divisible_by > 1:
                c = Add_Ing_To_Meal_Unit_Piece_Divisible_Dialog(caller_change=True,
                                                                caller_already_exists=False,
                                                                asc_obj_id=self.asc_obj_id,
                                                                ingredient_id=self.ingredient_id,
                                                                meal_id=self.meal_id)
                self.popup_add_ing_piece_divisible = MDDialog(
                    title=f"Change amount of {self.ingredient_name}",
                    type="custom",
                    size_hint=(.9, None),
                    height=MDApp.get_running_app().root.height*.8,
                    pos_hint={"center_x": .5, "center_y": .5},
                    content_cls=c,
                    radius=[20, 7, 20, 7]
                )
                c.popup_base_ing_opt = self.popup_base_ing_opt
                c.display_meal_screen = self.display_meal_screen
                c.popup_add_ing_piece_divisible = self.popup_add_ing_piece_divisible
                c.ids.pieces_amount_label.text = str(int(self.amount_numerator / self.ingredient_divisible_by))
                c.ids.pieces_amount_label.number = int(self.amount_numerator / self.ingredient_divisible_by)
                c.ids.slices_amount_label.numerator = int(self.amount_numerator % self.ingredient_divisible_by)
                c.ids.slices_amount_label.denominator = self.ingredient_divisible_by
                c.ids.ing_stats_label.text = self.ingredient_name
                c.ids.meal_stats_label.text = self.meal_name
                c.refresh_stats()
                c.confirm_button_check_validity()
                self.popup_add_ing_piece_divisible.open()
            else:
                c = Add_Ing_To_Meal_Unit_Piece_Indivisible_Dialog(caller_change=True,
                                                                  caller_already_exists=False,
                                                                  asc_obj_id=self.asc_obj_id,
                                                                  ingredient_id=self.ingredient_id,
                                                                  meal_id=self.meal_id)
                self.popup_add_ing_piece_indivisible = MDDialog(
                    title=f"Change amount of {self.ingredient_name}",
                    type="custom",
                    size_hint=(.9, None),
                    height=MDApp.get_running_app().root.height*.8,
                    pos_hint={"center_x": .5, "center_y": .5},
                    content_cls=c,
                    radius=[20, 7, 20, 7]
                )
                c.popup_base_ing_opt = self.popup_base_ing_opt
                c.display_meal_screen = self.display_meal_screen
                c.popup_add_ing_piece_indivisible = self.popup_add_ing_piece_indivisible
                c.ids.pieces_amount_label.text = str(self.amount_numerator)
                c.ids.pieces_amount_label.number = self.amount_numerator
                c.ids.ing_stats_label.text = self.ingredient_name
                c.ids.meal_stats_label.text = self.meal_name
                c.refresh_stats()
                c.confirm_button_check_validity()
                self.popup_add_ing_piece_indivisible.open()

    def open_delete_ingredient_dialog(self):
        c = Delete_Meal_Ingredient_Dialog(asc_obj_id=self.asc_obj_id)
        self.popup_delete_layer2 = MDDialog(
            title=f"Delete {self.ingredient_name} ?",
            type="custom",
            size_hint=(.9, None),
            pos_hint={"center_x": .5, "center_y": .5},
            content_cls=c,
            radius=[20, 7, 20, 7]
        )
        c.display_meal_screen = self.display_meal_screen
        c.popup_base_ing_opt = self.popup_base_ing_opt
        c.popup_delete_layer2 = self.popup_delete_layer2
        self.popup_delete_layer2.open()

class Delete_Meal_Ingredient_Dialog(MDBoxLayout):

    def __init__(self, asc_obj_id, *args, **kwargs):
        super(Delete_Meal_Ingredient_Dialog, self).__init__(*args, **kwargs)
        self.asc_obj_id = asc_obj_id
        self.screen_manager = MDApp.get_running_app().root.ids.screen_manager

    def cancel(self):
        self.popup_delete_layer2.dismiss()
    
    def delete(self):
        s = Session()
        s.delete(s.query(Association).get(self.asc_obj_id))
        s.commit()
        s.close()
        self.popup_base_ing_opt.dismiss()
        self.popup_delete_layer2.dismiss()
        self.display_meal_screen.refresh_internal_ingredient_list()
        self.display_meal_screen.refresh_display_ingredient_list()

# add_meal_to_database("Test",True,True,True,True,True,True)
# add_ingredient_to_meal("Test","Salami",100,1)
# add_ingredient_to_meal("Test","Salami Sticks",100,1)
# add_ingredient_to_meal("Test","Gouda",100,1)

s = Session()   
for i in s.query(Active).all():
    print(i) # Should only be one

for i in s.query(Settings).all():
    print
    (   
        i.name,
        i.breakfast,
        i.lunch,
        i.dinner,
        i.snack
    )
s.close()

class Meal_Plan_Item(MDBoxLayout):
    color = ListProperty([0,0,0,1])

    def __init__(self, meal_id, meal_type, pos_in_list, *args, **kwargs):
        super(Meal_Plan_Item, self).__init__(*args, **kwargs)
        self.meal_id = meal_id
        self.meal_type = meal_type
        self.pos_in_list = pos_in_list
        self.meal_plan_screen = MDApp.get_running_app().root.ids.meal_plan_screen
        self.meal_icon_color_dict = {
            "thermometer":(1,0,0,1),
            "snowflake":(0,.7,1,1),
            "candy-outline":(1,.4,.8,1),
            "french-fries":(1,.8,0,1),
            "egg-fried":(1,.5,0,1),
            "bowl-mix-outline":(1,.9,0,1),
            "pot-steam-outline":(.7,0,0.1),
            "fridge-outline":(0.4,.2,1),
            "cookie-outline":(.7,0,.15,1),
            "sausage":(.7,.2,.04,1)
        }
        self.color = [.5,.5,.5,1] if self.meal_type == "Breakfast" else [.2,.2,.2,1] if self.meal_type == "Lunch" else [.1,.1,.1,1] if self.meal_type == "Dinner" else [.05,.05,.05,1]
        self.get_stats()
        self.set_stats()
    
    def get_stats(self):
        s = Session()
        self.meal = s.get(Meal,self.meal_id)
        self.meal_name = self.meal.name
        self.sweet_savory = self.meal.sweet_savory
        self.hot_cold = self.meal.hot_cold
        self.meal_calories = self.meal.calories
        self.meal_fats = self.meal.fats
        self.meal_carbohydrates = self.meal.carbohydrates
        self.meal_proteins = self.meal.proteins
        s.close()
    
    def set_stats(self):
        self.ids.meal_name.text = self.meal_name
        self.ids.meal_calories.text = f"Calories:{'  '}{round(self.meal_calories,2)} kcals"
        self.ids.meal_fats.text = f"Fats:{'          '}{round(self.meal_fats,2)} g"
        self.ids.meal_carbohydrates.text = f"Carbs:{'       '}{round(self.meal_carbohydrates,2)} g"
        self.ids.meal_proteins.text = f"Proteins:{'  '}{round(self.meal_proteins,2)} g"
        self.ids.icon_meal_type.icon = ("egg-fried" if not self.hot_cold else "bowl-mix-outline") if self.meal_type == "Breakfast" else ("pot-steam-outline" if not self.hot_cold else "fridge-outline") if self.meal_type == "Lunch" or self.meal_type == "Dinner" else ("cookie-outline" if not self.sweet_savory else "sausage")
        self.ids.icon_meal_type.text_color = (self.meal_icon_color_dict["egg-fried"] if not self.hot_cold else self.meal_icon_color_dict["bowl-mix-outline"]) if self.meal_type == "Breakfast" else (self.meal_icon_color_dict["pot-steam-outline"] if not self.hot_cold else self.meal_icon_color_dict["fridge-outline"]) if self.meal_type == "Lunch" or self.meal_type == "Dinner" else (self.meal_icon_color_dict["cookie-outline"] if not self.sweet_savory else self.meal_icon_color_dict["sausage"])
        self.ids.icon_meal_sweet_savory.icon = ("candy-outline" if not self.sweet_savory else "french-fries") if self.meal_type == "Breakfast" else "candy-outline" if not self.sweet_savory else "french-fries" if self.meal_type == "Lunch" or self.meal_type == "Dinner" else "candy-outline" if not self.sweet_savory else "french-fries"
        self.ids.icon_meal_sweet_savory.text_color = (self.meal_icon_color_dict["candy-outline"] if not self.sweet_savory else self.meal_icon_color_dict["french-fries"]) if self.meal_type == "Breakfast" else (self.meal_icon_color_dict["candy-outline"] if not self.sweet_savory else self.meal_icon_color_dict["french-fries"]) if self.meal_type == "Lunch" or self.meal_type == "Dinner" else (self.meal_icon_color_dict["candy-outline"] if not self.sweet_savory else self.meal_icon_color_dict["french-fries"])
        self.ids.icon_meal_hot_cold.icon = ("thermometer" if not self.hot_cold else "snowflake") if self.meal_type == "Breakfast" else ("thermometer" if not self.hot_cold else "snowflake") if self.meal_type == "Lunch" or self.meal_type == "Dinner" else ("thermometer" if not self.hot_cold else "snowflake")
        self.ids.icon_meal_hot_cold.text_color =( self.meal_icon_color_dict["thermometer"] if not self.hot_cold else self.meal_icon_color_dict["snowflake"]) if self.meal_type == "Breakfast" else (self.meal_icon_color_dict["thermometer"] if not self.hot_cold else self.meal_icon_color_dict["snowflake"]) if self.meal_type == "Lunch" or self.meal_type == "Dinner" else (self.meal_icon_color_dict["thermometer"] if not self.hot_cold else self.meal_icon_color_dict["snowflake"])

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            for child in self.children:
                if child.collide_point(*touch.pos):
                    if child.name == "Box_Stats":
                        self.display_meal()
        return super().on_touch_down(touch)

    def display_meal(self):
        ic("display")
    
    def show_type(self):
        ic("type")
    
    def show_sweet_savory(self):
        ic("sweet_savory")
    
    def show_hot_cold(self):
        ic("hot_cold")
    
    def open_swap_options_dialog(self):
        ic("swap")
        c = Swap_Options_Dialog(meal_id=self.meal_id,
                                meal_type=self.meal_type)
        self.popup_base = MDDialog(
            title=f"Swap {self.meal_name}",
            type="custom",
            content_cls=c,
            radius=[20, 7, 20, 7]
        )
        c.logic = self
        c.popup_base = self.popup_base
        self.popup_base.open()


class Swap_Options_Dialog(MDBoxLayout):

    def __init__(self, meal_id, meal_type, *args, **kwargs):
        super(Swap_Options_Dialog, self).__init__(*args, **kwargs)
        self.current_meal_id = meal_id
        self.filter_conditions_input = [
            True if meal_type == "Breakfast" else False,
            True if meal_type == "Lunch" else False,
            True if meal_type == "Snack" else False,
            True if meal_type == "Dinner" else False
        ]
        self.filter_conditions = [
            Meal.breakfast == True,
            Meal.lunch == True,
            Meal.snack == True,
            Meal.dinner == True
        ]

    def cancel(self):
        self.popup_base.dismiss()

    def select_new_meal_random(self):
        ic("random")
        s = Session()
        new_meal_id_list = [i.id for i in s.query(Meal).filter(Meal.id != self.current_meal_id,*[self.filter_conditions[index] for index, i in enumerate(self.filter_conditions_input) if i]).all()]
        if new_meal_id_list:
            new_random_meal_id = rd.choice(new_meal_id_list)
            self.logic.meal_id = new_random_meal_id
            self.logic.meal_plan_screen.meal_plan_id_list[self.logic.pos_in_list[0]][self.logic.pos_in_list[1]] = new_random_meal_id
            self.logic.get_stats()
            self.logic.set_stats()
            self.popup_base.dismiss()
    def select_new_meal_manuel(self):
        ic("manuel")

class Meal_Plan_Screen(MDScreen):

    def __init__(self, *args, **kwargs):
        super(Meal_Plan_Screen,self).__init__(*args, **kwargs)
        self.internal_meal_plan = []
        s = Session()
        active_meal_plan = s.get(Meal_Plan,s.query(Active).first().meal_plan_id)
        if active_meal_plan:
            self.breakfast = active_meal_plan.breakfast
            self.lunch = active_meal_plan.lunch
            self.snack = active_meal_plan.snack
            self.dinner = active_meal_plan.dinner
            self.day_range = active_meal_plan.day_range
            self.meal_plan_id_list = eval(active_meal_plan.meal_plan_id_list)
            self.active_meal_plan_id = active_meal_plan.id
            self.active_meal_plan_name = active_meal_plan.name
        else:
            self.breakfast = False
            self.lunch = False
            self.snack = False
            self.dinner = False
            self.day_range = 0
            self.meal_plan_id_list = None
            self.active_meal_plan_id = None
        s.close()

    def open_meal_plan_settings(self):
        c = Meal_Plan_Settings_Dialog()
        self.popup_meal_plan_settings = MDDialog(
            title="Meal Plan Settings",
            type="custom",
            size_hint=(.9, None),
            pos_hint={"center_x": .5, "center_y": .5},
            content_cls=c,
            radius=[20, 7, 20, 7]
        )
        c.popup_meal_plan_settings = self.popup_meal_plan_settings
        s = Session()
        if self.active_meal_plan_id:
            active_meal_plan_settings = s.get(Meal_Plan,s.query(Active).first().meal_plan_id)
            c.ids.breakfast.active = active_meal_plan_settings.breakfast
            c.ids.lunch.active = active_meal_plan_settings.lunch
            c.ids.dinner.active = active_meal_plan_settings.dinner
            c.ids.snack.active = active_meal_plan_settings.snack
            c.ids.day_range.number = active_meal_plan_settings.day_range
        else:
            c.ids.breakfast.active = self.breakfast
            c.ids.lunch.active = self.lunch
            c.ids.dinner.active = self.snack
            c.ids.snack.active = self.dinner
            c.ids.day_range.number = self.day_range
        c.Meal_Plan_Screen = self
        s.close()
        self.popup_meal_plan_settings.open()

    def increment_page(self):
        if self.day_range - 1 > self.ids.meal_plan.page:
            self.ids.meal_plan.page += 1

    def decrement_page(self):
        if self.meal_plan.page > 0:
            self.ids.meal_plan.page -= 1

    def generate_button_check_validity(self):
        if any ([self.breakfast,self.lunch,self.snack,self.dinner]) and self.day_range > 0 and not self.ids.meal_plan.children:
            return True
        else:
            return False

    def erase_meal_plan(self):
        ic("delete_meal_plan")
        self.ids.meal_plan.clear_widgets()
        self.breakfast = False
        self.lunch = False
        self.snack = False
        self.dinner = False
        self.day_range = 0
        self.meal_plan_id_list = None
        self.active_meal_plan_id = None
        self.ids.meal_plan_title.title = "No current meal plan!"
        s = Session()
        s.query(Active).update({Active.meal_plan_id: None})
        s.commit()
        s.close()

    def open_save_meal_plan_options(self):
        if self.ids.meal_plan.children:
            if not self.active_meal_plan_id:
                ic("save_meal_plan")
                c = Save_Meal_Plan_Dialog()
                self.popup_base = MDDialog(
                    title="Save Meal Plan",
                    type="custom",
                    size_hint=(.9, None),
                    height=MDApp.get_running_app().root.height*.8,
                    pos_hint={"center_x": .5, "center_y": .5},
                    content_cls=c,
                    radius=[20, 7, 20, 7]
                )
                c.popup_base = self.popup_base
                c.breakfast = self.breakfast
                c.lunch = self.lunch
                c.snack = self.snack
                c.dinner = self.dinner
                c.day_range = self.day_range
                c.meal_plan_id_list = self.meal_plan_id_list
                self.popup_base.open()
            else:
                ic("save changes")
                # open popup to save changes or cancel
                c = Save_Meal_Plan_Changes_Dialog()
                self.popup_base = MDDialog(
                    title="Save Changes?",
                    type="custom",
                    size_hint=(.9, None),
                    pos_hint={"center_x": .5, "center_y": .5},
                    content_cls=c,
                    radius=[20, 7, 20, 7]
                )
                c.logic = self
                c.popup_base = self.popup_base
                self.popup_base.open()
    def set_meal_plan_settings(self):
        pass

    def load_meal_plan_settings(self,meal_plan_id):
        ic()
        s = Session()
        meal_plan = s.get(Meal_Plan,meal_plan_id)
        self.breakfast = meal_plan.breakfast
        self.lunch = meal_plan.lunch
        self.snack = meal_plan.snack
        self.dinner = meal_plan.dinner
        self.day_range = meal_plan.day_range
        self.meal_plan_id_list = eval(meal_plan.meal_plan_id_list)
        self.active_meal_plan_name = meal_plan.name
        self.active_meal_plan_id = meal_plan.id
        ic(self.meal_plan_id_list)
        self.display_meal_plan()
    
    def display_meal_plan(self):
        if self.active_meal_plan_id:
            self.ids.meal_plan.clear_widgets()
            self.ids.meal_plan_title.title = f"{self.active_meal_plan_name} : Day {self.ids.meal_plan.page + 1}"
            self.meal_type_list = [i for i in ["Breakfast" if self.breakfast else None, "Lunch" if self.lunch else None, "Snack" if self.snack else None, "Dinner" if self.dinner else None] if i]
            ic(self.meal_type_list)	
            for index, i in enumerate(self.meal_plan_id_list):
                self.ids.meal_plan.add_widget(MDScrollView(pos_hint={"center_x":.5}))
                self.ids.meal_plan.children[0].add_widget(Custom_MDGridLayout())
                self.ids.meal_plan.children[0].children[0].add_widget(Widget(size_hint_y=None,height=dp(25)))
                for index2,j in enumerate(i):
                    ic(j)
                    self.ids.meal_plan.children[0].children[0].add_widget(Meal_Plan_Item(meal_id=j,
                                                                                        meal_type=self.meal_type_list[index2],
                                                                                        pos_in_list=(index,index2)))
                    self.ids.meal_plan.children[0].children[0].add_widget(Widget(size_hint_y=None,height=dp(25)))
                self.ids.meal_plan.children[0].children[0].add_widget(Widget(size_hint_y=None,height=dp(100)))

    def open_load_meal_plan_dialog(self):
        ic("load_meal_plan")
        c = Load_Meal_Plan_Dialog()
        self.popup_base = MDDialog(
            title="Load Meal Plan",
            type="custom",
            size_hint=(.9, None),
            height=MDApp.get_running_app().root.height*.8,
            pos_hint={"center_x": .5, "center_y": .5},
            content_cls=c,
            radius=[20, 7, 20, 7]
        )
        c.popup_base = self.popup_base
        c.poup_base_logic = self
        c.refresh_display_list()
        self.popup_base.open()

    def generate_meal_plan(self):
        if self.generate_button_check_validity():
            ic("generate_meal_plan")
            s = Session() # I get the id lists in the function as to not miss when a meal is added or deleted
            self.breakfast_id_list = [i.id for i in s.query(Meal).filter(Meal.breakfast == True).all()]
            self.lunch_dinner_id_list = [i.id for i in s.query(Meal).filter(or_(Meal.lunch == True, Meal.dinner == True)).all()]
            self.snack_id_list = [i.id for i in s.query(Meal).filter(Meal.snack == True).all()]
            s.close()
            self.meal_plan_id_list = [[] for i in range(self.day_range)]
            for index, i in enumerate(range(self.day_range)):
                self.ids.meal_plan.add_widget(MDScrollView(pos_hint={"center_x":.5}))
                self.ids.meal_plan.children[0].add_widget(Custom_MDGridLayout())
                self.ids.meal_plan.children[0].children[0].add_widget(Widget(size_hint_y=None,height=dp(25)))
                if self.breakfast:
                    breakfast_choice = rd.choice(self.breakfast_id_list)
                    self.ids.meal_plan.children[0].children[0].add_widget(Meal_Plan_Item(meal_id=breakfast_choice,
                                                                                         meal_type="Breakfast",
                                                                                         pos_in_list=(index,0)))
                    self.meal_plan_id_list[index].append(breakfast_choice)
                    self.ids.meal_plan.children[0].children[0].add_widget(Widget(size_hint_y=None,height=dp(25)))
                if self.lunch:
                    lunch_choice = rd.choice(self.lunch_dinner_id_list)
                    self.ids.meal_plan.children[0].children[0].add_widget(Meal_Plan_Item(meal_id=lunch_choice,
                                                                                         meal_type="Lunch",
                                                                                         pos_in_list=(index,1 if self.breakfast else 0)))
                    self.meal_plan_id_list[index].append(lunch_choice)
                    self.ids.meal_plan.children[0].children[0].add_widget(Widget(size_hint_y=None,height=dp(25)))
                if self.snack:
                    snack_choice = rd.choice(self.snack_id_list)
                    self.ids.meal_plan.children[0].children[0].add_widget(Meal_Plan_Item(meal_id=snack_choice,
                                                                                         meal_type="Snack",
                                                                                         pos_in_list=(index,sum([1 for i in (self.breakfast,self.lunch) if i]))))
                    self.meal_plan_id_list[index].append(snack_choice)
                    self.ids.meal_plan.children[0].children[0].add_widget(Widget(size_hint_y=None,height=dp(25)))
                if self.dinner:
                    dinner_choice = rd.choice(self.lunch_dinner_id_list)
                    self.ids.meal_plan.children[0].children[0].add_widget(Meal_Plan_Item(meal_id=dinner_choice,
                                                                                         meal_type="Dinner",
                                                                                         pos_in_list=(index,sum([1 for i in (self.breakfast,self.lunch,self.snack) if i]))))
                    self.meal_plan_id_list[index].append(dinner_choice)
                self.ids.meal_plan.children[0].children[0].add_widget(Widget(size_hint_y=None,height=dp(100)))
            self.ids.meal_plan_title.title = "Day 1"
            ic(self.meal_plan_id_list)
    
    def adjust_calories(self):
        ic("adjust_calories")

    def display_page_title(self):
        if not self.active_meal_plan_id:
            self.ids.meal_plan_title.title = f"Day {self.ids.meal_plan.page + 1}"
        else:
            self.ids.meal_plan_title.title = f"{s.query(Meal_Plan).filter(Meal_Plan.id == self.active_meal_plan_id).first().name} : Day {self.ids.meal_plan.page + 1}"
class Save_Meal_Plan_Changes_Dialog(MDBoxLayout):

    def __init__(self, *args, **kwargs):
        super(Save_Meal_Plan_Changes_Dialog,self).__init__(*args, **kwargs)
    
    def cancel(self):
        self.popup_base.dismiss()
    
    def save_changes(self):
        s = Session()
        s.query(Meal_Plan).filter(Meal_Plan.id == self.logic.active_meal_plan_id).update({
            Meal_Plan.breakfast : self.logic.breakfast,
            Meal_Plan.lunch : self.logic.lunch,
            Meal_Plan.snack : self.logic.snack,
            Meal_Plan.dinner : self.logic.dinner,
            Meal_Plan.day_range : self.logic.day_range,
            Meal_Plan.meal_plan_id_list : str(self.logic.meal_plan_id_list)
            }
        )
        s.commit()
        s.close()
        self.popup_base.dismiss()
class Load_Meal_Plan_Dialog(MDBoxLayout):

    def __init__(self, *args, **kwargs):
        super(Load_Meal_Plan_Dialog,self).__init__(*args, **kwargs)
    
    def cancel(self):
        self.popup_base.dismiss()
    
    def refresh_display_list(self):
        self.search = self.ids.search.text
        self.ids.meal_plan_list.clear_widgets()
        s = Session()
        meal_plan_query = s.query(Meal_Plan).filter(Meal_Plan.name.like(f"%{self.search}%")).all()
        for i in meal_plan_query:
            self.ids.meal_plan_list.add_widget(ThreeLineValueListItem(
                text=i.name,
                meal_plan_id=i.id,
                secondary_text=f"{'Breakfast, ' if i.breakfast and any([i.lunch, i.snack, i.dinner]) else 'Breakfast' if i.breakfast else ''}{'Lunch, ' if i.lunch and any([i.snack, i.dinner]) else 'Lunch' if i.lunch else ''}{'Snack, ' if i.snack and i.dinner else 'Snack' if i.snack else ''}{'Dinner' if i.dinner else ''}",
                tertiary_text=f"placeholder, should display the calories per day",
                on_release=self.open_select_meal_plan_options_dialog
                )
            )
        s.close()

    def open_select_meal_plan_options_dialog(self,listitem):
        ic("load_meal_plan")
        c = Select_Meal_Plan_Options_Dialog(meal_plan_id=listitem.meal_plan_id)
        self.popup_select_meal_plan_options_dialog = MDDialog(
            title=f"{listitem.text} options",
            type="custom",
            size_hint=(.9, None),
            pos_hint={"center_x": .5, "center_y": .5},
            content_cls=c,
            radius=[20, 7, 20, 7]
        )
        c.popup_select_meal_plan_options_dialog = self.popup_select_meal_plan_options_dialog
        c.popup_base = self.popup_base
        c.load_meal_plan_dialog = self
        self.popup_select_meal_plan_options_dialog.open()

# class ThreeLineValueListItem(ThreeLineListItem):
#     meal_plan_id = NumericProperty(None)

class Select_Meal_Plan_Options_Dialog(MDBoxLayout):

    def __init__(self, meal_plan_id, *args, **kwargs):
        super(Select_Meal_Plan_Options_Dialog,self).__init__(*args, **kwargs)
        self.meal_plan_id = meal_plan_id
        self.meal_plan_screen = MDApp.get_running_app().root.ids.meal_plan_screen

    def delete(self):
        ic("delete")
        c = Delete_Meal_Plan_Dialog(meal_plan_id=self.meal_plan_id)
        self.popup_delete_layer3 = MDDialog(
            title="Delete meal plan?",
            type="custom",
            content_cls=c,
            pos_hint={"center_x": .5, "center_y": .5},
            radius=[20, 7, 20, 7]
        )
        c.popup_base = self.popup_base
        c.popup_delete_layer3 = self.popup_delete_layer3
        c.popup_select_meal_plan_options_dialog = self.popup_select_meal_plan_options_dialog
        c.load_meal_plan_dialog = self.load_meal_plan_dialog
        self.popup_delete_layer3.open()

    def load_meal_plan(self):
        ic("load_meal_plan")
        self.meal_plan_screen.load_meal_plan_settings(self.meal_plan_id)
        self.meal_plan_screen.display_page_title()
        s = Session()
        s.query(Active).update({Active.meal_plan_id:self.meal_plan_id})
        s.commit()
        s.close()
        self.popup_select_meal_plan_options_dialog.dismiss()
        self.popup_base.dismiss()


class Delete_Meal_Plan_Dialog(MDBoxLayout):

    def __init__(self, meal_plan_id, *args, **kwargs):
        super(Delete_Meal_Plan_Dialog,self).__init__(*args, **kwargs)
        self.meal_plan_id = meal_plan_id
        self.meal_plan_screen = MDApp.get_running_app().root.ids.meal_plan_screen

    def cancel(self):
        self.popup_delete_layer3.dismiss()

    def delete(self):
        s = Session()
        meal_plan_to_delete = s.get(Meal_Plan,self.meal_plan_id)
        s.delete(meal_plan_to_delete)
        s.commit()
        s.close()
        self.load_meal_plan_dialog.refresh_display_list()
        if self.meal_plan_id == s.query(Active).first().meal_plan_id:
            self.meal_plan_screen.erase_meal_plan()
            s.commit()
            s.close()
        self.popup_delete_layer3.dismiss()
        self.popup_select_meal_plan_options_dialog.dismiss()

class Save_Meal_Plan_Dialog(MDBoxLayout):

    def __init__(self, *args, **kwargs):
        super(Save_Meal_Plan_Dialog,self).__init__(*args, **kwargs)
        self.meal_plan_screen = MDApp.get_running_app().root.ids.meal_plan_screen
    def cancel(self):
        self.popup_base.dismiss()

    def check_save_button_validity(self):
        if self.ids.meal_plan_name.text == "":
            self.ids.safe_button.disabled = True
        else:
            self.ids.safe_button.disabled = False

    def save_meal_plan(self):
        s = Session()
        meal_plan_query = s.query(Meal_Plan).filter(Meal_Plan.name == self.ids.meal_plan_name.text).first()
        if meal_plan_query:
            if not meal_plan_query.id == s.query(Active).first().meal_plan_id:
                c = Meal_Plan_Already_Exists_Dialog(meal_plan_id=meal_plan_query.id)
                self.popup_meal_plan_already_exists_layer2 = MDDialog(
                    title=f"{meal_plan_query.name} already exists, would you like to overwrite?",
                    type="custom",
                    size_hint=(.9, None),
                    pos_hint={"center_x": .5, "center_y": .5},
                    content_cls=c,
                    radius=[20, 7, 20, 7]
                )
                c.meal_plan_name = meal_plan_query.name
                s.close()
                c.popup_base = self.popup_base
                c.breakfast = self.breakfast
                c.lunch = self.lunch
                c.snack = self.snack
                c.dinner = self.dinner
                c.day_range = self.day_range
                c.meal_plan_id_list = self.meal_plan_id_list
                c.popup_meal_plan_already_exists_layer2 = self.popup_meal_plan_already_exists_layer2
                self.popup_meal_plan_already_exists_layer2.open()
            else:
                meal_plan_query.name = self.ids.meal_plan_name.text
                meal_plan_query.breakfast = self.breakfast
                meal_plan_query.lunch = self.lunch
                meal_plan_query.snack = self.snack
                meal_plan_query.dinner = self.dinner
                meal_plan_query.day_range = self.day_range
                meal_plan_query.meal_plan_id_list = str(self.meal_plan_id_list)
                s.commit()
                s.close()
        else:
            new_meal_plan = Meal_Plan(
                name=self.ids.meal_plan_name.text,
                breakfast=self.breakfast,
                lunch=self.lunch,
                snack=self.snack,
                dinner=self.dinner,
                day_range=self.day_range,
                meal_plan_id_list=str(self.meal_plan_id_list)
            )
            s.add(new_meal_plan)            
            s.commit()
            meal_plan_id = new_meal_plan.id
            self.meal_plan_screen.active_meal_plan_id = meal_plan_id#
            self.meal_plan_screen.display_page_title()
            s.query(Active).update({Active.meal_plan_id: meal_plan_id})
            s.commit()
            s.close()
            self.popup_base.dismiss()

class Meal_Plan_Already_Exists_Dialog(MDBoxLayout):

    def __init__(self, meal_plan_id, *args, **kwargs):
        super(Meal_Plan_Already_Exists_Dialog,self).__init__(*args, **kwargs)
        self.meal_plan_id = meal_plan_id

    def cancel(self):
        self.popup_meal_plan_already_exists_layer2.dismiss()
    
    def overwrite_meal_plan(self):
        s = Session()
        meal_plan_query = s.get(Meal_Plan,self.meal_plan_id)
        meal_plan_query.name = self.meal_plan_name
        meal_plan_query.breakfast = self.breakfast
        meal_plan_query.lunch = self.lunch
        meal_plan_query.snack = self.snack
        meal_plan_query.dinner = self.dinner
        meal_plan_query.day_range = self.day_range
        meal_plan_query.meal_plan_id_list = str(self.meal_plan_id_list)
        s.query(Active).update({Active.meal_plan_id: self.meal_plan_id})
        s.commit()
        s.close()
        self.popup_meal_plan_already_exists_layer2.dismiss()
        self.popup_base.dismiss()
class  Meal_Plan_Settings_Dialog(MDBoxLayout):

    def __init__(self, *args, **kwargs):
        super(Meal_Plan_Settings_Dialog,self).__init__(*args, **kwargs)
    
    def cancel(self):
        self.popup_meal_plan_settings.dismiss()
    
    def check_apply_settings_button_validity(self):
        if any([self.ids.breakfast.active,self.ids.lunch.active,self.ids.dinner.active,self.ids.snack.active]):
            self.ids.apply_settings_button.disabled = False
        else:
            self.ids.apply_settings_button.disabled = True

    def decrement_day_range(self):
        if self.ids.day_range.number > 0:
            self.ids.day_range.number -= 1
            if self.ids.day_range.number == 0:
                self.ids.decrement_button.disabled = True
    
    def increment_day_range(self):
        self.ids.day_range.number += 1
        self.ids.decrement_button.disabled = False

    def save_settings(self):
        self.Meal_Plan_Screen.breakfast = self.ids.breakfast.active
        self.Meal_Plan_Screen.lunch = self.ids.lunch.active
        self.Meal_Plan_Screen.dinner = self.ids.dinner.active
        self.Meal_Plan_Screen.snack = self.ids.snack.active
        self.Meal_Plan_Screen.day_range = self.ids.day_range.number
        self.popup_meal_plan_settings.dismiss()

class Main_Logic(MDScreen):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        s = Session()
        if not s.query(Active).first():
            ic("initiate active profile")
            s.add(Active(name="Default",
                         meal_plan_id=None))
        s.commit()
        s.close()
    def load_active_profile(self):
        s = Session()
        active = s.query(Active).first()
        if active:
            settings = s.query(Settings).filter(Settings.name == active.name).first()
            if settings:
                icon_dict = {
                    "Male":"gender-male",
                    "Female":"gender-female"
                }
                self.ids.nav_drawer.ids.profile_gender_icon.icon = icon_dict[str(settings.gender)]
                self.ids.nav_drawer.ids.profile_name.text = settings.name
                self.ids.nav_drawer.ids.profile_weight.text = f"{settings.weight} kg"
                self.ids.nav_drawer.ids.profile_calories_per_day.text = f"{settings.calories_per_day} kcals/day"
        s.close()

    def get_ingredients(self):
        # Populates the ingredient list with all ingredients in the database
        MDApp.get_running_app().root.ids.screen_manager.get_screen("Ingredients_Screen").refresh_and_sort_all_ingredients_list()
    def get_meals(self):
        # Populates the meal list with all meals in the database
        MDApp.get_running_app().root.ids.screen_manager.get_screen("Meals_Screen").refresh_internal_list()
        MDApp.get_running_app().root.ids.screen_manager.get_screen("Meals_Screen").refresh_display_list()
    
    def get_meal_plan(self):
        MDApp.get_running_app().root.ids.meal_plan_screen.display_meal_plan()

class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        return Main_Logic()
    
    def on_start(self):
        self.root.load_active_profile()
        self.root.get_ingredients()
        self.root.get_meals()
        self.root.get_meal_plan()

if __name__ == "__main__":
    MainApp().run()
