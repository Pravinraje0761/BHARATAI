/**
 * Bharat 3D Lab™ - Interactive WebGL Science Visualizer
 * Powered by Three.js
 * Renders interactive DNA Double Helix, Bohr Atom, Electric Motor, and Solar System
 */

class Bharat3DLab {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.controls = null;
    this.currentModelType = null;
    this.modelGroup = null;
    this.isRotating = true;
    this.rotationSpeed = 0.008;
    this.animationFrameId = null;
    this.dynamicObjects = [];
    this.unwindFactor = 0.0; // 0 = helical, 1 = unzipped ladder
    this.currentSpec = null;

    if (this.container) {
      this.init();
    }
  }

  init() {
    // 1. Scene setup
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x07111e);

    // 2. Camera setup
    const w = this.container.clientWidth || 800;
    const h = this.container.clientHeight || 500;
    this.camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 1000);
    this.camera.position.set(0, 4, 18);

    // 3. Renderer setup
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setSize(w, h);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.container.innerHTML = '';
    this.container.appendChild(this.renderer.domElement);

    // 4. Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
    this.scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0xffffff, 1.2);
    dirLight1.position.set(10, 20, 15);
    this.scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0x00e5ff, 0.6);
    dirLight2.position.set(-10, -10, -10);
    this.scene.add(dirLight2);

    const pointLight = new THREE.PointLight(0xfe9832, 1.0, 50);
    pointLight.position.set(0, 0, 10);
    this.scene.add(pointLight);

    // 5. Orbit Controls
    if (typeof THREE.OrbitControls !== 'undefined') {
      this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
      this.controls.enableDamping = true;
      this.controls.dampingFactor = 0.05;
      this.controls.maxDistance = 60;
      this.controls.minDistance = 3;
    }

    // 6. Model Root Group
    this.modelGroup = new THREE.Group();
    this.scene.add(this.modelGroup);

    // Handle Resize
    window.addEventListener('resize', () => this.onResize());

    // Start loop
    this.animate();

    // Load default DNA model
    this.loadModel('dna');
  }

  onResize() {
    if (!this.container || !this.camera || !this.renderer) return;
    const w = this.container.clientWidth;
    const h = this.container.clientHeight;
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h);
  }

  clearModel() {
    while (this.modelGroup.children.length > 0) {
      const obj = this.modelGroup.children[0];
      this.modelGroup.remove(obj);
      if (obj.geometry) obj.geometry.dispose();
      if (obj.material) {
        if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose());
        else obj.material.dispose();
      }
    }
    this.dynamicObjects = [];
  }

  async loadModel(conceptOrKey) {
    try {
      const res = await fetch(`/api/3d/model?concept=${encodeURIComponent(conceptOrKey)}`);
      const spec = await res.json();
      this.renderSpec(spec);
    } catch (err) {
      console.error('Failed to load 3D model spec from server, using local fallback:', err);
      this.renderDNAHelix();
    }
  }

  renderSpec(spec) {
    this.currentSpec = spec;
    this.clearModel();
    this.currentModelType = spec.model_type;

    // Update UI title and description
    const titleEl = document.getElementById('3d-model-title');
    const descEl = document.getElementById('3d-model-description');
    if (titleEl) titleEl.textContent = spec.title;
    if (descEl) descEl.textContent = spec.description;

    // Update annotations panel
    this.renderAnnotationsUI(spec.annotations);

    if (spec.camera_position && this.camera) {
      this.camera.position.set(...spec.camera_position);
      if (this.controls) this.controls.target.set(0, 0, 0);
    }

    // Toggle DNA legend visibility
    const dnaLegend = document.getElementById('dna-legend');
    if (dnaLegend) {
      if (spec.model_type === 'dna_helix') dnaLegend.classList.remove('hidden');
      else dnaLegend.classList.add('hidden');
    }

    if (spec.model_type === 'dna_helix') {
      this.renderDNAHelix(spec.parameters);
    } else if (spec.model_type === 'bohr_atom') {
      this.renderBohrAtom(spec.parameters);
    } else if (spec.model_type === 'electric_motor') {
      this.renderElectricMotor(spec.parameters);
    } else if (spec.model_type === 'solar_orbits') {
      this.renderSolarSystem(spec.parameters);
    } else {
      this.renderProceduralScene(spec);
    }
  }

  // ------------------------------------------------------------------------- //
  // Universal Procedural 3D Scientific Scene Generator (Molecules, Cells, Atoms)
  // ------------------------------------------------------------------------- //
  renderProceduralScene(spec) {
    const elements = spec.elements || [];
    const connections = spec.connections || [];
    const elementMap = {};

    elements.forEach(el => {
      let geo;
      const [sx = 1, sy = 1, sz = 1] = el.size || [1, 1, 1];

      if (el.shape === 'sphere') {
        geo = new THREE.SphereGeometry(sx, 24, 24);
      } else if (el.shape === 'box') {
        geo = new THREE.BoxGeometry(sx, sy || sx, sz || sx);
      } else if (el.shape === 'cylinder') {
        geo = new THREE.CylinderGeometry(sx, sx, sy || 2, 20);
      } else if (el.shape === 'cone') {
        geo = new THREE.ConeGeometry(sx, sy || 2, 20);
      } else if (el.shape === 'torus') {
        geo = new THREE.TorusGeometry(sx, sy || 0.25, 16, 48);
      } else if (el.shape === 'capsule') {
        geo = new THREE.CylinderGeometry(sx, sx, sy || 4, 24);
      } else {
        geo = new THREE.SphereGeometry(sx, 20, 20);
      }

      const col = el.color ? parseInt(el.color.replace('#', '0x'), 16) : 0x4fc3f7;
      const em = el.emissive ? parseInt(el.emissive.replace('#', '0x'), 16) : 0x000000;

      const mat = new THREE.MeshStandardMaterial({
        color: col,
        roughness: 0.35,
        metalness: 0.25,
        emissive: em,
        transparent: (el.opacity && el.opacity < 1.0) ? true : false,
        opacity: el.opacity !== undefined ? el.opacity : 1.0,
      });

      const mesh = new THREE.Mesh(geo, mat);
      const [px = 0, py = 0, pz = 0] = el.position || [0, 0, 0];
      mesh.position.set(px, py, pz);

      if (el.rotation) {
        mesh.rotation.set(...el.rotation);
      }

      this.modelGroup.add(mesh);
      elementMap[el.id] = mesh;
    });

    connections.forEach(conn => {
      const m1 = elementMap[conn.from_id];
      const m2 = elementMap[conn.to_id];
      if (m1 && m2) {
        const col = conn.color ? parseInt(conn.color.replace('#', '0x'), 16) : 0xffffff;
        const mat = new THREE.MeshStandardMaterial({
          color: col,
          roughness: 0.4,
          metalness: 0.3,
        });
        const cyl = this.createCylinderBetweenPoints(
          m1.position,
          m2.position,
          conn.radius || 0.16,
          mat
        );
        this.modelGroup.add(cyl);
      }
    });
  }

  renderAnnotationsUI(annotations) {
    const listEl = document.getElementById('3d-annotations-list');
    if (!listEl) return;
    listEl.innerHTML = '';

    if (!annotations || annotations.length === 0) return;

    annotations.forEach(a => {
      const btn = document.createElement('button');
      btn.className = 'w-full text-left p-3 rounded-xl bg-surface border border-outline-variant/30 hover:border-primary transition-all space-y-1 group';
      btn.innerHTML = `
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full" style="background-color: ${a.color}"></span>
          <span class="font-bold text-[13px] text-on-surface group-hover:text-primary transition-colors">${a.label}</span>
        </div>
        <p class="text-[11px] text-on-surface-variant leading-normal">${a.description}</p>
      `;
      btn.addEventListener('click', () => this.focusAnnotation(a));
      listEl.appendChild(btn);
    });
  }

  focusAnnotation(annotation) {
    if (!annotation || !annotation.position) return;
    const [x, y, z] = annotation.position;

    // Smoothly pan controls target towards the annotation position
    if (this.controls) {
      this.controls.target.set(x, y, z);
    }

    // Spawn a temporary highlight beacon
    const beaconGeo = new THREE.SphereGeometry(0.5, 16, 16);
    const beaconMat = new THREE.MeshBasicMaterial({ color: annotation.color, wireframe: true });
    const beacon = new THREE.Mesh(beaconGeo, beaconMat);
    beacon.position.set(x, y, z);
    this.modelGroup.add(beacon);

    let pulse = 0;
    const pulseInterval = setInterval(() => {
      pulse++;
      beacon.scale.multiplyScalar(1.08);
      if (pulse > 15) {
        clearInterval(pulseInterval);
        this.modelGroup.remove(beacon);
      }
    }, 50);
  }

  // ------------------------------------------------------------------------- //
  // 1. DNA Double Helix 3D Generator
  // ------------------------------------------------------------------------- //
  renderDNAHelix(params = {}) {
    const radius = params.radius || 3.2;
    const height = params.height || 18.0;
    const turns = params.turns || 3;
    const count = params.base_pairs_count || 38;

    const baseColors = {
      'A': 0xfe9832, // Orange: Adenine
      'T': 0xd9381e, // Red: Thymine
      'G': 0x00b47d, // Emerald: Guanine
      'C': 0x9c27b0, // Purple: Cytosine
    };

    const pairTypes = [['A', 'T'], ['G', 'C'], ['T', 'A'], ['C', 'G']];

    const backboneMat1 = new THREE.MeshStandardMaterial({
      color: 0x1a73e8,
      roughness: 0.3,
      metalness: 0.6,
      emissive: 0x0a2b66,
      emissiveIntensity: 0.3,
    });

    const backboneMat2 = new THREE.MeshStandardMaterial({
      color: 0x00e5ff,
      roughness: 0.3,
      metalness: 0.6,
      emissive: 0x005566,
      emissiveIntensity: 0.3,
    });

    const sphereGeo = new THREE.SphereGeometry(0.35, 16, 16);

    for (let i = 0; i < count; i++) {
      const t = i / (count - 1);
      const angle = t * Math.PI * 2 * turns;
      const y = (t - 0.5) * height;

      // Strand 1 Position
      const x1 = Math.cos(angle) * radius;
      const z1 = Math.sin(angle) * radius;

      // Strand 2 Position (180 deg offset)
      const x2 = Math.cos(angle + Math.PI) * radius;
      const z2 = Math.sin(angle + Math.PI) * radius;

      // Backbone Nodes
      const bNode1 = new THREE.Mesh(sphereGeo, backboneMat1);
      bNode1.position.set(x1, y, z1);
      this.modelGroup.add(bNode1);

      const bNode2 = new THREE.Mesh(sphereGeo, backboneMat2);
      bNode2.position.set(x2, y, z2);
      this.modelGroup.add(bNode2);

      // Connect Base Pairs (Rung of the ladder)
      const [baseL, baseR] = pairTypes[i % pairTypes.length];
      const midPointX = (x1 + x2) / 2;
      const midPointZ = (z1 + z2) / 2;

      // Left Half Rung
      const rungMatL = new THREE.MeshStandardMaterial({
        color: baseColors[baseL],
        roughness: 0.4,
        metalness: 0.3,
      });
      const leftCyl = this.createCylinderBetweenPoints(
        new THREE.Vector3(x1, y, z1),
        new THREE.Vector3(midPointX, y, midPointZ),
        0.18,
        rungMatL
      );
      this.modelGroup.add(leftCyl);

      // Right Half Rung
      const rungMatR = new THREE.MeshStandardMaterial({
        color: baseColors[baseR],
        roughness: 0.4,
        metalness: 0.3,
      });
      const rightCyl = this.createCylinderBetweenPoints(
        new THREE.Vector3(midPointX, y, midPointZ),
        new THREE.Vector3(x2, y, z2),
        0.18,
        rungMatR
      );
      this.modelGroup.add(rightCyl);

      // Hydrogen Bond Node at Center
      const hBondGeo = new THREE.SphereGeometry(0.18, 8, 8);
      const hBondMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
      const hNode = new THREE.Mesh(hBondGeo, hBondMat);
      hNode.position.set(midPointX, y, midPointZ);
      this.modelGroup.add(hNode);
    }
  }

  createCylinderBetweenPoints(p1, p2, radius, material) {
    const dist = p1.distanceTo(p2);
    const geom = new THREE.CylinderGeometry(radius, radius, dist, 12);
    const mesh = new THREE.Mesh(geom, material);

    const mid = new THREE.Vector3().addVectors(p1, p2).multiplyScalar(0.5);
    mesh.position.copy(mid);

    const dir = new THREE.Vector3().subVectors(p2, p1).normalize();
    const up = new THREE.Vector3(0, 1, 0);
    const quat = new THREE.Quaternion().setFromUnitVectors(up, dir);
    mesh.setRotationFromQuaternion(quat);

    return mesh;
  }

  // ------------------------------------------------------------------------- //
  // 2. Bohr Atomic Model (Protons, Neutrons, Quantized Electron Shells)
  // ------------------------------------------------------------------------- //
  renderBohrAtom(params = {}) {
    const nucleusGroup = new THREE.Group();
    this.modelGroup.add(nucleusGroup);

    // Nucleus (Protons = Red, Neutrons = Light Blue)
    const nucleonGeo = new THREE.SphereGeometry(0.55, 16, 16);
    const protonMat = new THREE.MeshStandardMaterial({ color: 0xff3b30, roughness: 0.3, emissive: 0x660000 });
    const neutronMat = new THREE.MeshStandardMaterial({ color: 0x00bcd4, roughness: 0.3, emissive: 0x004455 });

    const totalNucleons = (params.protons || 6) + (params.neutrons || 6);
    for (let i = 0; i < totalNucleons; i++) {
      const mesh = new THREE.Mesh(nucleonGeo, i % 2 === 0 ? protonMat : neutronMat);
      mesh.position.set(
        (Math.random() - 0.5) * 1.8,
        (Math.random() - 0.5) * 1.8,
        (Math.random() - 0.5) * 1.8
      );
      nucleusGroup.add(mesh);
    }

    // Electron Shells
    const shells = params.shells || [
      { radius: 4.2, electrons: 2, speed: 0.035, tilt: 0.3 },
      { radius: 7.8, electrons: 4, speed: 0.02, tilt: -0.4 },
    ];

    shells.forEach((sh, shIdx) => {
      // Ring orbit line
      const ringGeo = new THREE.RingGeometry(sh.radius - 0.04, sh.radius + 0.04, 64);
      const ringMat = new THREE.MeshBasicMaterial({ color: 0x4fc3f7, side: THREE.DoubleSide, opacity: 0.4, transparent: true });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.rotation.x = Math.PI / 2 + sh.tilt;
      ring.rotation.y = shIdx * 0.5;
      this.modelGroup.add(ring);

      // Orbiting Electrons
      const eGeo = new THREE.SphereGeometry(0.3, 16, 16);
      const eMat = new THREE.MeshStandardMaterial({ color: 0x00e676, emissive: 0x00e676, emissiveIntensity: 0.7 });

      for (let e = 0; e < sh.electrons; e++) {
        const eMesh = new THREE.Mesh(eGeo, eMat);
        this.modelGroup.add(eMesh);
        this.dynamicObjects.push({
          mesh: eMesh,
          radius: sh.radius,
          angle: (e / sh.electrons) * Math.PI * 2,
          speed: sh.speed,
          tilt: sh.tilt,
          shIdx: shIdx,
        });
      }
    });
  }

  // ------------------------------------------------------------------------- //
  // 3. DC Electric Motor & Lorentz Force
  // ------------------------------------------------------------------------- //
  renderElectricMotor(params = {}) {
    // Permanent Magnets (North = Red, South = Blue)
    const magnetGeo = new THREE.BoxGeometry(3, 5, 8);
    const northMat = new THREE.MeshStandardMaterial({ color: 0xd32f2f, roughness: 0.4 });
    const southMat = new THREE.MeshStandardMaterial({ color: 0x1976d2, roughness: 0.4 });

    const magnetN = new THREE.Mesh(magnetGeo, northMat);
    magnetN.position.set(-8.5, 0, 0);
    this.modelGroup.add(magnetN);

    const magnetS = new THREE.Mesh(magnetGeo, southMat);
    magnetS.position.set(8.5, 0, 0);
    this.modelGroup.add(magnetS);

    // Magnetic Flux Lines (B-Field Arrows)
    for (let y = -2; y <= 2; y += 1) {
      for (let z = -2; z <= 2; z += 1.5) {
        const lineMat = new THREE.LineBasicMaterial({ color: 0x81d4fa, opacity: 0.5, transparent: true });
        const points = [new THREE.Vector3(-7, y, z), new THREE.Vector3(7, y, z)];
        const lineGeo = new THREE.BufferGeometry().setFromPoints(points);
        this.modelGroup.add(new THREE.Line(lineGeo, lineMat));
      }
    }

    // Rotating Armature Coil
    const armatureGroup = new THREE.Group();
    this.modelGroup.add(armatureGroup);

    const coilMat = new THREE.MeshStandardMaterial({ color: 0xffb300, roughness: 0.2, metalness: 0.8 });
    const w = 5.0, h = 6.0;

    // Rectangle loop of wire
    const t = 0.2;
    const topBar = new THREE.Mesh(new THREE.CylinderGeometry(t, t, w, 12), coilMat);
    topBar.rotation.z = Math.PI / 2;
    topBar.position.set(0, h / 2, 0);
    armatureGroup.add(topBar);

    const botBar = new THREE.Mesh(new THREE.CylinderGeometry(t, t, w, 12), coilMat);
    botBar.rotation.z = Math.PI / 2;
    botBar.position.set(0, -h / 2, 0);
    armatureGroup.add(botBar);

    const leftBar = new THREE.Mesh(new THREE.CylinderGeometry(t, t, h, 12), coilMat);
    leftBar.position.set(-w / 2, 0, 0);
    armatureGroup.add(leftBar);

    const rightBar = new THREE.Mesh(new THREE.CylinderGeometry(t, t, h, 12), coilMat);
    rightBar.position.set(w / 2, 0, 0);
    armatureGroup.add(rightBar);

    // Central Axle
    const axleMat = new THREE.MeshStandardMaterial({ color: 0x757575, metalness: 0.9 });
    const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 12, 16), axleMat);
    armatureGroup.add(axle);

    // Register rotation
    this.dynamicObjects.push({
      type: 'motor_armature',
      group: armatureGroup,
      speed: 0.05,
    });
  }

  // ------------------------------------------------------------------------- //
  // 4. Solar System Orbits
  // ------------------------------------------------------------------------- //
  renderSolarSystem(params = {}) {
    // Sun
    const sunGeo = new THREE.SphereGeometry(2.5, 32, 32);
    const sunMat = new THREE.MeshBasicMaterial({ color: 0xffd54f });
    const sun = new THREE.Mesh(sunGeo, sunMat);
    this.modelGroup.add(sun);

    const planets = params.planets || [
      { name: 'Mercury', dist: 4.8, size: 0.5, color: 0xa1887f, speed: 0.04 },
      { name: 'Venus', dist: 7.5, size: 0.8, color: 0xffe082, speed: 0.025 },
      { name: 'Earth', dist: 11.0, size: 0.95, color: 0x4fc3f7, speed: 0.018 },
      { name: 'Mars', dist: 15.0, size: 0.65, color: 0xff7043, speed: 0.012 },
    ];

    planets.forEach(p => {
      // Orbit Path Ring
      const orbitGeo = new THREE.RingGeometry(p.dist - 0.03, p.dist + 0.03, 64);
      const orbitMat = new THREE.MeshBasicMaterial({ color: 0xffffff, opacity: 0.2, transparent: true, side: THREE.DoubleSide });
      const orbitRing = new THREE.Mesh(orbitGeo, orbitMat);
      orbitRing.rotation.x = Math.PI / 2;
      this.modelGroup.add(orbitRing);

      // Planet Sphere
      const pGeo = new THREE.SphereGeometry(p.size, 16, 16);
      const pMat = new THREE.MeshStandardMaterial({ color: p.color, roughness: 0.5 });
      const pMesh = new THREE.Mesh(pGeo, pMat);
      this.modelGroup.add(pMesh);

      this.dynamicObjects.push({
        type: 'planet',
        mesh: pMesh,
        dist: p.dist,
        speed: p.speed,
        angle: Math.random() * Math.PI * 2,
      });
    });
  }

  // ------------------------------------------------------------------------- //
  // Animation Loop
  // ------------------------------------------------------------------------- //
  animate() {
    this.animationFrameId = requestAnimationFrame(() => this.animate());

    // Auto rotate model group
    if (this.isRotating && this.modelGroup) {
      this.modelGroup.rotation.y += this.rotationSpeed;
    }

    // Dynamic animation elements (electrons, armature, planets)
    this.dynamicObjects.forEach(obj => {
      if (obj.mesh && obj.radius) {
        // Bohr electron
        obj.angle += obj.speed;
        const x = Math.cos(obj.angle) * obj.radius;
        const z = Math.sin(obj.angle) * obj.radius;
        const y = Math.sin(obj.angle) * (obj.radius * Math.sin(obj.tilt));
        obj.mesh.position.set(x, y, z);
      } else if (obj.type === 'motor_armature') {
        obj.group.rotation.y += obj.speed;
      } else if (obj.type === 'planet') {
        obj.angle += obj.speed;
        obj.mesh.position.x = Math.cos(obj.angle) * obj.dist;
        obj.mesh.position.z = Math.sin(obj.angle) * obj.dist;
      }
    });

    if (this.controls) {
      this.controls.update();
    }

    if (this.renderer && this.scene && this.camera) {
      this.renderer.render(this.scene, this.camera);
    }
  }

  toggleRotation() {
    this.isRotating = !this.isRotating;
    return this.isRotating;
  }

  setSpeed(speed) {
    this.rotationSpeed = speed;
  }

  resetCamera() {
    if (this.camera && this.controls) {
      this.camera.position.set(0, 4, 18);
      this.controls.target.set(0, 0, 0);
    }
  }
}

// Global visualizer instance
window.Bharat3DLab = Bharat3DLab;
