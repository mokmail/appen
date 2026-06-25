<script lang="ts">
	import User from 'lucide-svelte/icons/user';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<User
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
