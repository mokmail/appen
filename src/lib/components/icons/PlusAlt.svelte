<script lang="ts">
	import PlusCircle from 'lucide-svelte/icons/plus-circle';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<PlusCircle
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
