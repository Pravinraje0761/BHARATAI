/**
 * Interactive Knowledge Graph Canvas for BHARATGURU
 * Visualizes conceptual mastery, prerequisite dependencies, confidence, and retention decay.
 */

class KnowledgeGraphVisualizer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.nodes = [];
    this.links = [];
    this.particles = [];
    this.hoveredNode = null;
    this.selectedNode = null;
    this.animationId = null;

    // Clean slate: start empty unless explicitly populated or demo mode
    this.nodes = [];
    this.links = [];
    this.particles = [];

    this.resize();
    this.bindEvents();
    this.animate();
  }

  loadDemoCurriculum() {
    this.initDefaultData();
  }

  initDefaultData() {
    this.nodes = [
      { id: 'Electric Current', label: 'Electric Current', x: 0.18, y: 0.45, radius: 24, status: 'mastered', mastery: 85, confidence: 0.9, domain: 'Electricity', attempts: 4, misconceptions: [] },
      { id: 'Potential Difference (Voltage)', label: 'Voltage (Potential Diff)', x: 0.35, y: 0.28, radius: 26, status: 'mastered', mastery: 80, confidence: 0.85, domain: 'Electricity', attempts: 3, misconceptions: [] },
      { id: "Resistance and Ohm's law", label: "Ohm's Law & Resistance", x: 0.45, y: 0.62, radius: 28, status: 'needs-remediation', mastery: 55, confidence: 0.6, domain: 'Electricity', attempts: 5, misconceptions: ["Current rises with resistance"] },
      { id: 'Joule Heating & Electric Power', label: 'Joule Heating & Power', x: 0.60, y: 0.38, radius: 22, status: 'ready-to-learn', mastery: 20, confidence: 0.5, domain: 'Electricity', attempts: 1, misconceptions: [] },
      { id: 'Series and parallel resistor networks', label: 'Series & Parallel Networks', x: 0.68, y: 0.70, radius: 26, status: 'in-progress', mastery: 42, confidence: 0.65, domain: 'Electricity', attempts: 2, misconceptions: [] },
      { id: 'Magnetic Effects of Current', label: 'Magnetic Effects', x: 0.82, y: 0.35, radius: 24, status: 'ready-to-learn', mastery: 15, confidence: 0.4, domain: 'Electromagnetism', attempts: 0, misconceptions: [] },
      { id: 'Electromagnetic Induction', label: 'EM Induction', x: 0.90, y: 0.60, radius: 22, status: 'locked', mastery: 0, confidence: 0.3, domain: 'Electromagnetism', attempts: 0, misconceptions: [] }
    ];

    this.links = [
      { source: 'Electric Current', target: "Resistance and Ohm's law" },
      { source: 'Potential Difference (Voltage)', target: "Resistance and Ohm's law" },
      { source: "Resistance and Ohm's law", target: 'Joule Heating & Electric Power' },
      { source: "Resistance and Ohm's law", target: 'Series and parallel resistor networks' },
      { source: 'Electric Current', target: 'Magnetic Effects of Current' },
      { source: 'Magnetic Effects of Current', target: 'Electromagnetic Induction' }
    ];

    this.initParticles();
  }

  initParticles() {
    this.particles = [];
    for (let i = 0; i < 24; i++) {
      this.particles.push({
        linkIndex: Math.floor(Math.random() * this.links.length),
        t: Math.random(),
        speed: 0.003 + Math.random() * 0.004
      });
    }
  }

  updateWithApiData(apiGraph) {
    if (!apiGraph || !apiGraph.nodes || apiGraph.nodes.length === 0) return;

    const existingCoords = {
      'Electric Current': { x: 0.18, y: 0.45 },
      'Potential Difference (Voltage)': { x: 0.35, y: 0.28 },
      "Resistance and Ohm's law": { x: 0.45, y: 0.62 },
      'Joule Heating & Electric Power': { x: 0.60, y: 0.38 },
      'Series and parallel resistor networks': { x: 0.68, y: 0.70 },
      'Magnetic Effects of Current': { x: 0.82, y: 0.35 },
      'Electromagnetic Induction': { x: 0.90, y: 0.60 },
      "Maxwell's Equations": { x: 0.92, y: 0.25 },
      "Newton's First Law & Inertia": { x: 0.20, y: 0.75 },
      "Newton's Second Law (F = ma)": { x: 0.40, y: 0.85 },
      "Newton's Third Law (Action-Reaction)": { x: 0.60, y: 0.85 },
      "Conservation of Momentum": { x: 0.80, y: 0.85 }
    };

    this.nodes = apiGraph.nodes.map((n, idx) => {
      const coord = existingCoords[n.concept] || {
        x: 0.15 + (idx % 4) * 0.24,
        y: 0.25 + Math.floor(idx / 4) * 0.3
      };
      return {
        id: n.concept,
        label: n.concept,
        x: coord.x,
        y: coord.y,
        radius: 24,
        status: n.status,
        mastery: n.mastery,
        confidence: n.confidence,
        domain: n.domain,
        attempts: n.attempts,
        misconceptions: n.misconceptions || [],
        retention: n.retention,
        prerequisites: n.prerequisites || []
      };
    });

    this.links = apiGraph.links || [];
    this.initParticles();
  }

  resize() {
    if (!this.canvas) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = rect.width * dpr;
    this.canvas.height = (rect.height || 384) * dpr;
    this.ctx.scale(dpr, dpr);
    this.width = rect.width;
    this.height = rect.height || 384;
  }

  bindEvents() {
    window.addEventListener('resize', () => this.resize());
    
    this.canvas.addEventListener('mousemove', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;

      let found = null;
      for (const node of this.nodes) {
        const nx = node.x * this.width;
        const ny = node.y * this.height;
        const dist = Math.hypot(mx - nx, my - ny);
        if (dist <= node.radius + 8) {
          found = node;
          break;
        }
      }
      this.hoveredNode = found;
      this.canvas.style.cursor = found ? 'pointer' : 'default';
    });

    this.canvas.addEventListener('click', (e) => {
      if (this.hoveredNode) {
        this.selectedNode = this.hoveredNode;
        this.renderConceptDetails(this.hoveredNode);
      }
    });
  }

  renderConceptDetails(node) {
    const detailBox = document.getElementById('concept-detail-box');
    if (!detailBox) return;

    let misHtml = '<p class="text-on-surface-variant italic">None recorded. Concept clear.</p>';
    if (node.misconceptions && node.misconceptions.length > 0) {
      misHtml = `<ul class="list-disc list-inside space-y-1 text-error font-medium">
        ${node.misconceptions.map(m => `<li>${m}</li>`).join('')}
      </ul>`;
    }

    detailBox.innerHTML = `
      <div class="p-4 rounded-xl bg-surface border border-outline-variant/30 space-y-3">
        <div class="flex items-center justify-between">
          <h4 class="font-headline-md font-bold text-[16px] text-on-surface">${node.label}</h4>
          <span class="font-mono text-[11px] px-2.5 py-0.5 rounded-full font-bold uppercase ${node.status === 'mastered' ? 'bg-tertiary-container text-on-tertiary' : node.status === 'needs-remediation' ? 'bg-error-container text-error' : 'bg-primary-container text-on-primary-container'}">${node.status}</span>
        </div>

        <div class="grid grid-cols-2 gap-2 text-[12px] pt-1 border-t border-outline-variant/20">
          <div><span class="text-on-surface-variant font-mono">Mastery:</span> <strong class="text-primary">${node.mastery}%</strong></div>
          <div><span class="text-on-surface-variant font-mono">Confidence:</span> <strong>${Math.round((node.confidence || 0.5) * 100)}%</strong></div>
          <div><span class="text-on-surface-variant font-mono">Attempts:</span> <strong>${node.attempts || 0}</strong></div>
          <div><span class="text-on-surface-variant font-mono">Retention:</span> <strong>${node.retention || node.mastery}%</strong></div>
        </div>

        <div class="pt-2 border-t border-outline-variant/20">
          <span class="font-mono text-[11px] uppercase font-bold text-on-surface-variant">Cognitive Gaps Tracked:</span>
          <div class="mt-1">${misHtml}</div>
        </div>
      </div>
    `;
  }

  animate() {
    this.render();
    this.animationId = requestAnimationFrame(() => this.animate());
  }

  render() {
    const { ctx, width, height } = this;
    if (!ctx) return;

    ctx.clearRect(0, 0, width, height);

    // Subtle background grid
    ctx.strokeStyle = 'rgba(214, 227, 255, 0.4)';
    ctx.lineWidth = 1;
    const gridStep = 45;
    for (let x = 0; x < width; x += gridStep) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += gridStep) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Clean Empty State: If no curriculum nodes have been loaded yet
    if (this.nodes.length === 0) {
      ctx.save();
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      // Watermark Icon
      ctx.font = '40px "Material Symbols Outlined", sans-serif';
      ctx.fillStyle = '#adc7f7';
      ctx.fillText('hub', width / 2, height / 2 - 34);

      // Main Heading
      ctx.font = 'bold 16px Inter, sans-serif';
      ctx.fillStyle = '#002045';
      ctx.fillText('Concept Dependency Graph Uninitialized', width / 2, height / 2 + 8);

      // Informative Guidance
      ctx.font = '500 12px Inter, sans-serif';
      ctx.fillStyle = '#535f70';
      ctx.fillText('Upload a chapter PDF or notes to generate this topic\'s interactive concept mastery map.', width / 2, height / 2 + 32);
      ctx.restore();
      return;
    }

    // Draw Links
    for (const link of this.links) {
      const s = this.nodes.find(n => n.id === link.source);
      const t = this.nodes.find(n => n.id === link.target);
      if (!s || !t) continue;

      const sx = s.x * width;
      const sy = s.y * height;
      const tx = t.x * width;
      const ty = t.y * height;

      const grad = ctx.createLinearGradient(sx, sy, tx, ty);
      grad.addColorStop(0, 'rgba(0, 32, 69, 0.3)');
      grad.addColorStop(1, 'rgba(254, 152, 50, 0.4)');

      ctx.beginPath();
      ctx.moveTo(sx, sy);
      ctx.lineTo(tx, ty);
      ctx.strokeStyle = grad;
      ctx.lineWidth = 2;
      ctx.stroke();
    }

    // Draw link animated particles
    for (const p of this.particles) {
      p.t += p.speed;
      if (p.t > 1) p.t = 0;

      const link = this.links[p.linkIndex];
      if (!link) continue;
      const s = this.nodes.find(n => n.id === link.source);
      const t = this.nodes.find(n => n.id === link.target);
      if (!s || !t) continue;

      const sx = s.x * width;
      const sy = s.y * height;
      const tx = t.x * width;
      const ty = t.y * height;

      const px = sx + (tx - sx) * p.t;
      const py = sy + (ty - sy) * p.t;

      ctx.beginPath();
      ctx.arc(px, py, 3, 0, Math.PI * 2);
      ctx.fillStyle = '#fe9832';
      ctx.shadowColor = '#fe9832';
      ctx.shadowBlur = 6;
      ctx.fill();
      ctx.shadowBlur = 0;
    }

    // Draw Nodes
    for (const node of this.nodes) {
      const nx = node.x * width;
      const ny = node.y * height;
      const isHovered = this.hoveredNode === node;
      const isSelected = this.selectedNode === node;
      const radius = node.radius + (isHovered || isSelected ? 4 : 0);

      let fillCol = '#002045';
      let strokeCol = '#86a0cd';

      if (node.status === 'mastered') {
        fillCol = '#003e29';
        strokeCol = '#6eab8c';
      } else if (node.status === 'needs-remediation') {
        fillCol = '#8f2000';
        strokeCol = '#ff6b4a';
      } else if (node.status === 'in-progress') {
        fillCol = '#8f4e00';
        strokeCol = '#fe9832';
      } else if (node.status === 'ready-to-learn') {
        fillCol = '#1a365d';
        strokeCol = '#adc7f7';
      } else {
        fillCol = '#213145';
        strokeCol = '#74777f';
      }

      // Outer glow
      ctx.beginPath();
      ctx.arc(nx, ny, radius + (isHovered || isSelected ? 8 : 4), 0, Math.PI * 2);
      ctx.fillStyle = isHovered || isSelected ? 'rgba(254, 152, 50, 0.3)' : 'rgba(0, 32, 69, 0.12)';
      ctx.fill();

      // Node Body
      ctx.beginPath();
      ctx.arc(nx, ny, radius, 0, Math.PI * 2);
      ctx.fillStyle = fillCol;
      ctx.fill();
      ctx.strokeStyle = strokeCol;
      ctx.lineWidth = isHovered || isSelected ? 3 : 2;
      ctx.stroke();

      // Mastery % inside node
      ctx.font = '700 10px "JetBrains Mono", monospace';
      ctx.fillStyle = '#ffffff';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(`${node.mastery}%`, nx, ny);

      // Label below node
      ctx.textBaseline = 'top';
      ctx.font = '600 11px Inter, sans-serif';
      ctx.fillStyle = '#0b1c30';
      ctx.fillText(node.label, nx, ny + radius + 8);
    }
  }

  destroy() {
    if (this.animationId) cancelAnimationFrame(this.animationId);
  }
}

window.KnowledgeGraphVisualizer = KnowledgeGraphVisualizer;
