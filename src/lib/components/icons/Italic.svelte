<script lang="ts">
	import Italic from 'lucide-svelte/icons/italic';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Italic
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
