<script lang="ts">
	import ScanFace from 'lucide-svelte/icons/scan-face';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<ScanFace
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
