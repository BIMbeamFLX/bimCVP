# IFC4 entity cheatsheet for HKLS/TGA/MEP

Quick reference for which IFC4 entity + PredefinedType to pick when extending the mapping CSVs. Restricted to entities relevant to mechanical/sanitary/plumbing systems.

## Pipe network

| Component | IFC entity | PredefinedType | Notes |
|---|---|---|---|
| Pipe segment | `IfcPipeSegment` | NOTDEFINED | Length carried by Qto |
| Pipe fitting (bend) | `IfcPipeFitting` | BEND | |
| Pipe fitting (T-piece) | `IfcPipeFitting` | JUNCTION | |
| Pipe fitting (reducer) | `IfcPipeFitting` | TRANSITION | |
| Flange | `IfcPipeFitting` | CONNECTOR | |
| End cap | `IfcPipeFitting` | ENTRY or TRANSITION | IFC4 has no CAP — workaround |

## Valves (IfcValve PredefinedTypes)

`AIRRELEASE`, `ANTIVACUUM`, `CHANGEOVER`, `CHECK`, `COMMISSIONING`, `DIVERTING`, `DRAWOFFCOCK`, `DOUBLECHECK`, `DOUBLEREGULATING`, `FAUCET`, `FLUSHING`, `GASCOCK`, `GASTAP`, `ISOLATING`, `MIXING`, `PRESSUREREDUCING`, `PRESSURERELIEF`, `REGULATING`, `SAFETYCUTOFF`, `STEAMTRAP`, `STOPCOCK`, `USERDEFINED`, `NOTDEFINED`

Common mappings:
- Ball/gate valve manual → `ISOLATING`
- Three-way mixing valve → `MIXING`
- Strainer/balancing valve → `REGULATING`
- Check valve / backflow preventer → `CHECK`
- Safety valve / pressure relief → `PRESSURERELIEF`
- Air vent / vent valve → `AIRRELEASE`
- Magnetic shut-off → `ISOLATING`

## Pumps (IfcPump PredefinedTypes)

`CIRCULATOR`, `ENDSUCTION`, `SPLITCASE`, `SUBMERSIBLEPUMP`, `SUMPPUMP`, `VERTICALINLINE`, `VERTICALTURBINE`, `USERDEFINED`, `NOTDEFINED`

- Heating/cooling circulation pump → `CIRCULATOR`
- Sewage lift station → `SUMPPUMP`
- Domestic water pressure pump → `VERTICALINLINE` or `ENDSUCTION`

## Tanks / storage (IfcTank PredefinedTypes)

`BASIN`, `BREAKPRESSURE`, `EXPANSION`, `FEEDANDEXPANSION`, `OILRETENTIONTRAY`, `PRESSUREVESSEL`, `STORAGE`, `VESSEL`, `WATERHEATER`, `WATERSTORAGEHORIZONTAL`, `WATERSTORAGEVERTICAL`, `USERDEFINED`, `NOTDEFINED`

- Buffer tank → `STORAGE`
- Membrane expansion tank → `EXPANSION`
- Hot water cylinder → `WATERHEATER`

## Air handling

| Component | IFC entity | PredefinedType | Notes |
|---|---|---|---|
| Air handling unit | `IfcAirToAirHeatRecovery` | `PLATEHEATEXCHANGER` | IFC4 has IfcUnitaryEquipment too — depends on type |
| Fan | `IfcFan` | `CENTRIFUGALFORWARDCURVED` / `AXIAL` / `VANEAXIAL` | |
| Duct segment | `IfcDuctSegment` | RIGIDSEGMENT or FLEXIBLESEGMENT | |
| Duct fitting (bend, branch, transition, end-cap) | `IfcDuctFitting` | `BEND` / `JUNCTION` / `TRANSITION` / `CONNECTOR` | No CAP — use TRANSITION |
| Damper (IfcDamper PredefinedTypes) | `IfcDamper` | see below | |
| Air terminal (IfcAirTerminal PredefinedTypes) | `IfcAirTerminal` | DIFFUSER / GRILLE / LOUVER / REGISTER | Only 4 values in IFC4 |
| Duct silencer | `IfcDuctSilencer` | `FLATOVAL` / `RECTANGULAR` / `ROUND` | |
| Filter | `IfcFilter` | `AIRPARTICLEFILTER` | |
| Coil | `IfcCoil` | `HEATING` / `COOLING` / `WATERHEATING` / `WATERCOOLING` | |

