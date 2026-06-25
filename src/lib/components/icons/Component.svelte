<script lang="ts">
	import Component from 'lucide-svelte/icons/component';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Component
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
