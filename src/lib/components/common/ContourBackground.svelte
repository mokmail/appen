<script lang="ts">
	/**
	 * ContourBackground — BEV Kartografisch signature motif.
	 * Hairline concentric topographic contour lines, the visual language of
	 * surveying & metrology. Used sparingly: empty states, the chat hero,
	 * the active-nav rail. The one element that makes this unmistakably BEV.
	 *
	 * Pure SVG, no images, reduced-motion safe (static when requested).
	 */
	export let className = '';
	export let density: 'sparse' | 'standard' | 'dense' = 'standard';
	export let active = false;
</script>

{#if density === 'sparse'}
	<svg
		xmlns="http://www.w3.org/2000/svg"
		preserveAspectRatio="xMidYMid slice"
		viewBox="0 0 400 300"
		class={className}
		fill="none"
		aria-hidden="true"
	>
		<g
			stroke={active ? 'var(--bev-contour-stroke-active)' : 'var(--bev-contour-stroke)'}
			stroke-width="0.6"
		>
			<path d="M200,150 m-30,0 a30,30 0 1,0 60,0 a30,30 0 1,0 -60,0" />
			<path d="M200,150 m-55,0 a55,40 0 1,0 110,0 a55,40 0 1,0 -110,0" />
			<path d="M200,150 m-85,0 a85,55 0 1,0 170,0 a85,55 0 1,0 -170,0" />
			<path d="M200,150 m-120,0 a120,75 0 1,0 240,0 a120,75 0 1,0 -240,0" />
		</g>
	</svg>
{:else if density === 'dense'}
	<svg
		xmlns="http://www.w3.org/2000/svg"
		preserveAspectRatio="xMidYMid slice"
		viewBox="0 0 600 400"
		class={className}
		fill="none"
		aria-hidden="true"
	>
		<g
			stroke={active ? 'var(--bev-contour-stroke-active)' : 'var(--bev-contour-stroke)'}
			stroke-width="0.5"
		>
			<path d="M300,200 m-20,0 a20,20 0 1,0 40,0 a20,20 0 1,0 -40,0" />
			<path d="M300,200 m-38,0 a38,28 0 1,0 76,0 a38,28 0 1,0 -76,0" />
			<path d="M300,200 m-56,0 a56,36 0 1,0 112,0 a56,36 0 1,0 -112,0" />
			<path d="M300,200 m-78,0 a78,46 0 1,0 156,0 a78,46 0 1,0 -156,0" />
			<path d="M300,200 m-104,0 a104,58 0 1,0 208,0 a104,58 0 1,0 -208,0" />
			<path d="M300,200 m-134,0 a134,72 0 1,0 268,0 a134,72 0 1,0 -268,0" />
			<path d="M300,200 m-170,0 a170,90 0 1,0 340,0 a170,90 0 1,0 -340,0" />
			<path d="M300,200 m-212,0 a212,112 0 1,0 424,0 a212,112 0 1,0 -424,0" />
			<path d="M300,200 m-260,0 a260,138 0 1,0 520,0 a260,138 0 1,0 -520,0" />
		</g>
	</svg>
{:else}
	<svg
		xmlns="http://www.w3.org/2000/svg"
		preserveAspectRatio="xMidYMid slice"
		viewBox="0 0 500 350"
		class={className}
		fill="none"
		aria-hidden="true"
	>
		<g
			stroke={active ? 'var(--bev-contour-stroke-active)' : 'var(--bev-contour-stroke)'}
			stroke-width="0.55"
		>
			<path d="M250,175 m-24,0 a24,24 0 1,0 48,0 a24,24 0 1,0 -48,0" />
			<path d="M250,175 m-44,0 a44,32 0 1,0 88,0 a44,32 0 1,0 -88,0" />
			<path d="M250,175 m-66,0 a66,42 0 1,0 132,0 a66,42 0 1,0 -132,0" />
			<path d="M250,175 m-92,0 a92,52 0 1,0 184,0 a92,52 0 1,0 -184,0" />
			<path d="M250,175 m-122,0 a122,64 0 1,0 244,0 a122,64 0 1,0 -244,0" />
			<path d="M250,175 m-156,0 a156,78 0 1,0 312,0 a156,78 0 1,0 -312,0" />
			<path d="M250,175 m-194,0 a194,96 0 1,0 388,0 a194,96 0 1,0 -388,0" />
			<path d="M250,175 m-238,0 a238,118 0 1,0 476,0 a238,118 0 1,0 -476,0" />
		</g>
	</svg>
{/if}