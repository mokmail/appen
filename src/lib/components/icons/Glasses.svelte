<script lang="ts">
	import Glasses from 'lucide-svelte/icons/glasses';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Glasses
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