### IfcDamper PredefinedTypes

`BACKDRAFTDAMPER`, `BALANCINGDAMPER`, `BLASTDAMPER`, `CONTROLDAMPER`, `FIREDAMPER`, `FIRESMOKEDAMPER`, `FUMEHOODEXHAUST`, `GRAVITYDAMPER`, `GRAVITYRELIEFDAMPER`, `RELIEFDAMPER`, `SMOKEDAMPER`, `USERDEFINED`, `NOTDEFINED`

- VAV / Volume Flow Controller → `CONTROLDAMPER` (no `VOLUMECONTROLDAMPER` in IFC4!)
- Fire damper → `FIREDAMPER`
- Smoke damper → `SMOKEDAMPER`
- Balancing damper → `BALANCINGDAMPER`

## Distribution chambers / manifolds

`IfcDistributionChamberElement` PredefinedTypes: `FORMEDDUCT`, `INSPECTIONCHAMBER`, `INSPECTIONPIT`, `MANHOLE`, `METERCHAMBER`, `SUMP`, `TRENCH`, `VALVECHAMBER`, `USERDEFINED`, `NOTDEFINED`

- Heating/cooling manifold (HZVT/KVT/VKF) → `NOTDEFINED` (no MANIFOLD value exists; Pset clarifies)
- Manhole shaft → `MANHOLE`

## Heat generation

- Boiler → `IfcBoiler` (`WATER` / `STEAM`)
- Chiller air-cooled → `IfcChiller` (`AIRCOOLED`)
- Chiller water-cooled → `IfcChiller` (`WATERCOOLED`)
- Heat pump → `IfcUnitaryEquipment` (`AIRHANDLER`) — IFC4 has no IfcHeatPump
- Heat exchanger plate → `IfcHeatExchanger` (`PLATE` / `SHELLANDTUBE`)
- Solar thermal collector → `IfcSolarDevice` (`SOLARCOLLECTOR`)

## Heat distribution (terminal)

- Radiator → `IfcSpaceHeater` (`RADIATOR`)
- Convector → `IfcSpaceHeater` (`CONVECTOR`)
- Panel radiator / underfloor heating panel → `IfcSpaceHeater` (`PANELRADIATOR`)
- Fan coil unit → `IfcUnitaryEquipment` (`FANCOILUNIT`)

## Sanitary

`IfcSanitaryTerminal` PredefinedTypes: `BATH`, `BIDET`, `CISTERN`, `SHOWER`, `SINK`, `SANITARYFOUNTAIN`, `TOILETPAN`, `URINAL`, `WASHHANDBASIN`, `WCSEAT`, `USERDEFINED`, `NOTDEFINED`

- Washbasin / Waschtisch → `WASHHANDBASIN`
- Kitchen sink → `SINK`
- WC with cistern → `TOILETPAN`
- Floor drain / Bodenablauf → no FLOORTRAP in IFC4; use `SINK` as workaround or `USERDEFINED`
- Faucet / tap (standalone) → no FAUCET; use `WASHHANDBASIN` or set on parent fixture

## Fire suppression

- Sprinkler head → `IfcFireSuppressionTerminal` (`SPRINKLER`)

## Insulation / covering

- Pipe insulation → `IfcCovering` (`INSULATION`)
- Duct insulation → `IfcCovering` (`INSULATION` or `USERDEFINED`)
- Linear's `IfcCovering` export uses `USERDEFINED` because insulation is not a pure cladding

## Auxiliary / virtual

- Linear's PartialNetworkStart / End / Port (geometric helpers) → `IfcVirtualElement` (`NOTDEFINED`)
- Generic fallback for unclassifiable → `IfcBuildingElementProxy` (PredefinedType `NOTDEFINED` or `USERDEFINED`) — try to avoid

## IFC4 vs IFC4.3 ADD2

IFC4 is what most exporters reliably produce today (2026). IFC4.3 ADD2 adds infrastructure entities (railway, bridge, ports) and refines distribution elements but the core HKLS entity set is identical. All mappings in this skill work for both — list both in the IDS `ifcVersion="IFC4 IFC4X3_ADD2"`.

When in doubt about a PredefinedType validity: open buildingSMART's IFC4 schema documentation (technical.buildingsmart.org/standards/ifc/ifc-schema-specifications/), search the entity name, scroll to `PredefinedType` enum.
