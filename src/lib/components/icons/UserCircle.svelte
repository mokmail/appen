<script lang="ts">
	import CircleUser from 'lucide-svelte/icons/circle-user';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<CircleUser
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
