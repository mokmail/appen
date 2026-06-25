<script lang="ts">
	import Menu from 'lucide-svelte/icons/menu';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Menu
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
