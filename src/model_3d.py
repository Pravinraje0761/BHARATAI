"""Bharat 3D Lab™ - Universal Procedural 3D Science Model Engine for BHARATGURU.

Generates and provisions interactive WebGL 3D models (DNA Double Helix, Bohr Atom,
Electric Motor, Solar Orbit, Molecules, Organelles, Cells, Physics) for dynamic student interaction.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from src.llm import generate_json


@dataclass
class Model3DAnnotation:
    id: str
    label: str
    description: str
    position: tuple[float, float, float]
    color: str


@dataclass
class Model3DSpec:
    model_type: str
    title: str
    description: str
    camera_position: tuple[float, float, float]
    background_color: str
    annotations: list[Model3DAnnotation]
    parameters: dict[str, Any]
    elements: list[dict[str, Any]] | None = None
    connections: list[dict[str, Any]] | None = None

    def to_dict(self) -> dict[str, Any]:
        d = {
            "model_type": self.model_type,
            "title": self.title,
            "description": self.description,
            "camera_position": list(self.camera_position),
            "background_color": self.background_color,
            "annotations": [asdict(a) if hasattr(a, "__dataclass_fields__") else a for a in self.annotations],
            "parameters": self.parameters,
        }
        if self.elements is not None:
            d["elements"] = self.elements
        if self.connections is not None:
            d["connections"] = self.connections
        return d


# Curated high-fidelity procedural science models
PRESET_3D_MODELS: dict[str, Model3DSpec] = {
    "dna": Model3DSpec(
        model_type="dna_helix",
        title="DNA Double Helix (Deoxyribonucleic Acid)",
        description="Interactive double-helical structure composed of sugar-phosphate backbones connected by complementary nitrogenous base pairs.",
        camera_position=(0.0, 5.0, 18.0),
        background_color="#0b1c30",
        annotations=[
            Model3DAnnotation(
                id="sugar_phosphate",
                label="Sugar-Phosphate Backbone",
                description="The structural framework forming the outer spirals of the double helix.",
                position=(3.2, 2.0, 0.0),
                color="#002045",
            ),
            Model3DAnnotation(
                id="adenine_thymine",
                label="Adenine (A) = Thymine (T)",
                description="Purine-pyrimidine base pair bonded via two hydrogen bonds.",
                position=(0.0, 0.0, 0.0),
                color="#fe9832",
            ),
            Model3DAnnotation(
                id="guanine_cytosine",
                label="Guanine (G) ≡ Cytosine (C)",
                description="Purine-pyrimidine base pair bonded via three hydrogen bonds.",
                position=(0.0, 2.5, 0.0),
                color="#00b47d",
            ),
            Model3DAnnotation(
                id="hydrogen_bonds",
                label="Hydrogen Bonding Axis",
                description="Non-covalent electrostatic interactions that stabilize the complementary strand pairings.",
                position=(0.0, -2.5, 0.0),
                color="#ffffff",
            ),
        ],
        parameters={
            "turns": 3,
            "radius": 3.2,
            "height": 18.0,
            "base_pairs_count": 36,
            "strand1_color": "#1a73e8",
            "strand2_color": "#00e5ff",
            "base_colors": {
                "A": "#fe9832",
                "T": "#d9381e",
                "G": "#00b47d",
                "C": "#9c27b0",
            },
        },
    ),
    "atom": Model3DSpec(
        model_type="bohr_atom",
        title="Bohr Atomic Model (Carbon-12)",
        description="Quantum atomic model showing a dense nucleus of protons and neutrons orbited by electrons in discrete quantized energy levels.",
        camera_position=(0.0, 0.0, 16.0),
        background_color="#0b1c30",
        annotations=[
            Model3DAnnotation(
                id="nucleus",
                label="Nucleus (Protons & Neutrons)",
                description="Densely packed cluster of 6 positively charged protons and 6 neutral neutrons bound by the strong nuclear force.",
                position=(0.0, 0.0, 0.0),
                color="#ff4444",
            ),
            Model3DAnnotation(
                id="k_shell",
                label="K-Shell (n=1 Energy Level)",
                description="Innermost stable orbit holding 2 high-energy electrons.",
                position=(3.5, 0.0, 0.0),
                color="#4285f4",
            ),
            Model3DAnnotation(
                id="l_shell",
                label="L-Shell (n=2 Valence Orbit)",
                description="Outermost valence shell holding 4 bonding electrons responsible for organic chemical versatility.",
                position=(6.5, 0.0, 0.0),
                color="#00e676",
            ),
        ],
        parameters={
            "protons": 6,
            "neutrons": 6,
            "shells": [
                {"radius": 3.8, "electrons": 2, "speed": 0.03, "tilt": 0.2},
                {"radius": 7.0, "electrons": 4, "speed": 0.015, "tilt": -0.35},
            ],
        },
    ),
    "motor": Model3DSpec(
        model_type="electric_motor",
        title="DC Electric Motor & Magnetic Lorentz Force",
        description="Demonstrates magnetic flux, rotating armature coil, and commutator torque converting electrical current into mechanical rotation.",
        camera_position=(0.0, 6.0, 18.0),
        background_color="#0b1c30",
        annotations=[
            Model3DAnnotation(
                id="magnet_north",
                label="Permanent Magnet (North Pole)",
                description="Magnetic field lines originate from North and cross towards South.",
                position=(-7.0, 0.0, 0.0),
                color="#d32f2f",
            ),
            Model3DAnnotation(
                id="magnet_south",
                label="Permanent Magnet (South Pole)",
                description="Opposing magnetic pole completing the uniform magnetic flux.",
                position=(7.0, 0.0, 0.0),
                color="#1976d2",
            ),
            Model3DAnnotation(
                id="armature_coil",
                label="Rotating Armature Coil",
                description="Current-carrying conductor experiencing opposing Lorentz forces (F = I x L x B) creating continuous torque.",
                position=(0.0, 2.0, 0.0),
                color="#fbc02d",
            ),
            Model3DAnnotation(
                id="split_commutator",
                label="Split-Ring Commutator",
                description="Reverses the current direction every half-turn to sustain unidirectional rotation.",
                position=(0.0, -4.0, 0.0),
                color="#9e9e9e",
            ),
        ],
        parameters={
            "magnet_gap": 14.0,
            "coil_width": 5.0,
            "coil_height": 6.0,
            "show_field_lines": True,
        },
    ),
    "solar": Model3DSpec(
        model_type="solar_orbits",
        title="Inner Solar System & Gravitational Orbits",
        description="Sun and inner terrestrial planets (Mercury, Venus, Earth with Moon, Mars) demonstrating Kepler's laws of planetary motion.",
        camera_position=(0.0, 15.0, 25.0),
        background_color="#050a14",
        annotations=[
            Model3DAnnotation(
                id="sun",
                label="The Sun",
                description="Yellow dwarf star containing 99.8% of the solar system's mass.",
                position=(0.0, 0.0, 0.0),
                color="#ffeb3b",
            ),
            Model3DAnnotation(
                id="earth",
                label="Earth & Moon",
                description="Habitable zone planet with axial tilt and natural satellite in gravitational equilibrium.",
                position=(12.0, 0.0, 0.0),
                color="#29b6f6",
            ),
        ],
        parameters={
            "planets": [
                {"name": "Mercury", "dist": 5.0, "size": 0.5, "color": "#a1887f", "speed": 0.04},
                {"name": "Venus", "dist": 8.5, "size": 0.85, "color": "#ffe082", "speed": 0.025},
                {"name": "Earth", "dist": 13.0, "size": 1.0, "color": "#4fc3f7", "speed": 0.018},
                {"name": "Mars", "dist": 17.5, "size": 0.65, "color": "#ff7043", "speed": 0.012},
            ]
        },
    ),
    "water": Model3DSpec(
        model_type="procedural_scene",
        title="Water Molecule (H₂O) — Molecular Dipole",
        description="Bent molecular geometry with 104.5° bond angle between hydrogen atoms and central electronegative oxygen, creating permanent electric dipole.",
        camera_position=(0.0, 2.0, 10.0),
        background_color="#07111e",
        annotations=[
            Model3DAnnotation(
                id="oxygen",
                label="Oxygen Atom (δ-)",
                description="Highly electronegative central atom pulling shared electrons, creating partial negative pole.",
                position=(0.0, 0.4, 0.0),
                color="#ff3b30",
            ),
            Model3DAnnotation(
                id="hydrogen1",
                label="Hydrogen Atom 1 (δ+)",
                description="Proton nucleus with partial positive charge resulting from asymmetric electron cloud.",
                position=(2.4, -1.2, 0.0),
                color="#e0e0e0",
            ),
            Model3DAnnotation(
                id="covalent_bond",
                label="Polar Covalent Bond",
                description="Shared pair of electrons with dipole moment vector pointing towards oxygen.",
                position=(1.2, -0.4, 0.0),
                color="#4fc3f7",
            ),
        ],
        parameters={},
        elements=[
            {"id": "oxygen", "shape": "sphere", "position": [0.0, 0.5, 0.0], "size": [1.5], "color": "#ff3b30", "label": "Oxygen (O)"},
            {"id": "h1", "shape": "sphere", "position": [2.3, -1.3, 0.0], "size": [0.85], "color": "#f5f5f5", "label": "Hydrogen (H₁)"},
            {"id": "h2", "shape": "sphere", "position": [-2.3, -1.3, 0.0], "size": [0.85], "color": "#f5f5f5", "label": "Hydrogen (H₂)"},
        ],
        connections=[
            {"from_id": "oxygen", "to_id": "h1", "color": "#4fc3f7", "radius": 0.22},
            {"from_id": "oxygen", "to_id": "h2", "color": "#4fc3f7", "radius": 0.22},
        ],
    ),
    "methane": Model3DSpec(
        model_type="procedural_scene",
        title="Methane Molecule (CH₄) — Tetrahedral Geometry",
        description="sp³ hybridised carbon bonded to four hydrogen atoms forming a symmetrical regular tetrahedron with 109.5° bond angles.",
        camera_position=(0.0, 2.0, 10.0),
        background_color="#07111e",
        annotations=[
            Model3DAnnotation(
                id="carbon",
                label="Carbon Atom (Center)",
                description="Tetravalent sp³ hybridised carbon with zero net molecular dipole moment.",
                position=(0.0, 0.0, 0.0),
                color="#424242",
            ),
            Model3DAnnotation(
                id="h_top",
                label="Apex Hydrogen (H₁)",
                description="One of four identical C-H single covalent bonds spaced at 109.5°.",
                position=(0.0, 2.4, 0.0),
                color="#ffffff",
            ),
        ],
        parameters={},
        elements=[
            {"id": "carbon", "shape": "sphere", "position": [0.0, 0.0, 0.0], "size": [1.3], "color": "#37474f", "label": "Carbon (C)"},
            {"id": "h_top", "shape": "sphere", "position": [0.0, 2.4, 0.0], "size": [0.75], "color": "#ffffff", "label": "Hydrogen (H₁)"},
            {"id": "h_base1", "shape": "sphere", "position": [2.2, -0.8, 0.0], "size": [0.75], "color": "#ffffff", "label": "Hydrogen (H₂)"},
            {"id": "h_base2", "shape": "sphere", "position": [-1.1, -0.8, 1.9], "size": [0.75], "color": "#ffffff", "label": "Hydrogen (H₃)"},
            {"id": "h_base3", "shape": "sphere", "position": [-1.1, -0.8, -1.9], "size": [0.75], "color": "#ffffff", "label": "Hydrogen (H₄)"},
        ],
        connections=[
            {"from_id": "carbon", "to_id": "h_top", "color": "#90a4ae", "radius": 0.18},
            {"from_id": "carbon", "to_id": "h_base1", "color": "#90a4ae", "radius": 0.18},
            {"from_id": "carbon", "to_id": "h_base2", "color": "#90a4ae", "radius": 0.18},
            {"from_id": "carbon", "to_id": "h_base3", "color": "#90a4ae", "radius": 0.18},
        ],
    ),
    "mitochondria": Model3DSpec(
        model_type="procedural_scene",
        title="Mitochondrion (Powerhouse of the Cell)",
        description="Double-membrane bound organelle responsible for aerobic cellular respiration, Krebs cycle, and ATP generation.",
        camera_position=(0.0, 4.0, 14.0),
        background_color="#07111e",
        annotations=[
            Model3DAnnotation(
                id="outer_membrane",
                label="Outer Phospholipid Membrane",
                description="Smooth protective boundary containing porins for metabolite transport.",
                position=(0.0, 0.0, 0.0),
                color="#ff7043",
            ),
            Model3DAnnotation(
                id="cristae_folds",
                label="Mitochondrial Cristae",
                description="Deep inner-membrane foldings providing vast surface area for ATP synthase enzymes.",
                position=(0.0, 0.5, 0.0),
                color="#ffb74d",
            ),
        ],
        parameters={},
        elements=[
            {"id": "outer_capsule", "shape": "capsule", "position": [0.0, 0.0, 0.0], "size": [2.6, 6.0], "color": "#d84315", "opacity": 0.45, "label": "Outer Membrane"},
            {"id": "fold1", "shape": "torus", "position": [0.0, 1.8, 0.0], "size": [1.7, 0.25], "color": "#ffa726", "label": "Crista 1"},
            {"id": "fold2", "shape": "torus", "position": [0.0, 0.0, 0.0], "size": [1.9, 0.25], "color": "#ffa726", "label": "Crista 2"},
            {"id": "fold3", "shape": "torus", "position": [0.0, -1.8, 0.0], "size": [1.7, 0.25], "color": "#ffa726", "label": "Crista 3"},
            {"id": "atp1", "shape": "sphere", "position": [0.8, 1.0, 0.5], "size": [0.3], "color": "#00e676", "emissive": "#00e676", "label": "ATP Synthase"},
            {"id": "atp2", "shape": "sphere", "position": [-0.8, -0.6, -0.5], "size": [0.3], "color": "#00e676", "emissive": "#00e676", "label": "ATP Synthase"},
        ],
        connections=[],
    ),
    "neuron": Model3DSpec(
        model_type="procedural_scene",
        title="Motor Neuron (Nerve Cell Architecture)",
        description="Excitable neural cell consisting of soma body, branching dendrites, myelinated axon with Nodes of Ranvier, and synaptic terminal.",
        camera_position=(0.0, 2.0, 15.0),
        background_color="#07111e",
        annotations=[
            Model3DAnnotation(
                id="soma",
                label="Soma (Cell Body & Nucleus)",
                description="Metabolic center integrating incoming electrical graded potentials.",
                position=(-5.0, 0.0, 0.0),
                color="#ab47bc",
            ),
            Model3DAnnotation(
                id="myelin",
                label="Myelin Sheath & Nodes of Ranvier",
                description="Insulating lipid layers enabling rapid saltatory action potential propagation.",
                position=(0.0, 0.0, 0.0),
                color="#42a5f5",
            ),
            Model3DAnnotation(
                id="synapse",
                label="Axon Synaptic Terminal",
                description="Releases neurotransmitter vesicles into the synaptic cleft.",
                position=(5.5, 0.0, 0.0),
                color="#26a69a",
            ),
        ],
        parameters={},
        elements=[
            {"id": "soma", "shape": "sphere", "position": [-5.0, 0.0, 0.0], "size": [1.8], "color": "#8e24aa", "label": "Soma"},
            {"id": "dendrite1", "shape": "cone", "position": [-6.5, 1.4, 0.0], "size": [0.5, 2.0], "color": "#ba68c8", "rotation": [0, 0, 1.2], "label": "Dendrite"},
            {"id": "dendrite2", "shape": "cone", "position": [-6.5, -1.4, 0.0], "size": [0.5, 2.0], "color": "#ba68c8", "rotation": [0, 0, -1.2], "label": "Dendrite"},
            {"id": "axon_core", "shape": "cylinder", "position": [0.0, 0.0, 0.0], "size": [0.2, 10.0], "color": "#ffca28", "rotation": [0, 0, 1.57], "label": "Axon Core"},
            {"id": "myelin1", "shape": "cylinder", "position": [-2.2, 0.0, 0.0], "size": [0.65, 1.8], "color": "#1e88e5", "rotation": [0, 0, 1.57], "label": "Myelin Sheath"},
            {"id": "myelin2", "shape": "cylinder", "position": [0.0, 0.0, 0.0], "size": [0.65, 1.8], "color": "#1e88e5", "rotation": [0, 0, 1.57], "label": "Myelin Sheath"},
            {"id": "myelin3", "shape": "cylinder", "position": [2.2, 0.0, 0.0], "size": [0.65, 1.8], "color": "#1e88e5", "rotation": [0, 0, 1.57], "label": "Myelin Sheath"},
            {"id": "terminal", "shape": "sphere", "position": [5.2, 0.0, 0.0], "size": [0.9], "color": "#00897b", "label": "Synaptic Knob"},
        ],
        connections=[],
    ),
}


def get_3d_model(concept_or_key: str) -> Model3DSpec:
    """Retrieves or dynamically matches a curated 3D model specification for a given STEM concept."""
    norm = concept_or_key.lower().strip()

    if any(k in norm for k in ["dna", "helix", "gene", "genetic", "chromosome", "nucleotide"]):
        return PRESET_3D_MODELS["dna"]

    if any(k in norm for k in ["water", "h2o", "ice", "steam", "liquid"]):
        return PRESET_3D_MODELS["water"]

    if any(k in norm for k in ["methane", "ch4", "hydrocarbon", "alkane"]):
        return PRESET_3D_MODELS["methane"]

    if any(k in norm for k in ["mitochondria", "mitochondrion", "atp", "cellular respiration", "organelle"]):
        return PRESET_3D_MODELS["mitochondria"]

    if any(k in norm for k in ["neuron", "brain cell", "axon", "synapse", "nervous system"]):
        return PRESET_3D_MODELS["neuron"]

    if any(k in norm for k in ["atom", "electron", "proton", "neutron", "bohr", "nucleus", "quantum"]):
        return PRESET_3D_MODELS["atom"]

    if any(k in norm for k in ["motor", "lorentz", "magnetic field", "magnet", "induction", "coil", "armature"]):
        return PRESET_3D_MODELS["motor"]

    if any(k in norm for k in ["solar", "orbit", "planet", "gravity", "earth", "kepler", "space"]):
        return PRESET_3D_MODELS["solar"]

    return PRESET_3D_MODELS["dna"]


def generate_custom_3d_concept(prompt_query: str) -> dict[str, Any]:
    """Uses LLM to dynamically construct procedural WebGL 3D elements and connections for any concept."""
    norm = prompt_query.lower().strip()

    # Fast match against curated procedural presets
    if any(k in norm for k in ["water", "h2o"]):
        return PRESET_3D_MODELS["water"].to_dict()
    if any(k in norm for k in ["methane", "ch4"]):
        return PRESET_3D_MODELS["methane"].to_dict()
    if any(k in norm for k in ["mitochondria", "organelle"]):
        return PRESET_3D_MODELS["mitochondria"].to_dict()
    if any(k in norm for k in ["neuron", "brain cell"]):
        return PRESET_3D_MODELS["neuron"].to_dict()
    if any(k in norm for k in ["atom", "bohr"]):
        return PRESET_3D_MODELS["atom"].to_dict()
    if any(k in norm for k in ["motor", "magnet"]):
        return PRESET_3D_MODELS["motor"].to_dict()
    if any(k in norm for k in ["solar", "planet"]):
        return PRESET_3D_MODELS["solar"].to_dict()
    if any(k in norm for k in ["dna", "helix"]):
        return PRESET_3D_MODELS["dna"].to_dict()

    # Dynamic LLM generation for novel prompts
    sys_prompt = (
        "You are the Bharat 3D Lab WebGL Architect. Generate a JSON procedural 3D model specification for Three.js. "
        "The model_type MUST be 'procedural_scene'. "
        "Include: "
        "- title: descriptive title "
        "- description: pedagogical 1-line concept explanation "
        "- camera_position: [x, y, z] usually [0, 2, 12] "
        "- annotations: list of 2-3 items with id, label, description, position [x, y, z], color "
        "- elements: list of 3-8 3D objects with: "
        "    id: string, shape: ('sphere'|'cylinder'|'box'|'torus'|'cone'), "
        "    position: [x, y, z], size: [radius/width, ...], color: hex (e.g. '#ff3b30'), label: string "
        "- connections: list of cylinders between elements: "
        "    from_id: string, to_id: string, color: hex, radius: float (e.g. 0.15) "
        "Strictly output valid JSON only."
    )
    prompt = f"Student requests interactive 3D science model for: '{prompt_query}'. Output valid JSON."

    try:
        data = generate_json(prompt, tag="3d_model", system=sys_prompt, temperature=0.3)
        if isinstance(data, dict) and "title" in data:
            data["model_type"] = "procedural_scene"
            if "elements" not in data or not isinstance(data["elements"], list):
                data["elements"] = [
                    {"id": "center", "shape": "sphere", "position": [0, 0, 0], "size": [1.5], "color": "#00e5ff", "label": "Core Component"},
                    {"id": "node1", "shape": "sphere", "position": [3, 0, 0], "size": [0.8], "color": "#fe9832", "label": "Attached Unit"},
                    {"id": "node2", "shape": "sphere", "position": [-3, 0, 0], "size": [0.8], "color": "#00b47d", "label": "Attached Unit"}
                ]
                data["connections"] = [
                    {"from_id": "center", "to_id": "node1", "color": "#ffffff", "radius": 0.15},
                    {"from_id": "center", "to_id": "node2", "color": "#ffffff", "radius": 0.15}
                ]
            return data
    except Exception as exc:
        print(f"[3D Generator] LLM generation fallback: {exc}")

    # Fallback to water molecule or DNA
    return PRESET_3D_MODELS["water"].to_dict()
