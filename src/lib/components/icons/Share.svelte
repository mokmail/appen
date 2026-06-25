<script lang="ts">
	import Share2 from 'lucide-svelte/icons/share-2';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Share2
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
