<script lang="ts">
	import Lightbulb from 'lucide-svelte/icons/lightbulb';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Lightbulb
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
