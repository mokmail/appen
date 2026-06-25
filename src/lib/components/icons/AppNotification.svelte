<script lang="ts">
	import Bell from 'lucide-svelte/icons/bell';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Bell
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
