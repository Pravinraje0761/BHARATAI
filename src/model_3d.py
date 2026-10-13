"""Bharat 3D Lab - Universal Procedural 3D Science Model Engine for BHARATGURU.

Generates and provisions interactive WebGL 3D models (Human Eye, DNA Double Helix, Bohr Atom,
Electric Motor, Solar Orbit, Heart, Plant Cell, Light Dispersion Prism, Molecules, Organelles)
for dynamic student interaction.
"""
from __future__ import annotations

import re
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
    pedagogical_reflection: str | None = None

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
        if self.pedagogical_reflection is not None:
            d["pedagogical_reflection"] = self.pedagogical_reflection
        return d


# Curated high-fidelity procedural science models
PRESET_3D_MODELS: dict[str, Model3DSpec] = {
    "eye": Model3DSpec(
        model_type="human_eye",
        title="Human Eye — Anatomy & Optics of Vision",
        description="Complex optical system demonstrating light refraction through cornea and crystalline biconvex lens, aperture regulation via iris/pupil, and retinal photoreception.",
        camera_position=(0.0, 1.5, 13.0),
        background_color="#07111e",
        pedagogical_reflection=(
            "Notice how light enters through the transparent cornea (which provides ~75% of refractive power), "
            "passes through the pupil aperture controlled by the pigmented iris, and is focused by the crystalline "
            "lens onto the retina. The ciliary muscles adjust lens curvature for accommodation between near and far objects!"
        ),
        annotations=[
            Model3DAnnotation(
                id="cornea",
                label="Cornea (Refractive Window)",
                description="Curved front transparent dome contributing 70-80% of total optical refraction.",
                position=(0.0, 0.0, 4.2),
                color="#00e5ff",
            ),
            Model3DAnnotation(
                id="iris_pupil",
                label="Iris & Pupil Aperture",
                description="Pigmented muscular diaphragm adjusting pupil diameter to control incident light intensity.",
                position=(0.0, 0.0, 2.9),
                color="#fe9832",
            ),
            Model3DAnnotation(
                id="crystalline_lens",
                label="Crystalline Biconvex Lens",
                description="Transparent flexible protein lens providing fine dynamic focus (accommodation) onto the retina.",
                position=(0.0, 0.0, 1.8),
                color="#80d8ff",
            ),
            Model3DAnnotation(
                id="ciliary_body",
                label="Ciliary Body & Zonules",
                description="Smooth ciliary muscle ring altering lens curvature for clear vision at varying distances.",
                position=(0.0, 2.6, 1.8),
                color="#ff5252",
            ),
            Model3DAnnotation(
                id="retina",
                label="Retina & Fovea Centralis",
                description="Posterior sensory lining containing ~125M photoreceptive rods and cones converting photons to neural signals.",
                position=(0.0, 0.0, -3.8),
                color="#ff6d00",
            ),
            Model3DAnnotation(
                id="optic_nerve",
                label="Optic Nerve (Cranial Nerve II)",
                description="Bundle of ~1.2 million retinal ganglion cell axons relaying visual action potentials to the brain.",
                position=(0.0, -0.6, -6.8),
                color="#ffd54f",
            ),
            Model3DAnnotation(
                id="sclera",
                label="Sclera (Protective Outer Coat)",
                description="Tough, fibrous white tunic maintaining intraocular pressure and eye geometry.",
                position=(-3.6, 1.4, 0.0),
                color="#eceff1",
            ),
        ],
        parameters={
            "pupil_radius": 0.85,
            "iris_radius": 2.2,
            "lens_power": 1.2,
            "show_optical_rays": True,
        },
        elements=[
            {"id": "sclera", "shape": "sphere", "position": [0.0, 0.0, 0.0], "size": [3.8], "color": "#f8f9fa", "opacity": 0.8, "label": "Sclera"},
            {"id": "cornea", "shape": "sphere", "position": [0.0, 0.0, 2.6], "size": [2.1], "color": "#80deea", "opacity": 0.45, "label": "Cornea"},
            {"id": "iris", "shape": "torus", "position": [0.0, 0.0, 2.7], "size": [1.5, 0.5], "color": "#0288d1", "label": "Iris"},
            {"id": "pupil", "shape": "sphere", "position": [0.0, 0.0, 2.75], "size": [0.75], "color": "#0d1117", "label": "Pupil"},
            {"id": "lens", "shape": "sphere", "position": [0.0, 0.0, 1.8], "size": [1.4], "color": "#b3e5fc", "opacity": 0.6, "label": "Crystalline Lens"},
            {"id": "ciliary", "shape": "torus", "position": [0.0, 0.0, 1.8], "size": [2.1, 0.28], "color": "#e53935", "label": "Ciliary Body"},
            {"id": "retina", "shape": "sphere", "position": [0.0, 0.0, -1.5], "size": [3.2], "color": "#d84315", "opacity": 0.55, "label": "Retina"},
            {"id": "fovea", "shape": "sphere", "position": [0.6, 0.2, -3.7], "size": [0.38], "color": "#ffd600", "label": "Fovea Centralis"},
            {"id": "optic_nerve", "shape": "cylinder", "position": [0.0, -0.5, -5.2], "size": [0.75, 3.2], "color": "#ffe082", "rotation": [1.57, 0, 0], "label": "Optic Nerve"},
        ],
        connections=[
            {"from_id": "ciliary", "to_id": "lens", "color": "#ff8a80", "radius": 0.12},
        ],
    ),
    "dna": Model3DSpec(
        model_type="dna_helix",
        title="DNA Double Helix (Deoxyribonucleic Acid)",
        description="Interactive double-helical structure composed of sugar-phosphate backbones connected by complementary nitrogenous base pairs.",
        camera_position=(0.0, 5.0, 18.0),
        background_color="#0b1c30",
        pedagogical_reflection=(
            "Notice how the complementary purine-pyrimidine base pairs (A=T with two hydrogen bonds, G≡C with three) "
            "ensure the outer sugar-phosphate backbones remain exactly 2.0 nanometers apart throughout the entire helical twist!"
        ),
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
        pedagogical_reflection=(
            "Carbon-12 features 6 protons and 6 neutrons in the central nucleus with 2 inner K-shell electrons and "
            "4 outer L-shell valence electrons. The tetravalent electron configuration enables Carbon to form versatile covalent bonds!"
        ),
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
        pedagogical_reflection=(
            "When direct current passes through the rectangular armature coil in the uniform magnetic field, "
            "opposing Lorentz forces (F = I·L×B) create rotational torque. The split-ring commutator switches current "
            "polarity every half-turn to sustain continuous clockwise rotation!"
        ),
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
        pedagogical_reflection=(
            "Planetary orbits trace elliptical paths governed by Kepler's Laws and Newton's Universal Gravitation. "
            "Notice how inner planets like Mercury orbit with much higher orbital velocity than Earth and Mars!"
        ),
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
        pedagogical_reflection=(
            "Observe the bent 104.5° bond angle: the two lone pairs on oxygen repel the bonding pairs, giving water "
            "its asymmetric geometry and strong dipole moment, making it the universal solvent of biochemistry!"
        ),
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
        pedagogical_reflection=(
            "Carbon forms four equivalent sp³ hybridized orbitals directed towards the vertices of a regular tetrahedron "
            "at 109.5°. The symmetrical geometry cancels individual C-H bond dipole moments, making CH₄ non-polar!"
        ),
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
        pedagogical_reflection=(
            "The extensively folded inner mitochondrial membrane (cristae) creates a vast surface area for the "
            "electron transport chain and ATP synthase complexes, transforming nutrient energy into cellular ATP currency!"
        ),
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
            {"id": "outer_capsule", "shape": "cylinder", "position": [0.0, 0.0, 0.0], "size": [2.6, 6.0], "color": "#d84315", "opacity": 0.45, "label": "Outer Membrane"},
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
        pedagogical_reflection=(
            "Electrical action potentials propagate down the myelinated axon via rapid saltatory conduction across the "
            "Nodes of Ranvier, triggering neurotransmitter exocytosis at the synaptic terminal knobs!"
        ),
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
    "heart": Model3DSpec(
        model_type="procedural_scene",
        title="Human Heart (Cardiovascular Hemodynamics)",
        description="Four-chambered muscular organ pumping blood through systemic and pulmonary circulatory loops with unidirectional atrioventricular valves.",
        camera_position=(0.0, 2.0, 14.0),
        background_color="#07111e",
        pedagogical_reflection=(
            "Double circulation ensures deoxygenated blood is pumped by the right ventricle to the lungs, while oxygenated "
            "blood from the pulmonary veins is propelled by the thick muscular left ventricle through the systemic aorta!"
        ),
        annotations=[
            Model3DAnnotation(
                id="left_ventricle",
                label="Left Ventricle (Thick Myocardium)",
                description="High-pressure muscular chamber ejecting oxygenated blood into the aorta.",
                position=(1.8, -1.5, 0.0),
                color="#d32f2f",
            ),
            Model3DAnnotation(
                id="right_ventricle",
                label="Right Ventricle",
                description="Pumps deoxygenated blood into the pulmonary artery toward the pulmonary capillary beds.",
                position=(-1.8, -1.5, 0.0),
                color="#1976d2",
            ),
            Model3DAnnotation(
                id="aorta",
                label="Aortic Arch",
                description="Primary systemic artery distributing oxygenated blood throughout the human body.",
                position=(0.0, 3.5, 0.0),
                color="#ff5252",
            ),
        ],
        parameters={},
        elements=[
            {"id": "lv", "shape": "sphere", "position": [1.6, -1.2, 0.0], "size": [1.9], "color": "#b71c1c", "label": "Left Ventricle"},
            {"id": "rv", "shape": "sphere", "position": [-1.6, -1.2, 0.0], "size": [1.7], "color": "#0d47a1", "label": "Right Ventricle"},
            {"id": "la", "shape": "sphere", "position": [1.4, 1.2, 0.0], "size": [1.4], "color": "#c2185b", "label": "Left Atrium"},
            {"id": "ra", "shape": "sphere", "position": [-1.4, 1.2, 0.0], "size": [1.4], "color": "#1565c0", "label": "Right Atrium"},
            {"id": "aorta", "shape": "torus", "position": [0.0, 3.0, 0.0], "size": [1.5, 0.45], "color": "#ff1744", "rotation": [1.57, 0, 0], "label": "Aortic Arch"},
            {"id": "pulmonary", "shape": "cylinder", "position": [-0.8, 2.5, 0.5], "size": [0.45, 2.4], "color": "#2979ff", "label": "Pulmonary Artery"},
        ],
        connections=[
            {"from_id": "lv", "to_id": "aorta", "color": "#ff5252", "radius": 0.25},
            {"from_id": "rv", "to_id": "pulmonary", "color": "#448aff", "radius": 0.25},
        ],
    ),
    "plant_cell": Model3DSpec(
        model_type="procedural_scene",
        title="Plant Cell (Eukaryotic Photosynthetic Architecture)",
        description="Rigid cellulose cell wall enclosing chloroplasts, central sap vacuole, and nucleus for photosynthesis and turgor maintenance.",
        camera_position=(0.0, 3.0, 14.0),
        background_color="#07111e",
        pedagogical_reflection=(
            "Plant cells withstand hypotonic environments thanks to their rigid cellulose cell walls and large central "
            "vacuoles, while chlorophyll-packed thylakoid chloroplasts capture solar photons for carbon fixation!"
        ),
        annotations=[
            Model3DAnnotation(
                id="cell_wall",
                label="Cellulose Cell Wall",
                description="Rigid outer carbohydrate wall providing structural support against high osmotic turgor pressure.",
                position=(0.0, 3.8, 0.0),
                color="#2e7d32",
            ),
            Model3DAnnotation(
                id="chloroplast",
                label="Chloroplasts (Photosynthetic Sites)",
                description="Double-membrane organelles housing thylakoid grana stacks synthesizing glucose via light reactions.",
                position=(2.2, 1.0, 0.0),
                color="#00e676",
            ),
            Model3DAnnotation(
                id="vacuole",
                label="Central Vacuole",
                description="Large fluid-filled reservoir regulating cellular osmotic pressure and waste storage.",
                position=(-0.8, -0.4, 0.0),
                color="#4fc3f7",
            ),
        ],
        parameters={},
        elements=[
            {"id": "wall", "shape": "box", "position": [0.0, 0.0, 0.0], "size": [7.0, 5.5, 3.5], "color": "#2e7d32", "opacity": 0.35, "label": "Cell Wall"},
            {"id": "vacuole", "shape": "sphere", "position": [-0.8, -0.3, 0.0], "size": [1.9], "color": "#81d4fa", "opacity": 0.7, "label": "Central Vacuole"},
            {"id": "nucleus", "shape": "sphere", "position": [2.2, -1.2, 0.0], "size": [1.0], "color": "#7b1fa2", "label": "Nucleus"},
            {"id": "chloro1", "shape": "sphere", "position": [2.0, 1.4, 0.4], "size": [0.65], "color": "#00c853", "label": "Chloroplast 1"},
            {"id": "chloro2", "shape": "sphere", "position": [-2.0, 1.4, -0.4], "size": [0.65], "color": "#00c853", "label": "Chloroplast 2"},
            {"id": "chloro3", "shape": "sphere", "position": [-2.0, -1.4, 0.2], "size": [0.65], "color": "#00c853", "label": "Chloroplast 3"},
        ],
        connections=[],
    ),
    "prism": Model3DSpec(
        model_type="procedural_scene",
        title="Triangular Glass Prism (Dispersion of White Light)",
        description="Refractive glass prism dispersing incident polychromatic white light into its constituent VIBGYOR spectral frequencies according to Snell's law.",
        camera_position=(0.0, 2.0, 13.0),
        background_color="#07111e",
        pedagogical_reflection=(
            "Dispersion arises because refractive index varies inversely with wavelength (Cauchy's relation). Violet light "
            "slows down the most and bends the sharpest, while red light refracts least, revealing the continuous rainbow spectrum!"
        ),
        annotations=[
            Model3DAnnotation(
                id="prism_body",
                label="Equilateral Glass Prism",
                description="Homogeneous optical medium with refractive index n ≈ 1.52.",
                position=(0.0, 0.0, 0.0),
                color="#b0bec5",
            ),
            Model3DAnnotation(
                id="incident_ray",
                label="Incident White Light Ray",
                description="Polychromatic electromagnetic beam containing all visible wavelengths (400-700 nm).",
                position=(-4.0, 0.0, 0.0),
                color="#ffffff",
            ),
            Model3DAnnotation(
                id="spectrum",
                label="VIBGYOR Dispersed Spectrum",
                description="Angularly separated spectral colors arranged from red (least deviation) to violet (maximum deviation).",
                position=(4.5, 0.0, 0.0),
                color="#ab47bc",
            ),
        ],
        parameters={},
        elements=[
            {"id": "prism", "shape": "cylinder", "position": [0.0, 0.0, 0.0], "size": [2.8, 3.8], "color": "#cfd8dc", "opacity": 0.45, "label": "Glass Prism"},
            {"id": "ray_white", "shape": "cylinder", "position": [-3.5, -0.5, 0.0], "size": [0.12, 4.0], "color": "#ffffff", "rotation": [0, 0, 1.2], "label": "White Ray"},
            {"id": "ray_red", "shape": "cylinder", "position": [3.6, 0.8, 0.0], "size": [0.1, 4.2], "color": "#f44336", "rotation": [0, 0, -1.3], "label": "Red (700nm)"},
            {"id": "ray_yellow", "shape": "cylinder", "position": [3.7, 0.2, 0.0], "size": [0.1, 4.2], "color": "#ffeb3b", "rotation": [0, 0, -1.4], "label": "Yellow (580nm)"},
            {"id": "ray_green", "shape": "cylinder", "position": [3.8, -0.4, 0.0], "size": [0.1, 4.2], "color": "#4caf50", "rotation": [0, 0, -1.48], "label": "Green (530nm)"},
            {"id": "ray_blue", "shape": "cylinder", "position": [3.9, -1.0, 0.0], "size": [0.1, 4.2], "color": "#2196f3", "rotation": [0, 0, -1.55], "label": "Blue (470nm)"},
            {"id": "ray_violet", "shape": "cylinder", "position": [4.0, -1.6, 0.0], "size": [0.1, 4.2], "color": "#9c27b0", "rotation": [0, 0, -1.62], "label": "Violet (400nm)"},
        ],
        connections=[],
    ),
}


def get_3d_model(concept_or_key: str) -> Model3DSpec:
    """Retrieves or dynamically matches a curated 3D model specification for a given STEM concept."""
    norm = concept_or_key.lower().strip()

    # 1. Human Eye & Optics of Vision
    if any(k in norm for k in ["eye", "cornea", "retina", "pupil", "iris", "vision", "optic nerve", "eyeball", "ciliary"]):
        return PRESET_3D_MODELS["eye"]

    # 2. Genetics & Molecular Biology
    if any(k in norm for k in ["dna", "helix", "gene", "genetic", "chromosome", "nucleotide"]):
        return PRESET_3D_MODELS["dna"]

    # 3. Water & Polar Molecules
    if any(k in norm for k in ["water", "h2o", "ice", "steam", "liquid", "dipole"]):
        return PRESET_3D_MODELS["water"]

    # 4. Organic Hydrocarbons
    if any(k in norm for k in ["methane", "ch4", "hydrocarbon", "alkane"]):
        return PRESET_3D_MODELS["methane"]

    # 5. Organelles & Bioenergetics
    if any(k in norm for k in ["mitochondria", "mitochondrion", "atp", "cellular respiration", "organelle"]):
        return PRESET_3D_MODELS["mitochondria"]

    # 6. Neurobiology
    if any(k in norm for k in ["neuron", "brain cell", "axon", "synapse", "nervous system", "nerve"]):
        return PRESET_3D_MODELS["neuron"]

    # 7. Atomic Physics & Quantum
    if any(k in norm for k in ["atom", "electron", "proton", "neutron", "bohr", "nucleus", "quantum"]):
        return PRESET_3D_MODELS["atom"]

    # 8. Electromagnetism & Motors
    if any(k in norm for k in ["motor", "lorentz", "magnetic field", "magnet", "induction", "coil", "armature"]):
        return PRESET_3D_MODELS["motor"]

    # 9. Planetary Gravitation & Astrophysics
    if any(k in norm for k in ["solar", "orbit", "planet", "gravity", "earth", "kepler", "space", "sun"]):
        return PRESET_3D_MODELS["solar"]

    # 10. Cardiovascular System
    if any(k in norm for k in ["heart", "cardio", "ventricle", "atrium", "aorta", "circulation", "blood"]):
        return PRESET_3D_MODELS["heart"]

    # 11. Botany & Plant Anatomy
    if any(k in norm for k in ["plant cell", "chloroplast", "vacuole", "cell wall", "photosynthesis"]):
        return PRESET_3D_MODELS["plant_cell"]

    # 12. Wave Optics & Dispersion
    if any(k in norm for k in ["prism", "dispersion", "spectrum", "vibgyor", "refraction"]):
        return PRESET_3D_MODELS["prism"]

    return PRESET_3D_MODELS["dna"]


def _synthesize_procedural_scene(query: str) -> dict[str, Any]:
    """Smart deterministic science synthesizer when LLM generation is unavailable or offline."""
    q = query.lower().strip()
    words = [w.capitalize() for w in re.findall(r"[a-zA-Z0-9]+", query) if len(w) > 2][:4]
    title_words = " ".join(words) if words else "Scientific Structure"

    # Anatomy & Biological organs
    if any(k in q for k in ["lung", "respirat", "alveol", "breathing"]):
        return {
            "model_type": "procedural_scene",
            "title": "Human Respiratory System (Lungs & Bronchial Tree)",
            "description": "Bilateral lungs with branching trachea, primary bronchi, and alveolar capillary networks for O2/CO2 gas exchange.",
            "camera_position": [0, 1, 14],
            "background_color": "#07111e",
            "pedagogical_reflection": "Gas exchange occurs across the ultra-thin single-cell alveolar membrane driven by partial pressure gradients of oxygen and carbon dioxide!",
            "annotations": [
                {"id": "trachea", "label": "Trachea & Bronchi", "description": "Cartilaginous windpipe branching into left and right bronchial trees.", "position": [0, 3, 0], "color": "#e0e0e0"},
                {"id": "lungs", "label": "Left & Right Lung Lobes", "description": "Elastic spongy organs expanding during diaphragm contraction.", "position": [2.2, 0, 0], "color": "#ef5350"},
                {"id": "alveoli", "label": "Alveolar Clusters", "description": "Millions of microscopic air sacs providing ~70 m² of surface area.", "position": [2.6, -1.2, 0], "color": "#ff8a80"},
            ],
            "parameters": {},
            "elements": [
                {"id": "trachea", "shape": "cylinder", "position": [0, 2.8, 0], "size": [0.45, 3.2], "color": "#cfd8dc", "label": "Trachea"},
                {"id": "bronchus_r", "shape": "cylinder", "position": [-1.4, 1.2, 0], "size": [0.35, 2.0], "color": "#b0bec5", "rotation": [0, 0, 0.7], "label": "Right Bronchus"},
                {"id": "bronchus_l", "shape": "cylinder", "position": [1.4, 1.2, 0], "size": [0.35, 2.0], "color": "#b0bec5", "rotation": [0, 0, -0.7], "label": "Left Bronchus"},
                {"id": "lung_r", "shape": "sphere", "position": [-2.4, -0.6, 0], "size": [2.2], "color": "#e57373", "opacity": 0.8, "label": "Right Lung"},
                {"id": "lung_l", "shape": "sphere", "position": [2.4, -0.6, 0], "size": [2.0], "color": "#e57373", "opacity": 0.8, "label": "Left Lung"},
            ],
            "connections": [
                {"from_id": "trachea", "to_id": "bronchus_r", "color": "#ffffff", "radius": 0.18},
                {"from_id": "trachea", "to_id": "bronchus_l", "color": "#ffffff", "radius": 0.18},
            ],
        }

    # Chemistry: Ammonia / general molecule
    if any(k in q for k in ["ammonia", "nh3", "nitrogen"]):
        return {
            "model_type": "procedural_scene",
            "title": "Ammonia Molecule (NH₃) — Trigonal Pyramidal",
            "description": "Central nitrogen atom with one lone pair and three covalent N-H bonds forming a trigonal pyramid with 107° bond angles.",
            "camera_position": [0, 2, 10],
            "background_color": "#07111e",
            "pedagogical_reflection": "Due to lone pair-bond pair repulsion in VSEPR theory, the bond angle compresses from the regular tetrahedral 109.5° to 107.0°!",
            "annotations": [
                {"id": "nitrogen", "label": "Nitrogen (N)", "description": "Central atom with sp³ hybridization and one localized lone electron pair.", "position": [0, 0.8, 0], "color": "#1976d2"},
                {"id": "hydrogen", "label": "Hydrogen Atoms (3x)", "description": "Forming polar covalent single bonds at 107° spacing.", "position": [1.8, -1.0, 0], "color": "#ffffff"},
            ],
            "parameters": {},
            "elements": [
                {"id": "nitrogen", "shape": "sphere", "position": [0, 0.6, 0], "size": [1.4], "color": "#1565c0", "label": "Nitrogen (N)"},
                {"id": "h1", "shape": "sphere", "position": [1.8, -1.0, 0], "size": [0.75], "color": "#ffffff", "label": "Hydrogen (H₁)"},
                {"id": "h2", "shape": "sphere", "position": [-0.9, -1.0, 1.5], "size": [0.75], "color": "#ffffff", "label": "Hydrogen (H₂)"},
                {"id": "h3", "shape": "sphere", "position": [-0.9, -1.0, -1.5], "size": [0.75], "color": "#ffffff", "label": "Hydrogen (H₃)"},
            ],
            "connections": [
                {"from_id": "nitrogen", "to_id": "h1", "color": "#64b5f6", "radius": 0.18},
                {"from_id": "nitrogen", "to_id": "h2", "color": "#64b5f6", "radius": 0.18},
                {"from_id": "nitrogen", "to_id": "h3", "color": "#64b5f6", "radius": 0.18},
            ],
        }

    # Physics / Optics: Telescope / Microscope / Lens
    if any(k in q for k in ["telescope", "microscope", "convex", "concave", "optics"]):
        return {
            "model_type": "procedural_scene",
            "title": f"{title_words} (Optical System & Refraction)",
            "description": "Multi-lens optical assembly refracting incident light rays along the principal axis to form magnified images.",
            "camera_position": [0, 2, 13],
            "background_color": "#07111e",
            "pedagogical_reflection": "Optical magnification is governed by the lens formula (1/f = 1/v - 1/u) and linear magnification ratios (m = v/u)!",
            "annotations": [
                {"id": "objective", "label": "Objective Lens", "description": "Large aperture lens gathering incident parallel rays.", "position": [-4, 0, 0], "color": "#00e5ff"},
                {"id": "focal", "label": "Principal Focal Point", "description": "Convergence point where intermediate real inverted image forms.", "position": [0, 0, 0], "color": "#ffd600"},
                {"id": "eyepiece", "label": "Eyepiece Lens", "description": "Magnifies the intermediate image to create enlarged virtual view for the eye.", "position": [4, 0, 0], "color": "#00e5ff"},
            ],
            "parameters": {},
            "elements": [
                {"id": "axis", "shape": "cylinder", "position": [0, 0, 0], "size": [0.08, 12], "color": "#90a4ae", "rotation": [0, 0, 1.57], "label": "Optical Axis"},
                {"id": "obj_lens", "shape": "sphere", "position": [-4, 0, 0], "size": [1.8], "color": "#80deea", "opacity": 0.55, "label": "Objective Lens"},
                {"id": "focus_point", "shape": "sphere", "position": [0, 0, 0], "size": [0.4], "color": "#ffeb3b", "emissive": "#ffeb3b", "label": "Focal Point"},
                {"id": "eye_lens", "shape": "sphere", "position": [4, 0, 0], "size": [1.3], "color": "#80deea", "opacity": 0.55, "label": "Eyepiece Lens"},
            ],
            "connections": [
                {"from_id": "obj_lens", "to_id": "focus_point", "color": "#ffeb3b", "radius": 0.12},
                {"from_id": "focus_point", "to_id": "eye_lens", "color": "#ffeb3b", "radius": 0.12},
            ],
        }

    # Universal structural science synthesizer
    return {
        "model_type": "procedural_scene",
        "title": f"{title_words} — Interactive 3D Model",
        "description": f"Dynamic procedural representation of {title_words} showing core interactive structural components.",
        "camera_position": [0, 2, 12],
        "background_color": "#07111e",
        "pedagogical_reflection": f"Notice how the functional sub-units of {title_words} organize symmetrically around the central core to optimize energy and stability!",
        "annotations": [
            {"id": "core", "label": f"{title_words} Core", "description": "Primary structural or reactive center.", "position": [0, 0, 0], "color": "#00e5ff"},
            {"id": "subunit_a", "label": "Functional Unit Alpha", "description": "First interactive coordinate subunit.", "position": [2.8, 1.2, 0], "color": "#fe9832"},
            {"id": "subunit_b", "label": "Functional Unit Beta", "description": "Second interactive coordinate subunit.", "position": [-2.8, -1.2, 0], "color": "#00b47d"},
        ],
        "parameters": {},
        "elements": [
            {"id": "core", "shape": "sphere", "position": [0, 0, 0], "size": [1.6], "color": "#00bcd4", "label": "Primary Core"},
            {"id": "node1", "shape": "sphere", "position": [2.8, 1.2, 0], "size": [0.9], "color": "#fe9832", "label": "Subunit Alpha"},
            {"id": "node2", "shape": "sphere", "position": [-2.8, -1.2, 0], "size": [0.9], "color": "#00b47d", "label": "Subunit Beta"},
            {"id": "orbital", "shape": "torus", "position": [0, 0, 0], "size": [3.2, 0.15], "color": "#90caf9", "label": "Interaction Ring"},
        ],
        "connections": [
            {"from_id": "core", "to_id": "node1", "color": "#ffffff", "radius": 0.15},
            {"from_id": "core", "to_id": "node2", "color": "#ffffff", "radius": 0.15},
        ],
    }


def generate_custom_3d_concept(prompt_query: str) -> dict[str, Any]:
    """Uses curated presets, LLM, or procedural synthesizer to build an interactive 3D model for any concept."""
    norm = prompt_query.lower().strip()

    # 1. Fast match against curated high-fidelity presets
    if any(k in norm for k in ["eye", "cornea", "retina", "pupil", "iris", "vision", "optic nerve", "eyeball", "ciliary"]):
        return PRESET_3D_MODELS["eye"].to_dict()
    if any(k in norm for k in ["heart", "cardio", "ventricle", "atrium", "aorta", "circulation", "blood"]):
        return PRESET_3D_MODELS["heart"].to_dict()
    if any(k in norm for k in ["plant", "chloroplast", "vacuole", "cell wall"]):
        return PRESET_3D_MODELS["plant_cell"].to_dict()
    if any(k in norm for k in ["prism", "dispersion", "spectrum", "rainbow", "vibgyor"]):
        return PRESET_3D_MODELS["prism"].to_dict()
    if any(k in norm for k in ["water", "h2o", "ice", "steam"]):
        return PRESET_3D_MODELS["water"].to_dict()
    if any(k in norm for k in ["methane", "ch4", "hydrocarbon"]):
        return PRESET_3D_MODELS["methane"].to_dict()
    if any(k in norm for k in ["mitochondria", "mitochondrion", "atp"]):
        return PRESET_3D_MODELS["mitochondria"].to_dict()
    if any(k in norm for k in ["neuron", "brain cell", "axon", "synapse"]):
        return PRESET_3D_MODELS["neuron"].to_dict()
    if any(k in norm for k in ["atom", "bohr", "electron", "proton", "quantum"]):
        return PRESET_3D_MODELS["atom"].to_dict()
    if any(k in norm for k in ["motor", "lorentz", "induction"]):
        return PRESET_3D_MODELS["motor"].to_dict()
    if any(k in norm for k in ["solar", "planet", "orbit", "earth", "sun"]):
        return PRESET_3D_MODELS["solar"].to_dict()
    if any(k in norm for k in ["dna", "helix", "gene", "chromosome"]):
        return PRESET_3D_MODELS["dna"].to_dict()

    # 2. Dynamic LLM generation for novel prompts
    sys_prompt = (
        "You are the Bharat 3D Lab WebGL Architect. Generate a JSON procedural 3D model specification for Three.js. "
        "The model_type MUST be 'procedural_scene'. "
        "Include: "
        "- title: descriptive title "
        "- description: pedagogical 1-line concept explanation "
        "- pedagogical_reflection: insightful 1-2 sentence reflection for students "
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
        if isinstance(data, dict) and "title" in data and not data.get("mock"):
            data["model_type"] = "procedural_scene"
            if "elements" not in data or not isinstance(data["elements"], list):
                fallback = _synthesize_procedural_scene(prompt_query)
                data["elements"] = fallback["elements"]
                data["connections"] = fallback["connections"]
            return data
    except Exception as exc:
        print(f"[3D Generator] LLM generation fallback: {exc}")

    # 3. Intelligent deterministic procedural synthesizer (never generic water molecule)
    return _synthesize_procedural_scene(prompt_query)
