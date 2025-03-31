// External dependencies
export { parse } from "https://deno.land/std@0.220.1/flags/mod.ts";
export * as path from "https://deno.land/std@0.220.1/path/mod.ts";
export * as fs from "https://deno.land/std@0.220.1/fs/mod.ts";
export { ensureDir } from "https://deno.land/std@0.220.1/fs/ensure_dir.ts";
export { retry } from "https://deno.land/std@0.220.1/async/retry.ts";

// Add type declarations for Deno and import.meta
declare global {
  interface ImportMeta {
    main: boolean;
  }
  
  // Definição para o objeto Deno global
  const Deno: {
    args: string[];
    exit(code?: number): never;
    env: {
      get(key: string): string | undefined;
      set(key: string, value: string): void;
      toObject(): { [key: string]: string };
    };
    // Adicione outras APIs do Deno conforme necessário
  };
}

// We'll use fetch instead of Puppeteer for simpler implementation
// This will avoid browser dependencies
