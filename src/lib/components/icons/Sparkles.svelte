<script lang="ts">
	import Sparkles from 'lucide-svelte/icons/sparkles';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Sparkles
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
