#!/usr/bin/env python3
from art import *
import random
from subprober.modules.logger.logger import random,bold,reset,white,colors
random_color = random.choice(colors)


def banner():
    tool_name = "subprober"
    fonts = ["big", "ogre", "shadow", "script", "colossal" , "smslant", "graffiti", "slant"]
    selected_font = random.choice(fonts)
    banner = text2art(f"{tool_name}", font=selected_font)
    banner = f"""{bold}{random_color}{banner}{reset}
                    {bold}{white}- RevoltSecurities{reset}\n"""
    return banner