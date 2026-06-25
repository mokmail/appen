<script lang="ts">
	import Pencil from 'lucide-svelte/icons/pencil';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Pencil
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
