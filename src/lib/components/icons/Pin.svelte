<script lang="ts">
	import Pin from 'lucide-svelte/icons/pin';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Pin
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
