<script lang="ts">
	import Link2Off from 'lucide-svelte/icons/link-2-off';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Link2Off
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
