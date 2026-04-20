#complete your tasks in this file

from dataclasses import dataclass
import math
from typing import TypeAlias

##########
# TASK 1 #
##########

degrees: TypeAlias = float

@dataclass(frozen=True)
class GlobeRect:
    lo_lat: degrees
    hi_lat: degrees
    west_long: degrees
    east_long: degrees

@dataclass(frozen=True)
class Region:
    rect: GlobeRect
    name: str
    terrain: str

@dataclass(frozen=True)
class RegionCondition:
    region: Region
    year: int
    pop: int
    ghg_rate: float

##########
# TASK 2 #
##########

# Tokyo Japan
rect_tokyo = GlobeRect(35.5, 35.9, 139.5, 139.9)
region_tokyo = Region(rect_tokyo, "Tokyo", "other")
rc_tokyo = RegionCondition(region_tokyo, 2024, 13960000, 60000000.0)

# São Paulo Brazil
rect_sao_paulo = GlobeRect(-23.7, -23.4, -46.8, -46.5)
region_sao_paulo = Region(rect_sao_paulo, "São Paulo", "other")
rc_sao_paulo = RegionCondition(region_sao_paulo, 2024, 12300000, 45000000.0)

# North Atlantic Section
rect_north_atlantic = GlobeRect(30.0, 50.0, -50.0, -20.0)
region_north_atlantic = Region(rect_north_atlantic, "North Atlantic", "ocean")
rc_north_atlantic = RegionCondition(region_north_atlantic, 2024, 0, 0.0)

# Cal Poly Region
rect_cal_poly = GlobeRect(35.1, 35.5, -120.9, -120.5)
region_cal_poly = Region(rect_cal_poly, "Cal Poly", "other")
rc_cal_poly = RegionCondition(region_cal_poly, 2024, 45000, 120000.0)

region_conditions = [rc_tokyo, rc_sao_paulo, rc_north_atlantic, rc_cal_poly]


##########
# TASK 3 #
##########

def emissions_per_capita(rc: RegionCondition) -> float:
    if not isinstance(rc, RegionCondition): raise TypeError("Input must be a RegionCondition")
    if rc.pop == 0: return 0.0
    return rc.ghg_rate / rc.pop

def area(gr: GlobeRect) -> float:
    if not isinstance(gr, GlobeRect): raise TypeError("Input must be a GlobdeRect")
    dx = gr.east_long - gr.west_long
    if dx < 0: dx += 360
    dx *= (2*math.pi/360)
    d_angle = math.sin(gr.hi_lat*(2*math.pi/360)) - math.sin(gr.lo_lat*(2*math.pi/360))
    a = (6378.1**2) * dx * d_angle
    return(a)

def emissions_per_square_km(rc: RegionCondition) -> float:
    if not isinstance(rc, RegionCondition): raise TypeError("Input must be a RegionCondition")
    sqr_km = area(rc.region.rect)
    if sqr_km == 0: raise ValueError("Region has 0 area")
    return(rc.ghg_rate/sqr_km)

def densest(rc_list: list[RegionCondition]) -> str:
    if len(rc_list) == 0: raise ValueError("List of RegionConditions is empty")
    result = densest_helper(rc_list)
    return result[1]
    

def densest_helper(rc_list: list[RegionCondition]) -> tuple[float, str]:
    if not isinstance(rc_list[0], RegionCondition): raise TypeError("List must contain exclusively RegionContition objects")
    d1 = rc_list[0].pop / area(rc_list[0].region.rect)
    if len(rc_list) == 1:
        return (d1, rc_list[0].region.name)
    r2 = densest_helper(rc_list[1:])
    if r2[0] > d1: return r2
    return (d1, rc_list[0].region.name)

##########
# TASK 4 #
##########

def project_condition(rc: RegionCondition, years: int) -> RegionCondition:
    if not isinstance(rc, RegionCondition): raise TypeError("Input must be a RegionCondition")
    if not isinstance(years, int): raise TypeError("years must be of type int")
    if years <= 0: raise ValueError("years must be greater than 0")
    growth_rate = get_growth_rate(rc.region)
    emissions_pc = emissions_per_capita(rc)
    new_pop = grow_pop(rc.pop, growth_rate, years)
    new_emissions = emissions_pc*new_pop
    return RegionCondition(rc.region, rc.year + years, new_pop, new_emissions)



def grow_pop(pop: int, rate: float, years: int) -> int:
    if years == 1:
        return int(pop + (pop*rate))
    return grow_pop(int(pop + (pop*rate)), rate, years-1)

def get_growth_rate(r: Region) -> float:
    if r.terrain == "ocean":
        return 0.0001
    elif r.terrain == "mountains":
        return 0.0005
    elif r.terrain == "forest":
        return -0.00001
    else:
        return 0.0003

