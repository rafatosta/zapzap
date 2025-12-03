(function () {
    "use strict";

    /* malevic@0.20.2 - Aug 10, 2024 */
    function m$1(tagOrComponent, props, ...children) {
        props = props || {};
        if (typeof tagOrComponent === "string") {
            const tag = tagOrComponent;
            return {type: tag, props, children};
        }
        if (typeof tagOrComponent === "function") {
            const component = tagOrComponent;
            return {type: component, props, children};
        }
        throw new Error("Unsupported spec type");
    }

    /* malevic@0.20.2 - Aug 10, 2024 */
    function createPluginsStore() {
        const plugins = [];
        return {
            add(plugin) {
                plugins.push(plugin);
                return this;
            },
            apply(props) {
                let result;
                let plugin;
                const usedPlugins = new Set();
                for (let i = plugins.length - 1; i >= 0; i--) {
                    plugin = plugins[i];
                    if (usedPlugins.has(plugin)) {
                        continue;
                    }
                    result = plugin(props);
                    if (result != null) {
                        return result;
                    }
                    usedPlugins.add(plugin);
                }
                return null;
            },
            delete(plugin) {
                for (let i = plugins.length - 1; i >= 0; i--) {
                    if (plugins[i] === plugin) {
                        plugins.splice(i, 1);
                        break;
                    }
                }
                return this;
            },
            empty() {
                return plugins.length === 0;
            }
        };
    }
    function iterateComponentPlugins(type, pairs, iterator) {
        pairs
            .filter(([key]) => type[key])
            .forEach(([key, plugins]) => {
                return type[key].forEach((plugin) => iterator(plugins, plugin));
            });
    }
    function addComponentPlugins(type, pairs) {
        iterateComponentPlugins(type, pairs, (plugins, plugin) =>
            plugins.add(plugin)
        );
    }
    function deleteComponentPlugins(type, pairs) {
        iterateComponentPlugins(type, pairs, (plugins, plugin) =>
            plugins.delete(plugin)
        );
    }

    const XHTML_NS = "http://www.w3.org/1999/xhtml";
    const SVG_NS = "http://www.w3.org/2000/svg";

    const PLUGINS_CREATE_ELEMENT = Symbol();
    const pluginsCreateElement = createPluginsStore();
    function createElement(spec, parent) {
        const result = pluginsCreateElement.apply({spec, parent});
        if (result) {
            return result;
        }
        const tag = spec.type;
        if (tag === "svg") {
            return document.createElementNS(SVG_NS, "svg");
        }
        const namespace = parent.namespaceURI;
        if (namespace === XHTML_NS || namespace == null) {
            return document.createElement(tag);
        }
        return document.createElementNS(namespace, tag);
    }

    function classes$1(...args) {
        const classes = [];
        const process = (c) => {
            if (!c) return;
            if (typeof c === "string") {
                classes.push(c);
            } else if (Array.isArray(c)) {
                c.forEach(process);
            } else if (typeof c === "object") {
                classes.push(
                    ...Object.keys(c).filter((key) => Boolean(c[key]))
                );
            }
        };
        args.forEach(process);
        return classes.join(" ");
    }
    function setInlineCSSPropertyValue(element, prop, $value) {
        if ($value != null && $value !== "") {
            let value = String($value);
            let important = "";
            if (value.endsWith("!important")) {
                value = value.substring(0, value.length - 10);
                important = "important";
            }
            element.style.setProperty(prop, value, important);
        } else {
            element.style.removeProperty(prop);
        }
    }

    function isObject(value) {
        return value != null && typeof value === "object";
    }

    const eventListeners = new WeakMap();
    function addEventListener(element, event, listener) {
        let listeners;
        if (eventListeners.has(element)) {
            listeners = eventListeners.get(element);
        } else {
            listeners = new Map();
            eventListeners.set(element, listeners);
        }
        if (listeners.get(event) !== listener) {
            if (listeners.has(event)) {
                element.removeEventListener(event, listeners.get(event));
            }
            element.addEventListener(event, listener);
            listeners.set(event, listener);
        }
    }
    function removeEventListener(element, event) {
        if (!eventListeners.has(element)) {
            return;
        }
        const listeners = eventListeners.get(element);
        element.removeEventListener(event, listeners.get(event));
        listeners.delete(event);
    }

    function setClassObject(element, classObj) {
        const cls = Array.isArray(classObj)
            ? classes$1(...classObj)
            : classes$1(classObj);
        if (cls) {
            element.setAttribute("class", cls);
        } else {
            element.removeAttribute("class");
        }
    }
    function mergeValues(obj, old) {
        const values = new Map();
        const newProps = new Set(Object.keys(obj));
        const oldProps = Object.keys(old);
        oldProps
            .filter((prop) => !newProps.has(prop))
            .forEach((prop) => values.set(prop, null));
        newProps.forEach((prop) => values.set(prop, obj[prop]));
        return values;
    }
    function setStyleObject(element, styleObj, prev) {
        let prevObj;
        if (isObject(prev)) {
            prevObj = prev;
        } else {
            prevObj = {};
            element.removeAttribute("style");
        }
        const declarations = mergeValues(styleObj, prevObj);
        declarations.forEach(($value, prop) =>
            setInlineCSSPropertyValue(element, prop, $value)
        );
    }
    function setEventListener(element, event, listener) {
        if (typeof listener === "function") {
            addEventListener(element, event, listener);
        } else {
            removeEventListener(element, event);
        }
    }
    const specialAttrs = new Set([
        "key",
        "oncreate",
        "onupdate",
        "onrender",
        "onremove"
    ]);
    const PLUGINS_SET_ATTRIBUTE = Symbol();
    const pluginsSetAttribute = createPluginsStore();
    function getPropertyValue(obj, prop) {
        return obj && obj.hasOwnProperty(prop) ? obj[prop] : null;
    }
    function syncAttrs(element, attrs, prev) {
        const values = mergeValues(attrs, prev || {});
        values.forEach((value, attr) => {
            if (!pluginsSetAttribute.empty()) {
                const result = pluginsSetAttribute.apply({
                    element,
                    attr,
                    value,
                    get prev() {
                        return getPropertyValue(prev, attr);
                    }
                });
                if (result != null) {
                    return;
                }
            }
            if (attr === "class" && isObject(value)) {
                setClassObject(element, value);
            } else if (attr === "style" && isObject(value)) {
                const prevValue = getPropertyValue(prev, attr);
                setStyleObject(element, value, prevValue);
            } else if (attr.startsWith("on")) {
                const event = attr.substring(2);
                setEventListener(element, event, value);
            } else if (specialAttrs.has(attr));
            else if (value == null || value === false) {
                element.removeAttribute(attr);
            } else {
                element.setAttribute(attr, value === true ? "" : String(value));
            }
        });
    }

    class LinkedList {
        constructor(...items) {
            this.nexts = new WeakMap();
            this.prevs = new WeakMap();
            this.first = null;
            this.last = null;
            items.forEach((item) => this.push(item));
        }
        empty() {
            return this.first == null;
        }
        push(item) {
            if (this.empty()) {
                this.first = item;
                this.last = item;
            } else {
                this.nexts.set(this.last, item);
                this.prevs.set(item, this.last);
                this.last = item;
            }
        }
        insertBefore(newItem, refItem) {
            const prev = this.before(refItem);
            this.prevs.set(newItem, prev);
            this.nexts.set(newItem, refItem);
            this.prevs.set(refItem, newItem);
            prev && this.nexts.set(prev, newItem);
            refItem === this.first && (this.first = newItem);
        }
        delete(item) {
            const prev = this.before(item);
            const next = this.after(item);
            prev && this.nexts.set(prev, next);
            next && this.prevs.set(next, prev);
            item === this.first && (this.first = next);
            item === this.last && (this.last = prev);
        }
        before(item) {
            return this.prevs.get(item) || null;
        }
        after(item) {
            return this.nexts.get(item) || null;
        }
        loop(iterator) {
            if (this.empty()) {
                return;
            }
            let current = this.first;
            do {
                if (iterator(current)) {
                    break;
                }
            } while ((current = this.after(current)));
        }
        copy() {
            const list = new LinkedList();
            this.loop((item) => {
                list.push(item);
                return false;
            });
            return list;
        }
        forEach(iterator) {
            this.loop((item) => {
                iterator(item);
                return false;
            });
        }
        find(iterator) {
            let result = null;
            this.loop((item) => {
                if (iterator(item)) {
                    result = item;
                    return true;
                }
                return false;
            });
            return result;
        }
        map(iterator) {
            const results = [];
            this.loop((item) => {
                results.push(iterator(item));
                return false;
            });
            return results;
        }
    }

    function matchChildren(vnode, old) {
        const oldChildren = old.children();
        const oldChildrenByKey = new Map();
        const oldChildrenWithoutKey = [];
        oldChildren.forEach((v) => {
            const key = v.key();
            if (key == null) {
                oldChildrenWithoutKey.push(v);
            } else {
                oldChildrenByKey.set(key, v);
            }
        });
        const children = vnode.children();
        const matches = [];
        const unmatched = new Set(oldChildren);
        const keys = new Set();
        children.forEach((v) => {
            let match = null;
            let guess = null;
            const key = v.key();
            if (key != null) {
                if (keys.has(key)) {
                    throw new Error("Duplicate key");
                }
                keys.add(key);
                if (oldChildrenByKey.has(key)) {
                    guess = oldChildrenByKey.get(key);
                }
            } else if (oldChildrenWithoutKey.length > 0) {
                guess = oldChildrenWithoutKey.shift();
            }
            if (v.matches(guess)) {
                match = guess;
            }
            matches.push([v, match]);
            if (match) {
                unmatched.delete(match);
            }
        });
        return {matches, unmatched};
    }

    function execute(vnode, old, vdom) {
        const didMatch = vnode && old && vnode.matches(old);
        if (didMatch && vnode.parent() === old.parent()) {
            vdom.replaceVNode(old, vnode);
        } else if (vnode) {
            vdom.addVNode(vnode);
        }
        const context = vdom.getVNodeContext(vnode);
        const oldContext = vdom.getVNodeContext(old);
        if (old && !didMatch) {
            old.detach(oldContext);
            old.children().forEach((v) => execute(null, v, vdom));
            old.detached(oldContext);
        }
        if (vnode && !didMatch) {
            vnode.attach(context);
            vnode.children().forEach((v) => execute(v, null, vdom));
            vnode.attached(context);
        }
        if (didMatch) {
            const result = vnode.update(old, context);
            if (result !== vdom.LEAVE) {
                const {matches, unmatched} = matchChildren(vnode, old);
                unmatched.forEach((v) => execute(null, v, vdom));
                matches.forEach(([v, o]) => execute(v, o, vdom));
                vnode.updated(context);
            }
        }
    }

    function m(tagOrComponent, props, ...children) {
        props = props || {};
        if (typeof tagOrComponent === "string") {
            const tag = tagOrComponent;
            return {type: tag, props, children};
        }
        if (typeof tagOrComponent === "function") {
            const component = tagOrComponent;
            return {type: component, props, children};
        }
        throw new Error("Unsupported spec type");
    }
    function isSpec(x) {
        return isObject(x) && x.type != null && x.nodeType == null;
    }
    function isNodeSpec(x) {
        return isSpec(x) && typeof x.type === "string";
    }
    function isComponentSpec(x) {
        return isSpec(x) && typeof x.type === "function";
    }

    class VNodeBase {
        constructor(parent) {
            this.parentVNode = parent;
        }
        key() {
            return null;
        }
        parent(vnode) {
            if (vnode) {
                this.parentVNode = vnode;
                return;
            }
            return this.parentVNode;
        }
        children() {
            return [];
        }
        attach(context) {}
        detach(context) {}
        update(old, context) {
            return null;
        }
        attached(context) {}
        detached(context) {}
        updated(context) {}
    }
    function nodeMatchesSpec(node, spec) {
        return (
            node instanceof Element &&
            ((node.namespaceURI === XHTML_NS &&
                spec.type === node.tagName.toLocaleLowerCase()) ||
                (node.namespaceURI !== XHTML_NS && spec.type === node.tagName))
        );
    }
    const refinedElements = new WeakMap();
    function markElementAsRefined(element, vdom) {
        let refined;
        if (refinedElements.has(vdom)) {
            refined = refinedElements.get(vdom);
        } else {
            refined = new WeakSet();
            refinedElements.set(vdom, refined);
        }
        refined.add(element);
    }
    function isElementRefined(element, vdom) {
        return (
            refinedElements.has(vdom) && refinedElements.get(vdom).has(element)
        );
    }
    class ElementVNode extends VNodeBase {
        constructor(spec, parent) {
            super(parent);
            this.spec = spec;
        }
        matches(other) {
            return (
                other instanceof ElementVNode &&
                this.spec.type === other.spec.type
            );
        }
        key() {
            return this.spec.props.key;
        }
        children() {
            return [this.child];
        }
        getExistingElement(context) {
            const parent = context.parent;
            const existing = context.node;
            let element;
            if (nodeMatchesSpec(existing, this.spec)) {
                element = existing;
            } else if (
                !isElementRefined(parent, context.vdom) &&
                context.vdom.isDOMNodeCaptured(parent)
            ) {
                const sibling = context.sibling;
                const guess = sibling
                    ? sibling.nextElementSibling
                    : parent.firstElementChild;
                if (guess && !context.vdom.isDOMNodeCaptured(guess)) {
                    if (nodeMatchesSpec(guess, this.spec)) {
                        element = guess;
                    } else {
                        parent.removeChild(guess);
                    }
                }
            }
            return element;
        }
        attach(context) {
            let element;
            const existing = this.getExistingElement(context);
            if (existing) {
                element = existing;
            } else {
                element = createElement(this.spec, context.parent);
                markElementAsRefined(element, context.vdom);
            }
            syncAttrs(element, this.spec.props, null);
            this.child = createDOMVNode(
                element,
                this.spec.children,
                this,
                false
            );
        }
        update(prev, context) {
            const prevContext = context.vdom.getVNodeContext(prev);
            const element = prevContext.node;
            syncAttrs(element, this.spec.props, prev.spec.props);
            this.child = createDOMVNode(
                element,
                this.spec.children,
                this,
                false
            );
        }
        attached(context) {
            const {oncreate, onrender} = this.spec.props;
            if (oncreate) {
                oncreate(context.node);
            }
            if (onrender) {
                onrender(context.node);
            }
        }
        detached(context) {
            const {onremove} = this.spec.props;
            if (onremove) {
                onremove(context.node);
            }
        }
        updated(context) {
            const {onupdate, onrender} = this.spec.props;
            if (onupdate) {
                onupdate(context.node);
            }
            if (onrender) {
                onrender(context.node);
            }
        }
    }
    const symbols = {
        CREATED: Symbol(),
        REMOVED: Symbol(),
        UPDATED: Symbol(),
        RENDERED: Symbol(),
        ACTIVE: Symbol(),
        DEFAULTS_ASSIGNED: Symbol()
    };
    const domPlugins = [
        [PLUGINS_CREATE_ELEMENT, pluginsCreateElement],
        [PLUGINS_SET_ATTRIBUTE, pluginsSetAttribute]
    ];
    class ComponentVNode extends VNodeBase {
        constructor(spec, parent) {
            super(parent);
            this.lock = false;
            this.spec = spec;
            this.prev = null;
            this.store = {};
            this.store[symbols.ACTIVE] = this;
        }
        matches(other) {
            return (
                other instanceof ComponentVNode &&
                this.spec.type === other.spec.type
            );
        }
        key() {
            return this.spec.props.key;
        }
        children() {
            return [this.child];
        }
        createContext(context) {
            const {parent} = context;
            const {spec, prev, store} = this;
            return {
                spec,
                prev,
                store,
                get node() {
                    return context.node;
                },
                get nodes() {
                    return context.nodes;
                },
                parent,
                onCreate: (fn) => (store[symbols.CREATED] = fn),
                onUpdate: (fn) => (store[symbols.UPDATED] = fn),
                onRemove: (fn) => (store[symbols.REMOVED] = fn),
                onRender: (fn) => (store[symbols.RENDERED] = fn),
                refresh: () => {
                    const activeVNode = store[symbols.ACTIVE];
                    activeVNode.refresh(context);
                },
                leave: () => context.vdom.LEAVE,
                getStore: (defaults) => {
                    if (defaults && !store[symbols.DEFAULTS_ASSIGNED]) {
                        Object.entries(defaults).forEach(([prop, value]) => {
                            store[prop] = value;
                        });
                        store[symbols.DEFAULTS_ASSIGNED] = true;
                    }
                    return store;
                }
            };
        }
        unbox(context) {
            const Component = this.spec.type;
            const props = this.spec.props;
            const children = this.spec.children;
            this.lock = true;
            const prevContext = ComponentVNode.context;
            ComponentVNode.context = this.createContext(context);
            let unboxed = null;
            try {
                unboxed = Component(props, ...children);
            } finally {
                ComponentVNode.context = prevContext;
                this.lock = false;
            }
            return unboxed;
        }
        refresh(context) {
            if (this.lock) {
                throw new Error(
                    "Calling refresh during unboxing causes infinite loop"
                );
            }
            this.prev = this.spec;
            const latestContext = context.vdom.getVNodeContext(this);
            const unboxed = this.unbox(latestContext);
            if (unboxed === context.vdom.LEAVE) {
                return;
            }
            const prevChild = this.child;
            this.child = createVNode(unboxed, this);
            context.vdom.execute(this.child, prevChild);
            this.updated(context);
        }
        addPlugins() {
            addComponentPlugins(this.spec.type, domPlugins);
        }
        deletePlugins() {
            deleteComponentPlugins(this.spec.type, domPlugins);
        }
        attach(context) {
            this.addPlugins();
            const unboxed = this.unbox(context);
            const childSpec = unboxed === context.vdom.LEAVE ? null : unboxed;
            this.child = createVNode(childSpec, this);
        }
        update(prev, context) {
            this.store = prev.store;
            this.prev = prev.spec;
            this.store[symbols.ACTIVE] = this;
            const prevContext = context.vdom.getVNodeContext(prev);
            this.addPlugins();
            const unboxed = this.unbox(prevContext);
            let result = null;
            if (unboxed === context.vdom.LEAVE) {
                result = unboxed;
                this.child = prev.child;
                context.vdom.adoptVNode(this.child, this);
            } else {
                this.child = createVNode(unboxed, this);
            }
            return result;
        }
        handle(event, context) {
            const fn = this.store[event];
            if (fn) {
                const nodes =
                    context.nodes.length === 0 ? [null] : context.nodes;
                fn(...nodes);
            }
        }
        attached(context) {
            this.deletePlugins();
            this.handle(symbols.CREATED, context);
            this.handle(symbols.RENDERED, context);
        }
        detached(context) {
            this.handle(symbols.REMOVED, context);
        }
        updated(context) {
            this.deletePlugins();
            this.handle(symbols.UPDATED, context);
            this.handle(symbols.RENDERED, context);
        }
    }
    ComponentVNode.context = null;
    function getComponentContext() {
        return ComponentVNode.context;
    }
    class TextVNode extends VNodeBase {
        constructor(text, parent) {
            super(parent);
            this.text = text;
        }
        matches(other) {
            return other instanceof TextVNode;
        }
        children() {
            return [this.child];
        }
        getExistingNode(context) {
            const {parent} = context;
            let node;
            if (context.node instanceof Text) {
                node = context.node;
            } else if (
                !isElementRefined(parent, context.vdom) &&
                context.vdom.isDOMNodeCaptured(parent)
            ) {
                const sibling = context.sibling;
                const guess = sibling ? sibling.nextSibling : parent.firstChild;
                if (
                    guess &&
                    !context.vdom.isDOMNodeCaptured(guess) &&
                    guess instanceof Text
                ) {
                    node = guess;
                }
            }
            return node;
        }
        attach(context) {
            const existing = this.getExistingNode(context);
            let node;
            if (existing) {
                node = existing;
                node.textContent = this.text;
            } else {
                node = document.createTextNode(this.text);
            }
            this.child = createVNode(node, this);
        }
        update(prev, context) {
            const prevContext = context.vdom.getVNodeContext(prev);
            const {node} = prevContext;
            if (this.text !== prev.text) {
                node.textContent = this.text;
            }
            this.child = createVNode(node, this);
        }
    }
    class InlineFunctionVNode extends VNodeBase {
        constructor(fn, parent) {
            super(parent);
            this.fn = fn;
        }
        matches(other) {
            return other instanceof InlineFunctionVNode;
        }
        children() {
            return [this.child];
        }
        call(context) {
            const fn = this.fn;
            const inlineFnContext = {
                parent: context.parent,
                get node() {
                    return context.node;
                },
                get nodes() {
                    return context.nodes;
                }
            };
            const result = fn(inlineFnContext);
            this.child = createVNode(result, this);
        }
        attach(context) {
            this.call(context);
        }
        update(prev, context) {
            const prevContext = context.vdom.getVNodeContext(prev);
            this.call(prevContext);
        }
    }
    class NullVNode extends VNodeBase {
        matches(other) {
            return other instanceof NullVNode;
        }
    }
    class DOMVNode extends VNodeBase {
        constructor(node, childSpecs, parent, isNative) {
            super(parent);
            this.node = node;
            this.childSpecs = childSpecs;
            this.isNative = isNative;
        }
        matches(other) {
            return other instanceof DOMVNode && this.node === other.node;
        }
        wrap() {
            this.childVNodes = this.childSpecs.map((spec) =>
                createVNode(spec, this)
            );
        }
        insertNode(context) {
            const {parent, sibling} = context;
            const shouldInsert = !(
                parent === this.node.parentElement &&
                sibling === this.node.previousSibling
            );
            if (shouldInsert) {
                const target = sibling
                    ? sibling.nextSibling
                    : parent.firstChild;
                parent.insertBefore(this.node, target);
            }
        }
        attach(context) {
            this.wrap();
            this.insertNode(context);
        }
        detach(context) {
            context.parent.removeChild(this.node);
        }
        update(prev, context) {
            this.wrap();
            this.insertNode(context);
        }
        cleanupDOMChildren(context) {
            const element = this.node;
            for (let current = element.lastChild; current != null; ) {
                if (context.vdom.isDOMNodeCaptured(current)) {
                    current = current.previousSibling;
                } else {
                    const prev = current.previousSibling;
                    element.removeChild(current);
                    current = prev;
                }
            }
        }
        refine(context) {
            if (!this.isNative) {
                this.cleanupDOMChildren(context);
            }
            const element = this.node;
            markElementAsRefined(element, context.vdom);
        }
        attached(context) {
            const {node} = this;
            if (
                node instanceof Element &&
                !isElementRefined(node, context.vdom) &&
                context.vdom.isDOMNodeCaptured(node)
            ) {
                this.refine(context);
            }
        }
        children() {
            return this.childVNodes;
        }
    }
    function isDOMVNode(v) {
        return v instanceof DOMVNode;
    }
    function createDOMVNode(node, childSpecs, parent, isNative) {
        return new DOMVNode(node, childSpecs, parent, isNative);
    }
    class ArrayVNode extends VNodeBase {
        constructor(items, key, parent) {
            super(parent);
            this.items = items;
            this.id = key;
        }
        matches(other) {
            return other instanceof ArrayVNode;
        }
        key() {
            return this.id;
        }
        children() {
            return this.childVNodes;
        }
        wrap() {
            this.childVNodes = this.items.map((spec) =>
                createVNode(spec, this)
            );
        }
        attach() {
            this.wrap();
        }
        update() {
            this.wrap();
        }
    }
    function createVNode(spec, parent) {
        if (isNodeSpec(spec)) {
            return new ElementVNode(spec, parent);
        }
        if (isComponentSpec(spec)) {
            if (spec.type === Array) {
                return new ArrayVNode(spec.children, spec.props.key, parent);
            }
            return new ComponentVNode(spec, parent);
        }
        if (typeof spec === "string") {
            return new TextVNode(spec, parent);
        }
        if (spec == null) {
            return new NullVNode(parent);
        }
        if (typeof spec === "function") {
            return new InlineFunctionVNode(spec, parent);
        }
        if (spec instanceof Node) {
            return createDOMVNode(spec, [], parent, true);
        }
        if (Array.isArray(spec)) {
            return new ArrayVNode(spec, null, parent);
        }
        throw new Error("Unable to create virtual node for spec");
    }

    function createVDOM(rootNode) {
        const contexts = new WeakMap();
        const hubs = new WeakMap();
        const parentNodes = new WeakMap();
        const passingLinks = new WeakMap();
        const linkedParents = new WeakSet();
        const LEAVE = Symbol();
        function execute$1(vnode, old) {
            execute(vnode, old, vdom);
        }
        function creatVNodeContext(vnode) {
            const parentNode = parentNodes.get(vnode);
            contexts.set(vnode, {
                parent: parentNode,
                get node() {
                    const linked = passingLinks
                        .get(vnode)
                        .find((link) => link.node != null);
                    return linked ? linked.node : null;
                },
                get nodes() {
                    return passingLinks
                        .get(vnode)
                        .map((link) => link.node)
                        .filter((node) => node);
                },
                get sibling() {
                    if (parentNode === rootNode.parentElement) {
                        return passingLinks.get(vnode).first.node
                            .previousSibling;
                    }
                    const hub = hubs.get(parentNode);
                    let current = passingLinks.get(vnode).first;
                    while ((current = hub.links.before(current))) {
                        if (current.node) {
                            return current.node;
                        }
                    }
                    return null;
                },
                vdom
            });
        }
        function createRootVNodeLinks(vnode) {
            const parentNode =
                rootNode.parentElement || document.createDocumentFragment();
            const node = rootNode;
            const links = new LinkedList({
                parentNode,
                node
            });
            passingLinks.set(vnode, links.copy());
            parentNodes.set(vnode, parentNode);
            hubs.set(parentNode, {
                node: parentNode,
                links
            });
        }
        function createVNodeLinks(vnode) {
            const parent = vnode.parent();
            const isBranch = linkedParents.has(parent);
            const parentNode = isDOMVNode(parent)
                ? parent.node
                : parentNodes.get(parent);
            parentNodes.set(vnode, parentNode);
            const vnodeLinks = new LinkedList();
            passingLinks.set(vnode, vnodeLinks);
            if (isBranch) {
                const newLink = {
                    parentNode,
                    node: null
                };
                let current = vnode;
                do {
                    passingLinks.get(current).push(newLink);
                    current = current.parent();
                } while (current && !isDOMVNode(current));
                hubs.get(parentNode).links.push(newLink);
            } else {
                linkedParents.add(parent);
                const links = isDOMVNode(parent)
                    ? hubs.get(parentNode).links
                    : passingLinks.get(parent);
                links.forEach((link) => vnodeLinks.push(link));
            }
        }
        function connectDOMVNode(vnode) {
            if (isDOMVNode(vnode)) {
                const {node} = vnode;
                hubs.set(node, {
                    node,
                    links: new LinkedList({
                        parentNode: node,
                        node: null
                    })
                });
                passingLinks.get(vnode).forEach((link) => (link.node = node));
            }
        }
        function addVNode(vnode) {
            const parent = vnode.parent();
            if (parent == null) {
                createRootVNodeLinks(vnode);
            } else {
                createVNodeLinks(vnode);
            }
            connectDOMVNode(vnode);
            creatVNodeContext(vnode);
        }
        function getVNodeContext(vnode) {
            return contexts.get(vnode);
        }
        function getAncestorsLinks(vnode) {
            const parentNode = parentNodes.get(vnode);
            const hub = hubs.get(parentNode);
            const allLinks = [];
            let current = vnode;
            while ((current = current.parent()) && !isDOMVNode(current)) {
                allLinks.push(passingLinks.get(current));
            }
            allLinks.push(hub.links);
            return allLinks;
        }
        function replaceVNode(old, vnode) {
            if (vnode.parent() == null) {
                addVNode(vnode);
                return;
            }
            const oldContext = contexts.get(old);
            const {parent: parentNode} = oldContext;
            parentNodes.set(vnode, parentNode);
            const oldLinks = passingLinks.get(old);
            const newLink = {
                parentNode,
                node: null
            };
            getAncestorsLinks(vnode).forEach((links) => {
                const nextLink = links.after(oldLinks.last);
                oldLinks.forEach((link) => links.delete(link));
                if (nextLink) {
                    links.insertBefore(newLink, nextLink);
                } else {
                    links.push(newLink);
                }
            });
            const vnodeLinks = new LinkedList(newLink);
            passingLinks.set(vnode, vnodeLinks);
            creatVNodeContext(vnode);
        }
        function adoptVNode(vnode, parent) {
            const vnodeLinks = passingLinks.get(vnode);
            const parentLinks = passingLinks.get(parent).copy();
            vnode.parent(parent);
            getAncestorsLinks(vnode).forEach((links) => {
                vnodeLinks.forEach((link) =>
                    links.insertBefore(link, parentLinks.first)
                );
                parentLinks.forEach((link) => links.delete(link));
            });
        }
        function isDOMNodeCaptured(node) {
            return hubs.has(node) && node !== rootNode.parentElement;
        }
        const vdom = {
            execute: execute$1,
            addVNode,
            getVNodeContext,
            replaceVNode,
            adoptVNode,
            isDOMNodeCaptured,
            LEAVE
        };
        return vdom;
    }

    const roots = new WeakMap();
    const vdoms = new WeakMap();
    function realize(node, vnode) {
        const old = roots.get(node) || null;
        roots.set(node, vnode);
        let vdom;
        if (vdoms.has(node)) {
            vdom = vdoms.get(node);
        } else {
            vdom = createVDOM(node);
            vdoms.set(node, vdom);
        }
        vdom.execute(vnode, old);
        return vdom.getVNodeContext(vnode);
    }
    function render$1(element, spec) {
        const vnode = createDOMVNode(
            element,
            Array.isArray(spec) ? spec : [spec],
            null,
            false
        );
        realize(element, vnode);
        return element;
    }
    function sync(node, spec) {
        const vnode = createVNode(spec, null);
        const context = realize(node, vnode);
        const {nodes} = context;
        if (nodes.length !== 1 || nodes[0] !== node) {
            throw new Error("Spec does not match the node");
        }
        return nodes[0];
    }

    function normalize(attrsOrChild, ...otherChildren) {
        const attrs =
            isObject(attrsOrChild) && !isSpec(attrsOrChild)
                ? attrsOrChild
                : null;
        const children =
            attrs == null
                ? [attrsOrChild].concat(otherChildren)
                : otherChildren;
        return {attrs, children};
    }
    function createTagFunction(tag) {
        return (attrsOrChild, ...otherChildren) => {
            const {attrs, children} = normalize(attrsOrChild, otherChildren);
            return m(tag, attrs, children);
        };
    }
    new Proxy(
        {},
        {
            get: (_, tag) => {
                return createTagFunction(tag);
            }
        }
    );

    var MessageTypeUItoBG;
    (function (MessageTypeUItoBG) {
        MessageTypeUItoBG["GET_DATA"] = "ui-bg-get-data";
        MessageTypeUItoBG["GET_DEVTOOLS_DATA"] = "ui-bg-get-devtools-data";
        MessageTypeUItoBG["SUBSCRIBE_TO_CHANGES"] =
            "ui-bg-subscribe-to-changes";
        MessageTypeUItoBG["UNSUBSCRIBE_FROM_CHANGES"] =
            "ui-bg-unsubscribe-from-changes";
        MessageTypeUItoBG["CHANGE_SETTINGS"] = "ui-bg-change-settings";
        MessageTypeUItoBG["SET_THEME"] = "ui-bg-set-theme";
        MessageTypeUItoBG["TOGGLE_ACTIVE_TAB"] = "ui-bg-toggle-active-tab";
        MessageTypeUItoBG["MARK_NEWS_AS_READ"] = "ui-bg-mark-news-as-read";
        MessageTypeUItoBG["MARK_NEWS_AS_DISPLAYED"] =
            "ui-bg-mark-news-as-displayed";
        MessageTypeUItoBG["LOAD_CONFIG"] = "ui-bg-load-config";
        MessageTypeUItoBG["APPLY_DEV_DYNAMIC_THEME_FIXES"] =
            "ui-bg-apply-dev-dynamic-theme-fixes";
        MessageTypeUItoBG["RESET_DEV_DYNAMIC_THEME_FIXES"] =
            "ui-bg-reset-dev-dynamic-theme-fixes";
        MessageTypeUItoBG["APPLY_DEV_INVERSION_FIXES"] =
            "ui-bg-apply-dev-inversion-fixes";
        MessageTypeUItoBG["RESET_DEV_INVERSION_FIXES"] =
            "ui-bg-reset-dev-inversion-fixes";
        MessageTypeUItoBG["APPLY_DEV_STATIC_THEMES"] =
            "ui-bg-apply-dev-static-themes";
        MessageTypeUItoBG["RESET_DEV_STATIC_THEMES"] =
            "ui-bg-reset-dev-static-themes";
        MessageTypeUItoBG["START_ACTIVATION"] = "ui-bg-start-activation";
        MessageTypeUItoBG["RESET_ACTIVATION"] = "ui-bg-reset-activation";
        MessageTypeUItoBG["COLOR_SCHEME_CHANGE"] = "ui-bg-color-scheme-change";
        MessageTypeUItoBG["HIDE_HIGHLIGHTS"] = "ui-bg-hide-highlights";
    })(MessageTypeUItoBG || (MessageTypeUItoBG = {}));
    var MessageTypeBGtoUI;
    (function (MessageTypeBGtoUI) {
        MessageTypeBGtoUI["CHANGES"] = "bg-ui-changes";
    })(MessageTypeBGtoUI || (MessageTypeBGtoUI = {}));
    var DebugMessageTypeBGtoUI;
    (function (DebugMessageTypeBGtoUI) {
        DebugMessageTypeBGtoUI["CSS_UPDATE"] = "debug-bg-ui-css-update";
        DebugMessageTypeBGtoUI["UPDATE"] = "debug-bg-ui-update";
    })(DebugMessageTypeBGtoUI || (DebugMessageTypeBGtoUI = {}));
    var MessageTypeBGtoCS;
    (function (MessageTypeBGtoCS) {
        MessageTypeBGtoCS["ADD_CSS_FILTER"] = "bg-cs-add-css-filter";
        MessageTypeBGtoCS["ADD_DYNAMIC_THEME"] = "bg-cs-add-dynamic-theme";
        MessageTypeBGtoCS["ADD_STATIC_THEME"] = "bg-cs-add-static-theme";
        MessageTypeBGtoCS["ADD_SVG_FILTER"] = "bg-cs-add-svg-filter";
        MessageTypeBGtoCS["CLEAN_UP"] = "bg-cs-clean-up";
        MessageTypeBGtoCS["FETCH_RESPONSE"] = "bg-cs-fetch-response";
        MessageTypeBGtoCS["UNSUPPORTED_SENDER"] = "bg-cs-unsupported-sender";
    })(MessageTypeBGtoCS || (MessageTypeBGtoCS = {}));
    var DebugMessageTypeBGtoCS;
    (function (DebugMessageTypeBGtoCS) {
        DebugMessageTypeBGtoCS["RELOAD"] = "debug-bg-cs-reload";
    })(DebugMessageTypeBGtoCS || (DebugMessageTypeBGtoCS = {}));
    var MessageTypeCStoBG;
    (function (MessageTypeCStoBG) {
        MessageTypeCStoBG["COLOR_SCHEME_CHANGE"] = "cs-bg-color-scheme-change";
        MessageTypeCStoBG["DARK_THEME_DETECTED"] = "cs-bg-dark-theme-detected";
        MessageTypeCStoBG["DARK_THEME_NOT_DETECTED"] =
            "cs-bg-dark-theme-not-detected";
        MessageTypeCStoBG["FETCH"] = "cs-bg-fetch";
        MessageTypeCStoBG["DOCUMENT_CONNECT"] = "cs-bg-document-connect";
        MessageTypeCStoBG["DOCUMENT_FORGET"] = "cs-bg-document-forget";
        MessageTypeCStoBG["DOCUMENT_FREEZE"] = "cs-bg-document-freeze";
        MessageTypeCStoBG["DOCUMENT_RESUME"] = "cs-bg-document-resume";
    })(MessageTypeCStoBG || (MessageTypeCStoBG = {}));
    var DebugMessageTypeCStoBG;
    (function (DebugMessageTypeCStoBG) {
        DebugMessageTypeCStoBG["LOG"] = "debug-cs-bg-log";
    })(DebugMessageTypeCStoBG || (DebugMessageTypeCStoBG = {}));
    var MessageTypeCStoUI;
    (function (MessageTypeCStoUI) {
        MessageTypeCStoUI["EXPORT_CSS_RESPONSE"] = "cs-ui-export-css-response";
    })(MessageTypeCStoUI || (MessageTypeCStoUI = {}));
    var MessageTypeUItoCS;
    (function (MessageTypeUItoCS) {
        MessageTypeUItoCS["EXPORT_CSS"] = "ui-cs-export-css";
    })(MessageTypeUItoCS || (MessageTypeUItoCS = {}));

    const isNavigatorDefined = typeof navigator !== "undefined";
    const userAgent = isNavigatorDefined
        ? navigator.userAgentData &&
          Array.isArray(navigator.userAgentData.brands)
            ? navigator.userAgentData.brands
                  .map(
                      (brand) => `${brand.brand.toLowerCase()} ${brand.version}`
                  )
                  .join(" ")
            : navigator.userAgent.toLowerCase()
        : "some useragent";
    const platform = isNavigatorDefined
        ? navigator.userAgentData &&
          typeof navigator.userAgentData.platform === "string"
            ? navigator.userAgentData.platform.toLowerCase()
            : navigator.platform.toLowerCase()
        : "some platform";
    const isFirefox = false;
    userAgent.includes("vivaldi");
    userAgent.includes("yabrowser");
    userAgent.includes("opr") || userAgent.includes("opera");
    const isEdge = userAgent.includes("edg");
    const isWindows = platform.startsWith("win");
    const isMacOS = platform.startsWith("mac");
    const isMobile =
        isNavigatorDefined && navigator.userAgentData
            ? navigator.userAgentData.mobile
            : userAgent.includes("mobile") || false;
    const isMatchMediaChangeEventListenerBuggy =
        (isNavigatorDefined &&
            navigator.userAgentData &&
            ["Linux", "Android"].includes(navigator.userAgentData.platform)) ||
        platform.startsWith("linux");
    (() => {
        const m = userAgent.match(/chrom(?:e|ium)(?:\/| )([^ ]+)/);
        if (m && m[1]) {
            return m[1];
        }
        return "";
    })();
    (() => {
        const m = userAgent.match(/(?:firefox|librewolf)(?:\/| )([^ ]+)/);
        if (m && m[1]) {
            return m[1];
        }
        return "";
    })();
    (() => {
        try {
            document.querySelector(":defined");
            return true;
        } catch (err) {
            return false;
        }
    })();
    const isCSSColorSchemePropSupported = (() => {
        try {
            if (typeof document === "undefined") {
                return false;
            }
            const el = document.createElement("div");
            if (!el || typeof el.style !== "object") {
                return false;
            }
            if (typeof el.style.colorScheme === "string") {
                return true;
            }
            el.setAttribute("style", "color-scheme: dark");
            return el.style.colorScheme === "dark";
        } catch (e) {
            return false;
        }
    })();

    class Connector {
        constructor() {
            this.onChangesReceived = ({type, data}) => {
                if (type === MessageTypeBGtoUI.CHANGES) {
                    this.changeSubscribers.forEach((callback) =>
                        callback(data)
                    );
                }
            };
            this.changeSubscribers = new Set();
        }
        async sendRequest(type, data) {
            return new Promise((resolve, reject) => {
                chrome.runtime.sendMessage({type, data}, ({data, error}) => {
                    if (error) {
                        reject(error);
                    } else {
                        resolve(data);
                    }
                });
            });
        }
        async firefoxSendRequestWithResponse(type, data) {
            return new Promise((resolve, reject) => {
                const dataPort = chrome.runtime.connect({name: type});
                dataPort.onDisconnect.addListener(() => reject());
                dataPort.onMessage.addListener(({data, error}) => {
                    if (error) {
                        reject(error);
                    } else {
                        resolve(data);
                    }
                    dataPort.disconnect();
                });
                data && dataPort.postMessage({data});
            });
        }
        async getData() {
            return await this.sendRequest(MessageTypeUItoBG.GET_DATA);
        }
        async getDevToolsData() {
            return await this.sendRequest(MessageTypeUItoBG.GET_DEVTOOLS_DATA);
        }
        subscribeToChanges(callback) {
            this.changeSubscribers.add(callback);
            if (this.changeSubscribers.size === 1) {
                chrome.runtime.onMessage.addListener(this.onChangesReceived);
                chrome.runtime.sendMessage({
                    type: MessageTypeUItoBG.SUBSCRIBE_TO_CHANGES
                });
            }
        }
        async setShortcut(command, shortcut) {
            return null;
        }
        changeSettings(settings) {
            chrome.runtime.sendMessage({
                type: MessageTypeUItoBG.CHANGE_SETTINGS,
                data: settings
            });
        }
        setTheme(theme) {
            chrome.runtime.sendMessage({
                type: MessageTypeUItoBG.SET_THEME,
                data: theme
            });
        }
        toggleActiveTab() {
            chrome.runtime.sendMessage({
                type: MessageTypeUItoBG.TOGGLE_ACTIVE_TAB,
                data: {}
            });
        }
        markNewsAsRead(ids) {
            chrome.runtime.sendMessage({
                type: MessageTypeUItoBG.MARK_NEWS_AS_READ,
                data: ids
            });
        }
        markNewsAsDisplayed(ids) {
            chrome.runtime.sendMessage({
                type: MessageTypeUItoBG.MARK_NEWS_AS_DISPLAYED,
                data: ids
            });
        }
        loadConfig(options) {
            chrome.runtime.sendMessage({
                type: MessageTypeUItoBG.LOAD_CONFIG,
                data: options
            });
        }
        async applyDevDynamicThemeFixes(text) {
            return await this.sendRequest(
                MessageTypeUItoBG.APPLY_DEV_DYNAMIC_THEME_FIXES,
                text
            );
        }
        resetDevDynamicThemeFixes() {
            chrome.runtime.sendMessage({
                type: MessageTypeUItoBG.RESET_DEV_DYNAMIC_THEME_FIXES
            });
        }
        async applyDevInversionFixes(text) {
            return await this.sendRequest(
                MessageTypeUItoBG.APPLY_DEV_INVERSION_FIXES,
                text
            );
        }
        resetDevInversionFixes() {
            chrome.runtime.sendMessage({
                type: MessageTypeUItoBG.RESET_DEV_INVERSION_FIXES
            });
        }
        async applyDevStaticThemes(text) {
            return await this.sendRequest(
                MessageTypeUItoBG.APPLY_DEV_STATIC_THEMES,
                text
            );
        }
        resetDevStaticThemes() {
            chrome.runtime.sendMessage({
                type: MessageTypeUItoBG.RESET_DEV_STATIC_THEMES
            });
        }
        startActivation(email, key) {
            chrome.runtime.sendMessage({
                type: MessageTypeUItoBG.START_ACTIVATION,
                data: {email, key}
            });
        }
        resetActivation() {
            chrome.runtime.sendMessage({
                type: MessageTypeUItoBG.RESET_ACTIVATION
            });
        }
        async hideHighlights(ids) {
            chrome.runtime.sendMessage({
                type: MessageTypeUItoBG.HIDE_HIGHLIGHTS,
                data: ids
            });
        }
        disconnect() {
            if (this.changeSubscribers.size > 0) {
                this.changeSubscribers.clear();
                chrome.runtime.onMessage.removeListener(this.onChangesReceived);
                chrome.runtime.sendMessage({
                    type: MessageTypeUItoBG.UNSUBSCRIBE_FROM_CHANGES
                });
            }
        }
    }

    function classes(...args) {
        const classes = [];
        args.filter((c) => Boolean(c)).forEach((c) => {
            if (typeof c === "string") {
                classes.push(c);
            } else if (typeof c === "object") {
                classes.push(
                    ...Object.keys(c).filter((key) => Boolean(c[key]))
                );
            }
        });
        return classes.join(" ");
    }
    function openFile(options, callback) {
        const input = document.createElement("input");
        input.type = "file";
        input.style.display = "none";
        if (options.extensions && options.extensions.length > 0) {
            input.accept = options.extensions.map((ext) => `.${ext}`).join(",");
        }
        const reader = new FileReader();
        reader.onloadend = () => callback(reader.result);
        input.onchange = () => {
            if (input.files[0]) {
                reader.readAsText(input.files[0]);
                document.body.removeChild(input);
            }
        };
        document.body.appendChild(input);
        input.click();
    }
    function saveFile(name, content) {
        const a = document.createElement("a");
        a.href = URL.createObjectURL(new Blob([content]));
        a.download = name;
        a.click();
    }
    function throttle(callback) {
        let frameId = null;
        return (...args) => {
            if (!frameId) {
                callback(...args);
                frameId = requestAnimationFrame(() => (frameId = null));
            }
        };
    }
    function onSwipeStart(startEventObj, startHandler) {
        const isTouchEvent =
            typeof TouchEvent !== "undefined" &&
            startEventObj instanceof TouchEvent;
        const touchId = isTouchEvent
            ? startEventObj.changedTouches[0].identifier
            : null;
        const pointerMoveEvent = isTouchEvent ? "touchmove" : "mousemove";
        const pointerUpEvent = isTouchEvent ? "touchend" : "mouseup";
        if (!isTouchEvent) {
            startEventObj.preventDefault();
        }
        function getSwipeEventObject(e) {
            const {clientX, clientY} = isTouchEvent ? getTouch(e) : e;
            return {clientX, clientY};
        }
        const startSE = getSwipeEventObject(startEventObj);
        const {move: moveHandler, up: upHandler} = startHandler(
            startSE,
            startEventObj
        );
        function getTouch(e) {
            return Array.from(e.changedTouches).find(
                ({identifier: id}) => id === touchId
            );
        }
        const onPointerMove = throttle((e) => {
            const se = getSwipeEventObject(e);
            moveHandler(se, e);
        });
        function onPointerUp(e) {
            unsubscribe();
            const se = getSwipeEventObject(e);
            upHandler(se, e);
        }
        function unsubscribe() {
            window.removeEventListener(pointerMoveEvent, onPointerMove);
            window.removeEventListener(pointerUpEvent, onPointerUp);
        }
        window.addEventListener(pointerMoveEvent, onPointerMove, {
            passive: true
        });
        window.addEventListener(pointerUpEvent, onPointerUp, {passive: true});
    }
    function createSwipeHandler(startHandler) {
        return (e) => onSwipeStart(e, startHandler);
    }
    async function getExtensionPageTab(url) {
        return new Promise((resolve) => {
            chrome.tabs.query(
                {
                    url
                },
                ([tab]) => resolve(tab || null)
            );
        });
    }
    async function openExtensionPage(page) {
        const url = chrome.runtime.getURL(`/ui/${page}/index.html`);
        if (isMobile || page === "options") {
            const extensionPageTab = await getExtensionPageTab(url);
            if (extensionPageTab !== null) {
                chrome.tabs.update(extensionPageTab.id, {active: true});
                window.close();
            } else {
                chrome.tabs.create({url});
                window.close();
            }
        } else {
            const extensionPageTab = await getExtensionPageTab(url);
            if (extensionPageTab !== null) {
                chrome.windows.update(extensionPageTab.windowId, {
                    focused: true
                });
                window.close();
            } else {
                chrome.windows.create({
                    type: "popup",
                    url,
                    width: 800,
                    height: 600
                });
                window.close();
            }
        }
    }

    function toArray(x) {
        return Array.isArray(x) ? x : [x];
    }
    function mergeClass(cls, propsCls) {
        const normalized = toArray(cls).concat(toArray(propsCls));
        return classes(...normalized);
    }
    function omitAttrs(omit, attrs) {
        const result = {};
        Object.keys(attrs).forEach((key) => {
            if (omit.indexOf(key) < 0) {
                result[key] = attrs[key];
            }
        });
        return result;
    }
    function isElementHidden(element) {
        return element.offsetParent === null;
    }

    function Button(props, ...children) {
        const cls = mergeClass("button", props.class);
        const attrs = omitAttrs(["class"], props);
        return m$1(
            "button",
            {class: cls, ...attrs},
            m$1("span", {class: "button__wrapper"}, ...children)
        );
    }

    function CheckBox(props, ...children) {
        const cls = mergeClass("checkbox", props.class);
        const attrs = omitAttrs(["class", "checked", "onchange"], props);
        const check = (domNode) => (domNode.checked = Boolean(props.checked));
        return m$1(
            "label",
            {class: cls, ...attrs},
            m$1("input", {
                class: "checkbox__input",
                type: "checkbox",
                checked: props.checked,
                onchange: props.onchange,
                onrender: check
            }),
            m$1("span", {class: "checkbox__checkmark"}),
            m$1("span", {class: "checkbox__content"}, children)
        );
    }

    function ControlGroup(props, control, description) {
        return m$1(
            "span",
            {class: ["control-group", props.class]},
            control,
            description
        );
    }
    function Control(props, ...content) {
        return m$1(
            "span",
            {class: ["control-group__control", props.class]},
            ...content
        );
    }
    function Description(props, ...content) {
        return m$1(
            "span",
            {class: ["control-group__description", props.class]},
            ...content
        );
    }
    var ControlGroup$1 = Object.assign(ControlGroup, {Control, Description});

    function CheckButton(props) {
        return m$1(
            ControlGroup$1,
            {class: "check-button"},
            m$1(
                ControlGroup$1.Control,
                null,
                m$1(
                    CheckBox,
                    {
                        class: "check-button__checkbox",
                        checked: props.checked,
                        onchange: (e) => props.onChange(e.target.checked)
                    },
                    props.label
                )
            ),
            m$1(
                ControlGroup$1.Description,
                {class: "check-button__description"},
                props.description
            )
        );
    }

    function evalMath(expression) {
        const rpnStack = [];
        const workingStack = [];
        let lastToken;
        for (let i = 0, len = expression.length; i < len; i++) {
            const token = expression[i];
            if (!token || token === " ") {
                continue;
            }
            if (operators.has(token)) {
                const op = operators.get(token);
                while (workingStack.length) {
                    const currentOp = operators.get(workingStack[0]);
                    if (!currentOp) {
                        break;
                    }
                    if (op.lessOrEqualThan(currentOp)) {
                        rpnStack.push(workingStack.shift());
                    } else {
                        break;
                    }
                }
                workingStack.unshift(token);
            } else if (!lastToken || operators.has(lastToken)) {
                rpnStack.push(token);
            } else {
                rpnStack[rpnStack.length - 1] += token;
            }
            lastToken = token;
        }
        rpnStack.push(...workingStack);
        const stack = [];
        for (let i = 0, len = rpnStack.length; i < len; i++) {
            const op = operators.get(rpnStack[i]);
            if (op) {
                const args = stack.splice(0, 2);
                stack.push(op.exec(args[1], args[0]));
            } else {
                stack.unshift(parseFloat(rpnStack[i]));
            }
        }
        return stack[0];
    }
    class Operator {
        constructor(precedence, method) {
            this.precendce = precedence;
            this.execMethod = method;
        }
        exec(left, right) {
            return this.execMethod(left, right);
        }
        lessOrEqualThan(op) {
            return this.precendce <= op.precendce;
        }
    }
    const operators = new Map([
        ["+", new Operator(1, (left, right) => left + right)],
        ["-", new Operator(1, (left, right) => left - right)],
        ["*", new Operator(2, (left, right) => left * right)],
        ["/", new Operator(2, (left, right) => left / right)]
    ]);

    const isSystemDarkModeEnabled = () =>
        matchMedia("(prefers-color-scheme: dark)").matches;

    function getParenthesesRange(input, searchStartIndex = 0) {
        return getOpenCloseRange(input, searchStartIndex, "(", ")", []);
    }
    function getOpenCloseRange(
        input,
        searchStartIndex,
        openToken,
        closeToken,
        excludeRanges
    ) {
        let indexOf;
        if (excludeRanges.length === 0) {
            indexOf = (token, pos) => input.indexOf(token, pos);
        } else {
            indexOf = (token, pos) =>
                indexOfExcluding(input, token, pos, excludeRanges);
        }
        const {length} = input;
        let depth = 0;
        let firstOpenIndex = -1;
        for (let i = searchStartIndex; i < length; i++) {
            if (depth === 0) {
                const openIndex = indexOf(openToken, i);
                if (openIndex < 0) {
                    break;
                }
                firstOpenIndex = openIndex;
                depth++;
                i = openIndex;
            } else {
                const closeIndex = indexOf(closeToken, i);
                if (closeIndex < 0) {
                    break;
                }
                const openIndex = indexOf(openToken, i);
                if (openIndex < 0 || closeIndex <= openIndex) {
                    depth--;
                    if (depth === 0) {
                        return {start: firstOpenIndex, end: closeIndex + 1};
                    }
                    i = closeIndex;
                } else {
                    depth++;
                    i = openIndex;
                }
            }
        }
        return null;
    }
    function indexOfExcluding(input, search, position, excludeRanges) {
        const i = input.indexOf(search, position);
        const exclusion = excludeRanges.find((r) => i >= r.start && i < r.end);
        if (exclusion) {
            return indexOfExcluding(
                input,
                search,
                exclusion.end,
                excludeRanges
            );
        }
        return i;
    }

    const rgbaParseCache = new Map();
    function parseColorWithCache($color) {
        $color = $color.trim();
        if (rgbaParseCache.has($color)) {
            return rgbaParseCache.get($color);
        }
        if ($color.includes("calc(")) {
            $color = lowerCalcExpression($color);
        }
        const color = parse($color);
        if (color) {
            rgbaParseCache.set($color, color);
            return color;
        }
        return null;
    }
    function hslToRGB({h, s, l, a = 1}) {
        if (s === 0) {
            const [r, b, g] = [l, l, l].map((x) => Math.round(x * 255));
            return {r, g, b, a};
        }
        const c = (1 - Math.abs(2 * l - 1)) * s;
        const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
        const m = l - c / 2;
        const [r, g, b] = (
            h < 60
                ? [c, x, 0]
                : h < 120
                  ? [x, c, 0]
                  : h < 180
                    ? [0, c, x]
                    : h < 240
                      ? [0, x, c]
                      : h < 300
                        ? [x, 0, c]
                        : [c, 0, x]
        ).map((n) => Math.round((n + m) * 255));
        return {r, g, b, a};
    }
    function rgbToHSL({r: r255, g: g255, b: b255, a = 1}) {
        const r = r255 / 255;
        const g = g255 / 255;
        const b = b255 / 255;
        const max = Math.max(r, g, b);
        const min = Math.min(r, g, b);
        const c = max - min;
        const l = (max + min) / 2;
        if (c === 0) {
            return {h: 0, s: 0, l, a};
        }
        let h =
            (max === r
                ? ((g - b) / c) % 6
                : max === g
                  ? (b - r) / c + 2
                  : (r - g) / c + 4) * 60;
        if (h < 0) {
            h += 360;
        }
        const s = c / (1 - Math.abs(2 * l - 1));
        return {h, s, l, a};
    }
    function toFixed(n, digits = 0) {
        const fixed = n.toFixed(digits);
        if (digits === 0) {
            return fixed;
        }
        const dot = fixed.indexOf(".");
        if (dot >= 0) {
            const zerosMatch = fixed.match(/0+$/);
            if (zerosMatch) {
                if (zerosMatch.index === dot + 1) {
                    return fixed.substring(0, dot);
                }
                return fixed.substring(0, zerosMatch.index);
            }
        }
        return fixed;
    }
    function rgbToHexString({r, g, b, a}) {
        return `#${[r, g, b]
            .map((x) => {
                return `${x < 16 ? "0" : ""}${x.toString(16)}`;
            })
            .join("")}`;
    }
    function hslToString(hsl) {
        const {h, s, l} = hsl;
        return `hsl(${toFixed(h)}, ${toFixed(s * 100)}%, ${toFixed(l * 100)}%)`;
    }
    const rgbMatch = /^rgba?\([^\(\)]+\)$/;
    const hslMatch = /^hsla?\([^\(\)]+\)$/;
    const hexMatch = /^#[0-9a-f]+$/i;
    const supportedColorFuncs = [
        "color",
        "color-mix",
        "hwb",
        "lab",
        "lch",
        "oklab",
        "oklch"
    ];
    function parse($color) {
        const c = $color.trim().toLowerCase();
        if (c.includes("(from ")) {
            if (c.indexOf("(from") !== c.lastIndexOf("(from")) {
                return null;
            }
            return domParseColor(c);
        }
        if (c.match(rgbMatch)) {
            if (c.startsWith("rgb(#") || c.startsWith("rgba(#")) {
                if (c.lastIndexOf("rgb") > 0) {
                    return null;
                }
                return domParseColor(c);
            }
            return parseRGB(c);
        }
        if (c.match(hslMatch)) {
            return parseHSL(c);
        }
        if (c.match(hexMatch)) {
            return parseHex(c);
        }
        if (knownColors.has(c)) {
            return getColorByName(c);
        }
        if (systemColors.has(c)) {
            return getSystemColor(c);
        }
        if (c === "transparent") {
            return {r: 0, g: 0, b: 0, a: 0};
        }
        if (
            c.endsWith(")") &&
            supportedColorFuncs.some(
                (fn) =>
                    c.startsWith(fn) &&
                    c[fn.length] === "(" &&
                    c.lastIndexOf(fn) === 0
            )
        ) {
            return domParseColor(c);
        }
        if (c.startsWith("light-dark(") && c.endsWith(")")) {
            const match = c.match(
                /^light-dark\(\s*([a-z]+(\(.*\))?),\s*([a-z]+(\(.*\))?)\s*\)$/
            );
            if (match) {
                const schemeColor = isSystemDarkModeEnabled()
                    ? match[3]
                    : match[1];
                return parse(schemeColor);
            }
        }
        return null;
    }
    function getNumbers($color) {
        const numbers = [];
        let prevPos = 0;
        let isMining = false;
        const startIndex = $color.indexOf("(");
        $color = $color.substring(startIndex + 1, $color.length - 1);
        for (let i = 0; i < $color.length; i++) {
            const c = $color[i];
            if ((c >= "0" && c <= "9") || c === "." || c === "+" || c === "-") {
                isMining = true;
            } else if (isMining && (c === " " || c === "," || c === "/")) {
                numbers.push($color.substring(prevPos, i));
                isMining = false;
                prevPos = i + 1;
            } else if (!isMining) {
                prevPos = i + 1;
            }
        }
        if (isMining) {
            numbers.push($color.substring(prevPos, $color.length));
        }
        return numbers;
    }
    function getNumbersFromString(str, range, units) {
        const raw = getNumbers(str);
        const unitsList = Object.entries(units);
        const numbers = raw
            .map((r) => r.trim())
            .map((r, i) => {
                let n;
                const unit = unitsList.find(([u]) => r.endsWith(u));
                if (unit) {
                    n =
                        (parseFloat(r.substring(0, r.length - unit[0].length)) /
                            unit[1]) *
                        range[i];
                } else {
                    n = parseFloat(r);
                }
                if (range[i] > 1) {
                    return Math.round(n);
                }
                return n;
            });
        return numbers;
    }
    const rgbRange = [255, 255, 255, 1];
    const rgbUnits = {"%": 100};
    function parseRGB($rgb) {
        const [r, g, b, a = 1] = getNumbersFromString($rgb, rgbRange, rgbUnits);
        if (r == null || g == null || b == null || a == null) {
            return null;
        }
        return {r, g, b, a};
    }
    const hslRange = [360, 1, 1, 1];
    const hslUnits = {"%": 100, "deg": 360, "rad": 2 * Math.PI, "turn": 1};
    function parseHSL($hsl) {
        const [h, s, l, a = 1] = getNumbersFromString($hsl, hslRange, hslUnits);
        if (h == null || s == null || l == null || a == null) {
            return null;
        }
        return hslToRGB({h, s, l, a});
    }
    function parseHex($hex) {
        const h = $hex.substring(1);
        switch (h.length) {
            case 3:
            case 4: {
                const [r, g, b] = [0, 1, 2].map((i) =>
                    parseInt(`${h[i]}${h[i]}`, 16)
                );
                const a =
                    h.length === 3 ? 1 : parseInt(`${h[3]}${h[3]}`, 16) / 255;
                return {r, g, b, a};
            }
            case 6:
            case 8: {
                const [r, g, b] = [0, 2, 4].map((i) =>
                    parseInt(h.substring(i, i + 2), 16)
                );
                const a =
                    h.length === 6 ? 1 : parseInt(h.substring(6, 8), 16) / 255;
                return {r, g, b, a};
            }
        }
        return null;
    }
    function getColorByName($color) {
        const n = knownColors.get($color);
        return {
            r: (n >> 16) & 255,
            g: (n >> 8) & 255,
            b: (n >> 0) & 255,
            a: 1
        };
    }
    function getSystemColor($color) {
        const n = systemColors.get($color);
        return {
            r: (n >> 16) & 255,
            g: (n >> 8) & 255,
            b: (n >> 0) & 255,
            a: 1
        };
    }
    function lowerCalcExpression(color) {
        let searchIndex = 0;
        const replaceBetweenIndices = (start, end, replacement) => {
            color =
                color.substring(0, start) + replacement + color.substring(end);
        };
        while ((searchIndex = color.indexOf("calc(")) !== -1) {
            const range = getParenthesesRange(color, searchIndex);
            if (!range) {
                break;
            }
            let slice = color.slice(range.start + 1, range.end - 1);
            const includesPercentage = slice.includes("%");
            slice = slice.split("%").join("");
            const output = Math.round(evalMath(slice));
            replaceBetweenIndices(
                range.start - 4,
                range.end,
                output + (includesPercentage ? "%" : "")
            );
        }
        return color;
    }
    const knownColors = new Map(
        Object.entries({
            aliceblue: 0xf0f8ff,
            antiquewhite: 0xfaebd7,
            aqua: 0x00ffff,
            aquamarine: 0x7fffd4,
            azure: 0xf0ffff,
            beige: 0xf5f5dc,
            bisque: 0xffe4c4,
            black: 0x000000,
            blanchedalmond: 0xffebcd,
            blue: 0x0000ff,
            blueviolet: 0x8a2be2,
            brown: 0xa52a2a,
            burlywood: 0xdeb887,
            cadetblue: 0x5f9ea0,
            chartreuse: 0x7fff00,
            chocolate: 0xd2691e,
            coral: 0xff7f50,
            cornflowerblue: 0x6495ed,
            cornsilk: 0xfff8dc,
            crimson: 0xdc143c,
            cyan: 0x00ffff,
            darkblue: 0x00008b,
            darkcyan: 0x008b8b,
            darkgoldenrod: 0xb8860b,
            darkgray: 0xa9a9a9,
            darkgrey: 0xa9a9a9,
            darkgreen: 0x006400,
            darkkhaki: 0xbdb76b,
            darkmagenta: 0x8b008b,
            darkolivegreen: 0x556b2f,
            darkorange: 0xff8c00,
            darkorchid: 0x9932cc,
            darkred: 0x8b0000,
            darksalmon: 0xe9967a,
            darkseagreen: 0x8fbc8f,
            darkslateblue: 0x483d8b,
            darkslategray: 0x2f4f4f,
            darkslategrey: 0x2f4f4f,
            darkturquoise: 0x00ced1,
            darkviolet: 0x9400d3,
            deeppink: 0xff1493,
            deepskyblue: 0x00bfff,
            dimgray: 0x696969,
            dimgrey: 0x696969,
            dodgerblue: 0x1e90ff,
            firebrick: 0xb22222,
            floralwhite: 0xfffaf0,
            forestgreen: 0x228b22,
            fuchsia: 0xff00ff,
            gainsboro: 0xdcdcdc,
            ghostwhite: 0xf8f8ff,
            gold: 0xffd700,
            goldenrod: 0xdaa520,
            gray: 0x808080,
            grey: 0x808080,
            green: 0x008000,
            greenyellow: 0xadff2f,
            honeydew: 0xf0fff0,
            hotpink: 0xff69b4,
            indianred: 0xcd5c5c,
            indigo: 0x4b0082,
            ivory: 0xfffff0,
            khaki: 0xf0e68c,
            lavender: 0xe6e6fa,
            lavenderblush: 0xfff0f5,
            lawngreen: 0x7cfc00,
            lemonchiffon: 0xfffacd,
            lightblue: 0xadd8e6,
            lightcoral: 0xf08080,
            lightcyan: 0xe0ffff,
            lightgoldenrodyellow: 0xfafad2,
            lightgray: 0xd3d3d3,
            lightgrey: 0xd3d3d3,
            lightgreen: 0x90ee90,
            lightpink: 0xffb6c1,
            lightsalmon: 0xffa07a,
            lightseagreen: 0x20b2aa,
            lightskyblue: 0x87cefa,
            lightslategray: 0x778899,
            lightslategrey: 0x778899,
            lightsteelblue: 0xb0c4de,
            lightyellow: 0xffffe0,
            lime: 0x00ff00,
            limegreen: 0x32cd32,
            linen: 0xfaf0e6,
            magenta: 0xff00ff,
            maroon: 0x800000,
            mediumaquamarine: 0x66cdaa,
            mediumblue: 0x0000cd,
            mediumorchid: 0xba55d3,
            mediumpurple: 0x9370db,
            mediumseagreen: 0x3cb371,
            mediumslateblue: 0x7b68ee,
            mediumspringgreen: 0x00fa9a,
            mediumturquoise: 0x48d1cc,
            mediumvioletred: 0xc71585,
            midnightblue: 0x191970,
            mintcream: 0xf5fffa,
            mistyrose: 0xffe4e1,
            moccasin: 0xffe4b5,
            navajowhite: 0xffdead,
            navy: 0x000080,
            oldlace: 0xfdf5e6,
            olive: 0x808000,
            olivedrab: 0x6b8e23,
            orange: 0xffa500,
            orangered: 0xff4500,
            orchid: 0xda70d6,
            palegoldenrod: 0xeee8aa,
            palegreen: 0x98fb98,
            paleturquoise: 0xafeeee,
            palevioletred: 0xdb7093,
            papayawhip: 0xffefd5,
            peachpuff: 0xffdab9,
            peru: 0xcd853f,
            pink: 0xffc0cb,
            plum: 0xdda0dd,
            powderblue: 0xb0e0e6,
            purple: 0x800080,
            rebeccapurple: 0x663399,
            red: 0xff0000,
            rosybrown: 0xbc8f8f,
            royalblue: 0x4169e1,
            saddlebrown: 0x8b4513,
            salmon: 0xfa8072,
            sandybrown: 0xf4a460,
            seagreen: 0x2e8b57,
            seashell: 0xfff5ee,
            sienna: 0xa0522d,
            silver: 0xc0c0c0,
            skyblue: 0x87ceeb,
            slateblue: 0x6a5acd,
            slategray: 0x708090,
            slategrey: 0x708090,
            snow: 0xfffafa,
            springgreen: 0x00ff7f,
            steelblue: 0x4682b4,
            tan: 0xd2b48c,
            teal: 0x008080,
            thistle: 0xd8bfd8,
            tomato: 0xff6347,
            turquoise: 0x40e0d0,
            violet: 0xee82ee,
            wheat: 0xf5deb3,
            white: 0xffffff,
            whitesmoke: 0xf5f5f5,
            yellow: 0xffff00,
            yellowgreen: 0x9acd32
        })
    );
    const systemColors = new Map(
        Object.entries({
            "ActiveBorder": 0x3b99fc,
            "ActiveCaption": 0x000000,
            "AppWorkspace": 0xaaaaaa,
            "Background": 0x6363ce,
            "ButtonFace": 0xffffff,
            "ButtonHighlight": 0xe9e9e9,
            "ButtonShadow": 0x9fa09f,
            "ButtonText": 0x000000,
            "CaptionText": 0x000000,
            "GrayText": 0x7f7f7f,
            "Highlight": 0xb2d7ff,
            "HighlightText": 0x000000,
            "InactiveBorder": 0xffffff,
            "InactiveCaption": 0xffffff,
            "InactiveCaptionText": 0x000000,
            "InfoBackground": 0xfbfcc5,
            "InfoText": 0x000000,
            "Menu": 0xf6f6f6,
            "MenuText": 0xffffff,
            "Scrollbar": 0xaaaaaa,
            "ThreeDDarkShadow": 0x000000,
            "ThreeDFace": 0xc0c0c0,
            "ThreeDHighlight": 0xffffff,
            "ThreeDLightShadow": 0xffffff,
            "ThreeDShadow": 0x000000,
            "Window": 0xececec,
            "WindowFrame": 0xaaaaaa,
            "WindowText": 0x000000,
            "-webkit-focus-ring-color": 0xe59700
        }).map(([key, value]) => [key.toLowerCase(), value])
    );
    let canvas;
    let context;
    function domParseColor($color) {
        if (!context) {
            canvas = document.createElement("canvas");
            canvas.width = 1;
            canvas.height = 1;
            context = canvas.getContext("2d", {willReadFrequently: true});
        }
        context.fillStyle = $color;
        context.fillRect(0, 0, 1, 1);
        const d = context.getImageData(0, 0, 1, 1).data;
        const color = `rgba(${d[0]}, ${d[1]}, ${d[2]}, ${(d[3] / 255).toFixed(2)})`;
        return parseRGB(color);
    }

    function TextBox(props) {
        const cls = mergeClass("textbox", props.class);
        const attrs = omitAttrs(["class", "type"], props);
        const type = props.type || "text";
        return m$1("input", {
            class: cls,
            type: type,
            spellcheck: "false",
            ...attrs
        });
    }

    function scale(x, inLow, inHigh, outLow, outHigh) {
        return ((x - inLow) * (outHigh - outLow)) / (inHigh - inLow) + outLow;
    }
    function clamp(x, min, max) {
        return Math.min(max, Math.max(min, x));
    }

    const hsbPickerDefaults = {
        wasPrevHidden: true,
        hueCanvasRendered: false,
        activeHSB: null,
        activeChangeHandler: null,
        hueTouchStartHandler: null,
        sbTouchStartHandler: null
    };
    function rgbToHSB({r, g, b}) {
        const min = Math.min(r, g, b);
        const max = Math.max(r, g, b);
        return {
            h: rgbToHSL({r, g, b}).h,
            s: max === 0 ? 0 : 1 - min / max,
            b: max / 255
        };
    }
    function hsbToRGB({h: hue, s: sat, b: br}) {
        let c;
        if (hue < 60) {
            c = [1, hue / 60, 0];
        } else if (hue < 120) {
            c = [(120 - hue) / 60, 1, 0];
        } else if (hue < 180) {
            c = [0, 1, (hue - 120) / 60];
        } else if (hue < 240) {
            c = [0, (240 - hue) / 60, 1];
        } else if (hue < 300) {
            c = [(hue - 240) / 60, 0, 1];
        } else {
            c = [1, 0, (360 - hue) / 60];
        }
        const max = Math.max(...c);
        const [r, g, b] = c
            .map((v) => v + (max - v) * (1 - sat))
            .map((v) => v * br)
            .map((v) => Math.round(v * 255));
        return {r, g, b, a: 1};
    }
    function hsbToString(hsb) {
        const rgb = hsbToRGB(hsb);
        return rgbToHexString(rgb);
    }
    function render(canvas, getPixel) {
        const {width, height} = canvas;
        const context = canvas.getContext("2d");
        const imageData = context.getImageData(0, 0, width, height);
        const d = imageData.data;
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                const i = 4 * (y * width + x);
                const c = getPixel(x, y);
                for (let j = 0; j < 4; j++) {
                    d[i + j] = c[j];
                }
            }
        }
        context.putImageData(imageData, 0, 0);
    }
    function renderHue(canvas) {
        const {height} = canvas;
        render(canvas, (_, y) => {
            const hue = scale(y, 0, height, 0, 360);
            const {r, g, b} = hsbToRGB({h: hue, s: 1, b: 1});
            return new Uint8ClampedArray([r, g, b, 255]);
        });
    }
    function renderSB(hue, canvas) {
        const {width, height} = canvas;
        render(canvas, (x, y) => {
            const sat = scale(x, 0, width - 1, 0, 1);
            const br = scale(y, 0, height - 1, 1, 0);
            const {r, g, b} = hsbToRGB({h: hue, s: sat, b: br});
            return new Uint8ClampedArray([r, g, b, 255]);
        });
    }
    function HSBPicker(props) {
        const context = getComponentContext();
        const store = context.getStore(hsbPickerDefaults);
        store.activeChangeHandler = props.onChange;
        const prevColor = context.prev && context.prev.props.color;
        const prevActiveColor = store.activeHSB
            ? hsbToString(store.activeHSB)
            : null;
        const didColorChange =
            props.color !== prevColor && props.color !== prevActiveColor;
        let activeHSB;
        if (didColorChange) {
            const rgb = parseColorWithCache(props.color);
            activeHSB = rgbToHSB(rgb);
            store.activeHSB = activeHSB;
        } else {
            activeHSB = store.activeHSB;
        }
        function onSBCanvasRender(canvas) {
            if (isElementHidden(canvas)) {
                return;
            }
            const hue = activeHSB.h;
            const prevHue =
                prevColor && rgbToHSB(parseColorWithCache(prevColor)).h;
            if (store.wasPrevHidden || hue !== prevHue) {
                renderSB(hue, canvas);
            }
            store.wasPrevHidden = false;
        }
        function onHueCanvasRender(canvas) {
            if (store.hueCanvasRendered || isElementHidden(canvas)) {
                return;
            }
            store.hueCanvasRendered = true;
            renderHue(canvas);
        }
        function createHSBSwipeHandler(getEventHSB) {
            return createSwipeHandler((startEvt, startNativeEvt) => {
                const rect =
                    startNativeEvt.currentTarget.getBoundingClientRect();
                function onPointerMove(e) {
                    store.activeHSB = getEventHSB({...e, rect});
                    props.onColorPreview(hsbToString(store.activeHSB));
                    context.refresh();
                }
                function onPointerUp(e) {
                    const hsb = getEventHSB({...e, rect});
                    store.activeHSB = hsb;
                    props.onChange(hsbToString(hsb));
                }
                store.activeHSB = getEventHSB({...startEvt, rect});
                context.refresh();
                return {
                    move: onPointerMove,
                    up: onPointerUp
                };
            });
        }
        const onSBPointerDown = createHSBSwipeHandler(
            ({clientX, clientY, rect}) => {
                const sat = clamp((clientX - rect.left) / rect.width, 0, 1);
                const br = clamp(1 - (clientY - rect.top) / rect.height, 0, 1);
                return {...activeHSB, s: sat, b: br};
            }
        );
        const onHuePointerDown = createHSBSwipeHandler(({clientY, rect}) => {
            const hue = clamp((clientY - rect.top) / rect.height, 0, 1) * 360;
            return {...activeHSB, h: hue};
        });
        const hueCursorStyle = {
            "background-color": hslToString({h: activeHSB.h, s: 1, l: 0.5}),
            "left": "0%",
            "top": `${(activeHSB.h / 360) * 100}%`
        };
        const sbCursorStyle = {
            "background-color": rgbToHexString(hsbToRGB(activeHSB)),
            "left": `${activeHSB.s * 100}%`,
            "top": `${(1 - activeHSB.b) * 100}%`
        };
        return m$1(
            "span",
            {class: "hsb-picker"},
            m$1(
                "span",
                {
                    class: "hsb-picker__sb-container",
                    onmousedown: onSBPointerDown,
                    onupdate: (el) => {
                        if (store.sbTouchStartHandler) {
                            el.removeEventListener(
                                "touchstart",
                                store.sbTouchStartHandler
                            );
                        }
                        el.addEventListener("touchstart", onSBPointerDown, {
                            passive: true
                        });
                        store.sbTouchStartHandler = onSBPointerDown;
                    }
                },
                m$1("canvas", {
                    class: "hsb-picker__sb-canvas",
                    onrender: onSBCanvasRender
                }),
                m$1("span", {
                    class: "hsb-picker__sb-cursor",
                    style: sbCursorStyle
                })
            ),
            m$1(
                "span",
                {
                    class: "hsb-picker__hue-container",
                    onmousedown: onHuePointerDown,
                    onupdate: (el) => {
                        if (store.hueTouchStartHandler) {
                            el.removeEventListener(
                                "touchstart",
                                store.hueTouchStartHandler
                            );
                        }
                        el.addEventListener("touchstart", onHuePointerDown, {
                            passive: true
                        });
                        store.hueTouchStartHandler = onHuePointerDown;
                    }
                },
                m$1("canvas", {
                    class: "hsb-picker__hue-canvas",
                    onrender: onHueCanvasRender
                }),
                m$1("span", {
                    class: "hsb-picker__hue-cursor",
                    style: hueCursorStyle
                })
            )
        );
    }

    function isValidColor(color) {
        return Boolean(parseColorWithCache(color));
    }
    const colorPickerFocuses = new WeakMap();
    function focusColorPicker(node) {
        const focus = colorPickerFocuses.get(node);
        focus();
    }
    function ColorPicker(props) {
        const context = getComponentContext();
        context.onRender((node) => colorPickerFocuses.set(node, focus));
        const store = context.store;
        const isColorValid = isValidColor(props.color);
        function onColorPreview(previewColor) {
            store.previewNode.style.backgroundColor = previewColor;
            store.textBoxNode.value = previewColor;
            store.textBoxNode.blur();
        }
        function onColorChange(rawValue) {
            const value = rawValue.trim();
            if (isValidColor(value)) {
                props.onChange(value);
            } else {
                props.onChange(props.color);
            }
        }
        function focus() {
            if (store.isFocused) {
                return;
            }
            store.isFocused = true;
            context.refresh();
            window.addEventListener("mousedown", onOuterClick, {passive: true});
        }
        function blur() {
            if (!store.isFocused) {
                return;
            }
            window.removeEventListener("mousedown", onOuterClick);
            store.isFocused = false;
            context.refresh();
        }
        function toggleFocus() {
            if (store.isFocused) {
                blur();
            } else {
                focus();
            }
        }
        function onOuterClick(e) {
            if (!e.composedPath().some((el) => el === context.node)) {
                blur();
            }
        }
        const textBox = m$1(TextBox, {
            class: "color-picker__input",
            onrender: (el) => {
                store.textBoxNode = el;
                store.textBoxNode.value = isColorValid ? props.color : "";
            },
            onkeypress: (e) => {
                const input = e.target;
                if (e.key === "Enter") {
                    const {value} = input;
                    onColorChange(value);
                    blur();
                    onColorPreview(value);
                }
            },
            onfocus: focus
        });
        const previewElement = m$1("span", {
            class: "color-picker__preview",
            onclick: toggleFocus,
            onrender: (el) => {
                store.previewNode = el;
                el.style.backgroundColor = isColorValid
                    ? props.color
                    : "transparent";
            }
        });
        const resetButton = props.canReset
            ? m$1("span", {
                  role: "button",
                  class: "color-picker__reset",
                  onclick: () => {
                      props.onReset();
                      blur();
                  }
              })
            : null;
        const textBoxLine = m$1(
            "span",
            {class: "color-picker__textbox-line"},
            textBox,
            previewElement,
            resetButton
        );
        const hsbLine = isColorValid
            ? m$1(
                  "span",
                  {class: "color-picker__hsb-line"},
                  m$1(HSBPicker, {
                      color: props.color,
                      onChange: onColorChange,
                      onColorPreview: onColorPreview
                  })
              )
            : null;
        return m$1(
            "span",
            {
                class: [
                    "color-picker",
                    store.isFocused && "color-picker--focused",
                    props.class
                ]
            },
            m$1("span", {class: "color-picker__wrapper"}, textBoxLine, hsbLine)
        );
    }
    Object.assign(ColorPicker, {focus: focusColorPicker});

    function DropDown(props) {
        const context = getComponentContext();
        const store = context.store;
        if (context.prev) {
            const currOptions = props.options.map((o) => o.id);
            const prevOptions = context.prev.props.options.map((o) => o.id);
            if (
                currOptions.length !== prevOptions.length ||
                currOptions.some((o, i) => o !== prevOptions[i])
            ) {
                store.isOpen = false;
            }
        }
        function saveListNode(el) {
            store.listNode = el;
        }
        function saveSelectedNode(el) {
            store.selectedNode = el;
        }
        function onSelectedClick() {
            store.isOpen = !store.isOpen;
            context.refresh();
            if (store.isOpen) {
                const onOuterClick = (e) => {
                    window.removeEventListener("mousedown", onOuterClick);
                    const listRect = store.listNode.getBoundingClientRect();
                    const ex = e.clientX;
                    const ey = e.clientY;
                    if (
                        ex < listRect.left ||
                        ex > listRect.right ||
                        ey < listRect.top ||
                        ey > listRect.bottom
                    ) {
                        store.isOpen = false;
                        context.refresh();
                    }
                };
                window.addEventListener("mousedown", onOuterClick, {
                    passive: true
                });
            }
        }
        function createListItem(value) {
            return m$1(
                "span",
                {
                    class: {
                        "dropdown__list__item": true,
                        "dropdown__list__item--selected":
                            value.id === props.selected,
                        [props.class]: Boolean(props.class)
                    },
                    onclick: () => {
                        store.isOpen = false;
                        context.refresh();
                        props.onChange(value.id);
                    }
                },
                value.content
            );
        }
        const selectedContent = props.options.find(
            (value) => value.id === props.selected
        ).content;
        return m$1(
            "span",
            {
                class: {
                    "dropdown": true,
                    "dropdown--open": store.isOpen,
                    [props.class]: Boolean(props.class)
                }
            },
            m$1(
                "span",
                {class: "dropdown__list", oncreate: saveListNode},
                props.options
                    .slice()
                    .sort((a, b) =>
                        a.id === props.selected
                            ? -1
                            : b.id === props.selected
                              ? 1
                              : 0
                    )
                    .map(createListItem)
            ),
            m$1(
                "span",
                {
                    class: "dropdown__selected",
                    oncreate: saveSelectedNode,
                    onclick: onSelectedClick
                },
                m$1(
                    "span",
                    {class: "dropdown__selected__text"},
                    selectedContent
                )
            )
        );
    }

    const DEFAULT_OVERLAY_KEY = Symbol();
    const overlayNodes = new Map();
    const clickListeners = new WeakMap();
    function getOverlayDOMNode(key) {
        if (key == null) {
            key = DEFAULT_OVERLAY_KEY;
        }
        if (!overlayNodes.has(key)) {
            const node = document.createElement("div");
            node.classList.add("overlay");
            node.addEventListener(
                "click",
                (e) => {
                    if (clickListeners.has(node) && e.currentTarget === node) {
                        const listener = clickListeners.get(node);
                        listener();
                    }
                },
                {passive: true}
            );
            overlayNodes.set(key, node);
        }
        return overlayNodes.get(key);
    }
    function Overlay(props) {
        return getOverlayDOMNode(props.key);
    }
    function Portal(props, ...content) {
        const context = getComponentContext();
        context.onRender(() => {
            const node = getOverlayDOMNode(props.key);
            if (props.onOuterClick) {
                clickListeners.set(node, props.onOuterClick);
            } else {
                clickListeners.delete(node);
            }
            render$1(node, content);
        });
        context.onRemove(() => {
            const container = getOverlayDOMNode(props.key);
            render$1(container, null);
        });
        return context.leave();
    }
    var Overlay$1 = Object.assign(Overlay, {Portal});

    function MessageBox(props) {
        return m$1(
            Overlay$1.Portal,
            {key: props.portalKey, onOuterClick: props.onCancel},
            m$1(
                "div",
                {class: "message-box"},
                m$1("label", {class: "message-box__caption"}, props.caption),
                m$1(
                    "div",
                    {class: "message-box__buttons"},
                    m$1(
                        Button,
                        {
                            class: "message-box__button message-box__button-ok",
                            onclick: props.onOK
                        },
                        "OK"
                    ),
                    props.hideCancel
                        ? null
                        : m$1(
                              Button,
                              {
                                  class: "message-box__button message-box__button-cancel",
                                  onclick: props.onCancel
                              },
                              "Cancel"
                          )
                )
            )
        );
    }

    function ResetButton$1(props, ...content) {
        return m$1(
            Button,
            {class: ["nav-button", props.class], onclick: props.onClick},
            m$1("span", {class: "nav-button__content"}, ...content)
        );
    }

    function ResetButton(props, ...content) {
        return m$1(
            Button,
            {class: "reset-button", onclick: props.onClick},
            m$1(
                "span",
                {class: "reset-button__content"},
                m$1("span", {class: "reset-button__icon"}),
                ...content
            )
        );
    }

    function VirtualScroll(props) {
        if (props.items.length === 0) {
            return props.root;
        }
        const {store} = getComponentContext();
        function renderContent(root, scrollToIndex) {
            if (root.clientWidth === 0) {
                return;
            }
            if (store.itemHeight == null) {
                const tempItem = {
                    ...props.items[0],
                    props: {
                        ...props.items[0].props,
                        oncreate: null,
                        onupdate: null,
                        onrender: null
                    }
                };
                const tempNode = render$1(root, tempItem).firstElementChild;
                store.itemHeight = tempNode.getBoundingClientRect().height;
            }
            const {itemHeight} = store;
            const wrapper = render$1(
                root,
                m$1("div", {
                    style: {
                        flex: "none",
                        height: `${props.items.length * itemHeight}px`,
                        overflow: "hidden",
                        position: "relative"
                    }
                })
            ).firstElementChild;
            if (scrollToIndex >= 0) {
                root.scrollTop = scrollToIndex * itemHeight;
            }
            const containerHeight =
                document.documentElement.clientHeight -
                root.getBoundingClientRect().top;
            let focusedIndex = -1;
            if (document.activeElement) {
                let current = document.activeElement;
                while (current && current.parentElement !== wrapper) {
                    current = current.parentElement;
                }
                if (current) {
                    focusedIndex = store.nodesIndices.get(current);
                }
            }
            store.nodesIndices = store.nodesIndices || new WeakMap();
            const saveNodeIndex = (node, index) =>
                store.nodesIndices.set(node, index);
            const items = props.items
                .map((item, index) => {
                    return {item, index};
                })
                .filter(({index}) => {
                    const eTop = index * itemHeight;
                    const eBottom = (index + 1) * itemHeight;
                    const rTop = root.scrollTop;
                    const rBottom = root.scrollTop + containerHeight;
                    const isTopBoundVisible = eTop >= rTop && eTop <= rBottom;
                    const isBottomBoundVisible =
                        eBottom >= rTop && eBottom <= rBottom;
                    return (
                        isTopBoundVisible ||
                        isBottomBoundVisible ||
                        focusedIndex === index
                    );
                })
                .map(({item, index}) =>
                    m$1(
                        "div",
                        {
                            key: index,
                            onrender: (node) => saveNodeIndex(node, index),
                            style: {
                                left: "0",
                                position: "absolute",
                                top: `${index * itemHeight}px`,
                                width: "100%"
                            }
                        },
                        item
                    )
                );
            render$1(wrapper, items);
        }
        let rootNode;
        let prevScrollTop;
        const rootDidMount = props.root.props.oncreate;
        const rootDidUpdate = props.root.props.onupdate;
        const rootDidRender = props.root.props.onrender;
        return {
            ...props.root,
            props: {
                ...props.root.props,
                oncreate: rootDidMount,
                onupdate: rootDidUpdate,
                onrender: (node) => {
                    rootNode = node;
                    rootDidRender && rootDidRender(rootNode);
                    renderContent(
                        rootNode,
                        isNaN(props.scrollToIndex) ? -1 : props.scrollToIndex
                    );
                },
                onscroll: () => {
                    if (rootNode.scrollTop === prevScrollTop) {
                        return;
                    }
                    prevScrollTop = rootNode.scrollTop;
                    renderContent(rootNode, -1);
                }
            },
            children: []
        };
    }

    function ShortcutLink(props) {
        const shortcut = props.shortcuts[props.commandName];
        const shortcutMessage = props.textTemplate(shortcut);
        const cls = mergeClass("shortcut", [
            shortcut ? "shortcut--set" : null,
            props.class
        ]);
        function onClick(e) {
            e.preventDefault();
            if (isEdge) {
                chrome.tabs.create({
                    url: `edge://extensions/shortcuts`,
                    active: true
                });
                return;
            }
            chrome.tabs.create({
                url: `chrome://extensions/configureCommands#command-${chrome.runtime.id}-${props.commandName}`,
                active: true
            });
        }
        function onRender(node) {
            node.textContent = shortcutMessage;
        }
        return m$1("a", {
            class: cls,
            href: "#",
            onclick: onClick,
            oncreate: onRender
        });
    }

    function parseTime($time) {
        const parts = $time.split(":").slice(0, 2);
        const lowercased = $time.trim().toLowerCase();
        const isAM = lowercased.endsWith("am") || lowercased.endsWith("a.m.");
        const isPM = lowercased.endsWith("pm") || lowercased.endsWith("p.m.");
        let hours = parts.length > 0 ? parseInt(parts[0]) : 0;
        if (isNaN(hours) || hours > 23) {
            hours = 0;
        }
        if (isAM && hours === 12) {
            hours = 0;
        }
        if (isPM && hours < 12) {
            hours += 12;
        }
        let minutes = parts.length > 1 ? parseInt(parts[1]) : 0;
        if (isNaN(minutes) || minutes > 59) {
            minutes = 0;
        }
        return [hours, minutes];
    }

    function toLong24HTime($time) {
        const [hours, minutes] = parseTime($time);
        const hh = `${hours < 10 ? "0" : ""}${hours}`;
        const mm = `${minutes < 10 ? "0" : ""}${minutes}`;
        return `${hh}:${mm}`;
    }
    function to24HTime($time) {
        const [hours, minutes] = parseTime($time);
        const mm = `${minutes < 10 ? "0" : ""}${minutes}`;
        return `${hours}:${mm}`;
    }
    function TimeRangePicker(props) {
        function onStartTimeChange($startTime) {
            props.onChange([to24HTime($startTime), props.endTime]);
        }
        function onEndTimeChange($endTime) {
            props.onChange([props.startTime, to24HTime($endTime)]);
        }
        function setStartTime(node) {
            node.value = toLong24HTime(props.startTime);
        }
        function setEndTime(node) {
            node.value = toLong24HTime(props.endTime);
        }
        return m$1(
            "span",
            {class: "time-range-picker"},
            m$1(TextBox, {
                class: "time-range-picker__input time-range-picker__input--start",
                type: "time",
                placeholder: "18:00",
                onrender: setStartTime,
                onchange: (e) => onStartTimeChange(e.target.value),
                onkeypress: (e) => {
                    if (e.key === "Enter") {
                        const input = e.target;
                        input.blur();
                        onStartTimeChange(input.value);
                    }
                }
            }),
            m$1(TextBox, {
                class: "time-range-picker__input time-range-picker__input--end",
                type: "time",
                placeholder: "09:00",
                onrender: setEndTime,
                onchange: (e) => onEndTimeChange(e.target.value),
                onkeypress: (e) => {
                    if (e.key === "Enter") {
                        const input = e.target;
                        input.blur();
                        onEndTimeChange(input.value);
                    }
                }
            })
        );
    }

    function getLocalMessage(messageName) {
        return chrome.i18n.getMessage(messageName) || messageName;
    }
    function getUILanguage() {
        let code;
        if (
            "i18n" in chrome &&
            "getUILanguage" in chrome.i18n &&
            typeof chrome.i18n.getUILanguage === "function"
        ) {
            code = chrome.i18n.getUILanguage();
        } else {
            code = navigator.language.split("-")[0];
        }
        if (code.endsWith("-mac")) {
            return code.substring(0, code.length - 4);
        }
        return code;
    }

    function AdvancedIcon() {
        return m$1(
            "svg",
            {viewBox: "0 0 16 16"},
            m$1(
                "defs",
                null,
                m$1("path", {id: "cog", d: "M-1.25,-6.5 h2.5 l1,3 h-4.5 z"}),
                m$1(
                    "g",
                    {id: "cogwheel"},
                    m$1("path", {
                        d: "M0,-5 a5,5 0 0 1 0,10 a5,5 0 0 1 0,-10 z M0,-3 a3,3 0 0 0 0,6 a3,3 0 0 0 0,-6 z"
                    }),
                    m$1("use", {href: "#cog"}),
                    m$1("use", {href: "#cog", transform: "rotate(60)"}),
                    m$1("use", {href: "#cog", transform: "rotate(120)"}),
                    m$1("use", {href: "#cog", transform: "rotate(180)"}),
                    m$1("use", {href: "#cog", transform: "rotate(240)"}),
                    m$1("use", {href: "#cog", transform: "rotate(300)"})
                )
            ),
            m$1(
                "g",
                {fill: "currentColor"},
                m$1("use", {
                    href: "#cogwheel",
                    transform: "translate(8 4) scale(0.5)"
                }),
                m$1("use", {
                    href: "#cogwheel",
                    transform: "translate(4 11) scale(0.5)"
                }),
                m$1("use", {
                    href: "#cogwheel",
                    transform: "translate(12 11) scale(0.5)"
                })
            )
        );
    }

    function DeleteIcon() {
        return m$1(
            "svg",
            {viewBox: "0 0 16 16"},
            m$1("path", {
                fill: "currentColor",
                d: "M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"
            }),
            m$1("path", {
                "fill": "currentColor",
                "fill-rule": "evenodd",
                "d": "M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"
            })
        );
    }

    function HelpIcon() {
        return m$1(
            "svg",
            {viewBox: "0 0 16 16"},
            m$1("circle", {
                "fill": "none",
                "stroke": "currentColor",
                "stroke-width": "1",
                "cx": "8",
                "cy": "8",
                "r": "7"
            }),
            m$1(
                "text",
                {
                    "fill": "currentColor",
                    "x": "8",
                    "y": "12",
                    "text-anchor": "middle",
                    "font-size": "12",
                    "font-weight": "bold"
                },
                "?"
            )
        );
    }

    function KeyIcon(props) {
        var _a;
        return m$1(
            "svg",
            {viewBox: "-8 -8 16 16", class: props.class},
            m$1(
                "g",
                {
                    "stroke":
                        (_a = props.color) !== null && _a !== void 0
                            ? _a
                            : "currentColor",
                    "stroke-width": "2"
                },
                m$1("circle", {r: "3", cx: "-4", cy: "0"}),
                m$1("path", {d: "M-1,0 h6 v3"}),
                m$1("path", {d: "M4,0 v2.5"})
            )
        );
    }

    function KeyboardIcon() {
        return m$1(
            "svg",
            {viewBox: "0 0 16 16"},
            m$1("rect", {
                "fill": "none",
                "stroke": "var(--icon-color, currentColor)",
                "stroke-width": "1",
                "x": "2",
                "y": "4",
                "width": "12",
                "height": "8"
            }),
            m$1(
                "g",
                {
                    "stroke": "var(--icon-color, currentColor)",
                    "stroke-width": "1"
                },
                m$1("line", {x1: "4", y1: "10", x2: "12", y2: "10"}),
                m$1("line", {x1: "4", y1: "6", x2: "6", y2: "6"}),
                m$1("line", {x1: "7", y1: "6", x2: "9", y2: "6"}),
                m$1("line", {x1: "10", y1: "6", x2: "12", y2: "6"}),
                m$1("line", {x1: "5.5", y1: "8", x2: "7.5", y2: "8"}),
                m$1("line", {x1: "8.5", y1: "8", x2: "10.5", y2: "8"})
            )
        );
    }

    function ListIcon() {
        return m$1(
            "svg",
            {viewBox: "-1 -1 10 10"},
            m$1("path", {
                d: "M0,0 h1 v1 h-1 z m2,0 h6 v1 h-6 z m-2,3.25 h1 v1 h-1 z m2,0 h6 v1 h-6 z m-2,3.25 h1 v1 h-1 z m2,0 h6 v1 h-6 z",
                fill: "currentColor"
            })
        );
    }

    function SettingsIcon(props) {
        var _a;
        return m$1(
            "svg",
            {viewBox: "0 0 16 16", class: props.class},
            m$1(
                "defs",
                null,
                m$1("path", {id: "cog", d: "M-1.25,-6.5 h2.5 l1,3 h-4.5 z"})
            ),
            m$1(
                "g",
                {
                    transform: "translate(8 8)",
                    fill:
                        (_a = props.color) !== null && _a !== void 0
                            ? _a
                            : "currentColor"
                },
                m$1("path", {
                    d: "M0,-5 a5,5 0 0 1 0,10 a5,5 0 0 1 0,-10 z M0,-3 a3,3 0 0 0 0,6 a3,3 0 0 0 0,-6 z"
                }),
                m$1("use", {href: "#cog"}),
                m$1("use", {href: "#cog", transform: "rotate(60)"}),
                m$1("use", {href: "#cog", transform: "rotate(120)"}),
                m$1("use", {href: "#cog", transform: "rotate(180)"}),
                m$1("use", {href: "#cog", transform: "rotate(240)"}),
                m$1("use", {href: "#cog", transform: "rotate(300)"})
            )
        );
    }

    function WatchIcon(props) {
        const {hours, minutes, color = "white"} = props;
        const cx = 8;
        const cy = 8.5;
        const lenHour = 3;
        const lenMinute = 4;
        const clockR = 5.5;
        const btnSize = 2;
        const btnPad = 1.5;
        const ah =
            (((hours > 11 ? hours - 12 : hours) + minutes / 60) / 12) *
            Math.PI *
            2;
        const am = (minutes / 60) * Math.PI * 2;
        const hx = cx + lenHour * Math.sin(ah);
        const hy = cy - lenHour * Math.cos(ah);
        const mx = cx + lenMinute * Math.sin(am);
        const my = cy - lenMinute * Math.cos(am);
        return m$1(
            "svg",
            {viewBox: "0 0 16 16"},
            m$1("circle", {
                "fill": "none",
                "stroke": color,
                "stroke-width": "1.5",
                "cx": cx,
                "cy": cy,
                "r": clockR
            }),
            m$1("line", {
                "stroke": color,
                "stroke-width": "1.5",
                "x1": cx,
                "y1": cy,
                "x2": hx,
                "y2": hy
            }),
            m$1("line", {
                "stroke": color,
                "stroke-width": "1.5",
                "opacity": "0.67",
                "x1": cx,
                "y1": cy,
                "x2": mx,
                "y2": my
            }),
            [30, -30].map((angle) => {
                return m$1("path", {
                    "fill": color,
                    "transform": `rotate(${angle})`,
                    "transform-origin": `${cx} ${cy}`,
                    "d": `M${cx - btnSize},${cy - clockR - btnPad} a${btnSize},${btnSize} 0 0 1 ${2 * btnSize},0 z`
                });
            })
        );
    }

    const HOMEPAGE_URL = "https://darkreader.org";
    const DONATE_URL = "https://darkreader.org/support-us/";
    const MOBILE_URL = "https://darkreader.org/tips/mobile/";
    const PRIVACY_URL = "https://darkreader.org/privacy/";
    const HELP_URL = "https://darkreader.org/help";
    const helpLocales = [
        "be",
        "cs",
        "de",
        "en",
        "es",
        "fr",
        "it",
        "ja",
        "nl",
        "pt",
        "ru",
        "sr",
        "tr",
        "zh-CN",
        "zh-TW"
    ];
    function getHelpURL() {
        if (isEdge && isMobile) {
            return `${HELP_URL}/mobile/`;
        }
        const locale = getUILanguage();
        const matchLocale =
            helpLocales.find((hl) => hl === locale) ||
            helpLocales.find((hl) => locale.startsWith(hl)) ||
            "en";
        return `${HELP_URL}/${matchLocale}/`;
    }

    let appVersion;
    function AppVersion() {
        if (!appVersion) {
            appVersion = chrome.runtime.getManifest().version;
        }
        return m$1(
            "label",
            {class: "darkreader-version"},
            getLocalMessage("version"),
            " ",
            appVersion
        );
    }

    function AboutTab(props) {
        return m$1(
            "div",
            {class: "settings-tab about-tab"},
            m$1(AppVersion, null),
            m$1(
                "div",
                null,
                m$1(
                    "a",
                    {
                        href: PRIVACY_URL,
                        target: "_blank",
                        rel: "noopener noreferrer"
                    },
                    "Privacy Policy"
                )
            ),
            m$1(
                "div",
                null,
                m$1(
                    "a",
                    {
                        href: `${HOMEPAGE_URL}/terms/`,
                        target: "_blank",
                        rel: "noopener noreferrer"
                    },
                    "Terms of Use"
                )
            ),
            isMobile
                ? null
                : m$1(
                      "div",
                      null,
                      m$1(
                          "a",
                          {
                              href: MOBILE_URL,
                              target: "_blank",
                              rel: "noopener noreferrer"
                          },
                          getLocalMessage("mobile")
                      )
                  ),
            m$1(
                "div",
                null,
                m$1(
                    "a",
                    {
                        href: props.plus ? `${HELP_URL}/plus/` : getHelpURL(),
                        target: "_blank",
                        rel: "noopener noreferrer"
                    },
                    getLocalMessage("help")
                )
            ),
            props.plus
                ? null
                : isMobile
                  ? m$1(
                        "div",
                        null,
                        m$1(
                            "a",
                            {
                                href: `${HOMEPAGE_URL}/plus/`,
                                target: "_blank",
                                rel: "noopener noreferrer"
                            },
                            getLocalMessage("pay_for_using")
                        )
                    )
                  : props.data.uiHighlights.includes("anniversary")
                    ? m$1(
                          "div",
                          null,
                          m$1(
                              "a",
                              {
                                  href: DONATE_URL,
                                  target: "_blank",
                                  rel: "noopener noreferrer"
                              },
                              getLocalMessage("pay_for_using")
                          )
                      )
                    : null
        );
    }

    function ActivationTab(props) {
        const context = getComponentContext();
        const store = context.getStore({
            emailTextElement: null,
            keyTextElement: null,
            errorMessage: "",
            checking: false
        });
        if (!props.data.uiHighlights.includes("anniversary")) {
            return m$1(
                "div",
                {
                    class: {
                        "settings-tab": true,
                        "activation-tab": true
                    }
                },
                m$1(
                    "div",
                    {class: "activation__success-message"},
                    "Activation was successful"
                ),
                m$1(
                    ControlGroup$1,
                    null,
                    m$1(
                        ControlGroup$1.Control,
                        {class: "activation__reset-control"},
                        m$1(
                            Button,
                            {
                                class: "activation__reset-control__button",
                                onclick: () => {
                                    store.checking = true;
                                    store.errorMessage = "";
                                    context.refresh();
                                    props.actions.resetActivation();
                                    store.checking = false;
                                }
                            },
                            "Reset"
                        )
                    )
                ),
                m$1(
                    "div",
                    {class: "activation__thumb-up"},
                    m$1("img", {
                        src: "../assets/images/darkreader-thumb-up.svg"
                    })
                )
            );
        }
        const activate = () => {
            var _a, _b, _c, _d;
            if (store.checking) {
                return;
            }
            const email =
                (_b =
                    (_a = store.emailTextElement) === null || _a === void 0
                        ? void 0
                        : _a.value.trim()) !== null && _b !== void 0
                    ? _b
                    : "";
            const key =
                (_d =
                    (_c = store.keyTextElement) === null || _c === void 0
                        ? void 0
                        : _c.value.trim()) !== null && _d !== void 0
                    ? _d
                    : "";
            store.errorMessage = "";
            store.checking = true;
            context.refresh();
            props.actions.startActivation(email, key);
            store.errorMessage = "Please check your email and key";
            store.checking = false;
        };
        return m$1(
            "div",
            {
                class: {
                    "settings-tab": true,
                    "activation-tab": true,
                    "activation-tab--checking": store.checking
                }
            },
            m$1(
                ControlGroup$1,
                null,
                m$1(
                    ControlGroup$1.Control,
                    {class: "activation__get-code-control"},
                    m$1(
                        "a",
                        {
                            href: DONATE_URL,
                            target: "_blank",
                            rel: "noopener noreferrer"
                        },
                        "Get activation code"
                    )
                )
            ),
            m$1(
                ControlGroup$1,
                null,
                m$1(
                    ControlGroup$1.Control,
                    {class: "activation__email-control"},
                    m$1(TextBox, {
                        class: "activation__email-control__text",
                        placeholder: "example@gmail.com",
                        onchange: (e) => e.target.value,
                        oncreate: (node) => {
                            store.emailTextElement = node;
                        },
                        onkeypress: (e) => {
                            var _a;
                            if (e.key === "Enter") {
                                (_a = store.keyTextElement) === null ||
                                _a === void 0
                                    ? void 0
                                    : _a.focus();
                            }
                        }
                    })
                ),
                m$1(ControlGroup$1.Description, null, "Email")
            ),
            m$1(
                ControlGroup$1,
                null,
                m$1(
                    ControlGroup$1.Control,
                    {class: "activation__key-control"},
                    m$1(TextBox, {
                        class: "activation__key-control__text",
                        placeholder: "XXXX-XXXX-XXXX-XXXX",
                        onchange: (e) => e.target.value,
                        oncreate: (node) => {
                            store.keyTextElement = node;
                        },
                        onkeypress: (e) => {
                            var _a;
                            if (e.key === "Enter") {
                                (_a = store.keyTextElement) === null ||
                                _a === void 0
                                    ? void 0
                                    : _a.blur();
                                activate();
                            }
                        }
                    })
                ),
                m$1(ControlGroup$1.Description, null, "Code")
            ),
            m$1(
                ControlGroup$1,
                null,
                m$1(
                    ControlGroup$1.Control,
                    {class: "activation__activate-control"},
                    m$1(
                        Button,
                        {
                            class: "activation__activate-control__button",
                            onclick: activate
                        },
                        "Activate"
                    )
                ),
                m$1(ControlGroup$1.Description, null, "Activate the code")
            ),
            m$1(
                ControlGroup$1,
                null,
                m$1(
                    ControlGroup$1.Control,
                    null,
                    m$1("div", {class: "activation__error"}, store.errorMessage)
                )
            )
        );
    }

    function ContextMenus(props) {
        function onContextMenusChange(checked) {
            if (checked) {
                chrome.permissions.request(
                    {permissions: ["contextMenus"]},
                    (hasPermission) => {
                        if (hasPermission) {
                            props.actions.changeSettings({
                                enableContextMenus: true
                            });
                        } else {
                            console.warn(
                                "User declined contextMenus permission prompt."
                            );
                        }
                    }
                );
            } else {
                props.actions.changeSettings({enableContextMenus: false});
            }
        }
        return isMobile
            ? null
            : m$1(CheckButton, {
                  checked: props.data.settings.enableContextMenus,
                  label: "Use context menus",
                  description: props.data.settings.enableContextMenus
                      ? "Context menu integration is enabled"
                      : "Context menu integration is disabled",
                  onChange: onContextMenusChange
              });
    }

    async function openDevTools() {
        await openExtensionPage("devtools");
    }
    function DevTools() {
        return m$1(
            ControlGroup$1,
            null,
            m$1(
                ControlGroup$1.Control,
                null,
                m$1(
                    ResetButton$1,
                    {
                        onClick: openDevTools,
                        class: "advanced__dev-tools-button"
                    },
                    "\uD83D\uDEE0 ",
                    getLocalMessage("open_dev_tools")
                )
            ),
            m$1(ControlGroup$1.Description, null, "Make a fix for a website")
        );
    }

    function EnableForProtectedPages(props) {
        function onEnableForProtectedPages(value) {
            props.actions.changeSettings({enableForProtectedPages: value});
        }
        return m$1(CheckButton, {
            checked: props.data.settings.enableForProtectedPages,
            onChange: onEnableForProtectedPages,
            label: "Enable on restricted pages",
            description: props.data.settings.enableForProtectedPages
                ? "You should enable it in browser flags too"
                : "Disabled for web store and other pages"
        });
    }

    function ExportSettings(props) {
        function exportSettings() {
            saveFile(
                "Dark-Reader-Settings.json",
                JSON.stringify(props.data.settings, null, 4)
            );
        }
        return m$1(
            ControlGroup$1,
            null,
            m$1(
                ControlGroup$1.Control,
                null,
                m$1(
                    Button,
                    {
                        onclick: exportSettings,
                        class: "advanced__export-settings-button"
                    },
                    "Export Settings"
                )
            ),
            m$1(
                ControlGroup$1.Description,
                null,
                "Save settings to a JSON file"
            )
        );
    }

    var ThemeEngine;
    (function (ThemeEngine) {
        ThemeEngine["cssFilter"] = "cssFilter";
        ThemeEngine["svgFilter"] = "svgFilter";
        ThemeEngine["staticTheme"] = "staticTheme";
        ThemeEngine["dynamicTheme"] = "dynamicTheme";
    })(ThemeEngine || (ThemeEngine = {}));

    var AutomationMode;
    (function (AutomationMode) {
        AutomationMode["NONE"] = "";
        AutomationMode["TIME"] = "time";
        AutomationMode["SYSTEM"] = "system";
        AutomationMode["LOCATION"] = "location";
    })(AutomationMode || (AutomationMode = {}));

    const DEFAULT_COLORS = {
        darkScheme: {
            background: "#181a1b",
            text: "#e8e6e3"
        },
        lightScheme: {
            background: "#dcdad7",
            text: "#181a1b"
        }
    };
    const DEFAULT_THEME = {
        mode: 1,
        brightness: 100,
        contrast: 100,
        grayscale: 0,
        sepia: 0,
        useFont: false,
        fontFamily: isMacOS
            ? "Helvetica Neue"
            : isWindows
              ? "Segoe UI"
              : "Open Sans",
        textStroke: 0,
        engine: ThemeEngine.dynamicTheme,
        stylesheet: "",
        darkSchemeBackgroundColor: DEFAULT_COLORS.darkScheme.background,
        darkSchemeTextColor: DEFAULT_COLORS.darkScheme.text,
        lightSchemeBackgroundColor: DEFAULT_COLORS.lightScheme.background,
        lightSchemeTextColor: DEFAULT_COLORS.lightScheme.text,
        scrollbarColor: "",
        selectionColor: "auto",
        styleSystemControls: !isCSSColorSchemePropSupported,
        lightColorScheme: "Default",
        darkColorScheme: "Default",
        immediateModify: false
    };
    const filterModeSites = [
        "*.officeapps.live.com",
        "*.sharepoint.com",
        "docs.google.com",
        "onedrive.live.com"
    ];
    const DEFAULT_SETTINGS = {
        schemeVersion: 0,
        enabled: true,
        fetchNews: true,
        theme: DEFAULT_THEME,
        presets: [],
        customThemes: filterModeSites.map((url) => {
            const engine = ThemeEngine.cssFilter;
            return {
                url: [url],
                theme: {...DEFAULT_THEME, engine},
                builtIn: true
            };
        }),
        enabledByDefault: true,
        enabledFor: [],
        disabledFor: [],
        changeBrowserTheme: false,
        syncSettings: true,
        syncSitesFixes: false,
        automation: {
            enabled: isEdge && isMobile ? true : false,
            mode:
                isEdge && isMobile
                    ? AutomationMode.SYSTEM
                    : AutomationMode.NONE,
            behavior: "OnOff"
        },
        time: {
            activation: "18:00",
            deactivation: "9:00"
        },
        location: {
            latitude: null,
            longitude: null
        },
        previewNewDesign: false,
        previewNewestDesign: false,
        enableForPDF: true,
        enableForProtectedPages: false,
        enableContextMenus: false,
        detectDarkTheme: true
    };

    function isBoolean(x) {
        return typeof x === "boolean";
    }
    function isPlainObject(x) {
        return typeof x === "object" && x != null && !Array.isArray(x);
    }
    function isArray(x) {
        return Array.isArray(x);
    }
    function isString(x) {
        return typeof x === "string";
    }
    function isNonEmptyString(x) {
        return x && isString(x);
    }
    function isNonEmptyArrayOfNonEmptyStrings(x) {
        return (
            Array.isArray(x) &&
            x.length > 0 &&
            x.every((s) => isNonEmptyString(s))
        );
    }
    function isRegExpMatch(regexp) {
        return (x) => {
            return isString(x) && x.match(regexp) != null;
        };
    }
    const isTime = isRegExpMatch(
        /^((0?[0-9])|(1[0-9])|(2[0-3])):([0-5][0-9])$/
    );
    function isNumber(x) {
        return typeof x === "number" && !isNaN(x);
    }
    function isNumberBetween(min, max) {
        return (x) => {
            return isNumber(x) && x >= min && x <= max;
        };
    }
    function isOneOf(...values) {
        return (x) => values.includes(x);
    }
    function hasRequiredProperties(obj, keys) {
        return keys.every((key) => obj.hasOwnProperty(key));
    }
    function createValidator() {
        const errors = [];
        function validateProperty(obj, key, validator, fallback) {
            if (!obj.hasOwnProperty(key) || validator(obj[key])) {
                return;
            }
            errors.push(
                `Unexpected value for "${key}": ${JSON.stringify(obj[key])}`
            );
            obj[key] = fallback[key];
        }
        function validateArray(obj, key, validator) {
            if (!obj.hasOwnProperty(key)) {
                return;
            }
            const wrongValues = new Set();
            const arr = obj[key];
            for (let i = 0; i < arr.length; i++) {
                if (!validator(arr[i])) {
                    wrongValues.add(arr[i]);
                    arr.splice(i, 1);
                    i--;
                }
            }
            if (wrongValues.size > 0) {
                errors.push(
                    `Array "${key}" has wrong values: ${Array.from(wrongValues)
                        .map((v) => JSON.stringify(v))
                        .join("; ")}`
                );
            }
        }
        return {validateProperty, validateArray, errors};
    }
    function validateSettings(settings) {
        if (!isPlainObject(settings)) {
            return {
                errors: ["Settings are not a plain object"],
                settings: DEFAULT_SETTINGS
            };
        }
        const {validateProperty, validateArray, errors} = createValidator();
        const isValidPresetTheme = (theme) => {
            if (!isPlainObject(theme)) {
                return false;
            }
            const {errors: themeErrors} = validateTheme(theme);
            return themeErrors.length === 0;
        };
        validateProperty(settings, "schemeVersion", isNumber, DEFAULT_SETTINGS);
        validateProperty(settings, "enabled", isBoolean, DEFAULT_SETTINGS);
        validateProperty(settings, "fetchNews", isBoolean, DEFAULT_SETTINGS);
        validateProperty(settings, "theme", isPlainObject, DEFAULT_SETTINGS);
        const {errors: themeErrors} = validateTheme(settings.theme);
        errors.push(...themeErrors);
        validateProperty(settings, "presets", isArray, DEFAULT_SETTINGS);
        validateArray(settings, "presets", (preset) => {
            const presetValidator = createValidator();
            if (
                !(
                    isPlainObject(preset) &&
                    hasRequiredProperties(preset, [
                        "id",
                        "name",
                        "urls",
                        "theme"
                    ])
                )
            ) {
                return false;
            }
            presetValidator.validateProperty(
                preset,
                "id",
                isNonEmptyString,
                preset
            );
            presetValidator.validateProperty(
                preset,
                "name",
                isNonEmptyString,
                preset
            );
            presetValidator.validateProperty(
                preset,
                "urls",
                isNonEmptyArrayOfNonEmptyStrings,
                preset
            );
            presetValidator.validateProperty(
                preset,
                "theme",
                isValidPresetTheme,
                preset
            );
            return presetValidator.errors.length === 0;
        });
        validateProperty(settings, "customThemes", isArray, DEFAULT_SETTINGS);
        validateArray(settings, "customThemes", (custom) => {
            if (
                !(
                    isPlainObject(custom) &&
                    hasRequiredProperties(custom, ["url", "theme"])
                )
            ) {
                return false;
            }
            const presetValidator = createValidator();
            presetValidator.validateProperty(
                custom,
                "url",
                isNonEmptyArrayOfNonEmptyStrings,
                custom
            );
            presetValidator.validateProperty(
                custom,
                "theme",
                isValidPresetTheme,
                custom
            );
            return presetValidator.errors.length === 0;
        });
        validateProperty(settings, "enabledFor", isArray, DEFAULT_SETTINGS);
        validateArray(settings, "enabledFor", isNonEmptyString);
        validateProperty(settings, "disabledFor", isArray, DEFAULT_SETTINGS);
        validateArray(settings, "disabledFor", isNonEmptyString);
        validateProperty(
            settings,
            "enabledByDefault",
            isBoolean,
            DEFAULT_SETTINGS
        );
        validateProperty(
            settings,
            "changeBrowserTheme",
            isBoolean,
            DEFAULT_SETTINGS
        );
        validateProperty(settings, "syncSettings", isBoolean, DEFAULT_SETTINGS);
        validateProperty(
            settings,
            "syncSitesFixes",
            isBoolean,
            DEFAULT_SETTINGS
        );
        validateProperty(
            settings,
            "automation",
            (automation) => {
                if (!isPlainObject(automation)) {
                    return false;
                }
                const automationValidator = createValidator();
                automationValidator.validateProperty(
                    automation,
                    "enabled",
                    isBoolean,
                    automation
                );
                automationValidator.validateProperty(
                    automation,
                    "mode",
                    isOneOf(
                        AutomationMode.SYSTEM,
                        AutomationMode.TIME,
                        AutomationMode.LOCATION,
                        AutomationMode.NONE
                    ),
                    automation
                );
                automationValidator.validateProperty(
                    automation,
                    "behavior",
                    isOneOf("OnOff", "Scheme"),
                    automation
                );
                return automationValidator.errors.length === 0;
            },
            DEFAULT_SETTINGS
        );
        validateProperty(
            settings,
            AutomationMode.TIME,
            (time) => {
                if (!isPlainObject(time)) {
                    return false;
                }
                const timeValidator = createValidator();
                timeValidator.validateProperty(
                    time,
                    "activation",
                    isTime,
                    time
                );
                timeValidator.validateProperty(
                    time,
                    "deactivation",
                    isTime,
                    time
                );
                return timeValidator.errors.length === 0;
            },
            DEFAULT_SETTINGS
        );
        validateProperty(
            settings,
            AutomationMode.LOCATION,
            (location) => {
                if (!isPlainObject(location)) {
                    return false;
                }
                const locValidator = createValidator();
                const isValidLoc = (x) => x === null || isNumber(x);
                locValidator.validateProperty(
                    location,
                    "latitude",
                    isValidLoc,
                    location
                );
                locValidator.validateProperty(
                    location,
                    "longitude",
                    isValidLoc,
                    location
                );
                return locValidator.errors.length === 0;
            },
            DEFAULT_SETTINGS
        );
        validateProperty(
            settings,
            "previewNewDesign",
            isBoolean,
            DEFAULT_SETTINGS
        );
        validateProperty(
            settings,
            "previewNewestDesign",
            isBoolean,
            DEFAULT_SETTINGS
        );
        validateProperty(settings, "enableForPDF", isBoolean, DEFAULT_SETTINGS);
        validateProperty(
            settings,
            "enableForProtectedPages",
            isBoolean,
            DEFAULT_SETTINGS
        );
        validateProperty(
            settings,
            "enableContextMenus",
            isBoolean,
            DEFAULT_SETTINGS
        );
        validateProperty(
            settings,
            "detectDarkTheme",
            isBoolean,
            DEFAULT_SETTINGS
        );
        return {errors, settings};
    }
    function validateTheme(theme) {
        if (!isPlainObject(theme)) {
            return {
                errors: ["Theme is not a plain object"],
                theme: DEFAULT_THEME
            };
        }
        const {validateProperty, errors} = createValidator();
        validateProperty(theme, "mode", isOneOf(0, 1), DEFAULT_THEME);
        validateProperty(
            theme,
            "brightness",
            isNumberBetween(0, 200),
            DEFAULT_THEME
        );
        validateProperty(
            theme,
            "contrast",
            isNumberBetween(0, 200),
            DEFAULT_THEME
        );
        validateProperty(
            theme,
            "grayscale",
            isNumberBetween(0, 100),
            DEFAULT_THEME
        );
        validateProperty(
            theme,
            "sepia",
            isNumberBetween(0, 100),
            DEFAULT_THEME
        );
        validateProperty(theme, "useFont", isBoolean, DEFAULT_THEME);
        validateProperty(theme, "fontFamily", isNonEmptyString, DEFAULT_THEME);
        validateProperty(
            theme,
            "textStroke",
            isNumberBetween(0, 1),
            DEFAULT_THEME
        );
        validateProperty(
            theme,
            "engine",
            isOneOf("dynamicTheme", "staticTheme", "cssFilter", "svgFilter"),
            DEFAULT_THEME
        );
        validateProperty(theme, "stylesheet", isString, DEFAULT_THEME);
        validateProperty(
            theme,
            "darkSchemeBackgroundColor",
            isRegExpMatch(/^#[0-9a-f]{6}$/i),
            DEFAULT_THEME
        );
        validateProperty(
            theme,
            "darkSchemeTextColor",
            isRegExpMatch(/^#[0-9a-f]{6}$/i),
            DEFAULT_THEME
        );
        validateProperty(
            theme,
            "lightSchemeBackgroundColor",
            isRegExpMatch(/^#[0-9a-f]{6}$/i),
            DEFAULT_THEME
        );
        validateProperty(
            theme,
            "lightSchemeTextColor",
            isRegExpMatch(/^#[0-9a-f]{6}$/i),
            DEFAULT_THEME
        );
        validateProperty(
            theme,
            "scrollbarColor",
            (x) => x === "" || isRegExpMatch(/^(auto)|(#[0-9a-f]{6})$/i)(x),
            DEFAULT_THEME
        );
        validateProperty(
            theme,
            "selectionColor",
            isRegExpMatch(/^(auto)|(#[0-9a-f]{6})$/i),
            DEFAULT_THEME
        );
        validateProperty(
            theme,
            "styleSystemControls",
            isBoolean,
            DEFAULT_THEME
        );
        validateProperty(
            theme,
            "lightColorScheme",
            isNonEmptyString,
            DEFAULT_THEME
        );
        validateProperty(
            theme,
            "darkColorScheme",
            isNonEmptyString,
            DEFAULT_THEME
        );
        validateProperty(theme, "immediateModify", isBoolean, DEFAULT_THEME);
        return {errors, theme};
    }

    function ImportSettings(props) {
        const context = getComponentContext();
        function showDialog(caption) {
            context.store.caption = caption;
            context.store.isDialogVisible = true;
            context.refresh();
        }
        function hideDialog() {
            context.store.isDialogVisible = false;
            context.refresh();
        }
        const dialog =
            context && context.store.isDialogVisible
                ? m$1(MessageBox, {
                      caption: context.store.caption,
                      onOK: hideDialog,
                      onCancel: hideDialog,
                      hideCancel: true
                  })
                : null;
        function showWarningDialog() {
            context.store.isWarningDialogVisible = true;
            context.refresh();
        }
        function hideWarningDialog() {
            context.store.isWarningDialogVisible = false;
            context.refresh();
        }
        const warningDialog = context.store.isWarningDialogVisible
            ? m$1(MessageBox, {
                  caption:
                      "Warning! Your current settings will be overwritten. Click OK to proceed.",
                  onOK: importSettings,
                  onCancel: hideWarningDialog
              })
            : null;
        function importSettings() {
            openFile({extensions: ["json"]}, (result) => {
                try {
                    const content = JSON.parse(result);
                    const {settings, errors} = validateSettings(content);
                    const count = errors.length;
                    if (count) {
                        console.error(
                            "Could not validate imported settings",
                            errors,
                            result,
                            content
                        );
                        showDialog(
                            `The given file has incorrect JSON: ${count > 1 ? `${count} errors, including ${errors[0]}` : errors[0]}`
                        );
                        return;
                    }
                    props.actions.changeSettings(settings);
                    showDialog("Settings imported");
                } catch (err) {
                    console.error(err);
                    showDialog("Failed to read file");
                }
            });
        }
        return m$1(
            ControlGroup$1,
            null,
            m$1(
                ControlGroup$1.Control,
                null,
                m$1(
                    Button,
                    {
                        onclick: showWarningDialog,
                        class: "advanced__import-settings-button"
                    },
                    "Import Settings",
                    dialog,
                    warningDialog
                )
            ),
            m$1(
                ControlGroup$1.Description,
                null,
                "Open settings from a JSON file"
            )
        );
    }

    function ResetSettings(props) {
        const context = getComponentContext();
        function showDialog() {
            context.store.isDialogVisible = true;
            context.refresh();
        }
        function hideDialog() {
            context.store.isDialogVisible = false;
            context.refresh();
        }
        function reset() {
            context.store.isDialogVisible = false;
            props.actions.changeSettings(DEFAULT_SETTINGS);
        }
        const dialog = context.store.isDialogVisible
            ? m$1(MessageBox, {
                  caption:
                      "Are you sure you want to remove all your settings? You cannot restore them later",
                  onOK: reset,
                  onCancel: hideDialog
              })
            : null;
        return m$1(
            ControlGroup$1,
            null,
            m$1(
                ControlGroup$1.Control,
                null,
                m$1(
                    ResetButton,
                    {onClick: showDialog},
                    "Reset settings",
                    dialog
                )
            ),
            m$1(
                ControlGroup$1.Description,
                null,
                "Restore settings to defaults"
            )
        );
    }

    function SyncConfig(props) {
        function syncConfig(syncSitesFixes) {
            props.actions.changeSettings({syncSitesFixes});
            props.actions.loadConfig({local: !syncSitesFixes});
        }
        return m$1(CheckButton, {
            checked: props.data.settings.syncSitesFixes,
            label: "Synchronize sites fixes",
            description: "Load the latest sites fixes from a remote server",
            onChange: syncConfig
        });
    }

    function SyncSettings(props) {
        function onSyncSettingsChange(checked) {
            props.actions.changeSettings({syncSettings: checked});
        }
        return m$1(CheckButton, {
            checked: props.data.settings.syncSettings,
            label: "Enable settings sync",
            description: props.data.settings.syncSettings
                ? "Synchronized across devices"
                : "Not synchronized across devices",
            onChange: onSyncSettingsChange
        });
    }

    function AdvancedTab(props) {
        return m$1(
            "div",
            {class: "settings-tab"},
            m$1(SyncSettings, {...props}),
            m$1(SyncConfig, {...props}),
            m$1(EnableForProtectedPages, {...props}),
            m$1(ContextMenus, {...props}),
            m$1(ImportSettings, {...props}),
            m$1(ExportSettings, {...props}),
            m$1(ResetSettings, {...props}),
            m$1(DevTools, null)
        );
    }

    function AutomationTab(props) {
        const isSystemAutomation =
            props.data.settings.automation.mode === AutomationMode.SYSTEM &&
            props.data.settings.automation.enabled;
        const locationSettings = props.data.settings.location;
        const values = {
            latitude: {
                min: -90,
                max: 90
            },
            longitude: {
                min: -180,
                max: 180
            }
        };
        function getLocationString(location) {
            if (location == null) {
                return "";
            }
            return `${location}°`;
        }
        function locationChanged(inputElement, newValue, type) {
            if (newValue.trim() === "") {
                inputElement.value = "";
                props.actions.changeSettings({
                    location: {
                        ...locationSettings,
                        [type]: null
                    }
                });
                return;
            }
            const min = values[type].min;
            const max = values[type].max;
            newValue = newValue.replace(",", ".").replace("°", "");
            let num = Number(newValue);
            if (isNaN(num)) {
                num = 0;
            } else if (num > max) {
                num = max;
            } else if (num < min) {
                num = min;
            }
            inputElement.value = getLocationString(num);
            props.actions.changeSettings({
                location: {
                    ...locationSettings,
                    [type]: num
                }
            });
        }
        function changeAutomationMode(mode) {
            props.actions.changeSettings({
                automation: {
                    ...props.data.settings.automation,
                    ...{mode, enabled: Boolean(mode)}
                }
            });
        }
        function changeAutomationBehavior(behavior) {
            props.actions.changeSettings({
                automation: {...props.data.settings.automation, ...{behavior}}
            });
        }
        return m$1(
            "div",
            {class: "settings-tab"},
            m$1(
                ControlGroup$1,
                null,
                m$1(
                    ControlGroup$1.Control,
                    {class: "automation__time-picker-control"},
                    m$1(CheckBox, {
                        checked:
                            props.data.settings.automation.mode ===
                            AutomationMode.TIME,
                        onchange: (e) =>
                            changeAutomationMode(
                                e.target.checked
                                    ? AutomationMode.TIME
                                    : AutomationMode.NONE
                            )
                    }),
                    m$1(TimeRangePicker, {
                        startTime: props.data.settings.time.activation,
                        endTime: props.data.settings.time.deactivation,
                        onChange: ([start, end]) =>
                            props.actions.changeSettings({
                                time: {activation: start, deactivation: end}
                            })
                    })
                ),
                m$1(
                    ControlGroup$1.Description,
                    null,
                    getLocalMessage("set_active_hours")
                )
            ),
            m$1(
                ControlGroup$1,
                null,
                m$1(
                    ControlGroup$1.Control,
                    {class: "automation__location-control"},
                    m$1(CheckBox, {
                        checked:
                            props.data.settings.automation.mode ===
                            AutomationMode.LOCATION,
                        onchange: (e) =>
                            changeAutomationMode(
                                e.target.checked
                                    ? AutomationMode.LOCATION
                                    : AutomationMode.NONE
                            )
                    }),
                    m$1(TextBox, {
                        class: "automation__location-control__latitude",
                        placeholder: getLocalMessage("latitude"),
                        onchange: (e) =>
                            locationChanged(
                                e.target,
                                e.target.value,
                                "latitude"
                            ),
                        oncreate: (node) =>
                            (node.value = getLocationString(
                                locationSettings.latitude
                            )),
                        onkeypress: (e) => {
                            if (e.key === "Enter") {
                                e.target.blur();
                            }
                        }
                    }),
                    m$1(TextBox, {
                        class: "automation__location-control__longitude",
                        placeholder: getLocalMessage("longitude"),
                        onchange: (e) =>
                            locationChanged(
                                e.target,
                                e.target.value,
                                "longitude"
                            ),
                        oncreate: (node) =>
                            (node.value = getLocationString(
                                locationSettings.longitude
                            )),
                        onkeypress: (e) => {
                            if (e.key === "Enter") {
                                e.target.blur();
                            }
                        }
                    })
                ),
                m$1(
                    ControlGroup$1.Description,
                    null,
                    getLocalMessage("set_location")
                )
            ),
            m$1(
                ControlGroup$1,
                null,
                m$1(
                    ControlGroup$1.Control,
                    {class: "automation__system-control"},
                    m$1(CheckBox, {
                        class: "automation__system-control__checkbox",
                        checked: isSystemAutomation,
                        onchange: (e) =>
                            changeAutomationMode(
                                e.target.checked
                                    ? AutomationMode.SYSTEM
                                    : AutomationMode.NONE
                            )
                    }),
                    m$1(
                        Button,
                        {
                            class: {
                                "automation__system-control__button": true,
                                "automation__system-control__button--active":
                                    isSystemAutomation
                            },
                            onclick: () => {
                                changeAutomationMode(
                                    isSystemAutomation
                                        ? AutomationMode.NONE
                                        : AutomationMode.SYSTEM
                                );
                            }
                        },
                        getLocalMessage("system_dark_mode")
                    )
                ),
                m$1(
                    ControlGroup$1.Description,
                    null,
                    getLocalMessage("system_dark_mode_description"),
                    !isMatchMediaChangeEventListenerBuggy
                        ? null
                        : [
                              m$1("br", null),
                              getLocalMessage(
                                  "system_dark_mode_chromium_warning"
                              )
                          ]
                )
            ),
            m$1(
                ControlGroup$1,
                null,
                m$1(
                    ControlGroup$1.Control,
                    {class: "automation__behavior"},
                    m$1(DropDown, {
                        onChange: (selected) =>
                            changeAutomationBehavior(selected),
                        selected: props.data.settings.automation.behavior,
                        options: [
                            {id: "OnOff", content: "Toggle on/off"},
                            {id: "Scheme", content: "Toggle dark/light"}
                        ]
                    })
                ),
                m$1(ControlGroup$1.Description, null, "Automation behavior")
            )
        );
    }

    function DetectDarkTheme(props) {
        function onDetectDarkThemeChange(checked) {
            props.actions.changeSettings({detectDarkTheme: checked});
        }
        return m$1(CheckButton, {
            checked: props.data.settings.detectDarkTheme,
            label: "Detect dark theme",
            description: props.data.settings.detectDarkTheme
                ? `Will not override website's dark theme`
                : `Will override website's dark theme`,
            onChange: onDetectDarkThemeChange
        });
    }

    function EnabledByDefault(props) {
        function onEnabledByDefaultChange(checked) {
            props.actions.changeSettings({enabledByDefault: checked});
        }
        return m$1(CheckButton, {
            checked: props.data.settings.enabledByDefault,
            label: "Enable by default",
            description: props.data.settings.enabledByDefault
                ? "Enabled on all websites by default"
                : "Disabled on all websites by default",
            onChange: onEnabledByDefaultChange
        });
    }

    function EnableForPDF(props) {
        function onInvertPDFChange(checked) {
            props.actions.changeSettings({enableForPDF: checked});
        }
        return m$1(CheckButton, {
            checked: props.data.settings.enableForPDF,
            label: "Enable for PDF files",
            description: props.data.settings.enableForPDF
                ? "Enabled for PDF documents"
                : "Disabled for PDF documents",
            onChange: onInvertPDFChange
        });
    }

    function GeneralTab(props) {
        return m$1(
            "div",
            {class: "settings-tab"},
            m$1(EnabledByDefault, {...props}),
            m$1(DetectDarkTheme, {...props}),
            m$1(EnableForPDF, {...props}),
            null
        );
    }

    function HotkeysTab(props) {
        const {data, actions} = props;
        return m$1(
            "div",
            {class: "settings-tab"},
            m$1(
                ControlGroup$1,
                null,
                m$1(
                    ControlGroup$1.Control,
                    null,
                    m$1(ShortcutLink, {
                        class: "hotkeys__control",
                        commandName: "toggle",
                        shortcuts: data.shortcuts,
                        textTemplate: (hotkey) =>
                            hotkey
                                ? hotkey
                                : getLocalMessage("click_to_set_shortcut"),
                        onSetShortcut: (shortcut) =>
                            actions.setShortcut("toggle", shortcut)
                    })
                ),
                m$1(
                    ControlGroup$1.Description,
                    null,
                    "Enable/disable the extension"
                )
            ),
            m$1(
                ControlGroup$1,
                null,
                m$1(
                    ControlGroup$1.Control,
                    null,
                    m$1(ShortcutLink, {
                        class: "hotkeys__control",
                        commandName: "addSite",
                        shortcuts: data.shortcuts,
                        textTemplate: (hotkey) =>
                            hotkey
                                ? hotkey
                                : getLocalMessage("click_to_set_shortcut"),
                        onSetShortcut: (shortcut) =>
                            actions.setShortcut("addSite", shortcut)
                    })
                ),
                m$1(
                    ControlGroup$1.Description,
                    null,
                    "Toggle the current website"
                )
            )
        );
    }

    function ClearSiteList(props) {
        const context = getComponentContext();
        const store = context.getStore({isDialogVisible: false});
        function showDialog() {
            store.isDialogVisible = true;
            context.refresh();
        }
        function hideDialog() {
            store.isDialogVisible = false;
            context.refresh();
        }
        function reset() {
            store.isDialogVisible = false;
            props.actions.changeSettings({enabledFor: [], disabledFor: []});
        }
        const dialog = store.isDialogVisible
            ? m$1(MessageBox, {
                  caption:
                      "Are you sure you want to remove all your sites from the list? You cannot restore them later",
                  onOK: reset,
                  onCancel: hideDialog
              })
            : null;
        return m$1(
            ControlGroup$1,
            null,
            m$1(
                ControlGroup$1.Control,
                null,
                m$1(
                    Button,
                    {onclick: showDialog, class: "clear-site-list-button"},
                    m$1(
                        "span",
                        {class: "clear-site-list-button__content"},
                        m$1(
                            "span",
                            {class: "clear-site-list-button__icon"},
                            m$1(DeleteIcon, null)
                        ),
                        "Clear site list"
                    ),
                    dialog
                )
            ),
            m$1(
                ControlGroup$1.Description,
                null,
                "Remove all sites from the list"
            )
        );
    }

    function SiteList(props) {
        const context = getComponentContext();
        const store = context.store;
        if (!context.prev) {
            store.indices = new WeakMap();
            store.shouldFocusAtIndex = -1;
            store.wasVisible = false;
        }
        context.onRender((node) => {
            const isVisible = node.clientWidth > 0;
            const {wasVisible} = store;
            store.wasVisible = isVisible;
            if (!wasVisible && isVisible) {
                store.shouldFocusAtIndex = props.siteList.length;
                context.refresh();
            }
        });
        function onTextChange(e) {
            const index = store.indices.get(e.target);
            const values = props.siteList.slice();
            const value = e.target.value.trim();
            if (values.includes(value)) {
                return;
            }
            if (!value) {
                values.splice(index, 1);
                store.shouldFocusAtIndex = index;
            } else if (index === values.length) {
                values.push(value);
                store.shouldFocusAtIndex = index + 1;
            } else {
                values.splice(index, 1, value);
                store.shouldFocusAtIndex = index + 1;
            }
            props.onChange(values);
        }
        function removeValue(event) {
            const previousSibling = event.target.previousSibling;
            const index = store.indices.get(previousSibling);
            const filtered = props.siteList.slice();
            filtered.splice(index, 1);
            store.shouldFocusAtIndex = index;
            props.onChange(filtered);
        }
        function createTextBox(text, index) {
            const onRender = (node) => {
                store.indices.set(node, index);
                if (store.shouldFocusAtIndex === index) {
                    store.shouldFocusAtIndex = -1;
                    node.focus();
                }
            };
            return m$1(
                "div",
                {class: "site-list__item"},
                m$1(TextBox, {
                    class: "site-list__textbox",
                    value: text,
                    onrender: onRender,
                    placeholder: "google.com/maps"
                }),
                text
                    ? m$1("span", {
                          class: "site-list__item__remove",
                          role: "button",
                          onclick: removeValue
                      })
                    : null
            );
        }
        const virtualScroll = m$1(VirtualScroll, {
            root: m$1("div", {
                class: "site-list__v-scroll-root",
                onchange: onTextChange
            }),
            items: props.siteList
                .map((site, index) => createTextBox(site, index))
                .concat(createTextBox("", props.siteList.length)),
            scrollToIndex: store.shouldFocusAtIndex
        });
        return m$1(
            ControlGroup$1,
            {class: "site-list-group"},
            m$1(
                ControlGroup$1.Control,
                {class: "site-list-group__control"},
                m$1("div", {class: "site-list"}, virtualScroll)
            ),
            m$1(
                ControlGroup$1.Description,
                {class: "site-list-group__description"},
                "Type in the domain name and press Enter"
            )
        );
    }

    function SiteListTab(props) {
        const {settings} = props.data;
        const {enabledByDefault} = settings;
        function onSiteListChange(sites) {
            const changes = enabledByDefault
                ? {disabledFor: sites}
                : {enabledFor: sites};
            props.actions.changeSettings(changes);
        }
        const label = enabledByDefault
            ? "Disable on these websites"
            : "Enable on these websites";
        const sites = enabledByDefault
            ? settings.disabledFor
            : settings.enabledFor;
        return m$1(
            "div",
            {class: "settings-tab site-list-tab"},
            m$1("label", {class: "site-list-tab__label"}, label),
            m$1(SiteList, {siteList: sites, onChange: onSiteListChange}),
            m$1(ClearSiteList, {...props})
        );
    }

    function TabPanel(props, ...children) {
        const {activeTabId} = props;
        function createTabButton(tabSpec) {
            var _a;
            const {id, label, icon, iconClass = ""} = tabSpec.props;
            function onClick() {
                props.onTabChange(id);
            }
            return m$1(
                Button,
                {
                    class: {
                        "settings-tab-panel__button": true,
                        "settings-tab-panel__button--active": activeTabId === id
                    },
                    onclick:
                        (_a = tabSpec.props.onClick) !== null && _a !== void 0
                            ? _a
                            : onClick
                },
                m$1(
                    "span",
                    {
                        class: {
                            "settings-tab-panel__button__icon": true,
                            [iconClass]: Boolean(iconClass)
                        }
                    },
                    icon
                ),
                label
            );
        }
        return m$1(
            "div",
            {
                class: {
                    "settings-tab-panel": true,
                    "settings-tab-panel--vertical": props.isVertical
                }
            },
            m$1(
                "div",
                {class: "settings-tab-panel__buttons"},
                ...children.map(createTabButton)
            ),
            m$1(
                "div",
                {class: "settings-tab-panel__tabs"},
                ...children.map((child) => {
                    const {id} = child.props;
                    const spec = {
                        ...child,
                        props: {
                            ...child.props,
                            isActive: id === activeTabId
                        }
                    };
                    return spec;
                })
            )
        );
    }
    function Tab(props, ...children) {
        return m$1(
            "div",
            {
                class: {
                    "settings-tab-panel__tab": true,
                    "settings-tab-panel__tab--active": props.isActive
                }
            },
            props.isActive ? children : null
        );
    }
    var TabPanel$1 = Object.assign(TabPanel, {Tab});

    function Body(props) {
        const context = getComponentContext();
        const store = context.getStore({activeTabId: "general"});
        function onSettingsTabChange(tabId) {
            store.activeTabId = tabId;
            context.refresh();
        }
        const now = new Date();
        const autoIcon = m$1(WatchIcon, {
            hours: now.getHours(),
            minutes: now.getMinutes(),
            color: "currentColor"
        });
        return m$1(
            "body",
            null,
            m$1(
                "header",
                null,
                m$1("img", {
                    id: "logo",
                    src: "../assets/images/darkreader-type.svg",
                    alt: "Dark Reader"
                }),
                m$1("h1", {id: "title"}, "Settings")
            ),
            m$1(
                TabPanel$1,
                {
                    activeTabId: store.activeTabId,
                    onTabChange: onSettingsTabChange
                },
                m$1(
                    TabPanel$1.Tab,
                    {
                        id: "general",
                        label: "General",
                        icon: m$1(SettingsIcon, null),
                        iconClass: "settings-icon-general"
                    },
                    m$1(GeneralTab, {...props})
                ),
                m$1(
                    TabPanel$1.Tab,
                    {
                        id: "site-list",
                        label: "Site List",
                        icon: m$1(ListIcon, null),
                        iconClass: "settings-icon-list"
                    },
                    m$1(SiteListTab, {...props})
                ),
                m$1(
                    TabPanel$1.Tab,
                    {
                        id: "automation",
                        label: "Automation",
                        icon: autoIcon,
                        iconClass: "settings-icon-auto"
                    },
                    m$1(AutomationTab, {...props})
                ),
                m$1(
                    TabPanel$1.Tab,
                    {
                        id: "hotkeys",
                        label: "Hotkeys",
                        icon: m$1(KeyboardIcon, null),
                        iconClass: "settings-icon-hotkeys"
                    },
                    m$1(HotkeysTab, {...props})
                ),
                m$1(
                    TabPanel$1.Tab,
                    {
                        id: "activation",
                        label: "Activation",
                        icon: m$1(KeyIcon, null),
                        iconClass: "settings-icon-activation"
                    },
                    m$1(ActivationTab, {...props})
                ),
                m$1(
                    TabPanel$1.Tab,
                    {
                        id: "advanced",
                        label: "Advanced",
                        icon: m$1(AdvancedIcon, null),
                        iconClass: "settings-icon-advanced"
                    },
                    m$1(AdvancedTab, {...props})
                ),
                m$1(
                    TabPanel$1.Tab,
                    {
                        id: "about",
                        label: "About",
                        icon: m$1(HelpIcon, null),
                        iconClass: "settings-icon-about"
                    },
                    m$1(AboutTab, {...props})
                )
            ),
            m$1(Overlay$1, null)
        );
    }

    function renderBody(data, actions) {
        sync(document.body, m$1(Body, {data: data, actions: actions}));
    }
    async function start() {
        const connector = new Connector();
        window.addEventListener("unload", () => connector.disconnect(), {
            passive: true
        });
        const data = await connector.getData();
        renderBody(data, connector);
        connector.subscribeToChanges(async (newData) => {
            renderBody(newData, connector);
        });
    }
    document.documentElement.classList.toggle("mobile", isMobile);
    document.documentElement.classList.toggle("firefox", isFirefox);
    start();
})();
