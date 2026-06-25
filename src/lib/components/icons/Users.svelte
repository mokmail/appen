<script lang="ts">
	import Users from 'lucide-svelte/icons/users';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Users
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
