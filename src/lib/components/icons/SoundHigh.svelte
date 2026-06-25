<script lang="ts">
	import Volume2 from 'lucide-svelte/icons/volume-2';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Volume2
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
