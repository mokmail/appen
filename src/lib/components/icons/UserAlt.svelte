<script lang="ts">
	import UserRound from 'lucide-svelte/icons/user-round';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<UserRound
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
