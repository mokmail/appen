<script lang="ts">
	import Plus from 'lucide-svelte/icons/plus';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Plus
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
