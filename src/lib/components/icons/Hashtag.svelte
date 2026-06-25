<script lang="ts">
	import Hash from 'lucide-svelte/icons/hash';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Hash
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
