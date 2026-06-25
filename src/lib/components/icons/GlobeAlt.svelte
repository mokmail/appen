<script lang="ts">
	import Globe from 'lucide-svelte/icons/globe';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Globe
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
