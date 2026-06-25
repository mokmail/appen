<script lang="ts">
	import Strikethrough from 'lucide-svelte/icons/strikethrough';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Strikethrough
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
