const creations = [
  {
    name: "Living Projects",
    category: "Projects",
    color: "#64f4d7",
    x: 220,
    y: 170,
    detail: "The work that keeps evolving: prototypes, apps, essays, sketches, and systems that grow as you do.",
  },
  {
    name: "Stories",
    category: "Stories",
    color: "#9f8cff",
    x: 940,
    y: 155,
    detail: "The memories and narratives that turn raw experience into meaning others can cross into.",
  },
  {
    name: "Tools",
    category: "Tools",
    color: "#ffd166",
    x: 1030,
    y: 435,
    detail: "The instruments, workflows, and shortcuts you built to make the next act easier to start.",
  },
  {
    name: "Impact",
    category: "Impact",
    color: "#ff9ac8",
    x: 730,
    y: 610,
    detail: "The changes that outlive the moment: people helped, lessons shared, momentum transferred.",
  },
  {
    name: "Experiments",
    category: "Projects",
    color: "#64f4d7",
    x: 275,
    y: 545,
    detail: "The brave attempts, half-built wonders, and weird questions that taught you what the map could become.",
  },
];

const svg = document.querySelector("#bridge-map");
const starLayer = svg.querySelector(".stars");
const lineLayer = svg.querySelector(".bridge-lines");
const nodeLayer = svg.querySelector(".creation-nodes");
const panelName = document.querySelector("#creation-name");
const panelDetail = document.querySelector("#creation-detail");
const center = { x: 600, y: 360 };

function svgElement(tag, attributes = {}) {
  const element = document.createElementNS("http://www.w3.org/2000/svg", tag);

  Object.entries(attributes).forEach(([key, value]) => {
    element.setAttribute(key, value);
  });

  return element;
}

function bridgeCurve({ x, y }, offset = 0) {
  const midX = (center.x + x) / 2;
  const midY = (center.y + y) / 2;
  const bend = y < center.y ? -90 - offset : 90 + offset;

  return `M ${center.x} ${center.y} Q ${midX} ${midY + bend} ${x} ${y}`;
}

function renderStars() {
  const stars = Array.from({ length: 42 }, (_, index) => ({
    x: 60 + ((index * 149) % 1080),
    y: 45 + ((index * 83) % 620),
    r: 1.2 + (index % 4) * 0.55,
    delay: `${(index % 9) * 0.32}s`,
  }));

  stars.forEach((star) => {
    const circle = svgElement("circle", {
      class: "star",
      cx: star.x,
      cy: star.y,
      r: star.r,
      style: `animation-delay: ${star.delay}`,
    });
    starLayer.append(circle);
  });
}

function renderBridgeLine(creation, index) {
  const support = svgElement("path", {
    class: "support-path",
    d: bridgeCurve(creation, index * 5),
  });
  const path = svgElement("path", {
    class: "bridge-path",
    d: bridgeCurve(creation, index * 5),
    style: `animation-delay: ${index * -0.35}s`,
  });

  lineLayer.append(support, path);
}

function renderCreationNode(creation, index) {
  const group = svgElement("g", {
    class: "creation-node",
    transform: `translate(${creation.x} ${creation.y})`,
    tabindex: "0",
    role: "button",
    "aria-label": `${creation.name}: ${creation.detail}`,
  });

  const halo = svgElement("circle", {
    r: 54,
    fill: creation.color,
    opacity: "0.12",
  });
  const orb = svgElement("circle", {
    class: "node-orb",
    r: 38,
    fill: creation.color,
  });
  const label = svgElement("text", {
    class: "node-label",
    y: 76,
  });
  const category = svgElement("text", {
    class: "node-category",
    y: 98,
  });

  label.textContent = creation.name;
  category.textContent = creation.category;
  group.style.animationDelay = `${index * 0.2}s`;
  group.append(halo, orb, label, category);
  group.addEventListener("mouseenter", () => updatePanel(creation));
  group.addEventListener("focus", () => updatePanel(creation));
  nodeLayer.append(group);
}

function updatePanel(creation) {
  panelName.textContent = creation.name;
  panelDetail.textContent = creation.detail;
}

renderStars();
creations.forEach((creation, index) => {
  renderBridgeLine(creation, index);
  renderCreationNode(creation, index);
});
updatePanel(creations[0]);
