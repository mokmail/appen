<script lang="ts">
	import Keyboard from 'lucide-svelte/icons/keyboard';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Keyboard
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
