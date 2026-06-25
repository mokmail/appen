<script lang="ts">
	import Cloud from 'lucide-svelte/icons/cloud';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Cloud
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
