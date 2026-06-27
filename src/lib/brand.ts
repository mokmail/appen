/**
 * BEV branding overlay — frontend single source of truth.
 *
 * The static constants below are *fallbacks* used before the backend
 * /api/config response arrives.  At runtime the BRAND store (in
 * stores/index.ts) is populated from the backend's `brand` config block,
 * which reads values from the .env file via backend/open_webui/branding.py.
 *
 * See BEV_CUSTOMIZATIONS.md.
 */

export const BRAND_NAME = 'Bundesamt für Eich- und Vermessungswesen';
export const BRAND_SHORT_NAME = 'BEV';
export const BRAND_TAGLINE = 'KI-Plattform des Bundesamtes für Eich- und Vermessungswesen';
export const BRAND_URL = 'https://www.bev.gv.at';
export const BRAND_THEME_KEY = 'bev';

/** PWA / manifest */
export const BRAND_BG_COLOR_DARK = '#0f1419';
export const BRAND_BG_COLOR_LIGHT = '#f5f8fa';
export const BRAND_META_COLOR_DARK = '#1a1a1a';
export const BRAND_META_COLOR_LIGHT = '#ffffff';

/** Fallback BrandConfig used to initialise the BRAND store before /api/config loads. */
export const BRAND_FALLBACKS = {
	name: BRAND_NAME,
	short_name: BRAND_SHORT_NAME,
	description: BRAND_TAGLINE,
	url: BRAND_URL,
	favicon_url: '/favicon.png',
	theme_key: BRAND_THEME_KEY,
	bg_color_dark: BRAND_BG_COLOR_DARK,
	bg_color_light: BRAND_BG_COLOR_LIGHT,
	meta_color_dark: BRAND_META_COLOR_DARK,
	meta_color_light: BRAND_META_COLOR_LIGHT,
};

export default BRAND_NAME;