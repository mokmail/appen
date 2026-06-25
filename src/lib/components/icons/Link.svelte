<script lang="ts">
	import Link from 'lucide-svelte/icons/link';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Link
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
