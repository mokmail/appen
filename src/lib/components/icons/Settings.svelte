<script lang="ts">
	import Settings from 'lucide-svelte/icons/settings';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Settings
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
