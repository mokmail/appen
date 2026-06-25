<script lang="ts">
	import Zap from 'lucide-svelte/icons/zap';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Zap
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
