<script lang="ts">
	import Save from 'lucide-svelte/icons/save';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Save
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
