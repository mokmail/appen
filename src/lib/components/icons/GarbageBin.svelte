<script lang="ts">
	import Trash2 from 'lucide-svelte/icons/trash-2';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Trash2
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
