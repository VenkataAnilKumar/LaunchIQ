type Json = Record<string, unknown>;

/**
 * Pydantic renders Optional[str] as anyOf:[{type:string},{type:null}], which JSON-Schema form
 * libraries show as a confusing type picker. Collapse those to the single real type; an empty
 * field is then simply omitted from the edited output.
 */
export function simplifySchema<T>(node: T): T {
	if (Array.isArray(node)) {
		return node.map((item) => simplifySchema(item)) as unknown as T;
	}
	if (node && typeof node === "object") {
		const obj = { ...(node as Json) };
		const anyOf = obj.anyOf;
		if (Array.isArray(anyOf)) {
			const real = anyOf.filter((option) => !(option && typeof option === "object" && (option as Json).type === "null"));
			if (real.length === 1 && real.length !== anyOf.length) {
				delete obj.anyOf;
				delete obj.default;
				Object.assign(obj, simplifySchema(real[0]));
			}
		}
		for (const key of Object.keys(obj)) {
			obj[key] = simplifySchema(obj[key]);
		}
		return obj as T;
	}
	return node;
}

/** Remove keys with null/empty-string values so optional fields round-trip as "not set". */
export function pruneEmpty<T>(value: T): T {
	if (Array.isArray(value)) {
		return value.map((item) => pruneEmpty(item)) as unknown as T;
	}
	if (value && typeof value === "object") {
		const out: Json = {};
		for (const [key, child] of Object.entries(value as Json)) {
			if (child === null || child === "") {
				continue;
			}
			out[key] = pruneEmpty(child);
		}
		return out as T;
	}
	return value;
}

/** Drop auto-generated model-class titles ("LaunchStrategyOutput", "LaunchPhase") so only field names show. */
export function stripModelTitles(schema: Json): Json {
	const out: Json = { ...schema };
	delete out.title;
	const defs = out.$defs;
	if (defs && typeof defs === "object") {
		out.$defs = Object.fromEntries(
			Object.entries(defs as Record<string, Json>).map(([name, def]) => {
				const copy = { ...def };
				delete copy.title;
				return [name, copy];
			}),
		);
	}
	return out;
}
