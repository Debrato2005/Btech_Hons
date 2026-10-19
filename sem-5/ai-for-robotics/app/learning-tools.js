/* AI for Robotics learning-tool engine. No network, DOM, or storage dependencies.
 * Course claims come only from supplied, source-linked records. Built-in examples
 * are synthetic software fixtures, never verified course examination questions.
 */
(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.RoboticsLearningTools = api;
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const ENGINE_VERSION = '1.0.0';
  const families = new Map();
  const own = (obj, key) => Object.prototype.hasOwnProperty.call(obj, key);
  const clone = value => JSON.parse(JSON.stringify(value));
  const compareText = (a, b) => String(a) < String(b) ? -1 : String(a) > String(b) ? 1 : 0;

  function fail(message, code = 'INVALID_INPUT') {
    const error = new Error(message);
    error.code = code;
    throw error;
  }
  function assert(condition, message, code) { if (!condition) fail(message, code); }
  function finite(value, name) {
    assert(typeof value === 'number' && Number.isFinite(value), name + ' must be a finite number.');
    return value;
  }
  function integer(value, name, min, max) {
    finite(value, name);
    assert(Number.isSafeInteger(value) && value >= min && value <= max,
      name + ' must be an integer from ' + min + ' to ' + max + '.');
    return value;
  }
  function bounded(value, name, min, max) {
    finite(value, name);
    assert(value >= min && value <= max, name + ' must be from ' + min + ' to ' + max + '.');
    return value;
  }
  function nonempty(value, name) {
    assert(typeof value === 'string' && value.trim().length > 0, name + ' must be a nonempty string.');
    return value;
  }
  function stableStringify(value) {
    if (Array.isArray(value)) return '[' + value.map(stableStringify).join(',') + ']';
    if (value && typeof value === 'object') {
      return '{' + Object.keys(value).sort().map(key => JSON.stringify(key) + ':' + stableStringify(value[key])).join(',') + '}';
    }
    return JSON.stringify(value);
  }
  // FNV-1a gives a stable identifier, not a security or content-integrity hash.
  function hash32(text) {
    let value = 2166136261;
    for (let i = 0; i < text.length; i++) {
      value ^= text.charCodeAt(i);
      value = Math.imul(value, 16777619);
    }
    return value >>> 0;
  }
  function normalizeSeed(seed) {
    assert((typeof seed === 'string' && seed.length > 0) ||
      (typeof seed === 'number' && Number.isSafeInteger(seed)),
    'A reproducible, nonempty string or safe-integer seed is required.');
    return hash32(typeof seed + ':' + String(seed));
  }
  // Mulberry32. Never use for cryptography, authentication, or external randomness.
  function createRng(seed) {
    let state = normalizeSeed(seed);
    return {
      next() {
        state = (state + 0x6D2B79F5) >>> 0;
        let t = state;
        t = Math.imul(t ^ (t >>> 15), t | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
      },
      int(min, max) {
        integer(min, 'min', -2147483647, 2147483647);
        integer(max, 'max', min, 2147483647);
        return min + Math.floor(this.next() * (max - min + 1));
      },
      pick(values) {
        assert(Array.isArray(values) && values.length, 'Cannot sample an empty list.');
        return values[this.int(0, values.length - 1)];
      },
      shuffle(values) {
        const result = values.slice();
        for (let i = result.length - 1; i > 0; i--) {
          const j = this.int(0, i);
          [result[i], result[j]] = [result[j], result[i]];
        }
        return result;
      }
    };
  }
  function roundNumber(value, precision = 3) {
    finite(value, 'value');
    integer(precision, 'precision', 0, 10);
    const scale = 10 ** precision;
    assert(Math.abs(value) * scale <= Number.MAX_SAFE_INTEGER / 4,
      'Value is too large for the requested decimal precision.');
    const magnitude = Math.abs(value) * scale;
    const rounded = Math.sign(value) * Math.round(magnitude + Number.EPSILON * Math.max(1, magnitude) * 2) / scale;
    return Object.is(rounded, -0) ? 0 : rounded;
  }
  function formatNumber(value, precision = 3) { return roundNumber(value, precision).toFixed(precision); }
  function validateNumericOptions(options, correctValue, precision = 3, units = '') {
    assert(Array.isArray(options) && options.length >= 4, 'A numerical MCQ requires at least four options.');
    finite(correctValue, 'correctValue');
    const seenIds = new Set(), seenValues = new Set(), seenLabels = new Set();
    let matching = 0;
    const canonicalAnswer = formatNumber(correctValue, precision);
    const result = options.map(option => {
      nonempty(option.id, 'Option ID');
      assert(!seenIds.has(option.id), 'Duplicate option ID: ' + option.id, 'DUPLICATE_OPTION');
      seenIds.add(option.id);
      finite(option.value, 'Option value');
      assert(option.units === undefined || option.units === units, 'All numerical options must use the declared units.');
      const canonical = formatNumber(option.value, precision);
      assert(!seenValues.has(canonical), 'Options become equivalent at the declared rounding precision.', 'EQUIVALENT_OPTIONS');
      seenValues.add(canonical);
      const text = option.text || canonical + (units ? ' ' + units : '');
      const label = text.trim().replace(/\s+/g, ' ').toLowerCase();
      assert(!seenLabels.has(label), 'Duplicate displayed option label.', 'DUPLICATE_OPTION');
      seenLabels.add(label);
      const correct = canonical === canonicalAnswer;
      if (correct) matching++;
      return { ...option, units, text, roundedValue: roundNumber(option.value, precision), correct };
    });
    assert(matching === 1, 'Exactly one numerical option must match the rounded answer.', 'AMBIGUOUS_ANSWER');
    return result;
  }
  function provenance(record) {
    const sourceRefs = record.sourceRefs || record.citations || [];
    const status = record.status || (record.audit && record.audit.status) || 'draft';
    // A reference is evidence to inspect, not proof that review has happened.
    return {
      kind: record.synthetic ? 'synthetic-demonstration' : 'course-derived',
      synthetic: Boolean(record.synthetic),
      status,
      courseSupported: !record.synthetic && sourceRefs.length > 0,
      sourceRefs: clone(sourceRefs),
      review: record.review ? clone(record.review) : null
    };
  }
  function registerNumericalFamily(definition) {
    nonempty(definition.id, 'Family ID');
    nonempty(definition.version, 'Generator version');
    assert(typeof definition.sample === 'function' && typeof definition.validate === 'function' &&
      typeof definition.solve === 'function', 'A family requires sample, validate, and solve functions.');
    assert(!families.has(definition.id), 'A numerical family with this ID is already registered.');
    assert(definition.synthetic === true || (Array.isArray(definition.sourceRefs) && definition.sourceRefs.length > 0),
      'Course-derived numerical families require exact source references.');
    families.set(definition.id, Object.freeze({ ...definition }));
    return definition.id;
  }
  function listNumericalFamilies({ includeSynthetic = false } = {}) {
    return [...families.values()].filter(f => includeSynthetic || !f.synthetic).map(f => ({
      id: f.id, title: f.title, version: f.version, description: f.description || '',
      parameterDomains: clone(f.parameterDomains || {}), provenance: provenance(f)
    }));
  }
  function generateVariant(familyId, { seed, parameters, shuffleOptions = true, maxAttempts = 200 } = {}) {
    const family = families.get(familyId);
    assert(family, 'Unknown numerical family: ' + familyId);
    const normalizedSeed = normalizeSeed(seed), rng = createRng(seed);
    integer(maxAttempts, 'maxAttempts', 1, 1000);
    const fixedParameters = parameters !== undefined;
    let lastError;
    for (let attempt = 0; attempt < (fixedParameters ? 1 : maxAttempts); attempt++) {
      const sampled = fixedParameters ? clone(parameters) : family.sample(rng);
      family.validate(sampled);
      const solved = family.solve(clone(sampled));
      const precision = solved.precision === undefined ? 3 : solved.precision;
      try {
        const options = validateNumericOptions(solved.options, solved.answer, precision, solved.units || '');
        const ordered = shuffleOptions ? rng.shuffle(options) : options;
        const identity = { familyId, generatorVersion: family.version, seed, parameters: sampled };
        return {
          id: familyId + ':' + hash32(stableStringify(identity)).toString(16).padStart(8, '0'),
          engineVersion: ENGINE_VERSION, familyId, generatorVersion: family.version,
          seed, normalizedSeed, generationAttempt: attempt + 1, parameters: clone(sampled),
          type: 'single-select', question: solved.question,
          options: ordered.map(({ correct, ...option }) => option),
          optionOrder: ordered.map(option => option.id),
          correctOptionIds: ordered.filter(option => option.correct).map(option => option.id),
          answer: solved.answer, roundedAnswer: roundNumber(solved.answer, precision),
          precision, rounding: 'nearest decimal, half away from zero; round only the final answer',
          units: solved.units || '', formula: solved.formula || null,
          variableDefinitions: clone(solved.variableDefinitions || {}),
          assumptions: clone(solved.assumptions || []),
          steps: clone(solved.steps || []), explanation: solved.explanation || '',
          provenance: provenance(family)
        };
      } catch (error) {
        if (fixedParameters || !['EQUIVALENT_OPTIONS', 'DUPLICATE_OPTION', 'AMBIGUOUS_ANSWER'].includes(error.code)) throw error;
        lastError = error;
      }
    }
    fail('Unable to generate a valid distinct-option variant: ' + (lastError && lastError.message), 'GENERATION_EXHAUSTED');
  }
  function restoreVariant(saved) {
    assert(saved && saved.engineVersion === ENGINE_VERSION, 'Unsupported numerical engine version.', 'VERSION_MISMATCH');
    const family = families.get(saved.familyId);
    assert(family && family.version === saved.generatorVersion, 'The saved generator version is unavailable.', 'VERSION_MISMATCH');
    const restored = generateVariant(saved.familyId, { seed: saved.seed, parameters: saved.parameters, shuffleOptions: false });
    assert(restored.id === saved.id, 'Variant identity does not match its seed and parameters.', 'CORRUPT_VARIANT');
    assert(Array.isArray(saved.optionOrder) && saved.optionOrder.length === restored.options.length &&
      new Set(saved.optionOrder).size === restored.options.length &&
      saved.optionOrder.every(id => restored.options.some(option => option.id === id)),
    'Saved option order is invalid.', 'CORRUPT_VARIANT');
    const byId = new Map(restored.options.map(option => [option.id, option]));
    restored.options = saved.optionOrder.map(id => byId.get(id));
    restored.optionOrder = saved.optionOrder.slice();
    restored.generationAttempt = saved.generationAttempt || 1;
    return restored;
  }
  function registerBankNumericalFamilies(bank, { includeDrafts = false } = {}) {
    const registered = [], diagnostics = [];
    const records = (bank.learningTools && bank.learningTools.numericalFamilies) || [];
    const implementationIds = {
      'bayes-two-hypotheses': 'synthetic.bayes-two-hypotheses',
      'q-learning-update': 'synthetic.q-learning-update'
    };
    for (const record of records) {
      const errors = validateReferences(getRefs(record), bank);
      const implementationId = implementationIds[record.generatorKind];
      const implementation = implementationId && families.get(implementationId);
      if (!implementation) errors.push('Unknown allowlisted generatorKind.');
      if (!record.id || !record.generatorVersion) errors.push('A family requires id and generatorVersion.');
      if (record.synthetic) errors.push('Synthetic records cannot be registered as course families.');
      if (getStatus(record) !== 'verified' && !includeDrafts) errors.push('Family review is not verified.');
      if (implementation && record.generatorVersion !== implementation.version) errors.push('Generator version does not match the implemented formula version.');
      if (errors.length) { diagnostics.push({id:record.id,errors}); continue; }
      const previous = families.get(record.id);
      if (previous) {
        if (previous.version !== record.generatorVersion || stableStringify(previous.sourceRefs) !== stableStringify(getRefs(record))) {
          diagnostics.push({id:record.id,errors:['Registered family identity/version/source references conflict.']});
          continue;
        }
      } else {
        registerNumericalFamily({ ...implementation, id:record.id, version:record.generatorVersion,
          title:record.title || implementation.title.replace(' (synthetic)', ''),
          description:record.description || 'Generated numerical exercise derived from the cited course premises under the stated assumptions.',
          synthetic:false, status:getStatus(record), sourceRefs:clone(getRefs(record)), review:record.review || null });
      }
      registered.push(record.id);
    }
    return {registered,diagnostics};
  }

  registerNumericalFamily({
    id: 'synthetic.bayes-two-hypotheses', version: '1.0.0', synthetic: true,
    status: 'draft', title: 'Bayes update: two hypotheses (synthetic)',
    description: 'Software demonstration only. Not a verified question from this course.',
    parameterDomains: { prior: '(0, 1)', likelihoodTrue: '(0, 1]', likelihoodFalse: '(0, 1]' },
    sample: rng => ({ prior: rng.int(1, 9) / 10, likelihoodTrue: rng.int(1, 9) / 10, likelihoodFalse: rng.int(1, 9) / 10 }),
    validate(p) {
      for (const key of ['prior', 'likelihoodTrue', 'likelihoodFalse']) bounded(p[key], key, Number.EPSILON, 1);
      assert(p.prior < 1, 'prior must be strictly less than one.');
    },
    solve(p) {
      const numerator = p.prior * p.likelihoodTrue;
      const evidence = numerator + (1 - p.prior) * p.likelihoodFalse;
      const answer = numerator / evidence;
      return {
        answer, precision: 3,
        question: 'For two exhaustive, mutually exclusive hypotheses H and not-H, P(H) = ' + p.prior +
          ', P(E|H) = ' + p.likelihoodTrue + ', and P(E|not-H) = ' + p.likelihoodFalse +
          '. Find P(H|E), rounding only the final result to 3 decimal places.',
        formula: 'P(H|E) = P(E|H)P(H) / [P(E|H)P(H) + P(E|not-H)(1 − P(H))]',
        variableDefinitions: { H: 'hypothesis', E: 'observed evidence', prior: 'P(H)', likelihoodTrue: 'P(E|H)', likelihoodFalse: 'P(E|not-H)' },
        assumptions: ['The hypotheses are exhaustive and mutually exclusive.', 'Evidence probability is positive.', 'All probabilities are dimensionless.'],
        steps: ['Joint probability P(E and H) = ' + numerator + '.',
          'Total evidence probability = ' + evidence + '.', 'Divide the joint probability by the evidence probability: ' + answer + '.',
          'Round once, at the end: ' + formatNumber(answer, 3) + '.'],
        explanation: 'The update normalizes the prior-weighted likelihoods. The likelihood P(E|H) is not itself the posterior P(H|E).',
        options: [
          { id: 'posterior', value: answer, justification: 'Correct: normalize the prior-weighted likelihood.' },
          { id: 'joint', value: numerator, justification: 'This is P(E and H), not the conditional posterior; the evidence denominator is missing.' },
          { id: 'likelihood', value: p.likelihoodTrue, justification: 'This reverses the conditional: P(E|H) is not generally P(H|E).' },
          { id: 'complement', value: 1 - answer, justification: 'This is P(not-H|E), the complementary hypothesis posterior.' }
        ]
      };
    }
  });
  registerNumericalFamily({
    id: 'synthetic.q-learning-update', version: '1.0.0', synthetic: true,
    status: 'draft', title: 'Single Q-learning update (synthetic)',
    description: 'Software demonstration only. Terminal transitions use a target of reward alone.',
    parameterDomains: { oldQ: 'finite', reward: 'finite', maxNextQ: 'finite', alpha: '[0, 1]', gamma: '[0, 1]', terminal: 'boolean' },
    sample: rng => ({ oldQ: rng.int(1, 8), reward: rng.int(1, 12), maxNextQ: rng.int(2, 10),
      alpha: rng.pick([0.25, 0.5, 0.75]), gamma: rng.pick([0.5, 0.8, 0.9]), terminal: false }),
    validate(p) {
      for (const key of ['oldQ', 'reward', 'maxNextQ']) finite(p[key], key);
      bounded(p.alpha, 'alpha', 0, 1); bounded(p.gamma, 'gamma', 0, 1);
      assert(typeof p.terminal === 'boolean', 'terminal must be explicitly true or false.');
    },
    solve(p) {
      const target = p.reward + (p.terminal ? 0 : p.gamma * p.maxNextQ);
      const error = target - p.oldQ, answer = p.oldQ + p.alpha * error;
      return {
        answer, precision: 3,
        question: 'Given Q(s,a) = ' + p.oldQ + ', reward r = ' + p.reward + ', learning rate α = ' + p.alpha +
          ', discount γ = ' + p.gamma + ', max next-state action value = ' + p.maxNextQ +
          ', and a ' + (p.terminal ? 'terminal' : 'nonterminal') + ' transition, compute the new Q(s,a). Round the final answer to 3 decimal places.',
        formula: 'Q_new(s,a) = Q_old(s,a) + α[r + γ max_a′ Q_old(s′,a′) − Q_old(s,a)] (omit bootstrap at terminal)',
        variableDefinitions: { oldQ: 'pre-update action value', reward: 'observed immediate reward', alpha: 'learning rate', gamma: 'discount factor', maxNextQ: 'maximum legal next-state action value before this update' },
        assumptions: ['One sequential update.', 'Bootstrap values are read before updating.', 'Terminal transitions have zero bootstrap contribution.', 'All values use the same reward units.'],
        steps: ['Target = ' + target + '.', 'Temporal-difference error = target − old value = ' + error + '.',
          'New value = old value + α × error = ' + answer + '.', 'Rounded final answer = ' + formatNumber(answer, 3) + '.'],
        explanation: 'The learning rate interpolates between the old estimate and the one-step target. A terminal transition has no future-reward term.',
        options: [
          { id: 'updated', value: answer, justification: 'Correct: apply the stated temporal-difference update.' },
          { id: 'bootstrap-error', value: p.oldQ + p.alpha * (p.reward + (p.terminal ? p.gamma * p.maxNextQ : 0) - p.oldQ),
            justification: p.terminal ? 'This incorrectly bootstraps from a terminal state.' : 'This incorrectly drops the discounted next-state value for a nonterminal transition.' },
          { id: 'replace-target', value: target, justification: 'This replaces the estimate by the target, which would require α = 1.' },
          { id: 'omit-subtraction', value: p.oldQ + p.alpha * target, justification: 'This fails to subtract the old estimate inside the temporal-difference error.' }
        ]
      };
    }
  });

  function validateGraph(graph) {
    assert(graph && Array.isArray(graph.nodes) && graph.nodes.length > 0, 'Graph requires a nonempty nodes array.');
    assert(typeof graph.directed === 'boolean', 'Graph direction must be explicit: directed true or false.');
    assert(Array.isArray(graph.edges), 'Graph requires an edges array.');
    const nodes = graph.nodes.map(node => typeof node === 'string' ? node : node.id);
    nodes.forEach(node => nonempty(node, 'Node ID'));
    assert(new Set(nodes).size === nodes.length, 'Duplicate graph node IDs.');
    const nodeSet = new Set(nodes), seen = new Set();
    const adjacency = new Map(nodes.map(node => [node, []]));
    const edges = graph.edges.map(edge => {
      assert(nodeSet.has(edge.from) && nodeSet.has(edge.to), 'Every edge endpoint must name a graph node.');
      const cost = edge.cost === undefined ? 1 : finite(edge.cost, 'Edge cost');
      assert(cost >= 0, 'Only nonnegative edge costs are supported.');
      const pair = graph.directed ? [edge.from, edge.to] : [edge.from, edge.to].sort(compareText);
      const key = stableStringify(pair);
      assert(!seen.has(key), 'Parallel/duplicate edges are not supported; merge them explicitly.');
      seen.add(key);
      adjacency.get(edge.from).push({ node: edge.to, cost });
      if (!graph.directed && edge.from !== edge.to) adjacency.get(edge.to).push({ node: edge.from, cost });
      return { from: edge.from, to: edge.to, cost };
    });
    return { nodes, edges, adjacency };
  }
  function searchTrace(graph, options = {}) {
    const { nodes, adjacency } = validateGraph(graph);
    const algorithm = String(options.algorithm || 'bfs').toLowerCase().replace('*', 'star');
    assert(['bfs', 'dfs', 'ucs', 'astar'].includes(algorithm), 'Supported algorithms: bfs, dfs, ucs, astar.');
    const { start, goal } = options;
    assert(nodes.includes(start) && nodes.includes(goal), 'Start and goal must exist in the graph.');
    const neighborOrder = options.neighborOrder || 'lexicographic';
    assert(['lexicographic', 'input'].includes(neighborOrder), 'neighborOrder must be lexicographic or input.');
    const tieBreak = options.tieBreak || 'insertion';
    assert(['lexicographic', 'insertion'].includes(tieBreak), 'tieBreak must be lexicographic or insertion.');
    const maxSteps = options.maxSteps === undefined ? 10000 : integer(options.maxSteps, 'maxSteps', 1, 100000);
    const weighted = algorithm === 'ucs' || algorithm === 'astar';
    const heuristic = options.heuristic || {};
    for (const key of Object.keys(heuristic)) assert(nodes.includes(key), 'Heuristic names an unknown node: ' + key);
    if (algorithm === 'astar') for (const node of nodes) bounded(heuristic[node], 'Heuristic for ' + node, 0, Number.MAX_VALUE);
    const getH = node => algorithm === 'astar' ? heuristic[node] : 0;
    let serial = 0;
    const makeEntry = (node, path, g, depth) => ({ node, path, g, h: getH(node), f: finite(g + getH(node), 'Frontier priority'), depth, serial: serial++ });
    let frontier = [makeEntry(start, [start], 0, 0)];
    const discovered = new Set([start]), closed = new Set(), bestG = new Map([[start, 0]]);
    const snapshots = [];
    const convention = {
      algorithm, directed: graph.directed, neighborOrder, tieBreak,
      edgeCosts: weighted ? 'nonnegative supplied costs; omitted costs are one' : 'edges count as one hop for selection; supplied costs are summed only for reporting',
      frontier: algorithm === 'bfs' ? 'FIFO queue' : algorithm === 'dfs' ? 'LIFO stack, reverse-push neighbors so the first ordered neighbor is expanded first' : 'priority queue',
      priority: algorithm === 'astar' ? 'f = g + h' : algorithm === 'ucs' ? 'g' : algorithm === 'bfs' ? 'discovery order' : 'reverse insertion order',
      repeatedStates: weighted ? 'strictly lower g replaces queued entry and reopens closed state; equal-cost alternatives ignored' : 'mark discovered on insertion; ignore any later discovery',
      goalTest: 'when removed from the frontier, before expansion',
      heuristic: algorithm === 'astar' ? 'explicit nonnegative h for every node; admissibility/consistency are not inferred' : 'not used',
      optimality: algorithm === 'bfs' ? 'fewest edges, not necessarily minimum weighted cost' : algorithm === 'dfs' ? 'no shortest-path guarantee' :
        algorithm === 'ucs' ? 'minimum path cost on this finite nonnegative-cost graph' :
        'minimum path cost requires admissible h with h(goal)=0; this engine permits reopening but does not certify admissibility',
      arithmetic: 'IEEE-754 double precision; priority ties and strict improvements use exact stored numeric comparisons', maxSteps
    };
    function queueOrder() {
      if (weighted) frontier.sort((a, b) => (algorithm === 'astar' ? a.f - b.f : a.g - b.g) ||
        (tieBreak === 'lexicographic' ? compareText(a.node, b.node) : 0) || a.serial - b.serial);
    }
    function snapshot(event, current, actions = []) {
      queueOrder();
      snapshots.push({ index: snapshots.length, event, current: current ? clone(current) : null,
        frontier: clone(algorithm === 'dfs' ? frontier.slice().reverse() : frontier),
        closed: [...closed], discovered: [...discovered], bestG: Object.fromEntries(bestG), actions: clone(actions) });
    }
    snapshot('initial', null);
    let result = null, expansions = 0;
    while (frontier.length && expansions < maxSteps) {
      queueOrder();
      const current = algorithm === 'dfs' ? frontier.pop() : frontier.shift();
      if (current.node === goal) {
        result = current;
        snapshot('goal', current, [{ type: 'goal-test', accepted: true }]);
        break;
      }
      closed.add(current.node);
      expansions++;
      let neighbors = adjacency.get(current.node).slice();
      if (neighborOrder === 'lexicographic') neighbors.sort((a, b) => compareText(a.node, b.node));
      if (algorithm === 'dfs') neighbors.reverse();
      const actions = [];
      for (const neighbor of neighbors) {
        const g = current.g + neighbor.cost;
        assert(Number.isFinite(g), 'Path-cost overflow.');
        const better = weighted ? !bestG.has(neighbor.node) || g < bestG.get(neighbor.node) : !discovered.has(neighbor.node);
        if (!better) {
          actions.push({ type: 'ignore', from: current.node, to: neighbor.node, tentativeG: g,
            reason: weighted ? 'not a strictly cheaper path' : 'already discovered' });
          continue;
        }
        const reopened = closed.delete(neighbor.node);
        const replaced = frontier.some(entry => entry.node === neighbor.node);
        if (weighted) frontier = frontier.filter(entry => entry.node !== neighbor.node);
        discovered.add(neighbor.node); bestG.set(neighbor.node, g);
        frontier.push(makeEntry(neighbor.node, current.path.concat(neighbor.node), g, current.depth + 1));
        actions.push({ type: reopened ? 'reopen' : replaced ? 'decrease-key' : 'discover', from: current.node, to: neighbor.node, g });
      }
      snapshot('expand', current, actions);
    }
    const status = result ? 'found' : frontier.length ? 'truncated' : 'exhausted';
    if (!result) snapshot(status, null);
    return { engineVersion: ENGINE_VERSION, algorithm, status, conventions: convention,
      provenance: options.provenance ? clone(options.provenance) : { kind: 'synthetic-demonstration', synthetic: true, courseSupported: false },
      path: result ? result.path : null, cost: result ? result.g : null, hops: result ? result.depth : null,
      expansions, steps: snapshots };
  }
  function qLearningTrace(config) {
    assert(config && Array.isArray(config.transitions), 'Q-learning requires an explicit transitions array.');
    const alpha = bounded(config.alpha, 'alpha', 0, 1), gamma = bounded(config.gamma, 'gamma', 0, 1);
    const initialValue = config.initialValue === undefined ? 0 : finite(config.initialValue, 'initialValue');
    const initialQ = config.initialQ || {};
    assert(initialQ && typeof initialQ === 'object' && !Array.isArray(initialQ), 'initialQ must be a state/action mapping.');
    const q = new Map();
    function ensureState(state) {
      nonempty(state, 'State');
      if (!q.has(state)) q.set(state, new Map());
      return q.get(state);
    }
    function value(state, action) {
      nonempty(action, 'Action');
      const actions = ensureState(state);
      return actions.has(action) ? actions.get(action) : initialValue;
    }
    for (const state of Object.keys(initialQ)) {
      const actions = initialQ[state];
      assert(actions && typeof actions === 'object' && !Array.isArray(actions), 'Each initial Q state must contain an action mapping.');
      for (const action of Object.keys(actions)) ensureState(state).set(nonempty(action, 'Action'), finite(actions[action], 'Initial Q value'));
    }
    const table = () => Object.fromEntries([...q].map(([state, actions]) => [state, Object.fromEntries(actions)]));
    const steps = [{ index: 0, event: 'initial', q: table() }];
    config.transitions.forEach((transition, index) => {
      const { state, action, nextState, terminal } = transition;
      nonempty(state, 'Transition state'); nonempty(action, 'Transition action'); nonempty(nextState, 'Next state');
      finite(transition.reward, 'Reward');
      assert(typeof terminal === 'boolean', 'Every transition must explicitly declare terminal true or false.');
      const nextActions = transition.nextActions || (initialQ[nextState] ? Object.keys(initialQ[nextState]) : []);
      assert(Array.isArray(nextActions) && new Set(nextActions).size === nextActions.length, 'nextActions must be a duplicate-free array.');
      nextActions.forEach(a => nonempty(a, 'Next action'));
      assert(terminal || nextActions.length > 0, 'A nonterminal transition requires at least one explicitly legal next action.');
      const oldQ = value(state, action);
      // Read every bootstrap value before the write, including a self-transition.
      const nextValues = terminal ? [] : nextActions.map(a => ({ action: a, value: value(nextState, a) }));
      const maxNextQ = terminal ? 0 : Math.max(...nextValues.map(a => a.value));
      const target = transition.reward + (terminal ? 0 : gamma * maxNextQ);
      const tdError = target - oldQ, newQ = oldQ + alpha * tdError;
      finite(newQ, 'Updated Q value');
      ensureState(state).set(action, newQ);
      steps.push({ index: index + 1, event: 'update', transition: clone(transition), oldQ, nextValues, maxNextQ,
        target, tdError, alpha, gamma, newQ, q: table(),
        equation: oldQ + ' + ' + alpha + ' × (' + target + ' − ' + oldQ + ') = ' + newQ });
    });
    return { engineVersion: ENGINE_VERSION, algorithm: 'q-learning', steps, finalQ: table(),
      provenance: config.provenance ? clone(config.provenance) : { kind: 'synthetic-demonstration', synthetic: true, courseSupported: false },
      conventions: {
        update: 'Q(s,a) ← Q(s,a) + α[r + γ max over legal actions Q(s′,a′) − Q(s,a)]',
        timing: 'sequential, in supplied transition order; bootstrap from the table before this transition writes',
        terminal: 'terminal target is reward alone, even if a terminal-state row exists',
        unknownActionValue: initialValue, legalActions: 'transition.nextActions, otherwise keys explicitly supplied in initialQ for nextState',
        policy: 'transitions are supplied observations; no exploration policy or greedy action is inferred', alpha, gamma
      } };
  }
  function createStepper(trace) {
    assert(trace && Array.isArray(trace.steps) && trace.steps.length > 0, 'A nonempty trace is required.');
    let index = 0;
    return {
      get index() { return index; }, get length() { return trace.steps.length; },
      current: () => clone(trace.steps[index]),
      next() { index = Math.min(index + 1, trace.steps.length - 1); return this.current(); },
      previous() { index = Math.max(0, index - 1); return this.current(); },
      reset() { index = 0; return this.current(); },
      seek(target) { index = integer(target, 'Step index', 0, trace.steps.length - 1); return this.current(); }
    };
  }

  function getStatus(record) {
    return record && (record.status || (record.audit && record.audit.status) || (record.verification && record.verification.status)) || 'draft';
  }
  function getRefs(record) { return record && (record.sourceRefs || record.citations || record.sources) || []; }
  function validateReferences(refs, bank) {
    if (!Array.isArray(refs) || refs.length === 0) return ['No source references.'];
    const sources = new Map((bank.sources || []).map(source => [source.id || source.sourceId, source]));
    const errors = [];
    refs.forEach(ref => {
      const sourceId = ref.sourceId || ref.source_id, source = sources.get(sourceId);
      const page = ref.page === undefined ? (ref.pdfPage === undefined ? ref.physicalPage : ref.pdfPage) : ref.page;
      if (!source) errors.push('Unknown source ' + sourceId + '.');
      if (!Number.isInteger(page) || page < 1) errors.push('Source references need one-based physical PDF pages.');
      if (source && (source.pageCount || source.pages) && page > (source.pageCount || source.pages)) errors.push('Source reference exceeds page count.');
      if (!(ref.statement || ref.quote || ref.region || ref.evidence || ref.locator)) errors.push('Source reference needs a statement, quote, region, evidence, or locator.');
    });
    return errors;
  }
  // No formulas or course contrasts are inferred from generic implementation code.
  // Only explicit data records with exact source mappings enter these study views.
  function buildLearningViews(bank, { includeDrafts = false } = {}) {
    const input = bank.learningTools || {}, diagnostics = [];
    const questionIds = new Set((bank.questions || []).map(q => q.id));
    const normalize = (kind, values) => (values || []).flatMap(item => {
      const errors = validateReferences(getRefs(item), bank);
      if (!item.id) errors.push('Missing learning item ID.');
      for (const id of item.questionIds || []) if (!questionIds.has(id)) errors.push('Unknown linked question ' + id + '.');
      if (item.synthetic) errors.push('Synthetic examples are excluded from course views.');
      if (getStatus(item) !== 'verified') errors.push('Learning item has not been independently verified.');
      if (errors.length) diagnostics.push({ kind, id: item.id || null, errors });
      const referencesValid = !validateReferences(getRefs(item), bank).length;
      if (item.synthetic || !referencesValid || (!includeDrafts && errors.length)) return [];
      return [{ ...clone(item), sourceRefs: clone(getRefs(item)), status: getStatus(item), auditWarnings: errors }];
    });
    const formulas = normalize('formula', input.formulaSheet || input.formulas || bank.formulas);
    const confusionPairs = normalize('confusion-pair', input.confusionPairs || bank.confusionPairs);
    const traps = normalize('trap', input.traps || bank.traps);
    const formulasByWeek = {};
    for (const formula of formulas) {
      const week = formula.weekId || formula.week || 'unmapped';
      if (!own(formulasByWeek, week)) Object.defineProperty(formulasByWeek, week, { value: [], enumerable: true });
      formulasByWeek[week].push(formula);
    }
    return { formulas, formulasByWeek, confusionPairs, traps, diagnostics,
      emptyMessage: 'No independently verified, source-linked learning records are available for this view yet.' };
  }

  function masteryByConcept(questions, attempts) {
    const questionsById = new Map(questions.map(q => [q.id, q])), groups = new Map();
    const dimensions = new Set(['factual', 'conceptual', 'application', 'numerical']);
    const getDimension = q => dimensions.has(q.masteryDimension) ? q.masteryDimension :
      q.cognitiveSkill === 'recall' ? 'factual' : dimensions.has(q.cognitiveSkill) ? q.cognitiveSkill :
      /numerical|calculation/.test(q.type || '') ? 'numerical' : /application|scenario/.test(q.type || '') ? 'application' :
        /fact|definition|recall/.test(q.type || '') ? 'factual' : 'conceptual';
    attempts.forEach((attempt, inputIndex) => {
      const question = questionsById.get(attempt.questionId);
      if (!question || getStatus(question) !== 'verified' || typeof attempt.correct !== 'boolean') return;
      const evidenceId = question.familyId || question.numericalFamilyId || (question.variant && question.variant.familyId) || question.id;
      const timestamp = typeof attempt.timestamp === 'number' ? attempt.timestamp : Date.parse(attempt.timestamp || '');
      const sequence = Number.isFinite(timestamp) ? timestamp : inputIndex;
      for (const conceptId of question.conceptIds || []) {
        const dimension = getDimension(question), key = stableStringify([conceptId, dimension]);
        if (!groups.has(key)) groups.set(key, { conceptId, dimension, attempts: 0, evidence: new Map() });
        const group = groups.get(key);
        group.attempts++;
        const prior = group.evidence.get(evidenceId);
        if (!prior || sequence >= prior.sequence) group.evidence.set(evidenceId, { correct: attempt.correct, questionId: question.id, sequence });
      }
    });
    return [...groups.values()].map(group => {
      const evidence = [...group.evidence.values()], uniqueEvidenceCount = evidence.length;
      const correctCount = evidence.filter(item => item.correct).length;
      const estimatedAccuracy = (correctCount + 1) / (uniqueEvidenceCount + 2);
      return { conceptId: group.conceptId, dimension: group.dimension, attempts: group.attempts,
        uniqueEvidenceCount, correctCount, estimatedAccuracy,
        evidenceQuestionIds: evidence.map(item => item.questionId),
        label: uniqueEvidenceCount < 3 ? 'limited evidence' : estimatedAccuracy >= 0.8 ? 'strong observed performance' :
          estimatedAccuracy >= 0.5 ? 'developing' : 'needs revision',
        heuristic: 'Latest outcome per distinct question/family; (correct + 1) / (distinct evidence + 2). Repeated variants do not add evidence breadth.' };
    });
  }
  function mistakeRevision(bank, attempts, { bookmarks = [], reviewFlags = [] } = {}) {
    const questions = bank.questions || [], concepts = new Map((bank.concepts || []).map(c => [c.id, c]));
    const latest = new Map();
    attempts.forEach(attempt => {
      if (typeof attempt.correct === 'boolean') latest.set(attempt.questionId, attempt);
    });
    const weakConcepts = new Set();
    for (const question of questions) if (latest.has(question.id) && !latest.get(question.id).correct) {
      (question.conceptIds || []).forEach(id => weakConcepts.add(id));
    }
    const prerequisites = new Set();
    function visit(id, path) {
      if (path.has(id)) return;
      const concept = concepts.get(id);
      if (!concept) return;
      const nextPath = new Set(path); nextPath.add(id);
      for (const prerequisite of concept.prerequisiteConceptIds || concept.prerequisiteIds || []) {
        if (nextPath.has(prerequisite)) continue;
        prerequisites.add(prerequisite); visit(prerequisite, nextPath);
      }
    }
    weakConcepts.forEach(id => visit(id, new Set()));
    const bookmarked = new Set(bookmarks), review = new Set(reviewFlags);
    return questions.filter(q => getStatus(q) === 'verified').map(question => {
      const reasons = [];
      if (latest.has(question.id) && !latest.get(question.id).correct) reasons.push('Most recent attempt was incorrect');
      if (bookmarked.has(question.id)) reasons.push('Bookmarked');
      if (review.has(question.id)) reasons.push('Marked for review');
      if ((question.conceptIds || []).some(id => prerequisites.has(id))) reasons.push('Prerequisite of a recently missed concept');
      if ((question.conceptIds || []).some(id => weakConcepts.has(id)) && !latest.has(question.id)) reasons.push('Unattempted practice for a recently missed concept');
      return { questionId: question.id, reasons, priority: reasons.length + (reasons[0] === 'Most recent attempt was incorrect' ? 3 : 0) };
    }).filter(item => item.reasons.length).sort((a, b) => b.priority - a.priority || compareText(a.questionId, b.questionId));
  }

  return Object.freeze({ ENGINE_VERSION, createRng, roundNumber, formatNumber, validateNumericOptions,
    registerNumericalFamily, registerBankNumericalFamilies, listNumericalFamilies, generateVariant, restoreVariant,
    validateGraph, searchTrace, qLearningTrace, createStepper,
    validateReferences, buildLearningViews, masteryByConcept, mistakeRevision });
}));
