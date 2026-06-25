<script lang="ts">
	import Group from 'lucide-svelte/icons/group';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Group
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
