"""
fuel_properties.py
------------------
First-principles fuel-gas thermochemistry for a refinery fired heater.

Given a molar fuel-gas composition (mole fractions), this module computes the
properties the digital twin needs as *derived* first-principles quantities:

    - Lower / Higher Heating Value  (mass & volumetric basis)
    - Molecular weight, gas density
    - Wobbe Index (burner interchangeability)
    - Stoichiometric air demand
    - Full combustion product balance at a chosen excess-air level
      (wet & dry flue gas, flue O2 %, CO2, H2O, SO2, N2)

Everything is derived from per-component atomic makeup and standard heats of
combustion -- no black-box correlations. This is the "foundation model based on
first principles" referenced in the project roadmap.

Component data
--------------
LHV values are standard lower heating values at 25 C (kJ/mol).
Stoichiometric O2 is derived from the reaction:
    Cx Hy Sz  +  (x + y/4 + z) O2  ->  x CO2 + (y/2) H2O + z SO2
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Component:
    name: str
    mw: float          # molecular weight, g/mol
    lhv_mol: float     # lower heating value, kJ/mol
    n_C: float         # carbon atoms  -> CO2
    n_H: float         # hydrogen atoms -> H2O
    n_S: float         # sulfur atoms  -> SO2
    inert: bool = False

    @property
    def o2_stoich(self) -> float:
        """Moles O2 needed for complete combustion of 1 mol of this component."""
        return self.n_C + self.n_H / 4.0 + self.n_S


# Reference: NIST / Perry's. HHV~LHV+ (n_H/2 * 44.0) kJ/mol water latent adjust.
COMPONENTS = {
    "H2":    Component("H2",    2.016,  241.8, 0, 2, 0),
    "CH4":   Component("CH4",   16.043, 802.3, 1, 4, 0),
    "C2H6":  Component("C2H6",  30.070, 1428.6, 2, 6, 0),
    "C2H4":  Component("C2H4",  28.054, 1323.2, 2, 4, 0),
    "C3H8":  Component("C3H8",  44.097, 2043.9, 3, 8, 0),
    "C3H6":  Component("C3H6",  42.081, 1926.1, 3, 6, 0),
    "iC4H10": Component("iC4H10", 58.123, 2649.0, 4, 10, 0),
    "nC4H10": Component("nC4H10", 58.123, 2657.3, 4, 10, 0),
    "CO":    Component("CO",    28.010, 283.0, 1, 0, 0),   # C already, burns to CO2
    "CO2":   Component("CO2",   44.010, 0.0,   1, 0, 0, inert=True),
    "N2":    Component("N2",    28.014, 0.0,   0, 0, 0, inert=True),
    "H2S":   Component("H2S",   34.081, 518.0, 0, 2, 1),   # -> SO2 + H2O
    "H2O":   Component("H2O",   18.015, 0.0,   0, 0, 0, inert=True),
}

# Latent heat of vaporization of water used for HHV back-out (kJ per mol H2O).
_H2O_LATENT = 44.0
_O2_IN_AIR = 0.2095        # mole fraction O2 in dry air
_N2_PER_O2 = (1 - _O2_IN_AIR) / _O2_IN_AIR   # ~3.773 mol N2 per mol O2


@dataclass
class FuelProperties:
    mw: float                 # g/mol
    lhv_mass: float           # MJ/kg
    hhv_mass: float           # MJ/kg
    lhv_vol: float            # MJ/Nm3  (normal m3, 0 C, 1 atm)
    density_norm: float       # kg/Nm3
    wobbe: float              # MJ/Nm3
    o2_stoich_mol: float      # mol O2 / mol fuel
    air_stoich_mass: float    # kg air / kg fuel (AFR stoichiometric)


def normalize(comp: dict) -> dict:
    """Normalize a composition dict of mole fractions to sum to 1.0."""
    total = sum(comp.values())
    if total <= 0:
        raise ValueError("composition sums to zero")
    return {k: v / total for k, v in comp.items()}


def fuel_properties(comp: dict) -> FuelProperties:
    """Compute first-principles fuel-gas properties from a molar composition."""
    comp = normalize(comp)
    mw = 0.0
    lhv_mol = 0.0            # kJ per mol of fuel mixture
    hhv_mol = 0.0
    o2_mol = 0.0
    for name, x in comp.items():
        c = COMPONENTS[name]
        mw += x * c.mw
        lhv_mol += x * c.lhv_mol
        # HHV: add back latent heat of the water formed (n_H/2 mol H2O per mol)
        hhv_mol += x * (c.lhv_mol + (c.n_H / 2.0) * _H2O_LATENT)
        o2_mol += x * c.o2_stoich

    # Mass-basis heating values: kJ/mol / (g/mol) = kJ/g = MJ/kg
    lhv_mass = lhv_mol / mw
    hhv_mass = hhv_mol / mw

    # Molar volume at normal conditions (0 C, 101.325 kPa) = 22.414 L/mol
    molar_vol_norm = 22.414e-3   # Nm3/mol
    density_norm = (mw / 1000.0) / molar_vol_norm   # kg/Nm3
    lhv_vol = (lhv_mol / 1000.0) / molar_vol_norm   # MJ/Nm3

    # Wobbe index = HHV_vol / sqrt(specific gravity vs air)
    hhv_vol = (hhv_mol / 1000.0) / molar_vol_norm
    sg = mw / 28.964                                # rel. to air MW
    wobbe = hhv_vol / (sg ** 0.5)

    # Stoichiometric air-fuel ratio on a mass basis
    air_mol = o2_mol * (1 + _N2_PER_O2)             # mol air / mol fuel
    air_mass_per_fuel_mass = (air_mol * 28.964) / mw
    return FuelProperties(
        mw=mw,
        lhv_mass=lhv_mass,
        hhv_mass=hhv_mass,
        lhv_vol=lhv_vol,
        density_norm=density_norm,
        wobbe=wobbe,
        o2_stoich_mol=o2_mol,
        air_stoich_mass=air_mass_per_fuel_mass,
    )


@dataclass
class CombustionProducts:
    excess_air_frac: float
    flue_o2_dry_pct: float     # dry-basis O2 %  (the "Stack O2" the KPI uses)
    flue_co2_dry_pct: float
    flue_co_ppm: float
    flue_so2_ppm: float
    flue_nox_ppm: float
    mol_flue_wet_per_mol_fuel: float
    mol_flue_dry_per_mol_fuel: float
    mol_co2_per_mol_fuel: float
    mol_h2o_per_mol_fuel: float


def combustion_products(comp: dict, excess_air_frac: float,
                        combustion_eff: float = 0.999,
                        nox_ppm: float = 60.0) -> CombustionProducts:
    """
    Full flue-gas balance for complete-ish combustion at a given excess air.

    combustion_eff < 1 diverts a small carbon fraction to CO (models burner
    upset / insufficient air). nox_ppm is supplied by the thermal-NOx model in
    the plant layer (depends on flame temperature).
    """
    comp = normalize(comp)
    n_CO2 = n_H2O = n_SO2 = n_N2_fuel = o2_stoich = 0.0
    carbon_total = 0.0
    for name, x in comp.items():
        c = COMPONENTS[name]
        carbon_total += x * c.n_C
        n_CO2 += x * c.n_C
        n_H2O += x * c.n_H / 2.0
        n_SO2 += x * c.n_S
        o2_stoich += x * c.o2_stoich
        if name == "N2":
            n_N2_fuel += x            # fuel-bound inert N2 passes through

    # Incomplete combustion: shift a fraction of carbon from CO2 to CO
    co_fraction = max(0.0, 1.0 - combustion_eff)
    n_CO = carbon_total * co_fraction
    n_CO2 = n_CO2 - n_CO
    # CO combustion only needs 0.5 O2 vs 1.0 for full -> frees a little O2
    o2_consumed = o2_stoich - 0.5 * n_CO

    o2_supplied = o2_stoich * (1.0 + excess_air_frac)
    o2_excess = o2_supplied - o2_consumed
    n_N2_air = o2_supplied * _N2_PER_O2

    n_N2_total = n_N2_air + n_N2_fuel
    wet = n_CO2 + n_H2O + n_SO2 + n_CO + o2_excess + n_N2_total
    dry = wet - n_H2O

    flue_o2_dry_pct = 100.0 * o2_excess / dry
    flue_co2_dry_pct = 100.0 * n_CO2 / dry
    flue_co_ppm = 1e6 * n_CO / dry
    flue_so2_ppm = 1e6 * n_SO2 / dry

    return CombustionProducts(
        excess_air_frac=excess_air_frac,
        flue_o2_dry_pct=flue_o2_dry_pct,
        flue_co2_dry_pct=flue_co2_dry_pct,
        flue_co_ppm=flue_co_ppm,
        flue_so2_ppm=flue_so2_ppm,
        flue_nox_ppm=nox_ppm,
        mol_flue_wet_per_mol_fuel=wet,
        mol_flue_dry_per_mol_fuel=dry,
        mol_co2_per_mol_fuel=n_CO2 + n_CO,   # total carbon leaving
        mol_h2o_per_mol_fuel=n_H2O,
    )


if __name__ == "__main__":
    # Quick sanity check: a typical refinery fuel gas (H2/CH4 rich)
    demo = {"H2": 25, "CH4": 45, "C2H6": 12, "C3H8": 8, "C4H10": 0,
            "nC4H10": 3, "CO2": 3, "N2": 3, "H2S": 0.05}
    demo = {k: v for k, v in demo.items() if k in COMPONENTS}
    p = fuel_properties(demo)
    print(f"MW           = {p.mw:6.2f} g/mol")
    print(f"LHV (mass)   = {p.lhv_mass:6.2f} MJ/kg")
    print(f"HHV (mass)   = {p.hhv_mass:6.2f} MJ/kg")
    print(f"LHV (vol)    = {p.lhv_vol:6.2f} MJ/Nm3")
    print(f"Density      = {p.density_norm:6.3f} kg/Nm3")
    print(f"Wobbe        = {p.wobbe:6.2f} MJ/Nm3")
    print(f"AFR stoich   = {p.air_stoich_mass:6.2f} kg air/kg fuel")
    cp = combustion_products(demo, excess_air_frac=0.15)
    print(f"Flue O2 dry  = {cp.flue_o2_dry_pct:5.2f} %  (target ~2-3.5%)")
    print(f"Flue CO2 dry = {cp.flue_co2_dry_pct:5.2f} %")
