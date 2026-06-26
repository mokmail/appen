import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import { readFileSync } from 'fs';
import { resolve } from 'path';

import { viteStaticCopy } from 'vite-plugin-static-copy';

// BEV overlay: read WEBUI_VERSION from .env so the frontend build matches
// the backend version without needing to manually `export` it first.
// Falls back to package.json version if .env has no WEBUI_VERSION.
function readEnvVersion(): string {
	try {
		const envPath = resolve(process.cwd(), '.env');
		const envContent = readFileSync(envPath, 'utf-8');
		const match = envContent.match(/^WEBUI_VERSION\s*=\s*['"]?([^'"\s#]+)['"]?/m);
		if (match) return match[1];
	} catch {
		// .env not found — fall through to package.json
	}
	return process.env.npm_package_version;
}

const resolvedVersion = readEnvVersion();

export default defineConfig({
	plugins: [
		sveltekit(),
		viteStaticCopy({
			targets: [
				{
					src: 'node_modules/onnxruntime-web/dist/*.jsep.*',

					dest: 'wasm'
				}
			]
		})
	],
	define: {
		APP_VERSION: JSON.stringify(resolvedVersion),
		APP_BUILD_HASH: JSON.stringify(process.env.APP_BUILD_HASH || 'dev-build')
	},
	build: {
		sourcemap: true
	},
	worker: {
		format: 'es'
	},
	esbuild: {
		pure: process.env.ENV === 'dev' ? [] : ['console.log', 'console.debug', 'console.error']
	}
});