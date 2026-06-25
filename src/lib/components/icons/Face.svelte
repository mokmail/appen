<script lang="ts">
	import Smile from 'lucide-svelte/icons/smile';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Smile
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
