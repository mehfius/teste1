// External dependencies
export { parse } from "https://deno.land/std@0.192.0/flags/mod.ts";
export * as path from "https://deno.land/std@0.192.0/path/mod.ts";
export * as fs from "https://deno.land/std@0.192.0/fs/mod.ts";
export { ensureDir } from "https://deno.land/std@0.192.0/fs/ensure_dir.ts";
export { retry } from "https://deno.land/std@0.192.0/async/retry.ts";

// We'll use fetch instead of Puppeteer for simpler implementation
// This will avoid browser dependencies
